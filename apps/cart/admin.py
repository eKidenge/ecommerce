from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('unit_price', 'subtotal')
    fields = ('product', 'variant', 'quantity', 'unit_price', 'subtotal')
    can_delete = True

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'total_items', 'total_price', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__username', 'session_key')
    readonly_fields = ('created_at', 'updated_at', 'subtotal', 'total_discount', 'total_price', 'grand_total')
    inlines = [CartItemInline]
    fieldsets = (
        ('Cart Information', {
            'fields': ('user', 'session_key')
        }),
        ('Coupon', {
            'fields': ('coupon_code', 'coupon_discount')
        }),
        ('Totals', {
            'fields': ('subtotal', 'total_discount', 'total_price', 'shipping_cost', 'grand_total'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'variant', 'quantity', 'unit_price', 'subtotal', 'created_at')
    list_filter = ('created_at', 'product__category')
    search_fields = ('product__name', 'product__sku', 'cart__user__email')
    readonly_fields = ('subtotal', 'created_at', 'updated_at')
    fields = ('cart', 'product', 'variant', 'quantity', 'unit_price')