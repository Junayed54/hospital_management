# Generated by Django 5.1.3 on 2024-12-31 12:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0005_alter_patient_medical_history'),
        ('tests', '0003_testorder_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testorder',
            name='patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='patients.patient'),
        ),
    ]
