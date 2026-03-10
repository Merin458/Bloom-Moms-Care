#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BloomMomsproject.settings')
django.setup()

from adminapp.models import tbl_patient

# Fetch all patients and check their status values
patients = tbl_patient.objects.all()
print(f'Showing first 10 patient status values:')
print('-' * 60)
for i, patient in enumerate(patients[:10]):
    print(f'{i+1}. {patient.patient_name}: status="{patient.status}"')

# Check unique status values
unique_statuses = tbl_patient.objects.values('status').distinct()
print()
print(f'Unique status values in database:')
for status_obj in unique_statuses:
    status = status_obj['status']
    count = tbl_patient.objects.filter(status=status).count()
    if status:
        print(f'  "{status}": {count} patients')
    else:
        print(f'  (NULL/Empty): {count} patients')
