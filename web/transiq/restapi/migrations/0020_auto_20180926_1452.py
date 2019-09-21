# Generated by Django 2.0.5 on 2018-09-26 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0019_auto_20180924_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingstatusesmappinglocation',
            name='city',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='historicalbookingstatusesmappinglocation',
            name='city',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='bookingstatusesmappinglocation',
            name='country',
            field=models.CharField(default='India', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='historicalbookingstatusesmappinglocation',
            name='country',
            field=models.CharField(default='India', max_length=100, null=True),
        ),
    ]