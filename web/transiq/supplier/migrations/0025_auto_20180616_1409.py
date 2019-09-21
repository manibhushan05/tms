# Generated by Django 2.0.5 on 2018-06-16 14:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supplier', '0024_auto_20180610_1147'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsupplier',
            name='created_by',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='supplier',
            name='created_by',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_active': True, 'is_staff': True}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supplier_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='changed_by',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_active': True, 'is_staff': True}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supplier_changed_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
