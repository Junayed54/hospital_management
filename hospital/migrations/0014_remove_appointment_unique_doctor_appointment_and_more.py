# Generated by Django 5.1.3 on 2024-12-26 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0013_alter_prescription_patient_alter_appointment_patient_and_more'),
        ('patients', '0003_alter_patient_emergency_contact'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='appointment',
            name='unique_doctor_appointment',
        ),
        migrations.AddConstraint(
            model_name='appointment',
            constraint=models.UniqueConstraint(fields=('doctor', 'appointment_date', 'phone_number'), name='unique_doctor_appointment'),
        ),
    ]
