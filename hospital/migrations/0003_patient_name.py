# Generated by Django 5.1.3 on 2024-12-01 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0002_doctor_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='name',
            field=models.CharField(default='', max_length=150),
        ),
    ]