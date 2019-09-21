# Generated by Django 2.0.5 on 2018-07-26 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0115_auto_20180707_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalmanualbooking',
            name='booking_id',
            field=models.CharField(db_index=True, max_length=35, verbose_name='Booking ID'),
        ),
        migrations.AlterField(
            model_name='manualbooking',
            name='booking_id',
            field=models.CharField(max_length=35, unique=True, verbose_name='Booking ID'),
        ),
    ]