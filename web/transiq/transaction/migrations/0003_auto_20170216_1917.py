# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-16 19:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0002_auto_20170202_0901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uservendor',
            name='phone',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='uservendor',
            unique_together=set([]),
        ),
    ]
