# Generated migration for unlock feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0017_tbl_prescription_dosage'),
    ]

    operations = [
        migrations.AddField(
            model_name='tbl_patient',
            name='unlock_start_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='tbl_patient',
            name='unlock_end_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
