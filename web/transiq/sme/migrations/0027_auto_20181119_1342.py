# Generated by Django 2.0.5 on 2018-11-19 13:42

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sme', '0026_smesummary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smesummary',
            name='accounting_summary',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='smesummary',
            name='billed_accounting_summary',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='smesummary',
            name='placed_order_accounting_summary',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]