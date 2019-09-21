# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-25 17:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supplier', '0008_auto_20180425_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalContactPerson',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('updated_on', models.DateTimeField(blank=True, editable=False)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('changed_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('supplier', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='supplier.Supplier')),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical contact person',
            },
        ),
        migrations.CreateModel(
            name='HistoricalContactPersonPhone',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('phone', models.CharField(db_index=True, max_length=15)),
                ('active', models.BooleanField(default=True)),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('updated_on', models.DateTimeField(blank=True, editable=False)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('changed_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical contact person phone',
            },
        ),
        migrations.RemoveField(
            model_name='driver',
            name='name',
        ),
        migrations.RemoveField(
            model_name='historicaldriver',
            name='name',
        ),
        migrations.AddField(
            model_name='contactperson',
            name='changed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supplier_contact_person', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contactperson',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contactperson',
            name='deleted_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contactperson',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contactpersonphone',
            name='changed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supplier_contact_persom', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contactpersonphone',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contactpersonphone',
            name='deleted_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalcontactpersonphone',
            name='contact_person',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='supplier.ContactPerson'),
        ),
        migrations.AddField(
            model_name='historicalcontactpersonphone',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]