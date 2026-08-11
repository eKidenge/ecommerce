from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from apps.cart.models import Cart
from apps.accounts.models import Address
from .models import Order, OrderItem, OrderStatusHistory
from .forms import CheckoutForm

@login_required
@csrf_protect
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if cart.total_items == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:view')
    
    addresses = request.user.addresses.filter(is_active=True)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    subtotal=cart.subtotal,
                    discount_amount=cart.total_discount,
                    shipping_cost=cart.shipping_cost,
                    tax_amount=0,  # Calculate tax if needed
                    total_amount=cart.grand_total,
                    shipping_address=form.cleaned_data['shipping_address'],
                    billing_address=form.cleaned_data.get('billing_address') or form.cleaned_data['shipping_address'],
                    customer_notes=form.cleaned_data.get('notes', ''),
                )
                
                # Create order items
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        variant=cart_item.variant,
                        product_name=cart_item.product.name,
                        sku=cart_item.product.sku,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.unit_price,
                        total_price=cart_item.subtotal,
                        discount_amount=cart_item.discount_amount,
                    )
                    
                    # Update stock
                    if cart_item.variant:
                        cart_item.variant.stock -= cart_item.quantity
                        cart_item.variant.save()
                    else:
                        cart_item.product.stock -= cart_item.quantity
                        cart_item.product.save()
                
                # Create status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status='pending',
                    note='Order placed',
                    created_by=request.user
                )
                
                # Clear cart
                cart.items.all().delete()
                
                # Redirect to payment
                return redirect('payments:process_payment', order_id=order.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CheckoutForm(user=request.user)
    
    context = {
        'cart': cart,
        'addresses': addresses,
        'form': form,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(orders, 10)
    page = request.GET.get('page', 1)
    try:
        orders = paginator.page(page)
    except:
        orders = paginator.page(1)
    
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/track_order.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status not in ['pending', 'processing']:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        with transaction.atomic():
            order.status = 'cancelled'
            order.cancelled_at = timezone.now()
            order.save()
            
            # Restore stock
            for item in order.items.all():
                if item.variant:
                    item.variant.stock += item.quantity
                    item.variant.save()
                else:
                    item.product.stock += item.quantity
                    item.product.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                note=request.POST.get('reason', 'Order cancelled by customer'),
                created_by=request.user
            )
            
            messages.success(request, 'Order cancelled successfully.')
            return redirect('orders:order_detail', order_id=order.id)
    
    return render(request, 'orders/cancel_order.html', {'order': order})



# Add these to existing views.py

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    template = get_template('orders/invoice.html')
    html = template.render({'order': order})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice-{order.order_number}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def reorder(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = get_cart(request)
    
    # Clear existing cart
    cart.items.all().delete()
    
    # Add items from order to cart
    for item in order.items.all():
        if item.product.is_active and item.product.in_stock:
            CartItem.objects.create(
                cart=cart,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                unit_price=item.product.price
            )
    
    messages.success(request, 'Items added to cart successfully!')
    return redirect('cart:view')