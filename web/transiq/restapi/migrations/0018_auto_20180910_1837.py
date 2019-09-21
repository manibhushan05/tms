# Generated by Django 2.0.5 on 2018-09-10 18:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0017_auto_20180910_1835'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingstatusesmappinglocation',
            name='booking_status_mapping',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='restapi.BookingStatusesMapping'),
        ),
        migrations.AddField(
            model_name='historicalbookingstatusesmappinglocation',
            name='booking_status_mapping',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='restapi.BookingStatusesMapping'),
        ),
    ]
