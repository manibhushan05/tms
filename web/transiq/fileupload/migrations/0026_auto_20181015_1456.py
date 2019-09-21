# Generated by Django 2.0.5 on 2018-10-15 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileupload', '0025_auto_20180910_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoicereceiptfile',
            name='invoice_confirm_by_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='invoicereceiptfile',
            name='invoice_confirm_by_phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='invoicereceiptfile',
            name='invoice_confirm_mode',
            field=models.CharField(choices=[('CR', 'Courier'), ('WA', 'Written Acknowledgement'), ('EM', 'Email Screenshot')], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='invoicereceiptfile',
            name='invoice_sent_mode',
            field=models.CharField(choices=[('CR', 'Courier'), ('HD', 'Hand Delivered'), ('EM', 'Email Screenshot')], max_length=2, null=True),
        ),
    ]
