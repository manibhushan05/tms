# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-25 20:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0009_auto_20180425_1754'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contactpersonphone',
            name='changed_by',
        ),
        migrations.RemoveField(
            model_name='contactpersonphone',
            name='contact_person',
        ),
        migrations.RemoveField(
            model_name='historicalcontactpersonphone',
            name='changed_by',
        ),
        migrations.RemoveField(
            model_name='historicalcontactpersonphone',
            name='contact_person',
        ),
        migrations.RemoveField(
            model_name='historicalcontactpersonphone',
            name='history_user',
        ),
        migrations.DeleteModel(
            name='ContactPersonPhone',
        ),
        migrations.DeleteModel(
            name='HistoricalContactPersonPhone',
        ),
    ]