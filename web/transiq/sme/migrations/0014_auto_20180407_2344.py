# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-07 23:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sme', '0013_auto_20180407_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractroute',
            name='destination',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contract_route_destination', to='utils.City'),
        ),
        migrations.AlterField(
            model_name='contractroute',
            name='source',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contract_route_source', to='utils.City'),
        ),
        migrations.AlterField(
            model_name='historicalcontractroute',
            name='destination',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='utils.City'),
        ),
        migrations.AlterField(
            model_name='historicalcontractroute',
            name='source',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='utils.City'),
        ),
    ]
