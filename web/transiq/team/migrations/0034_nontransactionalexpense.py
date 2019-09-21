# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-12 14:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0005_aahooffice_branch_name'),
        ('employee', '0006_auto_20170520_1229'),
        ('team', '0033_auto_20170531_1247'),
    ]

    operations = [
        migrations.CreateModel(
            name='NonTransactionalExpense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid_to', models.CharField(blank=True, max_length=300, null=True)),
                ('amount', models.IntegerField(null=True)),
                ('payment_mode', models.CharField(blank=True, choices=[('cash', 'Cash'), ('neft', 'NEFT'), ('imps', 'IMPS'), ('cheque', 'Cheque')], max_length=30, null=True)),
                ('payment_date', models.DateTimeField(null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='non_transactional_created_by', to='employee.Employee')),
                ('office', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='non_transactional_office', to='utils.AahoOffice')),
                ('paid_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='non_transactional_paid_by', to='employee.Employee')),
            ],
        ),
    ]