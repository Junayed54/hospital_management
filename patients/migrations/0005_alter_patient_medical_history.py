# Generated by Django 5.1.3 on 2024-12-31 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0004_patient_latitude_patient_location_patient_longitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='medical_history',
            field=models.TextField(blank=True, null=True),
        ),
    ]
