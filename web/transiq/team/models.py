import json
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords

from api.models import S3Upload
from api.utils import get_or_none, to_str, to_int, to_round
from broker.models import Broker
from driver.models import Driver
from employee.models import Employee
from owner.models import FuelCard, Owner, Vehicle
from sme.models import Sme
from supplier.models import Supplier
from team.helper.helper import format_datetime, format_date, to_float
from utils.models import AahoOffice, City, Bank, VehicleCategory


class InvoiceSummary(models.Model):
    ref_number = models.CharField(max_length=20, unique=True, null=True)
    datetime = models.DateTimeField(null=True)
    s3_upload = models.ForeignKey(S3Upload, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, related_name='invoice_summary_created_by', on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, null=True, related_name='invoice_summary_changed_by', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.ref_number


class BookingStatusColor(models.Model):
    keyword = models.CharField(max_length=10)
    color_code = models.CharField(max_length=8)

    def __str__(self):
        return '{}-{}'.format(self.keyword, self.color_code)


class ManualBooking(models.Model):
    billing_types = (
        ('T.B.B.', 'T.B.B.'),
        ('To Pay', 'To Pay'),
        ('Paid', 'Paid'),
        ('contract', 'Contract'),
    )
    POD_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('unverified', 'Unverified'),
        ('rejected', 'Rejected'),
        ('completed', 'Delivered'),
        ('not_required', 'Not Required')
    )
    GST_LIABILITY_CHOICES = (
        ('consignor', 'Consignor'),
        ('consignee', 'Consignee'),
        ('carrier', 'Carrier'),
        ('exempted', 'Exempted'),
    )
    TDS_CERTIFICATE_STATUS = (
        ('y', 'Yes'),
        ('n', 'No'),
    )
    INWARD_PAYMENT_STATUS = (
        ('no_payment', 'Nil'),
        ('partial_received', 'Partial'),
        ('full_received', 'Full'),
        ('excess', 'Excess'),
    )
    INVOICE_STATUS = (
        ('no_invoice', 'NoInvoice'),
        ('invoice_raised', 'InvoiceRaised'),
        ('invoice_sent', 'InvoiceSent'),
        ('invoice_confirmed', 'InvoiceConfirmed'),
    )
    OUTWARD_STATUS = (
        ('no_payment_made', 'Nil'),
        ('partial', 'Partial'),
        ('complete', 'Full'),
        ('excess', 'Excess'),
    )
    BOOKING_STATUS = (
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    )
    IS_ADVANCE = (
        ('no', 'No'),
        ('yes', 'Yes'),
    )
    booking_id = models.CharField(max_length=35, unique=True, verbose_name='Booking ID')
    source_office = models.ForeignKey(AahoOffice, blank=True, null=True, related_name='source_office',
                                      on_delete=models.CASCADE, verbose_name='Source Office')
    destination_office = models.ForeignKey(
        AahoOffice, blank=True, null=True,
        related_name='destination_office',
        on_delete=models.CASCADE,
        verbose_name='Destination Office'
    )
    company = models.ForeignKey(
        Sme, blank=True, null=True,
        related_name='mb_bill_order_placed',
        on_delete=models.CASCADE,
        verbose_name='Customer who has placed order '
    )
    customer_to_be_billed_to = models.ForeignKey(
        Sme, blank=True, null=True, related_name='mb_bill_paid_by',
        on_delete=models.CASCADE,
        verbose_name='Customer who will make payment'
    )
    company_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='Company Code')
    supplier = models.ForeignKey(
        Broker, null=True, blank=True,
        related_name='team_booking_broker',
        on_delete=models.CASCADE,
        verbose_name='Broker Name'
    )
    booking_supplier = models.ForeignKey(Supplier, null=True, related_name='manualbooking_booking_supplier', blank=True,
                                         on_delete=models.CASCADE)
    accounting_supplier = models.ForeignKey(Supplier, related_name='manualbooking_accounting_supplier', null=True,
                                            blank=True, on_delete=models.CASCADE)
    owner_supplier = models.ForeignKey(Supplier, related_name='manualbooking_owner_supplier', null=True, blank=True,
                                       on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Owner Name')
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Driver Name')
    driver_supplier = models.ForeignKey('supplier.Driver', null=True, blank=True, on_delete=models.CASCADE,
                                        verbose_name='Supplier Driver')
    # consignor details
    consignor_name = models.CharField(max_length=100, blank=True, null=True)
    consignor_address = models.CharField(max_length=255, blank=True, null=True)
    consignor_city = models.CharField(max_length=35, blank=True, null=True)
    consignor_city_fk = models.ForeignKey(City, null=True, blank=True, related_name='booking_consignor_city',
                                          on_delete=models.CASCADE)
    consignor_pin = models.CharField(max_length=6, blank=True, null=True)
    consignor_phone = models.CharField(max_length=20, blank=True, null=True)
    consignor_cst_tin = models.CharField(max_length=35, blank=True, null=True)
    consignor_gstin = models.CharField(max_length=15, blank=True, null=True)
    # consignee details
    consignee_name = models.CharField(max_length=100, blank=True, null=True)
    consignee_address = models.CharField(max_length=400, blank=True, null=True)
    consignee_city = models.CharField(max_length=35, blank=True, null=True)
    consignee_city_fk = models.ForeignKey(City, null=True, blank=True, related_name='booking_consignee_city',
                                          on_delete=models.CASCADE)
    consignee_pin = models.CharField(max_length=6, blank=True, null=True)
    consignee_phone = models.CharField(max_length=20, blank=True, null=True)
    consignee_cst_tin = models.CharField(max_length=50, blank=True, null=True)
    consignee_gstin = models.CharField(max_length=50, blank=True, null=True)
    billing_type = models.CharField(max_length=20, choices=billing_types, blank=True, null=True)
    gst_liability = models.CharField(max_length=15, choices=GST_LIABILITY_CHOICES, blank=True, null=True)
    liability_of_service_tax = models.CharField(max_length=40, blank=True, null=True)
    shipment_date = models.DateField(null=True, blank=True)
    delivery_datetime = models.DateTimeField(null=True, blank=True)
    from_city = models.CharField(max_length=50, blank=True, null=True)
    to_city = models.CharField(max_length=50, blank=True, null=True)
    from_city_fk = models.ForeignKey(City, null=True, related_name='booking_from_city', on_delete=models.CASCADE)
    to_city_fk = models.ForeignKey(City, null=True, related_name='booking_to_city', on_delete=models.CASCADE)
    lorry_number = models.CharField(max_length=15, blank=True, null=True)
    vehicle = models.ForeignKey(Vehicle, null=True, on_delete=models.CASCADE)
    supplier_vehicle = models.ForeignKey('supplier.Vehicle', null=True, verbose_name='Vehicle',
                                         on_delete=models.CASCADE)
    type_of_vehicle = models.CharField(max_length=70, blank=True, null=True)
    vehicle_category = models.ForeignKey(VehicleCategory, null=True, on_delete=models.CASCADE)
    road_permit_number = models.CharField(max_length=255, blank=True, null=True)
    # invoice details
    party_invoice_number = models.CharField(max_length=255, blank=True, null=True)
    party_invoice_date = models.DateField(blank=True, null=True)
    party_invoice_amount = models.CharField(max_length=100, blank=True, null=True)
    # material details
    number_of_package = models.CharField(max_length=30, blank=True, null=True)
    material = models.CharField(max_length=500, blank=True, null=True)
    loaded_weight = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=3, default=1,
                                        verbose_name='Loaded Weight (MT)')
    delivered_weight = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=3, default=1,
                                           verbose_name='Delivered Weight (MT)')
    charged_weight = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=3, default=1,
                                         verbose_name='Party Charged Weight(MT)')
    supplier_charged_weight = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=3, default=1,
                                                  verbose_name='Supplier Charged Weight(MT)')
    party_rate = models.IntegerField(blank=True, null=True, default=0, verbose_name='Party Rate(M.T.)')
    supplier_rate = models.IntegerField(blank=True, null=True, default=0, verbose_name='Supplier Rate(M.T.)')
    # Insurance
    is_insured = models.BooleanField(default=False)
    insurance_provider = models.CharField(max_length=200, blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=200, blank=True, null=True)
    insured_amount = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True, default=0)
    insurance_date = models.DateField(blank=True, null=True)
    insurance_risk = models.CharField(max_length=200, blank=True, null=True)
    # vendor details
    driver_name = models.CharField(max_length=255, blank=True, null=True)
    driver_phone = models.CharField(max_length=255, blank=True, null=True)
    driver_dl_number = models.CharField(max_length=255, blank=True, null=True)
    driver_dl_validity = models.DateField(blank=True, null=True)
    truck_broker_owner_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Truck Owner/Broker name')
    truck_broker_owner_phone = models.CharField(
        max_length=25, blank=True, null=True, verbose_name='Truck Owner/Broker Phone Number')
    truck_owner_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Truck Owner name')
    truck_owner_phone = models.CharField(
        max_length=25, blank=True, null=True, verbose_name='Truck Owner Phone Number')
    loading_points = models.CharField(max_length=255, blank=True, null=True)
    unloading_points = models.CharField(max_length=255, blank=True, null=True)
    # payment details
    total_in_ward_amount = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0, blank=True)
    total_out_ward_amount = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0, blank=True)
    total_amount_to_company = models.IntegerField(blank=True, null=True, default=0)
    advance_amount_from_company = models.IntegerField(default=0, blank=True, null=True)
    refund_amount = models.IntegerField(default=0, blank=True, null=True)
    total_amount_to_owner = models.IntegerField(blank=True, null=True, default=0)
    loading_charge = models.IntegerField(blank=True, null=True, default=0)
    unloading_charge = models.IntegerField(blank=True, null=True, default=0)
    detention_charge = models.IntegerField(blank=True, null=True, default=0)
    additional_charges_for_company = models.IntegerField(
        blank=True, null=True, verbose_name="Additional Charges/Deductions for Company (+/-)", default=0)
    remarks_about_additional_charges = models.TextField(
        blank=True, null=True, verbose_name="Explanation Additional Charges/Deductions for Company (+/-)")
    additional_charges_for_owner = models.IntegerField(
        blank=True, null=True, verbose_name="Additional Charges/Deductions for Owner (+/-)", default=0)
    note_for_additional_owner_charges = models.TextField(
        blank=True, null=True, verbose_name="Explanation Additional Charges/Deductions for Owner (+/-)")
    # deduction for vendor
    commission = models.IntegerField(blank=True, null=True, default=0)
    lr_cost = models.IntegerField(blank=True, null=True, default=0)
    deduction_for_advance = models.IntegerField(blank=True, null=True, default=0)
    deduction_for_balance = models.IntegerField(blank=True, null=True, default=0)
    other_deduction = models.IntegerField(blank=True, null=True, default=0)
    remarks_about_deduction = models.TextField(blank=True, null=True)
    # deduction for company
    deductions_for_company = models.IntegerField(default=0)
    # billing details
    to_be_billed_to = models.CharField(max_length=200, blank=True, null=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='Invoice Number')
    billing_address = models.CharField(max_length=300, blank=True, null=True)
    billing_contact_number = models.CharField(max_length=50, blank=True, null=True)
    billing_invoice_date = models.DateField(blank=True, null=True)
    invoice_remarks_for_additional_charges = models.TextField(blank=True, null=True)
    invoice_remarks_for_deduction_discount = models.TextField(blank=True, null=True)
    tds_deducted_amount = models.IntegerField(blank=True, null=True, default=0)
    # status
    pod_date = models.DateTimeField(blank=True, null=True)
    pod_status = models.CharField(max_length=20, choices=POD_STATUS_CHOICES, blank=True, null=True, default='pending')
    outward_payment_status = models.CharField(
        max_length=20, choices=OUTWARD_STATUS, default='no_payment_made', null=True)
    inward_payment_status = models.CharField(
        max_length=20, choices=INWARD_PAYMENT_STATUS, default='no_payment', null=True)
    invoice_status = models.CharField(max_length=35, null=True, choices=INVOICE_STATUS, default='no_invoice')
    comments = models.TextField(blank=True, null=True)
    remarks_advance_from_company = models.TextField(blank=True, null=True)
    tds_certificate_status = models.CharField(max_length=20, choices=TDS_CERTIFICATE_STATUS, default='N', null=True)
    booking_status = models.CharField(max_length=70, choices=BOOKING_STATUS, default='confirmed')
    booking_status_color = models.ForeignKey(BookingStatusColor, null=True, blank=True, on_delete=models.CASCADE)
    is_advance = models.CharField(max_length=20, choices=IS_ADVANCE, default='no', null=True)
    is_print_payment_mode_instruction = models.BooleanField(default=False)
    invoice_summary = models.ForeignKey(
        InvoiceSummary, null=True, blank=True, related_name='booking', on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, null=True, related_name='manual_booking_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name='manual_booking_changed_by',
                                   on_delete=models.CASCADE)
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

    def clean(self):
        if self.booking_status == 'cancelled' and (
                self.outward_booking.exclude(deleted=True).exists()):
            raise ValidationError('Outward payment has already made')
        elif self.booking_status == 'cancelled' and self.inward_booking.exclude(deleted=True).exists():
            raise ValidationError('Inward payment has already made')
        elif self.booking_status == 'cancelled' and self.podfile_set.filter(verified=True, is_valid=True).exists():
            raise ValidationError('POD already received and verified')
        elif self.booking_status == 'cancelled' and self.invoices.exclude(deleted=True).exists():
            raise ValidationError('Invoice is already raised')
        else:
            pass

    @property
    def refundable_paid_amount(self):
        return to_int(to_round(sum(self.outward_booking.filter(
            is_refund_amount=True).exclude(deleted=True).values_list('actual_amount', flat=True))))

    @property
    def credit_amount_customer(self):
        return to_int(to_round(sum(self.creditnotecustomer_set.filter(status__in=['partial', 'adjusted']).values_list(
            'adjusted_amount', flat=True)) + sum(
            self.creditnotecustomerdirectadvance_set.filter(status__in=['partial', 'adjusted']).values_list(
                'adjusted_amount', flat=True))))

    @property
    def credit_amount_supplier(self):
        return to_int(to_round(sum(self.creditnotesupplier_set.filter(status__in=['partial', 'adjusted']).values_list(
            'adjusted_amount', flat=True))))

    @property
    def adjusted_cnca_amount(self):
        return to_int(to_round(sum(
            self.creditnotecustomerdirectadvance_set.filter(status__in=['partial', 'adjusted']).values_list(
                'adjusted_amount', flat=True))))

    @property
    def debit_amount_customer(self):
        return to_int(to_round(sum(self.debitnotecustomer_set.filter(status__in=['partial', 'adjusted']).values_list(
            'adjusted_amount', flat=True))))

    @property
    def debit_amount_supplier(self):
        return to_int(to_round(sum(self.debitnotesupplier_set.filter(status__in=['partial', 'adjusted']).values_list(
            'adjusted_amount', flat=True)) + sum(
            self.creditnotecustomerdirectadvance_set.filter(status__in=['partial', 'adjusted']).values_list(
                'adjusted_amount', flat=True))))

    @property
    def approved_debit_amount_supplier(self):
        return to_int(to_round(sum(self.debitnotesupplier_set.filter(status__in=['approved']).values_list(
            'debit_amount', flat=True))))

    @property
    def supplier_freight(self):
        return to_int(to_round(self.supplier_charged_weight * self.supplier_rate))

    @property
    def customer_freight(self):
        return to_round(self.charged_weight * self.party_rate)

    @property
    def vehicle_number(self):
        return self.vehicle.number() if self.vehicle else ''

    @property
    def refundable_due_amount(self):
        return to_int(self.refund_amount - self.refundable_paid_amount)

    @property
    def supplier_amount(self):
        return to_int(
            to_round(self.supplier_freight + to_int(
                to_float(self.additional_charges_for_owner) + to_float(self.loading_charge) + to_float(
                    self.unloading_charge) + to_float(self.detention_charge) - to_float(self.commission) - to_float(
                    self.lr_cost) - to_float(self.deduction_for_advance) - to_float(
                    self.deduction_for_balance) - to_float(
                    self.other_deduction)
            ))
        )

    @property
    def amount_paid_to_supplier_data(self):
        return {
            'outward_payment': [payment.to_json() for payment in
                                self.outward_booking.exclude(deleted=True).exclude(is_refund_amount=True)],
            'debit_note': self.debitnotesupplier_set.filter(status__in=['partial', 'adjusted']).exclude(deleted=True),
            'credit_note': self.creditnotesupplier_set.filter(status__in=['partial', 'adjusted']).exclude(deleted=True),
            'credit_note_direct_advance': self.creditnotecustomerdirectadvance_set.filter(
                status__in=['partial', 'adjusted']).exclude(deleted=True),
        }

    @property
    def amount_received_from_customer_data(self):
        return {
            'inward_payment': self.inward_booking.exclude(deleted=True),
            'debit_note': self.debitnotecustomer_set.filter(status__in=['partial', 'adjusted']).exclude(deleted=True),
            'credit_note': self.creditnotecustomer_set.filter(status__in=['partial', 'adjusted']).exclude(deleted=True),
            'credit_note_direct_advance': self.creditnotecustomerdirectadvance_set.filter(
                status__in=['partial', 'adjusted']).exclude(deleted=True),
        }

    @property
    def customer_amount(self):
        return to_int(self.customer_freight + to_int(
            to_float(self.additional_charges_for_company) - to_float(self.deductions_for_company)))

    @property
    def amount_paid_to_supplier(self):
        return to_int(self.outward_amount - self.credit_amount_supplier + self.debit_amount_supplier)

    @property
    def fms_supplier_amount(self):
        return to_int(self.total_amount_to_owner + self.credit_amount_supplier - self.debit_amount_supplier)

    @property
    def fms_supplier_paid_amount(self):
        return to_int(self.outward_amount)

    @property
    def fms_balance_supplier(self):
        return self.fms_supplier_amount - self.outward_amount

    @property
    def amount_received_from_customer(self):
        return to_int(
            self.inward_amount + to_int(
                self.tds_deducted_amount) + self.credit_amount_customer - self.debit_amount_customer)

    @property
    def outward_amount(self):
        return to_int(
            to_round(sum(self.outward_booking.exclude(actual_amount=None).exclude(is_refund_amount=True).values_list(
                'actual_amount', flat=True)))
        )
    @property
    def adjusted_outward_amount(self):
        return to_int(
            to_round(sum(self.outward_booking.filter(payment_mode='adjustment').exclude(actual_amount=None).exclude(is_refund_amount=True).values_list(
                'actual_amount', flat=True)))
        )

    @property
    def balance_for_customer(self):
        return to_int(self.total_amount_to_company - (
                self.inward_amount + self.tds_deducted_amount + self.credit_amount_customer - self.debit_amount_customer
        ))

    @property
    def balance_for_supplier(self):
        return to_int(self.total_amount_to_owner - (
                self.outward_amount - self.credit_amount_supplier + self.debit_amount_supplier))

    @property
    def inward_amount(self):
        return to_round(sum(self.inward_booking.exclude(actual_amount=None).exclude(
            deleted=True).values_list('actual_amount', flat=True)))

    @property
    def tds_amount_customer(self):
        return to_round(sum(self.inward_booking.exclude(tds=None).values_list('tds', flat=True)))

    def __str__(self):
        return '{}, {}, {}, {}'.format(self.booking_id, self.from_city, self.to_city, self.lorry_number)

    def save(self, *args, **kwargs):
        self.from_city = None if not self.from_city_fk else self.from_city_fk.name.title()
        self.to_city = None if not self.to_city_fk else self.to_city_fk.name.title()
        self.lorry_number = None if not isinstance(self.vehicle, Vehicle) else self.vehicle.number()
        super().save(*args, **kwargs)

        from team import tasks
        if settings.ENABLE_CELERY:
            tasks.update_booking_summary.delay(self.id)
            tasks.save_manual_booking_data.delay(self.id)
        else:
            tasks.update_booking_summary(self.id)
            tasks.save_manual_booking_data(self.id)

    def delete(self, *args, **kwargs):
        DeletedData.objects.create(model='manual_booking', data=json.loads(
            serializers.serialize(format='json', queryset=ManualBooking.objects.filter(id=self.id),
                                  use_natural_foreign_keys=True).strip("[]")))
        super().delete(*args, **kwargs)

    def natural_key(self):
        return json.loads(serializers.serialize(format='json', queryset=ManualBooking.objects.filter(id=self.id),
                                                use_natural_foreign_keys=True).strip("[]"))

    def pod_status_verbose(self):
        return dict(ManualBooking.POD_STATUS_CHOICES)[self.pod_status]

    @staticmethod
    def get_company_name(company):
        return Sme.get_company_name(company)

    def freight_from_company(self):
        return self.party_rate * self.charged_weight

    def to_lr_list_json(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'lr_number': [lr.lr_number for lr in self.lr_numbers.all()],
            'shipment_date': self.shipment_date,
            'company': self.get_company_name(self.company.id if self.company else None),
            'supplier_name': self.truck_broker_owner_name,
            'from_city': self.from_city,
            'to_city': self.to_city,
            'lorry_number': self.lorry_number,
            'total_amount_to_company': self.total_amount_to_company,
            'total_amount_to_owner': self.total_amount_to_owner,
            'total_out_ward_amount': self.total_out_ward_amount,
            'total_in_ward_amount': self.total_in_ward_amount,
        }


