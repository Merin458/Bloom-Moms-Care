from django.urls import path
from . import views

urlpatterns = [
    path('patient/', views.patient_notifications, name='patient_notifications'),
    path('doctor/', views.doctor_notifications, name='doctor_notifications'),
    path('admin/', views.admin_notifications, name='admin_notifications'),
    path('mark-as-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/<str:user_type>/', views.mark_all_read, name='mark_all_read'),
]
