# Generated migration to simplify tbl_payment model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0020_tbl_payment_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tbl_payment',
            name='card_number_last4',
        ),
        migrations.RemoveField(
            model_name='tbl_payment',
            name='card_holder_name',
        ),
        migrations.RemoveField(
            model_name='tbl_payment',
            name='card_expiry',
        ),
        migrations.RemoveField(
            model_name='tbl_payment',
            name='upi_id',
        ),
        migrations.RemoveField(
            model_name='tbl_payment',
            name='upi_mobile',
        ),
        migrations.RemoveField(
            model_name='tbl_payment',
            name='bank_account_number',
        ),
        migrations.RemoveField(
            model_name='tbl_payment',
            name='bank_holder_name',
        ),
        migrations.RemoveField(
            model_name='tbl_payment',
            name='bank_ifsc_code',
        ),
        migrations.RemoveField(
            model_name='tbl_payment',
            name='bank_name',
        ),
        migrations.RemoveField(
            model_name='tbl_payment',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='tbl_payment',
            name='payment_status',
            field=models.CharField(
                choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='tbl_payment',
            name='transaction_id',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tbl_payment',
            name='unlock_start_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='tbl_payment',
            name='unlock_end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='tbl_payment',
            name='payment_method',
            field=models.CharField(
                choices=[('CARD', 'Card'), ('UPI', 'UPI'), ('NETBANKING', 'Net Banking')],
                max_length=20,
            ),
        ),
    ]
