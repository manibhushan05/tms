# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-20 19:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_auto_20170520_1229'),
        ('sme', '0008_auto_20171106_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='sme',
            name='aaho_poc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employee.Employee'),
        ),
        migrations.AddField(
            model_name='sme',
            name='credit_period',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
