# Generated by Django 2.0.2 on 2018-05-17 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0006_auto_20180515_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insurance',
            name='is_insured',
            field=models.CharField(blank=True, choices=[('yes', 'YES'), ('no', 'NO')], max_length=4, null=True),
        ),
    ]
