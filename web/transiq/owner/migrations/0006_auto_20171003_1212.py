# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-03 12:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owner', '0005_auto_20170510_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='owner',
            name='pan',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
        migrations.AddField(
            model_name='owner',
            name='route_temp',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
