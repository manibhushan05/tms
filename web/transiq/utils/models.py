from __future__ import unicode_literals

import json

from django.contrib.auth.models import User
from django.core import serializers
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.utils import format_date
from fms.models import Document
from api.utils import to_str
from utils.managers import CityManager, AahoOfficeManager

HOLIDAY_STATUS = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
)

class State(models.Model):
    name = models.CharField(max_length=70)
    code = models.CharField(max_length=2, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="state_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="state_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def natural_key(self):
        return json.loads(serializers.serialize(format='json', queryset=State.objects.filter(id=self.id),
                                                use_natural_foreign_keys=True).strip("[]"))

    class Meta:
        verbose_name_plural = "States"
        ordering = ['-id']


class City(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    code = models.CharField(max_length=3, null=True, unique=True)
    pin = models.CharField(max_length=6, null=True, blank=True)
    state = models.ForeignKey(State, blank=True, null=True, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="city_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="city_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['-id']

    def natural_key(self):
        return json.loads(serializers.serialize(format='json', queryset=City.objects.filter(id=self.id),
                                                use_natural_foreign_keys=True).strip("[]"))

    @property
    def state_name(self):
        if isinstance(self.state, State):
            return self.state.name
        return ''

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state.name,
            'latitude': float(self.latitude) if self.latitude else 0,
            'longitude': float(self.longitude) if self.longitude else 0,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }

    def __str__(self):
        return " %s, %s" % (self.name, self.state)


class CityLocal(models.Model):
    city = models.OneToOneField(City, null=True, blank=True, related_name='city_local',
                                on_delete=models.CASCADE)
    hindi_name = models.CharField(max_length=200, null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='citylocal_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.hindi_name


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    code = models.CharField(max_length=3, null=True, blank=True, unique=True)
    name = models.CharField(max_length=70, db_index=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE,
                                   related_name="district_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="district_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (('state', 'name'), ('latitude', 'longitude'))

    def __str__(self):
        return self.name


class SubDistrict(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    code = models.CharField(max_length=4, null=True, blank=True)
    name = models.CharField(max_length=70, db_index=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="sub_district_created_by",
                                   on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="sub_district_changed_by")

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (('district', 'name'), ('latitude', 'longitude'))

    def __str__(self):
        return self.name


class PinCode(models.Model):
    sub_district = models.ForeignKey(SubDistrict, on_delete=models.CASCADE)
    pin_code = models.PositiveIntegerField(validators=[MaxValueValidator(999999), MinValueValidator(110003)],
                                           db_index=True, unique=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE,
                                   related_name="pin_code_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="pin_code_changed_by")

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (('sub_district', 'pin_code'), ('latitude', 'longitude'))

    def __str__(self):
        return self.pin_code


class Locality(models.Model):
    pin_code = models.ForeignKey(PinCode, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    post_office = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    created_by = models.ForeignKey(User, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE,
                                   related_name="locality_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="locality_changed_by")

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{}, {}'.format(self.name, self.post_office)


class Address(models.Model):
    line1 = models.CharField(max_length=500, blank=True, null=True)
    line2 = models.CharField(max_length=200, blank=True, null=True)
    line3 = models.CharField(max_length=200, blank=True, null=True)
    landmark = models.CharField(max_length=200, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=8, blank=True, null=True)
    latitude = models.CharField(max_length=30, blank=True, null=True)
    longitude = models.CharField(max_length=30, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="address_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="address_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def to_string(string):
        return '' if not string else string

    def full_address(self):
        city_name = '' if not self.city else ', '.join(
            [self.city.name, '' if not self.city.state else self.city.state.name])
        address = []
        if self.line1:
            address.append(to_str(self.line1))
        if self.line2:
            address.append(to_str(self.line2))
        if self.line3:
            address.append(to_str(self.line3))
        if city_name:
            address.append(city_name)
        if self.pin:
            address.append(to_str(self.pin))

        return ', '.join(address)

    def __str__(self):
        return self.full_address()

    def partial_address(self):
        address = []
        if self.line1:
            address.append(to_str(self.line1))
        if self.line2:
            address.append(to_str(self.line2))
        if self.line3:
            address.append(to_str(self.line3))
        if self.landmark:
            address.append(to_str(self.landmark))
        return ', '.join(address)

    def to_json(self):
        return {
            'id': self.id,
            'line1': self.line1,
            'line2': self.line2,
            'line3': self.line3,
            'landmark': self.line3,
            'pin': self.line3,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'city': None if not self.city else self.city.to_json(),
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }

    class Meta:
        verbose_name_plural = "Address"
        ordering = ['-id']


class IDDetails(models.Model):
    id_choices = (('PAN', 'PAN Card'),
                  ('DL', 'Driving Licence'),
                  ('EL', 'Election ID'),
                  ('AC', 'Aadhar Card'),
                  ('PT', 'Passport'),
                  ('RC', 'Ration Card'),
                  )
    id_type = models.CharField(max_length=20, choices=id_choices)
    id_number = models.CharField(max_length=30)
    id_issued_in = models.CharField(max_length=255, blank=True, null=True)
    validity = models.DateField(blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    id_image_url = models.URLField(blank=True, null=True)
    document = models.ForeignKey(Document, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="id_details_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="id_details_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "ID Card Details"

    def __str__(self):
        return self.id_number

    def to_json(self):
        return {
            'id': self.id,
            'id_type': self.id_type,
            'id_number': self.id_number,
            'id_issued_in': self.id_issued_in,
            'validity': format_date(self.validity),
            'issue_date': format_date(self.issue_date),
            'id_image_url': self.id_image_url,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }


class BankName(models.Model):
    name = models.CharField(max_length=200, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="bank_name_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="bank_name_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "ID: %s, Bank Name: %s" % (self.id, self.name)


class IfscDetail(models.Model):
    bank = models.ForeignKey(BankName, null=True, related_name='ifsc_details', on_delete=models.CASCADE)
    ifsc_code = models.CharField(max_length=20, db_index=True, unique=True)
    micr_code = models.CharField(max_length=35, blank=True, null=True)
    branch_name = models.CharField(max_length=400, null=True)
    address = models.CharField(max_length=400, null=True)
    contact_details = models.CharField(max_length=400, blank=True, null=True)
    centre = models.CharField(max_length=400, blank=True, null=True)
    district = models.CharField(max_length=70, blank=True, null=True)
    state = models.CharField(max_length=70, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="ifsc_detail_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="ifsc_detail_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Bank: %s, IFSC: %s" % (self.bank, self.ifsc_code)


class Bank(models.Model):
    account_choices = (
        ('SA', 'Saving Account'),
        ('CA', 'Current Account'),
        ('KCC', 'Kisan Credit Card'),
        ('RA', 'Recurring Account'),
    )
    transaction_type_choide = (
        ('neft', 'NEFT'),
        ('rtgs', 'RTGS'),
        ('both', 'Both'),
        ('hdfc_internal_account', 'HDFC Internal Account'),
    )
    status = (
        ('active', 'Active'),
        ('inactive', 'Inactive')
    )
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    bank = models.CharField(max_length=255, blank=True, null=True)
    account_holder_name = models.CharField(max_length=100, blank=True, null=True)
    beneficiary_code = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=30, blank=True, null=True, unique=True)
    transaction_type = models.CharField(max_length=35, blank=True, null=True, choices=transaction_type_choide)
    account_type = models.CharField(max_length=15, null=True, choices=account_choices, default='SA')
    ifsc = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=400, blank=True, null=True)
    city = models.CharField(max_length=70, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    is_verified = models.CharField(max_length=10, null=True, choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    status = models.CharField(max_length=20, blank=True, null=True, choices=status, default='active')
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="bank_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="bank_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Bank Account Details'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        self.beneficiary_code = None if self.beneficiary_code is None else self.beneficiary_code.upper()
        self.ifsc = None if self.ifsc is None else self.ifsc.upper()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "ID: %s Name: %s, Account: %s" % (self.id, self.account_holder_name, self.account_number)

    def to_json(self):
        return {
            'id': self.id,
            'bank': self.bank,
            'account_holder_name': self.account_holder_name,
            'account_number': self.account_number,
            'account_type': self.account_type,
            'account_type_verbose': dict(Bank.account_choices).get(self.account_type, ''),
            'ifsc': self.ifsc,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }


class TaxationID(models.Model):
    service_tax_number = models.CharField(max_length=40, blank=True, null=True, verbose_name="CST/VAT/TIN/SALES TAX")
    tan_number = models.CharField(max_length=40, blank=True, null=True)
    pan = models.CharField(max_length=30, blank=True, null=True)
    pan_doc = models.ForeignKey(Document, related_name='pan_bearer', null=True, blank=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="taxation_id_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="taxation_id_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Taxation ID Details"

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {
            'id': self.id,
            'service_tax_number': self.service_tax_number,
            'tan_number': self.tan_number,
            'pan': self.pan,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }


class VehicleBodyCategory(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="vehicle_body_category_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="vehicle_body_category_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class VehicleCategory(models.Model):
    vehicle_type = models.CharField(max_length=100, unique=True)
    capacity = models.CharField(max_length=30, blank=True, null=True)
    truck_body_type = models.CharField(max_length=50, blank=True, null=True)
    truck_body = models.ForeignKey(VehicleBodyCategory, null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="vehicle_category_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="vehicle_category_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Vehicle Category"
        ordering = ['-id']

    def name(self):
        data = []
        if self.vehicle_type:
            data.append(self.vehicle_type)
        if self.capacity:
            data.append(self.capacity)
        return ', '.join(data)

    @property
    def vehicle_category(self):
        data = []
        if self.vehicle_type:
            data.append(self.vehicle_type)
        if self.capacity:
            data.append(self.capacity)
        if self.truck_body:
            data.append(self.truck_body.name)
        return ', '.join(data)


    def get_name(self):
        data = []
        if self.vehicle_type:
            data.append(self.vehicle_type)
        if self.capacity:
            data.append(self.capacity)
        return ', '.join(data)

    def __str__(self):
        return self.name()

    def to_json(self):
        return {
            'id': self.id,
            'vehicle_type': self.vehicle_type,
            'capacity': self.capacity,
            'truck_body_type': self.truck_body_type,
            'description': self.description,
            'priority': self.priority,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }


class AahoOffice(models.Model):
    branch_name = models.CharField(max_length=200, null=True)
    branch = models.ForeignKey(City, on_delete=models.CASCADE)
    branch_head = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    pin = models.CharField(max_length=7, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    t1_name = models.CharField(max_length=35, null=True, verbose_name='Traffic Person 1 Name')
    t1_phone = models.CharField(max_length=10, null=True, help_text='enter 10 digit mobile number',
                                verbose_name='Traffic Person 1 Phone')
    t2_name = models.CharField(max_length=35, null=True, blank=True, verbose_name='Traffic Person 2 Name')
    t2_phone = models.CharField(max_length=10, null=True, help_text='enter 10 digit mobile number',
                                verbose_name='Traffic Person 2 Phone', blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="aaho_office_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="aaho_office_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.branch_name

    def natural_key(self):
        return json.loads(serializers.serialize(format='json', queryset=AahoOffice.objects.filter(id=self.id),
                                                use_natural_foreign_keys=True).strip("[]"))

    def to_json(self):
        return {
            'id': self.id,
            'address': self.address,
            'city': None if not self.branch else self.branch.name,
            'state': None if not self.branch else self.branch.state.name,
            'pin': self.pin,
            'phone': self.phone,
            't1_name': self.t1_name,
            't1_phone': self.t1_phone,
            't2_name': self.t2_name,
            't2_phone': self.t2_phone,
            'branch_head': self.branch_head,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }


class DatabaseUpdateLog(models.Model):
    db_table = models.CharField(max_length=100)
    updated_by = models.ForeignKey(User, related_name='database_update', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s, %s' % (self.db_table, self.updated_by)


class FieldChangeLog(models.Model):
    database_log = models.ForeignKey(DatabaseUpdateLog, related_name='field_changed_log', on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100)
    old_value = models.CharField(max_length=300)
    new_value = models.CharField(max_length=300)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s, %s, %s, %s, %s' % (
            self.database_log, self.field_name, self.old_value, self.new_value, self.created_on)


class BankHolidays(models.Model):
    name = models.CharField(max_length=300)
    states = models.ManyToManyField(State)
    date = models.DateField()
    remarks = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s, %s' % (self.name, self.date)


class AahoHolidays(models.Model):
    name = models.CharField(max_length=300)
    type = models.TextField(null=True, blank=True)
    offices = models.ManyToManyField(AahoOffice, related_name="holidays_offices")
    date = models.DateField()
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=HOLIDAY_STATUS, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='aahoholidays_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s, %s' % (self.name, self.date)
