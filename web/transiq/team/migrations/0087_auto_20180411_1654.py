# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-11 16:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0086_auto_20180410_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='pod_status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('unverified', 'Unverified'), ('rejected', 'Rejected'), ('completed', 'Delivered')], default='pending', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='pod_status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('unverified', 'Unverified'), ('rejected', 'Rejected'), ('completed', 'Delivered')], default='pending', max_length=20, null=True),
        ),
    ]
