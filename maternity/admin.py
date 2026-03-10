from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, DoctorProfile, PatientProfile,
    Appointment, TrimsesterUpdate, Prescription,
    MedicalReport, ClinicalNote,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone')}),
    )


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'experience_years', 'is_available']
    list_filter = ['specialization', 'is_available']


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'assigned_doctor', 'blood_group', 'expected_delivery_date', 'is_locked']
    list_filter = ['blood_group', 'is_locked']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'requested_date', 'status', 'created_at']
    list_filter = ['status']


@admin.register(TrimsesterUpdate)
class TrimsesterUpdateAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'trimester_number', 'date_recorded']
    list_filter = ['trimester_number']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'title', 'date_prescribed']


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ['patient', 'report_type', 'title', 'uploaded_by', 'report_date']
    list_filter = ['report_type', 'uploaded_by']


@admin.register(ClinicalNote)
class ClinicalNoteAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'title', 'date_noted']
