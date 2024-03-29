# Generated by Django 2.0.2 on 2018-05-13 18:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0018_merge_20180508_1254'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aahooffice',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='bank',
            options={'ordering': ['-id'], 'verbose_name_plural': 'Bank Account Details'},
        ),
        migrations.AlterField(
            model_name='district',
            name='created_by',
            field=models.ForeignKey(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='locality',
            name='created_by',
            field=models.ForeignKey(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pincode',
            name='created_by',
            field=models.ForeignKey(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='subdistrict',
            name='created_by',
            field=models.ForeignKey(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
