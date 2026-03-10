from django.db import models
from guestapp.models import tbl_login
from adminapp.models import *


# Create your models here.
class tbl_appointment(models.Model):
   appointment_id = models.AutoField(primary_key=True)
   patient_id = models.ForeignKey('adminapp.tbl_patient', on_delete=models.CASCADE, null=True, blank=True)
   doctor_id = models.ForeignKey('adminapp.tbl_doctor', on_delete=models.CASCADE, null=True, blank=True)
   appointment_date = models.DateField()
   appointment_time = models.TimeField()
   reason = models.CharField(max_length=200)
   status = models.CharField(max_length=20, default='Pending')
   reschedule_date = models.DateField(null=True, blank=True)
   reschedule_time = models.TimeField(null=True, blank=True)
   admin_note = models.CharField(max_length=300, null=True, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)