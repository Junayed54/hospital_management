# Generated by Django 5.1.3 on 2024-12-24 17:21

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='age',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='blood_type',
            field=models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], max_length=5),
        ),
        migrations.CreateModel(
            name='BPLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('systolic', models.PositiveIntegerField()),
                ('diastolic', models.PositiveIntegerField()),
                ('date', models.DateField(default=datetime.date.today)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bp_levels', to='patients.patient')),
            ],
        ),
        migrations.CreateModel(
            name='CholesterolLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.FloatField()),
                ('date', models.DateField(default=datetime.date.today)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cholesterol_levels', to='patients.patient')),
            ],
        ),
        migrations.CreateModel(
            name='HeartRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.PositiveIntegerField()),
                ('date', models.DateField(default=datetime.date.today)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='heart_rates', to='patients.patient')),
            ],
        ),
        migrations.CreateModel(
            name='SugarLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.FloatField()),
                ('date', models.DateField(default=datetime.date.today)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sugar_levels', to='patients.patient')),
            ],
        ),
    ]
