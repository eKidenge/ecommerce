from django.db import models
from django.contrib.auth import get_user_model
from apps.orders.models import Order

User = get_user_model()

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('stripe', 'Stripe'),
        ('mpesa', 'M-Pesa'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
    )
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    payment_intent_id = models.CharField(max_length=100, blank=True)
    
    # M-Pesa specific fields
    mpesa_receipt = models.CharField(max_length=50, blank=True)
    mpesa_phone = models.CharField(max_length=15, blank=True)
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True)
    
    # Response data
    response_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.transaction_id or self.id} - {self.amount} {self.currency}"