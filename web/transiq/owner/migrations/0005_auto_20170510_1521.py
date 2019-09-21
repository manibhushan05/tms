# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-10 15:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('owner', '0004_auto_20170219_0110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='driver',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_driver', to='driver.Driver'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_owner', to='owner.Owner'),
        ),
    ]