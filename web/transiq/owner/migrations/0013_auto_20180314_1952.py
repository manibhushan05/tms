# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-14 19:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('owner', '0012_auto_20180314_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='changed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]