# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-04 17:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0052_pendinginwardpaymententry'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendinginwardpaymententry',
            name='remarks',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pendinginwardpaymententry',
            name='adjusted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pending_payment_adjusted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pendinginwardpaymententry',
            name='adjusted_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pendinginwardpaymententry',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='pendinginwardpaymententry',
            name='uploaded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pending_payment_uploaded_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pendinginwardpaymententry',
            name='uploaded_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
