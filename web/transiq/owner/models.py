from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from simple_history.models import HistoricalRecords

from api.utils import format_date
from authentication.models import Profile
from driver.models import DriverAppUser, Driver, VEHICLE_STATUS_CHOICES
from fms.models import Document
from owner.vehicle_util import display_format, compare_format
from utils.models import Address, Bank, TaxationID, City, VehicleCategory


class Route(models.Model):
    source = models.ForeignKey(City, related_name="source_route_city", on_delete=models.CASCADE)
    destination = models.ForeignKey(City, related_name="destination_route_city", on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="route_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="route_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)


class Owner(models.Model):
    name = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    address = models.OneToOneField(Address, blank=True, null=True, on_delete=models.CASCADE)
    owner_address = models.CharField(max_length=300, blank=True, null=True)
    city = models.ForeignKey(City, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6, blank=True, null=True)
    route = models.ManyToManyField(Route, blank=True)
    route_temp = models.CharField(max_length=300, null=True, blank=True)
    pan = models.CharField(max_length=11, blank=True, null=True)
    vehicles_detail = models.CharField(max_length=500, blank=True, null=True)
    account_details = models.OneToOneField(Bank, blank=True, null=True, on_delete=models.CASCADE)
    taxation_details = models.OneToOneField(TaxationID, blank=True, null=True, on_delete=models.CASCADE)
    declaration = models.CharField(max_length=255, null=True, blank=True)
    declaration_validity = models.DateField(blank=True, null=True)
    declaration_doc = models.ForeignKey(Document, related_name='declaration_owner', null=True, blank=True,
                                        on_delete=models.CASCADE)
    # active = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="owner_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="owner_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Owner Basic Info"
        ordering = ['-id']

    def __str__(self):
        return '{}- {}'.format(self.get_name(), self.get_phone())

    def name_phone(self):
        name = None
        phone = None
        if self.name_id:
            try:
                profile = Profile.objects.get(user_id=self.name_id)
                name = profile.name
                phone = profile.phone
            except Profile.DoesNotExist:
                pass
        return name, phone

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
                phone = profile.phone
            except Profile.DoesNotExist:
                pass
        return phone

    def to_json(self):
        name, phone = self.name_phone()
        return {
            'id': self.id,
            'user_id': None if not self.name else self.name.id,
            'username': None if not self.name else self.name.username,
            'user_fullname': None if not self.name else self.name.get_full_name(),
            'name': name or ('' if not self.name else self.name.username),
            'phone': phone,
            'address': None if not self.address else self.address.to_json(),
            'vehicles_detail': self.vehicles_detail,
            'account_details': None if not self.account_details else self.account_details.to_json(),
            'taxation_details': None if not self.taxation_details else self.taxation_details.to_json(),
            'declaration': self.declaration,
            'declaration_doc': None if not self.declaration_doc else self.declaration_doc.to_json(),
            'declaration_validity': format_date(self.declaration_validity),
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }


