from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
import uuid
import json

class User(AbstractUser):
    USER_TYPES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
    )
    
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')],
        blank=True
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    profile_picture = models.ImageField(upload_to='users/profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Account status
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    
    # Timestamps
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    currency = models.CharField(max_length=3, default='KES')
    language = models.CharField(max_length=10, default='en')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Vendor specific fields
    store_name = models.CharField(max_length=200, blank=True)
    store_description = models.TextField(blank=True)
    store_logo = models.ImageField(upload_to='stores/logos/', null=True, blank=True)
    store_banner = models.ImageField(upload_to='stores/banners/', null=True, blank=True)
    is_store_active = models.BooleanField(default=False)
    
    # Business details for vendors
    business_license = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    
    # Security
    two_factor_enabled = models.BooleanField(default=False)
    device_tokens = models.JSONField(default=list, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reset_token = models.UUIDField(null=True, blank=True)
    reset_token_expires = models.DateTimeField(null=True, blank=True)
    
    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True)
    
    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['user_type']),
            models.Index(fields=['is_active', 'is_blocked']),
        ]

    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def is_vendor(self):
        return self.user_type == 'vendor'
    
    @property
    def is_customer(self):
        return self.user_type == 'customer'
    
    @property
    def is_moderator(self):
        return self.user_type in ['moderator', 'admin']
    
    def lock_account(self, duration_minutes=30):
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.is_active = False
        self.save()
    
    def unlock_account(self):
        self.locked_until = None
        self.is_active = True
        self.failed_login_attempts = 0
        self.save()
    
    def generate_reset_token(self):
        self.reset_token = uuid.uuid4()
        self.reset_token_expires = timezone.now() + timezone.timedelta(hours=24)
        self.save()
        return self.reset_token

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    website = models.URLField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    notification_settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"

class Address(models.Model):
    ADDRESS_TYPES = (
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
        ('both', 'Both'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='both')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = 'Addresses'
    
    def __str__(self):
        return f"{self.user.email} - {self.address_line1}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class UserActivityLog(models.Model):
    ACTION_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('registration', 'Registration'),
        ('password_change', 'Password Change'),
        ('profile_update', 'Profile Update'),
        ('order_placed', 'Order Placed'),
        ('payment_made', 'Payment Made'),
        ('review_added', 'Review Added'),
        ('product_added', 'Product Added'),
        ('product_updated', 'Product Updated'),
        ('product_deleted', 'Product Deleted'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.created_at}"