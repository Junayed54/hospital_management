# Generated by Django 5.1.3 on 2025-01-03 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0012_alter_testorder_result'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='result',
            field=models.TextField(blank=True, null=True),
        ),
    ]
