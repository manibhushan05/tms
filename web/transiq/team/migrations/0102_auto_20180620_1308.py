# Generated by Django 2.0.5 on 2018-06-20 13:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('team', '0101_auto_20180619_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendinginwardpaymententry',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pending_inward_payment_entry_changed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pendinginwardpaymententry',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pending_inward_payment_entry_created_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
