from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.products.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('payment/', include('apps.payments.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('wishlist/', include('apps.wishlist.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Robots.txt and sitemap
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml')),
]

# ============================================
# SERVE MEDIA FILES - CRITICAL FOR UPLOADED IMAGES
# ============================================
# Always serve media files (works for both development and production)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files only in development (production uses Whitenoise)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)