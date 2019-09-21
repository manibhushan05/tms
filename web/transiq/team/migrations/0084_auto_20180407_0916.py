# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-07 09:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0083_auto_20180403_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='billing_type',
            field=models.CharField(blank=True, choices=[('T.B.B.', 'T.B.B.'), ('To Pay', 'To Pay'), ('Paid', 'Paid'), ('contract', 'Contract')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='billing_type',
            field=models.CharField(blank=True, choices=[('T.B.B.', 'T.B.B.'), ('To Pay', 'To Pay'), ('Paid', 'Paid'), ('contract', 'Contract')], max_length=20, null=True),
        ),
    ]
