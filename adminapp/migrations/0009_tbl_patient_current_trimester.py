# Generated migration to add current_trimester field to tbl_patient

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0007_tbl_patient'),
    ]

    operations = [
        migrations.AddField(
            model_name='tbl_patient',
            name='current_trimester',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
