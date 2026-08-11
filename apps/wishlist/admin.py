from django.contrib import admin
from .models import Wishlist, WishlistItem

class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    fields = ('product', 'added_at')
    readonly_fields = ('added_at',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    inlines = [WishlistItemInline]

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'wishlist', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('wishlist__user__email', 'product__name')