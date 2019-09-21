from __future__ import absolute_import, print_function

from django.db.models import Q

from owner.models import Vehicle, Owner
from owner.vehicle_util import compare_format
from team.models import ManualBooking


def vehicle_booking_update():
    for booking in ManualBooking.objects.all():
        try:
            vehicle = Vehicle.objects.get(vehicle_number=compare_format(booking.lorry_number))
            booking.vehicle = vehicle
            booking.save()
        except Vehicle.DoesNotExist:
            print(booking.lorry_number)


def vehicle_owner_update():
    data = []
    for booking in ManualBooking.objects.all():
        try:
            vehicle = Vehicle.objects.get(vehicle_number=compare_format(booking.lorry_number))
            if not vehicle.owner and booking.truck_owner_phone and Owner.objects.filter(
                    Q(name__profile__phone__icontains=booking.truck_owner_phone) | Q(
                        name__profile__contact_person_phone__icontains=booking.truck_owner_phone)).exists():
                data.append([
                    vehicle.vehicle_number,
                    '\n'.join(['{}{}'.format(owner.get_name(), owner.get_phone()) for owner in Owner.objects.filter(
                        Q(name__profile__phone__icontains=booking.truck_owner_phone) | Q(
                            name__profile__contact_person_phone__icontains=booking.truck_owner_phone))])
                ])
        except Vehicle.DoesNotExist:
            pass
    print(data)
