# Generated by Django 2.0.5 on 2018-06-22 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0026_auto_20180621_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insurance',
            name='is_insured',
            field=models.CharField(blank=True, choices=[('yes', 'YES'), ('no', 'NO')], max_length=4, null=True),
        ),
    ]
