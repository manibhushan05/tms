from django_filters import rest_framework as filters

from owner.models import Owner, Vehicle, FuelCard
from restapi.filter.common import ListFilter


class OwnerFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    owner_name = filters.CharFilter(name="name__profile__name", label=" owner name", lookup_expr='icontains')
    owner_phone = filters.CharFilter(name="name__profile__phone", label=" owner phone", lookup_expr='icontains')
    name = filters.CharFilter(name="name__username", label=" name", lookup_expr='icontains')

    name_null = filters.BooleanFilter(name="name", label="Is Name Null", lookup_expr="isnull")

    address = filters.CharFilter(name="address__line1", label="Address", lookup_expr='icontains')
    address_null = filters.BooleanFilter(name="address", label="Is Address Null", lookup_expr="isnull")

    owner_address = filters.CharFilter(name="owner_address", label="Owner address", lookup_expr='icontains')
    owner_address_null = filters.BooleanFilter(name="owner_address", label="Is Owner Address Null",
                                               lookup_expr="isnull")

    city = filters.CharFilter(name="city__name", label="City Name", lookup_expr='icontains')
    city_null = filters.BooleanFilter(name="city", label="Is City Null", lookup_expr="isnull")

    route_source = filters.CharFilter(name="route__source__name", label="Route Source", lookup_expr='icontains')
    route_destination = filters.CharFilter(name="route__destination__name", label="Route Destination",
                                           lookup_expr='icontains')
    route_null = filters.BooleanFilter(name="route", label="Is Route Null", lookup_expr="isnull")

    route_temp = filters.CharFilter(name="route_temp", label="Route Temp",
                                    lookup_expr='icontains')
    route_temp_null = filters.BooleanFilter(name="route_temp", label="Is Route Temp Null", lookup_expr="isnull")

    pan = filters.CharFilter(name="pan", label="PAN", lookup_expr='icontains')
    pan_null = filters.BooleanFilter(name="pan", label="Is PAN Null", lookup_expr="isnull")

    vehicles_detail = filters.CharFilter(name="vehicles_detail", label="Vehicle Detail", lookup_expr='icontains')
    vehicles_detail_null = filters.BooleanFilter(name="vehicles_detail", label="Is Vehicle Detail Null",
                                                 lookup_expr="isnull")

    account_details_null = filters.BooleanFilter(name="account_details", label="Is Account Details Null",
                                                 lookup_expr="isnull")
    account_number = filters.CharFilter(name="account_details__account_number", label="Account Number",
                                        lookup_expr='exact')
    bank_name = filters.CharFilter(name="account_details__bank", label="Bank Name", lookup_expr='icontains')
    ifsc = filters.CharFilter(name="account_details__ifsc", label="IFSC Code", lookup_expr='icontains')
    service_tax_number = filters.CharFilter(name="taxation_details__service_tax_number", label="Service Tax Number",
                                            lookup_expr='exact')
    taxation_details_null = filters.BooleanFilter(name="taxation_details", label="Is Taxation Details Null",
                                                  lookup_expr="isnull")

    declaration = filters.CharFilter(name="declaration", label="Declaration", lookup_expr='icontains')
    declaration_null = filters.BooleanFilter(name="declaration", label="Is Declaration Null", lookup_expr="isnull")

    declaration_validity = filters.DateFilter(name="declaration_validity", label="Declaration Validity",
                                              lookup_expr='icontains')
    declaration_validity_null = filters.BooleanFilter(name="declaration_validity", label="Is Declaration Validity Null",
                                                      lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    # Reverse relations
    serial = filters.CharFilter(name="owner_files__serial", label="Owner Files Serial", lookup_expr="icontains")
    verified = filters.BooleanFilter(name="owner_files__verified", label="Owner Files Verified", lookup_expr="exact")
    vehicle_id = ListFilter(field_name='vehicle_owner__id', label='Vehicle Number')

    # aaho_poc = filters.NumberFilter(name="aaho_poc__id", label="Aaho POC", lookup_expr='exact')
    # aaho_poc_null = filters.BooleanFilter(name="aaho_poc", label="Is Aaho POC Null", lookup_expr="isnull")
    # aaho_office = filters.NumberFilter(field_name='aaho_office_id', label="Aaho Office", lookup_expr='exact')
    # aaho_office_null = filters.NumberFilter(field_name='aaho_office', label="Aaho Office", lookup_expr='isnull')

    class Meta:
        model = Owner
        fields = []


class OwnerVehicleFilter(filters.FilterSet):
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
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    owner = ListFilter(name="owner__id", label="Owner name")
    owner_null = filters.BooleanFilter(name="owner", label="Is Owner Null", lookup_expr="isnull")

    driver = ListFilter(name="driver__id", label="Driver name")
    driver_null = filters.BooleanFilter(name="driver", label="Is Driver Null", lookup_expr="isnull")

    vehicle_number = filters.CharFilter(name="vehicle_number", label="Vehicle Number", lookup_expr='icontains')

    route_source = filters.CharFilter(name="route__source__name", label="Route Source", lookup_expr='icontains')
    route_destination = filters.CharFilter(name="route__destination__name", label="Route Destination",
                                           lookup_expr='icontains')
    route_null = filters.BooleanFilter(name="route", label="Is Route Null", lookup_expr="isnull")

    rc_number = filters.CharFilter(name="rc_number", label="RC Number", lookup_expr='icontains')
    rc_number_null = filters.BooleanFilter(name="rc_number", label="Is RC Number Null", lookup_expr="isnull")

    permit = filters.CharFilter(name="permit", label="Permit", lookup_expr='icontains')
    permit_null = filters.BooleanFilter(name="permit", label="Is Permit Null", lookup_expr="isnull")

    permit_validity = filters.DateFilter(name="permit_validity", label="Permit Validity", lookup_expr='icontains')
    permit_validity_null = filters.BooleanFilter(name="permit_validity", label="Is Permit Validity Null",
                                                 lookup_expr="isnull")

    permit_type = filters.CharFilter(name="permit_type", label="Permit Type", lookup_expr='icontains')
    permit_type_null = filters.BooleanFilter(name="permit_type", label="Is Permit Type Null", lookup_expr="isnull")

    vehicle_type = filters.NumberFilter(name="vehicle_type__id", label="Vehicle Type", lookup_expr='exact')
    vehicle_type_null = filters.BooleanFilter(name="vehicle_type", label="Is Vehicle Type Null", lookup_expr="isnull")

    vehicle_capacity = filters.NumberFilter(name="vehicle_capacity", label="vehicle Capacity", lookup_expr='icontains')
    vehicle_capacity_range = filters.NumericRangeFilter(name="vehicle_capacity", label="vehicle Capacity")

    body_type = filters.ChoiceFilter(name="body_type", label="Body Type", choices=body_type_choice)

    body_type_null = filters.BooleanFilter(name="body_type", label="Is Body Type Null", lookup_expr="isnull")

    vehicle_model = filters.CharFilter(name="vehicle_model", label="Vehicle Model", lookup_expr='icontains')
    chassis_number = filters.CharFilter(name="chassis_number", label="Chasis Number", lookup_expr='icontains')
    chassis_number_null = filters.BooleanFilter(name="chassis_number", label="Is Chasis Number Null",
                                                lookup_expr="isnull")
    engine_number = filters.CharFilter(name="engine_number", label="Engine Number", lookup_expr='icontains')
    engine_number_null = filters.BooleanFilter(name="engine_number", label="Is Engine Number Null",
                                               lookup_expr="isnull")

    insurer = filters.CharFilter(name="insurer", label="Insurer", lookup_expr='icontains')
    insurance_number = filters.CharFilter(name="insurance_number", label="Insurance Number", lookup_expr='icontains')

    insurance_validity = filters.DateFilter(name="insurance_validity", label="Insurance Validity",
                                            lookup_expr='icontains')
    insurance_validity_null = filters.BooleanFilter(name="insurance_validity", label="Is Insurance Validity Null",
                                                    lookup_expr="isnull")
    registration_year = filters.DateFilter(name="registration_year", label="Registration year", lookup_expr='icontains')
    registration_year_null = filters.BooleanFilter(name="registration_year", label="Is Registration Year Null",
                                                   lookup_expr="isnull")
    registration_year_range = filters.DateFromToRangeFilter(name="registration_year", label="Registration Year range")

    registration_validity = filters.DateFilter(name="registration_validity", label="Registration Validity",
                                               lookup_expr='icontains')
    registration_validity_range = filters.DateFromToRangeFilter(name="registration_validity",
                                                                label="Registration Validity Range")

    fitness_certificate_number = filters.CharFilter(name="fitness_certificate_number",
                                                    label="Fitness Certificate Number", lookup_expr='icontains')
    fitness_certificate_number_null = filters.BooleanFilter(name="fitness_certificate_number",
                                                            label="Is Fitness Certificate Number Null",
                                                            lookup_expr="isnull")

    fitness_certificate_issued_on = filters.DateFilter(name="fitness_certificate_issued_on",
                                                       label="Fitness Certificate issued on",
                                                       lookup_expr='icontains')
    fitness_certificate_issued_on_range = filters.DateFromToRangeFilter(name="fitness_certificate_issued_on",
                                                                        label="Fitness Certificate issued on Range")

    puc_certificate_number = filters.CharFilter(name="puc_certificate_number",
                                                label="PUC Certificate Number Null", lookup_expr='icontains')
    puc_certificate_number_null = filters.BooleanFilter(name="puc_certificate_number",
                                                        label="Is PUC Certificate Number Null",
                                                        lookup_expr="isnull")

    puc_certificate_issued_on = filters.DateFilter(name="puc_certificate_issued_on", label="PUC Certificate issued on",
                                                   lookup_expr='icontains')
    puc_certificate_issued_on_range = filters.DateFromToRangeFilter(name="puc_certificate_issued_on",
                                                                    label="PUC Certificate issued on Range")

    status = filters.ChoiceFilter(name="status", label="Status", choices=vehicle_status_choice)

    status_null = filters.BooleanFilter(name="status", label="Is Status Null", lookup_expr="isnull")

    gps_enabled = filters.BooleanFilter(name="gps_enabled", label="Is GPS Enable", lookup_expr="exact")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    # Reverse relations
    serial = filters.CharFilter(name="vehicle_files__serial", label="Vehicle Files Serial", lookup_expr="icontains")
    verified = filters.BooleanFilter(name="vehicle_files__verified", label="Vehicle Files Verified",
                                     lookup_expr="exact")


    class Meta:
        model = Vehicle
        fields = []


class FuelCardFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    customer_id = filters.CharFilter(name="customer_id", label="Customer Id", lookup_expr='icontains')
    customer_id_null = filters.BooleanFilter(name="customer_id", label="Is Customer Id Null", lookup_expr="isnull")

    card_number = filters.CharFilter(name="card_number", label="card_number", lookup_expr='icontains')
    card_number_null = filters.BooleanFilter(name="card_number", label="Is card_number Null", lookup_expr="isnull")

    issue_date = filters.DateFilter(name="issue_date", label="Issue Date", lookup_expr='icontains')
    issue_date_null = filters.BooleanFilter(name="issue_date", label="Is Issue Date Null",
                                            lookup_expr="isnull")
    issue_date_range = filters.DateFromToRangeFilter(name="issue_date", label="Issue Date range")

    expiry_date = filters.DateFilter(name="expiry_date", label="Rxpiry Date", lookup_expr='icontains')
    expiry_date_null = filters.BooleanFilter(name="expiry_date", label="Is Expiry Date Null",
                                             lookup_expr="isnull")
    expiry_date_range = filters.DateFromToRangeFilter(name="expiry_date", label="Expiry Date range")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = FuelCard
        fields = []
