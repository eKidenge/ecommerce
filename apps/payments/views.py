import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from apps.orders.models import Order, OrderStatusHistory
from .models import Payment
from .services.stripe_service import StripePaymentService
from .services.mpesa_service import MpesaPaymentService
import json
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def process_payment(request, order_id):
    """Process payment for an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        messages.warning(request, 'This order has already been paid.')
        return redirect('orders:detail', order_id=order.id)
    
    payment_method = request.GET.get('method', 'stripe')
    
    # Create payment record
    payment = Payment.objects.create(
        order=order,
        user=request.user,
        payment_method=payment_method,
        amount=order.total_amount,
        currency='KES',
        status='pending'
    )
    
    if payment_method == 'stripe':
        return process_stripe_payment(request, order, payment)
    elif payment_method == 'mpesa':
        return process_mpesa_payment(request, order, payment)
    else:
        messages.error(request, 'Invalid payment method selected.')
        return redirect('orders:detail', order_id=order.id)

def process_stripe_payment(request, order, payment):
    """Process Stripe payment"""
    try:
        stripe_service = StripePaymentService()
        checkout_session = stripe_service.create_checkout_session(order, payment, request)
        
        # Update payment with Stripe session ID
        payment.payment_intent_id = checkout_session.payment_intent
        payment.transaction_id = checkout_session.id
        payment.save()
        
        return redirect(checkout_session.url)
    
    except Exception as e:
        payment.status = 'failed'
        payment.error_message = str(e)
        payment.save()
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('orders:detail', order_id=order.id)

def process_mpesa_payment(request, order, payment):
    """Process M-Pesa payment"""
    try:
        mpesa_service = MpesaPaymentService()
        
        # Get phone number from request or user profile
        phone_number = request.POST.get('phone_number') or request.user.phone_number
        
        if not phone_number:
            messages.error(request, 'Phone number is required for M-Pesa payments.')
            return redirect('orders:detail', order_id=order.id)
        
        response = mpesa_service.stk_push(
            phone_number=phone_number,
            amount=order.total_amount,
            account_reference=f"ORDER{order.order_number}",
            transaction_desc=f"Payment for order {order.order_number}"
        )
        
        if response.get('ResponseCode') == '0':
            payment.mpesa_checkout_request_id = response.get('CheckoutRequestID')
            payment.mpesa_phone = phone_number
            payment.transaction_id = response.get('MerchantRequestID')
            payment.status = 'processing'
            payment.save()
            
            messages.info(request, 'Please complete payment on your M-Pesa phone.')
            return redirect('payments:pending', payment_id=payment.id)
        else:
            payment.status = 'failed'
            payment.error_message = response.get('ResponseDescription', 'M-Pesa payment failed')
            payment.save()
            messages.error(request, 'M-Pesa payment failed. Please try again.')
            return redirect('orders:detail', order_id=order.id)
    
    except Exception as e:
        payment.status = 'failed'
        payment.error_message = str(e)
        payment.save()
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('orders:detail', order_id=order.id)

def payment_success(request):
    """Handle successful payment"""
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('products:home')
    
    try:
        stripe_service = StripePaymentService()
        session = stripe_service.retrieve_session(session_id)
        order = Order.objects.get(id=session.client_reference_id)
        
        # Update payment and order status
        with transaction.atomic():
            payment = order.payment
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.transaction_id = session.payment_intent
            payment.response_data = session.to_dict()
            payment.save()
            
            order.payment_status = 'paid'
            order.paid_at = timezone.now()
            order.status = 'processing'
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                status='processing',
                note='Payment received, order is being processed',
                created_by=order.user
            )
        
        messages.success(request, 'Payment successful! Your order is being processed.')
        return render(request, 'payments/payment_success.html', {'order': order})
    
    except Exception as e:
        messages.error(request, f'Error processing payment: {str(e)}')
        return redirect('products:home')

def payment_cancel(request):
    """Handle cancelled payment"""
    messages.warning(request, 'Payment was cancelled.')
    return render(request, 'payments/payment_cancel.html')

def payment_pending(request, payment_id):
    """Show pending payment status"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return render(request, 'payments/payment_pending.html', {'payment': payment})

