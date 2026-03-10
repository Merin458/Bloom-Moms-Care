from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import CustomUser
from .models import (
    DoctorProfile, PatientProfile, Appointment, Prescription, MedicalRecord, TrimesterTracking
)
from .forms import (
    DoctorProfileForm, PatientProfileForm, AppointmentBookingForm, AppointmentStatusForm,
    PrescriptionForm, MedicalRecordForm, TrimesterTrackingForm
)


# ─────────────────────────── Helpers ────────────────────────────────────────

def _require_role(request, role):
    if getattr(request.user, 'role', None) != role:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    return None


# ─────────────────────────── Admin Views ────────────────────────────────────

@login_required
def admin_dashboard(request):
    denied = _require_role(request, 'admin')
    if denied:
        return denied
    context = {
        'total_patients': PatientProfile.objects.count(),
        'total_doctors': DoctorProfile.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
        'recent_appointments': Appointment.objects.select_related(
            'patient__user', 'doctor__user'
        ).order_by('-created_at')[:5],
    }
    return render(request, 'core/admin/dashboard.html', context)


@login_required
def admin_manage_doctors(request):
    denied = _require_role(request, 'admin')
    if denied:
        return denied
    doctors = DoctorProfile.objects.select_related('user').all()
    return render(request, 'core/admin/manage_doctors.html', {'doctors': doctors})


