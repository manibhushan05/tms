# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-11 18:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sme', '0015_auto_20180411_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='sme',
            name='lr_format_type',
            field=models.CharField(choices=[('S', 'Serial'), ('D', 'Default')], default='D', max_length=20, null=True),
        ),
    ]
