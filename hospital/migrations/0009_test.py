# Generated by Django 5.1.3 on 2024-12-05 16:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0008_appointment_patient_problem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_name', models.CharField(max_length=100)),
                ('test_description', models.TextField(blank=True, null=True)),
                ('test_date', models.DateField(blank=True, null=True)),
                ('result', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='hospital.prescription')),
            ],
        ),
    ]