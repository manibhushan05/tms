# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-30 13:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0015_mahindragpsdevice_mahindragpsdevicelog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mahindragpsdevice',
            name='imei',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
