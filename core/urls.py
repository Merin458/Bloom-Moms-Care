from django.urls import path
from . import views

urlpatterns = [
    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/doctors/', views.admin_manage_doctors, name='admin_manage_doctors'),
    path('admin-panel/doctors/add/', views.admin_add_doctor, name='admin_add_doctor'),
    path('admin-panel/doctors/<int:doctor_id>/toggle/', views.admin_toggle_doctor, name='admin_toggle_doctor'),
    path('admin-panel/patients/', views.admin_manage_patients, name='admin_manage_patients'),
    path('admin-panel/appointments/', views.admin_view_appointments, name='admin_view_appointments'),

    # Doctor
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/edit/', views.doctor_edit_profile, name='doctor_edit_profile'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/appointments/<int:appointment_id>/update/', views.doctor_update_appointment, name='doctor_update_appointment'),
    path('doctor/patients/', views.doctor_patients, name='doctor_patients'),
    path('doctor/patients/<int:patient_id>/', views.doctor_patient_detail, name='doctor_patient_detail'),
    path('doctor/patients/<int:patient_id>/prescription/add/', views.doctor_add_prescription, name='doctor_add_prescription'),
    path('doctor/patients/<int:patient_id>/record/add/', views.doctor_add_medical_record, name='doctor_add_medical_record'),
    path('doctor/patients/<int:patient_id>/trimester/add/', views.doctor_add_trimester_tracking, name='doctor_add_trimester_tracking'),

    # Patient
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/profile/edit/', views.patient_edit_profile, name='patient_edit_profile'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('patient/appointments/book/', views.patient_book_appointment, name='patient_book_appointment'),
    path('patient/appointments/<int:appointment_id>/cancel/', views.patient_cancel_appointment, name='patient_cancel_appointment'),
    path('patient/prescriptions/', views.patient_prescriptions, name='patient_prescriptions'),
    path('patient/records/', views.patient_medical_records, name='patient_medical_records'),
    path('patient/trimester/', views.patient_trimester_tracking, name='patient_trimester_tracking'),
]
