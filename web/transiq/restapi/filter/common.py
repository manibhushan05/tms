from django_filters import Filter
from django_filters.fields import Lookup

from owner.vehicle_util import compare_format


class ListFilter(Filter):
    def filter(self, qs, value):
        value_list = value.split(u',')
        return super(ListFilter, self).filter(qs, Lookup(value_list, 'in'))


class VehicleFilter(Filter):
    def filter(self, qs, value):
        vehicle_number = compare_format(value)
        return super(VehicleFilter, self).filter(qs, Lookup(vehicle_number, 'icontains'))
