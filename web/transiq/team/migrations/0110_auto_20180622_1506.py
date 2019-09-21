# Generated by Django 2.0.5 on 2018-06-22 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0109_auto_20180622_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditnotecustomer',
            name='credit_note_number',
            field=models.CharField(editable=False, max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='historicalcreditnotecustomer',
            name='credit_note_number',
            field=models.CharField(db_index=True, editable=False, max_length=16),
        ),
    ]
