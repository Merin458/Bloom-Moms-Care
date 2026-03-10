from django.shortcuts import render, redirect, get_object_or_404
from .models import Notification


def patient_notifications(request):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('patientapp:login')
    
    notifications = Notification.objects.filter(user_type='Patient', user_id=str(login_id)).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'Patient/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })


def doctor_notifications(request):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('doctorapp:login')
    
    notifications = Notification.objects.filter(user_type='Doctor', user_id=str(login_id)).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'Doctor/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })


def admin_notifications(request):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('adminapp:login')
    
    # Show ALL admin notifications (all admins need to see important notifications)
    notifications = Notification.objects.filter(user_type='Admin').order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'Admin/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })


def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    
    # Redirect back to the appropriate notifications page
    if notification.user_type == 'Patient':
        return redirect('notificationapp:patient_notifications')
    elif notification.user_type == 'Doctor':
        return redirect('notificationapp:doctor_notifications')
    else:
        return redirect('notificationapp:admin_notifications')


def mark_all_read(request, user_type):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('guestapp:login')
    
    # For Admin, mark all unread admin notifications as read
    # For Patient/Doctor, mark only the current user's unread notifications as read
    if user_type == 'Admin':
        Notification.objects.filter(user_type=user_type, is_read=False).update(is_read=True)
    else:
        Notification.objects.filter(user_type=user_type, user_id=str(login_id), is_read=False).update(is_read=True)
    
    if user_type == 'Patient':
        return redirect('notificationapp:patient_notifications')
    elif user_type == 'Doctor':
        return redirect('notificationapp:doctor_notifications')
    else:
        return redirect('notificationapp:admin_notifications')
