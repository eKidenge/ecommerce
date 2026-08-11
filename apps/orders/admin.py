from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, OrderStatusHistory

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'sku', 'quantity', 'unit_price', 'total_price', 'discount_amount')
    fields = ('product', 'variant', 'product_name', 'sku', 'quantity', 'unit_price', 'total_price', 'discount_amount')
    can_delete = False

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('status', 'note', 'created_by', 'created_at')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'status', 'payment_status', 'created_at', 'order_actions')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__email', 'user__username', 'tracking_number')
    readonly_fields = ('order_number', 'subtotal', 'discount_amount', 'shipping_cost', 'tax_amount', 
                      'total_amount', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'cancelled_at')
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_id', 'paid_at')
        }),
        ('Shipping', {
            'fields': ('tracking_number', 'shipping_carrier', 'estimated_delivery', 'shipped_at', 'delivered_at')
        }),
        ('Totals', {
            'fields': ('subtotal', 'discount_amount', 'shipping_cost', 'tax_amount', 'total_amount')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
    
    def order_actions(self, obj):
        actions = []
        if obj.status == 'pending':
            actions.append(f'<a href="#" class="button" onclick="processOrder({obj.id})">Process</a>')
        if obj.status in ['pending', 'processing']:
            actions.append(f'<a href="#" class="button" onclick="cancelOrder({obj.id})">Cancel</a>')
        if obj.status == 'processing':
            actions.append(f'<a href="#" class="button" onclick="shipOrder({obj.id})">Ship</a>')
        if obj.status == 'shipped':
            actions.append(f'<a href="#" class="button" onclick="deliverOrder({obj.id})">Deliver</a>')
        return format_html(' '.join(actions))
    order_actions.short_description = 'Actions'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'unit_price', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__order_number', 'product_name', 'sku')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'note', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'note')
    readonly_fields = ('created_at',)