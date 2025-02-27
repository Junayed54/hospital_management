# Generated by Django 5.1.3 on 2025-01-06 16:20

import django.db.models.deletion
import hospital.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0015_doctoravailability_waitinglist_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificationFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=hospital.models.certification_upload_path)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
