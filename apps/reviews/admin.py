from django.contrib import admin
from .models import Review, ReviewHelpful

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'title', 'is_verified', 'is_approved', 'helpful_count', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__email', 'user__username', 'title', 'comment')
    readonly_fields = ('helpful_count', 'created_at', 'updated_at')
    actions = ['approve_reviews', 'unapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = 'Approve selected reviews'
    
    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_reviews.short_description = 'Unapprove selected reviews'

@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')
    search_fields = ('review__product__name', 'user__email')