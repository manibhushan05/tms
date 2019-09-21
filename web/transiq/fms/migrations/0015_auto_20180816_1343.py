# Generated by Django 2.0.5 on 2018-08-16 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0012_remove_broker_updated'),
        ('fms', '0014_auto_20180630_0947'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalrequirementquote',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='requirementquote',
            name='supplier',
        ),
        migrations.AddField(
            model_name='historicalrequirementquote',
            name='broker',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='broker.Broker'),
        ),
        migrations.AddField(
            model_name='requirementquote',
            name='broker',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='broker_quote', to='broker.Broker'),
        ),
    ]
