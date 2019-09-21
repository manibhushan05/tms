# Generated by Django 2.0.5 on 2018-06-22 02:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0105_auto_20180621_1530'),
    ]

    operations = [
        migrations.RenameField(
            model_name='debitnotesupplier',
            old_name='credit_amount',
            new_name='debit_amount',
        ),
        migrations.RenameField(
            model_name='historicaldebitnotesupplier',
            old_name='credit_amount',
            new_name='debit_amount',
        ),
        migrations.AlterField(
            model_name='debitnotesupplier',
            name='adjusted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='debit_note_supplier_adjusted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='debitnotesupplier',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='debit_note_supplier_approved_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
