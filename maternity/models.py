from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=20, blank=True)

    def is_admin(self):
        return self.role == 'admin'

    def is_doctor(self):
        return self.role == 'doctor'

    def is_patient(self):
        return self.role == 'patient'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class DoctorProfile(models.Model):
    SPECIALIZATION_CHOICES = (
        ('gynecology', 'Gynecology'),
        ('obstetrics', 'Obstetrics'),
        ('pediatrics', 'Pediatrics'),
        ('general', 'General Medicine'),
        ('other', 'Other'),
    )

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='doctor_profile'
    )
    specialization = models.CharField(
        max_length=50, choices=SPECIALIZATION_CHOICES, default='gynecology'
    )
    qualification = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Dr. {self.user.get_full_name() or self.user.username}"
            f" - {self.get_specialization_display()}"
        )


class PatientProfile(models.Model):
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('unknown', 'Unknown'),
    )

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='patient_profile'
    )
    assigned_doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='patients'
    )
    age = models.PositiveIntegerField(null=True, blank=True)
    blood_group = models.CharField(
        max_length=10, choices=BLOOD_GROUP_CHOICES, default='unknown'
    )
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def check_and_update_lock(self):
        """Lock profile 6 months after actual delivery date."""
        if self.actual_delivery_date and not self.is_locked:
            lock_date = self.actual_delivery_date + timedelta(days=180)
            if timezone.now().date() >= lock_date:
                self.is_locked = True
                self.save(update_fields=['is_locked'])
        return self.is_locked

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rescheduled', 'Rescheduled'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name='appointments'
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name='appointments'
    )
    requested_date = models.DateField()
    requested_time = models.TimeField()
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"Appointment: {self.patient} with {self.doctor} "
            f"on {self.requested_date} [{self.status}]"
        )


class TrimsesterUpdate(models.Model):
    TRIMESTER_CHOICES = (
        (1, 'First Trimester (Weeks 1-12)'),
        (2, 'Second Trimester (Weeks 13-26)'),
        (3, 'Third Trimester (Weeks 27-40)'),
    )

    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name='trimester_updates'
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name='trimester_updates'
    )
    trimester_number = models.IntegerField(choices=TRIMESTER_CHOICES)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)
    fetal_heartbeat = models.CharField(max_length=50, blank=True)
    health_notes = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    date_recorded = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return (
            f"Trimester {self.trimester_number} update for "
            f"{self.patient} on {self.date_recorded}"
        )


class Prescription(models.Model):
    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name='prescriptions'
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name='prescriptions'
    )
    title = models.CharField(max_length=200)
    medications = models.TextField()
    dosage_instructions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    prescription_file = models.FileField(
        upload_to='prescriptions/', null=True, blank=True
    )
    date_prescribed = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_prescribed']

    def __str__(self):
        return (
            f"Prescription for {self.patient} by {self.doctor} "
            f"on {self.date_prescribed}"
        )


class MedicalReport(models.Model):
    REPORT_TYPE_CHOICES = (
        ('blood_test', 'Blood Test'),
        ('urine_test', 'Urine Test'),
        ('ultrasound', 'Ultrasound'),
        ('ecg', 'ECG'),
        ('xray', 'X-Ray'),
        ('mri', 'MRI'),
        ('glucose_test', 'Glucose Tolerance Test'),
        ('external_lab', 'External Laboratory'),
        ('other', 'Other'),
    )

    UPLOADED_BY_CHOICES = (
        ('admin', 'Administrator'),
        ('patient', 'Patient'),
    )

    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name='medical_reports'
    )
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_file = models.FileField(upload_to='reports/')
    uploaded_by = models.CharField(max_length=10, choices=UPLOADED_BY_CHOICES)
    uploaded_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True
    )
    report_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-report_date']

    def __str__(self):
        return (
            f"{self.get_report_type_display()} for {self.patient} "
            f"on {self.report_date}"
        )


class ClinicalNote(models.Model):
    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name='clinical_notes'
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name='clinical_notes'
    )
    title = models.CharField(max_length=200)
    note = models.TextField()
    date_noted = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_noted']

    def __str__(self):
        return f"Note for {self.patient} by {self.doctor} on {self.date_noted}"
