# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-30 11:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0019_supplier_serving_states'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsupplier',
            name='pin',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='pin',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]