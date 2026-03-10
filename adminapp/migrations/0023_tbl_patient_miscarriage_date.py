# Generated migration for miscarriage_date field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0022_tbl_patient_emergency_notes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tbl_patient',
            name='miscarriage_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
