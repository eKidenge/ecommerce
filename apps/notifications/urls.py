from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.view_notifications, name='view'),
    path('detail/<int:notification_id>/', views.notification_detail, name='detail'),
    path('mark-read/', views.mark_notification_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete'),
]