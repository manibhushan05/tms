from __future__ import absolute_import, print_function, division, unicode_literals

from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.db import models
from django.db.models import Q
from simple_history.models import HistoricalRecords

from authentication.models import Profile
from employee.models import Employee
from owner.vehicle_util import compare_format, display_format
from utils.models import City, AahoOffice, State, VehicleCategory, Bank


class Service(models.Model):
    name = models.CharField(max_length=50, null=True, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, related_name="service_changed_by",
                                   limit_choices_to={'is_staff': True}, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, related_name="service_created_by", on_delete=models.CASCADE)

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

    # def delete(self, using=None, keep_parents=False):
    #     self.deleted = True
    #     self.deleted_on = datetime.now()
    #     super(Service, self).save()

    def __str__(self):
        return self.name


class Supplier(models.Model):
    # rem
    user = models.OneToOneField(User, related_name='truck_supplier', on_delete=models.CASCADE)
    services = models.ManyToManyField(Service, blank=True, limit_choices_to={"deleted": False})
    code = models.CharField(max_length=4, null=True, unique=True, validators=[
        MinLengthValidator(limit_value=4, message='Supplier code must be exactly 4 Letter'),
        MaxLengthValidator(limit_value=4, message='Supplier code must be exactly 4 Letter')])
    address = models.CharField(max_length=300, blank=True, null=True)

    city = models.ForeignKey(City, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6, null=True, blank=True)
    pan = models.CharField(max_length=10, null=True, blank=True)
    route = models.CharField(max_length=255, blank=True, null=True)
    aaho_office = models.ForeignKey(AahoOffice, null=True, related_name='supplier_aaho_office',
                                    on_delete=models.CASCADE)
    aaho_poc = models.ForeignKey(Employee, null=True, blank=True, limit_choices_to={"status": "active"},
                                 on_delete=models.CASCADE)
    serving_states = models.ManyToManyField(State, blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='supplier_created_by',
                                   limit_choices_to={'is_staff': True},
                                   on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, related_name='supplier_changed_by', on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
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
    def _service_list(self):
        return '\n'.join(self.services.values_list('name', flat=True))

    @property
    def name(self):
        try:
            name = self.user.profile.name
        except Profile.DoesNotExist:
            name = '-'
        return name

    @property
    def email(self):
        try:
            email = self.user.profile.email
        except Profile.DoesNotExist:
            email = '-'
        return email

    @property
    def phone(self):
        try:
            phone = self.user.profile.phone
        except Profile.DoesNotExist:
            phone = '-'
        return phone

    @property
    def alt_phone(self):
        try:
            phone = self.user.profile.alternate_phone
        except Profile.DoesNotExist:
            phone = '-'
        return phone

    def clean(self):
        if not isinstance(self.user, User):
            raise ValidationError('User does not exists')
        if not isinstance(self.user.profile, Profile):
            raise ValidationError('Profile does not exists')

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super(Supplier, self).save()

    def __str__(self):
        return self.name


class SupplierAccountingSummary(models.Model):
    supplier = models.OneToOneField(Supplier, on_delete=models.DO_NOTHING)
    accounting_summary = JSONField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.supplier.name if self.supplier else None


class ContactPerson(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)  # remove this and check user is active or not
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, related_name='supplier_contact_person',
                                   limit_choices_to={'is_staff': True},
                                   on_delete=models.CASCADE
                                   )
    created_by = models.ForeignKey(User, null=True, related_name='supplier_contact_person_created_by',
                                   on_delete=models.CASCADE
                                   )

    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def name(self):
        try:
            name = self.user.profile.name
        except Profile.DoesNotExist:
            name = '-'
        return name

    @property
    def email(self):
        try:
            email = self.user.profile.email
        except Profile.DoesNotExist:
            email = '-'
        return email

    @property
    def phone(self):
        try:
            phone = self.user.profile.phone
        except Profile.DoesNotExist:
            phone = '-'
        return phone

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

    # def delete(self, using=None, keep_parents=False):
    #     self.deleted = True
    #     self.deleted_on = datetime.now()
    #     super(ContactPerson, self).save()

    def __str__(self):
        return self.name


