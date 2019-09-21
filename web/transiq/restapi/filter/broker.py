from django_filters import rest_framework as filters

from broker.models import Broker, BrokerVehicle, BrokerOwner, BrokerDriver, BrokerAccount
from restapi.filter.common import ListFilter


class BrokerFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    name = filters.CharFilter(name="name__username", label="Broker name", lookup_expr='icontains')
    broker_name=filters.CharFilter(field_name='name__profile__name',lookup_expr='icontains',label='Broker name')
    broker_phone=filters.CharFilter(field_name='name__profile__phone',lookup_expr='icontains',label='Broker Phone')

    name_null = filters.BooleanFilter(name="name", label="Is Name Null", lookup_expr="isnull")

    address = filters.CharFilter(name="address__line1", label="Broker address", lookup_expr='icontains')
    address_null = filters.BooleanFilter(name="address", label="Is Address Null", lookup_expr="isnull")
    code = filters.CharFilter(name="code", label="code", lookup_expr="exact")
    code_null = filters.BooleanFilter(name="code", label="Is Code Null", lookup_expr="isnull")
    city = filters.CharFilter(name="city__name", label="City Name", lookup_expr='icontains')
    city_null = filters.BooleanFilter(name="city", label="Is City Null", lookup_expr="isnull")
    route = filters.CharFilter(name="route", label="Route", lookup_expr='icontains')
    route_null = filters.BooleanFilter(name="route", label="Is Route Null", lookup_expr="isnull")

    pan = filters.CharFilter(name="pan", label="PAN", lookup_expr='icontains')
    pan_null = filters.BooleanFilter(name="pan", label="Is PAN Null", lookup_expr="isnull")
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
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")
    vehicle_id = filters.NumberFilter(field_name='broker_vehicle__vehicle__id', label='Vehicle Number',
                                        lookup_expr='exact')
    aaho_poc = ListFilter(name="aaho_poc__id", label="Aaho POC", lookup_expr='exact')
    aaho_poc_null = filters.BooleanFilter(name="aaho_poc", label="Is Aaho POC Null", lookup_expr="isnull")
    aaho_office = ListFilter(field_name='aaho_office_id', label="Aaho Office", lookup_expr='exact')
    aaho_office_null = filters.NumberFilter(field_name='aaho_office', label="Aaho Office", lookup_expr='isnull')


    class Meta:
        model = Broker
        fields = []


class BrokerVehicleFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    broker = filters.CharFilter(name="broker__name__username", label="Broker name", lookup_expr='icontains')

    vehicle_number = filters.CharFilter(name="vehicle__number", label="Vehicle Number", lookup_expr='exact')
    vehicle_body_type = filters.CharFilter(name="vehicle__body_type", label="Vehicle Body Type",
                                           lookup_expr="icontains")
    datetime = filters.IsoDateTimeFilter(name="datetime", label="Datetime")
    latest = filters.BooleanFilter(name="latest", label="Latest")
    deleted = filters.BooleanFilter(name="deleted", label="Deleted")

    account_details_null = filters.BooleanFilter(name="account_details", label="Is Account Details Null",
                                                 lookup_expr="isnull")
    account_number = filters.CharFilter(name="account_details__acount_number", label="Account Number",
                                        lookup_expr='exact')
    bank_name = filters.CharFilter(name="account_details__bank", label="Bank Name", lookup_expr='icontains')
    ifsc = filters.CharFilter(name="account_details__ifsc", label="IFSC Code", lookup_expr='icontains')
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = BrokerVehicle
        fields = []


class BrokerOwnerFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    broker = filters.CharFilter(name="broker__name__username", label="Broker name", lookup_expr='icontains')
    owner = filters.CharFilter(name="owner__name__username", label="Owner name", lookup_expr='icontains')
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = BrokerOwner
        fields = []


class BrokerDriverFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    broker = filters.CharFilter(name="broker__name__username", label="Broker name", lookup_expr='icontains')
    driver = filters.CharFilter(name="driver__name", label="Driver name", lookup_expr='icontains')
    driver_null = filters.BooleanFilter(name="driver__name", label="Is Driver name Null", lookup_expr="isnull")
    driver_phone = filters.CharFilter(name="driver__phone", label="Driver Phone", lookup_expr='icontains')
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = BrokerDriver
        fields = []


ACCOUNT_RELATION_CHOICES = (
    ('self', 'self'),
    ('driver', 'driver'),
    ('owner', 'owner')
)


class BrokerAccountFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    broker = filters.CharFilter(name="broker__name__username", label="Broker name", lookup_expr='icontains')

    relation = filters.ChoiceFilter(choices=ACCOUNT_RELATION_CHOICES, label="Account Relation Choices")

    account_null = filters.BooleanFilter(name="account", label="Is Account Null",
                                         lookup_expr="isnull")
    account_number = filters.CharFilter(name="account__acount_number", label="Account Number",
                                        lookup_expr='exact')
    bank_name = filters.CharFilter(name="account__bank", label="Bank Name", lookup_expr='icontains')
    ifsc = filters.CharFilter(name="account__ifsc", label="IFSC Code", lookup_expr='icontains')

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = BrokerAccount
        fields = []
