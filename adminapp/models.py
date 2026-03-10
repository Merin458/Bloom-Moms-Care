from django.db import models
from guestapp.models import tbl_login
from patientapp.models import tbl_appointment

# Create your models here.
class tbl_district(models.Model):
    district_id = models.AutoField(primary_key=True)
    district_name = models.CharField(max_length=100)
    
class tbl_country(models.Model):
    country_id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=100)

class tbl_doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    doctor_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100,null=True, blank=True)
    experience = models.IntegerField()
    hospital_timimg = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    login_id = models.ForeignKey(tbl_login, on_delete=models.CASCADE, null=True, blank=True)
    

class tbl_patient(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Delivered', 'Delivered'),
        ('Miscarriage', 'Miscarriage'),
        ('Emergency', 'Emergency'),
        ('Transferred', 'Transferred'),
    )
    
    patient_id = models.AutoField(primary_key=True)
    patient_name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=200)
    blood_group = models.CharField(max_length=10)
    last_cycle_date = models.DateField()
    current_trimester = models.IntegerField(default=1)
    
    edd_date = models.DateField()
    delivery_date = models.DateField(null=True, blank=True)
    profile_lock_status = models.CharField(max_length=20, default='unlocked')
    lock_start_date = models.DateField(null=True, blank=True)
    unlock_start_date = models.DateField(null=True, blank=True)
    unlock_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    
    # Miscarriage fields
    miscarriage_date = models.DateField(blank=True, null=True)
    miscarriage_notes = models.TextField(blank=True, null=True)
    
    # Emergency fields
    emergency_notes = models.TextField(blank=True, null=True)
    
    # Transfer fields
    transfer_reason = models.TextField(blank=True, null=True)
    transfer_date = models.DateField(blank=True, null=True)
    transfer_summary = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    doctor_id = models.ForeignKey(tbl_doctor, on_delete=models.CASCADE, null=True, blank=True)
    login_id = models.ForeignKey(tbl_login, on_delete=models.CASCADE, null=True, blank=True)

class tbl_doctor_leave(models.Model):
    doctor = models.ForeignKey(tbl_doctor, on_delete=models.CASCADE)
    leave_date = models.DateField()
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


class tbl_medical_record(models.Model):
    record_id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        tbl_patient,
        on_delete=models.CASCADE,
        related_name='medical_records'
    )

    UPLOADED_BY_CHOICES = (
        ('Patient', 'Patient'),
        ('Admin', 'Admin'),
    )

    uploaded_by = models.CharField(
        max_length=20,
        choices=UPLOADED_BY_CHOICES
    )

    patient_uploaded_file = models.FileField(
        upload_to='medical_records/patient/',
        null=True,
        blank=True
    )

    admin_uploaded_file = models.FileField(
        upload_to='medical_records/admin/',
        null=True,
        blank=True
    )

    doctor_view_status = models.BooleanField(default=False)

    description = models.TextField(null=True, blank=True)


    record_date = models.DateField()
    doctor_note = models.TextField(null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_medical_record'
        ordering = ['-record_date']

    def __str__(self):
        return f"Medical Record {self.record_id} - {self.patient}"
  

class tbl_prescription(models.Model):
    prescription_id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        tbl_patient,
        on_delete=models.CASCADE
    )

    doctor = models.ForeignKey(
        tbl_doctor,
        on_delete=models.CASCADE
    )

    appointment = models.ForeignKey(
        tbl_appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    diagnosis = models.TextField()

    medicines = models.TextField(
        help_text="Medicine name, dosage, duration"
    )
    dosage = models.TextField(null=True, blank=True)
    additional_notes = models.TextField(null=True, blank=True)

    prescription_date = models.DateField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_prescription'

    def __str__(self):
        return f"Prescription - {self.patient.name}"


class tbl_payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('NETBANKING', 'Net Banking'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
    )
    
    payment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(tbl_patient, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    plan_duration = models.IntegerField(help_text="Duration in months (1, 3, or 6)")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    unlock_start_date = models.DateField()
    unlock_end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tbl_payment'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment - {self.patient.patient_name} - {self.amount} - {self.payment_status}"
