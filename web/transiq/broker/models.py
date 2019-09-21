from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import JSONField

from authentication.models import Profile
from driver.models import Driver
from employee.models import Employee
from owner.models import Vehicle, Owner
from utils.models import Address, Bank, TaxationID, City, AahoOffice, State


class Broker(models.Model):
    name = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    address = models.OneToOneField(Address, blank=True, null=True, on_delete=models.CASCADE)
    code = models.CharField(max_length=4, null=True)
    route = models.CharField(max_length=400, null=True)
    aaho_office = models.ForeignKey(AahoOffice, null=True, blank=True, related_name='broker_aaho_office',
                                    on_delete=models.CASCADE)
    aaho_poc = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.CASCADE)
    city = models.ForeignKey(City, related_name='broker_city', null=True, on_delete=models.CASCADE)
    pan = models.CharField(max_length=15, blank=True, null=True)
    id_proof = models.CharField(max_length=70, blank=True)
    account_details = models.OneToOneField(Bank, blank=True, null=True, on_delete=models.CASCADE)
    taxation_details = models.OneToOneField(TaxationID, blank=True, null=True, on_delete=models.CASCADE)
    destination_state = models.ManyToManyField(State, blank=True, related_name='broker_destination_states')
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="broker_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="broker_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Broker Basic Info"
        ordering = ('-id',)

    def __str__(self):
        return '{}, {}'.format(self.get_name(), self.get_phone())

    @property
    def vehicles(self):
        return "\n".join([bv.vehicle.number() for bv in self.broker_vehicle.all()])

    @property
    def aaho_poc_name(self):
        if isinstance(self.aaho_poc, Employee):
            return self.aaho_poc.emp_name()
        return None

    def get_name(self):
        name = None
        if self.name_id:
            try:
                profile = Profile.objects.get(user_id=self.name_id)
                name = profile.name
            except Profile.DoesNotExist:
                pass
        return name

    def get_phone(self):
        phone = None
        if self.name_id:
            try:
                profile = Profile.objects.get(user_id=self.name_id)
                phone = profile.phone if profile.phone else ''
            except Profile.DoesNotExist:
                pass
        return phone

    def get_alt_phone(self):
        phone = None
        if self.name_id:
            try:
                profile = Profile.objects.get(user_id=self.name_id)
                phone = profile.alternate_phone if profile.alternate_phone else ''
            except Profile.DoesNotExist:
                pass
        return phone

    def to_json(self):
        data = {}
        if self.name:
            data['name'] = self.name.profile.name
            data['phone'] = self.name.profile.phone
        return data


class BrokerSummary(models.Model):
    broker = models.OneToOneField(Broker, on_delete=models.DO_NOTHING)
    accounting_summary = JSONField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.broker


class BrokerVehicle(models.Model):
    broker = models.ForeignKey(Broker, related_name='broker_vehicle', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    account_details = models.ForeignKey(Bank, blank=True, null=True, on_delete=models.CASCADE)
    datetime = models.DateTimeField(blank=True, null=True)
    latest = models.BooleanField(editable=False, default=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="broker_vehicle_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="broker_vehicle_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Broker Vehicles"
        unique_together = ('broker', 'vehicle')

    def __str__(self):
        return str('' if not self.broker else self.broker.name) + ", " + str(self.vehicle)


class BrokerOwner(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="broker_owner_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="broker_owner_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('broker', 'owner')

    def __str__(self):
        return 'Broker: %s, Owner: %s' % (str(self.broker), str(self.owner))


class BrokerDriver(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="broker_driver_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="broker_driver_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('broker', 'driver')


ACCOUNT_RELATION_CHOICES = (
    ('self', 'self'),
    ('driver', 'driver'),
    ('owner', 'owner')
)


class BrokerAccount(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    account = models.ForeignKey(Bank, on_delete=models.CASCADE)
    relation = models.CharField(max_length=10, choices=ACCOUNT_RELATION_CHOICES, default='self')
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="broker_account_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="broker_account_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('broker', 'account')


class Document(models.Model):
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
        ('broker', 'broker'),
    )

    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="document_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="document_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    # user who uploaded the document
    user = models.ForeignKey(User, related_name='broker_document', on_delete=models.CASCADE)

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
