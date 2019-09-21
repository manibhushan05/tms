from django_filters import rest_framework as filters

from restapi.filter.common import ListFilter
from sme.models import Sme, SmeTaskEmail, RateType, CustomerContract, ContractRoute, ContactDetails, Location, \
    ConsignorConsignee, PreferredVehicle


class SmeTaskEmailFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    name = filters.CharFilter(name="name", label="Sme Task Email Name", lookup_expr="icontains")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = SmeTaskEmail
        fields = []


IS_GST_APPLICABLE_CHOICE = (
    ('yes', 'Yes'),
    ('no', 'No'),
    ('unknown', 'Unknown')
)

LR_FORMAT_CHOICE = (
    ('S', 'Serial'),
    ('D', 'Default')
)


class SmeFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    name = filters.CharFilter(name="name__username", label="Sme name", lookup_expr='icontains')
    name_null = filters.BooleanFilter(name="name", label="Is Name Null", lookup_expr="isnull")
    company_name = filters.CharFilter(name="name__profile__name", label="Customer name", lookup_expr='icontains')

    email_tasks = filters.CharFilter(name='email_tasks__name', label="Name of Email Task", lookup_expr="icontains")
    company_code = filters.CharFilter(name='company_code', label="Company Code", lookup_expr="iexact")
    company_code_null = filters.BooleanFilter(name="company_code", label="Is Company Code Null", lookup_expr="isnull")

    latest_lr_serial_number = filters.NumberFilter(name="latest_lr_serial_number", label="Latest LR Serial Number")
    latest_lr_serial_number_between = filters.NumericRangeFilter(name="latest_lr_serial_number",
                                                                 label="Latest LR Serial Number Between")

    lr_format_type = filters.ChoiceFilter(name="lr_format_type", choices=LR_FORMAT_CHOICE)

    address = filters.CharFilter(name="address__line1", label="Sme address", lookup_expr='icontains')
    address_null = filters.BooleanFilter(name="address", label="Is Address Null", lookup_expr="isnull")

    customer_address = filters.CharFilter(name="customer_address", label="Customer Address")
    customer_address_null = filters.BooleanFilter(name="customer_address", label="Is Customer Address Null",
                                                  lookup_expr="isnull")

    credit_period = filters.CharFilter(name="credit_period", label="Credit Period", lookup_expr='icontains')
    credit_period_null = filters.BooleanFilter(name="credit_period", label="Credit Period", lookup_expr="isnull")

    aaho_poc = ListFilter(name="aaho_poc__id", label="Aaho POC")
    aaho_poc_null = filters.BooleanFilter(name="aaho_poc", label="Is Aaho POC Null", lookup_expr="isnull")

    city = filters.CharFilter(name="city__name", label="City Name", lookup_expr='icontains')
    city_null = filters.BooleanFilter(name="city", label="Is City Null", lookup_expr="isnull")

    pin = filters.CharFilter(name="pin", label="PIN", lookup_expr='icontains')
    pin_null = filters.BooleanFilter(name="pin", label="Is PIN Null", lookup_expr="isnull")

    gstin = filters.CharFilter(name="gstin", label="GSTIN", lookup_expr='icontains')
    gstin_null = filters.BooleanFilter(name="gstin", label="Is GSTIN Null", lookup_expr="isnull")

    is_gst_applicable = filters.ChoiceFilter(name="is_gst_applicable", label="Is GST Applicable",
                                             choices=IS_GST_APPLICABLE_CHOICE)

    id_proof = filters.CharFilter(name="id_proof", label="ID Proof", lookup_expr='icontains')
    id_proof_null = filters.BooleanFilter(name="id_proof", label="Is ID Proof Null", lookup_expr="isnull")
    account_details_null = filters.BooleanFilter(name="account_details", label="Is Account Details Null",
                                                 lookup_expr="isnull")
    account_number = filters.CharFilter(name="account_details__acount_number", label="Account Number",
                                        lookup_expr='exact')
    bank_name = filters.CharFilter(name="account_details__bank", label="Bank Name", lookup_expr='icontains')
    ifsc = filters.CharFilter(name="account_details__ifsc", label="IFSC Code", lookup_expr='icontains')

    service_tax_number = filters.CharFilter(name="taxation_details__service_tax_number", label="Service Tax Number",
                                            lookup_expr='exact')
    taxation_details_null = filters.BooleanFilter(name="taxation_details", label="Is Taxation Details Null",
                                                  lookup_expr="isnull")

    status = filters.ChoiceFilter(name="status", choices=(('active', 'active'), ('inactive', 'inactive')),
                                  label="Status")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    # Reverse relations
    cheque_number = filters.CharFilter(name="cheque_files__cheque_number", label="Cheque Files Cheque Number",
                                       lookup_expr="icontains")
    cheque_date = filters.DateFilter(name="cheque_files__cheque_date", label="Cheque Files Cheque Date")
    serial = filters.CharFilter(name="cheque_files__serial", label="Cheque Files Serial", lookup_expr="icontains")

    aaho_office = ListFilter(field_name='aaho_office_id', label="Aaho Office")
    aaho_office_null = filters.NumberFilter(field_name='aaho_office', label="Aaho Office", lookup_expr='isnull')

    class Meta:
        model = Sme
        fields = []


class RateTypeFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    name = filters.CharFilter(name="name", label="Rate Type Name", lookup_expr="icontains")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = RateType
        fields = []


BILLING_FREQUENCY_CHOICES = (
    ('d', 'Daily'),
    ('w', 'Weekly'),
    ('m', 'Monthly'),
    ('f', 'Fort Nightly'),
    ('o', 'Others'),
)


class CustomerContractFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    customer_name = filters.CharFilter(name="customer__name__username", label="Customer name", lookup_expr="icontains")
    customer_name_null = filters.BooleanFilter(name="customer__name__username", label="Is Customer name Null",
                                               lookup_expr='isnull')
    customer_code = filters.CharFilter(name="customer__company_code", label="Customer name")
    customer_code_null = filters.BooleanFilter(name="customer__name__username", label="Is Customer name Null",
                                               lookup_expr="isnull")
    start_date_between = filters.DateTimeFromToRangeFilter(name="start_date", label="Start Date Between")
    billing_frequency = filters.ChoiceFilter(name="billing_frequency", choices=BILLING_FREQUENCY_CHOICES)
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = CustomerContract
        fields = []


class ContractRouteFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    source = filters.CharFilter(name="source__name", label="Source City name", lookup_expr="icontains")
    source_null = filters.BooleanFilter(name="source", label="Is Source name Null", lookup_expr='isnull')

    destination = filters.CharFilter(name="destination__name", label="Destination name", lookup_expr="icontains")
    destination_null = filters.BooleanFilter(name="destination", label="Is Destination name Null", lookup_expr="isnull")

    rate_type = filters.CharFilter(name="rate_type__name", label="Rate Type name", lookup_expr="icontains")
    rate_type_null = filters.BooleanFilter(name="rate_type", label="Is Rate Type name Null", lookup_expr="isnull")

    rate_range = filters.NumericRangeFilter(name="rate", label="Rate Range")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = ContractRoute
        fields = []


class ContactDetailsFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    sme = filters.CharFilter(name="sme__name__username", label="Sme name", lookup_expr="icontains")
    type = filters.ChoiceFilter(name="type", choices=(('primary', 'primary'), ('secondary', 'secondary')), label="Type")
    name = filters.CharFilter(name="name", label="Name", lookup_expr="icontains")
    name_null = filters.BooleanFilter(name="name", label="Is name null", lookup_expr="isnull")
    phone = filters.CharFilter(name="phone", label="Phone", lookup_expr="icontains")
    phone_null = filters.BooleanFilter(name="phone", label="Is Phone null", lookup_expr="isnull")

    email = filters.CharFilter(name="email", label="Email", lookup_expr="icontains")
    email_null = filters.BooleanFilter(name="email", label="Is Email null", lookup_expr="isnull")

    designation = filters.CharFilter(name="designation", label="Designation", lookup_expr="icontains")
    designation_null = filters.BooleanFilter(name="designation", label="Is Designation null", lookup_expr="isnull")

    status = filters.ChoiceFilter(name="status", choices=(('active', 'active'), ('inactive', 'inactive')), label="Type")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = ContactDetails
        fields = []


location_choice = (
    ('loading', 'loading'),
    ('unloading', 'unloading'),
)


class LocationFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    type = filters.ChoiceFilter(name="type", choices=location_choice, label="Type")
    sme = filters.CharFilter(name="sme__name__username", label="Sme name", lookup_expr="icontains")
    sme_null = filters.BooleanFilter(name="sme", label="Is SME Null", lookup_expr="isnull")

    company_code = filters.CharFilter(name='sme__company_code', label="Company Code", lookup_expr="exact")
    company_code_null = filters.BooleanFilter(name="sme__company_code", label="Is Company Code Null",
                                              lookup_expr="isnull")

    contact = filters.CharFilter(name="contact__name", label="Contact Name", lookup_expr="icontains")
    contact_null = filters.BooleanFilter(name="contact", label="Is Contact Null", lookup_expr="isnull")

    address = filters.CharFilter(name="address", label="Address", lookup_expr="icontains")
    address_null = filters.BooleanFilter(name="address", label="Is Address Null", lookup_expr="isnull")

    city = filters.CharFilter(name="city__name", label="City Name", lookup_expr='icontains')
    city_null = filters.BooleanFilter(name="city", label="Is City Null", lookup_expr="isnull")

    material = filters.CharFilter(name="material", label="Material", lookup_expr='icontains')
    material_null = filters.BooleanFilter(name="material", label="Is Material Null", lookup_expr="isnull")

    status = filters.ChoiceFilter(name="status", choices=(('active', 'active'), ('inactive', 'inactive')), label="Type")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = Location
        fields = []


class ConsignorConsigneeFilter(filters.FilterSet):
    choices = (
        ('consignor', 'consignor'),
        ('consignee', 'consignee'),
    )

    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    type = filters.ChoiceFilter(name="type", choices=choices, label="Type")
    sme = filters.CharFilter(name="sme__name__username", label="Sme name", lookup_expr="icontains")
    sme_null = filters.BooleanFilter(name="sme", label="Is SME Null", lookup_expr="isnull")

    company_code = filters.CharFilter(name='sme__company_code', label="Company Code", lookup_expr="exact")
    company_code_null = filters.BooleanFilter(name="sme__company_code", label="Is Company Code Null",
                                              lookup_expr="isnull")

    name = filters.CharFilter(name="name", label="Name", lookup_expr="icontains")
    name_null = filters.BooleanFilter(name="name", label="Is name null", lookup_expr="isnull")

    address = filters.CharFilter(name="address", label="Address", lookup_expr="icontains")
    address_null = filters.BooleanFilter(name="address", label="Is Address Null", lookup_expr="isnull")

    city = filters.CharFilter(name="city__name", label="City Name", lookup_expr='icontains')
    city_null = filters.BooleanFilter(name="city", label="Is City Null", lookup_expr="isnull")

    pin = filters.CharFilter(name="pin", label="PIN", lookup_expr='icontains')
    pin_null = filters.BooleanFilter(name="pin", label="Is PIN Null", lookup_expr="isnull")

    phone = filters.CharFilter(name="phone", label="Phone", lookup_expr="icontains")
    phone_null = filters.BooleanFilter(name="phone", label="Is Phone null", lookup_expr="isnull")

    tax_id = filters.CharFilter(name="tax_id", label="Tax ID", lookup_expr="icontains")
    tax_id_null = filters.BooleanFilter(name="tax_id", label="Is Tax ID null", lookup_expr="isnull")

    status = filters.ChoiceFilter(name="status", choices=(('active', 'active'), ('inactive', 'inactive')), label="Type")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = ConsignorConsignee
        fields = []


class PreferredVehicleFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    sme = filters.CharFilter(name="sme__name__username", label="Sme name", lookup_expr="icontains")
    sme_null = filters.BooleanFilter(name="sme", label="Is SME Null", lookup_expr="isnull")

    company_code = filters.CharFilter(name='sme__company_code', label="Company Code", lookup_expr="exact")
    company_code_null = filters.BooleanFilter(name="sme__company_code", label="Is Company Code Null",
                                              lookup_expr="isnull")

    vehicle_type = filters.CharFilter(name='category__vehicle_type', label="Vehicle Type", lookup_expr="exact")
    truck_body_type = filters.CharFilter(name='category__truck_body_type', label="Truck Body Type", lookup_expr="exact")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = PreferredVehicle
        fields = []
