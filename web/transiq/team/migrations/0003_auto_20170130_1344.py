# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-30 08:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_auto_20170130_1330'),
    ]

    operations = [
        migrations.RenameField(
            model_name='manualbooking',
            old_name='invoice_remarks',
            new_name='remarks_advance_from_company',
        ),
    ]
