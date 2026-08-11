from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # ============================================
    # CUSTOMER DASHBOARD
    # ============================================
    path('', views.customer_dashboard, name='customer_dashboard'),
    path('orders/', views.customer_orders, name='customer_orders'),
    path('wishlist/', views.customer_wishlist, name='customer_wishlist'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('addresses/', views.customer_addresses, name='customer_addresses'),
    path('security/', views.customer_security, name='customer_security'),
    
    # ============================================
    # ADMIN DASHBOARD
    # ============================================
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Admin - Users
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/add/', views.admin_users_add, name='admin_users_add'),
    path('admin/users/<int:user_id>/edit/', views.admin_users_edit, name='admin_users_edit'),
    path('admin/users/<int:user_id>/delete/', views.admin_users_delete, name='admin_users_delete'),
    path('admin/users/<int:user_id>/block/', views.admin_users_block, name='admin_users_block'),
    path('admin/users/<int:user_id>/unblock/', views.admin_users_unblock, name='admin_users_unblock'),
    
    # Admin - Products
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/add/', views.admin_products_add, name='admin_products_add'),
    path('admin/products/<int:product_id>/edit/', views.admin_products_edit, name='admin_products_edit'),
    path('admin/products/<int:product_id>/delete/', views.admin_products_delete, name='admin_products_delete'),
    
    # Admin - Orders
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/orders/<int:order_id>/', views.admin_orders_detail, name='admin_orders_detail'),
    path('admin/orders/<int:order_id>/update-status/', views.admin_orders_update_status, name='admin_orders_update_status'),
    
    # Admin - Payments
    path('admin/payments/', views.admin_payments, name='admin_payments'),
    path('admin/payments/<int:payment_id>/detail/', views.admin_payments_detail, name='admin_payments_detail'),
    path('admin/payments/<int:payment_id>/status/<str:status>/', views.admin_payments_update_status, name='admin_payments_update_status'),
    
    # Admin - Reviews
    path('admin/reviews/', views.admin_reviews, name='admin_reviews'),
    path('admin/reviews/detail/<int:review_id>/', views.admin_reviews_detail, name='admin_reviews_detail'),  # ✅ ADDED
    path('admin/reviews/<int:review_id>/approve/', views.admin_reviews_approve, name='admin_reviews_approve'),
    path('admin/reviews/<int:review_id>/reject/', views.admin_reviews_reject, name='admin_reviews_reject'),
    path('admin/reviews/<int:review_id>/delete/', views.admin_reviews_delete, name='admin_reviews_delete'),
    
    # Admin - Wishlists
    path('admin/wishlists/', views.admin_wishlists, name='admin_wishlists'),  # ✅ ADDED
    path('admin/wishlists/detail/<int:wishlist_id>/', views.admin_wishlists_detail, name='admin_wishlists_detail'),  # ✅ ADDED
    path('admin/wishlists/item/remove/<int:item_id>/', views.admin_wishlists_item_remove, name='admin_wishlists_item_remove'),  # ✅ ADDED
    path('admin/wishlists/delete/<int:wishlist_id>/', views.admin_wishlists_delete, name='admin_wishlists_delete'),  # ✅ ADDED
    
    # Admin - Notifications
    path('admin/notifications/', views.admin_notifications, name='admin_notifications'),  # ✅ ADDED
    path('admin/notifications/detail/<int:notification_id>/', views.admin_notifications_detail, name='admin_notifications_detail'),  # ✅ ADDED
    path('admin/notifications/<int:notification_id>/mark-read/', views.admin_notifications_mark_read, name='admin_notifications_mark_read'),  # ✅ ADDED
    path('admin/notifications/<int:notification_id>/delete/', views.admin_notifications_delete, name='admin_notifications_delete'),  # ✅ ADDED
    path('admin/notifications/send/', views.admin_notifications_send, name='admin_notifications_send'),  # ✅ ADDED
    
    # Admin - Reports
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    
    # ============================================
    # VENDOR DASHBOARD
    # ============================================
    path('vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('vendor/orders/', views.vendor_orders, name='vendor_orders'),
    path('vendor/analytics/', views.vendor_analytics, name='vendor_analytics'),
    path('vendor/settings/', views.vendor_settings, name='vendor_settings'),
]