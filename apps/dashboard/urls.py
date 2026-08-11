from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Customer Dashboard
    path('', views.customer_dashboard, name='customer_dashboard'),
    path('orders/', views.customer_orders, name='customer_orders'),
    path('wishlist/', views.customer_wishlist, name='customer_wishlist'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('addresses/', views.customer_addresses, name='customer_addresses'),
    path('security/', views.customer_security, name='customer_security'),
    
    # Admin Dashboard
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/payments/', views.admin_payments, name='admin_payments'),
    path('admin/reviews/', views.admin_reviews, name='admin_reviews'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    
    # Vendor Dashboard
    path('vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('vendor/orders/', views.vendor_orders, name='vendor_orders'),
    path('vendor/analytics/', views.vendor_analytics, name='vendor_analytics'),
    path('vendor/settings/', views.vendor_settings, name='vendor_settings'),
]