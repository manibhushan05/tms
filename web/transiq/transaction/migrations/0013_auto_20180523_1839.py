# Generated by Django 2.0 on 2018-05-23 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0012_auto_20180523_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insurance',
            name='is_insured',
            field=models.CharField(blank=True, choices=[('no', 'NO'), ('yes', 'YES')], max_length=4, null=True),
        ),
    ]