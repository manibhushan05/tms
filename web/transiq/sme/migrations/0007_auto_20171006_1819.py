# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-06 18:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sme', '0006_auto_20170925_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sme',
            name='gstin',
            field=models.CharField(max_length=15, null=True),
        ),
    ]