# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-26 12:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0005_auto_20180425_0052'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='broker',
            name='aaho_offices',
        ),
    ]
