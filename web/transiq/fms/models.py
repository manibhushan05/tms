from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords
from storages.backends.s3boto3 import S3Boto3Storage
from django.db.models.signals import post_save
from fms.signals import requirement_post_save_handler

AWS_ACCESS_KEY = 'AKIAJXFC3JRVYNIHX2UA'
AWS_SECRET_ACCESS_KEY = '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'

BUCKET_NAME = 'fmsdocuments'

s3_storage = S3Boto3Storage(access_key=AWS_ACCESS_KEY, secret_key=AWS_SECRET_ACCESS_KEY, bucket=BUCKET_NAME)


def upload_filename(*args, **kwargs):
    return ''


DOCUMENT_TYPE_CHOICES = (
    ('PAN', 'PAN Card'),
    ('DL', 'Driving Licence'),
    ('EL', 'Election ID'),
    ('AC', 'Aadhar Card'),
    ('PT', 'Passport'),
    ('RC', 'Ration Card'),

    ('PUC', 'Puc Certificate'),
    ('FIT', 'Fitness Certificate'),
    ('REG', 'Registration Certificate'),
    ('PERM', 'Permission Certificate'),
    ('INS', 'Insurance Certificate'),

    ('DEC', 'Declaration'),
)

BEARER_CHOICES = (
    ('owner', 'owner'),
    ('driver', 'driver'),
    ('vehicle', 'vehicle'),
    ('supplier', 'supplier'),
)

REQ_STATUS = (
    ('open', 'Open'),
    ('cancelled', 'Cancelled'),
    ('fulfilled', 'Fulfilled'),
    ('unverified', 'Unverified'),
    ('lapsed', 'Lapsed'),
)

REQ_CANCEL_REASONS = (
    ('trucks_not_available', 'Trucks Not Available'),
    ('rate_not_matching', 'Rate Not Matching'),
    ('loading_cancelled_or_postponed', 'Loading Cancelled or Postponed'),
    ('customer_gave_to_other_transporter', 'Customer gave to other transporter'),
)

ANDROID_APPS = (
    ('AS', 'Aaho Sales'),
    ('AC', 'Aaho Customer'),
    ('AO', 'Aaho Owner'),
    ('AE', 'Aaho Employee'),
    ('WB', 'Aaho Web'),
)

APP_PLATFORM = (
    ('android', 'Android'),
    ('ios', 'IOS')
)

APP_VERSION_UPGRADE_TYPE = (
    ('force', 'Forcefull'),
    ('recommend', 'Recommended')
)

class Document(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # user who uploaded the document
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # the model this doc belongs to
    document_bearer_type = models.CharField(max_length=50, choices=BEARER_CHOICES)
    document_bearer_id = models.PositiveIntegerField()

    # field_name for the model
    document_purpose = models.CharField(max_length=100)

    # nature of the document, like passport or aadhar card
    document_type = models.CharField(max_length=100, choices=DOCUMENT_TYPE_CHOICES, null=True, blank=True)

    # document id
    document_id = models.CharField(max_length=100, null=True, blank=True)

    document = models.CharField(max_length=255, help_text='s3 file key')
    document_thumb = models.CharField(max_length=255, help_text='s3 file key', null=True, blank=True)

    @staticmethod
    def new(user, bearer, field_name, document_type, document, doc_id, thumb):
        return Document(
            user=user, document_bearer_type=bearer.__class__.__name__.lower(),
            document_bearer_id=bearer.id, document_purpose=field_name,
            document_type=document_type, document=document, document_id=doc_id, document_thumb=thumb)

    def __str__(self):
        return self.document

    def to_json(self):
        return {
            'url': self.document,
            'thumb_url': self.document_thumb,
            'document_id': self.document_id,
            'document_type': self.document_type,
            'document_purpose': self.document_purpose
        }


class MobileAppVersions(models.Model):

    app_platform = models.CharField(max_length=15, null=True, choices=APP_PLATFORM, default='android')
    app_name = models.CharField(max_length=15, null=True, choices=ANDROID_APPS, default='AO')
    app_version = models.CharField(max_length=15, null=True)
    comment = models.CharField(max_length=100, null=True, default='Latest_version')
    upgrade_type = models.CharField(max_length=30, null=True, choices=APP_VERSION_UPGRADE_TYPE, default='recommend')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='androidappversions_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s, %s, %s' % (
        self.created_on, self.app_name, self.app_version)


class Requirement(models.Model):
    client = models.ForeignKey(
        'sme.Sme', blank=True, null=True, related_name='requirements_placed_by',
        on_delete=models.CASCADE,
        verbose_name='Customer who placed requirement'
    )
    from_shipment_date = models.DateField(null=True, blank=True)
    to_shipment_date = models.DateField(null=True, blank=True)
    from_city = models.ForeignKey('utils.City', null=True, blank=True, related_name='req_from_city',
                                  on_delete=models.CASCADE)
    to_city = models.ForeignKey('utils.City', null=True, blank=True, related_name='req_to_city', on_delete=models.CASCADE)
    aaho_office = models.ForeignKey('utils.AahoOffice', null=True, related_name='aaho_office', on_delete=models.CASCADE)
    tonnage = models.DecimalField(blank=True, null=True, default=0, max_digits=6, decimal_places=2)
    no_of_vehicles = models.IntegerField(blank=True, null=True, default=0)
    rate = models.IntegerField(blank=True, null=True, default=0)

    material = models.CharField(max_length=35, null=True)
    type_of_vehicle = models.ForeignKey(
        'utils.VehicleCategory', blank=True, null=True, related_name='vehicle_type_requirements',
        on_delete=models.CASCADE,
        verbose_name='Type of Vehicle'
    )
    req_status = models.CharField(max_length=35, null=True, choices=REQ_STATUS, default='unverified')
    remark = models.CharField(max_length=25, null=True, blank=True)
    cancel_reason = models.CharField(max_length=75, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='requirement_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s, %s, %s, %s, %s' % (
        self.from_shipment_date, self.client, self.from_city, self.to_city, self.material)


post_save.connect(requirement_post_save_handler, sender=Requirement)


class QuoteVehicles(models.Model):
    vehicle_no = models.CharField(max_length=20)
    status = models.CharField(max_length=15, null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='vehicle_quote_created_by',
                                   on_delete=models.CASCADE)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s, %s' % (
            self.vehicle_no, self.status)


class RequirementVehicleQuote(models.Model):
    requirement = models.ForeignKey(Requirement, related_name='requirement_quote', on_delete=models.CASCADE)
    quote_vehicle = models.ForeignKey(QuoteVehicles, related_name='requirement_vehicle_quote', on_delete=models.CASCADE)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='requirement_vehicle_quote_created_by',
                                   on_delete=models.CASCADE)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s, %s' % (
            self.requirement, self.quote_vehicle)


class RequirementQuote(models.Model):
    broker = models.ForeignKey('broker.Broker', related_name='broker_quote', null=True, on_delete=models.CASCADE)
    supplier = models.ForeignKey('supplier.Supplier', related_name='supplier_quote', null=True, on_delete=models.CASCADE)
    requirement_vehicle_quote = models.ForeignKey(RequirementVehicleQuote, related_name='requirement_quote',
                                                  null=True, blank=True, on_delete=models.CASCADE)
    rate = models.CharField(max_length=15, null=True)
    status = models.CharField(max_length=15, null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='requirement_quote_created_by', on_delete=models.CASCADE)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return "{}{}{}".format(self.supplier, self.rate, self.status)

