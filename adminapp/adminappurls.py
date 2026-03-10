from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
path('', views.admin_login, name='admin_login'),
path('adminindex/', views.adminindex, name='adminindex'),
path('logout/', views.admin_logout, name='admin_logout'),
path('districtreg/', views.districtreg, name='districtreg'),
path('countryreg/', views.countryreg, name='countryreg'),
path('viewdistrict/', views.viewdistrict, name='viewdistrict'),
path('editdistrict/<id>/', views.editdistrict, name='editdistrict'),
path('deletedistrict/<id>/', views.deletedistrict, name='deletedistrict'),
path('doctorreg/', views.doctorreg, name='doctorreg'),
path('viewdoctors/', views.viewdoctors, name='viewdoctors'),
path('editdoctor/<id>/', views.editdoctor, name='editdoctor'),
path('deactivatedoctor/<id>/', views.deactivatedoctor, name='deactivatedoctor'),
path('activatedoctor/<id>/', views.activatedoctor, name='activatedoctor'),
path('deletedoctor/<id>/', views.deletedoctor, name='deletedoctor'), 
path('patientreg/', views.patientreg, name='patientreg'),
path('viewpatients/', views.viewpatients, name='viewpatients'),
path('editpatient/<id>/', views.editpatient, name='editpatient'),
path('deletepatient/<id>/', views.deletepatient, name='deletepatient'),
path('viewappointments/', views.view_appointments, name='view_appointments'),
path('accept_appointment/<id>/', views.accept_appointment, name='accept_appointment'),
path('reschedule_appointment/<id>/', views.reschedule_appointment, name='reschedule_appointment'),
path('doctorleave/', views.doctorleave, name='doctorleave'),
path('viewdoctorleave/', views.viewdoctorleave, name='viewdoctorleave'),
path('upload_medical_record/<int:patient_id>/', views.upload_medical_record, name='upload_medical_record'),
path('view_patients/',views.select_doctor,name='select_doctor'),
path('view_patients/<int:doctor_id>/',views.doctor_patients,name='doctor_patients'),
path('patient/<int:patient_id>/profile/',views.admin_patient_profile,name='admin_patient_profile'),
path('export_patient_report/', views.export_patient_report, name='export_patient_report'),


]


   