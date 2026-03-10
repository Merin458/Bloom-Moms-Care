from django import forms
from .models import (
    DoctorProfile, PatientProfile, Appointment, Prescription, MedicalRecord, TrimesterTracking
)


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ('specialization', 'qualification', 'experience_years', 'bio',
                  'available_days', 'available_time_start', 'available_time_end', 'is_available')
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'available_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Monday, Wednesday, Friday'}),
            'available_time_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'available_time_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ('date_of_birth', 'blood_group', 'address', 'emergency_contact_name',
                  'emergency_contact_phone', 'last_menstrual_period', 'due_date',
                  'assigned_doctor', 'allergies', 'medical_history')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'last_menstrual_period': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_doctor': forms.Select(attrs={'class': 'form-select'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('doctor', 'appointment_date', 'appointment_time', 'reason')
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for appointment'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = DoctorProfile.objects.filter(is_available=True).select_related('user')


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('status', 'notes')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ('medications', 'instructions', 'dietary_advice', 'follow_up_date')
        widgets = {
            'medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                                 'placeholder': 'List each medication on a new line with dosage and frequency'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dietary_advice': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ('diagnosis', 'treatment', 'weight_kg', 'blood_pressure', 'fetal_heart_rate', 'notes')
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'treatment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'blood_pressure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 120/80'}),
            'fetal_heart_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TrimesterTrackingForm(forms.ModelForm):
    class Meta:
        model = TrimesterTracking
        fields = ('trimester', 'week_number', 'symptoms', 'notes')
        widgets = {
            'trimester': forms.Select(attrs={'class': 'form-select'}),
            'week_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 42}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                             'placeholder': 'Describe any symptoms'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
