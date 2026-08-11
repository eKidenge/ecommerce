from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from apps.products.models import Product, ProductVariant
from .models import Cart, CartItem
import json

def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart

@login_required
def view_cart(request):
    cart = get_cart(request)
    context = {
        'cart': cart,
        'items': cart.items.all().select_related('product'),
    }
    return render(request, 'cart/cart.html', context)

@login_required
@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, is_active=True)
    
    # Check stock
    if variant:
        if variant.stock < quantity:
            return JsonResponse({'error': 'Not enough stock'}, status=400)
    elif product.stock < quantity:
        return JsonResponse({'error': 'Not enough stock'}, status=400)
    
    cart = get_cart(request)
    
    # Check if item exists
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={
            'quantity': quantity,
            'unit_price': variant.additional_price + product.price if variant else product.price
        }
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'total_items': cart.total_items,
        'total_price': cart.total_price,
    })

@login_required
@require_POST
def update_cart(request):
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if quantity <= 0:
        cart_item.delete()
    else:
        # Check stock
        if cart_item.variant:
            if cart_item.variant.stock < quantity:
                return JsonResponse({'error': 'Not enough stock'}, status=400)
        elif cart_item.product.stock < quantity:
            return JsonResponse({'error': 'Not enough stock'}, status=400)
        
        cart_item.quantity = quantity
        cart_item.save()
    
    cart = cart_item.cart
    return JsonResponse({
        'success': True,
        'total_items': cart.total_items,
        'total_price': cart.total_price,
        'subtotal': cart.subtotal,
        'item_subtotal': cart_item.subtotal,
    })

@login_required
@require_POST
def remove_from_cart(request):
    item_id = request.POST.get('item_id')
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    
    cart = cart_item.cart
    return JsonResponse({
        'success': True,
        'total_items': cart.total_items,
        'total_price': cart.total_price,
    })

@login_required
def cart_summary(request):
    cart = get_cart(request)
    return render(request, 'cart/cart_summary.html', {'cart': cart})

# Add these to existing views.py

@login_required
def clear_cart(request):
    cart = get_cart(request)
    cart.items.all().delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Cart cleared successfully'})
    
    messages.success(request, 'Cart cleared successfully.')
    return redirect('cart:view')

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()
        cart = get_cart(request)
        
        # Validate coupon (implement your coupon logic here)
        if coupon_code:
            # Example: Check if coupon exists and is valid
            # You would have a Coupon model to validate against
            cart.coupon_code = coupon_code
            cart.coupon_discount = 100  # Example discount amount
            cart.save()
            
            messages.success(request, f'Coupon "{coupon_code}" applied successfully!')
        else:
            messages.error(request, 'Please enter a coupon code.')
        
        return redirect('cart:view')
    
    return redirect('cart:view')

@login_required
def remove_coupon(request):
    cart = get_cart(request)
    cart.coupon_code = ''
    cart.coupon_discount = 0
    cart.save()
    
    messages.success(request, 'Coupon removed successfully.')
    return redirect('cart:view')