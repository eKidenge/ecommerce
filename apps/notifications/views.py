from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Notification

@login_required
def view_notifications(request):
    notifications = request.user.notifications.all()
    
    # Mark all as read if requested
    if request.GET.get('mark_all_read'):
        notifications.update(is_read=True)
        return redirect('notifications:view')
    
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page', 1)
    try:
        notifications = paginator.page(page)
    except:
        notifications = paginator.page(1)
    
    return render(request, 'notifications/notifications.html', {'notifications': notifications})

@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    return render(request, 'notifications/notification_detail.html', {'notification': notification})

@login_required
@require_POST
def mark_notification_read(request):
    notification_id = request.POST.get('notification_id')
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return JsonResponse({'success': True})

@login_required
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

@login_required
def get_unread_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})

# Context processor
def unread_notifications(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
        return {'unread_notifications': count}
    return {'unread_notifications': 0}

# Add this to existing views.py

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Notification deleted.')
    return redirect('notifications:view')