class LrNumber(models.Model):
    POD_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('unverified', 'Unverified'),
        ('rejected', 'Rejected'),
        ('completed', 'Delivered')
    )
    booking = models.ForeignKey(ManualBooking, blank=True, null=True, related_name='lr_numbers',
                                on_delete=models.CASCADE)
    lr_number = models.CharField(max_length=30, null=True, db_index=True)
    datetime = models.DateTimeField(null=True, blank=True)
    source_office = models.ForeignKey(AahoOffice, null=True, related_name='lr_source_office', on_delete=models.CASCADE)
    destination_office = models.ForeignKey(AahoOffice, blank=True, null=True, related_name='lr_destination_office',
                                           on_delete=models.CASCADE)
    pod_status = models.CharField(max_length=20, choices=POD_STATUS_CHOICES, blank=True, null=True, default='pending')
    created_by = models.ForeignKey(User, null=True, related_name='lr_number_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, related_name='lr_number_changed_by',
                                   limit_choices_to={'is_staff': True},
                                   on_delete=models.CASCADE)

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

    def __str__(self):
        return "{}, {}, {}".format(
            self.lr_number, self.booking.booking_id if isinstance(self.booking, ManualBooking) else None,
            self.datetime.date())

    def upload(self):
        return get_or_none(S3Upload, filename='{}.pdf'.format(self.lr_number))

    def natural_key(self):
        return json.loads(serializers.serialize(format='json', queryset=LrNumber.objects.filter(id=self.id),
                                                use_natural_foreign_keys=True).strip("[]"))

    def delete(self, *args, **kwargs):
        DeletedData.objects.create(model='lr_number', data=json.loads(
            serializers.serialize(format='json', queryset=LrNumber.objects.filter(id=self.id),
                                  use_natural_foreign_keys=True).strip("[]")))
        super().delete(*args, **kwargs)

    def to_json(self):
        return {
            'id': self.id,
            'booking_id': None if not self.booking else self.booking.booking_id,
            'lr_number': self.lr_number,
            'date': format_date(self.datetime),
            'created_on': format_datetime(self.created_on),
            'updated_on': format_datetime(self.updated_on)
        }


class ManualBookingS3Upload(models.Model):
    booking = models.ForeignKey(ManualBooking, on_delete=models.CASCADE)
    s3_upload = models.ForeignKey(S3Upload, on_delete=models.CASCADE)
    is_valid = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class LrS3Upload(models.Model):
    lr_number = models.ForeignKey(LrNumber, on_delete=models.CASCADE)
    s3_upload = models.ForeignKey(S3Upload, on_delete=models.CASCADE)
    is_valid = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class RejectedPOD(models.Model):
    booking = models.ForeignKey(ManualBooking, on_delete=models.CASCADE)
    lr = models.ForeignKey(LrNumber, null=True, on_delete=models.CASCADE)
    remarks = models.CharField(max_length=500)
    rejected_by = models.ForeignKey(User, limit_choices_to={'is_staff': True}, related_name="rejected_by_rejected_pod",
                                    on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, related_name="created_by_rejected_pod",
                                   on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, null=True, related_name="changed_by_rejected_pod",
                                   on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}, {}, {}'.format(
            self.booking.booking_id if self.booking else '', self.lr.lr_number if self.lr else '', self.remarks)


class ManualBookingSummary(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    vehicle = models.OneToOneField(Vehicle, blank=True, null=True, on_delete=models.CASCADE)
    supplier_vehicle = models.OneToOneField('supplier.Vehicle', null=True, blank=True, on_delete=models.CASCADE)
    summary = JSONField()
    created_by = models.ForeignKey(User, null=True, related_name='booking_summary_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, related_name='booking_summary_changed_by',
                                   limit_choices_to={'is_staff': True}, on_delete=models.CASCADE)

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


class BookingConsignorConsignee(models.Model):
    categories_choice = (
        ('CR', 'Consignor'),
        ('CE', 'Consignee'),
    )
    booking = models.ForeignKey(ManualBooking, null=True, on_delete=models.CASCADE)
    lr = models.ForeignKey(LrNumber, null=True, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    cst_tin = models.CharField(max_length=255, blank=True, null=True)
    gstin = models.CharField(max_length=15, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, related_name="created_by_booking_consignor_consignee",
                                   on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, null=True, related_name="changed_by_booking_consignor_consignee",
                                   on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class BookingInsurance(models.Model):
    is_insured = models.BooleanField(default=False)
    insurance_provider = models.CharField(max_length=200, blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=200, blank=True, null=True)
    insured_amount = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True, default=0)
    insurance_date = models.DateField(blank=True, null=True)
    insurance_risk = models.CharField(max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, related_name="created_by_booking_insurance",
                                   on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, null=True, related_name="changed_by_booking_booking_insurance",
                                   on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class InWardPayment(models.Model):
    modes = (
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('neft', 'NEFT'),
        ('imps', 'IMPS'),
        ('rtgs', 'RTGS'),
        ('happay', 'Happay'),
        ('cash_deposit', 'Cash Deposit'),
        ('hdfc_internal_account', 'HDFC Internal Account'),
    )
    booking_id = models.ManyToManyField(ManualBooking, blank=True, related_name='inward_booking')
    received_from = models.CharField(max_length=300, null=True)
    tds = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0)
    actual_amount = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0)
    expected_amount = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0)
    payment_mode = models.CharField(max_length=60, choices=modes, null=True)
    trn = models.CharField(max_length=200, blank=True, null=True)
    remarks = models.TextField(null=True)
    payment_date = models.DateField(null=True)
    invoice_number = models.CharField(max_length=300, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, related_name='inward_payment_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="inward_payment_changed_by",
                                   on_delete=models.CASCADE)
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

    def natural_key(self):
        return json.loads(serializers.serialize(format='json', queryset=InWardPayment.objects.filter(id=self.id),
                                                use_natural_foreign_keys=True).strip("[]"))

    def delete(self, *args, **kwargs):
        DeletedData.objects.create(model='inward_payment', data=json.loads(
            serializers.serialize(format='json', queryset=InWardPayment.objects.filter(id=self.id),
                                  use_natural_foreign_keys=True).strip("[]")))
        super().delete(*args, **kwargs)

    def __str__(self):
        return "id: {}, Received From: {}, Amount: {}, Mode: {}".format(
            self.id, self.received_from, self.actual_amount, self.get_payment_mode_display())


