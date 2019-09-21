# Generated by Django 2.0.5 on 2018-06-19 16:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sme', '0019_auto_20180514_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='consignorconsignee',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sme_consignor_consignee_changed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='consignorconsignee',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='consignorconsignee',
            name='deleted_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contactdetails',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contact_details_changed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contactdetails',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contactdetails',
            name='deleted_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contractroute',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contract_route_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customercontract',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_contract_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalcontractroute',
            name='created_by',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalcustomercontract',
            name='created_by',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='location',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location_changed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='location',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='location',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='location',
            name='deleted_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='preferredvehicle',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sme_preferred_vehicle_changed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='preferredvehicle',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sme_preffered_vehicle_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='preferredvehicle',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='preferredvehicle',
            name='deleted_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ratetype',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rate_type_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sme',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sme_changed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sme',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sme',
            name='deleted_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='smeenquiry',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sme_enquiry_changed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='smeenquiry',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sme_enquiry_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='smeenquiry',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='smeenquiry',
            name='deleted_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='smetaskemail',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sme_task_email_changed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='smetaskemail',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sme_task_email_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='smetaskemail',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='smetaskemail',
            name='deleted_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='contactdetails',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contact_details_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='contractroute',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contract_route_changed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='customercontract',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_contract_changed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ratetype',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rate_type_changed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sme',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sme_created_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
