from django.contrib import admin
from django.urls import include, path

from . import views
urlpatterns = [
path('doctorindex/', views.doctorindex, name='doctorindex'),
path('logout/', views.doctor_logout, name='doctor_logout'),
path('doctor_patients/', views.doctor_patients, name='doctor_patients'),
path('patient_info/<int:patient_id>/', views.patient_info, name='patient_info'),
path('delivery_due_soon/', views.delivery_due_soon, name='delivery_due_soon'),
path('generate_report/', views.generate_report, name='generate_report'),
path('export_patients_excel/', views.export_patients_excel, name='export_patients_excel'),
path('patient_profile/<int:patient_id>/', views.patient_profile, name='patient_profile'),
path('doctor_appointments_by_date/', views.doctor_appointments_by_date, name='doctor_appointments_by_date'),
path('add_visit/<int:appointment_id>/', views.add_visit, name='add_visit'),
path('view_visit/<int:appointment_id>/', views.view_visit, name='view_visit'),
path('doctor_visits/', views.doctor_visits, name='doctor_visits'),
path('add-prescription/<int:patient_id>/<int:appointment_id>/',views.add_prescription,name='add_prescription'),
path('add_delivery_details/<int:patient_id>/', views.add_delivery_details, name='add_delivery_details'),
path('view_delivery_details/<int:patient_id>/', views.view_delivery_details, name='view_delivery_details'),
]