class OutWardPayment(models.Model):
    mode = (
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('neft', 'NEFT'),
        ('imps', 'IMPS'),
        ('rtgs', 'RTGS'),
        ('happay', 'Happay'),
        ('fuel_card', 'Fuel Card'),
        ('hdfc_internal_account', 'HDFC Internal Account'),
        ('adjustment', 'Adjustment')
    )
    STATUS = (
        ('paid', 'Paid'),
        ('unpaid', 'Not Paid'),
        ('reconciled', 'Reconciled'),
    )
    booking_id = models.ManyToManyField(ManualBooking, blank=True, related_name='outward_booking')
    aaho_office = models.ForeignKey(AahoOffice, null=True, blank=True, on_delete=models.CASCADE)
    bank_account = models.ForeignKey(Bank, blank=True, null=True, on_delete=models.CASCADE)
    fuel_card = models.ForeignKey(FuelCard, blank=True, null=True, on_delete=models.CASCADE)
    paid_to = models.CharField(max_length=300, null=True)
    lorry_number = models.CharField(max_length=30, blank=True, null=True)
    actual_amount = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0)
    tds = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0)
    expected_amount = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0)
    payment_mode = models.CharField(max_length=60, choices=mode, null=True)
    remarks = models.TextField(null=True)
    payment_date = models.DateField(null=True)
    utr = models.CharField(max_length=200, null=True, blank=True)
    invoice_number = models.CharField(max_length=300, blank=True, null=True)
    status = models.CharField(max_length=35, null=True, choices=STATUS, default='unpaid')
    is_sms_supplier = models.BooleanField(default=False)
    is_refund_amount = models.BooleanField(default=False)
    adjusted_outward_payments = models.ManyToManyField("self", blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='outward_payment_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="outward_payment_changed_by",
                                   on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ('-id',)

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
    def bookings(self):
        return '\n'.join([booking.booking_id for booking in self.booking_id.exclude(booking_status='cancelled')])

    @property
    def vehicle_number(self):
        return '\n'.join([booking.vehicle_number for booking in self.booking_id.exclude(booking_status='cancelled')])

    @property
    def lr_numbers(self):
        return '\n'.join(['\n'.join([lr.lr_number for lr in booking.lr_numbers.exclude(deleted=True)]) for booking in
                          self.booking_id.exclude(booking_status='cancelled')])

    def delete(self, *args, **kwargs):
        DeletedData.objects.create(model='outward_payment', data=json.loads(
            serializers.serialize(format='json', queryset=OutWardPayment.objects.filter(id=self.id),
                                  use_natural_foreign_keys=True).strip("[]")))
        try:
            mb = ManualBooking.objects.get(booking_id=self.booking_id.all().last().booking_id)
            mb.total_out_ward_amount -= self.actual_amount
            mb.save()
            super().delete(*args, **kwargs)
        except:
            super().delete(*args, **kwargs)

    # def natural_key(self):
    #     return json.loads(serializers.serialize(format='json', queryset=OutWardPayment.objects.filter(id=self.id),
    #                                             use_natural_foreign_keys=True).strip("[]"))

    def __str__(self):
        return "id: {}, Paid To: {}, Amount: {}, Mode: {}".format(
            self.id, self.paid_to, self.actual_amount, self.get_payment_mode_display())

    def to_json(self):
        return {
            'id': self.id,
            'account_number': None if not self.bank_account else self.bank_account.account_number,
            'fuel_card': None if not self.fuel_card else self.fuel_card.card_number,
            'paid_to': self.paid_to,
            'lorry_number': self.lorry_number,
            'actual_amount': self.actual_amount,
            'expected_amount': self.expected_amount,
            'payment_mode': self.get_payment_mode_display(),
            'remarks': self.remarks,
            'payment_date': format_date(self.payment_date),
            'invoice_number': self.invoice_number,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }


class OutWardPaymentBill(models.Model):
    outward_pmt = models.ManyToManyField(OutWardPayment, related_name="outward_payment_bill")
    booking = models.ForeignKey(ManualBooking, blank=True, null=True, related_name='outward_payment_bill',
                                on_delete=models.CASCADE)
    bill_number = models.CharField(max_length=30, null=True, unique=True)
    bill_date = models.DateField(null=True)
    amount = models.IntegerField(null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    lr_number = models.CharField(max_length=200, blank=True, null=True)
    from_city = models.CharField(max_length=50, blank=True, null=True)
    to_city = models.CharField(max_length=50, blank=True, null=True)
    loading_date = models.DateField(blank=True, null=True)
    weight = models.CharField(max_length=50, blank=True, null=True)
    paid_to = models.CharField(max_length=50, blank=True, null=True)
    pan_number = models.CharField(max_length=30, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, related_name='outward_payment_bill_created_by',
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, limit_choices_to={'is_staff': True},
                                   related_name="outward_payment_bill_changed_by",
                                   on_delete=models.CASCADE)
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

    @property
    def total_amount(self):
        return sum(
            self.outward_pmt.exclude(deleted=True).exclude(actual_amount=None).values_list('actual_amount', flat=True))

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def natural_key(self):
        return json.loads(serializers.serialize(format='json', queryset=OutWardPaymentBill.objects.filter(id=self.id),
                                                use_natural_foreign_keys=True).strip("[]"))

    def delete(self, *args, **kwargs):
        DeletedData.objects.create(model='outward_payment_bill', data=json.loads(
            serializers.serialize(format='json', queryset=OutWardPaymentBill.objects.filter(id=self.id),
                                  use_natural_foreign_keys=True).strip("[]")))
        super().delete(*args, **kwargs)

    def __str__(self):
        return "{}, {}, {}".format(self.bill_number, self.bill_date, self.amount)


class Invoice(models.Model):
    bookings = models.ManyToManyField(ManualBooking, blank=True, related_name='invoices')
    invoice_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    company_name = models.CharField(max_length=255, null=True)
    customer_fk = models.ForeignKey(Sme, null=True, blank=True, related_name='team_invoice',
                                    on_delete=models.CASCADE)
    payment_received = models.BooleanField(default=False)
    address = models.CharField(max_length=500, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6, blank=True, null=True)
    gstin = models.CharField(max_length=15, blank=True, null=True)
    total_amount = models.IntegerField(default=0)
    advance_payment = models.IntegerField(default=0)
    remarks = models.TextField(null=True, blank=True)
    service_tax_paid_by = models.CharField(max_length=255, blank=True, null=True)
    service_tax_aaho = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    s3_upload = models.ForeignKey(S3Upload, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, related_name='create_invoice', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    summary_required = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, related_name='change_invoice',
                                   limit_choices_to={'is_staff': True}, on_delete=models.CASCADE)
    history = HistoricalRecords()

    class Meta:
        ordering = ('-id',)

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
    def invoice_balance(self):
        return sum([booking.balance_for_customer for booking in self.bookings.exclude(booking_status='cancelled')])

    def delete(self, *args, **kwargs):
        from restapi.models import BookingStatusesMapping
        DeletedData.objects.create(model='invoice', data=json.loads(
            serializers.serialize(format='json', queryset=Invoice.objects.filter(id=self.id),
                                  use_natural_foreign_keys=True).strip("[]")))
        try:
            for booking in self.bookings.all():
                booking.invoice_status = 'no_invoice'
                booking.save()
                BookingStatusesMapping.objects.filter(
                    manual_booking=booking,
                    booking_status_chain__booking_status__status__in=[
                        'invoice_raised', 'invoice_confirmed',
                        'party_invoice_sent']).update(booking_stage='reverted')
            super().delete(*args, **kwargs)
        except:
            super().delete(*args, **kwargs)

    def natural_key(self):
        return json.loads(serializers.serialize(format='json', queryset=Invoice.objects.filter(id=self.id),
                                                use_natural_foreign_keys=True).strip("[]"))

    def __str__(self):
        return "Invoice no: {}, Date: {}".format(self.invoice_number, self.date)

    def get_company_address(self):
        address = []
        if self.address:
            address.append(self.address)
        if self.city:
            if self.pin:
                address.append(' - '.join([self.city.name, self.pin]))
            else:
                address.append(self.city.name)
        return ', '.join(address)

    def get_company_name(self):
        return self.company_name

    @property
    def get_customer_balance(self):
        customer_balance = 0
        for booking in self.bookings.all():
            customer_balance += booking.balance_for_customer
        return customer_balance

    @property
    def is_overdue(self):
        if self.customer_fk and (
                self.date + timedelta(days=to_int(self.customer_fk.credit_period))) <= datetime.now().date():
            return True
        else:
            return False

    @property
    def get_overdue_balance(self):
        overdue_balance = 0
        if self.customer_fk and (
                self.date + timedelta(days=to_int(self.customer_fk.credit_period))) <= datetime.now().date():
            for booking in self.bookings.all():
                overdue_balance += booking.balance_for_customer
        return overdue_balance

    @property
    def get_amount_to_be_received(self):
        total_inward = 0
        for booking in self.bookings.all():
            total_inward += booking.total_in_ward_amount
        return self.total_amount - total_inward


class ToPayInvoice(models.Model):
    bookings = models.ManyToManyField(ManualBooking, related_name="to_pay_invoices")
    invoice_gen_office = models.CharField(max_length=200, blank=True, null=True)
    invoice_number = models.CharField(max_length=30, unique=True, null=True)
    date = models.DateField(blank=True, null=True)
    company_name = models.CharField(max_length=100, null=True)
    customer_fk = models.ForeignKey(Sme, null=True, blank=True, related_name='team_to_pay_invoice',
                                    on_delete=models.CASCADE)
    payment_received = models.BooleanField(default=False)
    company_address = models.CharField(max_length=300, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6, blank=True, null=True)
    gstin = models.CharField(max_length=15, blank=True, null=True)
    source = models.CharField(max_length=35, blank=True, null=True)
    destination = models.CharField(max_length=35, blank=True, null=True)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    lr_number = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.CharField(max_length=100, blank=True, null=True)
    rate = models.CharField(max_length=20, blank=True, null=True)
    total_payable_freight = models.CharField(max_length=30, blank=True, null=True)
    amount_payable_to_transiq = models.CharField(max_length=30, blank=True, null=True)
    balance_payable_to_lorry_driver = models.CharField(max_length=30, blank=True, null=True)
    advance_payment = models.IntegerField(default=0)
    remarks = models.TextField(null=True, blank=True)
    service_tax_paid_by = models.CharField(max_length=255, blank=True, null=True)
    service_tax_aaho = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, related_name='to_pay_invoice_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey(User, null=True, limit_choices_to={'is_staff': True},
                                   related_name="to_pay_invoice_changed_by",
                                   on_delete=models.CASCADE)
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

    def delete(self, *args, **kwargs):
        DeletedData.objects.create(model='to_pay_invoice', data=json.loads(
            serializers.serialize(format='json', queryset=ToPayInvoice.objects.filter(id=self.id),
                                  use_natural_foreign_keys=True).strip("[]")))
        try:
            for booking in self.bookings.all():
                booking.invoice_status = 'no_invoice'
                booking.save()
            super().delete(*args, **kwargs)
        except:
            super().delete(*args, **kwargs)

    def natural_key(self):
        return json.loads(serializers.serialize(format='json', queryset=ToPayInvoice.objects.filter(id=self.id),
                                                use_natural_foreign_keys=True).strip("[]"))

    def __str__(self):
        return "Invoice Id: {}, Date: {}".format(self.invoice_number, self.date)

    def get_company_address(self):
        address = []
        if self.company_address:
            address.append(self.company_address)
        if self.city:
            if self.pin:
                address.append(' - '.join([self.city.name, self.pin]))
            else:
                address.append(self.city.name)
        return ', '.join(address)

    def get_company_name(self):
        return self.company_name


class NonTransactionalExpense(models.Model):
    PAYMENT_MODE_CHOICES = (
        ('cash', 'Cash'),
        ('neft', 'NEFT'),
        ('imps', 'IMPS'),
        ('cheque', 'Cheque')
    )
    office = models.ForeignKey(AahoOffice, null=True, related_name='non_transactional_office', on_delete=models.CASCADE)
    paid_to = models.CharField(max_length=300, blank=True, null=True)
    paid_by = models.ForeignKey(Employee, null=True, related_name='non_transactional_paid_by', on_delete=models.CASCADE)
    amount = models.IntegerField(null=True)
    payment_mode = models.CharField(max_length=30, choices=PAYMENT_MODE_CHOICES, null=True, blank=True)
    payment_date = models.DateTimeField(null=True)
    remarks = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(Employee, null=True, related_name='non_transactional_created_by',
                                   on_delete=models.CASCADE)
    changed_by = models.ForeignKey(Employee, null=True, related_name='non_transactional_changed_by',
                                   on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)


class NotifyCompletedTaskEmail(models.Model):
    TASK_CHOICES = (
        ('notify_admins_about_pending_pod', 'Notify Admin About Pending POD'),
        ('notify_weekly_partial_tbb', 'Notify Weekly Partial TBB'),
        ('notify_admins_about_to_pay_booking', 'Notify About TO Pay Booking'),
        ('notify_outward_payment_status', 'Notify Outward Payment Status')
    )
    bookings = models.ManyToManyField(ManualBooking, related_name='booking_notify_completed_task')
    task = models.CharField(max_length=100, choices=TASK_CHOICES, null=True)
    office = models.ForeignKey(AahoOffice, null=True, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, related_name='notify_complete_task_email_created_by',
                                   on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, null=True, related_name='notify_complete_task_email_changed_by',
                                   on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)


class DeletedData(models.Model):
    MODEL_CHOICES = (
        ('manual_booking', 'Manual Booking'),
        ('lr_number', 'LR Number'),
        ('outward_payment', 'Outward Payment'),
        ('inward_payment', 'Inward Payment'),
        ('to_pay_invoice', 'To Pay Invoice'),
        ('tbb_pay_invoice', 'TBB Pay Invoice'),
        ('invoice', 'Invoice'),
        ('outward_payment_bill', 'Outward Payment Bill')
    )

    model = models.CharField(max_length=100, choices=MODEL_CHOICES)
    data = JSONField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, related_name='deleted_data_created_by',
                                   on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)


