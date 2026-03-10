from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_DOCTOR = 'doctor'
    ROLE_PATIENT = 'patient'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_PATIENT, 'Patient'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_PATIENT)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN

    def is_doctor(self):
        return self.role == self.ROLE_DOCTOR

    def is_patient(self):
        return self.role == self.ROLE_PATIENT

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
