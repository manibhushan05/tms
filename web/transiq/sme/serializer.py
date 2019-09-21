from rest_framework import serializers, ISO_8601

from owner.models import Vehicle
from restapi.helper_api import DATE_FORMAT
from team.models import ManualBooking
from utils.models import City


class BookingSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    shipment_date = serializers.DateField(format=DATE_FORMAT)
    from_city_name = serializers.SerializerMethodField()
    to_city_name = serializers.SerializerMethodField()
    vehicle_number = serializers.SerializerMethodField()
    lr_numbers = serializers.SerializerMethodField()
    party_rate = serializers.IntegerField(read_only=True)
    charged_weight = serializers.DecimalField(read_only=True, decimal_places=3, max_digits=12)
    customer_amount = serializers.SerializerMethodField()
    balance_for_customer = serializers.SerializerMethodField()
    vehicle = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Vehicle.objects.all())

    def get_from_city_name(self, instance):
        if isinstance(instance.from_city_fk, City):
            return instance.from_city_fk.name
        return None

    def get_to_city_name(self, instance):
        if isinstance(instance.to_city_fk, City):
            return instance.to_city_fk.name
        return None

    def get_customer_amount(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.customer_amount
        return None

    def get_balance_for_customer(self, instance):
        if isinstance(instance, ManualBooking):
            return instance.balance_for_customer
        return None

    def get_vehicle_number(self, instance):
        if isinstance(instance.vehicle, Vehicle):
            return instance.vehicle.number()
        return None

    def get_lr_numbers(self, instance):
        return '\n'.join(instance.lr_numbers.values_list('lr_number', flat=True))

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        excluded_fields = [

        ]
        for field in excluded_fields:
            kwargs['child'].fields.pop(field)
        return serializers.ListSerializer(*args, **kwargs)
