import stripe
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from apps.orders.models import Order, OrderStatusHistory
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
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
        pass

def handle_payment_intent_succeeded(payment_intent):
    # Handle successful payment intent
    pass

def handle_payment_intent_failed(payment_intent):
    # Handle failed payment intent
    pass

def handle_charge_refunded(charge):
    # Handle refund
    pass

@csrf_exempt
@require_POST
def mpesa_webhook(request):
    data = json.loads(request.body)
    # Handle M-Pesa webhook
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})

@csrf_exempt
@require_POST
def mpesa_callback(request):
    data = json.loads(request.body)
    # Handle M-Pesa callback
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})

@csrf_exempt
@require_POST
def mpesa_result(request):
    data = json.loads(request.body)
    # Handle M-Pesa result
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})