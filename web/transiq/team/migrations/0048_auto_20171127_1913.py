# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-27 19:13
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0047_auto_20171127_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deleteddata',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
    ]
