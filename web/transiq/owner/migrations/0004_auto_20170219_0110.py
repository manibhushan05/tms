# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-19 01:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owner', '0003_auto_20170216_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='owner',
            name='declaration',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
