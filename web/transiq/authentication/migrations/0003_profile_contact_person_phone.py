# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-02 14:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20170511_0046'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='contact_person_phone',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
    ]