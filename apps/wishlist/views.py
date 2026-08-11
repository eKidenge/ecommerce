from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.products.models import Product
from .models import Wishlist, WishlistItem

@login_required
def view_wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.all().select_related('product')
    return render(request, 'wishlist/wishlist.html', {'items': items})

@login_required
@require_POST
def add_to_wishlist(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    
    if created:
        return JsonResponse({'success': True, 'message': 'Added to wishlist!'})
    else:
        return JsonResponse({'success': False, 'message': 'Already in wishlist'})

@login_required
@require_POST
def remove_from_wishlist(request):
    product_id = request.POST.get('product_id')
    wishlist = get_object_or_404(Wishlist, user=request.user)
    item = get_object_or_404(WishlistItem, wishlist=wishlist, product_id=product_id)
    item.delete()
    return JsonResponse({'success': True, 'message': 'Removed from wishlist'})

@login_required
def toggle_wishlist(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
    if item:
        item.delete()
        in_wishlist = False
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        in_wishlist = True
    
    return JsonResponse({
        'success': True,
        'in_wishlist': in_wishlist,
        'total_items': wishlist.total_items
    })

# Add these to existing views.py

@login_required
def move_to_cart(request, item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Add to cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=wishlist_item.product,
        defaults={
            'quantity': 1,
            'unit_price': wishlist_item.product.price
        }
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # Remove from wishlist
    wishlist_item.delete()
    
    messages.success(request, f'"{wishlist_item.product.name}" moved to cart!')
    return redirect('wishlist:view')

@login_required
def move_all_to_cart(request):
    wishlist = get_object_or_404(Wishlist, user=request.user)
    
    if wishlist.total_items == 0:
        messages.info(request, 'Your wishlist is empty.')
        return redirect('wishlist:view')
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Move all items to cart
    for item in wishlist.items.all():
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=item.product,
            defaults={
                'quantity': 1,
                'unit_price': item.product.price
            }
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    
    # Clear wishlist
    wishlist.items.all().delete()
    
    messages.success(request, 'All items moved to cart!')
    return redirect('cart:view')