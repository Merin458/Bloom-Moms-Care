from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Admin
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/doctors/', views.admin_doctor_list, name='admin_doctor_list'),
    path('admin-panel/doctors/add/', views.admin_add_doctor, name='admin_add_doctor'),
    path('admin-panel/doctors/<int:pk>/edit/', views.admin_edit_doctor, name='admin_edit_doctor'),
    path('admin-panel/doctors/<int:pk>/delete/', views.admin_delete_doctor, name='admin_delete_doctor'),
    path('admin-panel/patients/', views.admin_patient_list, name='admin_patient_list'),
    path('admin-panel/patients/add/', views.admin_add_patient, name='admin_add_patient'),
    path('admin-panel/patients/<int:pk>/', views.admin_patient_detail, name='admin_patient_detail'),
    path('admin-panel/patients/<int:pk>/edit/', views.admin_edit_patient, name='admin_edit_patient'),
    path('admin-panel/patients/<int:pk>/delete/', views.admin_delete_patient, name='admin_delete_patient'),
    path('admin-panel/appointments/', views.admin_appointment_list, name='admin_appointment_list'),
    path('admin-panel/appointments/<int:pk>/', views.admin_appointment_detail, name='admin_appointment_detail'),
    path('admin-panel/reports/upload/', views.admin_upload_report, name='admin_upload_report'),

    # Doctor
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/patients/', views.doctor_patient_list, name='doctor_patient_list'),
    path('doctor/patients/<int:pk>/', views.doctor_patient_detail, name='doctor_patient_detail'),
    path('doctor/patients/<int:patient_pk>/prescriptions/add/', views.doctor_add_prescription, name='doctor_add_prescription'),
    path('doctor/patients/<int:patient_pk>/trimester/add/', views.doctor_add_trimester, name='doctor_add_trimester'),
    path('doctor/patients/<int:patient_pk>/notes/add/', views.doctor_add_clinical_note, name='doctor_add_clinical_note'),
    path('doctor/appointments/', views.doctor_appointment_list, name='doctor_appointment_list'),
    path('doctor/appointments/<int:pk>/complete/', views.doctor_mark_appointment_complete, name='doctor_mark_appointment_complete'),

    # Patient
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/doctors/', views.patient_available_doctors, name='patient_available_doctors'),
    path('patient/appointments/book/', views.patient_book_appointment, name='patient_book_appointment'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('patient/prescriptions/', views.patient_prescriptions, name='patient_prescriptions'),
    path('patient/reports/', views.patient_reports, name='patient_reports'),
    path('patient/reports/upload/', views.patient_upload_report, name='patient_upload_report'),
    path('patient/trimester/', views.patient_trimester_updates, name='patient_trimester_updates'),
    path('patient/notes/', views.patient_clinical_notes, name='patient_clinical_notes'),
]
