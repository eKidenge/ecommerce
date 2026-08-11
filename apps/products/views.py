from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg, Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, Category, Brand, ProductReview, ProductImage
from .forms import ProductReviewForm

@cache_page(60 * 15)
@vary_on_cookie
def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    best_sellers = Product.objects.filter(is_active=True, is_best_seller=True)[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True, is_featured=True)[:6]
    brands = Brand.objects.filter(is_active=True)[:6]
    
    context = {
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'home.html', context)

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Filter by brand
    brand_slug = request.GET.get('brand')
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=brand)
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
    
    # Filter by price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Filter by rating
    min_rating = request.GET.get('min_rating')
    if min_rating:
        products = products.filter(average_rating__gte=min_rating)
    
    # Filter by condition
    condition = request.GET.get('condition')
    if condition:
        products = products.filter(condition=condition)
    
    # Filter by in stock
    in_stock = request.GET.get('in_stock')
    if in_stock == 'true':
        products = products.filter(stock__gt=0)
    
    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    sort_options = {
        'price': 'price',
        '-price': '-price',
        'name': 'name',
        '-created_at': '-created_at',
        'rating': '-average_rating',
        'popularity': '-total_sales',
    }
    products = products.order_by(sort_options.get(sort_by, '-created_at'))
    
    # Pagination
    paginator = Paginator(products, 12)
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
        'brands': brands,
        'search_query': search_query,
        'sort_by': sort_by,
        'category_slug': category_slug,
        'brand_slug': brand_slug,
        'min_price': min_price,
        'max_price': max_price,
        'min_rating': min_rating,
        'condition': condition,
        'in_stock': in_stock,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Increment view count
    product.views_count += 1
    product.save(update_fields=['views_count'])
    
    # Get related products (same category)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    
    # Get reviews
    reviews = product.reviews.filter(is_approved=True)[:10]
    
    # Get variants
    variants = product.variants.filter(is_active=True)
    
    # Get images
    images = product.images.all()
    
    # Get average rating
    avg_rating = product.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Get rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = product.reviews.filter(is_approved=True, rating=i).count()
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'variants': variants,
        'images': images,
        'avg_rating': avg_rating,
        'rating_distribution': rating_distribution,
        'total_reviews': product.total_reviews,
    }
    return render(request, 'products/product_detail.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Get subcategories
    subcategories = category.children.filter(is_active=True)
    
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
    }
    return render(request, 'products/category.html', context)

def category_list(request):
    categories = Category.objects.filter(is_active=True, parent=None)
    return render(request, 'products/category_list.html', {'categories': categories})

def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query) |
        Q(brand__name__icontains=query)
    ) if query else []
    
    context = {
        'query': query,
        'products': products,
        'total_results': products.count() if query else 0,
    }
    return render(request, 'products/search_results.html', context)

def featured_products(request):
    products = Product.objects.filter(is_active=True, is_featured=True)
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'products/featured_products.html', {'products': products})

def new_arrivals(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'products/new_arrivals.html', {'products': products})

@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    # Check if user already reviewed
    if ProductReview.objects.filter(product=product, user=request.user).exists():
        messages.error(request, 'You have already reviewed this product.')
        return redirect('products:product_detail', slug=slug)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_verified = request.user.is_email_verified
            review.save()
            
            # Update product rating
            avg_rating = product.reviews.filter(is_approved=True).aggregate(
                Avg('rating')
            )['rating__avg'] or 0
            product.average_rating = avg_rating
            product.total_reviews = product.reviews.filter(is_approved=True).count()
            product.save()
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('products:product_detail', slug=slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductReviewForm()
    
    return render(request, 'products/add_review.html', {'form': form, 'product': product})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id, user=request.user)
    product = review.product
    
    if request.method == 'POST':
        review.delete()
        
        # Update product rating
        avg_rating = product.reviews.filter(is_approved=True).aggregate(
            Avg('rating')
        )['rating__avg'] or 0
        product.average_rating = avg_rating
        product.total_reviews = product.reviews.filter(is_approved=True).count()
        product.save()
        
        messages.success(request, 'Review deleted successfully.')
        return redirect('products:product_detail', slug=product.slug)
    
    return render(request, 'products/delete_review.html', {'review': review})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id, user=request.user)
    product = review.product
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            
            # Update product rating
            avg_rating = product.reviews.filter(is_approved=True).aggregate(
                Avg('rating')
            )['rating__avg'] or 0
            product.average_rating = avg_rating
            product.save()
            
            messages.success(request, 'Review updated successfully.')
            return redirect('products:product_detail', slug=product.slug)
    else:
        form = ProductReviewForm(instance=review)
    
    return render(request, 'products/edit_review.html', {'form': form, 'review': review, 'product': product})

@require_POST
def mark_review_helpful(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id)
    
    # You can implement helpful votes here
    # For now, just increment the count
    review.helpful_count += 1
    review.save()
    
    return JsonResponse({
        'success': True,
        'helpful_count': review.helpful_count
    })

def quick_view(request, product_id):
    """AJAX view for quick product preview"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    data = {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'price': str(product.price),
        'compare_price': str(product.compare_price) if product.compare_price else None,
        'description': product.short_description or product.description[:200],
        'image': product.images.first().image.url if product.images.exists() else None,
        'in_stock': product.in_stock,
        'average_rating': str(product.average_rating),
        'total_reviews': product.total_reviews,
    }
    
    return JsonResponse(data)

from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if email:
            try:
                # Check if already subscribed
                subscriber, created = NewsletterSubscriber.objects.get_or_create(
                    email=email,
                    defaults={'is_active': True}
                )
                
                if not created and subscriber.is_active:
                    messages.info(request, 'You are already subscribed to our newsletter.')
                elif not created and not subscriber.is_active:
                    subscriber.is_active = True
                    subscriber.save()
                    messages.success(request, 'You have been re-subscribed to our newsletter!')
                else:
                    messages.success(request, 'Thank you for subscribing to our newsletter!')
                
                # Send confirmation email (optional)
                try:
                    send_mail(
                        'Newsletter Subscription Confirmation',
                        f'Thank you for subscribing to our newsletter!\n\nYou will receive updates on new products and special offers.\n\nBest regards,\nE-Store Team',
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=True,
                    )
                except:
                    pass  # Don't fail if email fails
                
            except Exception as e:
                messages.error(request, 'Failed to subscribe. Please try again.')
        else:
            messages.error(request, 'Please enter a valid email address.')
        
        return HttpResponseRedirect(reverse('products:home'))
    
    return HttpResponseRedirect(reverse('products:home'))