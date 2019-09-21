# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-12 14:54
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('utils', '0011_auto_20180407_1344'),
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=3, null=True, unique=True)),
                ('name', models.CharField(db_index=True, max_length=70)),
                ('latitude', models.DecimalField(blank=True, decimal_places=12, max_digits=18, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=12, max_digits=18, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utils.State')),
            ],
        ),
        migrations.CreateModel(
            name='Locality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('post_office', models.CharField(max_length=200)),
                ('latitude', models.DecimalField(blank=True, decimal_places=12, max_digits=18, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=12, max_digits=18, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PinCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pin_code', models.PositiveIntegerField(db_index=True, validators=[django.core.validators.MaxValueValidator(999999), django.core.validators.MinValueValidator(110003)])),
                ('latitude', models.DecimalField(blank=True, decimal_places=12, max_digits=18, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=12, max_digits=18, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SubDistrict',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=4, null=True)),
                ('name', models.CharField(db_index=True, max_length=70)),
                ('latitude', models.DecimalField(blank=True, decimal_places=12, max_digits=18, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=12, max_digits=18, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utils.District')),
            ],
        ),
        migrations.AddField(
            model_name='pincode',
            name='sub_district',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utils.SubDistrict'),
        ),
        migrations.AddField(
            model_name='locality',
            name='pin_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utils.PinCode'),
        ),
        migrations.AlterUniqueTogether(
            name='subdistrict',
            unique_together=set([('latitude', 'longitude'), ('district', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='district',
            unique_together=set([('latitude', 'longitude'), ('state', 'name')]),
        ),
    ]