# Generated by Django 5.1.3 on 2024-12-26 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0002_patient_age_alter_patient_blood_type_bplevel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='emergency_contact',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
