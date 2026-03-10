from django.contrib import admin
from django.urls import include, path

from . import views
urlpatterns = [
path('patientindex/', views.patientindex, name='patientindex'),
path('logout/', views.patient_logout, name='patient_logout'),
path('about/', views.about_us, name='about_us'),
path('services/', views.services, name='services'),
path('antenatalcare/', views.antenatalcare, name='antenatalcare'),
path('ultrasound/', views.ultrasound, name='ultrasound'),
path('consultation/', views.consultation, name='consultation'),
path('trimestermonitor/', views.trimestermonitor, name='trimestermonitor'),
path('nutritioncare/', views.nutritioncare, name='nutritioncare'),
path('safedelivery/', views.safedelivery, name='safedelivery'),
path('contact/', views.contact, name='contact'),
path('trimesterview/', views.trimesterview, name='trimesterview'),
path('patientdoctorview/', views.patientdoctorview, name='patientdoctorview'),
path('appointmentbooking/', views.appointmentbooking, name='appointmentbooking'),
path('visit_history/', views.visit_history, name='visit_history'),
path('medical_records/',views.patient_medical_records,name='patient_medical_records'),
path('patient_prescriptions/',views.patient_prescriptions,name='patient_prescriptions'),
path('profile_unlock/',views.profile_unlock,name='profile_unlock'),
path('download_bill/<int:payment_id>/', views.download_bill, name='download_bill'),
]

