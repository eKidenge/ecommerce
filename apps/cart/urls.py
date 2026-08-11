from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='view'),
    path('add/', views.add_to_cart, name='add'),
    path('update/', views.update_cart, name='update'),
    path('remove/', views.remove_from_cart, name='remove'),
    path('summary/', views.cart_summary, name='summary'),
    path('clear/', views.clear_cart, name='clear'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
]