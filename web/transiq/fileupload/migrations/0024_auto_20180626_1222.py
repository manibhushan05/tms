# Generated by Django 2.0.5 on 2018-06-26 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileupload', '0023_auto_20180619_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='chequefile',
            name='is_valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='driverfile',
            name='is_valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='invoicereceiptfile',
            name='is_valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ownerfile',
            name='is_valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vehiclefile',
            name='is_valid',
            field=models.BooleanField(default=False),
        ),
    ]
