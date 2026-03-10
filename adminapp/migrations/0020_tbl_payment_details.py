# Generated migration for tbl_payment payment details fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0019_tbl_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='tbl_payment',
            name='card_number_last4',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='tbl_payment',
            name='card_holder_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='tbl_payment',
            name='card_expiry',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='tbl_payment',
            name='upi_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='tbl_payment',
            name='upi_mobile',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='tbl_payment',
            name='bank_account_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='tbl_payment',
            name='bank_holder_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='tbl_payment',
            name='bank_ifsc_code',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
        migrations.AddField(
            model_name='tbl_payment',
            name='bank_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
