# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-24 19:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0015_auto_20180417_1922'),
        ('employee', '0006_auto_20170520_1229'),
        ('broker', '0003_auto_20180328_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='broker',
            name='aaho_office',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='utils.AahoOffice'),
        ),
        migrations.AddField(
            model_name='broker',
            name='aaho_poc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employee.Employee'),
        ),
    ]