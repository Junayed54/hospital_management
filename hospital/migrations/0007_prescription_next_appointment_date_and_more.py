# Generated by Django 5.1.3 on 2024-12-05 12:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0006_alter_appointment_appointment_date'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='next_appointment_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='prescription',
            name='treatment_result',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='appointment_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Medication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('dosage', models.CharField(max_length=50)),
                ('frequency', models.CharField(max_length=50)),
                ('duration', models.CharField(max_length=50)),
                ('notes', models.TextField(blank=True, null=True)),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medications', to='hospital.prescription')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
                ('scheduled_time', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
