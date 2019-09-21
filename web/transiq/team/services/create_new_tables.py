from datetime import datetime

from django.contrib.auth.models import User

from api.utils import get_or_none
from team.helper.helper import django_date_format, fuel_card_obj, update_outward_payments, \
    update_inward_payments, payment_mode_date
from team.tasks import sms_outward_payment
from team.models import OutWardPayment, ManualBooking, InWardPayment
from django.conf import settings
from utils.models import Bank
from team import tasks


def outward_payment(paid_to, amount, date, fuel_card, remarks, booking_id_list, account_id, payment_mode, is_sms,
                    username, is_refund_amount=False):
    bank_account = get_or_none(Bank, id=account_id)
    if payment_mode == 'bank_transfer':
        mode, payment_date = payment_mode_date(
            current_datetime=datetime.now(), bank=bank_account, amount=amount,
            payment_date=django_date_format(date))
    else:
        mode, payment_date = payment_mode, django_date_format(date)
    manual_bookings = ManualBooking.objects.filter(id__in=booking_id_list)
    payment = OutWardPayment()
    payment.paid_to = paid_to
    payment.actual_amount = amount
    payment.remarks = remarks
    payment.payment_date = payment_date
    payment.fuel_card = fuel_card_obj(card_id=fuel_card)
    payment.bank_account, payment.payment_mode = bank_account, mode
    if payment.payment_mode not in ['neft', 'rtgs', 'hdfc_internal_account', 'imps']:
        payment.status = 'paid'
    else:
        payment.status = 'unpaid'
    payment.lorry_number = ', '.join([booking.lorry_number for booking in manual_bookings if booking.lorry_number])
    payment.created_by = User.objects.get(username=username)
    payment.is_refund_amount = True if is_refund_amount == 'y' else False
    payment.changed_by = User.objects.get(username=username)
    payment.save()
    for booking in manual_bookings:
        payment.booking_id.add(booking)
    for booking in manual_bookings:
        update_outward_payments(booking)

    if is_sms == 'yes':
        payment.is_sms_supplier = True
        payment.save()
    tasks.email_outward_payment.delay(payment.id)
    if payment.is_sms_supplier and settings.ENABLE_SMS:
        tasks.sms_outward_payment.delay(payment_id=payment.id)
    return payment


def inward_payment(booking_id_list, receive_from, amount, payment_mode, date, invoice_number, remarks, trn,
                   username, tds_amount=0):
    manual_bookings = ManualBooking.objects.filter(id__in=booking_id_list)
    payment = InWardPayment()
    payment.received_from = receive_from
    payment.actual_amount = amount
    payment.payment_mode = payment_mode
    payment.tds = tds_amount
    payment.remarks = remarks
    if trn:
        payment.trn = trn
    payment.payment_date = django_date_format(date)
    payment.invoice_number = invoice_number
    payment.created_by = User.objects.get(username=username)
    payment.changed_by = User.objects.get(username=username)
    payment.save()
    for booking in payment.booking_id.all():
        booking.tds_deducted_amount += sum(booking.inward_booking.values_list('tds', flat=True))
        booking.total_in_ward_amount += sum(booking.inward_booking.values_list('actual_amount', flat=True))
        booking.save()
    for booking in manual_bookings:
        payment.booking_id.add(booking)
    for booking in manual_bookings:
        update_inward_payments(booking)
    return payment
