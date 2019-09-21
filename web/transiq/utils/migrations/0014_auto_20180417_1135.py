# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-17 11:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0013_auto_20180412_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleBodyCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='vehiclecategory',
            name='truck_body',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='utils.VehicleBodyCategory'),
        ),
    ]