@login_required
def admin_add_doctor(request):
    denied = _require_role(request, 'admin')
    if denied:
        return denied
    from accounts.forms import PatientRegistrationForm

    class DoctorRegistrationForm(PatientRegistrationForm):
        def save(self, commit=True):
            user = super(PatientRegistrationForm, self).save(commit=False)
            user.set_password(self.cleaned_data['password1'])
            user.role = CustomUser.ROLE_DOCTOR
            if commit:
                user.save()
            return user

    if request.method == 'POST':
        user_form = DoctorRegistrationForm(request.POST)
        profile_form = DoctorProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, f'Doctor {user.get_full_name()} added successfully.')
            return redirect('admin_manage_doctors')
    else:
        user_form = DoctorRegistrationForm()
        profile_form = DoctorProfileForm()
    return render(request, 'core/admin/add_doctor.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def admin_manage_patients(request):
    denied = _require_role(request, 'admin')
    if denied:
        return denied
    patients = PatientProfile.objects.select_related('user', 'assigned_doctor__user').all()
    return render(request, 'core/admin/manage_patients.html', {'patients': patients})


@login_required
def admin_view_appointments(request):
    denied = _require_role(request, 'admin')
    if denied:
        return denied
    appointments = Appointment.objects.select_related(
        'patient__user', 'doctor__user'
    ).all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    return render(request, 'core/admin/appointments.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    })


@login_required
def admin_toggle_doctor(request, doctor_id):
    denied = _require_role(request, 'admin')
    if denied:
        return denied
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
    doctor.is_available = not doctor.is_available
    doctor.save()
    status = 'activated' if doctor.is_available else 'deactivated'
    messages.success(request, f'Dr. {doctor.user.get_full_name()} has been {status}.')
    return redirect('admin_manage_doctors')


# ─────────────────────────── Doctor Views ───────────────────────────────────

@login_required
def doctor_dashboard(request):
    denied = _require_role(request, 'doctor')
    if denied:
        return denied
    try:
        profile = request.user.doctor_profile
    except DoctorProfile.DoesNotExist:
        messages.warning(request, 'Please complete your doctor profile.')
        return redirect('doctor_edit_profile')

    context = {
        'profile': profile,
        'today_appointments': Appointment.objects.filter(
            doctor=profile, appointment_date=timezone.now().date()
        ).select_related('patient__user'),
        'pending_appointments': Appointment.objects.filter(
            doctor=profile, status='pending'
        ).select_related('patient__user').order_by('appointment_date')[:5],
        'my_patients': PatientProfile.objects.filter(assigned_doctor=profile).select_related('user'),
    }
    return render(request, 'core/doctor/dashboard.html', context)


@login_required
def doctor_edit_profile(request):
    denied = _require_role(request, 'doctor')
    if denied:
        return denied
    profile, _ = DoctorProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('doctor_dashboard')
    else:
        form = DoctorProfileForm(instance=profile)
    return render(request, 'core/doctor/edit_profile.html', {'form': form})


@login_required
def doctor_appointments(request):
    denied = _require_role(request, 'doctor')
    if denied:
        return denied
    profile = get_object_or_404(DoctorProfile, user=request.user)
    appointments = Appointment.objects.filter(doctor=profile).select_related('patient__user').order_by('appointment_date')
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    return render(request, 'core/doctor/appointments.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    })


@login_required
def doctor_update_appointment(request, appointment_id):
    denied = _require_role(request, 'doctor')
    if denied:
        return denied
    profile = get_object_or_404(DoctorProfile, user=request.user)
    appointment = get_object_or_404(Appointment, pk=appointment_id, doctor=profile)
    if request.method == 'POST':
        form = AppointmentStatusForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully.')
            return redirect('doctor_appointments')
    else:
        form = AppointmentStatusForm(instance=appointment)
    return render(request, 'core/doctor/update_appointment.html', {'form': form, 'appointment': appointment})


@login_required
def doctor_patients(request):
    denied = _require_role(request, 'doctor')
    if denied:
        return denied
    profile = get_object_or_404(DoctorProfile, user=request.user)
    patients = PatientProfile.objects.filter(assigned_doctor=profile).select_related('user')
    return render(request, 'core/doctor/patients.html', {'patients': patients})


@login_required
def doctor_patient_detail(request, patient_id):
    denied = _require_role(request, 'doctor')
    if denied:
        return denied
    profile = get_object_or_404(DoctorProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    context = {
        'patient': patient,
        'appointments': Appointment.objects.filter(patient=patient, doctor=profile).order_by('-appointment_date'),
        'prescriptions': Prescription.objects.filter(patient=patient, doctor=profile).order_by('-issued_date'),
        'medical_records': MedicalRecord.objects.filter(patient=patient, doctor=profile).order_by('-record_date'),
        'trimester_trackings': TrimesterTracking.objects.filter(patient=patient).order_by('-date_recorded'),
    }
    return render(request, 'core/doctor/patient_detail.html', context)


@login_required
def doctor_add_prescription(request, patient_id):
    denied = _require_role(request, 'doctor')
    if denied:
        return denied
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.patient = patient
            prescription.doctor = doctor_profile
            prescription.save()
            messages.success(request, 'Prescription added successfully.')
            return redirect('doctor_patient_detail', patient_id=patient_id)
    else:
        form = PrescriptionForm()
    return render(request, 'core/doctor/add_prescription.html', {'form': form, 'patient': patient})


@login_required
def doctor_add_medical_record(request, patient_id):
    denied = _require_role(request, 'doctor')
    if denied:
        return denied
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.doctor = doctor_profile
            record.save()
            messages.success(request, 'Medical record added.')
            return redirect('doctor_patient_detail', patient_id=patient_id)
    else:
        form = MedicalRecordForm()
    return render(request, 'core/doctor/add_medical_record.html', {'form': form, 'patient': patient})


@login_required
def doctor_add_trimester_tracking(request, patient_id):
    denied = _require_role(request, 'doctor')
    if denied:
        return denied
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if request.method == 'POST':
        form = TrimesterTrackingForm(request.POST)
        if form.is_valid():
            tracking = form.save(commit=False)
            tracking.patient = patient
            tracking.recorded_by_doctor = doctor_profile
            tracking.save()
            messages.success(request, 'Trimester tracking entry added.')
            return redirect('doctor_patient_detail', patient_id=patient_id)
    else:
        form = TrimesterTrackingForm()
    return render(request, 'core/doctor/add_trimester.html', {'form': form, 'patient': patient})


# ─────────────────────────── Patient Views ──────────────────────────────────

@login_required
def patient_dashboard(request):
    denied = _require_role(request, 'patient')
    if denied:
        return denied
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    if created:
        messages.info(request, 'Please complete your profile to get started.')
    context = {
        'profile': profile,
        'upcoming_appointments': Appointment.objects.filter(
            patient=profile, status__in=['pending', 'confirmed']
        ).select_related('doctor__user').order_by('appointment_date')[:5],
        'recent_prescriptions': Prescription.objects.filter(
            patient=profile
        ).select_related('doctor__user').order_by('-issued_date')[:3],
        'trimester': profile.get_trimester(),
        'weeks_pregnant': profile.get_weeks_pregnant(),
    }
    return render(request, 'core/patient/dashboard.html', context)


@login_required
def patient_edit_profile(request):
    denied = _require_role(request, 'patient')
    if denied:
        return denied
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('patient_dashboard')
    else:
        form = PatientProfileForm(instance=profile)
    return render(request, 'core/patient/edit_profile.html', {'form': form})


@login_required
def patient_book_appointment(request):
    denied = _require_role(request, 'patient')
    if denied:
        return denied
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = profile
            appointment.status = 'pending'
            appointment.save()
            messages.success(request, 'Appointment booked successfully! Awaiting confirmation.')
            return redirect('patient_appointments')
    else:
        form = AppointmentBookingForm()
    return render(request, 'core/patient/book_appointment.html', {'form': form})


@login_required
def patient_appointments(request):
    denied = _require_role(request, 'patient')
    if denied:
        return denied
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    appointments = Appointment.objects.filter(patient=profile).select_related('doctor__user').order_by('-appointment_date')
    return render(request, 'core/patient/appointments.html', {'appointments': appointments})


@login_required
def patient_cancel_appointment(request, appointment_id):
    denied = _require_role(request, 'patient')
    if denied:
        return denied
    profile = get_object_or_404(PatientProfile, user=request.user)
    appointment = get_object_or_404(Appointment, pk=appointment_id, patient=profile)
    if appointment.status in ('pending', 'confirmed'):
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled.')
    else:
        messages.error(request, 'This appointment cannot be cancelled.')
    return redirect('patient_appointments')


@login_required
def patient_prescriptions(request):
    denied = _require_role(request, 'patient')
    if denied:
        return denied
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    prescriptions = Prescription.objects.filter(patient=profile).select_related('doctor__user').order_by('-issued_date')
    return render(request, 'core/patient/prescriptions.html', {'prescriptions': prescriptions})


@login_required
def patient_medical_records(request):
    denied = _require_role(request, 'patient')
    if denied:
        return denied
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    records = MedicalRecord.objects.filter(patient=profile).select_related('doctor__user').order_by('-record_date')
    return render(request, 'core/patient/medical_records.html', {'records': records})


@login_required
def patient_trimester_tracking(request):
    denied = _require_role(request, 'patient')
    if denied:
        return denied
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    trackings = TrimesterTracking.objects.filter(patient=profile).order_by('-date_recorded')
    if request.method == 'POST':
        form = TrimesterTrackingForm(request.POST)
        if form.is_valid():
            tracking = form.save(commit=False)
            tracking.patient = profile
            tracking.save()
            messages.success(request, 'Tracking entry saved.')
            return redirect('patient_trimester_tracking')
    else:
        form = TrimesterTrackingForm()
    return render(request, 'core/patient/trimester_tracking.html', {
        'trackings': trackings,
        'form': form,
        'trimester': profile.get_trimester(),
        'weeks_pregnant': profile.get_weeks_pregnant(),
    })

