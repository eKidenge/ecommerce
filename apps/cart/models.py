from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    coupon_code = models.CharField(max_length=50, blank=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart - {self.user.username if self.user else self.session_key}"
    
    @property
    def total_items(self):
        return self.items.count()
    
    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def total_discount(self):
        return sum(item.discount_amount for item in self.items.all()) + float(self.coupon_discount)
    
    @property
    def total_price(self):
        return self.subtotal - self.total_discount
    
    @property
    def shipping_cost(self):
        # Calculate shipping based on total price
        if self.total_price >= 1000:
            return 0
        return 100
    
    @property
    def grand_total(self):
        return self.total_price + self.shipping_cost

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'product', 'variant']
    
    def __str__(self):
        variant_text = f" - {self.variant}" if self.variant else ""
        return f"{self.quantity} x {self.product.name}{variant_text}"
    
    @property
    def subtotal(self):
        return self.unit_price * self.quantity
    
    @property
    def discount_amount(self):
        if self.product.compare_price and self.product.compare_price > self.unit_price:
            return (self.product.compare_price - self.unit_price) * self.quantity
        return 0