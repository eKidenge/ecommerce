from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.view_wishlist, name='view'),
    path('add/', views.add_to_wishlist, name='add'),
    path('remove/', views.remove_from_wishlist, name='remove'),
    path('toggle/', views.toggle_wishlist, name='toggle'),
    path('move-to-cart/<int:item_id>/', views.move_to_cart, name='move_to_cart'),
    path('move-all-to-cart/', views.move_all_to_cart, name='move_all_to_cart'),
]