# Generated by Django 5.1.3 on 2025-03-06 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0015_testorder_total_pay'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testtype',
            name='price',
        ),
        migrations.AddField(
            model_name='testtype',
            name='estimate_time',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='testtype',
            name='fee',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='testtype',
            name='home_collection_available',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='testtype',
            name='pre_test_instruction',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='testtype',
            name='vat',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='testorder',
            name='total_pay',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
