# Generated by Django 2.0.5 on 2018-08-16 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0013_broker_destination_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='broker',
            name='destination_state',
            field=models.ManyToManyField(blank=True, related_name='broker_destination_states', to='utils.State'),
        ),
    ]
