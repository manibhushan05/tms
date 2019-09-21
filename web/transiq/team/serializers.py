from team.models import ManualBooking, OutWardPayment
from django.core import serializers

from utils.models import AahoOffice


def manual_booking_serializer():
    return serializers.serialize(format='json',queryset=OutWardPayment.objects.filter(id=9836),use_natural_foreign_keys=True)
