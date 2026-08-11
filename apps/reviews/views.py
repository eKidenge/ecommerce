from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from apps.products.models import Product
from .models import Review, ReviewHelpful
from .forms import ReviewForm

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check if user already reviewed
    existing_review = Review.objects.filter(product=product, user=request.user).first()
    if existing_review:
        messages.info(request, 'You have already reviewed this product.')
        return redirect('products:product_detail', slug=product.slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_verified = request.user.is_email_verified
            review.save()
            
            # Update product rating
            product.average_rating = Review.objects.filter(
                product=product, is_approved=True
            ).aggregate(models.Avg('rating'))['rating__avg'] or 0
            product.total_reviews = Review.objects.filter(
                product=product, is_approved=True
            ).count()
            product.save()
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('products:product_detail', slug=product.slug)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/review_form.html', {'form': form, 'product': product})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('products:product_detail', slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'reviews/review_edit.html', {'form': form, 'review': review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        product = review.product
        review.delete()
        
        # Update product rating
        product.average_rating = Review.objects.filter(
            product=product, is_approved=True
        ).aggregate(models.Avg('rating'))['rating__avg'] or 0
        product.total_reviews = Review.objects.filter(
            product=product, is_approved=True
        ).count()
        product.save()
        
        messages.success(request, 'Review deleted successfully!')
        return redirect('products:product_detail', slug=product.slug)
    
    return render(request, 'reviews/review_delete.html', {'review': review})

@login_required
def helpful_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    helpful_vote, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user,
        defaults={'is_helpful': True}
    )
    
    if not created:
        helpful_vote.is_helpful = not helpful_vote.is_helpful
        helpful_vote.save()
    
    # Update helpful count
    review.helpful_count = ReviewHelpful.objects.filter(
        review=review, is_helpful=True
    ).count()
    review.save()
    
    return JsonResponse({
        'success': True,
        'helpful_count': review.helpful_count,
        'is_helpful': helpful_vote.is_helpful
    })

# Add this to existing views.py

def product_reviews(request, product_id):
    from apps.products.models import Product
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = Review.objects.filter(product=product, is_approved=True).order_by('-created_at')
    
    context = {
        'product': product,
        'reviews': reviews,
        'total_reviews': reviews.count(),
    }
    return render(request, 'reviews/review_list.html', context)