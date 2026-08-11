from django.urls import path
from . import views
from . import webhooks

app_name = 'payments'

urlpatterns = [
    path('process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('pending/<int:payment_id>/', views.payment_pending, name='pending'),
    path('failed/<int:payment_id>/', views.payment_failed, name='failed'),
    path('webhook/stripe/', webhooks.stripe_webhook, name='stripe_webhook'),
    path('webhook/mpesa/', webhooks.mpesa_webhook, name='mpesa_webhook'),
    path('mpesa/callback/', webhooks.mpesa_callback, name='mpesa_callback'),
    path('mpesa/result/', webhooks.mpesa_result, name='mpesa_result'),
]