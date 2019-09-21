from django_filters import rest_framework as filters

from restapi.filter.common import ListFilter
from supplier.models import Vehicle, Supplier, ContactPerson, DriverPhone, VehicleStatus, VehicleInsurer, \
    VehicleInsurance, VehiclePUC, VehicleFitness, VehiclePermit, Service, DriverVehicle, SupplierVehicle, Driver
from utils.models import VehicleBodyCategory


class VehicleFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    owner = ListFilter(name="suppliervehicle__supplier_id", label="Owner name")
    owner_null = filters.BooleanFilter(name="supplier", label="Is Owner Null", lookup_expr="isnull")
    vehicle_number = filters.CharFilter(name="vehicle_number", label="Vehicle Number", lookup_expr='icontains')

    vehicle_type = filters.NumberFilter(name="vehicle_type__id", label="Vehicle Type", lookup_expr='exact')
    vehicle_type_null = filters.BooleanFilter(name="vehicle_type", label="Is Vehicle Type Null", lookup_expr="isnull")

    vehicle_capacity = filters.NumberFilter(name="vehicle_capacity", label="vehicle Capacity", lookup_expr='icontains')
    vehicle_capacity_range = filters.NumericRangeFilter(name="vehicle_capacity", label="vehicle Capacity")

    chassis_number = filters.CharFilter(name="chassis_number", label="Chasis Number", lookup_expr='icontains')
    chassis_number_null = filters.BooleanFilter(name="chassis_number", label="Is Chasis Number Null",
                                                lookup_expr="isnull")
    engine_number = filters.CharFilter(name="engine_number", label="Engine Number", lookup_expr='icontains')
    engine_number_null = filters.BooleanFilter(name="engine_number", label="Is Engine Number Null",
                                               lookup_expr="isnull")

    registration_year = filters.DateFilter(name="registration_year", label="Registration year", lookup_expr='icontains')
    registration_year_null = filters.BooleanFilter(name="registration_year", label="Is Registration Year Null",
                                                   lookup_expr="isnull")
    registration_year_range = filters.DateFromToRangeFilter(name="registration_year", label="Registration Year range")

    registration_validity = filters.DateFilter(name="registration_validity", label="Registration Validity",
                                               lookup_expr='icontains')
    registration_validity_range = filters.DateFromToRangeFilter(name="registration_validity",
                                                                label="Registration Validity Range")

    gps_enabled = filters.BooleanFilter(name="gps_enabled", label="Is GPS Enable", lookup_expr="exact")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = Vehicle
        fields = []


class SupplierFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    name = filters.CharFilter(field_name='user__profile__name', lookup_expr='icontains', label='Supplier name')
    phone = filters.CharFilter(field_name='user__profile__phone', lookup_expr='icontains', label='Supplier Phone')
    code = filters.CharFilter(field_name='code', lookup_expr='iexact', label='Supplier Code')
    pan = filters.CharFilter(field_name='pan', lookup_expr='icontains', label='Supplier PAN')
    vehicle_id = filters.NumberFilter(field_name='suppliervehicle__vehicle__id', label='Vehicle Number',
                                      lookup_expr='exact')
    aaho_poc = ListFilter(name="aaho_poc__id", label="Aaho POC", lookup_expr='exact')
    aaho_poc_null = filters.BooleanFilter(name="aaho_poc", label="Is Aaho POC Null", lookup_expr="isnull")
    aaho_office = ListFilter(field_name='aaho_office_id', label="Aaho Office", lookup_expr='exact')
    aaho_office_null = filters.NumberFilter(field_name='aaho_office', label="Aaho Office", lookup_expr='isnull')

    class Meta:
        model = Supplier
        fields = []


class ContactPersonFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = ContactPerson
        fields = []


class DriverPhoneFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = DriverPhone
        fields = ['id', ]


class DriverFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    name = filters.CharFilter(field_name='user__profile__name', lookup_expr='icontains')
    phone = filters.CharFilter(field_name='user__profile__phone', lookup_expr='exact')
    driving_licence_number = filters.CharFilter(field_name='driving_licence_number', lookup_expr='icontains')

    class Meta:
        model = Driver
        fields = ['id', ]


class VehicleBodyCategoryFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = VehicleBodyCategory
        fields = ['id', ]


class VehicleStatusFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = VehicleStatus
        fields = ['id', ]


class VehicleInsurerFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = VehicleInsurer
        fields = ['id', ]


class VehicleInsuranceFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = VehicleInsurance
        fields = ['id', ]


class VehiclePUCFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = VehiclePUC
        fields = ['id', ]


class VehicleFitnessFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = VehicleFitness
        fields = ['id', ]


class VehiclePermitFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = VehiclePermit
        fields = ['id', ]


class ServiceFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = Service
        fields = ['id', ]


class DriverVehicleFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = DriverVehicle
        fields = ['id', ]


class SupplierVehicleFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")

    class Meta:
        model = SupplierVehicle
        fields = ['id', ]