class PendingInwardPaymentEntry(models.Model):
    PAYMENT_MODES = (
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('neft', 'NEFT'),
        ('rtgs', 'RTGS'),
        ('cash_deposit', 'Cash Deposit'),
        ('hdfc_internal_account', 'HDFC'),
    )
    customer = models.ForeignKey(Sme, null=True, blank=True, on_delete=models.CASCADE)
    inward_payment = models.ManyToManyField(InWardPayment, blank=True)
    customer_name = models.CharField(max_length=300, blank=True, null=True)
    payment_mode = models.CharField(max_length=50, null=True, choices=PAYMENT_MODES)
    amount = models.DecimalField(null=True, max_digits=12, decimal_places=2, default=0)
    tds = models.DecimalField(null=True, max_digits=12, decimal_places=2, default=0)
    bookings = models.ManyToManyField(ManualBooking, blank=True)
    payment_date = models.DateField(null=True)
    adjusted_flag = models.BooleanField(default=False)
    credited_flag = models.BooleanField(default=False)
    uploaded_datetime = models.DateTimeField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, related_name='pending_payment_uploaded_by', null=True, blank=True,
                                    on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    adjusted_datetime = models.DateTimeField(null=True, blank=True)
    adjusted_by = models.ForeignKey(User, related_name='pending_payment_adjusted_by', null=True, blank=True,
                                    on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='pending_inward_payment_entry_created_by',
                                   on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, null=True, related_name='pending_inward_payment_entry_changed_by',
                                   on_delete=models.CASCADE)
    trn = models.TextField(null=True, blank=True)
    additional_remark = models.TextField(null=True, blank=True)

    def __str__(self):
        return '{}, {}, {}'.format(self.customer.get_name() if self.customer else '', self.amount, self.payment_date)

    def save(self, *args, **kwargs):
        from team import tasks
        pending_inward_instance = get_or_none(PendingInwardPaymentEntry, id=self.id)
        if isinstance(pending_inward_instance, PendingInwardPaymentEntry) and isinstance(
                pending_inward_instance.customer, Sme):
            customer_id = pending_inward_instance.customer.id
        else:
            customer_id = None
        super().save(*args, **kwargs)
        pending_inward_instance = get_or_none(PendingInwardPaymentEntry, id=self.id)
        if isinstance(pending_inward_instance, PendingInwardPaymentEntry) and isinstance(
                pending_inward_instance.customer, Sme):
            if settings.ENABLE_CELERY:
                tasks.update_accounting_summary.delay(customer_id=pending_inward_instance.customer.id)
                if customer_id:
                    tasks.update_accounting_summary.delay(customer_id=customer_id)
            else:
                tasks.update_accounting_summary(customer_id=pending_inward_instance.customer.id)
                if customer_id:
                    tasks.update_accounting_summary(customer_id=customer_id)

    def to_json(self):
        return {
            'id': self.id,
            'payment_date': self.payment_date.strftime('%d-%b-%Y') if self.payment_date else '',
            'customer': {
                'customer_text': to_str(self.customer_name), 'id': self.customer.id if self.customer else None,
                'name': self.customer.get_name() if self.customer else None
            },
            'payment_mode': self.get_payment_mode_display(),
            'trn': self.trn,
            'tds': to_str(self.tds),
            'amount': to_str(self.amount),
            'additional_remark': self.additional_remark
        }


