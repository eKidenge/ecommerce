from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('search/', views.search_products, name='search'),
    path('featured/', views.featured_products, name='featured'),
    path('new-arrivals/', views.new_arrivals, name='new_arrivals'),
    path('add-review/<slug:slug>/', views.add_review, name='add_review'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]