class Vehicle(models.Model):
    vehicle_status_choice = (
        ('free', 'FREE'),
        ('in_transit', 'In Transit'),
        ('to_pickup', 'TO be Pick Up'),
        ('delivery', 'To be Delivered')
    )
    body_type_choice = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('semi', 'Semi'),
        ('half', 'Half'),
        ('containerized', 'Containerized'),
    )

    owner = models.ForeignKey(Owner, blank=True, null=True, related_name='vehicle_owner', on_delete=models.CASCADE)
    driver = models.OneToOneField(Driver, blank=True, null=True, related_name='vehicle_driver',
                                  on_delete=models.CASCADE)
    driver_app_user = models.ForeignKey(DriverAppUser, null=True, blank=True, on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=18, unique=True)
    route = models.ManyToManyField(Route, blank=True)
    rc_number = models.CharField(max_length=20, blank=True, null=True)
    permit = models.CharField(max_length=25, blank=True, null=True)
    permit_validity = models.DateField(blank=True, null=True)
    permit_type = models.CharField(max_length=70, blank=True, null=True)
    vehicle_type = models.ForeignKey(VehicleCategory, blank=True, null=True, related_name="main_vehicle",
                                     on_delete=models.CASCADE)
    vehicle_capacity = models.IntegerField(blank=True, null=True, verbose_name="Exact Vehicle Capacity in Kg")
    body_type = models.CharField(max_length=50, choices=body_type_choice, null=True, blank=True)
    vehicle_model = models.CharField(max_length=30, blank=True, null=True)
    chassis_number = models.CharField(max_length=255, blank=True, null=True)
    engine_number = models.CharField(max_length=255, blank=True, null=True)
    insurer = models.CharField(max_length=100, blank=True, null=True)
    insurance_number = models.CharField(max_length=30, blank=True, null=True)
    insurance_validity = models.DateField(blank=True, null=True)
    registration_year = models.DateField(blank=True, null=True)
    registration_validity = models.DateField(blank=True, null=True)
    fitness_certificate_number = models.CharField(max_length=255, blank=True, null=True)
    fitness_certificate_issued_on = models.DateField(blank=True, null=True)
    fitness_certificate_validity_date = models.DateField(blank=True, null=True)
    puc_certificate_number = models.CharField(max_length=255, blank=True, null=True)
    puc_certificate_issued_on = models.DateField(blank=True, null=True)
    puc_certificate_validity_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default='unloaded')
    # active = models.BooleanField(default=False)
    gps_enabled = models.BooleanField(default=False)

    registration_certificate = models.ForeignKey(Document, related_name='reg_vehicle', null=True, blank=True,
                                                 on_delete=models.CASCADE)
    insurance_certificate = models.ForeignKey(Document, related_name='ins_vehicle', null=True, blank=True,
                                              on_delete=models.CASCADE)
    permit_certificate = models.ForeignKey(Document, related_name='perm_vehicle', null=True, blank=True,
                                           on_delete=models.CASCADE)
    puc_certificate = models.ForeignKey(Document, related_name='puc_vehicle', null=True, blank=True,
                                        on_delete=models.CASCADE)
    fitness_certificate = models.ForeignKey(Document, related_name='fit_vehicle', null=True, blank=True,
                                            on_delete=models.CASCADE)

    # redundant data from manual booking
    supplier_name = models.CharField(max_length=70, blank=True, null=True)
    supplier_phone = models.CharField(max_length=30, blank=True, null=True)
    owner_name = models.CharField(max_length=70, blank=True, null=True)
    owner_phone = models.CharField(max_length=30, blank=True, null=True)

    bank_account = models.ForeignKey(Bank, null=True, blank=True, on_delete=models.CASCADE)

    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="owner_vehicle_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="owner_vehicle_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "Vehicle Details"
        ordering = ['-id']

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

    @property
    def vehicle_category(self):
        return self.vehicle_type.vehicle_category if self.vehicle_type else None

    def save(self, *args, **kwargs):
        if self.vehicle_number:
            self.vehicle_number = compare_format(self.vehicle_number)
        return super().save(*args, **kwargs)

    @staticmethod
    def find(number):
        try:
            return Vehicle.objects.get(vehicle_number=compare_format(number))
        except Vehicle.DoesNotExist:
            return None

    def number(self):
        return display_format(self.vehicle_number)

    def __str__(self):
        return self.number()

    def to_json(self):
        data = {}
        ref_fields = [
            'owner', 'driver', 'driver_app_user', 'registration_certificate',
            'insurance_certificate', 'permit_certificate', 'puc_certificate', 'fitness_certificate'
        ]
        date_fields = [
            'permit_validity', 'insurance_validity', 'registration_validity',
            'fitness_certificate_issued_on', 'fitness_certificate_validity_date', 'updated_on', 'created_on',
            'puc_certificate_issued_on', 'puc_certificate_validity_date'
        ]
        normal_fields = [
            'id', 'puc_certificate_number', 'vehicle_number', 'rc_number', 'permit', 'permit_type',
            'vehicle_model', 'chassis_number', 'engine_number', 'insurer', 'insurance_number',
            'fitness_certificate_number', 'status', 'gps_enabled', 'vehicle_capacity'
        ]

        for field in normal_fields:
            value = getattr(self, field)
            data[field] = value

        for field in date_fields:
            value = getattr(self, field)
            data[field] = format_date(value)

        for field in ref_fields:
            value = getattr(self, field)
            data[field] = None if not value else value.to_json()

        data['registration_year'] = None if not self.registration_year else str(self.registration_year.year)
        data['vehicle_type'] = self.vehicle_type_id

        if self.vehicle_type:
            data['vehicle_type_data'] = self.vehicle_type.to_json()

        data['rc_doc'] = {
            'url': (data.get('registration_certificate', None) or {}).get('url', None),
            'thumb_url': (data.get('registration_certificate', None) or {}).get('thumb_url', None),
            'doc_id': data.get('rc_number', None),
            'validity': data.get('registration_validity', None),
            'manufacture_year': data.get('registration_year', None)
        }

        data['insurance_doc'] = {
            'url': (data.get('insurance_certificate', None) or {}).get('url', None),
            'thumb_url': (data.get('registration_certificate', None) or {}).get('thumb_url', None),
            'doc_id': data.get('insurance_number', None),
            'validity': data.get('insurance_validity', None),
            'insurer_name': data.get('insurer', None)
        }

        data['permit_doc'] = {
            'url': (data.get('permit_certificate', None) or {}).get('url', None),
            'thumb_url': (data.get('registration_certificate', None) or {}).get('thumb_url', None),
            'doc_id': data.get('permit', None),
            'validity': data.get('permit_validity', None),
            'permit_type': data.get('permit_type', None)
        }

        data['fitness_doc'] = {
            'url': (data.get('fitness_certificate', None) or {}).get('url', None),
            'thumb_url': (data.get('registration_certificate', None) or {}).get('thumb_url', None),
            'doc_id': data.get('fitness_certificate_number', None),
            'validity': data.get('fitness_certificate_validity_date', None)
        }

        data['puc_doc'] = {
            'url': (data.get('puc_certificate', None) or {}).get('url', None),
            'thumb_url': (data.get('registration_certificate', None) or {}).get('thumb_url', None),
            'doc_id': data.get('puc_certificate_number', None),
            'validity': data.get('puc_certificate_validity_date', None)
        }

        owner = self.owner
        if owner:
            tax = owner.taxation_details
            if tax:
                data['owner_pan_doc'] = {
                    'url': None if not tax.pan_doc else tax.pan_doc.document,
                    'thumb_url': None if not tax.pan_doc else tax.pan_doc.document_thumb,
                    'doc_id': tax.pan,
                    'validity': None
                }

            data['owner_dec_doc'] = {
                'url': None if not owner.declaration_doc else owner.declaration_doc.document,
                'thumb_url': None if not owner.declaration_doc else owner.declaration_doc.document_thumb,
                'doc_id': None,
                'validity': format_date(owner.declaration_validity)
            }

        driver = self.driver
        if driver:
            data['driver_dl_doc'] = {
                'url': None if not driver.driving_licence else driver.driving_licence.document,
                'thumb_url': None if not driver.driving_licence else driver.driving_licence.document_thumb,
                'doc_id': driver.driving_licence_number,
                'validity': format_date(driver.driving_licence_validity),
                'issue_location': driver.driving_licence_location
            }

        return data


class VehicleSummary(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.DO_NOTHING)
    accounting_summary = JSONField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.vehicle.number()


class FuelCard(models.Model):
    customer_id = models.CharField(max_length=30, default='1001507486')
    card_number = models.CharField(max_length=40, null=True, unique=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True)

    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="fuel_card_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="fuel_card_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "ID: %s, Card No.: %s, Issue Date: %s" % (self.id, self.card_number, self.issue_date)


class FuelCardTransaction(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    fuel_card = models.ForeignKey(FuelCard, on_delete=models.CASCADE)
    paid_to = models.CharField(max_length=70, blank=True, null=True)
    amount = models.IntegerField(default=0)
    payment_date = models.DateTimeField()
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="fuel_card_transaction_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="fuel_card_transaction_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Vehicle %s, Fuel Card %s Amount %s, Date %s" % (
            self.vehicle, self.fuel_card, self.amount, self.payment_date)
