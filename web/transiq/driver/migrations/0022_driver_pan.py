# Generated by Django 2.0.5 on 2018-08-28 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0021_auto_20180702_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='pan',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
    ]
