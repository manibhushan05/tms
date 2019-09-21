from django_filters import rest_framework as filters

from notification.models import MobileDevice


class MobileDeviceFilters(filters.FilterSet):
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between")
    token = filters.CharFilter(field_name='token', lookup_expr='exact')
    class Meta:
        model=MobileDevice
        fields = []