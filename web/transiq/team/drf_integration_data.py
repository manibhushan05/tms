from datetime import date, datetime

from django.db.models import Q

from api.utils import get_or_none
from broker.models import Broker
from team.models import ManualBooking


def booking_summary_supplier(user_id=None):
    data = {'pending_pod': {'balance': 0, 'amount_paid': 0, 'total_amount': 0, 'number_of_booking': 0},
            'delivered_pod': {'balance': 0, 'amount_paid': 0, 'total_amount': 0, 'number_of_booking': 0},
            'completed_booking': {'total_amount': 0, 'number_of_booking': 0}}
    supplier = get_or_none(Broker, name_id=user_id)
    if not isinstance(supplier, Broker):
        return data
    bookings = ManualBooking.objects.filter(supplier=supplier, shipment_date__gte='2017-12-01').exclude(
        Q(booking_status='cancelled') | Q(deleted=True))
    # PENDING POD
    total_amount = 0
    paid_amount = 0
    balance_amount = 0
    for booking in bookings.exclude(pod_status='completed'):
        total_amount += booking.fms_supplier_amount
        paid_amount += booking.fms_supplier_paid_amount
        balance_amount += booking.fms_balance_supplier
    data['pending_pod']['balance'] = balance_amount
    data['pending_pod']['amount_paid'] = paid_amount
    data['pending_pod']['total_amount'] = total_amount
    data['pending_pod']['number_of_booking'] = bookings.exclude(pod_status='completed').count()
    # DELIVERED POD AND INCOMPLETE OUTWARD PAYMENT
    total_amount = 0
    paid_amount = 0
    balance_amount = 0

    for booking in bookings.filter(pod_status='completed', outward_payment_status__in=['no_payment_made', 'partial']):
        total_amount += booking.fms_supplier_amount
        paid_amount += booking.fms_supplier_paid_amount
        balance_amount += booking.fms_balance_supplier
    data['delivered_pod']['balance'] = balance_amount
    data['delivered_pod']['amount_paid'] = paid_amount
    data['delivered_pod']['total_amount'] = total_amount
    data['delivered_pod']['number_of_booking'] = bookings.filter(pod_status='completed',
                                                                 outward_payment_status__in=['no_payment_made',
                                                                                             'partial']).count()

    # DELIVERED POD AND COMPLETE OUTWARD PAYMENT
    total_amount = 0

    for booking in bookings.filter(outward_payment_status__in=['complete', 'excess']):
        total_amount += booking.fms_supplier_amount
    data['completed_booking']['total_amount'] = total_amount
    data['completed_booking']['number_of_booking'] = bookings.filter(
        outward_payment_status__in=['complete', 'excess']).count()

    return data


def test_data():
    for booking in ManualBooking.objects.all():
        print(booking_summary_supplier(user_id=booking.supplier_id))
