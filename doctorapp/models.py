from django.db import models
from guestapp.models import tbl_login
from adminapp.models import tbl_doctor
from adminapp.models import tbl_patient
from patientapp.models import tbl_appointment
# Create your models here.
class tbl_trimester_update(models.Model):
    trimester_id = models.AutoField(primary_key=True)
    doctor_id = models.ForeignKey(tbl_doctor, on_delete=models.CASCADE, null=True, blank=True)
    patient_id = models.ForeignKey(tbl_patient, on_delete=models.CASCADE, null=True, blank=True)
    login_id = models.ForeignKey(tbl_login, on_delete=models.CASCADE, null=True, blank=True)
    trimester_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateField()  



class tbl_visit_history(models.Model):
    visit_id = models.AutoField(primary_key=True)
    patient_id = models.ForeignKey(tbl_patient, on_delete=models.CASCADE)
    doctor_id = models.ForeignKey(tbl_doctor, on_delete=models.CASCADE)
    appointment_id = models.ForeignKey(tbl_appointment, on_delete=models.CASCADE)

    visit_date = models.DateField()
    details = models.TextField()

    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, null=True, blank=True)

    health_status = models.CharField(max_length=50)
    next_visit_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit {self.visit_id} - {self.patient_id}"
    
    from django.db import models


class tbl_delivery_details(models.Model):
    DELIVERY_TYPE_CHOICES = [
        ('Normal', 'Normal Delivery'),
        ('C-Section', 'C-Section'),
        ('Assisted', 'Assisted Delivery'),
    ]

    CONDITION_CHOICES = [
        ('Good', 'Good'),
        ('Stable', 'Stable'),
        ('Critical', 'Critical'),
    ]

    delivery_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        tbl_patient,
        on_delete=models.CASCADE,
        related_name='delivery_details'
    )
    doctor = models.ForeignKey(
        tbl_doctor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deliveries'
    )
    delivery_date = models.DateField()
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_TYPE_CHOICES
    )
    baby_weight = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        help_text="Weight in kg"
    )
    baby_condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES
    )
    mother_condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES
    )
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_delivery_details'
        ordering = ['-delivery_date']

    def __str__(self):
        return f"Delivery - {self.patient} ({self.delivery_date})"

  