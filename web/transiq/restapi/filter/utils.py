from django_filters import rest_framework as filters

from utils.models import Bank, City, AahoOffice, VehicleCategory


class BankFilter(filters.FilterSet):
    account_choices = (
        ('SA', 'Saving Account'),
        ('CA', 'Current Account'),
        ('KCC', 'Kisan Credit Card'),
        ('RA', 'Recurring Account'),
    )
    transaction_type_choice = (
        ('neft', 'NEFT'),
        ('rtgs', 'RTGS'),
        ('both', 'Both'),
        ('hdfc_internal_account', 'HDFC Internal Account'),
    )
    status = (
        ('active', 'Active'),
        ('inactive', 'Inactive')
    )

    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    user = filters.CharFilter(name="user__username", label="User name", lookup_expr='icontains')

    user_null = filters.BooleanFilter(name="name", label="Is Username Null", lookup_expr="isnull")

    bank = filters.CharFilter(name="bank", label="bank", lookup_expr='icontains')
    bank_null = filters.BooleanFilter(name="bank", label="Is bank Null", lookup_expr="isnull")

    account_holder_name = filters.CharFilter(name="account_holder_name", label="account_holder_name",
                                             lookup_expr="icontains")
    account_holder_name_null = filters.BooleanFilter(name="account_holder_name", label="Is account_holder_name Null",
                                                     lookup_expr="isnull")

    beneficiary_code = filters.CharFilter(name="beneficiary_code", label="beneficiary_code", lookup_expr="exact")
    beneficiary_code_null = filters.BooleanFilter(name="beneficiary_code", label="Is beneficiary_code Null",
                                                  lookup_expr="isnull")

    account_number = filters.CharFilter(name="account_number",
                                        label="account_number", lookup_expr='icontains')
    account_number_null = filters.BooleanFilter(name="account_number",
                                                label="Is account_number Null", lookup_expr="isnull")

    transaction_type = filters.ChoiceFilter(name="transaction_type",
                                            label="transaction_type", choices=transaction_type_choice)
    transaction_type_null = filters.BooleanFilter(
        name="transaction_type", label="Is transaction_type Null", lookup_expr="isnull")

    account_type = filters.ChoiceFilter(name="account_type", choices=account_choices,
                                        label="account_type")
    account_type_null = filters.BooleanFilter(name="account_type", label="Is account_type Null", lookup_expr="isnull")

    ifsc = filters.CharFilter(name="ifsc", label="IFSC Code", lookup_expr='icontains')
    ifsc_null = filters.BooleanFilter(name="ifsc", label="Is IFSC Null",
                                      lookup_expr="isnull")

    address = filters.CharFilter(name="address", label="Address", lookup_expr='icontains')
    address_null = filters.BooleanFilter(name="address", label="Is Address Null", lookup_expr="isnull")

    city = filters.CharFilter(name="city", label="City Name", lookup_expr='icontains')
    city_null = filters.BooleanFilter(name="city", label="Is City Null", lookup_expr="isnull")

    remarks = filters.CharFilter(field_name="remarks", label="Remarks", lookup_expr="icontains")
    remarks_null = filters.BooleanFilter(field_name="remarks", label="Is Remarks Null", lookup_expr="isnull")

    is_verified = filters.ChoiceFilter(name="is_verified", choices=[('yes', 'Yes'), ('no', 'No')], label="Is verified")
    is_verified_null = filters.BooleanFilter(name="is_verified", lookup_expr="icontains", label="Is verified Null")

    status = filters.ChoiceFilter(name="status", label="status", choices=status)
    status_null = filters.BooleanFilter(name="status", label="Is status Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between",lookup_expr='range')

    class Meta:
        model = Bank
        fields = []


class CityFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    name = filters.CharFilter(name="name", label="City Name", lookup_expr='icontains')
    name_null = filters.BooleanFilter(name="name", label="Is City Null", lookup_expr="isnull")
    code = filters.CharFilter(name="code", label="City Code", lookup_expr='icontains')
    code_null = filters.BooleanFilter(name="code", label="Is City Null", lookup_expr="isnull")
    state_name = filters.CharFilter(name="state__name", label="State Name", lookup_expr='icontains')
    state_name_null = filters.BooleanFilter(name="state", label="Is State Null", lookup_expr="isnull")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = City
        fields = []


class AahoOfficeFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    branch_name = filters.CharFilter(name="branch_name", label="Aaho Office Name", lookup_expr='icontains')
    branch_name_null = filters.BooleanFilter(name="branch_name", label="Is Aaho Office Name Null", lookup_expr="isnull")
    branch = filters.CharFilter(name="branch__name", label="Aaho Office Branch", lookup_expr='icontains')
    branch_null = filters.BooleanFilter(name="branch", label="Is Aaho Office Branch Null", lookup_expr="isnull")
    address = filters.CharFilter(name="address", label="Aaho Office Address Name", lookup_expr='icontains')
    address_null = filters.BooleanFilter(name="address", label="Is Aaho Office Address Name Null", lookup_expr="isnull")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = AahoOffice
        fields = []


class VehicleCategoryFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    vehicle_type = filters.CharFilter(name="vehicle_type", label="Vehicle Type", lookup_expr='icontains')
    vehicle_type_null = filters.BooleanFilter(name="vehicle_type", label="Is Vehicle Type Null", lookup_expr="isnull")
    capacity = filters.CharFilter(name="capacity", label="Capacity", lookup_expr='icontains')
    capacity_null = filters.BooleanFilter(name="capacity", label="Is Capacity Null", lookup_expr="isnull")
    truck_body_type = filters.CharFilter(name="truck_body_type", label="Truck Body Type", lookup_expr='icontains')
    truck_body_type_null = filters.BooleanFilter(name="truck_body_type", label="Is Truck Body Type Null",
                                                 lookup_expr="isnull")
    truck_body_name = filters.CharFilter(name="truck_body__name", label="Truck Body Name", lookup_expr='icontains')
    truck_body_name_null = filters.BooleanFilter(name="truck_body", label="Is Truck Body Name Null",
                                                 lookup_expr="isnull")
    description = filters.CharFilter(name="description", label="Description", lookup_expr='icontains')
    description_null = filters.BooleanFilter(name="description", label="Is Description Null",
                                             lookup_expr="isnull")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = VehicleCategory
        fields = []
