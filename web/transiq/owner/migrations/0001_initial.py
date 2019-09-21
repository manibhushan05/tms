# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-26 17:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('utils', '0001_initial'),
        ('driver', '0001_initial'),
        ('fms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FuelCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.CharField(default='1001507486', max_length=30)),
                ('card_number', models.CharField(max_length=40, null=True, unique=True)),
                ('issue_date', models.DateField(blank=True, null=True)),
                ('expiry_date', models.DateField(null=True)),
                ('update_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FuelCardTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid_to', models.CharField(blank=True, max_length=70, null=True)),
                ('amount', models.IntegerField(default=0)),
                ('payment_date', models.DateTimeField()),
                ('update_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('fuel_card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='owner.FuelCard')),
            ],
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicles_detail', models.CharField(blank=True, max_length=500, null=True)),
                ('declaration', models.URLField(blank=True, null=True)),
                ('declaration_validity', models.DateField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('account_details', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='utils.Bank')),
                ('address', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='utils.Address')),
                ('declaration_doc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='declaration_owner', to='fms.Document')),
                ('name', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Owner Basic Info',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_route_city', to='utils.City')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_route_city', to='utils.City')),
            ],
            options={
                'verbose_name_plural': 'Route',
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_number', models.CharField(max_length=18, unique=True)),
                ('rc_number', models.CharField(blank=True, max_length=20, null=True)),
                ('permit', models.CharField(blank=True, max_length=25, null=True)),
                ('permit_validity', models.DateField(blank=True, null=True)),
                ('permit_type', models.CharField(blank=True, max_length=70, null=True)),
                ('vehicle_capacity', models.IntegerField(blank=True, null=True, verbose_name='Exact Vehicle Capacity in Kg')),
                ('body_type', models.CharField(blank=True, choices=[('open', 'open'), ('closed', 'closed'), ('semi', 'semi'), ('half', 'half'), ('containerized', 'containerized')], max_length=50, null=True)),
                ('fuel_card_number', models.CharField(blank=True, max_length=50, null=True)),
                ('vehicle_model', models.CharField(blank=True, max_length=30, null=True)),
                ('chesis_number', models.CharField(blank=True, max_length=255, null=True)),
                ('engine_number', models.CharField(blank=True, max_length=255, null=True)),
                ('insurer', models.CharField(blank=True, max_length=100, null=True)),
                ('insurance_number', models.CharField(blank=True, max_length=30, null=True)),
                ('insurance_validity', models.DateField(blank=True, null=True)),
                ('sim_number', models.CharField(blank=True, max_length=20, null=True)),
                ('sim_operator', models.CharField(blank=True, choices=[('aircel', 'Aircel'), ('airtel', 'Airtel'), ('vodafone', 'Vodafone'), ('bsnl', 'BSNL'), ('idea', 'Idea'), ('mtnl', 'MTNL'), ('mts', 'MTS'), ('reliance_cdma', 'Reliance CDMA'), ('reliance_gsm', 'Reliance GSM'), ('t24', 'T24'), ('tata_docomo', 'Tata DOCOMO'), ('tata_indicom', 'Tata Indicom'), ('telenor', 'Telenor'), ('videocon', 'Videocon')], max_length=20, null=True)),
                ('registration_year', models.DateField(blank=True, null=True)),
                ('registration_validity', models.DateField(blank=True, null=True)),
                ('fitness_certificate_number', models.CharField(blank=True, max_length=255, null=True)),
                ('fitness_certificate_issued_on', models.DateField(blank=True, null=True)),
                ('fitness_certificate_validity_date', models.DateField(blank=True, null=True)),
                ('puc_certificate_number', models.CharField(blank=True, max_length=255, null=True)),
                ('puc_certificate_issued_on', models.DateField(blank=True, null=True)),
                ('puc_certificate_validity_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[(b'unloaded', b'unloaded'), (b'loading', b'loading'), (b'loaded', b'loaded'), (b'unloading', b'unloading')], default='unloaded', max_length=20)),
                ('gps_enabled', models.BooleanField(default=False)),
                ('update_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('supplier_name', models.CharField(blank=True, max_length=70, null=True)),
                ('supplier_phone', models.CharField(blank=True, max_length=30, null=True)),
                ('owner_name', models.CharField(blank=True, max_length=70, null=True)),
                ('owner_phone', models.CharField(blank=True, max_length=30, null=True)),
                ('current_city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='utils.City')),
                ('driver', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='driver.Driver')),
                ('driver_app_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='driver.DriverAppUser')),
                ('fitness_certificate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fit_vehicle', to='fms.Document')),
                ('insurance_certificate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ins_vehicle', to='fms.Document')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='owner.Owner')),
                ('permit_certificate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='perm_vehicle', to='fms.Document')),
                ('puc_certificate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='puc_vehicle', to='fms.Document')),
                ('registration_certificate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reg_vehicle', to='fms.Document')),
                ('route', models.ManyToManyField(blank=True, to='owner.Route')),
                ('vehicle_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='main_vehicle', to='utils.VehicleCategory')),
            ],
            options={
                'verbose_name_plural': 'Vehicle Details',
            },
        ),
        migrations.AddField(
            model_name='owner',
            name='route',
            field=models.ManyToManyField(blank=True, to='owner.Route'),
        ),
        migrations.AddField(
            model_name='owner',
            name='taxation_details',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='utils.TaxationID'),
        ),
        migrations.AddField(
            model_name='fuelcardtransaction',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='owner.Vehicle'),
        ),
    ]
