# Generated by Django 2.0.5 on 2018-09-10 17:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fileupload', '0024_auto_20180626_1222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podfile',
            name='uploaded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pod_file_uploaded_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
