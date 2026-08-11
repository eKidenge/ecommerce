from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.products.models import Product, Category, Brand, ProductImage, ProductReview
from apps.accounts.models import User, Address
from apps.payments.models import Payment
from apps.cart.models import Cart
from apps.wishlist.models import Wishlist, WishlistItem
from apps.notifications.models import Notification

# ============================================
# CUSTOMER DASHBOARD VIEWS
# ============================================

@login_required
def customer_dashboard(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')[:10]
    
    # Stats
    total_orders = Order.objects.filter(user=user).count()
    total_spent = Order.objects.filter(user=user, payment_status='paid').aggregate(
        Sum('total_amount')
    )['total_amount__sum'] or 0
    
    pending_orders = Order.objects.filter(user=user, status='pending').count()
    shipped_orders = Order.objects.filter(user=user, status='shipped').count()
    
    # Wishlist count
    wishlist_count = 0
    try:
        wishlist_count = user.wishlist.items.count()
    except:
        pass
    
    # Review count
    review_count = ProductReview.objects.filter(user=user).count()
    
    # Recent orders
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Wishlist items
    wishlist_items = []
    try:
        wishlist_items = user.wishlist.items.all().select_related('product')[:3]
    except:
        pass
    
    context = {
        'user': user,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'pending_orders': pending_orders,
        'shipped_orders': shipped_orders,
        'wishlist_count': wishlist_count,
        'review_count': review_count,
        'recent_orders': recent_orders,
        'orders': orders,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'dashboard/customer/dashboard.html', context)

@login_required
def customer_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(orders, 10)
    page = request.GET.get('page', 1)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/customer/orders.html', {'orders': orders})

@login_required
def customer_wishlist(request):
    return redirect('wishlist:view')

@login_required
def customer_profile(request):
    return redirect('accounts:profile')

@login_required
def customer_addresses(request):
    addresses = request.user.addresses.filter(is_active=True)
    return render(request, 'dashboard/customer/addresses.html', {'addresses': addresses})

@login_required
def customer_security(request):
    return render(request, 'dashboard/customer/security.html')


# ============================================
# ADMIN DASHBOARD VIEWS
# ============================================

def is_admin(user):
    return user.is_staff or user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get date range
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Stats
    total_users = User.objects.count()
    total_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(
        payment_status='paid'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    # Monthly stats
    monthly_orders = Order.objects.filter(
        created_at__gte=start_date
    ).count()
    monthly_revenue = Order.objects.filter(
        created_at__gte=start_date,
        payment_status='paid'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Top products
    top_products = Product.objects.filter(is_active=True).order_by('-total_sales')[:10]
    
    # Recent users
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Total reviews
    total_reviews = ProductReview.objects.count()
    
    # Total payments
    total_payments = Payment.objects.count()
    
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'monthly_orders': monthly_orders,
        'monthly_revenue': monthly_revenue,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'recent_users': recent_users,
        'total_reviews': total_reviews,
        'total_payments': total_payments,
    }
    return render(request, 'dashboard/admin/dashboard.html', context)


# ============================================
# ADMIN USER MANAGEMENT (CRUD)
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    
    # Search and filter
    search_query = request.GET.get('q')
    role_filter = request.GET.get('role')
    status_filter = request.GET.get('status')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if role_filter:
        users = users.filter(user_type=role_filter)
    
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True, is_blocked=False)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
        elif status_filter == 'blocked':
            users = users.filter(is_blocked=True)
    
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    
    context = {
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/admin/users.html', context)

@login_required
@user_passes_test(is_admin)
def admin_users_add(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('dashboard:admin_users_add')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('dashboard:admin_users_add')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            is_active=True
        )
        
        messages.success(request, f'User {username} created successfully!')
        return redirect('dashboard:admin_users')
    
    return render(request, 'dashboard/admin/users_add.html')

@login_required
@user_passes_test(is_admin)
def admin_users_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.user_type = request.POST.get('user_type')
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_blocked = request.POST.get('is_blocked') == 'on'
        
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        user.save()
        messages.success(request, f'User {user.username} updated successfully!')
        return redirect('dashboard:admin_users')
    
    return render(request, 'dashboard/admin/users_edit.html', {'edit_user': user})

@login_required
@user_passes_test(is_admin)
def admin_users_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('dashboard:admin_users')
    
    return render(request, 'dashboard/admin/users_delete.html', {'delete_user': user})

@login_required
@user_passes_test(is_admin)
def admin_users_block(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_blocked = True
        user.is_active = False
        user.save()
        messages.success(request, f'User {user.username} has been blocked.')
        return redirect('dashboard:admin_users')
    
    return redirect('dashboard:admin_users')

@login_required
@user_passes_test(is_admin)
def admin_users_unblock(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_blocked = False
        user.is_active = True
        user.save()
        messages.success(request, f'User {user.username} has been unblocked.')
        return redirect('dashboard:admin_users')
    
    return redirect('dashboard:admin_users')


# ============================================
# ADMIN PRODUCT MANAGEMENT (CRUD)
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_products(request):
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.filter(is_active=True)
    
    # Search and filter
    search_query = request.GET.get('q')
    category_filter = request.GET.get('category')
    status_filter = request.GET.get('status')
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    if status_filter:
        if status_filter == 'active':
            products = products.filter(is_active=True)
        elif status_filter == 'inactive':
            products = products.filter(is_active=False)
    
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/admin/products.html', context)

@login_required
@user_passes_test(is_admin)
def admin_products_add(request):
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    vendors = User.objects.filter(user_type='vendor', is_active=True)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        short_description = request.POST.get('short_description')
        price = request.POST.get('price')
        compare_price = request.POST.get('compare_price')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        vendor_id = request.POST.get('vendor')
        stock = request.POST.get('stock')
        sku = request.POST.get('sku')
        is_active = request.POST.get('is_active') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        is_best_seller = request.POST.get('is_best_seller') == 'on'
        condition = request.POST.get('condition')
        
        product = Product.objects.create(
            name=name,
            description=description,
            short_description=short_description,
            price=price,
            compare_price=compare_price or None,
            category_id=category_id,
            brand_id=brand_id or None,
            vendor_id=vendor_id,
            stock=stock,
            sku=sku,
            is_active=is_active,
            is_featured=is_featured,
            is_best_seller=is_best_seller,
            condition=condition
        )
        
        # Handle product images
        images = request.FILES.getlist('images')
        for i, image in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=(i == 0),
                order=i
            )
        
        messages.success(request, f'Product {product.name} created successfully!')
        return redirect('dashboard:admin_products')
    
    context = {
        'categories': categories,
        'brands': brands,
        'vendors': vendors,
    }
    return render(request, 'dashboard/admin/products_add.html', context)

@login_required
@user_passes_test(is_admin)
def admin_products_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    vendors = User.objects.filter(user_type='vendor', is_active=True)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.short_description = request.POST.get('short_description')
        product.price = request.POST.get('price')
        product.compare_price = request.POST.get('compare_price') or None
        product.category_id = request.POST.get('category')
        product.brand_id = request.POST.get('brand') or None
        product.vendor_id = request.POST.get('vendor')
        product.stock = request.POST.get('stock')
        product.sku = request.POST.get('sku')
        product.is_active = request.POST.get('is_active') == 'on'
        product.is_featured = request.POST.get('is_featured') == 'on'
        product.is_best_seller = request.POST.get('is_best_seller') == 'on'
        product.condition = request.POST.get('condition')
        product.save()
        
        messages.success(request, f'Product {product.name} updated successfully!')
        return redirect('dashboard:admin_products')
    
    context = {
        'product': product,
        'categories': categories,
        'brands': brands,
        'vendors': vendors,
    }
    return render(request, 'dashboard/admin/products_edit.html', context)

@login_required
@user_passes_test(is_admin)
def admin_products_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product {name} deleted successfully!')
        return redirect('dashboard:admin_products')
    
    return render(request, 'dashboard/admin/products_delete.html', {'product': product})


# ============================================
# ADMIN ORDER MANAGEMENT
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    
    # Search and filter
    search_query = request.GET.get('q')
    status_filter = request.GET.get('status')
    payment_filter = request.GET.get('payment')
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if payment_filter:
        orders = orders.filter(payment_status=payment_filter)
    
    # Get total orders count for header
    total_orders = orders.count()
    
    paginator = Paginator(orders, 20)
    page = request.GET.get('page', 1)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'search_query': search_query,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
    }
    return render(request, 'dashboard/admin/orders.html', context)

@login_required
@user_passes_test(is_admin)
def admin_orders_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'dashboard/admin/orders_detail.html', {'order': order})

@login_required
@user_passes_test(is_admin)
def admin_orders_update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        note = request.POST.get('note', '')
        
        order.status = new_status
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            note=note,
            created_by=request.user
        )
        
        messages.success(request, f'Order #{order.order_number} status updated to {order.get_status_display()}')
        return redirect('dashboard:admin_orders_detail', order_id=order.id)
    
    return render(request, 'dashboard/admin/orders_update_status.html', {'order': order})


