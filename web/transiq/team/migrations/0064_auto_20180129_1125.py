# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-29 11:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0063_auto_20180125_1640'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inwardpayment',
            old_name='cheque_number',
            new_name='trn',
        ),
    ]
