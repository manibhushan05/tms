from __future__ import absolute_import

from team.models import ManualBooking


def booking_search():
    bookings = ManualBooking.objects.filter(booking_id__search='AaHO06001')
