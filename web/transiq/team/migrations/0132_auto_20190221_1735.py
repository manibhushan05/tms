# Generated by Django 2.0.2 on 2019-02-21 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0131_auto_20181220_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='pod_status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('unverified', 'Unverified'), ('rejected', 'Rejected'), ('completed', 'Delivered'), ('not_required', 'Not Required')], default='pending', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='pod_status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('unverified', 'Unverified'), ('rejected', 'Rejected'), ('completed', 'Delivered'), ('not_required', 'Not Required')], default='pending', max_length=20, null=True),
        ),
    ]
