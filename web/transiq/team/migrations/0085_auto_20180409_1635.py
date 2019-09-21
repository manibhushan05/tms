# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-09 16:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0084_auto_20180407_0916'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalmanualbooking',
            name='actual_weight',
        ),
        migrations.RemoveField(
            model_name='manualbooking',
            name='actual_weight',
        ),
        migrations.AddField(
            model_name='historicalmanualbooking',
            name='delivered_weight',
            field=models.DecimalField(blank=True, decimal_places=3, default=1, max_digits=12, null=True, verbose_name='Delivered Weight (MT)'),
        ),
        migrations.AddField(
            model_name='historicalmanualbooking',
            name='loaded_weight',
            field=models.DecimalField(blank=True, decimal_places=3, default=1, max_digits=12, null=True, verbose_name='Loaded Weight (MT)'),
        ),
        migrations.AddField(
            model_name='manualbooking',
            name='delivered_weight',
            field=models.DecimalField(blank=True, decimal_places=3, default=1, max_digits=12, null=True, verbose_name='Delivered Weight (MT)'),
        ),
        migrations.AddField(
            model_name='manualbooking',
            name='loaded_weight',
            field=models.DecimalField(blank=True, decimal_places=3, default=1, max_digits=12, null=True, verbose_name='Loaded Weight (MT)'),
        ),
    ]
