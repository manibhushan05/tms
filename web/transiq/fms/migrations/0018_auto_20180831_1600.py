# Generated by Django 2.0.5 on 2018-08-31 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fms', '0017_auto_20180829_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalrequirement',
            name='tonnage',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='requirement',
            name='tonnage',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=6, null=True),
        ),
    ]