class CreditDebitNoteReason(models.Model):
    name = models.CharField(max_length=30, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='credit_debit_note_reason_created_by',
                                   on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, null=True, related_name='credit_debit_note_reason_changed_by',
                                   on_delete=models.CASCADE)

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super().save()

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name


class CreditNoteCustomer(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    credit_note_number = models.CharField(max_length=16, unique=True, editable=False)  # editable=False
    bookings = models.ManyToManyField(ManualBooking, blank=True, verbose_name='Adjusted Bookings')
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Sme, null=True, on_delete=models.CASCADE)
    reason = models.ForeignKey(CreditDebitNoteReason, on_delete=models.CASCADE, verbose_name='Reason for Credit Note')
    credit_amount = models.PositiveIntegerField(default=0)
    adjusted_amount = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey(User, related_name='credit_note_customer_approved_by',
                                    limit_choices_to={'is_staff': True}, null=True, blank=True,
                                    on_delete=models.CASCADE)
    approved_on = models.DateTimeField(null=True, blank=True)
    adjusted_by = models.ForeignKey(User, related_name='credit_note_customer_adjusted_by',
                                    limit_choices_to={'is_staff': True}, null=True, blank=True,
                                    on_delete=models.CASCADE)
    adjusted_on = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejected_on = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User, null=True, blank=True, related_name='credit_note_customer_rejected_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )

    created_by = models.ForeignKey(
        User, null=True, related_name='credit_note_customer_created_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        User, null=True, related_name='credit_note_customer_changed_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Credit Note - Customer (CNC)'

    @property
    def customer_name(self):
        if self.customer:
            return self.customer.get_name()
        return ''

    @property
    def reason_name(self):
        if self.reason:
            return self.reason.name
        return ''

    @property
    def booking_list(self):
        return '\n'.join([booking.booking_id for booking in self.bookings.all()])

    @property
    def invoice_number(self):
        if self.invoice:
            return self.invoice.invoice_number
        return ''

    @property
    def approved_by_user(self):
        if self.approved_by:
            return self.approved_by.username
        return ''

    @property
    def adjusted_by_user(self):
        if self.adjusted_by:
            return self.adjusted_by.username
        return ''

    @property
    def rejected_by_user(self):
        if self.rejected_by:
            return self.rejected_by.username
        return ''

    @property
    def changed_by_user(self):
        if self.changed_by:
            return self.changed_by.username
        return ''

    @property
    def created_by_user(self):
        if self.created_by:
            return self.created_by.username
        return ''

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @property
    def amount_to_be_adjusted(self):
        return self.credit_amount - self.adjusted_amount

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super().save()

    def __str__(self):
        return self.credit_note_number


class DebitNoteCustomer(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    debit_note_number = models.CharField(max_length=16, unique=True)  # editable=False
    bookings = models.ManyToManyField(ManualBooking, verbose_name='Adjusted Bookings', blank=True)
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Sme, null=True, on_delete=models.CASCADE)
    reason = models.ForeignKey(CreditDebitNoteReason, on_delete=models.CASCADE, verbose_name='Reason for Credit Note')
    debit_amount = models.PositiveIntegerField(default=0)
    adjusted_amount = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey(User, related_name='debit_note_customer_approved_by', null=True, blank=True,
                                    on_delete=models.CASCADE)
    approved_on = models.DateTimeField(null=True, blank=True)
    adjusted_by = models.ForeignKey(User, related_name='debit_note_customer_adjusted_by', null=True, blank=True,
                                    on_delete=models.CASCADE)
    adjusted_on = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejected_on = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User, null=True, blank=True, related_name='debit_note_customer_rejected_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User, null=True, related_name='debit_note_customer_created_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        User, null=True, related_name='debit_note_customer_changed_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Debit Note – Customer (DNC)'

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @property
    def amount_to_be_adjusted(self):
        return self.debit_amount - self.adjusted_amount

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super().save()

    def __str__(self):
        return self.debit_note_number


class PendingInwardPaymentCreditDebitNoteCustomer(models.Model):
    cnc = models.ForeignKey(CreditNoteCustomer, null=True, blank=True, on_delete=models.CASCADE)
    dnc = models.ForeignKey(DebitNoteCustomer, null=True, blank=True, on_delete=models.CASCADE)
    pending_inward = models.ForeignKey(PendingInwardPaymentEntry, null=True, blank=True, on_delete=models.CASCADE)
    adjusted_amount = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        User, null=True, related_name='pending_inward_cdn_created_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        User, null=True, related_name='pending_inward_cdn_changed_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)


class CreditNoteSupplier(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    credit_note_number = models.CharField(max_length=16, unique=True)  # editable=False
    bookings = models.ManyToManyField(ManualBooking, verbose_name='Adjusted Bookings')
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.DO_NOTHING)
    broker = models.ForeignKey(Broker, null=True, on_delete=models.CASCADE)
    accounting_supplier = models.ForeignKey(Supplier, related_name="credit_note_supplier", null=True,
                                            on_delete=models.CASCADE,
                                            db_index=False)
    reason = models.ForeignKey(CreditDebitNoteReason, on_delete=models.CASCADE, verbose_name='Reason for Credit Note')
    credit_amount = models.PositiveIntegerField(default=0)
    adjusted_amount = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey(User, related_name='credit_note_supplier_approved_by', null=True, blank=True,
                                    on_delete=models.CASCADE)
    approved_on = models.DateTimeField(null=True, blank=True)
    adjusted_by = models.ForeignKey(User, related_name='credit_note_supplier_adjusted_by', null=True, blank=True,
                                    on_delete=models.CASCADE)
    adjusted_on = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejected_on = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User, null=True, blank=True, related_name='credit_note_supplier_rejected_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User, null=True, related_name='credit_note_supplier_created_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        User, null=True, related_name='credit_note_supplier_changed_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Credit Note – Supplier (CNS)'

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
    def amount_to_be_adjusted(self):
        return self.credit_amount - self.adjusted_amount

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super().save()

    def __str__(self):
        return self.credit_note_number


class DebitNoteSupplier(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    debit_note_number = models.CharField(max_length=16, unique=True)  # editable=False
    bookings = models.ManyToManyField(ManualBooking, blank=True, verbose_name='Adjusted Bookings')
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.DO_NOTHING)
    broker = models.ForeignKey(Broker, null=True, on_delete=models.CASCADE)
    accounting_supplier = models.ForeignKey(Supplier, null=True, on_delete=models.CASCADE, db_index=False)
    reason = models.ForeignKey(CreditDebitNoteReason, on_delete=models.CASCADE, verbose_name='Reason for Credit Note')
    debit_amount = models.PositiveIntegerField(default=0)
    adjusted_amount = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey(User, related_name='debit_note_supplier_approved_by', null=True, blank=True,
                                    on_delete=models.CASCADE)
    approved_on = models.DateTimeField(null=True, blank=True)
    adjusted_by = models.ForeignKey(User, related_name='debit_note_supplier_adjusted_by', null=True, blank=True,
                                    on_delete=models.CASCADE)
    adjusted_on = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejected_on = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User, null=True, blank=True, related_name='debit_note_supplier_rejected_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )

    created_by = models.ForeignKey(
        User, null=True, related_name='debit_note_supplier_created_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        User, null=True, related_name='debit_note_supplier_changed_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Debit Note – Supplier (DNS)'

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
    def amount_to_be_adjusted(self):
        return self.debit_amount - self.adjusted_amount

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super().save()

    def __str__(self):
        return self.debit_note_number


class CreditNoteCustomerDirectAdvance(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    credit_note_number = models.CharField(max_length=17, unique=True)  # editable=False
    bookings = models.ManyToManyField(ManualBooking, verbose_name='Adjusted Bookings')
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Sme, null=True, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, null=True, on_delete=models.CASCADE, db_index=False)
    accounting_supplier = models.ForeignKey(Supplier, related_name='credit_note_customer_da_supplier', null=True,
                                            on_delete=models.CASCADE, db_index=False)
    reason = models.ForeignKey(CreditDebitNoteReason, on_delete=models.CASCADE, verbose_name='Reason for Credit Note')
    credit_amount = models.PositiveIntegerField(default=0)
    adjusted_amount = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey(User, related_name='credit_note_customer_advance_approved_by', null=True,
                                    blank=True, on_delete=models.CASCADE)
    approved_on = models.DateTimeField(null=True, blank=True)
    adjusted_by = models.ForeignKey(User, related_name='credit_note_customer_advance_adjusted_by', null=True,
                                    blank=True, on_delete=models.CASCADE)
    adjusted_on = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(
        User, null=True, related_name='credit_note_customer_advance_created_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    rejected_on = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User, null=True, blank=True, related_name='credit_note_customer_advance_rejected_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        User, null=True, related_name='credit_note_customer_advance_changed_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Credit note – Customer for Direct Adv (CNCA)'

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
    def amount_to_be_adjusted(self):
        return self.credit_amount - self.adjusted_amount

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super().save()

    def __str__(self):
        return self.credit_note_number


class DebitNoteSupplierDirectAdvance(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    debit_note_number = models.CharField(max_length=17, unique=True)  # editable=False
    bookings = models.ManyToManyField(ManualBooking, verbose_name='Adjusted Bookings')
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.DO_NOTHING)
    broker = models.ForeignKey(Broker, null=True, on_delete=models.CASCADE)
    accounting_supplier = models.ForeignKey(Supplier, null=True, on_delete=models.CASCADE)
    customer = models.ForeignKey(Sme, null=True, on_delete=models.CASCADE)
    reason = models.ForeignKey(CreditDebitNoteReason, on_delete=models.CASCADE, verbose_name='Reason for Credit Note')
    debit_amount = models.PositiveIntegerField(default=0)
    adjusted_amount = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey(User, related_name='debit_note_supplier_advance_approved_by', null=True, blank=True,
                                    on_delete=models.CASCADE)
    approved_on = models.DateTimeField(null=True, blank=True)
    adjusted_by = models.ForeignKey(User, related_name='debit_note_supplier_advance_adjusted_by', null=True, blank=True,
                                    on_delete=models.CASCADE)
    adjusted_on = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejected_on = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User, null=True, blank=True, related_name='debit_note_supplier_advance_rejected_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )

    created_by = models.ForeignKey(
        User, null=True, related_name='debit_note_supplier_advance_created_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        User, null=True, related_name='debit_note_supplier_advance_changed_by',
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE
    )
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Debit Note – Supplier for Direct Adv (DNSA)'

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
    def amount_to_be_adjusted(self):
        return self.debit_amount - self.adjusted_amount

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super().save()

    def __str__(self):
        return self.debit_note_number


class DataTablesFilter(models.Model):
    TABLE_NAME_CHOICES = (
        ('MBS', 'Manual Bookings'),
        ('INV', 'Invoices'),
        ('OWP', 'Outward Payments'),
        ('IWP', 'Inward Payments'),
        ('CUS', 'Customers'),
        ('SUP', 'Suppliers'),
        ('OWN', 'Owners'),
        ('VEH', 'Vehicles'),
        ('DRV', 'Driver'),
        ('BAC', 'Bank Account'),
        ('INS', 'Invoice Summary'),
        ('POD', 'POD List'),
        ('OPR', 'Outward Payment Receipt'),
        ('LRD', 'Lorry Receipt'),
        ('GPS', 'GPS Devices'),
        ('CBL', 'Customer Bookings')
    )
    table_name = models.CharField(max_length=15, unique=True, choices=TABLE_NAME_CHOICES)
    criteria = JSONField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='datatables_filter_created_by',
                                   on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, null=True, related_name='datatables_filter_changed_by',
                                   on_delete=models.CASCADE)

    def __str__(self):
        return self.table_name
