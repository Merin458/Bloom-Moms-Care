# Generated migration for tbl_payment model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0018_unlock_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='tbl_payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('plan_duration', models.IntegerField(help_text='Duration in months (1, 3, or 6)')),
                ('payment_method', models.CharField(choices=[('card', 'Card'), ('upi', 'UPI'), ('bank', 'Bank Transfer')], max_length=20)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('unlock_start_date', models.DateField(blank=True, null=True)),
                ('unlock_end_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='adminapp.tbl_patient')),
            ],
            options={
                'db_table': 'tbl_payment',
                'ordering': ['-created_at'],
            },
        ),
    ]
