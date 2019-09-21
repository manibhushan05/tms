# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-12 13:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0012_auto_20170914_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='secugpsdevice',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='tempogogpsdevice',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='tracknovategpsdevice',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='waytrackergpsdevice',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
