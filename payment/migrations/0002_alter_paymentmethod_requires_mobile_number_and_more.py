# Generated by Django 5.1.3 on 2024-12-18 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='requires_mobile_number',
            field=models.BooleanField(blank=True, default=False, help_text='Does this method require a mobile number? (e.g., bKash, Nagad)', null=True),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='requires_transaction_id',
            field=models.BooleanField(blank=True, default=True, help_text='Does this method require a transaction ID?', null=True),
        ),
    ]
