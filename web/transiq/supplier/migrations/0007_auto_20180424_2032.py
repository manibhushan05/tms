# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-24 20:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0015_auto_20180417_1922'),
        ('employee', '0006_auto_20170520_1229'),
        ('supplier', '0006_auto_20170526_1318'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleInsurance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('insurance_number', models.CharField(max_length=25, null=True)),
                ('issued_on', models.DateField(null=True)),
                ('expired_by', models.DateField(null=True)),
                ('insurer', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VehiclePUC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='booking',
            name='driver',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='transporter',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='vehicle',
        ),
        migrations.RemoveField(
            model_name='document',
            name='user',
        ),
        migrations.RemoveField(
            model_name='inwardpayment',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='inwardpayment',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='outwardpayment',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='outwardpayment',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='owner',
            name='account_details',
        ),
        migrations.RemoveField(
            model_name='owner',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='owner',
            name='tds_declaration_doc',
        ),
        migrations.RemoveField(
            model_name='transporter',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='driver',
            name='driving_licence_docs',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='aadhaar_number',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='pan',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='body_type',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='driver',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='fitness_certificate',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='insurance_certificate_docs',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='insurance_number',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='insurance_validity',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='insurer',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='permit_certificate',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='puc_certificate',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='registration_certificate_docs',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='vehicle_type',
        ),
        migrations.AddField(
            model_name='supplier',
            name='aaho_offices',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='utils.AahoOffice'),
        ),
        migrations.AddField(
            model_name='supplier',
            name='aaho_poc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employee.Employee'),
        ),
        migrations.AddField(
            model_name='supplier',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='utils.City'),
        ),
        migrations.AddField(
            model_name='supplier',
            name='pin',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='vehicle_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='supplier.VehicleCategory'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='chassis_number',
            field=models.CharField(blank=True, help_text='Enter VIN and last 6 digits are chassis number', max_length=17, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='engine_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.DeleteModel(
            name='Booking',
        ),
        migrations.DeleteModel(
            name='Document',
        ),
        migrations.DeleteModel(
            name='InwardPayment',
        ),
        migrations.DeleteModel(
            name='OutwardPayment',
        ),
        migrations.DeleteModel(
            name='Owner',
        ),
        migrations.DeleteModel(
            name='Transporter',
        ),
        migrations.AddField(
            model_name='vehiclepuc',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supplier.Vehicle'),
        ),
        migrations.AddField(
            model_name='vehicleinsurance',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supplier.Vehicle'),
        ),
    ]