from django_filters import rest_framework as filters

from fms.models import RequirementQuote


class RequirementQuotesFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    broker_id = filters.CharFilter(name="broker__id", label="Broker Id", lookup_expr='exact')
    requirement_id = filters.CharFilter(name="requirement_vehicle_quote__requirement__id",
                                        label="Requirement Id", lookup_expr='exact')
    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = RequirementQuote
        fields = []