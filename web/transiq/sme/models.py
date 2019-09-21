from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from datetime import date
from api.utils import get_or_none
from authentication.models import Profile
from employee.models import Employee
from utils.models import Address, City, IDDetails, Bank, TaxationID, VehicleCategory, AahoOffice


class SmeTaskEmail(models.Model):
    name = models.CharField(max_length=200, null=True, unique=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="sme_task_email_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="sme_task_email_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Sme(models.Model):
    IS_GST_APPLICABLE_CHOICE = (
        ('yes', 'Yes'),
        ('no', 'No'),
        ('unknown', 'Unknown')
    )
    LR_FORMAT_CHOICE = (
        ('S', 'Serial'),
        ('D', 'Default')
    )
    name = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    aaho_office = models.ForeignKey(AahoOffice, null=True, on_delete=models.CASCADE)
    email_tasks = models.ManyToManyField(SmeTaskEmail, blank=True)
    company_code = models.CharField(max_length=3, null=True, unique=True)
    latest_lr_serial_number = models.PositiveIntegerField(default=0)
    lr_format_type = models.CharField(max_length=20, choices=LR_FORMAT_CHOICE, null=True, default='D')
    address = models.OneToOneField(Address, blank=True, null=True, on_delete=models.CASCADE)
    customer_address = models.CharField(max_length=300, blank=True, null=True)
    credit_period = models.CharField(max_length=300, blank=True, null=True)
    aaho_poc = models.ForeignKey(Employee, blank=True, null=True, on_delete=models.CASCADE)
    city = models.ForeignKey(City, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6, blank=True, null=True)
    gstin = models.CharField(max_length=15, null=True)
    is_gst_applicable = models.CharField(max_length=20, choices=IS_GST_APPLICABLE_CHOICE, default='unknown')
    id_proof = models.OneToOneField(IDDetails, blank=True, null=True, on_delete=models.CASCADE)
    account_details = models.OneToOneField(Bank, blank=True, null=True, on_delete=models.CASCADE)
    taxation_details = models.OneToOneField(TaxationID, blank=True, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('active', 'active'), ('inactive', 'inactive')], default='active')
    material = models.CharField(max_length=150, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="sme_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="sme_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "SME Basic Info"
        ordering = ['-id']

    @staticmethod
    def get_company_name(company):
        if not company:
            return ''
        sme = get_or_none(Sme, id=company)
        if not sme:
            return ''
        return sme.get_name()

    def get_address(self):
        return '' if not self.address else self.address.full_address()

    def get_name(self):
        if not hasattr(self, 'sme_profile'):
            self.sme_profile = get_or_none(Profile, user_id=self.name_id)
        if not self.sme_profile:
            return ''
        return self.sme_profile.name or ''

    @property
    def sme_email(self):
        if isinstance(self.name, User) and isinstance(self.name.profile, Profile) and self.name.profile.email:
            return self.name.profile.email
        return None

    @property
    def sme_alt_email(self):
        if isinstance(self.name, User) and isinstance(self.name.profile, Profile) and self.name.profile.alternate_email:
            return self.name.profile.alternate_email
        return None

    @property
    def aaho_poc_email(self):
        if isinstance(self.aaho_poc, Employee) and self.aaho_poc.status == 'active':
            return self.aaho_poc.emp_email
        return None

    @property
    def aaho_poc_name(self):
        if isinstance(self.aaho_poc, Employee):
            return self.aaho_poc.emp_name()
        return None

    @property
    def aaho_poc_phone(self):
        if isinstance(self.aaho_poc, Employee):
            return self.aaho_poc.emp_phone()
        return None

    @property
    def aaho_office_branch(self):
        if isinstance(self.aaho_office, AahoOffice):
            return self.aaho_office.branch_name
        return None

    def __str__(self):
        return self.get_name()


class SmeSummary(models.Model):
    sme = models.OneToOneField(Sme, on_delete=models.DO_NOTHING)
    billed_accounting_summary = JSONField(null=True)
    placed_order_accounting_summary = JSONField(null=True)
    accounting_summary = JSONField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.sme.get_name() if isinstance(self.sme, Sme) else '-'


class RateType(models.Model):
    name = models.CharField(max_length=100, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="rate_type_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="rate_type_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class CustomerContract(models.Model):
    BILLING_FREQUENCY_CHOICES = (
        ('d', 'Daily'),
        ('w', 'Weekly'),
        ('m', 'Monthly'),
        ('f', 'Fort Nightly'),
        ('o', 'Others'),
    )
    customer = models.ForeignKey(Sme, null=True, on_delete=models.CASCADE)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    billing_frequency = models.CharField(max_length=50, choices=BILLING_FREQUENCY_CHOICES, null=True)

    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="customer_contract_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="customer_contract_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ['-id']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

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
        return ' '.join([self.customer.get_name() if self.customer else '',
                         self.start_date.strftime('%d-%b-%Y') if self.start_date else '',
                         self.end_date.strftime('%d-%b-%Y') if self.end_date else ''])

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError(_('Contract end date must greater than start date'))

        if CustomerContract.objects.filter(Q(customer=self.customer) & (
                Q(start_date__lte=self.start_date) & Q(end_date__gte=self.end_date))).exclude(id=self.id).exists():
            raise ValidationError(_(
                'Contract is already exists for {}'.format(self.customer.get_name())))


class ContractRoute(models.Model):
    contract = models.ForeignKey(CustomerContract, null=True, on_delete=models.CASCADE)
    source = models.ForeignKey(City, null=True, related_name='contract_route_source', on_delete=models.CASCADE)
    destination = models.ForeignKey(City, null=True, related_name='contract_route_destination',
                                    on_delete=models.CASCADE)
    rate_type = models.ForeignKey(RateType, null=True, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="contract_route_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="contract_route_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ['-id']
        unique_together = ('contract', 'source', 'destination')

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
        return ' '.join([self.contract.__str__(), self.source.name if self.source else '',
                         self.destination.name if self.destination else '', str(self.rate)])


class ContactDetails(models.Model):
    sme = models.ForeignKey(Sme, related_name="sme_contact_details", on_delete=models.CASCADE)
    type = models.CharField(max_length=35, blank=True, null=True,
                            choices=[('primary', 'primary'), ('secondary', 'secondary')], default='secondary')
    name = models.CharField(max_length=70, blank=True, null=True)
    phone = models.CharField(max_length=17, blank=True, null=True)
    alternate_phone = models.CharField(max_length=17, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    alternate_email = models.EmailField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('active', 'active'), ('inactive', 'inactive')], default='active')
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="contact_details_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="contact_details_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "SME Contact Details"

    def __str__(self):
        return "%s, %s, %s" % (self.sme, self.phone, self.name)


class Location(models.Model):
    location_choice = (
        ('loading', 'loading'),
        ('unloading', 'unloading'),
    )
    type = models.CharField(max_length=30, choices=location_choice, blank=True, null=True)
    sme = models.ForeignKey(Sme, blank=True, null=True, related_name="sme_loading_unloading", on_delete=models.CASCADE)
    contact = models.OneToOneField(ContactDetails, blank=True, null=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, null=True)
    city = models.ForeignKey(City, null=True, on_delete=models.CASCADE)
    material = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=30, blank=True, null=True)
    longitude = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('active', 'active'), ('inactive', 'inactive')], default='active')
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="location_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="location_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "SME Loading & Unloading Points"

    def __str__(self):
        return "%s, %s, %s" % (self.type, self.address, self.contact)