def payment_failed(request, payment_id):
    """Show failed payment status"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return render(request, 'payments/payment_failed.html', {'payment': payment})

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        stripe_service = StripePaymentService()
        event = stripe_service.verify_webhook_signature(payload, sig_header)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    # Handle the event
    event_type = event['type']
    event_data = event['data']['object']
    
    if event_type == 'checkout.session.completed':
        handle_checkout_session_completed(event_data)
    elif event_type == 'payment_intent.succeeded':
        handle_payment_intent_succeeded(event_data)
    elif event_type == 'payment_intent.payment_failed':
        handle_payment_intent_failed(event_data)
    elif event_type == 'charge.refunded':
        handle_charge_refunded(event_data)
    
    return JsonResponse({'status': 'success'})

def handle_checkout_session_completed(session):
    """Handle checkout.session.completed webhook event"""
    order_id = session.get('client_reference_id')
    if not order_id:
        return
    
    try:
        with transaction.atomic():
            order = Order.objects.get(id=order_id)
            payment = order.payment
            
            payment.status = 'completed'
            payment.transaction_id = session.payment_intent
            payment.completed_at = timezone.now()
            payment.response_data = session
            payment.save()
            
            order.payment_status = 'paid'
            order.paid_at = timezone.now()
            order.status = 'processing'
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                status='processing',
                note='Payment confirmed via Stripe webhook',
            )
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found for webhook")

def handle_payment_intent_succeeded(payment_intent):
    """Handle payment_intent.succeeded webhook event"""
    # You can add additional logic here
    logger.info(f"Payment intent succeeded: {payment_intent.id}")

def handle_payment_intent_failed(payment_intent):
    """Handle payment_intent.payment_failed webhook event"""
    try:
        order = Order.objects.get(payment__payment_intent_id=payment_intent.id)
        payment = order.payment
        payment.status = 'failed'
        payment.error_message = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
        payment.save()
    except Order.DoesNotExist:
        logger.error(f"Order not found for payment intent: {payment_intent.id}")

def handle_charge_refunded(charge):
    """Handle charge.refunded webhook event"""
    try:
        order = Order.objects.get(payment__payment_intent_id=charge.payment_intent)
        payment = order.payment
        payment.status = 'refunded'
        payment.save()
        
        order.payment_status = 'refunded'
        order.status = 'refunded'
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            status='refunded',
            note='Payment refunded',
        )
    except Order.DoesNotExist:
        logger.error(f"Order not found for refund: {charge.payment_intent}")

@csrf_exempt
@require_POST
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    try:
        data = json.loads(request.body)
        mpesa_service = MpesaPaymentService()
        result = mpesa_service.process_callback(data)
        
        if result.get('success'):
            # Update payment status
            checkout_request_id = data.get('CheckoutRequestID')
            try:
                with transaction.atomic():
                    payment = Payment.objects.get(mpesa_checkout_request_id=checkout_request_id)
                    payment.status = 'completed'
                    payment.mpesa_receipt = result.get('mpesa_receipt')
                    payment.completed_at = timezone.now()
                    payment.save()
                    
                    # Update order
                    order = payment.order
                    order.payment_status = 'paid'
                    order.paid_at = timezone.now()
                    order.status = 'processing'
                    order.save()
                    
                    OrderStatusHistory.objects.create(
                        order=order,
                        status='processing',
                        note='M-Pesa payment confirmed',
                    )
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for checkout: {checkout_request_id}")
        
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
    
    except Exception as e:
        logger.error(f"M-Pesa callback error: {str(e)}")
        return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)})

@csrf_exempt
@require_POST
def mpesa_result(request):
    """Handle M-Pesa result URL"""
    try:
        data = json.loads(request.body)
        # Process M-Pesa result
        result_code = data.get('ResultCode')
        result_desc = data.get('ResultDesc')
        
        if result_code == '0':
            # Payment successful
            checkout_request_id = data.get('CheckoutRequestID')
            try:
                payment = Payment.objects.get(mpesa_checkout_request_id=checkout_request_id)
                payment.status = 'completed'
                payment.mpesa_receipt = data.get('MpesaReceiptNumber')
                payment.completed_at = timezone.now()
                payment.save()
            except Payment.DoesNotExist:
                pass
        
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
    
    except Exception as e:
        logger.error(f"M-Pesa result error: {str(e)}")
        return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)})

@login_required
def check_payment_status(request, payment_id):
    """Check payment status via AJAX"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # If M-Pesa payment, query status
    if payment.payment_method == 'mpesa' and payment.mpesa_checkout_request_id:
        try:
            mpesa_service = MpesaPaymentService()
            status = mpesa_service.query_status(payment.mpesa_checkout_request_id)
            
            if status.get('ResultCode') == '0':
                # Payment completed
                payment.status = 'completed'
                payment.save()
                
                order = payment.order
                order.payment_status = 'paid'
                order.save()
                
                return JsonResponse({
                    'status': 'completed',
                    'message': 'Payment completed successfully'
                })
            elif status.get('ResultCode') == '1':
                # Payment failed
                payment.status = 'failed'
                payment.save()
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Payment failed'
                })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': payment.status,
        'message': f'Payment status: {payment.get_status_display()}'
    })

@login_required
def retry_payment(request, order_id):
    """Retry a failed payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        messages.warning(request, 'This order has already been paid.')
        return redirect('orders:detail', order_id=order.id)
    
    # Delete existing failed payment
    Payment.objects.filter(order=order, status='failed').delete()
    
    # Redirect to payment process
    return redirect('payments:process_payment', order_id=order.id)

@login_required
def get_payment_methods(request, order_id):
    """Get available payment methods for an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    payment_methods = [
        {
            'id': 'stripe',
            'name': 'Credit/Debit Card',
            'icon': 'fa-credit-card',
            'logo': '/static/images/stripe-logo.png'
        },
        {
            'id': 'mpesa',
            'name': 'M-Pesa',
            'icon': 'fa-mobile-alt',
            'logo': '/static/images/mpesa-logo.png'
        }
    ]
    
    return JsonResponse({
        'payment_methods': payment_methods,
        'order_total': str(order.total_amount),
        'currency': 'KES'
    })