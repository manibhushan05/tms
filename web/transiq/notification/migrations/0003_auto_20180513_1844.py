# Generated by Django 2.0.2 on 2018-05-13 18:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_auto_20180427_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='changed_by',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