class ConsignorConsignee(models.Model):
    choices = (
        ('consignor', 'consignor'),
        ('consignee', 'consignee'),
    )
    sme = models.ForeignKey(Sme, blank=True, null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=30, choices=choices)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True, unique=False)
    tax_id = models.CharField(max_length=40, blank=True, null=True, unique=False)
    status = models.CharField(max_length=10, choices=[('active', 'active'), ('inactive', 'inactive')], default='active')
    created_by = models.ForeignKey(User, null=True, related_name='sme_consignor_consignee_user',
                                   on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="sme_consignor_consignee_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "SME Consignor & Consignee Details"

    def __str__(self):
        return "%s, %s" % (str(self.sme), str(self.type))


class PreferredVehicle(models.Model):
    sme = models.ForeignKey(Sme, on_delete=models.CASCADE)
    category = models.ForeignKey(VehicleCategory, related_name='sme_preffered_vehicle', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="sme_preffered_vehicle_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="sme_preferred_vehicle_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "SME Preferred Vehicles"

    def __str__(self):
        return str(self.sme) + " " + str(self.category)


class SmeEnquiry(models.Model):
    sme = models.ForeignKey(Sme, blank=True, null=True, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('active', 'active'), ('inactive', 'inactive')], default='active')
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="sme_enquiry_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="sme_enquiry_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "SME Enquiry"

    def __str__(self):
        return str(self.subject)
