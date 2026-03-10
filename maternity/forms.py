from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    CustomUser, DoctorProfile, PatientProfile,
    Appointment, TrimsesterUpdate, Prescription,
    MedicalReport, ClinicalNote,
)


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class DoctorUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = [
            'specialization', 'qualification',
            'experience_years', 'bio', 'is_available',
        ]
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PatientUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = [
            'assigned_doctor', 'age', 'blood_group', 'address',
            'emergency_contact', 'expected_delivery_date',
            'actual_delivery_date', 'medical_history',
        ]
        widgets = {
            'assigned_doctor': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'expected_delivery_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'actual_delivery_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'requested_date', 'requested_time', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'requested_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'requested_time': forms.TimeInput(
                attrs={'class': 'form-control', 'type': 'time'}
            ),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, patient_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if patient_profile and patient_profile.is_locked:
            # Locked patients can only book gynecology doctors
            self.fields['doctor'].queryset = DoctorProfile.objects.filter(
                specialization='gynecology', is_available=True
            )
        else:
            self.fields['doctor'].queryset = DoctorProfile.objects.filter(
                is_available=True
            )


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'scheduled_date', 'scheduled_time', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'scheduled_time': forms.TimeInput(
                attrs={'class': 'form-control', 'type': 'time'}
            ),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TrimsesterUpdateForm(forms.ModelForm):
    class Meta:
        model = TrimsesterUpdate
        fields = [
            'trimester_number', 'weight_kg', 'blood_pressure',
            'fetal_heartbeat', 'health_notes', 'recommendations', 'date_recorded',
        ]
        widgets = {
            'trimester_number': forms.Select(attrs={'class': 'form-control'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'blood_pressure': forms.TextInput(attrs={'class': 'form-control'}),
            'fetal_heartbeat': forms.TextInput(attrs={'class': 'form-control'}),
            'health_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_recorded': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = [
            'title', 'medications', 'dosage_instructions',
            'notes', 'prescription_file', 'date_prescribed',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'dosage_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'prescription_file': forms.FileInput(attrs={'class': 'form-control'}),
            'date_prescribed': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['report_type', 'title', 'description', 'report_file', 'report_date']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'report_file': forms.FileInput(attrs={'class': 'form-control'}),
            'report_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }


class AdminMedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['patient', 'report_type', 'title', 'description', 'report_file', 'report_date']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'report_file': forms.FileInput(attrs={'class': 'form-control'}),
            'report_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }


class ClinicalNoteForm(forms.ModelForm):
    class Meta:
        model = ClinicalNote
        fields = ['title', 'note', 'date_noted']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'date_noted': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }


class DoctorEditUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PatientEditUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
