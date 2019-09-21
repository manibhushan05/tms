# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-01 20:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0039_auto_20171027_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='manualbooking',
            name='consignee_gstin',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='manualbooking',
            name='consignor_gstin',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='manualbooking',
            name='gst_liability',
            field=models.CharField(blank=True, choices=[('consignor', 'Consignor'), ('consignee', 'Consignee'), ('carrier', 'Carrier'), ('exempted', 'Exempted')], max_length=15, null=True),
        ),
    ]