class Driver(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=300, blank=True, null=True)
    account_details = models.OneToOneField(Bank, blank=True, related_name='supplier_driver_account', null=True,
                                           on_delete=models.CASCADE)
    pan = models.CharField(max_length=11, null=True, blank=True)
    route = models.CharField(max_length=300, blank=True, null=True)
    driving_licence_number = models.CharField(max_length=50, null=True, blank=True)
    driving_licence_location = models.CharField(max_length=50, null=True, blank=True)
    driving_licence_validity = models.DateField(null=True, blank=True)
    smartphone_available = models.BooleanField(default=False)  # remove
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, related_name='supplier_drivers',
                                   limit_choices_to={'is_staff': True},
                                   on_delete=models.CASCADE
                                   )
    created_by = models.ForeignKey(User, null=True, related_name='supplier_drivers_created_by',
                                   on_delete=models.CASCADE
                                   )

    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
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
    def name(self):
        try:
            name = self.user.profile.name
        except (Profile.DoesNotExist, AttributeError):
            name = '-'
        return name

    @property
    def phone(self):
        try:
            phone = self.user.profile.phone
        except (Profile.DoesNotExist, AttributeError):
            phone = '-'
        return phone

    # def delete(self, using=None, keep_parents=False):
    #     self.deleted = True
    #     self.deleted_on = datetime.now()
    #     super(Driver, self).save()

    def __str__(self):
        return str(self.name)


class DriverPhone(models.Model):
    driver = models.ForeignKey(Driver, null=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15,
                             validators=[RegexValidator(regex=r'^\d{10}$', message='Please enter valid phone number')])
    active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   on_delete=models.CASCADE, related_name="driver_phone_changed_by"
                                   )
    created_by = models.ForeignKey(User, null=True, related_name="driver_phone_created_by",
                                   on_delete=models.CASCADE
                                   )
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        unique_together = ('phone', 'active')
        ordering = ['-id']

    # def delete(self, using=None, keep_parents=False):
    #     self.deleted = True
    #     self.deleted_on = datetime.now()
    #     super(DriverPhone, self).save()

    def __str__(self):
        return '{}, {}'.format(self.driver.name if isinstance(self.driver, Driver) else '', self.phone)


class Vehicle(models.Model):
    body_type_choice = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('semi', 'Semi'),
        ('half', 'Half'),
        ('containerized', 'Containerized'),
    )
    vehicle_number = models.CharField(max_length=11, unique=True)
    vehicle_type = models.ForeignKey(VehicleCategory, blank=True, null=True, on_delete=models.CASCADE)
    vehicle_capacity = models.PositiveIntegerField(blank=True, null=True, verbose_name="Exact Vehicle Capacity in Kg")
    chassis_number = models.CharField(
        max_length=17, blank=True, null=True,
        help_text='Enter VIN and last 6 digits are chassis number'
    )
    body_type = models.CharField(max_length=50, choices=body_type_choice, null=True, blank=True)
    engine_number = models.CharField(max_length=15, blank=True, null=True)
    registration_year = models.DateField(blank=True, null=True)
    registration_validity = models.DateField(blank=True, null=True)
    gps_enabled = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, related_name='vehicles_changed_by',
                                   limit_choices_to={'is_staff': True},
                                   on_delete=models.CASCADE
                                   )
    created_by = models.ForeignKey(User, null=True, related_name='vehicles_created_by',

                                   on_delete=models.CASCADE
                                   )

    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
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

    @property
    def owner(self):
        sv = self.suppliervehicle_set.filter(ownership__iexact='o', active=True).last()
        if sv:
            supplier = self.suppliervehicle_set.filter(ownership__iexact='o', active=True).last().supplier
        else:
            supplier = None
        return supplier

    @property
    def owner_name(self):
        if self.owner:
            return self.owner.name
        else:
            return '-'

    @property
    def owner_phone(self):
        if self.owner:
            return self.owner.phone
        else:
            return '-'

    @property
    def driver(self):
        if self.drivervehicle_set.filter(active=True).exists():
            return self.drivervehicle_set.filter(active=True).last().driver
        return None

    @property
    def driver_name(self):
        if self.driver:
            return self.driver.name
        else:
            return '-'

    @property
    def driver_phone(self):
        if self.driver:
            return self.driver.phone
        else:
            return '-'

    @property
    def vehicle_number_display(self):
        return display_format(self.vehicle_number)

    def save(self, *args, **kwargs):
        if self.vehicle_number:
            self.vehicle_number = compare_format(self.vehicle_number)
        return super(Vehicle, self).save(*args, **kwargs)

    @staticmethod
    def find(number):
        try:
            return Vehicle.objects.get(vehicle_number=compare_format(number))
        except Vehicle.DoesNotExist:
            return None

    def number(self):
        return display_format(self.vehicle_number)

    # def delete(self, using=None, keep_parents=False):
    #     self.deleted = True
    #     self.deleted_on = datetime.now()
    #     super(Vehicle, self).save()

    def __str__(self):
        return self.number()