# ============================================
# ADMIN PAYMENT MANAGEMENT
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_payments(request):
    payments = Payment.objects.all().order_by('-created_at')
    
    # Search and filter
    search_query = request.GET.get('q')
    status_filter = request.GET.get('status')
    method_filter = request.GET.get('method')
    
    if search_query:
        payments = payments.filter(
            Q(transaction_id__icontains=search_query) |
            Q(order__order_number__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    # Stats
    total_payments = payments.count()
    total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    completed_payments = payments.filter(status='completed').count()
    pending_payments = payments.filter(status='pending').count()
    
    paginator = Paginator(payments, 20)
    page = request.GET.get('page', 1)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)
    
    context = {
        'payments': payments,
        'total_payments': total_payments,
        'total_amount': total_amount,
        'completed_payments': completed_payments,
        'pending_payments': pending_payments,
        'search_query': search_query,
        'status_filter': status_filter,
        'method_filter': method_filter,
    }
    return render(request, 'dashboard/admin/payments.html', context)

@login_required
@user_passes_test(is_admin)
def admin_payments_detail(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    data = {
        'transaction_id': payment.transaction_id,
        'order_number': payment.order.order_number,
        'customer_name': payment.user.full_name,
        'customer_email': payment.user.email,
        'amount': str(payment.amount),
        'payment_method_display': payment.get_payment_method_display(),
        'status_display': payment.get_status_display(),
        'mpesa_receipt': payment.mpesa_receipt or 'N/A',
        'created_at': payment.created_at.strftime('%Y-%m-%d %H:%M'),
        'completed_at': payment.completed_at.strftime('%Y-%m-%d %H:%M') if payment.completed_at else 'Not completed',
        'error_message': payment.error_message or '',
    }
    return JsonResponse(data)

@login_required
@user_passes_test(is_admin)
def admin_payments_update_status(request, payment_id, status):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        payment.status = status
        if status == 'completed':
            payment.completed_at = timezone.now()
        payment.save()
        
        # Update order payment status
        if status == 'completed':
            payment.order.payment_status = 'paid'
            payment.order.paid_at = timezone.now()
            payment.order.save()
        elif status == 'refunded':
            payment.order.payment_status = 'refunded'
            payment.order.save()
        
        messages.success(request, f'Payment status updated to {payment.get_status_display()}')
        return redirect('dashboard:admin_payments')
    
    return redirect('dashboard:admin_payments')


# ============================================
# ADMIN REVIEW MANAGEMENT
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_reviews(request):
    reviews = ProductReview.objects.all().order_by('-created_at')
    
    # Search and filter
    search_query = request.GET.get('q')
    status_filter = request.GET.get('status')
    rating_filter = request.GET.get('rating')
    verified_filter = request.GET.get('verified')
    
    if search_query:
        reviews = reviews.filter(
            Q(product__name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(comment__icontains=search_query)
        )
    
    if status_filter:
        if status_filter == 'approved':
            reviews = reviews.filter(is_approved=True)
        elif status_filter == 'pending':
            reviews = reviews.filter(is_approved=False)
        elif status_filter == 'rejected':
            reviews = reviews.filter(is_approved=False, is_verified=False)
    
    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)
    
    if verified_filter == 'verified':
        reviews = reviews.filter(is_verified=True)
    elif verified_filter == 'unverified':
        reviews = reviews.filter(is_verified=False)
    
    # Stats
    total_reviews = reviews.count()
    approved_reviews = reviews.filter(is_approved=True).count()
    pending_reviews = reviews.filter(is_approved=False).count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page', 1)
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
    
    context = {
        'reviews': reviews,
        'total_reviews': total_reviews,
        'approved_reviews': approved_reviews,
        'pending_reviews': pending_reviews,
        'average_rating': average_rating,
        'search_query': search_query,
        'status_filter': status_filter,
        'rating_filter': rating_filter,
        'verified_filter': verified_filter,
    }
    return render(request, 'dashboard/admin/reviews.html', context)

@login_required
@user_passes_test(is_admin)
def admin_reviews_detail(request, review_id):
    """Get review details as JSON"""
    review = get_object_or_404(ProductReview, id=review_id)
    data = {
        'product_name': review.product.name,
        'user_name': review.user.full_name,
        'user_email': review.user.email,
        'rating': review.rating,
        'title': review.title,
        'comment': review.comment,
        'pros': review.pros,
        'cons': review.cons,
        'is_approved': review.is_approved,
        'is_verified': review.is_verified,
        'helpful_count': review.helpful_count,
        'created_at': review.created_at.strftime('%Y-%m-%d %H:%M'),
        'images': review.images,
    }
    return JsonResponse(data)

@login_required
@user_passes_test(is_admin)
def admin_reviews_approve(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id)
    
    if request.method == 'POST':
        review.is_approved = True
        review.save()
        
        # Update product rating
        product = review.product
        avg_rating = product.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0
        product.average_rating = avg_rating
        product.total_reviews = product.reviews.filter(is_approved=True).count()
        product.save()
        
        messages.success(request, 'Review approved successfully!')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)

@login_required
@user_passes_test(is_admin)
def admin_reviews_reject(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id)
    
    if request.method == 'POST':
        review.is_approved = False
        review.save()
        
        # Update product rating
        product = review.product
        avg_rating = product.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0
        product.average_rating = avg_rating
        product.total_reviews = product.reviews.filter(is_approved=True).count()
        product.save()
        
        messages.success(request, 'Review rejected successfully!')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)

