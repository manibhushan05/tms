# Generated by Django 2.0.5 on 2018-06-18 13:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0099_auto_20180618_1151'),
    ]

    operations = [
        migrations.RenameField(
            model_name='creditnotecustomerdirectadvance',
            old_name='supplier',
            new_name='broker',
        ),
        migrations.RenameField(
            model_name='creditnotesupplier',
            old_name='supplier',
            new_name='broker',
        ),
        migrations.RenameField(
            model_name='debitnotesupplier',
            old_name='supplier',
            new_name='broker',
        ),
        migrations.RenameField(
            model_name='debitnotesupplierdirectadvance',
            old_name='supplier',
            new_name='broker',
        ),
        migrations.RenameField(
            model_name='historicalcreditnotecustomerdirectadvance',
            old_name='supplier',
            new_name='broker',
        ),
        migrations.RenameField(
            model_name='historicalcreditnotesupplier',
            old_name='supplier',
            new_name='broker',
        ),
        migrations.RenameField(
            model_name='historicaldebitnotesupplier',
            old_name='supplier',
            new_name='broker',
        ),
        migrations.RenameField(
            model_name='historicaldebitnotesupplierdirectadvance',
            old_name='supplier',
            new_name='broker',
        ),
    ]