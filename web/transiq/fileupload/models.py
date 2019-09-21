# encoding: utf-8
from django.contrib.auth.models import User
from django.db import models

from api.models import S3Upload
from driver.models import Driver
from owner.models import Vehicle, Owner
from sme.models import Sme
from supplier.models import Supplier
from team.models import LrNumber, ManualBooking, Invoice

INVOICE_SENT_MODE_CHOICES = (
    ('CR', 'Courier'),
    ('HD', 'Hand Delivered'),
    ('EM', 'Email Screenshot')
)
INVOICE_CONFIRM_MODE_CHOICES = (
    ('PH', 'Phone'),
    ('WA', 'Written Acknowledgement'),
    ('EM', 'Email Screenshot')
)


class PODFile(models.Model):
    uploaded_by = models.ForeignKey(User, null=True, blank=True, related_name='pod_file_uploaded_by',
                                    on_delete=models.CASCADE)
    verified_by = models.ForeignKey(User, null=True, blank=True, related_name='pod_file_verified_by',
                                    on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    lr_number = models.ForeignKey(LrNumber, null=True, related_name='pod_files', on_delete=models.CASCADE)
    booking = models.ForeignKey(ManualBooking, null=True, blank=True, on_delete=models.CASCADE)
    s3_url = models.URLField(blank=True, null=True, unique=True)
    s3_thumb_url = models.URLField(blank=True, null=True, unique=True)
    serial = models.CharField(max_length=20)
    s3_upload = models.ForeignKey(S3Upload, related_name='upload_pod', on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    verified_datetime = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="pod_file_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="pod_file_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('lr_number', 'serial')

    def url(self):
        return self.s3_upload.public_url()

    def filename(self):
        return self.s3_upload.filename

    def __unicode__(self):
        return self.filename()

    def to_json(self):
        return {
            'uploaded_by': self.uploaded_by_id,
            'lr_number': self.lr_number_id,
            'serial': self.serial,
            'filename': self.filename(),
            'url': self.url()
        }


class WeighingSlip(models.Model):
    uploaded_by = models.ForeignKey(User, null=True, blank=True, related_name='weighing_slip_uploaded_by',
                                    on_delete=models.CASCADE)
    verified_by = models.ForeignKey(User, null=True, blank=True, related_name='weighing_slip_file_verified_by',
                                    on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    booking = models.ForeignKey(ManualBooking, null=True, blank=True, on_delete=models.CASCADE)
    s3_url = models.URLField(blank=True, null=True, unique=True)
    s3_thumb_url = models.URLField(blank=True, null=True, unique=True)
    serial = models.CharField(max_length=20)
    s3_upload = models.ForeignKey(S3Upload, related_name='upload_weighing_slip', on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    verified_datetime = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="weighing_slip_file_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="weighing_slip_file_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def url(self):
        return self.s3_upload.public_url()

    def filename(self):
        return self.s3_upload.filename

    def __unicode__(self):
        return self.filename()

    def to_json(self):
        return {
            'uploaded_by': self.uploaded_by_id,
            'booking_id': self.booking_id,
            'serial': self.serial,
            'filename': self.filename(),
            'url': self.url()
        }


class VehicleFile(models.Model):
    document_categories_choices = (
        ('PUC', 'Puc Certificate'),
        ('FIT', 'Fitness Certificate'),
        ('REG', 'Registration Certificate'),
        ('PERM', 'Permission Certificate'),
        ('INS', 'Insurance Certificate'),
    )
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, null=True, related_name='vehicle_files', on_delete=models.CASCADE)
    supplier_vehicle = models.ForeignKey('supplier.Vehicle', null=True, related_name='supplier_vehicle_files',
                                     on_delete=models.CASCADE)
    document_category = models.CharField(max_length=70, choices=document_categories_choices, null=True)
    s3_url = models.URLField(blank=True, null=True, unique=True)
    s3_thumb_url = models.URLField(blank=True, null=True, unique=True)
    serial = models.CharField(max_length=20)
    verified = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    s3_upload = models.ForeignKey(S3Upload, related_name='upload_vehicle', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="vehicle_file_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="vehicle_file_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('vehicle', 'serial')

    def url(self):
        return self.s3_upload.public_url()

    def filename(self):
        return self.s3_upload.filename

    def __unicode__(self):
        return self.filename()

    def to_json(self):
        return {
            'uploaded_by': self.uploaded_by_id,
            'vehicle_number': '' if not self.vehicle else self.vehicle.vehicle_number,
            'serial': self.serial,
            'filename': self.filename(),
            'url': self.url()
        }


class OwnerFile(models.Model):
    DOCUMENT_TYPE_CHOICES = (
        ('PAN', 'PAN Card'),
        ('DL', 'Driving Licence'),
        ('EL', 'Election ID'),
        ('AC', 'Aadhar Card'),
        ('PT', 'Passport'),
        ('RC', 'Ration Card'),
        ('DEC', 'Declaration'),
    )
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, null=True, related_name='owner_files', on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, null=True, related_name='supplier_files', on_delete=models.CASCADE)
    document_category = models.CharField(max_length=70, choices=DOCUMENT_TYPE_CHOICES, null=True)
    s3_url = models.URLField(blank=True, null=True, unique=True)
    s3_thumb_url = models.URLField(blank=True, null=True, unique=True)
    serial = models.CharField(max_length=20)
    verified = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    s3_upload = models.ForeignKey(S3Upload, related_name='upload_owner', on_delete=models.CASCADE)

    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="owner_file_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="owner_file_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('owner', 'serial')

    def url(self):
        return self.s3_upload.public_url()

    def filename(self):
        return self.s3_upload.filename

    def __unicode__(self):
        return self.filename()

    def to_json(self):
        return {
            'uploaded_by': self.uploaded_by_id,
            'owner_name': '' if not self.owner else self.owner.get_name(),
            'serial': self.serial,
            'filename': self.filename(),
            'url': self.url()
        }


class DriverFile(models.Model):
    DOCUMENT_TYPE_CHOICES = (
        ('PAN', 'PAN Card'),
        ('DL', 'Driving Licence'),
        ('EL', 'Election ID'),
        ('AC', 'Aadhar Card'),
        ('PT', 'Passport'),
        ('RC', 'Ration Card'),
    )
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, null=True, related_name='driver_files', on_delete=models.CASCADE)
    supplier_driver = models.ForeignKey(to='supplier.Driver', related_name='supplier_driver_files', blank=True,
                                        null=True,
                                        on_delete=models.CASCADE)
    document_category = models.CharField(max_length=70, choices=DOCUMENT_TYPE_CHOICES, null=True)
    s3_url = models.URLField(blank=True, null=True, unique=True)
    s3_thumb_url = models.URLField(blank=True, null=True, unique=True)
    verified = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    serial = models.CharField(max_length=20)
    s3_upload = models.ForeignKey(S3Upload, related_name='upload_driver', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="driver_file_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="driver_file_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('driver', 'serial')

    def url(self):
        return self.s3_upload.public_url()

    def filename(self):
        return self.s3_upload.filename

    def __unicode__(self):
        return self.filename()

    def to_json(self):
        return {
            'uploaded_by': self.uploaded_by_id,
            'driver_name': '' if not self.driver else self.driver.name,
            'serial': self.serial,
            'filename': self.filename(),
            'url': self.url()
        }


class ChequeFile(models.Model):
    uploaded_by = models.ForeignKey(User, null=True, blank=True, related_name='fileupload_cheque_uploaded_by',
                                    on_delete=models.CASCADE)
    resolved_by = models.ForeignKey(User, null=True, blank=True, related_name='fileupload_cheque_resolved_by',
                                    on_delete=models.CASCADE)
    s3_url = models.URLField(blank=True, null=True, unique=True)
    resolved_datetime = models.DateTimeField(null=True, blank=True)
    customer_name = models.CharField(max_length=300, null=True)
    customer = models.ForeignKey(Sme, related_name='cheque_files', null=True, blank=True, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    cheque_number = models.CharField(max_length=6, null=True, blank=True)
    cheque_date = models.DateField(null=True)
    remarks = models.CharField(max_length=300, blank=True, null=True)
    resolved = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    serial = models.CharField(max_length=20)
    s3_upload = models.ForeignKey(S3Upload, related_name='cheque_files', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="cheque_file_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="cheque_file_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('customer_name', 'serial')

    def url(self):
        return self.s3_upload.public_url()

    def filename(self):
        return self.s3_upload.filename

    def __unicode__(self):
        return self.filename()

    def to_json(self):
        return {
            'uploaded_by': self.uploaded_by_id,
            'customer_name': self.customer_name,
            'serial': self.serial,
            'filename': self.filename(),
            'url': self.url()
        }


class InvoiceReceiptFile(models.Model):
    invoice_sent_mode = models.CharField(max_length=2, choices=INVOICE_SENT_MODE_CHOICES, null=True)
    invoice_confirm_mode = models.CharField(max_length=2, choices=INVOICE_CONFIRM_MODE_CHOICES, null=True)
    invoice_confirm_by_name = models.CharField(max_length=50, null=True, blank=True)
    invoice_confirm_by_phone = models.CharField(max_length=15, null=True, blank=True)

    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    invoice_receipt = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    serial = models.CharField(max_length=20)
    s3_upload = models.ForeignKey(S3Upload, related_name='upload_invoice_receipt', null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="invoice_receipt_file_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="invoice_receipt_file_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def url(self):
        return self.s3_upload.public_url()

    def filename(self):
        return self.s3_upload.filename

    def __unicode__(self):
        return self.filename()

    def to_json(self):
        return {
            'uploaded_by': self.uploaded_by_id,
            'serial': self.serial,
            'filename': self.filename(),
            'url': self.url()
        }
