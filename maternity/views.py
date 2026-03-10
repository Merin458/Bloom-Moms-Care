from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from functools import wraps
from datetime import timedelta

from .models import (
    CustomUser, DoctorProfile, PatientProfile,
    Appointment, TrimsesterUpdate, Prescription,
    MedicalReport, ClinicalNote,
)
from .forms import (
    LoginForm, DoctorUserForm, DoctorProfileForm,
    PatientUserForm, PatientProfileForm,
    AppointmentForm, AppointmentStatusForm,
    TrimsesterUpdateForm, PrescriptionForm,
    MedicalReportForm, AdminMedicalReportForm,
    ClinicalNoteForm, DoctorEditUserForm, PatientEditUserForm,
)


# ─── Decorators ───────────────────────────────────────────────────────────────

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                messages.error(request, "You do not have permission to access that page.")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


# ─── Auth Views ───────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'maternity/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'doctor':
        return redirect('doctor_dashboard')
    elif user.role == 'patient':
        return redirect('patient_dashboard')
    return redirect('login')


# ─── Admin Views ──────────────────────────────────────────────────────────────

@login_required
@role_required('admin')
def admin_dashboard(request):
    context = {
        'total_doctors': DoctorProfile.objects.count(),
        'total_patients': PatientProfile.objects.count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
        'recent_appointments': Appointment.objects.filter(status='pending').select_related(
            'patient__user', 'doctor__user'
        )[:5],
        'recent_patients': PatientProfile.objects.select_related('user').order_by('-created_at')[:5],
    }
    return render(request, 'maternity/admin/dashboard.html', context)


@login_required
@role_required('admin')
def admin_doctor_list(request):
    doctors = DoctorProfile.objects.select_related('user').all()
    return render(request, 'maternity/admin/doctor_list.html', {'doctors': doctors})


