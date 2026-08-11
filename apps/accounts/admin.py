from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, Address, UserActivityLog

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'full_name', 'user_type', 'is_active', 'is_email_verified', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_email_verified', 'is_blocked')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 'bio')}),
        (_('Address'), {'fields': ('address', 'city', 'state', 'country', 'postal_code')}),
        (_('User Type'), {'fields': ('user_type',)}),
        (_('Vendor Details'), {'fields': ('store_name', 'store_description', 'store_logo', 'store_banner', 
                                         'is_store_active', 'business_license', 'tax_id', 'bank_account', 'bank_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Account Status'), {'fields': ('is_email_verified', 'is_phone_verified', 'is_blocked', 'is_banned')}),
        (_('Security'), {'fields': ('two_factor_enabled', 'failed_login_attempts', 'locked_until')}),
        (_('Preferences'), {'fields': ('currency', 'language', 'email_notifications', 'sms_notifications')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'user_type'),
        }),
    )

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line1', 'city', 'country', 'address_type', 'is_default')
    list_filter = ('address_type', 'is_default', 'country')
    search_fields = ('user__email', 'address_line1', 'city')

class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__email', 'description')
    readonly_fields = ('created_at',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserActivityLog, UserActivityLogAdmin)