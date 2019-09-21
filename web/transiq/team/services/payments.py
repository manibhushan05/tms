from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from owner.models import FuelCard
from team.models import InWardPayment, ManualBooking, OutWardPayment
from team.helper.helper import django_date_format, to_int, update_inward_payments, fuel_card_obj, \
    update_outward_payments
from team.tasks import email_updated_outward_payment


def get_group_name(username):
    try:
        user_object = User.objects.get(username=username)
        group = user_object.groups.get(name='team').name

    except:
        raise PermissionDenied
    return group


def in_ward_payments(request):
    if request.method == 'POST':
        payment = InWardPayment.objects.create(
            received_from=request.POST.get('received_from'),
            actual_amount=request.POST.get('actual_amount'),
            payment_mode=request.POST.get('payment_mode'),
            remarks=request.POST.get('remarks'),
            payment_date=django_date_format(request.POST.get('inward_payment_date')),
            invoice_number=request.POST.get('invoice_number'),
            created_by=User.objects.get(username=request.user.username)
        )
        booking_id_list = request.POST.getlist('booking_id[]')
        for booking_id in booking_id_list:
            manual_booking_id = ManualBooking.objects.get(booking_id=booking_id)
            in_ward_payment = InWardPayment.objects.filter(booking_id=manual_booking_id)
            amount = 0
            for value in in_ward_payment:
                amount += value.actual_amount
            amount += to_int(float(request.POST.get('actual_amount')))
            manual_booking_id.total_in_ward_amount = amount
            manual_booking_id.save()
            payment.booking_id.add(manual_booking_id)
            update_inward_payments(manual_booking_id)


def update_inward_payment(booking_id_list, payment_id, received_from, amount, payment_mode, remarks, date,
                          invoice_number, trn, tds_amount=0):
    manual_bookings = ManualBooking.objects.filter(id__in=booking_id_list)
    payment = InWardPayment.objects.get(id=payment_id)
    payment.received_from = received_from
    payment.tds = tds_amount
    payment.actual_amount = amount
    payment.payment_mode = payment_mode
    payment.remarks = remarks
    payment.payment_date = django_date_format(date)
    payment.invoice_number = invoice_number
    payment.trn = trn
    payment.save()
    for value in payment.booking_id.all():
        value.total_in_ward_amount -= to_int(amount)
        value.tds_deducted_amount += int(float(tds_amount))
        value.save()
    payment.booking_id.clear()
    for booking in manual_bookings:
        payment.booking_id.add(booking)
    for booking in manual_bookings:
        update_inward_payments(booking)


def update_outward_payment(booking_id_list, paid_to, amount, remarks, date, fuel_card, payment_mode, payment_id):
    manual_bookings = ManualBooking.objects.filter(id__in=booking_id_list)
    payment = OutWardPayment.objects.get(id=payment_id)
    old_amount = str(to_int(payment.actual_amount))
    payment.paid_to = paid_to
    payment.actual_amount = amount
    payment.remarks = remarks
    payment.payment_mode = payment_mode
    payment.payment_date = django_date_format(date)
    payment.fuel_card = fuel_card_obj(card_id=fuel_card)
    payment.lorry_number = ', '.join(manual_bookings.values_list('lorry_number', flat=True))
    payment.save()
    for value in payment.booking_id.all():
        value.total_out_ward_amount -= to_int(amount)
        value.save()
    payment.booking_id.clear()
    for booking in manual_bookings:
        payment.booking_id.add(booking)
        email_updated_outward_payment(booking.booking_id, payment_id, old_amount, str(to_int(amount)))
    for booking in manual_bookings:
        update_outward_payments(booking)


def save_updated_out_ward_payment(request):
    booking_id_list = request.POST.getlist('booking_id[]')
    payment_id = OutWardPayment.objects.get(id=request.POST.get('payment_id'))
    old_amount = str(to_int(payment_id.actual_amount))
    new_amount = str(to_int(request.POST.get('actual_amount')))
    payment_id.paid_to = request.POST.get('paid_to')
    payment_id.actual_amount = request.POST.get('actual_amount')
    payment_id.remarks = request.POST.get('remarks')
    payment_id.payment_date = django_date_format(request.POST.get('outward_payment_date'))
    payment_id.invoice_number = request.POST.get('invoice_number')
    payment_id.fuel_card = None if not request.POST.get('fuel_card_number') else FuelCard.objects.get(
        id=request.POST.get('fuel_card_number'))
    # save_outward_payment__mode(request, payment_id)
    if payment_id.payment_mode not in ['neft', 'rtgs', 'hdfc_internal_account']:
        payment_id.status = 'paid'
        payment_id.save()
    for value in payment_id.booking_id.all():
        value.total_out_ward_amount -= to_int(request.POST.get('actual_amount'))
        value.save()
    payment_id.booking_id.clear()
    booking_id = ''
    for value in booking_id_list:
        manual_booking_id = ManualBooking.objects.get(booking_id=value)
        payment_id.booking_id.add(manual_booking_id)
        out_ward_payment = OutWardPayment.objects.filter(booking_id=manual_booking_id).exclude(is_refund_amount=True)
        amount = 0
        for value in out_ward_payment:
            amount += value.actual_amount
        if manual_booking_id.total_amount_to_owner > amount:
            manual_booking_id.outward_payment_status = 'partial'
        elif manual_booking_id.total_amount_to_owner == amount:
            manual_booking_id.outward_payment_status = 'complete'
        elif manual_booking_id.total_amount_to_owner < amount:
            manual_booking_id.outward_payment_status = 'excess'
        manual_booking_id.total_out_ward_amount = amount
        booking_id = manual_booking_id.booking_id
        manual_booking_id.save()
        email_updated_outward_payment(request, booking_id, payment_id, old_amount, new_amount)