@login_required
@role_required('admin')
def admin_add_doctor(request):
    user_form = DoctorUserForm(request.POST or None)
    profile_form = DoctorProfileForm(request.POST or None)
    if request.method == 'POST' and user_form.is_valid() and profile_form.is_valid():
        user = user_form.save(commit=False)
        user.role = 'doctor'
        user.set_password(user_form.cleaned_data['password'])
        user.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()
        messages.success(request, f"Doctor {user.get_full_name()} added successfully.")
        return redirect('admin_doctor_list')
    return render(request, 'maternity/admin/add_doctor.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
@role_required('admin')
def admin_edit_doctor(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    user_form = DoctorEditUserForm(request.POST or None, instance=doctor.user)
    profile_form = DoctorProfileForm(request.POST or None, instance=doctor)
    if request.method == 'POST' and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, "Doctor updated successfully.")
        return redirect('admin_doctor_list')
    return render(request, 'maternity/admin/edit_doctor.html', {
        'doctor': doctor,
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
@role_required('admin')
def admin_delete_doctor(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    if request.method == 'POST':
        name = doctor.user.get_full_name()
        doctor.user.delete()
        messages.success(request, f"Doctor {name} deleted.")
        return redirect('admin_doctor_list')
    return render(request, 'maternity/admin/confirm_delete.html', {
        'object': doctor, 'object_type': 'Doctor',
    })


@login_required
@role_required('admin')
def admin_patient_list(request):
    patients = PatientProfile.objects.select_related('user', 'assigned_doctor__user').all()
    for p in patients:
        p.check_and_update_lock()
    return render(request, 'maternity/admin/patient_list.html', {'patients': patients})


@login_required
@role_required('admin')
def admin_add_patient(request):
    user_form = PatientUserForm(request.POST or None)
    profile_form = PatientProfileForm(request.POST or None)
    if request.method == 'POST' and user_form.is_valid() and profile_form.is_valid():
        user = user_form.save(commit=False)
        user.role = 'patient'
        user.set_password(user_form.cleaned_data['password'])
        user.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()
        messages.success(request, f"Patient {user.get_full_name()} added successfully.")
        return redirect('admin_patient_list')
    return render(request, 'maternity/admin/add_patient.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
@role_required('admin')
def admin_edit_patient(request, pk):
    patient = get_object_or_404(PatientProfile, pk=pk)
    user_form = PatientEditUserForm(request.POST or None, instance=patient.user)
    profile_form = PatientProfileForm(request.POST or None, instance=patient)
    if request.method == 'POST' and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile = profile_form.save(commit=False)
        if profile.actual_delivery_date:
            lock_date = profile.actual_delivery_date + timedelta(days=180)
            profile.is_locked = timezone.now().date() >= lock_date
        profile.save()
        messages.success(request, "Patient updated successfully.")
        return redirect('admin_patient_list')
    return render(request, 'maternity/admin/edit_patient.html', {
        'patient': patient,
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
@role_required('admin')
def admin_delete_patient(request, pk):
    patient = get_object_or_404(PatientProfile, pk=pk)
    if request.method == 'POST':
        name = str(patient)
        patient.user.delete()
        messages.success(request, f"Patient {name} deleted.")
        return redirect('admin_patient_list')
    return render(request, 'maternity/admin/confirm_delete.html', {
        'object': patient, 'object_type': 'Patient',
    })


@login_required
@role_required('admin')
def admin_patient_detail(request, pk):
    patient = get_object_or_404(PatientProfile, pk=pk)
    patient.check_and_update_lock()
    context = {
        'patient': patient,
        'appointments': patient.appointments.select_related('doctor__user').all()[:10],
        'prescriptions': patient.prescriptions.select_related('doctor__user').all()[:10],
        'reports': patient.medical_reports.all()[:10],
        'trimester_updates': patient.trimester_updates.select_related('doctor__user').all()[:10],
        'clinical_notes': patient.clinical_notes.select_related('doctor__user').all()[:10],
    }
    return render(request, 'maternity/admin/patient_detail.html', context)


@login_required
@role_required('admin')
def admin_appointment_list(request):
    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.select_related(
        'patient__user', 'doctor__user'
    ).all()
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    return render(request, 'maternity/admin/appointment_list.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    })


@login_required
@role_required('admin')
def admin_appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentStatusForm(request.POST or None, instance=appointment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Appointment status updated.")
        return redirect('admin_appointment_list')
    return render(request, 'maternity/admin/appointment_detail.html', {
        'appointment': appointment,
        'form': form,
    })


@login_required
@role_required('admin')
def admin_upload_report(request):
    form = AdminMedicalReportForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        report = form.save(commit=False)
        report.uploaded_by = 'admin'
        report.uploaded_by_user = request.user
        report.save()
        messages.success(request, "Medical report uploaded successfully.")
        return redirect('admin_patient_detail', pk=report.patient.pk)
    return render(request, 'maternity/admin/upload_report.html', {'form': form})


# ─── Doctor Views ──────────────────────────────────────────────────────────────

@login_required
@role_required('doctor')
def doctor_dashboard(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    context = {
        'doctor': doctor,
        'total_patients': doctor.patients.count(),
        'pending_appointments': doctor.appointments.filter(status='pending').count(),
        'accepted_appointments': doctor.appointments.filter(status='accepted').count(),
        'recent_appointments': doctor.appointments.filter(
            status__in=['pending', 'accepted']
        ).select_related('patient__user')[:5],
        'recent_patients': doctor.patients.select_related('user').all()[:5],
    }
    return render(request, 'maternity/doctor/dashboard.html', context)


@login_required
@role_required('doctor')
def doctor_patient_list(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    patients = doctor.patients.select_related('user').all()
    for p in patients:
        p.check_and_update_lock()
    return render(request, 'maternity/doctor/patient_list.html', {
        'patients': patients, 'doctor': doctor,
    })


@login_required
@role_required('doctor')
def doctor_patient_detail(request, pk):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, pk=pk, assigned_doctor=doctor)
    patient.check_and_update_lock()
    context = {
        'patient': patient,
        'doctor': doctor,
        'appointments': patient.appointments.filter(doctor=doctor).all()[:10],
        'prescriptions': patient.prescriptions.filter(doctor=doctor).all()[:10],
        'trimester_updates': patient.trimester_updates.filter(doctor=doctor).all()[:10],
        'clinical_notes': patient.clinical_notes.filter(doctor=doctor).all()[:10],
        'reports': patient.medical_reports.all()[:10],
    }
    return render(request, 'maternity/doctor/patient_detail.html', context)


@login_required
@role_required('doctor')
def doctor_add_prescription(request, patient_pk):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, pk=patient_pk, assigned_doctor=doctor)
    form = PrescriptionForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        prescription = form.save(commit=False)
        prescription.doctor = doctor
        prescription.patient = patient
        prescription.save()
        messages.success(request, "Prescription added successfully.")
        return redirect('doctor_patient_detail', pk=patient_pk)
    return render(request, 'maternity/doctor/add_prescription.html', {
        'form': form, 'patient': patient,
    })


@login_required
@role_required('doctor')
def doctor_add_trimester(request, patient_pk):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, pk=patient_pk, assigned_doctor=doctor)
    form = TrimsesterUpdateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        update = form.save(commit=False)
        update.doctor = doctor
        update.patient = patient
        update.save()
        messages.success(request, "Trimester update added successfully.")
        return redirect('doctor_patient_detail', pk=patient_pk)
    return render(request, 'maternity/doctor/add_trimester.html', {
        'form': form, 'patient': patient,
    })


@login_required
@role_required('doctor')
def doctor_add_clinical_note(request, patient_pk):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, pk=patient_pk, assigned_doctor=doctor)
    form = ClinicalNoteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        note = form.save(commit=False)
        note.doctor = doctor
        note.patient = patient
        note.save()
        messages.success(request, "Clinical note added.")
        return redirect('doctor_patient_detail', pk=patient_pk)
    return render(request, 'maternity/doctor/add_clinical_note.html', {
        'form': form, 'patient': patient,
    })


@login_required
@role_required('doctor')
def doctor_appointment_list(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    status_filter = request.GET.get('status', '')
    appointments = doctor.appointments.select_related('patient__user').all()
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    return render(request, 'maternity/doctor/appointment_list.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'status_choices': Appointment.STATUS_CHOICES,
        'doctor': doctor,
    })


@login_required
@role_required('doctor')
def doctor_mark_appointment_complete(request, pk):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    if request.method == 'POST':
        appointment.status = 'completed'
        appointment.save()
        messages.success(request, "Appointment marked as completed.")
    return redirect('doctor_appointment_list')


# ─── Patient Views ─────────────────────────────────────────────────────────────

@login_required
@role_required('patient')
def patient_dashboard(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    patient.check_and_update_lock()
    context = {
        'patient': patient,
        'pending_appointments': patient.appointments.filter(status='pending').count(),
        'accepted_appointments': patient.appointments.filter(status='accepted').count(),
        'recent_appointments': patient.appointments.select_related('doctor__user').all()[:5],
        'recent_prescriptions': patient.prescriptions.select_related('doctor__user').all()[:3],
        'trimester_updates': patient.trimester_updates.select_related('doctor__user').all()[:3],
    }
    return render(request, 'maternity/patient/dashboard.html', context)


@login_required
@role_required('patient')
def patient_available_doctors(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    patient.check_and_update_lock()
    if patient.is_locked:
        doctors = DoctorProfile.objects.filter(
            specialization='gynecology', is_available=True
        ).select_related('user')
    else:
        doctors = DoctorProfile.objects.filter(is_available=True).select_related('user')
    return render(request, 'maternity/patient/available_doctors.html', {
        'doctors': doctors, 'patient': patient,
    })


@login_required
@role_required('patient')
def patient_book_appointment(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    patient.check_and_update_lock()
    form = AppointmentForm(request.POST or None, patient_profile=patient)
    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        appointment.patient = patient
        appointment.save()
        messages.success(request, "Appointment request submitted. Awaiting admin review.")
        return redirect('patient_appointments')
    return render(request, 'maternity/patient/book_appointment.html', {
        'form': form, 'patient': patient,
    })


@login_required
@role_required('patient')
def patient_appointments(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    appointments = patient.appointments.select_related('doctor__user').all()
    return render(request, 'maternity/patient/appointments.html', {
        'appointments': appointments, 'patient': patient,
    })


@login_required
@role_required('patient')
def patient_prescriptions(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    prescriptions = patient.prescriptions.select_related('doctor__user').all()
    return render(request, 'maternity/patient/prescriptions.html', {
        'prescriptions': prescriptions, 'patient': patient,
    })


@login_required
@role_required('patient')
def patient_reports(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    reports = patient.medical_reports.all()
    return render(request, 'maternity/patient/reports.html', {
        'reports': reports, 'patient': patient,
    })


@login_required
@role_required('patient')
def patient_upload_report(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    form = MedicalReportForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        report = form.save(commit=False)
        report.patient = patient
        report.uploaded_by = 'patient'
        report.uploaded_by_user = request.user
        report.save()
        messages.success(request, "Medical report uploaded successfully.")
        return redirect('patient_reports')
    return render(request, 'maternity/patient/upload_report.html', {
        'form': form, 'patient': patient,
    })


@login_required
@role_required('patient')
def patient_trimester_updates(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    updates = patient.trimester_updates.select_related('doctor__user').all()
    return render(request, 'maternity/patient/trimester_updates.html', {
        'updates': updates, 'patient': patient,
    })


@login_required
@role_required('patient')
def patient_clinical_notes(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    notes = patient.clinical_notes.select_related('doctor__user').all()
    return render(request, 'maternity/patient/clinical_notes.html', {
        'notes': notes, 'patient': patient,
    })
