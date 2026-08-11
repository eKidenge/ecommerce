from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductImage, ProductVariant, ProductReview

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active', 'is_featured', 'order']
    list_filter = ['is_active', 'is_featured', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'compare_price', 'stock', 'category', 'vendor', 'is_active', 'is_featured', 'average_rating']
    list_filter = ['is_active', 'is_featured', 'is_best_seller', 'is_on_sale', 'category', 'brand', 'vendor', 'condition']
    search_fields = ['name', 'sku', 'description', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['average_rating', 'total_reviews', 'total_sales', 'views_count', 'created_at', 'updated_at']
    inlines = [ProductImageInline, ProductVariantInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        ('Categories & Brand', {
            'fields': ('category', 'brand')
        }),
        ('Vendor & Stock', {
            'fields': ('vendor', 'stock', 'min_stock_level', 'condition')
        }),
        ('Shipping', {
            'fields': ('weight', 'dimensions')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'is_best_seller', 'is_on_sale')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_reviews', 'total_sales', 'views_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_verified', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_verified', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    readonly_fields = ['helpful_count', 'created_at', 'updated_at']