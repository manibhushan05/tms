import re
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import serializers, ISO_8601
from rest_framework.validators import UniqueValidator

from api.models import S3Upload
from api.utils import to_int
from owner.models import Owner, FuelCard
from restapi.helper_api import generate_credit_note_customer_serial_number, generate_debit_note_customer_serial_number, \
    generate_credit_note_supplier_serial_number, generate_debit_note_supplier_serial_number, \
    generate_credit_note_customer_direct_advance_serial_number, \
    generate_debit_note_supplier_direct_advance_serial_number, DATE_FORMAT, DATETIME_FORMAT
from restapi.models import BookingStatuses, BookingStatusChain, BookingStatusesMapping
from restapi.serializers.sme import SmeSerializer
from restapi.serializers.utils import AahoOfficeSerializer, CitySerializer
from restapi.service.booking import get_booking_images, access_payment_paid_to_supplier, debit_amount_to_be_adjusted, \
    get_booking_bank_accounts
from restapi.service.validators import validate_gstin, validate_vehicle_number
from sme.models import Sme
from supplier.models import Driver
from supplier.models import Supplier
from supplier.models import Vehicle
from team.models import InvoiceSummary, ManualBooking, LrNumber, RejectedPOD, BookingConsignorConsignee, \
    BookingInsurance, InWardPayment, OutWardPayment, OutWardPaymentBill, Invoice, ToPayInvoice, \
    PendingInwardPaymentEntry, CreditDebitNoteReason, CreditNoteCustomer, DebitNoteCustomer, CreditNoteSupplier, \
    DebitNoteSupplier, CreditNoteCustomerDirectAdvance, DebitNoteSupplierDirectAdvance, BookingStatusColor, \
    DataTablesFilter
from utils.models import City, AahoOffice, VehicleCategory, Bank


class InvoiceSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    ref_number = serializers.CharField(max_length=20,
                                       validators=[UniqueValidator(queryset=InvoiceSummary.objects.all())])
    datetime = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    s3_upload = serializers.PrimaryKeyRelatedField(queryset=S3Upload.objects.all())

    booking = serializers.PrimaryKeyRelatedField(many=True, queryset=ManualBooking.objects.all(), required=False)
    booking_id = serializers.SerializerMethodField()
    lr_numbers = serializers.SerializerMethodField()
    s3_upload_data = serializers.SerializerMethodField()

    def get_booking_id(self, instance):
        return '\n'.join(instance.booking.values_list('booking_id', flat=True))

    def get_lr_numbers(self, instance):
        return '\n'.join(['\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in
                          instance.booking.all()])

    def get_s3_upload_url(self, instance):
        if isinstance(instance.s3_upload, S3Upload):
            return instance.s3_upload.public_url()
        return ''

    def validate_created_by(self, value):
        if isinstance(self.instance, InvoiceSummary) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def get_s3_upload_data(self, instance):
        if isinstance(instance.s3_upload, S3Upload):
            return {
                "url": instance.s3_upload.public_url(),
                "filename": instance.s3_upload.filename
            }
        return {}

    def create(self, validated_data):
        instance = InvoiceSummary.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        InvoiceSummary.objects.filter(id=instance.id).update(**validated_data)
        return InvoiceSummary.objects.get(id=instance.id)


class ManualBookingMISSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True, format=DATETIME_FORMAT)
    shipment_date = serializers.DateField(read_only=True, format=DATE_FORMAT)

    delivery_datetime = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)
    booking_id = serializers.CharField(read_only=True)
    lr_number = serializers.SerializerMethodField()

    customer_placed_order_data = serializers.SerializerMethodField(read_only=True)

    consignor_name = serializers.CharField(read_only=True)
    consignee_name = serializers.CharField(read_only=True)
    customer_to_be_billed_to_data = serializers.SerializerMethodField(read_only=True)
    from_city = serializers.SerializerMethodField()
    to_city = serializers.SerializerMethodField()

    vehicle = serializers.SerializerMethodField()
    lorry_number = serializers.CharField(read_only=True)
    party_rate = serializers.IntegerField(read_only=True)
    charged_weight = serializers.DecimalField(read_only=True, decimal_places=3, max_digits=12)
    freight_revenue = serializers.SerializerMethodField()
    additional_charges_for_company = serializers.DecimalField(read_only=True, decimal_places=3, max_digits=12)
    invoice_remarks_for_additional_charges = serializers.CharField(read_only=True)
    deductions_for_company = serializers.DecimalField(read_only=True, decimal_places=3, max_digits=12)
    invoice_remarks_for_deduction_discount = serializers.CharField(read_only=True)
    total_amount_to_company = serializers.IntegerField(read_only=True)
    refund_amount_due = serializers.SerializerMethodField()
    refund_amount_paid = serializers.SerializerMethodField()
    inward_payments_advance = serializers.SerializerMethodField()
    inward_payments_other = serializers.SerializerMethodField()
    tds_deducted_amount = serializers.IntegerField(read_only=True)
    credit_amount_customer = serializers.SerializerMethodField()
    debit_amount_customer = serializers.SerializerMethodField()
    balance_for_customer = serializers.IntegerField(read_only=True)
    invoice_status = serializers.CharField(read_only=True)
    invoice_number = serializers.CharField(read_only=True)
    billing_invoice_date = serializers.DateField(read_only=True)
    supplier_data = serializers.SerializerMethodField()
    supplier_charged_weight = serializers.CharField(read_only=True)
    supplier_rate = serializers.IntegerField(read_only=True)
    supplier_freight = serializers.IntegerField(read_only=True)
    loading_charge = serializers.IntegerField(read_only=True)
    unloading_charge = serializers.IntegerField(read_only=True)
    detention_charge = serializers.IntegerField(read_only=True)
    other_deduction = serializers.IntegerField(read_only=True)
    remarks_about_deduction = serializers.CharField(read_only=True)
    tds_deducted_supplier = serializers.SerializerMethodField()
    total_amount_to_owner = serializers.IntegerField(read_only=True)
    total_out_ward_amount = serializers.CharField(read_only=True)
    credit_amount_supplier = serializers.SerializerMethodField()
    debit_amount_supplier = serializers.SerializerMethodField()
    debit_amount_supplier_direct_advance = serializers.SerializerMethodField()
    balance_amt_payable = serializers.SerializerMethodField()
    pod_status = serializers.CharField(read_only=True)
    source_office = serializers.SerializerMethodField()
    destination_office = serializers.SerializerMethodField()

    def get_debit_amount_customer(self, instance):
        return sum(
            instance.debitnotecustomer_set.filter(status__in=['partial', 'adjusted']).exclude(deleted=True).values_list(
                'adjusted_amount', flat=True))

    def get_credit_amount_customer(self, instance):
        return sum(instance.creditnotecustomer_set.filter(status__in=['partial', 'adjusted']).exclude(
            deleted=True).values_list(
            'adjusted_amount', flat=True))

    def get_credit_amount_supplier(self, instance):
        return sum(instance.creditnotesupplier_set.filter(status__in=['partial', 'adjusted']).exclude(
            deleted=True).values_list(
            'adjusted_amount', flat=True))

    def get_debit_amount_supplier(self, instance):
        return sum(
            instance.debitnotesupplier_set.filter(status__in=['partial', 'adjusted']).exclude(deleted=True).values_list(
                'adjusted_amount', flat=True))

    def get_vehicle(self, instance):
        if isinstance(instance.supplier_vehicle, Vehicle):
            vehicle = {
                'id': instance.supplier_vehicle.id, 'vehicle_number': instance.supplier_vehicle.number(),
            }
            if isinstance(instance.supplier_vehicle.vehicle_type, VehicleCategory):
                vehicle["vehicle_type"] = instance.supplier_vehicle.vehicle_type.vehicle_type
            else:
                vehicle["vehicle_type"] = None
            return vehicle
        return {'id': -1, 'vehicle_number': None, "vehicle_type": None}

    def get_customer_placed_order_data(self, instance):
        if isinstance(instance.customer_to_be_billed_to, Sme):
            return {'id': instance.customer_to_be_billed_to.id, 'name': instance.customer_to_be_billed_to.get_name(),
                    'code': instance.customer_to_be_billed_to.company_code,
                    'gstin': instance.customer_to_be_billed_to.gstin}
        return {}

    def get_lr_number(self, instance):
        if isinstance(instance, ManualBooking) and len(instance.lr_numbers.values_list()) > 0:
            return '\n'.join(instance.lr_numbers.values_list('lr_number', flat=True))
        return ''

    def get_customer_to_be_billed_to_data(self, instance):
        if isinstance(instance.customer_to_be_billed_to, Sme):
            return {'id': instance.customer_to_be_billed_to.id, 'name': instance.customer_to_be_billed_to.get_name(),
                    'code': instance.customer_to_be_billed_to.company_code}
        return {}

    def get_from_city(self, instance):
        if isinstance(instance, ManualBooking) and isinstance(instance.from_city_fk, City):
            return instance.from_city_fk.name
        return None

    def get_to_city(self, instance):
        if isinstance(instance, ManualBooking) and isinstance(instance.to_city_fk, City):
            return instance.to_city_fk.name
        return None

    def get_freight_revenue(self, instance):
        return instance.customer_freight

    def get_refund_amount_due(self, instance):
        return instance.refundable_due_amount

    def get_refund_amount_paid(self, instance):
        return instance.refundable_paid_amount

    def get_inward_payments_advance(self, instance):
        return instance.adjusted_cnca_amount

    def get_inward_payments_other(self, instance):
        return instance.inward_amount

    def get_tds_deducted_supplier(self, instance):
        return 0

    def get_supplier_data(self, instance):
        if isinstance(instance.booking_supplier, Supplier):
            return {'id': instance.booking_supplier.id, 'name': instance.booking_supplier.name,
                    'phone': instance.booking_supplier.phone, 'code': instance.booking_supplier.code}
        return {}

    def get_debit_amount_supplier_direct_advance(self, instance):
        return instance.adjusted_cnca_amount

    def get_balance_amt_payable(self, instance):
        return instance.balance_for_supplier

    def get_source_office(self, instance):
        if isinstance(instance.source_office, AahoOffice):
            return {'id': instance.source_office.id, 'branch_name': instance.source_office.branch_name}
        return {}

    def get_destination_office(self, instance):
        if isinstance(instance.destination_office, AahoOffice):
            return {'id': instance.destination_office.id, 'branch_name': instance.destination_office.branch_name}
        return {}


class FMSManualBookingSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    booking_id = serializers.CharField(read_only=True)
    shipment_date = serializers.DateField(format=DATE_FORMAT)
    from_city = serializers.CharField(max_length=50)
    to_city = serializers.CharField(max_length=50)
    lorry_number = serializers.CharField(max_length=15, min_length=7)

    pod_status = serializers.ChoiceField(
        allow_null=True, choices=(
            ('pending', 'Pending'), ('unverified', 'Unverified'), ('rejected', 'Rejected'), ('completed', 'Delivered')),
        required=False
    )
    outward_payment_status = serializers.ChoiceField(allow_null=True, choices=(
        ('no_payment_made', 'Nil'), ('partial', 'Partial'), ('complete', 'Full'), ('excess', 'Excess')), required=False)
    supplier_charged_weight = serializers.DecimalField(allow_null=True, decimal_places=3, max_digits=12, required=True)
    supplier_rate = serializers.IntegerField(read_only=True)
    loading_charge = serializers.IntegerField(read_only=True)
    unloading_charge = serializers.IntegerField(read_only=True)
    detention_charge = serializers.IntegerField(read_only=True)
    additional_charges_for_owner = serializers.IntegerField(read_only=True)
    commission = serializers.IntegerField(read_only=True)
    lr_cost = serializers.IntegerField(read_only=True)
    deduction_for_advance = serializers.IntegerField(read_only=True)
    deduction_for_balance = serializers.IntegerField(read_only=True)
    other_deduction = serializers.IntegerField(read_only=True)
    remarks_about_deduction = serializers.CharField(read_only=True)
    total_amount_to_owner = serializers.IntegerField(read_only=True)

    lr_numbers = serializers.SerializerMethodField()
    outward_payments = serializers.SerializerMethodField()
    pod_data = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    paid_amount = serializers.SerializerMethodField()
    balance_amount = serializers.SerializerMethodField()
    latest_payment_date = serializers.SerializerMethodField()
    debit_note_supplier = serializers.SerializerMethodField()
    credit_note_supplier = serializers.SerializerMethodField()
    credit_note_for_direct_advance = serializers.SerializerMethodField()
    vehicle_data = serializers.SerializerMethodField()

    def get_latest_payment_date(self, instance):
        if instance.outward_booking.exclude(payment_date=None).exists():
            return instance.outward_booking.last().payment_date.strftime('%d-%b-%Y')
        return None

    def get_credit_note_for_direct_advance(self, instance):
        return CreditNoteCustomerDirectAdvanceSerializer(many=True,
                                                         instance=instance.creditnotecustomerdirectadvance_set.filter(
                                                             status__in=['partial', 'adjusted'])).data

    def get_credit_note_supplier(self, instance):
        return CreditNoteSupplierSerializer(many=True, instance=instance.creditnotesupplier_set.filter(
            status__in=['partial', 'adjusted'])).data

    def get_debit_note_supplier(self, instance):
        return DebitNoteSupplierSerializer(many=True, instance=instance.debitnotesupplier_set.filter(
            status__in=['partial', 'adjusted'])).data

    def get_amount(self, instance):
        return instance.fms_supplier_amount

    def get_paid_amount(self, instance):
        return instance.fms_supplier_paid_amount

    def get_balance_amount(self, instance):
        return instance.fms_balance_supplier

    def get_pod_data(self, instance):
        from restapi.serializers.file_upload import BasicPODFileSerializer
        return BasicPODFileSerializer(instance.podfile_set.all(), many=True).data

    def get_outward_payments(self, instance):
        return OutWardPaymentSerializer(
            OutWardPayment.objects.filter(
                booking_id=instance).exclude(is_refund_amount=True).exclude(deleted=True), many=True).data

    def get_lr_numbers(self, instance):
        return [{"id": lr.id, "lr_number": lr.lr_number} for lr in instance.lr_numbers.all()]

    def get_vehicle_data(self, instance):
        if isinstance(instance.supplier_vehicle, Vehicle):
            vehicle = {
                'id': instance.supplier_vehicle.id, 'vehicle_number': instance.supplier_vehicle.number(),
            }
            if isinstance(instance.supplier_vehicle.vehicle_type, VehicleCategory):
                vehicle["vehicle_type"] = instance.supplier_vehicle.vehicle_type.vehicle_type
            else:
                vehicle["vehicle_type"] = None
            return vehicle
        return {'id': -1, 'vehicle_number': None, "vehicle_type": None}

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        excluded_fields = [
            'outward_payments', 'credit_note_supplier', 'debit_note_supplier',
            'credit_note_for_direct_advance'
        ]
        for field in excluded_fields:
            kwargs['child'].fields.pop(field)
        return serializers.ListSerializer(*args, **kwargs)


class CustomerManualBookingSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    booking_id = serializers.CharField(read_only=True)
    shipment_date = serializers.DateField(format=DATE_FORMAT)
    from_city = serializers.CharField(max_length=50)
    to_city = serializers.CharField(max_length=50)
    lorry_number = serializers.CharField(max_length=15, min_length=7)

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        excluded_fields = [

        ]
        for field in excluded_fields:
            kwargs['child'].fields.pop(field)
        return serializers.ListSerializer(*args, **kwargs)


class ConnectManualBookingSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    booking_id = serializers.CharField(max_length=35, required=True,
                                       validators=[UniqueValidator(queryset=ManualBooking.objects.all())])

    shipment_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, ISO_8601])

    charged_weight = serializers.DecimalField(allow_null=True, decimal_places=3, max_digits=12, required=True)
    supplier_charged_weight = serializers.DecimalField(allow_null=True, decimal_places=3, max_digits=12, required=True)
    party_rate = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=0, required=False)
    supplier_rate = serializers.IntegerField(
        allow_null=True, max_value=2147483647, min_value=0, required=True)
    loading_charge = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=0,
                                              required=False)
    unloading_charge = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=0,
                                                required=False)
    detention_charge = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=0,
                                                required=False)
    additional_charges_for_company = serializers.IntegerField(allow_null=True,
                                                              label='Additional Charges/Deductions for Company (+/-)',
                                                              max_value=2147483647, min_value=0,
                                                              required=False)
    remarks_about_additional_charges = serializers.CharField(allow_null=True, required=False)
    additional_charges_for_owner = serializers.IntegerField(allow_null=True, max_value=2147483647,
                                                            min_value=0, required=False)
    note_for_additional_owner_charges = serializers.CharField(allow_null=True, required=False)
    commission = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=0, required=False)
    lr_cost = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=0, required=False)
    deduction_for_advance = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=0,
                                                     required=False)
    deduction_for_balance = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=0,
                                                     required=False)
    other_deduction = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=0,
                                               required=False)
    remarks_about_deduction = serializers.CharField(allow_null=True, required=False)
    deductions_for_company = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=0,
                                                      required=False)

    pod_status = serializers.ChoiceField(
        allow_null=True, choices=(
            ('pending', 'Pending'), ('unverified', 'Unverified'), ('rejected', 'Rejected'), ('completed', 'Delivered')),
        required=False
    )

    booking_status = serializers.ChoiceField(choices=(
        ('confirmed', 'Confirmed'), ('delivered', 'Delivered'), ('closed', 'Closed'), ('cancelled', 'Cancelled')),
        required=False)
    source_office_data = serializers.SerializerMethodField()
    destination_office_data = serializers.SerializerMethodField()
    customer_placed_order_data = serializers.SerializerMethodField()
    customer_to_be_billed_to_data = serializers.SerializerMethodField()
    supplier_data = serializers.SerializerMethodField()
    owner_data = serializers.SerializerMethodField()
    driver_data = serializers.SerializerMethodField()
    from_city_fk_data = serializers.SerializerMethodField()
    to_city_fk_data = serializers.SerializerMethodField()
    vehicle_data = serializers.SerializerMethodField()
    vehicle_category_data = serializers.SerializerMethodField()
    lr_numbers = serializers.SerializerMethodField()

    inward_payments = serializers.SerializerMethodField()
    outward_payments = serializers.SerializerMethodField()
    invoices = serializers.SerializerMethodField()
    pod_data = serializers.SerializerMethodField()
    supplier_freight = serializers.SerializerMethodField()
    customer_freight = serializers.SerializerMethodField()
    status_color_code = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    outward_amount = serializers.SerializerMethodField()
    inward_amount = serializers.SerializerMethodField()
    supplier_amount = serializers.SerializerMethodField()
    customer_amount = serializers.SerializerMethodField()
    amount_received_from_customer = serializers.SerializerMethodField()
    amount_paid_to_supplier = serializers.SerializerMethodField()
    balance_for_customer = serializers.SerializerMethodField()
    balance_for_supplier = serializers.SerializerMethodField()
    tds_amount_customer = serializers.SerializerMethodField()
    debit_amount_supplier = serializers.SerializerMethodField()
    credit_amount_supplier = serializers.SerializerMethodField()
    debit_amount_customer = serializers.SerializerMethodField()
    credit_amount_customer = serializers.SerializerMethodField()
    credit_note_customer = serializers.SerializerMethodField()
    credit_note_supplier = serializers.SerializerMethodField()
    debit_note_customer = serializers.SerializerMethodField()
    debit_note_supplier = serializers.SerializerMethodField()
    credit_note_for_direct_advance = serializers.SerializerMethodField()

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        excluded_fields = [
            'inward_payments', 'outward_payments', 'credit_amount_customer', 'debit_amount_customer',
            'credit_amount_supplier', 'debit_amount_supplier', 'tds_amount_customer',
            'balance_for_supplier', 'balance_for_customer', 'amount_paid_to_supplier',
            'amount_received_from_customer', 'customer_amount', 'supplier_amount', 'inward_amount',
            'outward_amount', 'documents', 'status_color_code', 'customer_freight', 'supplier_freight',
            'credit_note_customer', 'credit_note_supplier', 'debit_note_customer',
            'debit_note_supplier', 'credit_note_for_direct_advance'
        ]
        for field in excluded_fields:
            kwargs['child'].fields.pop(field)
        return serializers.ListSerializer(*args, **kwargs)

    def get_credit_note_for_direct_advance(self, instance):
        return CreditNoteCustomerDirectAdvanceSerializer(many=True,
                                                         instance=instance.creditnotecustomerdirectadvance_set.all()).data

    def get_credit_note_customer(self, instance):
        return CreditNoteCustomerSerializer(many=True, instance=instance.creditnotecustomer_set.all()).data

    def get_credit_note_supplier(self, instance):
        return CreditNoteSupplierSerializer(many=True, instance=instance.creditnotesupplier_set.all()).data

    def get_debit_note_customer(self, instance):
        return DebitNoteCustomerSerializer(many=True, instance=instance.debitnotecustomer_set.all()).data

    def get_debit_note_supplier(self, instance):
        return DebitNoteSupplierSerializer(many=True, instance=instance.debitnotesupplier_set.all()).data

    def get_excess_payment_paid_to_supplier(self, instance):
        if isinstance(instance.accounting_supplier, Supplier):
            supplier_excess_amount, supplier_excess_amount_msg = access_payment_paid_to_supplier(
                supplier=instance.accounting_supplier)
            return {'supplier_excess_amount': supplier_excess_amount,
                    'supplier_excess_amount_msg': supplier_excess_amount_msg}
        return {'supplier_excess_amount': 0,
                'supplier_excess_amount_msg': None}

    def get_debit_amount_to_be_adjusted(self, instance):
        if isinstance(instance.accounting_supplier, Supplier):
            debit_amount = debit_amount_to_be_adjusted(supplier=instance.accounting_supplier)
            return {'debit_amount_to_be_adjusted': debit_amount}
        return {'debit_amount_to_be_adjusted': 0}

    def get_refundable_paid_amount(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.refundable_paid_amount
        return None

    def get_outward_amount(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.outward_amount
        return None

    def get_inward_amount(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.inward_amount
        return None

    def get_credit_amount_customer(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.credit_amount_customer
        return None

    def get_debit_amount_customer(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.debit_amount_customer
        return None

    def get_credit_amount_supplier(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.credit_amount_supplier
        return None

    def get_debit_amount_supplier(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.debit_amount_supplier
        return None

    def get_tds_amount_customer(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.tds_amount_customer
        return None

    def get_balance_for_supplier(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.balance_for_supplier
        return None

    def get_balance_for_customer(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.balance_for_customer
        return None

    def get_supplier_amount(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.supplier_amount
        return None

    def get_customer_amount(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.customer_amount
        return None

    def get_amount_received_from_customer(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.amount_received_from_customer
        return None

    def get_amount_paid_to_supplier(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.amount_paid_to_supplier
        return None

    def get_documents(self, instance):
        if isinstance(instance, ManualBooking):
            return get_booking_images(instance)
        return []

    def get_status_color_code(self, instance):
        if isinstance(instance.booking_status_color, BookingStatusColor) and instance.booking_status_color.color_code:
            return instance.booking_status_color.color_code
        return '#000000'

    def get_customer_freight(self, instance):
        return instance.customer_freight

    def get_supplier_freight(self, instance):
        return instance.supplier_freight

    def get_pod_data(self, instance):
        from restapi.serializers.file_upload import BasicPODFileSerializer
        return BasicPODFileSerializer(instance.podfile_set.all(), many=True).data

    def get_inward_payments(self, instance):
        return InWardPaymentSerializer(InWardPayment.objects.filter(booking_id=instance), many=True).data

    def get_outward_payments(self, instance):
        return OutWardPaymentSerializer(OutWardPayment.objects.filter(booking_id=instance), many=True).data

    def get_invoices(self, instance):
        return InvoiceSerializer(Invoice.objects.filter(bookings=instance).distinct(), many=True).data

    def get_lr_numbers(self, instance):
        return [{"id": lr.id, "lr_number": lr.lr_number} for lr in instance.lr_numbers.all()]

    @staticmethod
    def get_source_office_data(instance):
        if isinstance(instance.source_office, AahoOffice):
            return {'id': instance.source_office.id, 'branch_name': instance.source_office.branch_name}
        return {'id': -1, 'branch_name': None}

    @staticmethod
    def get_destination_office_data(instance):
        if isinstance(instance.destination_office, AahoOffice):
            return {'id': instance.destination_office.id, 'branch_name': instance.destination_office.branch_name}
        return {'id': -1, 'branch_name': None}

    @staticmethod
    def get_customer_placed_order_data(instance):
        if isinstance(instance.company, Sme):
            return {'id': instance.company.id, 'name': instance.company.get_name(),
                    'code': instance.company.company_code, 'gstin': instance.company.gstin}
        return {'id': None, 'name': None, 'code': None, 'gstin': None}

    @staticmethod
    def get_customer_to_be_billed_to_data(obj):
        if isinstance(obj.customer_to_be_billed_to, Sme):
            return {'id': obj.customer_to_be_billed_to.id, 'name': obj.customer_to_be_billed_to.get_name(),
                    'code': obj.customer_to_be_billed_to.company_code, 'gstin': obj.customer_to_be_billed_to.gstin,
                    'address': obj.customer_to_be_billed_to.customer_address, 'pin': obj.customer_to_be_billed_to.pin,
                    'city': {
                        'name': obj.customer_to_be_billed_to.city.name if obj.customer_to_be_billed_to.city else None,
                        'id': obj.customer_to_be_billed_to.city.id if obj.customer_to_be_billed_to.city else -1},
                    'credit_period': obj.customer_to_be_billed_to.credit_period}
        return {'id': -1, 'name': None, 'pin': None, 'code': None, 'gstin': None, 'address': None,
                'city': {'name': None, 'id': -1}, 'credit_period': None}

    @staticmethod
    def get_supplier_data(instance):
        if isinstance(instance.booking_supplier, Supplier):
            return {'id': instance.booking_supplier.id, 'name': instance.booking_supplier.name,
                    'phone': instance.booking_supplier.phone, 'code': instance.booking_supplier.code}
        return {'id': -1, 'name': None, 'phone': None, 'code': None}

    @staticmethod
    def get_owner_data(instance):
        if isinstance(instance.owner_supplier, Supplier):
            return {'id': instance.owner_supplier.id, 'name': instance.owner_supplier.name,
                    'phone': instance.owner_supplier.phone}
        return {'id': -1, 'name': None, 'phone': None}

    @staticmethod
    def get_driver_data(instance):
        if isinstance(instance.driver_supplier, Driver):
            return {'id': instance.driver_supplier.id, 'name': instance.driver_supplier.name,
                    'phone': instance.driver_supplier.phone}
        return {'id': -1, 'name': None, 'phone': None}

    @staticmethod
    def get_consignor_city_fk_data(instance):
        if isinstance(instance.consignor_city_fk, City):
            return {'id': instance.consignor_city_fk.id, 'name': instance.consignor_city_fk.name,
                    'code': instance.consignor_city_fk.code}
        return {'id': -1, 'name': None, 'code': None}

    @staticmethod
    def get_consignee_city_fk_data(instance):
        if isinstance(instance.consignee_city_fk, City):
            return {'id': instance.consignee_city_fk.id, 'name': instance.consignee_city_fk.name,
                    'code': instance.consignee_city_fk.code}
        return {'id': -1, 'name': None, 'code': None}

    @staticmethod
    def get_from_city_fk_data(instance):
        if isinstance(instance.from_city_fk, City):
            return {'id': instance.from_city_fk.id, 'name': instance.from_city_fk.name,
                    'code': instance.from_city_fk.code}
        return {'id': -1, 'name': None, 'code': None}

    @staticmethod
    def get_to_city_fk_data(instance):
        if isinstance(instance.to_city_fk, City):
            return {'id': instance.to_city_fk.id, 'name': instance.to_city_fk.name,
                    'code': instance.to_city_fk.code}
        return {'id': -1, 'name': None, 'code': None}

    @staticmethod
    def get_vehicle_data(instance):
        if isinstance(instance.supplier_vehicle, Vehicle):
            vehicle = {
                'id': instance.supplier_vehicle.id, 'vehicle_number': instance.supplier_vehicle.number(),
            }
            if isinstance(instance.supplier_vehicle.vehicle_type, VehicleCategory):
                vehicle["vehicle_type"] = instance.supplier_vehicle.vehicle_type.vehicle_type
            else:
                vehicle["vehicle_type"] = None
            return vehicle
        return {'id': -1, 'vehicle_number': None, "vehicle_type": None}

    @staticmethod
    def get_vehicle_category_data(instance):
        if isinstance(instance.vehicle_category, VehicleCategory):
            return {'id': instance.vehicle_category.id, 'type': instance.vehicle_category.vehicle_category}
        return {}

    def validate_created_by(self, value):
        if isinstance(self.instance, ManualBooking) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def validate_lorry_number(self, value):
        vehicle_number_pattern = re.compile('^[a-z]{2}\d{1,2}[a-z]{0,3}\d{4}$')
        if not vehicle_number_pattern.match(value):
            raise serializers.ValidationError({"vehicle_number": "Vehicle Number is not valid"})
        return value


class TinyManualBookingSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    booking_id = serializers.CharField(read_only=True)
    lr_numbers = serializers.SerializerMethodField()

    def get_lr_numbers(self, instance):
        return ', '.join(instance.lr_numbers.values_list('lr_number', flat=True))

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ManualBookingSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    booking_id = serializers.CharField(max_length=35, required=True,
                                       validators=[UniqueValidator(queryset=ManualBooking.objects.all())])
    company_code = serializers.CharField(label='Company Code', max_length=3, min_length=3)
    consignor_name = serializers.CharField(allow_null=True, max_length=100, required=False)
    consignor_address = serializers.CharField(allow_null=True, max_length=255, required=False)
    consignor_city = serializers.CharField(allow_null=True, max_length=35, required=False)
    consignor_pin = serializers.CharField(allow_null=True, max_length=6, required=False)
    consignor_phone = serializers.CharField(allow_null=True, max_length=20, required=False)
    consignor_cst_tin = serializers.CharField(allow_null=True, max_length=35, required=False)
    consignor_gstin = serializers.CharField(allow_null=True, min_length=15, max_length=15, required=False)
    consignee_name = serializers.CharField(allow_null=True, max_length=100, required=False)
    consignee_address = serializers.CharField(allow_null=True, max_length=400, required=False)
    consignee_city = serializers.CharField(allow_null=True, max_length=35, required=False)
    consignee_pin = serializers.CharField(allow_null=True, max_length=6, required=False)
    consignee_phone = serializers.CharField(allow_null=True, max_length=20, required=False)
    consignee_cst_tin = serializers.CharField(allow_null=True, max_length=50, required=False)
    consignee_gstin = serializers.CharField(allow_null=True, max_length=50, required=False)
    billing_type = serializers.ChoiceField(choices=(
        ('T.B.B.', 'T.B.B.'), ('To Pay', 'To Pay'), ('Paid', 'Paid'), ('contract', 'Contract')))
    gst_liability = serializers.ChoiceField(allow_null=True, choices=(
        ('consignor', 'Consignor'), ('consignee', 'Consignee'), ('carrier', 'Carrier'), ('exempted', 'Exempted')))
    liability_of_service_tax = serializers.CharField(allow_null=True, max_length=40, required=False)
    shipment_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, ISO_8601])
    delivery_datetime = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT,
                                                  input_formats=[DATE_FORMAT, ISO_8601])
    from_city = serializers.CharField(max_length=50)
    to_city = serializers.CharField(max_length=50)
    lorry_number = serializers.CharField(max_length=15, min_length=7)
    type_of_vehicle = serializers.CharField(allow_null=True, max_length=70, required=True)
    road_permit_number = serializers.CharField(allow_null=True, max_length=255, required=False)
    party_invoice_number = serializers.CharField(allow_null=True, max_length=255, required=False)
    party_invoice_date = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                               input_formats=[DATE_FORMAT, ISO_8601])
    party_invoice_amount = serializers.CharField(allow_null=True, max_length=100, required=False)
    number_of_package = serializers.CharField(allow_null=True, max_length=30, required=False)
    material = serializers.CharField(allow_null=True, max_length=500, required=False)
    loaded_weight = serializers.DecimalField(allow_null=True, decimal_places=3, max_digits=12, required=False)
    delivered_weight = serializers.DecimalField(allow_null=True, decimal_places=3, max_digits=12, required=False)
    charged_weight = serializers.DecimalField(allow_null=True, decimal_places=3, max_digits=12, required=True)
    supplier_charged_weight = serializers.DecimalField(allow_null=True, decimal_places=3, max_digits=12, required=True)
    party_rate = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0, required=False)
    supplier_rate = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0,
                                             required=True)
    is_insured = serializers.BooleanField(required=False)
    insurance_provider = serializers.CharField(allow_null=True, max_length=200, required=False)
    insurance_policy_number = serializers.CharField(allow_null=True, max_length=200, required=False)
    insured_amount = serializers.DecimalField(allow_null=True, decimal_places=2, max_digits=30, required=False)
    insurance_date = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                           input_formats=[DATE_FORMAT, ISO_8601])
    insurance_risk = serializers.CharField(allow_null=True, max_length=200, required=False)
    driver_name = serializers.CharField(max_length=255, required=True)
    driver_phone = serializers.CharField(max_length=255, required=True)
    driver_dl_number = serializers.CharField(allow_null=True, max_length=255, required=True)
    driver_dl_validity = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                               input_formats=[DATE_FORMAT, ISO_8601])
    truck_broker_owner_name = serializers.CharField(allow_null=True, allow_blank=True, label='Truck Owner/Broker name',
                                                    max_length=100, required=False)
    truck_broker_owner_phone = serializers.CharField(allow_null=True, allow_blank=True,
                                                     label='Truck Owner/Broker Phone Number',
                                                     max_length=25)
    truck_owner_name = serializers.CharField(allow_null=True, allow_blank=True, label='Truck Owner name',
                                             max_length=100, required=False)
    truck_owner_phone = serializers.CharField(allow_null=True, allow_blank=True, label='Truck Owner Phone Number',
                                              max_length=25,
                                              required=False)
    loading_points = serializers.CharField(allow_null=True, max_length=255, required=False)
    unloading_points = serializers.CharField(allow_null=True, max_length=255, required=False)
    total_in_ward_amount = serializers.DecimalField(allow_null=True, decimal_places=2, max_digits=30, required=False)
    total_out_ward_amount = serializers.DecimalField(allow_null=True, decimal_places=2, max_digits=30, required=False)
    total_amount_to_company = serializers.IntegerField(allow_null=True, max_value=1000000, required=False)
    advance_amount_from_company = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0,
                                                           required=False)
    refund_amount = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0,
                                             required=False)
    total_amount_to_owner = serializers.IntegerField(allow_null=True, max_value=1000000, required=False)
    loading_charge = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0,
                                              required=False)
    unloading_charge = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0,
                                                required=False)
    detention_charge = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0,
                                                required=False)
    additional_charges_for_company = serializers.IntegerField(allow_null=True,
                                                              label='Additional Charges/Deductions for Company (+/-)',
                                                              max_value=1000000, min_value=0,
                                                              required=False)
    remarks_about_additional_charges = serializers.CharField(allow_null=True, required=False)
    additional_charges_for_owner = serializers.IntegerField(allow_null=True, max_value=1000000,
                                                            min_value=0, required=False)
    note_for_additional_owner_charges = serializers.CharField(allow_null=True, required=False)
    commission = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0, required=False)
    lr_cost = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0, required=False)
    deduction_for_advance = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0,
                                                     required=False)
    deduction_for_balance = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0,
                                                     required=False)
    other_deduction = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0,
                                               required=False)
    remarks_about_deduction = serializers.CharField(allow_null=True, required=False)
    deductions_for_company = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0,
                                                      required=False)
    to_be_billed_to = serializers.CharField(allow_null=True, max_length=200, required=False)
    invoice_number = serializers.CharField(allow_null=True, label='Invoice Number', max_length=50,
                                           required=False)
    billing_address = serializers.CharField(allow_null=True, max_length=300, required=False)
    billing_contact_number = serializers.CharField(allow_null=True, max_length=50, required=False)
    billing_invoice_date = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                                 input_formats=[DATE_FORMAT, ISO_8601])
    invoice_remarks_for_additional_charges = serializers.CharField(allow_null=True, required=False,
                                                                   style={'base_template': 'textarea.html'})
    invoice_remarks_for_deduction_discount = serializers.CharField(allow_null=True, required=False,
                                                                   style={'base_template': 'textarea.html'})
    tds_deducted_amount = serializers.IntegerField(allow_null=True, max_value=1000000, min_value=0,
                                                   required=False)
    pod_date = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT,
                                         input_formats=[DATE_FORMAT, '%Y-%m-%d', ISO_8601])
    pod_status = serializers.ChoiceField(
        allow_null=True, choices=(
            ('pending', 'Pending'), ('unverified', 'Unverified'), ('rejected', 'Rejected'), ('completed', 'Delivered'),
            ('not_required', 'Not Required')),
        required=False
    )
    outward_payment_status = serializers.ChoiceField(allow_null=True, choices=(
        ('no_payment_made', 'Nil'), ('partial', 'Partial'), ('complete', 'Full'), ('excess', 'Excess')), required=False)
    inward_payment_status = serializers.ChoiceField(allow_null=True, choices=(
        ('no_payment', 'Nil'), ('partial_received', 'Partial'), ('full_received', 'Full'), ('excess', 'Excess')),
                                                    required=False)
    invoice_status = serializers.ChoiceField(allow_null=True, choices=(
        ('no_invoice', 'NoInvoice'), ('invoice_raised', 'InvoiceRaised'), ('invoice_sent', 'InvoiceSent'),
        ('invoice_confirmed', 'InvoiceConfirmed')),
                                             required=False)
    comments = serializers.CharField(allow_null=True, required=False
                                     )
    remarks_advance_from_company = serializers.CharField(allow_null=True, required=False,
                                                         style={'base_template': 'textarea.html'})
    tds_certificate_status = serializers.ChoiceField(allow_null=True, choices=(('y', 'Yes'), ('n', 'No')),
                                                     required=False)
    booking_status = serializers.ChoiceField(choices=(
        ('confirmed', 'Confirmed'), ('delivered', 'Delivered'), ('closed', 'Closed'), ('cancelled', 'Cancelled')),
        required=False)
    is_advance = serializers.ChoiceField(allow_null=True, choices=(('no', 'No'), ('yes', 'Yes')), required=False)
    is_print_payment_mode_instruction = serializers.BooleanField(required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    source_office = serializers.PrimaryKeyRelatedField(write_only=True, queryset=AahoOffice.objects.all())
    source_office_data = serializers.SerializerMethodField()

    destination_office = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=AahoOffice.objects.exclude(deleted=True))
    destination_office_data = serializers.SerializerMethodField()

    company = serializers.PrimaryKeyRelatedField(
        write_only=True, label='Customer who has placed order ', queryset=Sme.objects.all())
    customer_placed_order_data = serializers.SerializerMethodField()
    customer_to_be_billed_to = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True, label='Customer who will make payment',
        queryset=Sme.objects.all(), required=True
    )
    customer_to_be_billed_to_data = serializers.SerializerMethodField()
    supplier = serializers.PrimaryKeyRelatedField(source='booking_supplier', write_only=True, allow_null=True,
                                                  required=False,
                                                  queryset=Supplier.objects.all())
    accounting_supplier = serializers.PrimaryKeyRelatedField(write_only=True, allow_null=True, required=False,
                                                             queryset=Supplier.objects.all())
    owner_supplier = serializers.PrimaryKeyRelatedField(write_only=True, allow_null=True, required=False,
                                                        queryset=Supplier.objects.all())
    supplier_data = serializers.SerializerMethodField()
    accounting_supplier_data = serializers.SerializerMethodField()
    owner = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True, queryset=Owner.objects.all(), required=False)
    owner_data = serializers.SerializerMethodField()
    driver_supplier = serializers.PrimaryKeyRelatedField(
        write_only=True, required=False, allow_null=True, label='Driver Name', queryset=Driver.objects.all())
    driver = serializers.PrimaryKeyRelatedField(
        write_only=True, required=False, allow_null=True, label='Driver Name', queryset=Driver.objects.all())
    driver_data = serializers.SerializerMethodField()
    consignor_city_fk = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True, queryset=City.objects.all(), required=False)
    consignor_city_fk_data = serializers.SerializerMethodField()
    consignee_city_fk = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True, queryset=City.objects.all(), required=False)
    consignee_city_fk_data = serializers.SerializerMethodField()
    from_city_fk = serializers.PrimaryKeyRelatedField(write_only=True, queryset=City.objects.all())
    from_city_fk_data = serializers.SerializerMethodField()
    to_city_fk = serializers.PrimaryKeyRelatedField(write_only=True, queryset=City.objects.all())
    to_city_fk_data = serializers.SerializerMethodField()
    vehicle = serializers.PrimaryKeyRelatedField(write_only=True, source='supplier_vehicle',
                                                 queryset=Vehicle.objects.all())
    vehicle_data = serializers.SerializerMethodField()
    vehicle_category = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True, queryset=VehicleCategory.objects.all(), required=False)
    vehicle_category_data = serializers.SerializerMethodField()
    invoice_summary = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=InvoiceSummary.objects.all(), required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    lr_numbers = serializers.SerializerMethodField()
    inward_payments = serializers.SerializerMethodField()
    outward_payments = serializers.SerializerMethodField()
    invoices = serializers.SerializerMethodField()
    pod_data = serializers.SerializerMethodField()
    supplier_freight = serializers.SerializerMethodField()
    customer_freight = serializers.SerializerMethodField()
    status_color_code = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    bank_accounts = serializers.SerializerMethodField()
    outward_amount = serializers.SerializerMethodField()
    inward_amount = serializers.SerializerMethodField()
    supplier_amount = serializers.SerializerMethodField()
    customer_amount = serializers.SerializerMethodField()
    amount_received_from_customer = serializers.SerializerMethodField()
    amount_paid_to_supplier = serializers.SerializerMethodField()
    balance_for_customer = serializers.SerializerMethodField()
    balance_for_supplier = serializers.SerializerMethodField()
    tds_amount_customer = serializers.SerializerMethodField()
    debit_amount_supplier = serializers.SerializerMethodField()
    credit_amount_supplier = serializers.SerializerMethodField()
    debit_amount_customer = serializers.SerializerMethodField()
    credit_amount_customer = serializers.SerializerMethodField()
    refundable_paid_amount = serializers.SerializerMethodField()

    credit_note_customer = serializers.SerializerMethodField()
    credit_note_supplier = serializers.SerializerMethodField()
    debit_note_customer = serializers.SerializerMethodField()
    debit_note_supplier = serializers.SerializerMethodField()
    credit_note_for_direct_advance = serializers.SerializerMethodField()
    excess_payment_paid_to_supplier = serializers.SerializerMethodField()
    debit_amount_to_be_adjusted = serializers.SerializerMethodField()
    valid_s3_lr_doc_url = serializers.SerializerMethodField()
    decide_account_supplier = serializers.SerializerMethodField()

    def validate_consignor_gstin(self, value):
        if value and not validate_gstin(value):
            raise serializers.ValidationError("Not a valid gstin")
        return value

    def validate_consignee_gstin(self, value):
        if value and not validate_gstin(value):
            raise serializers.ValidationError("Not a valid gstin")
        return value

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        excluded_fields = [
            'credit_note_for_direct_advance', 'debit_note_supplier', 'debit_note_customer', 'credit_note_supplier',
            'credit_note_customer', 'refundable_paid_amount', 'credit_amount_customer', 'debit_amount_customer',
            'credit_amount_supplier', 'debit_amount_supplier', 'tds_amount_customer',
            'amount_paid_to_supplier', 'amount_received_from_customer', 'customer_amount',
            'supplier_amount', 'inward_amount', 'outward_amount', 'documents', 'bank_accounts', 'customer_freight',
            'supplier_freight',
            'pod_data', 'invoices', 'outward_payments', 'inward_payments', 'changed_by', 'created_by',
            'invoice_summary', 'vehicle_category', 'vehicle',
            'to_city_fk', 'from_city_fk', 'consignee_city_fk_data',
            'consignee_city_fk', 'consignor_city_fk_data', 'consignor_city_fk', 'driver_data', 'driver', 'owner_data',
            'owner', 'supplier', 'destination_office', 'is_advance',
            'is_print_payment_mode_instruction', 'customer_to_be_billed_to', 'company', 'source_office', 'created_on',
            'updated_on', 'deleted', 'deleted_on', 'to_be_billed_to', 'billing_address', 'billing_contact_number',
            'invoice_remarks_for_additional_charges', 'invoice_remarks_for_deduction_discount', 'pod_date', 'comments',
            'remarks_advance_from_company', 'tds_certificate_status', 'booking_status', 'loading_points',
            'unloading_points', 'advance_amount_from_company', 'loading_charge', 'unloading_charge', 'detention_charge',
            'additional_charges_for_company', 'remarks_about_additional_charges', 'additional_charges_for_owner',
            'note_for_additional_owner_charges', 'commission', 'lr_cost', 'deduction_for_advance',
            'deduction_for_balance', 'other_deduction', 'remarks_about_deduction', 'deductions_for_company',
            'insurance_provider', 'insurance_policy_number', 'insured_amount', 'insurance_date', 'insurance_risk',
            'driver_name', 'driver_phone', 'driver_dl_number', 'driver_dl_validity', 'truck_broker_owner_phone',
            'truck_owner_name', 'truck_owner_phone', 'is_insured', 'billing_type', 'gst_liability',
            'liability_of_service_tax', 'type_of_vehicle', 'road_permit_number', 'party_invoice_number',
            'party_invoice_date', 'party_invoice_amount', 'number_of_package', 'material', 'loaded_weight',
            'delivered_weight', 'company_code', 'consignor_name', 'consignor_address', 'consignor_city',
            'consignor_pin', 'consignor_phone', 'consignor_cst_tin', 'consignor_gstin', 'consignee_name',
            'consignee_address', 'consignee_city', 'consignee_pin', 'consignee_phone', 'valid_s3_lr_doc_url',
            'consignee_cst_tin', 'consignee_gstin', 'excess_payment_paid_to_supplier', 'decide_account_supplier']
        for field in excluded_fields:
            kwargs['child'].fields.pop(field)
        return serializers.ListSerializer(*args, **kwargs)

    def get_bank_accounts(self, instance):
        return get_booking_bank_accounts(instance)

    def get_decide_account_supplier(self, instance):
        booking_supplier = instance.booking_supplier
        owner_supplier = instance.owner_supplier
        return {
            'status': 'success' if isinstance(instance, ManualBooking) else 'error',
            'booking_supplier': {
                'supplier_data': {'id': booking_supplier.id, 'name': booking_supplier.name,
                                  'phone': booking_supplier.phone,
                                  'code': booking_supplier.code} if isinstance(
                    booking_supplier, Supplier) else {'id': -1, 'name': None, 'phone': None, 'code': None},
                'valid_pan': True if isinstance(instance.booking_supplier,
                                                Supplier) and booking_supplier.supplier_files.filter(
                    document_category='PAN').exists() else False,
                'valid_dec': True if isinstance(instance.booking_supplier,
                                                Supplier) and booking_supplier.supplier_files.filter(
                    document_category='DEC').exists() else False,
            },
            'owner_supplier': {
                'supplier_data': {'id': owner_supplier.id, 'name': owner_supplier.name, 'phone': owner_supplier.phone,
                                  'code': owner_supplier.code} if isinstance(
                    owner_supplier, Supplier) else {'id': -1, 'name': None, 'phone': None, 'code': None},
                'valid_pan': True if isinstance(instance.owner_supplier,
                                                Supplier) and owner_supplier.supplier_files.filter(
                    document_category='PAN').exists() else False,
                'valid_dec': True if isinstance(instance.owner_supplier,
                                                Supplier) and owner_supplier.supplier_files.filter(
                    document_category='DEC').exists() else False,
            },
        }

    def get_valid_s3_lr_doc_url(self, instance):
        if isinstance(instance, ManualBooking) and instance.manualbookings3upload_set.filter(is_valid=True).exclude(
                s3_upload=None).exists():
            return instance.manualbookings3upload_set.filter(is_valid=True).exclude(
                s3_upload=None).last().s3_upload.public_url()
        return None

    def get_excess_payment_paid_to_supplier(self, instance):
        if isinstance(instance.accounting_supplier, Supplier):
            supplier_excess_amount, supplier_excess_amount_msg = access_payment_paid_to_supplier(
                supplier=instance.accounting_supplier)
            return {'supplier_excess_amount': supplier_excess_amount,
                    'supplier_excess_amount_msg': supplier_excess_amount_msg}
        return {'supplier_excess_amount': 0,
                'supplier_excess_amount_msg': None}

    def get_debit_amount_to_be_adjusted(self, instance):
        if isinstance(instance.accounting_supplier, Supplier):
            debit_amount = debit_amount_to_be_adjusted(supplier=instance.accounting_supplier)
            return {'debit_amount_to_be_adjusted': debit_amount}
        return {'debit_amount_to_be_adjusted': 0}

    def get_credit_note_for_direct_advance(self, instance):
        return CreditNoteCustomerDirectAdvanceSerializer(many=True,
                                                         instance=instance.creditnotecustomerdirectadvance_set.all()).data

    def get_credit_note_customer(self, instance):
        return CreditNoteCustomerSerializer(many=True, instance=instance.creditnotecustomer_set.all()).data

    def get_credit_note_supplier(self, instance):
        return CreditNoteSupplierSerializer(many=True, instance=instance.creditnotesupplier_set.all()).data

    def get_debit_note_customer(self, instance):
        return DebitNoteCustomerSerializer(many=True, instance=instance.debitnotecustomer_set.all()).data

    def get_debit_note_supplier(self, instance):
        return DebitNoteSupplierSerializer(many=True, instance=instance.debitnotesupplier_set.all()).data

    def get_refundable_paid_amount(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.refundable_paid_amount
        return None

    def get_outward_amount(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.outward_amount
        return None

    def get_inward_amount(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.inward_amount
        return None

    def get_credit_amount_customer(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.credit_amount_customer
        return None

    def get_debit_amount_customer(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.debit_amount_customer
        return None

    def get_credit_amount_supplier(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.credit_amount_supplier
        return None

    def get_debit_amount_supplier(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.debit_amount_supplier
        return None

    def get_tds_amount_customer(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.tds_amount_customer
        return None

    def get_balance_for_supplier(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.balance_for_supplier
        return None

    def get_balance_for_customer(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.balance_for_customer
        return None

    def get_supplier_amount(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.supplier_amount
        return None

    def get_customer_amount(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.customer_amount
        return None

    def get_amount_received_from_customer(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.amount_received_from_customer
        return None

    def get_amount_paid_to_supplier(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.amount_paid_to_supplier
        return None

    def get_documents(self, instance):
        if isinstance(instance, ManualBooking):
            return get_booking_images(instance)
        return []

    def get_status_color_code(self, instance):
        if isinstance(instance.booking_status_color, BookingStatusColor) and instance.booking_status_color.color_code:
            return instance.booking_status_color.color_code
        return '#000000'

    def get_customer_freight(self, instance):
        return instance.customer_freight

    def get_supplier_freight(self, instance):
        return instance.supplier_freight

    def get_pod_data(self, instance):
        from restapi.serializers.file_upload import BasicPODFileSerializer
        return BasicPODFileSerializer(instance.podfile_set.all(), many=True).data

    def get_inward_payments(self, instance):
        return InWardPaymentSerializer(InWardPayment.objects.filter(booking_id=instance), many=True).data

    def get_outward_payments(self, instance):
        return OutWardPaymentSerializer(OutWardPayment.objects.filter(booking_id=instance), many=True).data

    def get_invoices(self, instance):
        return InvoiceSerializer(Invoice.objects.filter(bookings=instance), many=True).data

    def get_lr_numbers(self, instance):
        return '\n'.join(instance.lr_numbers.values_list('lr_number', flat=True))

    @staticmethod
    def get_source_office_data(instance):
        if isinstance(instance.source_office, AahoOffice):
            return {'id': instance.source_office.id, 'branch_name': instance.source_office.branch_name}
        return {'id': -1, 'branch_name': None}

    @staticmethod
    def get_destination_office_data(instance):
        if isinstance(instance.destination_office, AahoOffice):
            return {'id': instance.destination_office.id, 'branch_name': instance.destination_office.branch_name}
        return {'id': -1, 'branch_name': None}

    @staticmethod
    def get_customer_placed_order_data(instance):
        if isinstance(instance.company, Sme):
            return {'id': instance.company.id, 'name': instance.company.get_name(),
                    'code': instance.company.company_code, 'gstin': instance.company.gstin}
        return {'id': None, 'name': None, 'code': None, 'gstin': None}

    @staticmethod
    def get_customer_to_be_billed_to_data(obj):
        if isinstance(obj.customer_to_be_billed_to, Sme):
            return {'id': obj.customer_to_be_billed_to.id, 'name': obj.customer_to_be_billed_to.get_name(),
                    'code': obj.customer_to_be_billed_to.company_code, 'gstin': obj.customer_to_be_billed_to.gstin,
                    'address': obj.customer_to_be_billed_to.customer_address, 'pin': obj.customer_to_be_billed_to.pin,
                    'city': {
                        'name': obj.customer_to_be_billed_to.city.name if obj.customer_to_be_billed_to.city else None,
                        'id': obj.customer_to_be_billed_to.city.id if obj.customer_to_be_billed_to.city else -1}}
        return {'id': -1, 'name': None, 'pin': None, 'code': None, 'gstin': None, 'address': None,
                'city': {'name': None, 'id': -1}}

    @staticmethod
    def get_supplier_data(instance):
        if isinstance(instance.booking_supplier, Supplier):
            return {'id': instance.booking_supplier.id, 'name': instance.booking_supplier.name,
                    'phone': instance.booking_supplier.phone, 'code': instance.booking_supplier.code,
                    'name_code': '{}, {}'.format(instance.booking_supplier.name, instance.booking_supplier.code)}
        return {'id': -1, 'name': None, 'phone': None, 'code': None,'name_code':None}

    def get_accounting_supplier_data(self, instance):
        if isinstance(instance.accounting_supplier, Supplier):
            return {'id': instance.accounting_supplier.id, 'name': instance.accounting_supplier.name,
                    'phone': instance.accounting_supplier.phone, 'code': instance.accounting_supplier.code,
                    'name_code': '{}, {}'.format(instance.accounting_supplier.name, instance.accounting_supplier.code)}
        return {'id': -1, 'name': None, 'phone': None, 'code': None, 'name_code': None}

    @staticmethod
    def get_owner_data(instance):
        if isinstance(instance.owner_supplier, Supplier):
            return {'id': instance.owner_supplier.id, 'name': instance.owner_supplier.name,
                    'phone': instance.owner_supplier.phone}
        return {'id': -1, 'name': None, 'phone': None}

    @staticmethod
    def get_driver_data(instance):
        if isinstance(instance.driver_supplier, Driver):
            return {'id': instance.driver_supplier.id, 'name': instance.driver_supplier.name,
                    'phone': instance.driver_supplier.phone}
        return {'id': -1, 'name': None, 'phone': None}

    @staticmethod
    def get_consignor_city_fk_data(instance):
        if isinstance(instance.consignor_city_fk, City):
            return {'id': instance.consignor_city_fk.id, 'name': instance.consignor_city_fk.name,
                    'code': instance.consignor_city_fk.code}
        return {'id': -1, 'name': None, 'code': None}

    @staticmethod
    def get_consignee_city_fk_data(instance):
        if isinstance(instance.consignee_city_fk, City):
            return {'id': instance.consignee_city_fk.id, 'name': instance.consignee_city_fk.name,
                    'code': instance.consignee_city_fk.code}
        return {'id': -1, 'name': None, 'code': None}

    @staticmethod
    def get_from_city_fk_data(instance):
        if isinstance(instance.from_city_fk, City):
            return {'id': instance.from_city_fk.id, 'name': instance.from_city_fk.name,
                    'code': instance.from_city_fk.code}
        return {'id': -1, 'name': None, 'code': None}

    @staticmethod
    def get_to_city_fk_data(instance):
        if isinstance(instance.to_city_fk, City):
            return {'id': instance.to_city_fk.id, 'name': instance.to_city_fk.name,
                    'code': instance.to_city_fk.code}
        return {'id': -1, 'name': None, 'code': None}

    @staticmethod
    def get_vehicle_data(instance):
        if isinstance(instance.supplier_vehicle, Vehicle):
            vehicle = {
                'id': instance.supplier_vehicle.id, 'vehicle_number': instance.supplier_vehicle.number(),
            }
            if isinstance(instance.supplier_vehicle.vehicle_type, VehicleCategory):
                vehicle["vehicle_type"] = instance.supplier_vehicle.vehicle_type.vehicle_type
            else:
                vehicle["vehicle_type"] = None
            return vehicle
        return {'id': -1, 'vehicle_number': None, "vehicle_type": None}

    @staticmethod
    def get_vehicle_category_data(instance):
        if isinstance(instance.vehicle_category, VehicleCategory):
            return {'id': instance.vehicle_category.id, 'type': instance.vehicle_category.vehicle_category}
        return {}

    def validate_created_by(self, value):
        if isinstance(self.instance, ManualBooking) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    # def validate_lorry_number(self, value):
    #     if not validate_vehicle_number(value):
    #         raise serializers.ValidationError({"vehicle_number": "Vehicle Number is not valid"})
    #     return value

    def create(self, validated_data):
        instance = ManualBooking.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        ManualBooking.objects.filter(id=instance.id).update(**validated_data)
        booking = ManualBooking.objects.get(id=instance.id)
        booking.save()
        return ManualBooking.objects.get(id=instance.id)

    @staticmethod
    def create_booking_status_mapping(data):
        manual_booking = ManualBooking.objects.get(id=data['mb_id'])
        try:
            booking_status = BookingStatuses.objects.get(status=data['status'])
        except BookingStatuses.DoesNotExist:
            return {'id': None, 'booking_status_chain_id': None}
        try:
            booking_status_chain = BookingStatusChain.objects.get(booking_status=booking_status)
        except BookingStatusChain.DoesNotExist:
            return {'id': None, 'booking_status_chain_id': None}
        due_date = (timezone.now() + timedelta(minutes=booking_status_chain.booking_status.time_limit)).date()
        booking_statuses_mapping = BookingStatusesMapping.objects.create(booking_status_chain=booking_status_chain,
                                                                         manual_booking=manual_booking,
                                                                         booking_stage='in_progress',
                                                                         created_by=data['user'],
                                                                         due_date=due_date)
        return {'id': booking_statuses_mapping.id, 'booking_status_chain_id': booking_status_chain.id}


class LrNumberSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    lr_number = serializers.CharField(max_length=30, validators=[UniqueValidator(queryset=LrNumber.objects.all())])
    datetime = serializers.DateTimeField(format=DATE_FORMAT)
    pod_status = serializers.ChoiceField(allow_null=True, choices=(
        ('pending', 'Pending'), ('unverified', 'Unverified'), ('rejected', 'Rejected'), ('completed', 'Delivered')),
                                         required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    booking = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=ManualBooking.objects.all(), required=False)
    source_office = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=AahoOffice.objects.all(),
                                                       required=False)
    destination_office = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=AahoOffice.objects.all(),
                                                            required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    booking_id = serializers.SerializerMethodField()
    s3_upload_url = serializers.SerializerMethodField()

    def to_representation(self, instance):
        # self.fields["booking"] = ManualBookingSerializer(read_only=True)
        self.fields["source_office"] = AahoOfficeSerializer(read_only=True)
        self.fields["destination_office"] = AahoOfficeSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def validate_created_by(self, value):
        if isinstance(self.instance, LrNumber) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def get_booking_id(self, instance):
        if isinstance(instance.booking, ManualBooking):
            return instance.booking.booking_id
        return None

    def get_s3_upload_url(self, instance):
        if isinstance(instance, LrNumber) and instance.lrs3upload_set.filter(is_valid=True).exclude(
                s3_upload=None).exclude(deleted=True).exists():
            return instance.lrs3upload_set.filter(is_valid=True).exclude(s3_upload=None).exclude(
                deleted=True).last().s3_upload.public_url()
        return None

    def create(self, validated_data):
        instance = LrNumber.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        LrNumber.objects.filter(id=instance.id).update(**validated_data)
        return LrNumber.objects.get(id=instance.id)


class RejectedPODSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    remarks = serializers.CharField(max_length=500)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    # created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    # changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    booking = serializers.PrimaryKeyRelatedField(queryset=ManualBooking.objects.all())
    lr = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=LrNumber.objects.all())
    rejected_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def to_representation(self, instance):
        # self.fields["booking"] = ManualBookingSerializer(read_only=True)
        self.fields["lr"] = LrNumberSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def validate_created_by(self, value):
        if isinstance(self.instance, RejectedPOD) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        instance = RejectedPOD.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        RejectedPOD.objects.filter(id=instance.id).update(**validated_data)
        return RejectedPOD.objects.get(id=instance.id)


class BookingConsignorConsigneeSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    category = serializers.CharField(allow_null=True, max_length=20, required=False)
    name = serializers.CharField(allow_null=True, max_length=255, required=False)
    address = serializers.CharField(allow_null=True, max_length=255, required=False)
    pin = serializers.CharField(allow_null=True, max_length=255, required=False)
    phone = serializers.CharField(allow_null=True, max_length=255, required=False)
    cst_tin = serializers.CharField(allow_null=True, max_length=255, required=False)
    gstin = serializers.CharField(allow_null=True, max_length=15, required=False)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    booking = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=ManualBooking.objects.all(), required=False)
    lr = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=LrNumber.objects.all(), required=False)
    city = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=City.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["booking"] = ManualBookingSerializer(read_only=True)
        self.fields["lr"] = LrNumberSerializer(read_only=True)
        self.fields["city"] = CitySerializer(read_only=True)
        return super().to_representation(instance=instance)

    def validate_created_by(self, value):
        if isinstance(self.instance, BookingConsignorConsignee) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        instance = BookingConsignorConsignee.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        BookingConsignorConsignee.objects.filter(id=instance.id).update(**validated_data)
        return BookingConsignorConsignee.objects.get(id=instance.id)


class BookingInsuranceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    is_insured = serializers.BooleanField(required=False)
    insurance_provider = serializers.CharField(allow_null=True, max_length=200, required=False)
    insurance_policy_number = serializers.CharField(allow_null=True, max_length=200, required=False)
    insured_amount = serializers.DecimalField(allow_null=True, decimal_places=2, max_digits=30, required=False)
    insurance_date = serializers.DateField(allow_null=True, required=False)
    insurance_risk = serializers.CharField(allow_null=True, max_length=200, required=False)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def validate_created_by(self, value):
        if isinstance(self.instance, BookingInsurance) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        instance = BookingInsurance.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        BookingInsurance.objects.filter(id=instance.id).update(**validated_data)
        return BookingInsurance.objects.get(id=instance.id)


class InWardPaymentSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    received_from = serializers.CharField(max_length=300)
    tds = serializers.DecimalField(decimal_places=2, max_digits=30)
    actual_amount = serializers.DecimalField(decimal_places=2, max_digits=30)
    expected_amount = serializers.DecimalField(allow_null=True, decimal_places=2, max_digits=30, required=False)
    payment_mode = serializers.ChoiceField(choices=(
        ('cash', 'Cash'), ('cheque', 'Cheque'), ('neft', 'NEFT'), ('imps', 'IMPS'), ('rtgs', 'RTGS'),
        ('happay', 'Happay'),
        ('cash_deposit', 'Cash Deposit'), ('hdfc_internal_account', 'HDFC Internal Account')))
    trn = serializers.CharField(allow_null=True, max_length=200, required=False)
    remarks = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    payment_date = serializers.DateField(input_formats=[DATE_FORMAT, ISO_8601, "%d/%m/%Y"], format=DATE_FORMAT)
    invoice_number = serializers.CharField(allow_null=True, max_length=300)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    booking_id = serializers.PrimaryKeyRelatedField(many=True, queryset=ManualBooking.objects.all())
    bookings = serializers.SerializerMethodField()
    lr_numbers = serializers.SerializerMethodField()
    pending_inward_id = serializers.SerializerMethodField()
    booking_data = serializers.SerializerMethodField()

    def validate_created_by(self, value):
        if isinstance(self.instance, InWardPayment) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def get_booking_data(self, instance):
        return [{'id': booking.id, 'booking_id': booking.booking_id,
                 'lr_number': ', '.join(booking.lr_numbers.values_list('lr_number', flat=True))} for booking in
                instance.booking_id.all()]

    def get_payment_mode_display(self, instance):
        return instance.get_payment_mode_display()

    def get_bookings(self, instance):
        return '\n'.join(instance.booking_id.values_list('booking_id', flat=True))

    def get_lr_numbers(self, instance):
        return '\n'.join(['\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in
                          instance.booking_id.all()])

    def get_pending_inward_id(self, instance):
        if instance.pendinginwardpaymententry_set.exists():
            pending_inward = instance.pendinginwardpaymententry_set.last()
            return pending_inward.id
        return '-'

    def create(self, validated_data):
        booking_ids = []
        if "booking_id" in validated_data.keys():
            booking_ids = validated_data.pop('booking_id')

        instance = InWardPayment.objects.create(**validated_data)

        for booking_id in booking_ids:
            instance.booking_id.add(booking_id)
            booking_id.save()
        return instance

    def update(self, instance, validated_data):
        booking_ids = []
        if "booking_id" in validated_data.keys():
            booking_ids = validated_data.pop('booking_id')
            instance.booking_id.clear()

        InWardPayment.objects.filter(id=instance.id).update(**validated_data)
        for booking_id in booking_ids:
            instance.booking_id.add(booking_id)
        return InWardPayment.objects.get(id=instance.id)


class OutWardPaymentSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    paid_to = serializers.CharField(max_length=300)
    lorry_number = serializers.CharField(allow_null=True, max_length=30, required=False)
    utr = serializers.CharField(allow_null=True, min_length=16, max_length=30, required=False)
    actual_amount = serializers.DecimalField(decimal_places=2, max_digits=30, required=True)
    tds = serializers.DecimalField(allow_null=True, decimal_places=2, max_digits=30, required=False)
    expected_amount = serializers.DecimalField(write_only=True, allow_null=True, decimal_places=2, max_digits=30,
                                               required=False)
    payment_mode = serializers.ChoiceField(write_only=True, choices=(
        ('cash', 'Cash'), ('cheque', 'Cheque'), ('neft', 'NEFT'), ('imps', 'IMPS'), ('rtgs', 'RTGS'),
        ('happay', 'Happay'), ('fuel_card', 'Fuel Card'), ('hdfc_internal_account', 'HDFC Internal Account'),
        ('adjustment', 'Adjustment')))
    remarks = serializers.CharField(allow_null=True, required=False, style={'base_template': 'textarea.html'})
    payment_date = serializers.DateField(format=DATE_FORMAT,
                                         input_formats=[DATE_FORMAT, ISO_8601, "%d/%m/%Y", '%Y-%m-%d'])
    invoice_number = serializers.CharField(write_only=True, allow_null=True, max_length=300, required=False)
    status = serializers.ChoiceField(
        allow_null=True, choices=(('paid', 'Paid'), ('unpaid', 'Not Paid'), ('reconciled', 'Reconciled')),
        required=False)
    is_sms_supplier = serializers.BooleanField(required=False)
    is_refund_amount = serializers.BooleanField(required=False)
    created_on = serializers.DateTimeField(read_only=True, format=DATETIME_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True, format=DATETIME_FORMAT)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False,
                                           input_formats=[DATE_FORMAT, ISO_8601, "%d/%m/%Y", '%Y-%m-%d'])
    bank_account = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True, queryset=Bank.objects.all(), required=False)
    fuel_card = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=FuelCard.objects.all(), required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    booking_id = serializers.PrimaryKeyRelatedField(write_only=True, many=True, queryset=ManualBooking.objects.all(),
                                                    required=False)
    aaho_office = serializers.PrimaryKeyRelatedField(write_only=True, allow_null=True,
                                                     queryset=AahoOffice.objects.all(), required=False)
    bookings = serializers.SerializerMethodField()
    lr_numbers = serializers.SerializerMethodField()
    bank_account_detail = serializers.SerializerMethodField()
    fuel_card_detail = serializers.SerializerMethodField()
    payment_mode_display = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    account_number = serializers.SerializerMethodField()

    bookings_data = serializers.SerializerMethodField()

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        excluded_fields = [
            'deleted', 'deleted_on', 'updated_on', 'created_on'
        ]
        for field in excluded_fields:
            kwargs['child'].fields.pop(field)
        return serializers.ListSerializer(*args, **kwargs)

    def get_bookings_data(self, instance):
        if instance.booking_id.count() > 0:
            booking = instance.booking_id.last()
            return {'id': booking.id, 'booking_id': booking.booking_id}
        return {'id': -1, 'booking_id': None}

    def get_details(self, instance):
        if isinstance(instance.bank_account, Bank):
            return 'A/C No.: {}'.format(instance.bank_account.account_number)
        elif isinstance(instance.fuel_card, FuelCard):
            return 'Card Number: {}'.format(instance.fuel_card.card_number)
        else:
            return None

    def get_account_number(self, instance):
        return instance.bank_account.account_number if isinstance(instance.bank_account, Bank) else None

    def get_fuel_card_detail(self, instance):
        if isinstance(instance.fuel_card, FuelCard):
            return {'id': instance.fuel_card.id, 'card_number': instance.fuel_card.card_number}
        return {'id': -1, 'card_number': None}

    def get_bank_account_detail(self, instance):
        if isinstance(instance.bank_account, Bank):
            return {'id': instance.bank_account.id, 'account_holder_name': instance.bank_account.account_holder_name,
                    'account_number': instance.bank_account.account_number}
        return {'id': -1, 'account_holder_name': None, 'account_number': None}

    def get_payment_mode_display(self, instance):
        return instance.get_payment_mode_display()

    def get_bookings(self, instance):
        return '\n'.join(instance.booking_id.values_list('booking_id', flat=True))

    def get_lr_numbers(self, instance):
        return '\n'.join(['\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in
                          instance.booking_id.all()])

    def validate_created_by(self, value):
        if isinstance(self.instance, OutWardPayment) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        booking_ids = []
        if "booking_id" in validated_data.keys():
            booking_ids = validated_data.pop('booking_id')
        instance = OutWardPayment.objects.create(**validated_data)
        for booking_id in booking_ids:
            instance.booking_id.add(booking_id)
            booking_id.save()
        return instance

    def update(self, instance, validated_data):
        booking_ids = []
        if "booking_id" in validated_data.keys():
            booking_ids = validated_data.pop('booking_id')
            instance.booking_id.clear()

        OutWardPayment.objects.filter(id=instance.id).update(**validated_data)
        for booking_id in booking_ids:
            instance.booking_id.add(booking_id)
        return OutWardPayment.objects.get(id=instance.id)


class OutWardPaymentBillSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    bill_number = serializers.CharField(max_length=30,
                                        validators=[UniqueValidator(queryset=OutWardPaymentBill.objects.all())])
    bill_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, ISO_8601])
    amount = serializers.IntegerField(max_value=2147483647, min_value=0)
    vehicle_number = serializers.CharField(allow_null=True, max_length=50, required=False)
    lr_number = serializers.CharField(allow_null=True, max_length=200, required=False)
    from_city = serializers.CharField(allow_null=True, max_length=50, required=False)
    to_city = serializers.CharField(allow_null=True, max_length=50, required=False)
    loading_date = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                         input_formats=[DATE_FORMAT, ISO_8601])
    weight = serializers.CharField(allow_null=True, max_length=50, required=False)
    paid_to = serializers.CharField(allow_null=True, max_length=50, required=False)
    pan_number = serializers.CharField(allow_null=True, max_length=30, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    booking = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=ManualBooking.objects.all(), required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    outward_pmt = serializers.PrimaryKeyRelatedField(allow_empty=False, many=True,
                                                     queryset=OutWardPayment.objects.all())
    booking_id = serializers.SerializerMethodField()
    s3_upload_url = serializers.SerializerMethodField()
    all_lr_numbers = serializers.SerializerMethodField()
    payment_date_mode_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        excluded_fields = [
            'id', 'deleted', 'deleted_on', 'updated_on', 'from_city', 'to_city'
        ]
        for field in excluded_fields:
            kwargs['child'].fields.pop(field)
        return serializers.ListSerializer(*args, **kwargs)

    def validate_created_by(self, value):
        if isinstance(self.instance, OutWardPaymentBill) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def get_payment_mode_display(self, instance):
        return instance.get_payment_mode_display()

    def get_booking_id(self, instance):
        if isinstance(instance, OutWardPaymentBill) and isinstance(instance.booking, ManualBooking):
            return instance.booking.booking_id
        return None

    def get_all_lr_numbers(self, instance):
        if isinstance(instance, OutWardPaymentBill) and isinstance(instance.booking, ManualBooking):
            return '\n'.join(instance.booking.lr_numbers.values_list("lr_number", flat=True))
        return None

    def get_payment_date_mode_amount(self, instance):
        if isinstance(instance, OutWardPaymentBill) and instance.outward_pmt:
            return [{'payment_date': payment.payment_date.strftime(DATE_FORMAT) if payment.payment_date else None,
                     'mode': payment.get_payment_mode_display(),
                     'amount': to_int(payment.actual_amount)} for payment in instance.outward_pmt.exclude(deleted=True)]
        return []

    def get_s3_upload_url(self, instance):
        if isinstance(instance, OutWardPaymentBill):
            if S3Upload.objects.filter(filename__istartswith='{}-{}'.format('OPB', instance.bill_number),
                                       filename__iendswith='.pdf').exists():
                return S3Upload.objects.filter(filename__istartswith='{}-{}'.format('OPB', instance.bill_number),
                                               filename__iendswith='.pdf').last().public_url()
        return None

    def get_total_amount(self, instance):
        if isinstance(instance, OutWardPaymentBill):
            return instance.total_amount
        return None

    def create(self, validated_data):
        outward_pmts = []
        if "outward_pmt" in validated_data.keys():
            outward_pmts = validated_data.pop('outward_pmt')
        instance = OutWardPaymentBill.objects.create(**validated_data)
        for outward_pmt in outward_pmts:
            instance.outward_pmt.add(outward_pmt)

        return instance

    def update(self, instance, validated_data):
        outward_pmts = []
        if "outward_pmt" in validated_data.keys():
            outward_pmts = validated_data.pop('outward_pmt')
            instance.outward_pmt.clear()
        OutWardPaymentBill.objects.filter(id=instance.id).update(**validated_data)
        for outward_pmt in outward_pmts:
            instance.outward_pmt.add(outward_pmt)
        return OutWardPaymentBill.objects.get(id=instance.id)


class InvoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    invoice_number = serializers.CharField(max_length=30, validators=[UniqueValidator(queryset=Invoice.objects.all())])
    date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, ISO_8601])
    company_name = serializers.CharField(max_length=255)
    payment_received = serializers.BooleanField(required=False)
    address = serializers.CharField(allow_null=True, max_length=500)
    pin = serializers.CharField(allow_null=True, max_length=6, required=True)
    gstin = serializers.CharField(allow_null=True, min_length=15, max_length=15, required=True)
    total_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=True)
    advance_payment = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    remarks = serializers.CharField(allow_null=True, max_length=500, required=False)
    service_tax_paid_by = serializers.CharField(allow_null=True, max_length=255, required=True)
    service_tax_aaho = serializers.DecimalField(decimal_places=2, max_digits=4)
    created_on = serializers.DateTimeField(read_only=True, format=DATETIME_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True, format=DATETIME_FORMAT)
    deleted = serializers.BooleanField(required=False)
    summary_required = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, format=DATETIME_FORMAT)

    customer_fk = serializers.PrimaryKeyRelatedField(queryset=Sme.objects.all(), required=True)
    city = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=City.objects.all(), required=True)
    s3_upload = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=S3Upload.objects.all(), required=True)
    s3_upload_url = serializers.SerializerMethodField()

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    bookings = serializers.PrimaryKeyRelatedField(many=True, queryset=ManualBooking.objects.all(), required=False)
    booking_id = serializers.SerializerMethodField()
    lr_numbers = serializers.SerializerMethodField()
    is_escalate = serializers.SerializerMethodField()
    due_date = serializers.SerializerMethodField()
    amount_to_be_received = serializers.SerializerMethodField()

    def get_is_escalate(self, instance):
        if BookingStatusesMapping.objects.filter(
                manual_booking__in=instance.bookings.all(),
                booking_status_chain__booking_status__status='party_invoice_sent',
                booking_stage='in_progress').exists():
            return True
        return False

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        excluded_fields = [
            'deleted', 'bookings', 'changed_by', 's3_upload', 'city', 'customer_fk', 'updated_on',
            'service_tax_paid_by', 'service_tax_aaho', 'summary_required', 'address', 'remarks', 'deleted_on'
        ]
        for field in excluded_fields:
            kwargs['child'].fields.pop(field)
        return serializers.ListSerializer(*args, **kwargs)

    def get_booking_id(self, instance):
        return '\n'.join(instance.bookings.values_list('booking_id', flat=True))

    def get_amount_to_be_received(self, instance):
        return instance.get_amount_to_be_received

    def get_due_date(self, instance):
        if instance.customer_fk:
            credit_period = instance.customer_fk.credit_period if instance.customer_fk.credit_period else 0
        else:
            credit_period = 0
        return (instance.date + timedelta(days=int(credit_period))).strftime("%d-%b-%Y")

    def get_lr_numbers(self, instance):
        return '\n'.join(['\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in
                          instance.bookings.all()])

    def get_s3_upload_url(self, instance):
        if isinstance(instance.s3_upload, S3Upload):
            return instance.s3_upload.public_url()
        return ''

    def validate_created_by(self, value):
        if isinstance(self.instance, Invoice) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        bookings = []
        if "bookings" in validated_data.keys():
            bookings = validated_data.pop('bookings')
        instance = Invoice.objects.create(**validated_data)
        for booking in bookings:
            instance.bookings.add(booking)

        return instance

    def update(self, instance, validated_data):
        bookings = []
        if "bookings" in validated_data.keys():
            bookings = validated_data.pop('bookings')
            instance.bookings.clear()

        Invoice.objects.filter(id=instance.id).update(**validated_data)
        for booking in bookings:
            instance.bookings.add(booking)
        return Invoice.objects.get(id=instance.id)


class ToPayInvoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    invoice_gen_office = serializers.CharField(allow_null=True, max_length=200, required=False)
    invoice_number = serializers.CharField(allow_null=True, max_length=30, required=False,
                                           validators=[UniqueValidator(queryset=ToPayInvoice.objects.all())])
    date = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                 input_formats=[DATE_FORMAT, ISO_8601])
    company_name = serializers.CharField(allow_null=True, max_length=100, required=False)
    payment_received = serializers.BooleanField(required=False)
    company_address = serializers.CharField(allow_null=True, max_length=300, required=False)
    pin = serializers.CharField(allow_null=True, max_length=6, required=False)
    gstin = serializers.CharField(allow_null=True, max_length=15, required=False)
    source = serializers.CharField(allow_null=True, max_length=35, required=False)
    destination = serializers.CharField(allow_null=True, max_length=35, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    lr_number = serializers.CharField(allow_null=True, max_length=100, required=False)
    quantity = serializers.CharField(allow_null=True, max_length=100, required=False)
    rate = serializers.CharField(allow_null=True, max_length=20, required=False)
    total_payable_freight = serializers.CharField(allow_null=True, max_length=30, required=False)
    amount_payable_to_transiq = serializers.CharField(allow_null=True, max_length=30, required=False)
    balance_payable_to_lorry_driver = serializers.CharField(allow_null=True, max_length=30,
                                                            required=False)
    advance_payment = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    remarks = serializers.CharField(allow_null=True, required=False,
                                    style={'base_template': 'textarea.html'})
    service_tax_paid_by = serializers.CharField(allow_null=True, max_length=255, required=False)
    service_tax_aaho = serializers.DecimalField(allow_null=True, decimal_places=2, max_digits=4, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    customer_fk = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Sme.objects.all(), required=False)
    city = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=City.objects.all(), required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    bookings = serializers.PrimaryKeyRelatedField(allow_empty=False, many=True, queryset=ManualBooking.objects.all())

    def to_representation(self, instance):
        self.fields["customer_fk"] = SmeSerializer(read_only=True)
        self.fields["city"] = CitySerializer(read_only=True)
        self.fields["bookings"] = ManualBookingSerializer(read_only=True, many=True)
        return super().to_representation(instance=instance)

    def validate_created_by(self, value):
        if isinstance(self.instance, ToPayInvoice) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        bookings = []
        if "bookings" in validated_data.keys():
            bookings = validated_data.pop('bookings')
        instance = ToPayInvoice.objects.create(**validated_data)
        for booking in bookings:
            instance.bookings.add(booking)

        return instance

    def update(self, instance, validated_data):
        bookings = []
        if "bookings" in validated_data.keys():
            bookings = validated_data.pop('bookings')
            instance.bookings.clear()

        ToPayInvoice.objects.filter(id=instance.id).update(**validated_data)
        for booking in bookings:
            instance.bookings.add(booking)
        return ToPayInvoice.objects.get(id=instance.id)


class PendingInwardPaymentEntrySerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    customer_name = serializers.CharField(allow_null=True, max_length=300, required=False)
    payment_mode = serializers.ChoiceField(choices=(
        ('cash', 'Cash'), ('cheque', 'Cheque'), ('neft', 'NEFT'), ('rtgs', 'RTGS'), ('cash_deposit', 'Cash Deposit'),
        ('hdfc_internal_account', 'HDFC')))
    amount = serializers.DecimalField(decimal_places=2, max_digits=12, required=True)
    tds = serializers.DecimalField(decimal_places=2, max_digits=12, required=False)
    payment_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, ISO_8601, "%d/%m/%Y"])
    adjusted_flag = serializers.BooleanField(required=False)
    credited_flag = serializers.BooleanField(required=False)
    uploaded_datetime = serializers.DateTimeField(allow_null=True, default=datetime.now())
    adjusted_datetime = serializers.DateTimeField(allow_null=True, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    trn = serializers.CharField(allow_null=True,
                                style={'base_template': 'textarea.html'}, required=False)
    additional_remark = serializers.CharField(allow_null=True, required=False,
                                              style={'base_template': 'textarea.html'})
    customer = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Sme.objects.all())
    uploaded_by = serializers.SlugRelatedField(allow_null=True, queryset=User.objects.all(),
                                               slug_field="username")
    adjusted_by = serializers.SlugRelatedField(allow_null=True, queryset=User.objects.all(), required=False,
                                               slug_field="username")
    inward_payment = serializers.PrimaryKeyRelatedField(many=True, allow_empty=False,
                                                        queryset=InWardPayment.objects.all(), required=False)
    bookings = serializers.PrimaryKeyRelatedField(many=True, allow_empty=False, queryset=ManualBooking.objects.all(),
                                                  required=False)

    # def to_representation(self, instance):
    #     self.fields["customer"] = SmeSerializer(read_only=True)
    #     self.fields["uploaded_by"] = UserSerializer(read_only=True)
    #     self.fields["adjusted_by"] = UserSerializer(read_only=True)
    #     self.fields["inward_payment"] = InWardPaymentSerializer(read_only=True, many=True)
    #     self.fields["bookings"] = ManualBookingSerializer(read_only=True, many=True)
    #     return super(PendingInwardPaymentEntrySerializer, self).to_representation(instance=instance)

    def validate(self, attrs):
        if isinstance(self.instance, PendingInwardPaymentEntry):
            if "payment_mode" in attrs.keys() and attrs["payment_mode"] != "cash":
                payment_date = attrs["payment_date"] if "payment_date" in attrs.keys() else self.instance.payment_date
                trn = attrs["trn"] if "trn" in attrs.keys() else self.instance.trn
                if PendingInwardPaymentEntry.objects.filter(trn=trn, payment_date=payment_date).exists():
                    raise serializers.ValidationError(
                        "Error: TRN = {}, Payment Date = {} combination with Payment Mode = {} already exist".format(
                            trn,
                            payment_date,
                            attrs["payment_mode"].upper())
                    )

        else:
            if "payment_mode" in attrs.keys() and attrs["payment_mode"] != "cash":
                if PendingInwardPaymentEntry.objects.filter(trn=attrs["trn"],
                                                            payment_date=attrs["payment_date"]).exists():
                    raise serializers.ValidationError(
                        "Error: TRN = {}, Payment Date = {} combination with Payment Mode = {} already exist".format(
                            attrs["trn"],
                            attrs["payment_date"],
                            attrs["payment_mode"].upper())
                    )
        return attrs

    def validate_uploaded_by(self, value):
        if isinstance(self.instance, PendingInwardPaymentEntry) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        bookings = []
        inward_payments = []

        if validated_data["customer"] is not None:
            validated_data["customer_name"] = validated_data["customer"].get_name()

        if "bookings" in validated_data.keys():
            bookings = validated_data.pop('bookings')
        if "inward_payment" in validated_data.keys():
            inward_payments = validated_data.pop('inward_payment')
        instance = PendingInwardPaymentEntry.objects.create(**validated_data)
        for booking in bookings:
            instance.bookings.add(booking)
        for inward_payment in inward_payments:
            instance.inward_payment.add(inward_payment)
        return instance

    def update(self, instance, validated_data):
        bookings = []
        inward_payments = []
        if "bookings" in validated_data.keys():
            bookings = validated_data.pop('bookings')
            instance.bookings.clear()
        if "inward_payment" in validated_data.keys():
            inward_payments = validated_data.pop('inward_payment')
            instance.inward_payment.clear()
        PendingInwardPaymentEntry.objects.filter(id=instance.id).update(**validated_data)

        for booking in bookings:
            instance.bookings.add(booking)
        for inward_payment in inward_payments:
            instance.inward_payment.add(inward_payment)
        return PendingInwardPaymentEntry.objects.get(id=instance.id)


class CreditDebitNoteReasonSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(max_length=30,
                                 validators=[UniqueValidator(queryset=CreditDebitNoteReason.objects.all())])
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def validate_created_by(self, value):
        if isinstance(self.instance, CreditDebitNoteReason) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        return CreditDebitNoteReason.objects.create(**validated_data)

    def update(self, instance, validated_data):
        CreditDebitNoteReason.objects.filter(id=instance.id).update(**validated_data)
        return CreditDebitNoteReason.objects.get(id=instance.id)


class CreditNoteCustomerSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    credit_note_number = serializers.CharField(max_length=16,
                                               validators=[UniqueValidator(queryset=CreditNoteCustomer.objects.all())],
                                               required=False)
    credit_amount = serializers.IntegerField(max_value=2147483647, min_value=0)
    adjusted_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    approved_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    adjusted_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    remarks = serializers.CharField(allow_null=True, required=False,
                                    style={'base_template': 'textarea.html'})
    status = serializers.ChoiceField(choices=(
        ('pending', 'Pending for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'), ('adjusted', 'Fully Adjusted')), required=False)
    rejected_on = serializers.DateTimeField(allow_null=True, required=False)
    rejection_reason = serializers.CharField(allow_null=True, required=False,
                                             style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    invoice = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Invoice.objects.all(), required=False)
    customer = serializers.PrimaryKeyRelatedField(queryset=Sme.objects.all())
    reason = serializers.PrimaryKeyRelatedField(
        label='Reason for Credit Note', queryset=CreditDebitNoteReason.objects.all())
    bookings = serializers.PrimaryKeyRelatedField(
        label='Adjusted Bookings', many=True, queryset=ManualBooking.objects.all(), required=False)

    approved_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    adjusted_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    rejected_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)

    customer_name = serializers.SerializerMethodField()
    reason_text = serializers.SerializerMethodField()

    def get_reason_text(self, instance):
        if isinstance(instance.reason, CreditDebitNoteReason):
            return instance.reason.name
        return None

    def to_representation(self, instance):
        self.fields["reason"] = CreditDebitNoteReasonSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def get_customer_name(self, instance):
        if isinstance(instance.customer, Sme):
            return instance.customer.get_name()
        return None

    def validate_created_by(self, value):
        if isinstance(self.instance, CreditNoteCustomer) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        validated_data["credit_note_number"] = generate_credit_note_customer_serial_number(
            validated_data["customer"].id)
        bookings = []
        if "bookings" in validated_data.keys():
            bookings = validated_data.pop("bookings")
        instance = CreditNoteCustomer.objects.create(**validated_data)

        for booking in bookings:
            instance.bookings.add(booking)
        return instance

    def update(self, instance, validated_data):
        bookings = []
        if "bookings" in validated_data.keys():
            instance.bookings.clear()
            bookings = validated_data.pop("bookings")
        CreditNoteCustomer.objects.filter(id=instance.id).update(**validated_data)
        for booking in bookings:
            instance.bookings.add(booking)

        return CreditNoteCustomer.objects.get(id=instance.id)


class DebitNoteCustomerSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    debit_note_number = serializers.CharField(max_length=16,
                                              validators=[UniqueValidator(queryset=DebitNoteCustomer.objects.all())],
                                              required=False)
    debit_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    adjusted_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    approved_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    adjusted_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    remarks = serializers.CharField(allow_null=True, required=False,
                                    style={'base_template': 'textarea.html'})
    status = serializers.ChoiceField(choices=(
        ('pending', 'Pending for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'), ('adjusted', 'Fully Adjusted')), required=False)
    rejected_on = serializers.DateTimeField(allow_null=True, required=False)
    rejection_reason = serializers.CharField(allow_null=True, required=False,
                                             style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    invoice = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Invoice.objects.all(), required=False)
    customer = serializers.PrimaryKeyRelatedField(queryset=Sme.objects.all())
    reason = serializers.PrimaryKeyRelatedField(label='Reason for Credit Note',
                                                queryset=CreditDebitNoteReason.objects.all())
    bookings = serializers.PrimaryKeyRelatedField(label='Adjusted Bookings', many=True,
                                                  queryset=ManualBooking.objects.all(),
                                                  required=False)

    approved_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    adjusted_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    rejected_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)

    customer_name = serializers.SerializerMethodField()
    reason_text = serializers.SerializerMethodField()

    def get_reason_text(self, instance):
        if isinstance(instance.reason, CreditDebitNoteReason):
            return instance.reason.name
        return None

    def to_representation(self, instance):
        self.fields["reason"] = CreditDebitNoteReasonSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def get_customer_name(self, instance):
        if isinstance(instance.customer, Sme):
            return instance.customer.get_name()
        return None

    def validate_created_by(self, value):
        if isinstance(self.instance, DebitNoteCustomer) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        validated_data["debit_note_number"] = generate_debit_note_customer_serial_number(
            validated_data["customer"].id)

        bookings = []
        if "bookings" in validated_data.keys():
            bookings = validated_data.pop("bookings")
        instance = DebitNoteCustomer.objects.create(**validated_data)

        for booking in bookings:
            instance.bookings.add(booking)
        return instance

    def update(self, instance, validated_data):
        bookings = []
        if "bookings" in validated_data.keys():
            instance.bookings.clear()
            bookings = validated_data.pop("bookings")
        DebitNoteCustomer.objects.filter(id=instance.id).update(**validated_data)
        for booking in bookings:
            instance.bookings.add(booking)
        return DebitNoteCustomer.objects.get(id=instance.id)


class CreditNoteSupplierSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    credit_note_number = serializers.CharField(max_length=16,
                                               validators=[UniqueValidator(queryset=CreditNoteSupplier.objects.all())],
                                               required=False)
    credit_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    adjusted_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    approved_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    adjusted_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    remarks = serializers.CharField(allow_null=True, required=False,
                                    style={'base_template': 'textarea.html'})
    status = serializers.ChoiceField(choices=(
        ('pending', 'Pending for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'), ('adjusted', 'Fully Adjusted')), required=False)
    rejected_on = serializers.DateTimeField(allow_null=True, required=False)
    rejection_reason = serializers.CharField(allow_null=True, required=False,
                                             style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    invoice = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Invoice.objects.all(), required=False)
    accounting_supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())
    reason = serializers.PrimaryKeyRelatedField(label='Reason for Credit Note',
                                                queryset=CreditDebitNoteReason.objects.all())
    bookings = serializers.PrimaryKeyRelatedField(allow_empty=False, label='Adjusted Bookings', many=True,
                                                  queryset=ManualBooking.objects.all(), required=False)
    approved_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    adjusted_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    rejected_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)

    supplier_name = serializers.SerializerMethodField()
    reason_text = serializers.SerializerMethodField()

    def get_reason_text(self, instance):
        if isinstance(instance.reason, CreditDebitNoteReason):
            return instance.reason.name
        return None

    def get_supplier_name(self, instance):
        if isinstance(instance.accounting_supplier, Supplier):
            return instance.accounting_supplier.name
        return None

    def validate_created_by(self, value):
        if isinstance(self.instance, CreditNoteSupplier) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def to_representation(self, instance):
        self.fields["reason"] = CreditDebitNoteReasonSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        validated_data["credit_note_number"] = generate_credit_note_supplier_serial_number(
            validated_data["accounting_supplier"].id)
        bookings = []
        if "bookings" in validated_data.keys():
            bookings = validated_data.pop("bookings")
        instance = CreditNoteSupplier.objects.create(**validated_data)

        for booking in bookings:
            instance.bookings.add(booking)
        return instance

    def update(self, instance, validated_data):
        bookings = []
        if "bookings" in validated_data.keys():
            instance.bookings.clear()
            bookings = validated_data.pop("bookings")
        CreditNoteSupplier.objects.filter(id=instance.id).update(**validated_data)
        for booking in bookings:
            instance.bookings.add(booking)
        return CreditNoteSupplier.objects.get(id=instance.id)


class DebitNoteSupplierSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    debit_note_number = serializers.CharField(max_length=16,
                                              validators=[UniqueValidator(queryset=DebitNoteSupplier.objects.all())],
                                              required=False)
    debit_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    adjusted_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    approved_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    adjusted_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    remarks = serializers.CharField(allow_null=True, required=False,
                                    style={'base_template': 'textarea.html'})
    status = serializers.ChoiceField(choices=(
        ('pending', 'Pending for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'), ('adjusted', 'Fully Adjusted')), required=False)
    rejected_on = serializers.DateTimeField(allow_null=True, required=False)
    rejection_reason = serializers.CharField(allow_null=True, required=False,
                                             style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    invoice = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Invoice.objects.all(), required=False)
    accounting_supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())
    reason = serializers.PrimaryKeyRelatedField(label='Reason for Credit Note',
                                                queryset=CreditDebitNoteReason.objects.all())
    bookings = serializers.PrimaryKeyRelatedField(allow_empty=False, label='Adjusted Bookings', many=True,
                                                  queryset=ManualBooking.objects.all(), required=False)

    approved_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    adjusted_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    rejected_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    supplier_name = serializers.SerializerMethodField()
    reason_text = serializers.SerializerMethodField()

    def get_reason_text(self, instance):
        if isinstance(instance.reason, CreditDebitNoteReason):
            return instance.reason.name
        return None

    def get_supplier_name(self, instance):
        if isinstance(instance.accounting_supplier, Supplier):
            return instance.accounting_supplier.name
        return None

    def validate_created_by(self, value):
        if isinstance(self.instance, DebitNoteSupplier) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def to_representation(self, instance):
        self.fields["reason"] = CreditDebitNoteReasonSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        validated_data["debit_note_number"] = generate_debit_note_supplier_serial_number(
            validated_data["accounting_supplier"].id)
        bookings = []
        if "bookings" in validated_data.keys():
            bookings = validated_data.pop("bookings")
        instance = DebitNoteSupplier.objects.create(**validated_data)

        for booking in bookings:
            instance.bookings.add(booking)
        return instance

    def update(self, instance, validated_data):
        bookings = []
        if "bookings" in validated_data.keys():
            instance.bookings.clear()
            bookings = validated_data.pop("bookings")
        DebitNoteSupplier.objects.filter(id=instance.id).update(**validated_data)
        for booking in bookings:
            instance.bookings.add(booking)
        return DebitNoteSupplier.objects.get(id=instance.id)


class CreditNoteCustomerDirectAdvanceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    credit_note_number = serializers.CharField(max_length=17, validators=[UniqueValidator(
        queryset=CreditNoteCustomerDirectAdvance.objects.all())], required=False)
    credit_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    adjusted_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    approved_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    adjusted_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    remarks = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                    style={'base_template': 'textarea.html'})
    status = serializers.ChoiceField(choices=(
        ('pending', 'Pending for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'), ('adjusted', 'Fully Adjusted')), required=False)
    rejected_on = serializers.DateTimeField(allow_null=True, required=False)
    rejection_reason = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                             style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    invoice = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Invoice.objects.all(), required=False)
    customer = serializers.PrimaryKeyRelatedField(queryset=Sme.objects.all())
    accounting_supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), required=False)
    reason = serializers.PrimaryKeyRelatedField(label='Reason for Credit Note',
                                                queryset=CreditDebitNoteReason.objects.all())
    bookings = serializers.PrimaryKeyRelatedField(allow_empty=False, label='Adjusted Bookings', many=True,
                                                  queryset=ManualBooking.objects.all(), required=False)

    approved_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    adjusted_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    rejected_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)

    customer_name = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()
    reason_text = serializers.SerializerMethodField()

    def get_reason_text(self, instance):
        if isinstance(instance.reason, CreditDebitNoteReason):
            return instance.reason.name
        return None

    def get_supplier_name(self, instance):
        if isinstance(instance.accounting_supplier, Supplier):
            return instance.accounting_supplier.name
        return None

    def to_representation(self, instance):
        self.fields["reason"] = CreditDebitNoteReasonSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def get_customer_name(self, instance):
        if isinstance(instance.customer, Sme):
            return instance.customer.get_name()
        return None

    def validate_created_by(self, value):
        if isinstance(self.instance, CreditNoteCustomerDirectAdvance) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        validated_data["credit_note_number"] = generate_credit_note_customer_direct_advance_serial_number(
            validated_data["customer"].id)
        bookings = []
        if "bookings" in validated_data.keys():
            bookings = validated_data.pop("bookings")
        instance = CreditNoteCustomerDirectAdvance.objects.create(**validated_data)

        for booking in bookings:
            instance.bookings.add(booking)
        return instance

    def update(self, instance, validated_data):
        bookings = []
        if "bookings" in validated_data.keys():
            instance.bookings.clear()
            bookings = validated_data.pop("bookings")
        CreditNoteCustomerDirectAdvance.objects.filter(id=instance.id).update(**validated_data)
        for booking in bookings:
            instance.bookings.add(booking)
        return CreditNoteCustomerDirectAdvance.objects.get(id=instance.id)


class DebitNoteSupplierDirectAdvanceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    debit_note_number = serializers.CharField(max_length=17, validators=[UniqueValidator(
        queryset=DebitNoteSupplierDirectAdvance.objects.all())], required=False)
    debit_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    adjusted_amount = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    approved_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    adjusted_on = serializers.DateTimeField(allow_null=True, required=False, format=DATE_FORMAT)
    remarks = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                    style={'base_template': 'textarea.html'})
    status = serializers.ChoiceField(choices=(
        ('pending', 'Pending for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'), ('adjusted', 'Fully Adjusted')), required=False)
    rejected_on = serializers.DateTimeField(allow_null=True, required=False)
    rejection_reason = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                             style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    invoice = serializers.PrimaryKeyRelatedField(queryset=Invoice.objects.all(), required=False)
    accounting_supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=Sme.objects.all(), required=False)
    reason = serializers.PrimaryKeyRelatedField(label='Reason for Credit Note',
                                                queryset=CreditDebitNoteReason.objects.all())
    bookings = serializers.PrimaryKeyRelatedField(allow_empty=False, label='Adjusted Bookings', many=True,
                                                  queryset=ManualBooking.objects.all(), required=False)

    approved_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    adjusted_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    rejected_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)
    supplier_name = serializers.SerializerMethodField()

    def get_supplier_name(self, instance):
        if isinstance(instance.accounting_supplier, Supplier):
            return instance.accounting_supplier.name
        return None

    def to_representation(self, instance):
        self.fields["reason"] = CreditDebitNoteReasonSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def validate_created_by(self, value):
        if isinstance(self.instance, DebitNoteSupplierDirectAdvance) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def create(self, validated_data):
        validated_data["debit_note_number"] = generate_debit_note_supplier_direct_advance_serial_number(
            validated_data["accounting_supplier"].id)
        bookings = []
        if "bookings" in validated_data.keys():
            bookings = validated_data.pop("bookings")
        instance = DebitNoteSupplierDirectAdvance.objects.create(**validated_data)

        for booking in bookings:
            instance.bookings.add(booking)
        return instance

    def update(self, instance, validated_data):
        bookings = []
        if "bookings" in validated_data.keys():
            instance.bookings.clear()
            bookings = validated_data.pop("bookings")
        DebitNoteSupplierDirectAdvance.objects.filter(id=instance.id).update(**validated_data)
        for booking in bookings:
            instance.bookings.add(booking)
        return DebitNoteSupplierDirectAdvance.objects.get(id=instance.id)


class DataTablesFilterSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    table_name = serializers.ChoiceField(choices=(
        ('MBS', 'Manual Bookings'), ('INV', 'Invoices'), ('OWP', 'Outward Payments'), ('IWP', 'Inward Payments'),
        ('CUS', 'Customers'), ('SUP', 'Suppliers'), ('OWN', 'Owners'), ('VEH', 'Vehicles')),
        validators=[UniqueValidator(queryset=DataTablesFilter.objects.all())])
    criteria = serializers.JSONField(style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    created_by = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=User.objects.all(), required=False)
    changed_by = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=User.objects.all(), required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
