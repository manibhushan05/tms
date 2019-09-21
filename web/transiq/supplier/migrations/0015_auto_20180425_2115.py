# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-25 21:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0014_auto_20180425_2053'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vehicleinsurer',
            options={'verbose_name_plural': 'Insurance Companies'},
        ),
        migrations.AlterField(
            model_name='historicalvehicleinsurer',
            name='name',
            field=models.CharField(db_index=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='vehicleinsurer',
            name='name',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
