# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-25 11:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sme', '0002_sme_gstin'),
    ]

    operations = [
        migrations.AddField(
            model_name='sme',
            name='is_gst_applicable',
            field=models.BooleanField(default=False),
        ),
    ]
