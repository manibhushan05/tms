# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-24 17:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20170224_1716'),
        ('team', '0021_auto_20170219_0110'),
    ]

    operations = [
        migrations.AddField(
            model_name='lrnumber',
            name='upload',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.S3Upload'),
        ),
        migrations.AlterField(
            model_name='lrnumber',
            name='datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