class VehicleAccountingSummary(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.DO_NOTHING)
    accounting_summary = JSONField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.vehicle.number()


class DriverVehicle(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   on_delete=models.CASCADE, related_name="driver_vehicle_changed_by")
    created_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="driver_vehicle_created_by",
                                   on_delete=models.CASCADE)

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

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super(DriverVehicle, self).save()


class VehicleStatus(models.Model):
    VEHICLE_STATUS_CHOICES = (
        ('UD', 'Unloaded'),
        ('LG', 'Loading'),
        ('LD', 'Loaded'),
        ('UG', 'Unloading')
    )
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=VEHICLE_STATUS_CHOICES, default='UD')
    active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   on_delete=models.CASCADE, related_name="vehicle_status_changed_by")
    created_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="vehicle_status_created_by",
                                   on_delete=models.CASCADE)

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

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super(VehicleStatus, self).save()

    def clean(self):
        if self.active and VehicleStatus.objects.filter(vehicle=self.vehicle, active=True).exclude(id=self.id).exists():
            raise ValidationError(
                'Status for {} is already active'.format(self.vehicle.number()))

    def __str__(self):
        return '{}, {}'.format(self.vehicle, self.get_status_display())


class VehicleInsurer(models.Model):
    name = models.CharField(max_length=100, null=True, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE,
                                   related_name="vehicle_insurer_changed_by"
                                   )
    created_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE,
                                   related_name="vehicle_insurer_created_by"
                                   )

    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Insurance Companies'

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

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super(VehicleInsurer, self).save()

    def __str__(self):
        return self.name


class VehicleInsurance(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    insurance_number = models.CharField(max_length=25, null=True, blank=True)
    issued_on = models.DateField(null=True, blank=True)
    expired_by = models.DateField(null=True)
    insurer = models.ForeignKey(VehicleInsurer, null=True, blank=True, on_delete=models.CASCADE)
    image_url = models.URLField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="vehicle_insurance_changed_by",
                                   on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="vehicle_insurance_created_by",
                                   on_delete=models.CASCADE)

    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def insurer_name(self):
        if self.insurer:
            return self.insurer.name
        return

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

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super(VehicleInsurance, self).save()


class VehiclePUC(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    serial_number = models.CharField(
        max_length=30, blank=True, null=True,
        help_text='The serial number of the issued certificate'
    )
    issued_date = models.DateField(null=True, help_text='The date on which the test was conducted')
    expiry_date = models.DateField(null=True, help_text='The expiry date of the PUC certificate')
    readings = models.CharField(
        max_length=250, null=True, blank=True,
        help_text='The readings and observations from the test'
    )
    image_url = models.URLField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="vehicle_puc_changed_by",
                                   on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="vehicle_puc_created_by",
                                   on_delete=models.CASCADE)

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

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super(VehiclePUC, self).save()


class VehicleFitness(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=30, null=True)
    issued_date = models.DateField(null=True)
    expiry_date = models.DateField(null=True)
    image_url = models.URLField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="vehicle_fitness_changed_by",
                                   on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, related_name="vehicle_fitness_created_by", on_delete=models.CASCADE)
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

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super(VehicleFitness, self).save()


class VehiclePermit(models.Model):
    vehicle = models.ForeignKey(Vehicle, null=True, on_delete=models.CASCADE)
    permit_number = models.CharField(max_length=30, blank=True, null=True)
    permit_type = models.CharField(max_length=100, blank=True, null=True)
    issued_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True)
    image_url = models.URLField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="vehicle_permit_changed_by",
                                   on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, related_name="vehicle_permit_created_by",
                                   on_delete=models.CASCADE)
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

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super(VehiclePermit, self).save()


class SupplierVehicle(models.Model):
    OWNERSHIP_CHOICES = (
        ('B', 'Broker'),
        ('O', 'Owner')
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    ownership = models.CharField(max_length=1, choices=OWNERSHIP_CHOICES, null=True)
    active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="supplier_vehicle_changed_by",
                                   on_delete=models.CASCADE)

    created_by = models.ForeignKey(User, null=True, related_name="supplier_vehicle_created_by",
                                   on_delete=models.CASCADE)

    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        unique_together = ('supplier', 'vehicle', 'ownership')

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

    # def delete(self, using=None, keep_parents=False):
    #     self.deleted = True
    #     self.deleted_on = datetime.now()
    #     super(SupplierVehicle, self).save()

    def clean(self):
        if SupplierVehicle.objects.filter(vehicle=self.vehicle, ownership='O', active=True).exclude(
                id=self.id).exists():
            raise ValidationError('Owner for vehicle number {} is already exists'.format(self.vehicle.number()))
