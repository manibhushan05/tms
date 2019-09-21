from django.contrib.auth.models import User
from django_filters import rest_framework as filters

from restapi.models import UserCategory


class UserCategoryFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    category = filters.CharFilter(name="category", label="User Category", lookup_expr='icontains')
    category_null = filters.BooleanFilter(name="category", label="Is User Category Null", lookup_expr="isnull")
    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = UserCategory
        fields = []

class UserFilters(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    is_active = filters.BooleanFilter(name="is_active", label="Is User Category Null")

    class Meta:
        model = User
        fields = []