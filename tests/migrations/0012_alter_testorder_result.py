# Generated by Django 5.1.3 on 2025-01-03 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0011_testcollectionassignment_collector'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testorder',
            name='result',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
