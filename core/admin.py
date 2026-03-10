from django.contrib import admin
from .models import DoctorProfile, PatientProfile, Appointment, Prescription, MedicalRecord, TrimesterTracking


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'experience_years', 'is_available')
    list_filter = ('specialization', 'is_available')
    search_fields = ('user__first_name', 'user__last_name', 'user__username')


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'due_date', 'assigned_doctor')
    list_filter = ('blood_group',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('patient__user__first_name', 'doctor__user__first_name')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'issued_date', 'follow_up_date')
    list_filter = ('issued_date',)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'record_date', 'blood_pressure', 'weight_kg')
    list_filter = ('record_date',)


@admin.register(TrimesterTracking)
class TrimesterTrackingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'trimester', 'week_number', 'date_recorded')
    list_filter = ('trimester',)