@login_required
@user_passes_test(is_admin)
def admin_reviews_delete(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id)
    
    if request.method == 'POST':
        product = review.product
        review.delete()
        
        # Update product rating
        avg_rating = product.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0
        product.average_rating = avg_rating
        product.total_reviews = product.reviews.filter(is_approved=True).count()
        product.save()
        
        messages.success(request, 'Review deleted successfully!')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)


# ============================================
# ADMIN WISHLIST MANAGEMENT
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_wishlists(request):
    wishlists = Wishlist.objects.all().order_by('-created_at')
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        wishlists = wishlists.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    
    # Stats
    total_wishlists = wishlists.count()
    total_items = WishlistItem.objects.count()
    
    # Most wishlisted product
    top_product = WishlistItem.objects.values('product__name').annotate(
        count=Count('product')
    ).order_by('-count').first()
    
    paginator = Paginator(wishlists, 20)
    page = request.GET.get('page', 1)
    try:
        wishlists = paginator.page(page)
    except PageNotAnInteger:
        wishlists = paginator.page(1)
    except EmptyPage:
        wishlists = paginator.page(paginator.num_pages)
    
    context = {
        'wishlists': wishlists,
        'total_wishlists': total_wishlists,
        'total_items': total_items,
        'top_product_name': top_product['product__name'] if top_product else 'N/A',
        'search_query': search_query,
    }
    return render(request, 'dashboard/admin/wishlist.html', context)

