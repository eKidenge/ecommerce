from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'user', 'payment_method', 'amount', 'status', 'transaction_id', 'created_at')
    list_filter = ('payment_method', 'status', 'currency', 'created_at')
    search_fields = ('transaction_id', 'payment_intent_id', 'mpesa_receipt', 'order__order_number', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'user', 'payment_method', 'amount', 'currency', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'payment_intent_id')
        }),
        ('M-Pesa Details', {
            'fields': ('mpesa_receipt', 'mpesa_phone', 'mpesa_checkout_request_id'),
            'classes': ('collapse',)
        }),
        ('Response Data', {
            'fields': ('response_data', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )