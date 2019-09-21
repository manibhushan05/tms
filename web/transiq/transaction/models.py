from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from api.utils import format_date
from fms.models import Document
from owner.models import Vehicle
from sme.models import ConsignorConsignee
from utils.models import VehicleCategory, City, AahoOffice


class Transaction(models.Model):
    TRANSACTION_STATUS_CHOICE = (
        ('open', 'Open'),
        ('pending', 'Pending'),
        ('confirmed', 'confirmed'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancel', 'Cancel')
    )
    transaction_id = models.CharField(max_length=20, null=True, unique=True)
    booking_agent = models.ForeignKey(User, null=True, related_name="booking_agent", on_delete=models.CASCADE)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(max_length=100, blank=True, null=True)
    total_vehicle_requested = models.CharField(max_length=10, blank=True, null=True)
    material = models.TextField(blank=True, null=True)
    shipment_datetime = models.DateTimeField(null=True)
    booking_request_datetime = models.DateTimeField(blank=True, null=True)
    booking_confirmation_datetime = models.DateTimeField(blank=True, null=True)
    transaction_managed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    transaction_status = models.CharField(max_length=35, choices=TRANSACTION_STATUS_CHOICE, default='pending',
                                          blank=True, null=True, )
    expected_rate = models.CharField(max_length=255, blank=True, null=True)
    total_amount_charged_to_company = models.PositiveIntegerField(blank=True, null=True, default=0)
    total_amount_paid_to_owner = models.PositiveIntegerField(blank=True, null=True, default=0)
    advance_amount_from_company = models.PositiveIntegerField(blank=True, null=True, default=0)
    advance_amount_paid_to_owner = models.PositiveIntegerField(blank=True, null=True, default=0)
    advance_amount_to_broker_driver = models.PositiveIntegerField(blank=True, null=True, default=0)
    additional_charges_for_customer = models.IntegerField(blank=True, null=True,
                                                          verbose_name="Additional Charges/Deductions for Customer (+/-)")
    note_for_additional_customer_charges = models.TextField(blank=True, null=True,
                                                            verbose_name="Explanation Additional Charges/Deductions for Customer (+/-)")
    additional_charges_for_owner = models.IntegerField(blank=True, null=True,
                                                       verbose_name="Additional Charges/Deductions for Owner (+/-)")
    note_for_additional_owner_charges = models.TextField(blank=True, null=True,
                                                         verbose_name="Explanation Additional Charges/Deductions for Owner (+/-)")
    cancellation_date = models.DateField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Transactions"

    def __str__(self):
        return str(self.transaction_id)


class LoadingUnloadingAddress(models.Model):
    loading_choice = (
        ('loading', 'loading'),
        ('unloading', 'unloading'),
    )
    type = models.CharField(max_length=30, choices=loading_choice, blank=True, null=True)
    transaction = models.ForeignKey(Transaction, blank=True, null=True, related_name="loading_unloading_location", on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Loading/Unloading Locations'

    def __str__(self):
        return "%s, %s, %s, %s" % (self.transaction, self.type, self.address, self.city)


class VehicleRequest(models.Model):
    transaction = models.ForeignKey(Transaction, related_name="requested_vehicles", on_delete=models.CASCADE)
    vehicle_category = models.ForeignKey(VehicleCategory, blank=True, null=True, related_name="vehicle_requests", on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=100)
    vehicle_capacity = models.CharField(max_length=30, blank=True, null=True)
    quantity = models.IntegerField()
    details = models.CharField(max_length=200, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Vehicle(s) Requested'
        db_table = 'transaction_vehiclerequest'

    def name(self):
        return self.vehicle_type + ', ' + self.vehicle_capacity

    def __str__(self):
        return '%s, %s, %s, %s' % (self.transaction, self.vehicle_type, self.vehicle_capacity, self.quantity)


class VehicleAllocated(models.Model):
    POD_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('loading', 'Loading'),
        ('in_transit', 'In-Transit'),
        ('unloading', 'Unloading'),
        ('completed', 'Completed')
    )
    tds_certificate_status = (
        ('y', 'Yes'),
        ('n', 'No'),
    )
    inward_payment_status = (
        ('no_invoice', 'No Invoice'),
        ('invoice_raised', 'Invoice Raised'),
        ('partial_received', 'Partial Received'),
        ('full_received', 'Full Received')
    )
    outward_status = (
        ('no_payment_made', 'No Payment Made'),
        ('partial', 'Partial'),
        ('complete', 'Complete'),
    )
    transaction = models.ForeignKey(Transaction, blank=True, null=True, related_name="allocated_vehicle", on_delete=models.CASCADE)
    vehicle_number = models.ForeignKey(Vehicle, blank=True, null=True, on_delete=models.CASCADE)
    driver_name = models.CharField(max_length=70, blank=True, null=True)
    driver_phone = models.CharField(max_length=20, blank=True, null=True)
    lr_number = models.CharField(max_length=200, blank=True, null=True)
    source_address = models.CharField(max_length=255, blank=True, null=True)
    source_city = models.CharField(max_length=70, blank=True, null=True)
    source_pin = models.CharField(max_length=255, blank=True, null=True)
    destination_address = models.CharField(max_length=255, blank=True, null=True)
    destination_city = models.CharField(max_length=70, blank=True, null=True)
    destination_pin = models.CharField(max_length=255, blank=True, null=True)
    material = models.CharField(max_length=300, blank=True, null=True)
    actual_weight = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=3, default=1,
                                        verbose_name='Actual Weight (MT)')
    charged_weight = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=3, default=1,
                                         verbose_name='Charged Weight(MT)')
    party_rate = models.IntegerField(blank=True, null=True, default=0, verbose_name='Party Rate(M.T.)')
    supplier_rate = models.IntegerField(blank=True, null=True, default=0, verbose_name='Supplier Rate(M.T.)')
    # payment details
    total_in_ward_amount = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0, blank=True)
    total_out_ward_amount = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0, blank=True)
    total_amount_to_company = models.IntegerField(blank=True, null=True, default=0)
    advance_amount_from_company = models.IntegerField(blank=True, null=True, default=0)
    total_amount_to_owner = models.IntegerField(blank=True, null=True, default=0)
    advance_amount_to_owner = models.IntegerField(blank=True, null=True, default=0)
    advance_to_driver_or_broker = models.IntegerField(blank=True, null=True, default=0)
    extra_length_charge = models.IntegerField(blank=True, null=True, default=0)
    extra_height_charge = models.IntegerField(blank=True, null=True, default=0)
    extra_weight_charge = models.IntegerField(blank=True, null=True, default=0)
    loading_charge = models.IntegerField(blank=True, null=True, default=0)
    unloading_charge = models.IntegerField(blank=True, null=True, default=0)
    detention_charge = models.IntegerField(blank=True, null=True, default=0)
    # other_charges_for_company = models.IntegerField(blank=True, null=True, default=0)
    additional_charges_for_company = models.IntegerField(blank=True, null=True,
                                                         verbose_name="Additional Charges/Deductions for Company (+/-)",
                                                         default=0)
    remarks_about_additional_charges = models.TextField(blank=True, null=True,
                                                        verbose_name="Explanation Additional Charges/Deductions for Company (+/-)")
    additional_charges_for_owner = models.IntegerField(blank=True, null=True,
                                                       verbose_name="Additional Charges/Deductions for Owner (+/-)",
                                                       default=0)
    note_for_additional_owner_charges = models.TextField(blank=True, null=True,
                                                         verbose_name="Explanation Additional Charges/Deductions for Owner (+/-)")
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
    billing_address = models.CharField(max_length=300, blank=True, null=True)
    billing_contact_number = models.CharField(max_length=50, blank=True, null=True)
    billing_invoice_date = models.DateField(blank=True, null=True)
    invoice_remarks_for_additional_charges = models.TextField(blank=True, null=True)
    invoice_remarks_for_deduction_discount = models.TextField(blank=True, null=True)
    tds_deducted_amount = models.IntegerField(blank=True, null=True)

    booking_request_time = models.DateTimeField(blank=True, null=True)
    booking_confirmation_time = models.DateTimeField(blank=True, null=True)
    pod_date = models.DateTimeField(blank=True, null=True)
    pod_status = models.CharField(max_length=20, choices=POD_STATUS_CHOICES, blank=True, null=True, default='pending')
    pod = models.CharField(max_length=255, help_text='s3 file key', null=True, blank=True)
    pod_thumb = models.CharField(max_length=255, help_text='s3 file key', null=True, blank=True)
    pod_verified = models.BooleanField(default=False)
    outward_payment_status = models.CharField(max_length=20, choices=outward_status, blank=True, null=True)
    inward_payment_status = models.CharField(max_length=20, choices=inward_payment_status, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Vehicle(s) Allocated'

    def __str__(self):
        return "%s, %s,%s" % (self.transaction, self.vehicle_number, self.vehicle_number.vehicle_type.vehicle_type)

    def pod_details(self):
        return {
            'allocated_vehicle_id': self.id,
            'transaction_id': self.transaction_id,
            'pod': self.pod,
            'pod_status': self.pod_status,
            'pod_date': format_date(self.pod_date),
            'pod_thumb': self.pod_thumb,
            'pod_verified': self.pod_verified,
        }


class AllocatedVehicleLoadingUnloadingAddress(models.Model):
    allocated_vehicle = models.ForeignKey(VehicleAllocated, on_delete=models.CASCADE)
    loading_unloading_address = models.ForeignKey(LoadingUnloadingAddress, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class Insurance(models.Model):
    company_choice = (
        ('Sun Birla', 'Sun Birla'),
    )
    #is_insured = models.CharField(max_length=4, choices={('yes', 'YES'), ('no', 'NO')}, blank=True, null=True)
    company = models.CharField(max_length=255, choices=company_choice, blank=True, null=True)
    policy_number = models.CharField(max_length=30, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    amount = models.CharField(max_length=30, blank=True, null=True)
    risk = models.CharField(max_length=70, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Customer Insurance Details'

    def __str__(self):
        return self.policy_number


class PartyInvoice(models.Model):
    ITEM_CHOICE = (
        ("advance", "advance"),
        ("balance", "balance"),
        ("additional_charges", "additional charges")
    )
    transaction = models.ForeignKey(Transaction, null=True, blank=True, related_name='transactions', on_delete=models.CASCADE)
    item_description = models.CharField(max_length=200, choices=ITEM_CHOICE, blank=True, null=True)
    invoice_number = models.CharField(max_length=70, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    amount = models.CharField(max_length=70, blank=True, null=True)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Invoices'

    def __str__(self):
        return self.invoice_number


class LrDetails(models.Model):
    rate_choice = (
        ('kg', 'Kilogram'),
        ('cft', 'Cubic feet'),
        ('mt', 'Metric Ton'),
    )
    transaction = models.ForeignKey(Transaction, related_name='lr', blank=True, null=True, on_delete=models.CASCADE)
    lr_number = models.CharField(max_length=30, null=True)
    allocated_vehicle = models.ForeignKey(VehicleAllocated, blank=True, null=True, related_name='lr_num', on_delete=models.CASCADE)
    consignor = models.ForeignKey(ConsignorConsignee, blank=True, null=True, related_name='consignor_details', on_delete=models.CASCADE)
    consignee = models.ForeignKey(ConsignorConsignee, blank=True, null=True, related_name='consignee_details', on_delete=models.CASCADE)
    package = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    weight_actual = models.CharField(max_length=70, blank=True, null=True)
    weight_charged = models.CharField(max_length=70, blank=True, null=True)
    rate_type = models.CharField(max_length=30, choices=rate_choice, blank=True, null=True)
    rate = models.CharField(max_length=70, blank=True, null=True)
    freight_charge = models.CharField(max_length=70, blank=True, null=True)
    loading_charge = models.CharField(max_length=70, blank=True, null=True)
    unloading_charge = models.CharField(max_length=70, blank=True, null=True)
    lr_charge = models.CharField(max_length=20, blank=True, null=True)
    service_tax_charge = models.CharField(max_length=30, blank=True, null=True)
    insurance = models.ForeignKey(Insurance, blank=True, null=True, on_delete=models.CASCADE)
    reporting_datetime = models.DateTimeField(blank=True, null=True)
    unloading_datetime = models.DateTimeField(blank=True, null=True)
    delivery_address = models.ForeignKey(AahoOffice, blank=True, null=True, on_delete=models.CASCADE)
    lr_date = models.DateField(blank=True, null=True)
    from_city = models.CharField(max_length=70, blank=True, null=True)
    to_city = models.CharField(max_length=70, blank=True, null=True)
    lr_aaho = models.CharField(max_length=30, blank=True, null=True)
    road_permit_number = models.CharField(max_length=200, blank=True, null=True)
    liability_of_service_tax = models.CharField(max_length=200, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "LR Details"

    def __str__(self):
        return self.lr_number


class AppBooking(models.Model):
    booking_id = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    number_of_loading_points = models.CharField(max_length=255, blank=True, null=True)
    number_of_unloading_points = models.CharField(max_length=255, blank=True, null=True)
    pick_up_location = models.CharField(max_length=255, blank=True, null=True)
    pick_up_city = models.CharField(max_length=255, blank=True, null=True)
    drop_location = models.CharField(max_length=255, blank=True, null=True)
    drop_city = models.CharField(max_length=255, blank=True, null=True)
    vehicle_type = models.CharField(max_length=255, blank=True, null=True)
    number_of_vehicle = models.CharField(max_length=255, blank=True, null=True)
    shipment_datetime = models.DateTimeField(blank=True, null=True)
    total_weight = models.CharField(max_length=255, blank=True, null=True)
    material = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=255, blank=True, null=True)
    expected_rate = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.booking_id


class InWardPayment(models.Model):
    modes = (
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('neft', 'NEFT'),
        ('imps', 'IMPS'),
        ('rtgs', 'RTGS'),
        ('happay', 'Happay'),
        ('hdfc_internal_account', 'HDFC Internal Account'),
    )
    transaction = models.ManyToManyField(PartyInvoice, blank=True, related_name='payment')
    allocated_vehicle = models.ForeignKey(VehicleAllocated, null=True, blank=True,
                                          related_name="inward_payment_allocated_vehicle", on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=35, blank=True, null=True)
    received_from = models.CharField(max_length=300, null=True)
    payment_mode = models.CharField(max_length=40, choices=modes, blank=True, null=True)
    amount = models.IntegerField(default=0)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transaction_inwardpayment'

    def __str__(self):
        return str(self.payment_id)


class OutWardPayment(models.Model):
    modes = (
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('neft', 'NEFT'),
        ('imps', 'IMPS'),
        ('rtgs', 'RTGS'),
        ('happay', 'Happay'),
        ('hdfc_internal_account', 'HDFC Internal Account'),
    )
    transaction = models.ForeignKey(Transaction, blank=True, null=True, related_name='payment', on_delete=models.CASCADE)
    allocated_vehicle = models.ForeignKey(VehicleAllocated, null=True, blank=True,
                                          related_name="outward_payment_allocated_vehicle", on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=35, blank=True, null=True)
    paid_to = models.CharField(max_length=300, null=True)
    payment_mode = models.CharField(max_length=20, choices=modes, blank=True, null=True)
    amount = models.CharField(max_length=20, blank=True, null=True)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transaction_outwardpayment'

    def __str__(self):
        return str(self.payment_id)


class UserVendor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'user: %s, vendor: %s (%s)' % (self.user.username, self.name, self.phone)

    class Meta:
        unique_together = ('user', 'phone')


class TransactionVendorRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    vendor = models.ForeignKey(UserVendor, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'user: %s, transaction: %s, vendor: %s' % (self.user.username, self.transaction_id, self.vendor.name)


VENDOR_RESPONSE_STATUS = (
    ('new', 'new'),
    ('accepted', 'accepted'),
    ('declined', 'declined')
)


class VendorRequestResponse(models.Model):
    transaction = models.ForeignKey(Transaction, related_name='vendor_response', blank=True, null=True, on_delete=models.CASCADE)
    response_id = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    keyword = models.CharField(max_length=16, blank=True, null=True)
    vendor = models.ForeignKey(UserVendor, null=True, blank=True, related_name='transaction_vendor_response', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=VENDOR_RESPONSE_STATUS, default='new')
    datetime = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'transaction: %s, phone: %s, status: %s' % (str(self.transaction), self.phone, self.status)


class VehicleRequestQuote(models.Model):
    transaction = models.ForeignKey(Transaction, related_name='transaction_quotes', on_delete=models.CASCADE)
    vehicle_request = models.ForeignKey(VehicleRequest, related_name='vehicle_request_quotes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # FMS user
    quantity = models.PositiveIntegerField()
    # rename amount to vendor_amount
    amount = models.PositiveIntegerField(default=0)
    aaho_amount = models.PositiveIntegerField(default=0)
    comments = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('vehicle_request', 'user')

    def __str__(self):
        return 'user: %s, quantity: %s, amount: %s, transaction %s' % (
            str(self.user_id), self.quantity, self.amount, self.transaction)

    def to_json(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'vehicle_request_id': self.vehicle_request_id,
            'user_id': self.user_id,
            'quantity': self.quantity,
            'amount': self.amount,
            'comments': self.comments,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }
