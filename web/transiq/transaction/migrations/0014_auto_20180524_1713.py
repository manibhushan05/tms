# Generated by Django 2.0 on 2018-05-24 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0013_auto_20180523_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insurance',
            name='is_insured',
            field=models.CharField(blank=True, choices=[('yes', 'YES'), ('no', 'NO')], max_length=4, null=True),
        ),
    ]