@login_required
@user_passes_test(is_admin)
def admin_wishlists_detail(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id)
    data = {
        'user_name': wishlist.user.full_name,
        'user_email': wishlist.user.email,
        'total_items': wishlist.total_items,
        'created_at': wishlist.created_at.strftime('%Y-%m-%d %H:%M'),
        'items': [
            {
                'id': item.id,
                'product_name': item.product.name,
                'price': str(item.product.price),
                'added_at': item.added_at.strftime('%Y-%m-%d %H:%M'),
            }
            for item in wishlist.items.all()
        ]
    }
    return JsonResponse(data)

@login_required
@user_passes_test(is_admin)
def admin_wishlists_item_remove(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(WishlistItem, id=item_id)
        item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
@user_passes_test(is_admin)
def admin_wishlists_delete(request, wishlist_id):
    if request.method == 'POST':
        wishlist = get_object_or_404(Wishlist, id=wishlist_id)
        wishlist.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


# ============================================
# ADMIN NOTIFICATION MANAGEMENT
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_notifications(request):
    notifications = Notification.objects.all().order_by('-created_at')
    
    # Search and filter
    search_query = request.GET.get('q')
    type_filter = request.GET.get('type')
    status_filter = request.GET.get('status')
    
    if search_query:
        notifications = notifications.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    if type_filter:
        notifications = notifications.filter(type=type_filter)
    
    if status_filter == 'read':
        notifications = notifications.filter(is_read=True)
    elif status_filter == 'unread':
        notifications = notifications.filter(is_read=False)
    
    # Stats
    total_notifications = Notification.objects.count()
    unread_count = Notification.objects.filter(is_read=False).count()
    read_count = Notification.objects.filter(is_read=True).count()
    unique_users = Notification.objects.values('user').distinct().count()
    
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page', 1)
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)
    
    # All users for send notification
    all_users = User.objects.filter(is_active=True)
    
    context = {
        'notifications': notifications,
        'total_notifications': total_notifications,
        'unread_count': unread_count,
        'read_count': read_count,
        'unique_users': unique_users,
        'all_users': all_users,
        'search_query': search_query,
        'type_filter': type_filter,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/admin/notifications.html', context)

@login_required
@user_passes_test(is_admin)
def admin_notifications_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    data = {
        'user_name': notification.user.full_name,
        'user_email': notification.user.email,
        'type_display': notification.get_type_display(),
        'title': notification.title,
        'message': notification.message,
        'is_read': notification.is_read,
        'link': notification.link,
        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
        'metadata': notification.metadata,
    }
    return JsonResponse(data)

@login_required
@user_passes_test(is_admin)
def admin_notifications_mark_read(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id)
        notification.mark_as_read()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
@user_passes_test(is_admin)
def admin_notifications_delete(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id)
        notification.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
@user_passes_test(is_admin)
def admin_notifications_send(request):
    if request.method == 'POST':
        notification_type = request.POST.get('type')
        user_id = request.POST.get('user_id')
        title = request.POST.get('title')
        message = request.POST.get('message')
        link = request.POST.get('link', '')
        
        if user_id:
            # Send to specific user
            user = get_object_or_404(User, id=user_id)
            Notification.objects.create(
                user=user,
                type=notification_type,
                title=title,
                message=message,
                link=link
            )
            messages.success(request, f'Notification sent to {user.full_name}')
        else:
            # Send to all users
            users = User.objects.filter(is_active=True)
            count = 0
            for user in users:
                Notification.objects.create(
                    user=user,
                    type=notification_type,
                    title=title,
                    message=message,
                    link=link
                )
                count += 1
            messages.success(request, f'Notification sent to {count} users')
        
        return redirect('dashboard:admin_notifications')
    
    return redirect('dashboard:admin_notifications')


# ============================================
# ADMIN REPORTS
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    # Get period
    period = request.GET.get('period', 'week')
    start_date = None
    end_date = timezone.now()
    
    if period == 'today':
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_date = end_date - timedelta(days=7)
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
    elif period == 'quarter':
        start_date = end_date - timedelta(days=90)
    elif period == 'year':
        start_date = end_date - timedelta(days=365)
    elif period == 'custom':
        start_date_str = request.GET.get('start')
        end_date_str = request.GET.get('end')
        if start_date_str and end_date_str:
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
            except:
                start_date = end_date - timedelta(days=30)
    
    # Stats
    total_revenue = Order.objects.filter(payment_status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = Order.objects.count()
    total_customers = User.objects.filter(user_type='customer').count()
    total_products = Product.objects.filter(is_active=True).count()
    average_order_value = Order.objects.filter(payment_status='paid').aggregate(Avg('total_amount'))['total_amount__avg'] or 0
    conversion_rate = 0
    
    # Top products
    top_products = Product.objects.filter(is_active=True).order_by('-total_sales')[:10]
    
    # Top categories
    from django.db.models import Sum, F
    top_categories = Category.objects.annotate(
        product_count=Count('products'),
        total_revenue=Sum('products__total_sales') * F('products__price')
    ).order_by('-total_revenue')[:5]
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    # Payment methods distribution
    payment_methods = Payment.objects.values('payment_method').annotate(
        count=Count('id')
    )
    payment_labels = []
    payment_data = []
    for method in payment_methods:
        payment_labels.append(method['payment_method'].title())
        payment_data.append(method['count'])
    
    # Charts data
    revenue_labels = []
    revenue_data = []
    orders_labels = []
    orders_data = []
    customer_labels = []
    customer_data = []
    
    if start_date:
        # Generate daily data for charts
        days = (end_date - start_date).days
        for i in range(days + 1):
            day = start_date + timedelta(days=i)
            day_str = day.strftime('%b %d')
            
            # Revenue data
            day_revenue = Order.objects.filter(
                created_at__date=day.date(),
                payment_status='paid'
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            revenue_labels.append(day_str)
            revenue_data.append(float(day_revenue))
            
            # Orders data
            day_orders = Order.objects.filter(created_at__date=day.date()).count()
            orders_labels.append(day_str)
            orders_data.append(day_orders)
            
            # Customer data
            day_customers = User.objects.filter(date_joined__date=day.date()).count()
            customer_labels.append(day_str)
            customer_data.append(day_customers)
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'average_order_value': average_order_value,
        'conversion_rate': conversion_rate,
        'top_products': top_products,
        'top_categories': top_categories,
        'recent_orders': recent_orders,
        'payment_labels': payment_labels,
        'payment_data': payment_data,
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        'orders_labels': orders_labels,
        'orders_data': orders_data,
        'customer_labels': customer_labels,
        'customer_data': customer_data,
    }
    return render(request, 'dashboard/admin/reports.html', context)


# ============================================
# VENDOR DASHBOARD VIEWS
# ============================================

@login_required
def vendor_dashboard(request):
    if not request.user.is_vendor:
        messages.error(request, 'Access denied. Vendor area only.')
        return redirect('products:home')
    
    products = Product.objects.filter(vendor=request.user)
    
    # Get orders containing vendor products
    from apps.orders.models import Order
    orders = Order.objects.filter(items__product__in=products).distinct()
    
    # Stats
    total_products = products.count()
    total_orders = orders.count()
    total_revenue = orders.filter(payment_status='paid').aggregate(
        Sum('total_amount')
    )['total_amount__sum'] or 0
    total_customers = orders.values('user').distinct().count()
    
    # Recent products
    recent_products = products.order_by('-created_at')[:5]
    
    # Recent orders
    recent_orders = orders.order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'recent_products': recent_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/vendor/dashboard.html', context)

@login_required
def vendor_products(request):
    if not request.user.is_vendor:
        messages.error(request, 'Access denied.')
        return redirect('products:home')
    
    products = Product.objects.filter(vendor=request.user).order_by('-created_at')
    
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/vendor/products.html', {'products': products})

@login_required
def vendor_orders(request):
    if not request.user.is_vendor:
        messages.error(request, 'Access denied.')
        return redirect('products:home')
    
    from apps.products.models import Product
    from apps.orders.models import Order
    
    products = Product.objects.filter(vendor=request.user)
    orders = Order.objects.filter(items__product__in=products).distinct().order_by('-created_at')
    
    paginator = Paginator(orders, 20)
    page = request.GET.get('page', 1)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/vendor/orders.html', {'orders': orders})

@login_required
def vendor_analytics(request):
    if not request.user.is_vendor:
        messages.error(request, 'Access denied.')
        return redirect('products:home')
    
    from apps.products.models import Product
    from apps.orders.models import Order
    from django.db.models import Sum, Count
    
    products = Product.objects.filter(vendor=request.user)
    
    # Last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    orders = Order.objects.filter(
        items__product__in=products,
        created_at__gte=start_date,
        payment_status='paid'
    ).distinct()
    
    total_sales = orders.count()
    total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    top_products = products.order_by('-total_sales')[:10]
    recent_orders = orders.order_by('-created_at')[:10]
    
    context = {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'top_products': top_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/vendor/analytics.html', context)

@login_required
def vendor_settings(request):
    if not request.user.is_vendor:
        messages.error(request, 'Access denied.')
        return redirect('products:home')
    
    if request.method == 'POST':
        # Update vendor settings
        store_name = request.POST.get('store_name')
        store_description = request.POST.get('store_description')
        is_store_active = request.POST.get('is_store_active') == 'on'
        business_license = request.POST.get('business_license')
        tax_id = request.POST.get('tax_id')
        bank_account = request.POST.get('bank_account')
        bank_name = request.POST.get('bank_name')
        
        user = request.user
        user.store_name = store_name
        user.store_description = store_description
        user.is_store_active = is_store_active
        user.business_license = business_license
        user.tax_id = tax_id
        user.bank_account = bank_account
        user.bank_name = bank_name
        user.save()
        
        messages.success(request, 'Store settings updated successfully!')
        return redirect('dashboard:vendor_settings')
    
    return render(request, 'dashboard/vendor/settings.html', {'user': request.user})