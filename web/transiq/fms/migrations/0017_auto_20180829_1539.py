# Generated by Django 2.0.5 on 2018-08-29 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fms', '0016_auto_20180816_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobileappversions',
            name='app_name',
            field=models.CharField(choices=[('AS', 'Aaho Sales'), ('AC', 'Aaho Customer'), ('AO', 'Aaho Owner'), ('AE', 'Aaho Employee')], default='AO', max_length=15, null=True),
        ),
    ]