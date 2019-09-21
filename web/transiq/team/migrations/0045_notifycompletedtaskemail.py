# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-16 16:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0044_auto_20171116_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotifyCompletedTaskEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task', models.CharField(choices=[('notify_admins_about_pending_pod', 'Notify Admin About Pending POD'), ('notify_weekly_partial_tbb', 'Notify Weekly Partial TBB'), ('notify_admins_about_to_pay_booking', 'Notify About TO Pay Booking'), ('notify_outward_payment_status', 'Notify Outward Payment Status')], max_length=100, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('bookings', models.ManyToManyField(to='team.ManualBooking')),
            ],
        ),
    ]
