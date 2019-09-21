# Generated by Django 2.0.5 on 2018-06-22 02:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0106_auto_20180622_0213'),
    ]

    operations = [
        migrations.RenameField(
            model_name='debitnotesupplierdirectadvance',
            old_name='credit_amount',
            new_name='debit_amount',
        ),
        migrations.RenameField(
            model_name='historicaldebitnotesupplierdirectadvance',
            old_name='credit_amount',
            new_name='debit_amount',
        ),
        migrations.AlterField(
            model_name='creditnotecustomerdirectadvance',
            name='adjusted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='credit_note_customer_advance_adjusted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='creditnotecustomerdirectadvance',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='credit_note_customer_advance_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='debitnotesupplierdirectadvance',
            name='adjusted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='debit_note_supplier_advance_adjusted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='debitnotesupplierdirectadvance',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='debit_note_supplier_advance_approved_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
