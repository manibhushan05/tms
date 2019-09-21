from django_filters import rest_framework as filters

from driver.models import Driver, GPSDevice, GPSDeviceProvider


class DriverFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    name = filters.CharFilter(name="name", label="Broker name", lookup_expr='icontains')

    name_null = filters.BooleanFilter(name="name", label="Is Name Null", lookup_expr="isnull")

    address = filters.CharFilter(name="address__line1", label="Broker address", lookup_expr='icontains')
    address_null = filters.BooleanFilter(name="address", label="Is Address Null", lookup_expr="isnull")

    phone = filters.CharFilter(name="phone", label="phone", lookup_expr="exact")
    phone_null = filters.BooleanFilter(name="phone", label="Is Phone Null", lookup_expr="isnull")

    alt_phone = filters.CharFilter(name="alt_phone", label="alt_phone", lookup_expr="exact")
    alt_phone_null = filters.BooleanFilter(name="alt_phone", label="Is alt_phone Null", lookup_expr="isnull")

    driving_licence_number = filters.CharFilter(name="driving_licence_number",
                                                label="driving_licence_number", lookup_expr='icontains')
    driving_licence_number_null = filters.BooleanFilter(name="driving_licence_number",
                                                        label="Is driving_licence_number Null", lookup_expr="isnull")

    driving_licence_location = filters.CharFilter(name="driving_licence_location",
                                                  label="driving_licence_location", lookup_expr='icontains')
    driving_licence_location_null = filters.BooleanFilter(name="driving_licence_location",
                                                          label="Is driving_licence_location Null",
                                                          lookup_expr="isnull")

    driving_licence_validity = filters.IsoDateTimeFilter(name="driving_licence_validity",
                                                         label="driving_licence_validity")
    driving_licence_validity_between = filters.DateTimeFromToRangeFilter(name="driving_licence_validity",
                                                                         label="driving_licence_validity Between")

    service_tax_number = filters.CharFilter(name="taxation_id__service_tax_number", label="Service Tax Number",
                                            lookup_expr='exact')
    taxation_id_null = filters.BooleanFilter(name="taxation_id", label="Is Taxation Details Null",
                                             lookup_expr="isnull")

    account_details_null = filters.BooleanFilter(name="account_details", label="Is Account Details Null",
                                                 lookup_expr="isnull")
    account_number = filters.CharFilter(name="account_details__account_number", label="Account Number",
                                        lookup_expr='exact')
    bank_name = filters.CharFilter(name="account_details__bank", label="Bank Name", lookup_expr='icontains')
    ifsc = filters.CharFilter(name="account_details__ifsc", label="IFSC Code", lookup_expr='icontains')

    route = filters.CharFilter(name="route", label="Route", lookup_expr='icontains')
    route_null = filters.BooleanFilter(name="route", label="Is Route Null", lookup_expr="isnull")

    priority_level = filters.CharFilter(name="priority_level", label="priority_level", lookup_expr='icontains')
    priority_level_null = filters.BooleanFilter(name="priority_level", label="Is priority_level Null",
                                                lookup_expr="isnull")

    id_proof = filters.CharFilter(name="id_proof", label="ID Proof", lookup_expr='icontains')
    id_proof_null = filters.BooleanFilter(name="id_proof", label="Is ID Proof Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = Driver
        fields = []


class GPSDeviceProviderFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    name = filters.CharFilter(field_name='name', label='Name', lookup_expr='icontains')

    class Meta:
        model = GPSDeviceProvider
        fields = []


class GPSDeviceFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    device_id = filters.CharFilter(field_name='device_id', label='Device ID', lookup_expr='icontains')
    location_time_between = filters.DateTimeFromToRangeFilter(name="location_time", label="Location Time Between",
                                                              lookup_expr='range')
    vehicle = filters.NumberFilter(field_name='vehicle__id', label='Vehicle Number', lookup_expr='exact')
    driver = filters.NumberFilter(field_name='driver__id', label='Driver', lookup_expr='exact')
    gps_device_provider = filters.NumberFilter(field_name='device_provider__id', label='GPS Device Provider',
                                               lookup_expr='exact')

    class Meta:
        model = GPSDevice
        fields = []
