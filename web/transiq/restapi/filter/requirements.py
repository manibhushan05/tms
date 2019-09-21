from django_filters import rest_framework as filters

from fms.models import Requirement


class RequirementFilter(filters.FilterSet):
    REQ_STATUS = (
        ('open', 'Open'),
        ('cancelled', 'Cancelled'),
        ('fulfilled', 'Fulfilled'),
        ('unverified', 'Unverified'),
        ('lapsed', 'Lapsed'),
    )

    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    client = filters.CharFilter(name="client__name__username", label=" Client", lookup_expr='icontains')

    client_null = filters.BooleanFilter(name="client", label="Is Client Null", lookup_expr="isnull")

    from_shipment_date = filters.DateFilter(field_name="from_shipment_date", label="from_shipment_date")
    from_shipment_date_between = filters.DateFromToRangeFilter(field_name="from_shipment_date",
                                                               label="from_shipment_date Between")
    from_shipment_date_null = filters.BooleanFilter(field_name="from_shipment_date", label="Is from_shipment_date Null",
                                                    lookup_expr="isnull")

    to_shipment_date = filters.DateFilter(field_name="to_shipment_date", label="to_shipment_date")
    to_shipment_date_between = filters.DateFromToRangeFilter(field_name="to_shipment_date",
                                                             label="to_shipment_date Between")
    to_shipment_date_null = filters.BooleanFilter(field_name="to_shipment_date", label="Is to_shipment_date Null",
                                                  lookup_expr="isnull")

    from_city = filters.CharFilter(field_name="from_city__name", label="From City", lookup_expr="icontains")
    from_city_null = filters.BooleanFilter(field_name="from_city", label="Is From City Null",
                                           lookup_expr="isnull")

    to_city = filters.CharFilter(field_name="to_city__name", label="to_city", lookup_expr="icontains")
    to_city_null = filters.BooleanFilter(field_name="to_city", label="Is to_city Null", lookup_expr="isnull")

    aaho_office = filters.CharFilter(name="aaho_office__branch_name", label="Aaho Office", lookup_expr='icontains')
    aaho_office_id = filters.NumberFilter(name="aaho_office__id", label="Aaho Office ID", lookup_expr='exact')
    aaho_office_null = filters.BooleanFilter(name="aaho_office", label="Is Aaho Office Null", lookup_expr="isnull")

    tonnage = filters.NumberFilter(field_name="tonnage", label="tonnage")
    tonnage_range = filters.NumericRangeFilter(field_name="tonnage", label="tonnage_Range")
    tonnage_null = filters.BooleanFilter(field_name="tonnage", label="Is tonnage Null", lookup_expr="isnull")

    no_of_vehicles = filters.NumberFilter(field_name="no_of_vehicles", label="no_of_vehicles")
    no_of_vehicles_range = filters.NumericRangeFilter(field_name="no_of_vehicles", label="no_of_vehicles_Range")
    no_of_vehicles_null = filters.BooleanFilter(field_name="no_of_vehicles", label="Is no_of_vehicles Null",
                                                lookup_expr="isnull")

    rate = filters.NumberFilter(field_name="rate", label="rate")
    rate_range = filters.NumericRangeFilter(field_name="rate", label="rate_Range")
    rate_null = filters.BooleanFilter(field_name="rate", label="Is rate Null", lookup_expr="isnull")

    material = filters.CharFilter(name="material", label="Material", lookup_expr='icontains')
    material_null = filters.BooleanFilter(name="material", label="Is Material Null",
                                          lookup_expr="isnull")

    type_of_vehicle = filters.CharFilter(name="type_of_vehicle__vehicle_type", label="Vehicle Type",
                                         lookup_expr='icontains')
    type_of_vehicle_null = filters.BooleanFilter(name="type_of_vehicle", label="Is Vehicle Type Null",
                                                 lookup_expr="isnull")

    status = filters.ChoiceFilter(name="req_status", label="Req Status", choices=REQ_STATUS)
    req_status_null = filters.BooleanFilter(name="req_status", label="Is Req Status Null", lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between")

    class Meta:
        model = Requirement
        fields = []
