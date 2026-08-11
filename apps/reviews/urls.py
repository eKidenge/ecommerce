from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:product_id>/', views.add_review, name='add'),
    path('edit/<int:review_id>/', views.edit_review, name='edit'),
    path('delete/<int:review_id>/', views.delete_review, name='delete'),
    path('helpful/<int:review_id>/', views.helpful_review, name='helpful'),
    path('product/<int:product_id>/', views.product_reviews, name='product_reviews'),
]