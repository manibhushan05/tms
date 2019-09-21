from django_filters import rest_framework as filterset
from django.db.models.constants import LOOKUP_SEP
from broker.models import *
from team.models import ManualBooking

model = ManualBooking


class TestFilter(filterset.FilterSet):
    class Meta:
        model = model
        fields = '__all__'
    @classmethod
    def get_filter_name(cls, field_name, lookup_expr):
        """
        Combine a field name and lookup expression into a usable filter name.
        Exact lookups are the implicit default, so "exact" is stripped from the
        end of the filter name.
        """
        LOOKUP_SEP = '_'
        filter_name = LOOKUP_SEP.join([field_name, lookup_expr])

        # This also works with transformed exact lookups, such as 'date__exact'
        _exact = LOOKUP_SEP + 'exact'
        if filter_name.endswith(_exact):
            filter_name = filter_name[:-len(_exact)]
        return filter_name


def gen_serializer():
    obj = model
