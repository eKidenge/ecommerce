from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='confirmation'),
    path('detail/<int:order_id>/', views.order_detail, name='detail'),
    path('history/', views.order_history, name='history'),
    path('track/<int:order_id>/', views.track_order, name='track'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel'),
    path('invoice/<int:order_id>/', views.download_invoice, name='invoice'),
    path('reorder/<int:order_id>/', views.reorder, name='reorder'),
]