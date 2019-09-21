from datetime import datetime, timedelta

from django.utils import timezone
from django.utils.html import format_html

from api.models import S3Upload
from authentication.models import Profile
from . import models
from django.contrib import admin
from django.contrib.admin import DateFieldListFilter


class ChequeFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'cheque_number', 'customer_name', 'amount', 'get_uploaded_by', 'get_resolved_by',
                    'resolved_datetime', 'link', 'resolved', 'created_on']
    search_fields = ['id', 'cheque_number', 'customer_name', 'amount', 'uploaded_by__username',
                     'uploaded_by__profile__name', 'uploaded_by__profile__phone', 'resolved_by__username',
                     'resolved_by__profile__name', 'resolved_by__profile__phone']
    autocomplete_fields = ['uploaded_by', 'resolved_by', 'customer', 's3_upload']
    readonly_fields = ['id', 's3_upload', 'created_on', 'updated_on', 's3_url', 'serial', 'created_by', 'changed_by',
                       'deleted', 'deleted_on']

    def get_resolved_by(self, instance):
        if instance.resolved_by:
            return instance.resolved_by.profile.name if isinstance(instance.resolved_by.profile,
                                                                   Profile) else instance.resolved_by.username
        return '-'

    get_resolved_by.short_description = 'Resolved By'

    def get_uploaded_by(self, instance):
        if instance.uploaded_by:
            return instance.uploaded_by.profile.name if isinstance(instance.uploaded_by.profile,
                                                                   Profile) else instance.uploaded_by.username
        return '-'

    get_uploaded_by.short_description = 'Uploaded By'

    def link(self, obj):
        return format_html('<a href="{}">download</a>'.format(obj.s3_upload.public_url()))

    link.short_description = 'Link'


class PODFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'lr', 'booking_id', 'link', 'get_uploaded_by', 'get_verified_by', 'verified', 'is_valid',
                    'verified_datetime', 'created_on']
    search_fields = ['id', 'lr_number__lr_number', 'booking__booking_id', 's3_upload__filename',
                     'verified_by__username', 'verified_by__profile__name', 'verified_by__profile__phone',
                     'uploaded_by__username', 'uploaded_by__profile__name', 'uploaded_by__profile__phone']
    list_filter = [('created_on', DateFieldListFilter), ('verified_datetime', DateFieldListFilter), 'verified',
                   'is_valid', 'uploaded_by', 'verified_by']
    autocomplete_fields = ['uploaded_by', 'verified_by', 'lr_number', 'booking', 's3_upload']
    readonly_fields = ['id', 'created_on', 'updated_on', 's3_upload', 'verified_datetime', 'created_by', 'changed_by',
                       'deleted', 'deleted_on']

    def get_verified_by(self, instance):
        if instance.verified_by:
            return instance.verified_by.profile.name if isinstance(instance.verified_by.profile,
                                                                   Profile) else instance.verified_by.username
        return '-'

    get_verified_by.short_description = 'Verified By'

    def get_uploaded_by(self, instance):
        if instance.uploaded_by:
            return instance.uploaded_by.profile.name if isinstance(instance.uploaded_by.profile,
                                                                   Profile) else instance.uploaded_by.username
        return '-'

    get_uploaded_by.short_description = 'Uploaded By'

    def link(self, obj):
        return format_html('<a href="{}">download</a>'.format(obj.s3_upload.public_url()))

    def lr(self, obj):
        return obj.lr_number.lr_number if obj.lr_number else ''

    def booking_id(self, obj):
        return obj.booking.booking_id if obj.booking else ''

    link.short_description = 'Link'


class MyDateTimeFilter(DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        super(MyDateTimeFilter, self).__init__(*args, **kwargs)

        now = datetime.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)

        today = now.date()

        self.links += ((
            (('Next 7 days'), {
                self.lookup_kwarg_since: str(today),
                self.lookup_kwarg_until: str(today + timedelta(days=7)),
            }),
        ))


class VehicleFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'uploaded_by', 'supplier_vehicle', 'document_category', 'created_on', 'link']
    list_filter = (
        ('created_on', MyDateTimeFilter),
    )
    search_fields = ['id', 'supplier_vehicle__vehicle_number', 'uploaded_by__profile__name', 'uploaded_by__username']
    readonly_fields = ['id', 's3_upload', 'created_by', 'changed_by', 'created_on', 'updated_on',
                       'deleted', 'deleted_on','vehicle','serial','s3_url','s3_thumb_url']
    autocomplete_fields = ['uploaded_by', 'supplier_vehicle']

    def link(self, obj):
        return format_html('<a href="{}">download</a>'.format(obj.s3_upload.public_url()))

    link.short_description = 'Link'


class DriverFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'uploaded_by', 'supplier_driver', 'created_on', 'link']
    search_fields = ['id', 'uploaded_by__profile__name', 'uploaded_by__username', 'supplier_driver__user__profile__name', 'supplier_driver__user__profile__phone']
    readonly_fields = ['id', 'created_on', 's3_upload', 'created_by', 'changed_by', 'updated_on',
                       'deleted', 'deleted_on','s3_url','s3_thumb_url','driver','serial']
    autocomplete_fields = ['uploaded_by', 'driver']

    def link(self, obj):
        return format_html('<a href="{}">download</a>'.format(obj.s3_upload.public_url()))

    link.short_description = 'Link'


class InvoiceReceiptFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_number', 'invoice_receipt', 'uploaded_by', 'verified', 'link']
    search_fields = ['id', 'invoice_number', 'invoice_receipt__invoice_number', 'uploaded_by__profile__name',
                     'uploaded_by__username']
    readonly_fields = ['id', 'created_on', 's3_upload', 'serial', 'created_by', 'changed_by', 'updated_on',
                       'deleted', 'deleted_on']
    autocomplete_fields = ['uploaded_by', 'invoice_receipt']

    def link(self, obj):
        if isinstance(obj.s3_upload, S3Upload):
            return format_html('<a href="{}">download</a>'.format(obj.s3_upload.public_url()))
        return '-'

    link.short_description = 'Link'


class OwnerFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'document_category', 'supplier', 'uploaded_by', 'created_on', 'link']
    list_filter = ['document_category']

    search_fields = ['id', 'document_category', 's3_upload__uuid', 'supplier__user__profile__name',
                     'uploaded_by__profile__name', 'uploaded_by__username']
    readonly_fields = ['id', 's3_upload', 'serial', 'created_by','owner', 'changed_by', 'created_on', 'updated_on',
                       'deleted', 'deleted_on','s3_url','s3_thumb_url']
    autocomplete_fields = ['uploaded_by',  'supplier']

    def link(self, obj):
        return format_html('<a href="{}">download</a>'.format(obj.s3_upload.public_url()))

    link.short_description = 'Link'


class WeighingSlip(admin.ModelAdmin):
    list_display = ('id', 'booking')
    readonly_fields = ['id', 's3_upload', 'serial', 'created_by', 'changed_by', 'created_on', 'updated_on',
                       'deleted', 'deleted_on']


admin.site.register(models.PODFile, PODFileAdmin)
admin.site.register(models.VehicleFile, VehicleFileAdmin)
admin.site.register(models.OwnerFile, OwnerFileAdmin)
admin.site.register(models.DriverFile, DriverFileAdmin)
admin.site.register(models.InvoiceReceiptFile, InvoiceReceiptFileAdmin)
admin.site.register(models.ChequeFile, ChequeFileAdmin)
admin.site.register(models.WeighingSlip, WeighingSlip)
