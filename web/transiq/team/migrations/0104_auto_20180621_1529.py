# Generated by Django 2.0.5 on 2018-06-21 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0103_auto_20180621_1506'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='creditnotecustomer',
            name='date',
        ),
        migrations.RemoveField(
            model_name='creditnotecustomer',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='creditnotecustomer',
            name='issued_on',
        ),
        migrations.RemoveField(
            model_name='creditnotecustomerdirectadvance',
            name='date',
        ),
        migrations.RemoveField(
            model_name='creditnotecustomerdirectadvance',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='creditnotecustomerdirectadvance',
            name='issued_on',
        ),
        migrations.RemoveField(
            model_name='creditnotesupplier',
            name='date',
        ),
        migrations.RemoveField(
            model_name='creditnotesupplier',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='creditnotesupplier',
            name='issued_on',
        ),
        migrations.RemoveField(
            model_name='debitnotecustomer',
            name='date',
        ),
        migrations.RemoveField(
            model_name='debitnotecustomer',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='debitnotecustomer',
            name='issued_on',
        ),
        migrations.RemoveField(
            model_name='debitnotesupplier',
            name='date',
        ),
        migrations.RemoveField(
            model_name='debitnotesupplier',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='debitnotesupplier',
            name='issued_on',
        ),
        migrations.RemoveField(
            model_name='debitnotesupplierdirectadvance',
            name='date',
        ),
        migrations.RemoveField(
            model_name='debitnotesupplierdirectadvance',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='debitnotesupplierdirectadvance',
            name='issued_on',
        ),
        migrations.RemoveField(
            model_name='historicalcreditnotecustomer',
            name='date',
        ),
        migrations.RemoveField(
            model_name='historicalcreditnotecustomer',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='historicalcreditnotecustomer',
            name='issued_on',
        ),
        migrations.RemoveField(
            model_name='historicalcreditnotecustomerdirectadvance',
            name='date',
        ),
        migrations.RemoveField(
            model_name='historicalcreditnotecustomerdirectadvance',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='historicalcreditnotecustomerdirectadvance',
            name='issued_on',
        ),
        migrations.RemoveField(
            model_name='historicalcreditnotesupplier',
            name='date',
        ),
        migrations.RemoveField(
            model_name='historicalcreditnotesupplier',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='historicalcreditnotesupplier',
            name='issued_on',
        ),
        migrations.RemoveField(
            model_name='historicaldebitnotecustomer',
            name='date',
        ),
        migrations.RemoveField(
            model_name='historicaldebitnotecustomer',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='historicaldebitnotecustomer',
            name='issued_on',
        ),
        migrations.RemoveField(
            model_name='historicaldebitnotesupplier',
            name='date',
        ),
        migrations.RemoveField(
            model_name='historicaldebitnotesupplier',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='historicaldebitnotesupplier',
            name='issued_on',
        ),
        migrations.RemoveField(
            model_name='historicaldebitnotesupplierdirectadvance',
            name='date',
        ),
        migrations.RemoveField(
            model_name='historicaldebitnotesupplierdirectadvance',
            name='issued_by',
        ),
        migrations.RemoveField(
            model_name='historicaldebitnotesupplierdirectadvance',
            name='issued_on',
        ),
        migrations.AlterField(
            model_name='creditnotecustomerdirectadvance',
            name='credit_note_number',
            field=models.CharField(max_length=17, unique=True),
        ),
        migrations.AlterField(
            model_name='creditnotesupplier',
            name='credit_note_number',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='debitnotecustomer',
            name='debit_note_number',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='debitnotesupplier',
            name='debit_note_number',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='debitnotesupplierdirectadvance',
            name='debit_note_number',
            field=models.CharField(max_length=17, unique=True),
        ),
        migrations.AlterField(
            model_name='historicalcreditnotecustomerdirectadvance',
            name='credit_note_number',
            field=models.CharField(db_index=True, max_length=17),
        ),
        migrations.AlterField(
            model_name='historicalcreditnotesupplier',
            name='credit_note_number',
            field=models.CharField(db_index=True, max_length=16),
        ),
        migrations.AlterField(
            model_name='historicaldebitnotecustomer',
            name='debit_note_number',
            field=models.CharField(db_index=True, max_length=16),
        ),
        migrations.AlterField(
            model_name='historicaldebitnotesupplier',
            name='debit_note_number',
            field=models.CharField(db_index=True, max_length=16),
        ),
        migrations.AlterField(
            model_name='historicaldebitnotesupplierdirectadvance',
            name='debit_note_number',
            field=models.CharField(db_index=True, max_length=17),
        ),
    ]
