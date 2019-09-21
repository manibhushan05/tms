from django_filters import rest_framework as filters

from restapi.filter.common import ListFilter
from team.models import ManualBooking


class BookingFilters(filters.FilterSet):
    lr_number = ListFilter(field_name='lr_numbers__id', label="Lr Number")
    shipment_date_between = filters.DateFromToRangeFilter(
        field_name="shipment_date", label="Shipment date Between", lookup_expr='range')
    charged_weight_range = filters.NumericRangeFilter(
        field_name="charged_weight", label="charged_weight_Range", lookup_expr='range')
    party_rate_range = filters.NumericRangeFilter(
        field_name="party_rate", label="party_rate_Range", lookup_expr='range')
    total_amount_to_company_range = filters.NumericRangeFilter(
        field_name="total_amount_to_company", label="total_amount_to_company_Range", lookup_expr='range')

    vehicle_id = ListFilter(field_name='vehicle_id', label='vehicle')

    source_office_id = ListFilter(field_name='source_office_id', label='Source Office')
    destination_office_id = ListFilter(field_name='destination_office_id', label='Destination Office')
    to_city_fk_id = ListFilter(field_name='to_city_fk_id', label='To City')
    from_city_fk_id = ListFilter(field_name='from_city_fk_id', label='From City')

    class Meta:
        model = ManualBooking
        fields = []
