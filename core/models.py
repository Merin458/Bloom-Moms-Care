from django.db import models
from django.conf import settings
from django.utils import timezone


class DoctorProfile(models.Model):
    SPECIALIZATION_CHOICES = [
        ('gynecologist', 'Gynecologist'),
        ('obstetrician', 'Obstetrician'),
        ('midwife', 'Midwife'),
        ('neonatologist', 'Neonatologist'),
        ('general', 'General Practitioner'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile'
    )
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, default='general')
    qualification = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    available_days = models.CharField(
        max_length=100, blank=True, help_text='E.g., Monday, Wednesday, Friday'
    )
    available_time_start = models.TimeField(null=True, blank=True)
    available_time_end = models.TimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.get_specialization_display()})"


class PatientProfile(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    last_menstrual_period = models.DateField(null=True, blank=True, verbose_name='Last Menstrual Period (LMP)')
    due_date = models.DateField(null=True, blank=True)
    assigned_doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients'
    )
    allergies = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)

    def get_trimester(self):
        """Calculate current trimester based on LMP."""
        if not self.last_menstrual_period:
            return None
        weeks_pregnant = (timezone.now().date() - self.last_menstrual_period).days // 7
        if weeks_pregnant <= 12:
            return 1
        elif weeks_pregnant <= 26:
            return 2
        elif weeks_pregnant <= 40:
            return 3
        return None

    def get_weeks_pregnant(self):
        if not self.last_menstrual_period:
            return None
        return (timezone.now().date() - self.last_menstrual_period).days // 7

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class Appointment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name='appointments'
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name='appointments'
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True, verbose_name='Doctor Notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        return (
            f"Appointment: {self.patient} with Dr. {self.doctor.user.get_full_name()} "
            f"on {self.appointment_date}"
        )


class Prescription(models.Model):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name='prescription', null=True, blank=True
    )
    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name='prescriptions'
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name='prescriptions'
    )
    medications = models.TextField(help_text='List medications with dosage and frequency')
    instructions = models.TextField(blank=True)
    dietary_advice = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    issued_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-issued_date']

    def __str__(self):
        return f"Prescription for {self.patient} by Dr. {self.doctor.user.get_full_name()} on {self.issued_date}"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name='medical_records'
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name='medical_records'
    )
    appointment = models.ForeignKey(
        Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_records'
    )
    diagnosis = models.TextField()
    treatment = models.TextField(blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True, help_text='E.g., 120/80')
    fetal_heart_rate = models.PositiveIntegerField(null=True, blank=True, help_text='Beats per minute')
    notes = models.TextField(blank=True)
    record_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-record_date']

    def __str__(self):
        return f"Record for {self.patient} on {self.record_date}"


class TrimesterTracking(models.Model):
    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name='trimester_trackings'
    )
    trimester = models.PositiveSmallIntegerField(choices=[(1, '1st Trimester'), (2, '2nd Trimester'), (3, '3rd Trimester')])
    week_number = models.PositiveSmallIntegerField()
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    recorded_by_doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.SET_NULL, null=True, blank=True
    )
    date_recorded = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"Trimester {self.trimester} - Week {self.week_number} for {self.patient}"

