# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-15 01:18
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0013_auto_20180412_1457'),
        ('owner', '0014_auto_20180316_1200'),
        ('team', '0089_bookingconsignorconsignee_rejectedpod'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingInsurance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_insured', models.BooleanField(default=False)),
                ('insurance_provider', models.CharField(blank=True, max_length=200, null=True)),
                ('insurance_policy_number', models.CharField(blank=True, max_length=200, null=True)),
                ('insured_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True)),
                ('insurance_date', models.DateField(blank=True, null=True)),
                ('insurance_risk', models.CharField(blank=True, max_length=200, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='booking',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='team.ManualBooking'),
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='category',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='utils.City'),
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2018, 4, 15, 1, 18, 17, 560974)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='cst_tin',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='deleted_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='gstin',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='lr',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='team.LrNumber'),
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='pin',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bookingconsignorconsignee',
            name='updated_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='historicalmanualbooking',
            name='consignee_city_fk',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='utils.City'),
        ),
        migrations.AddField(
            model_name='historicalmanualbooking',
            name='consignor_city_fk',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='utils.City'),
        ),
        migrations.AddField(
            model_name='historicalmanualbooking',
            name='vehicle',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='owner.Vehicle'),
        ),
        migrations.AddField(
            model_name='historicalmanualbooking',
            name='vehicle_category',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='utils.VehicleCategory'),
        ),
        migrations.AddField(
            model_name='manualbooking',
            name='consignee_city_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='booking_consignee_city', to='utils.City'),
        ),
        migrations.AddField(
            model_name='manualbooking',
            name='consignor_city_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='booking_consignor_city', to='utils.City'),
        ),
        migrations.AddField(
            model_name='manualbooking',
            name='vehicle',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='owner.Vehicle'),
        ),
        migrations.AddField(
            model_name='manualbooking',
            name='vehicle_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='utils.VehicleCategory'),
        ),
        migrations.AlterField(
            model_name='bookingconsignorconsignee',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='deleteddata',
            name='model',
            field=models.CharField(choices=[('manual_booking', 'Manual Booking'), ('lr_number', 'LR Number'), ('outward_payment', 'Outward Payment'), ('inward_payment', 'Inward Payment'), ('to_pay_invoice', 'To Pay Invoice'), ('tbb_pay_invoice', 'TBB Pay Invoice'), ('invoice', 'Invoice'), ('outward_payment_bill', 'Outward Payment Bill')], max_length=100),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='consignee_address',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='consignee_city',
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='consignee_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='consignee_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='consignee_pin',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='consignor_city',
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='consignor_cst_tin',
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='consignor_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='consignor_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='consignor_pin',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='from_city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='lorry_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='to_city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='type_of_vehicle',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='consignee_address',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='consignee_city',
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='consignee_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='consignee_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='consignee_pin',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='consignor_city',
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='consignor_cst_tin',
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='consignor_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='consignor_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='consignor_pin',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='from_city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='lorry_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='to_city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='type_of_vehicle',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
    ]
