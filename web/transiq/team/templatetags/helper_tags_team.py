from datetime import datetime, date

from django import template
from django.http import Http404

from api.models import S3Upload
from api.utils import get_or_none
from index.models import RouteFreight
from owner.vehicle_util import display_format
from team.models import ManualBooking, OutWardPaymentBill, OutWardPayment
from team.helper.helper import to_int, to_float

register = template.Library()


@register.simple_tag
def multiply_integers(num1, num2):
    return to_int(num1) * to_int(num2)


@register.simple_tag
def multiply_numbers(num1, num2):
    return to_float(num1) * to_float(num2)


@register.simple_tag
def subtract_intgers(num1, num2):
    return to_int(num1) - to_int(num2)


@register.simple_tag
def customer_balance(booking_id):
    booking = ManualBooking.objects.get(id=booking_id)
    return booking.total_amount_to_company - sum(
        booking.inward_booking.exclude(actual_amount=None).values_list('actual_amount', flat=True)) - sum(
        booking.inward_booking.exclude(tds=None).values_list('tds', flat=True))
@register.simple_tag
def customer_inward_amount(booking_id):
    booking = ManualBooking.objects.get(id=booking_id)
    return sum(
        booking.inward_booking.exclude(actual_amount=None).values_list('actual_amount', flat=True)) + sum(
        booking.inward_booking.exclude(tds=None).values_list('tds', flat=True))


@register.simple_tag
def to_int(value):
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        return int(float(value))


@register.simple_tag
def to_datetime(date):
    return datetime.strptime(date, '%d-%b-%Y').strftime('%d-%b-%Y %I:%M %p')


@register.simple_tag
def compare_gst_date(shipment_date):
    return date(2017, 6, 30) >= shipment_date


@register.simple_tag
def isGSTDate():
    return any([compare_gst_date(value.shipment_date) for value in ManualBooking.objects.all()])


@register.simple_tag
def get_invoice_number_for_inward(booking_id):
    mb = get_or_none(ManualBooking, id=booking_id)
    if mb:
        if mb.to_pay_invoices.all():
            invoice_number = mb.to_pay_invoices.all().latest('updated_on').invoice_number
        elif mb.invoices.all():
            invoice_number = mb.invoices.all().latest('updated_on').invoice_number
        else:
            invoice_number = ''
    else:
        invoice_number = ''
    return invoice_number


@register.simple_tag
def is_opb_reprint_enabled(booking_id):
    ids = ManualBooking.objects.filter(id=booking_id).values_list('id', flat=True).exclude(
        booking_status__icontains='cancelled')
    if OutWardPaymentBill.objects.filter(booking_id__in=ids).exists():
        return True
    else:
        return False


@register.simple_tag
def is_opb_enabled(booking_id):
    booking = ManualBooking.objects.filter(id=booking_id).exclude(
        booking_status__icontains='cancelled').last()
    if isinstance(booking, ManualBooking):
        return not all(
            [value.outward_payment_bill.exists() for value in booking.outward_booking.exclude(is_refund_amount=True)])
    else:
        raise Http404


@register.simple_tag
def is_opb_raised(payment_id):
    return OutWardPaymentBill.objects.filter(outward_pmt__in=OutWardPayment.objects.filter(id=payment_id)).exists()


@register.simple_tag
def s3_upload_bill_obj(payment_id):
    outward_payment = OutWardPayment.objects.get(id=payment_id)
    opb = OutWardPaymentBill.objects.filter(outward_pmt=outward_payment).last()
    if opb:
        s3_obj = S3Upload.objects.filter(filename__iexact='OPB-' + opb.bill_number + '.pdf')
    else:
        s3_obj = None
    return s3_obj


@register.simple_tag
def is_invoice_raised(booking_id):
    try:
        booking = ManualBooking.objects.get(id=booking_id)
        if booking.invoices.exists() and booking.invoices.all().last().s3_upload is not None:
            return True
        else:
            return False
    except ManualBooking.DoesNotExist:
        return False


@register.simple_tag
def is_pod_button_enabled(booking_id):
    booking = get_or_none(ManualBooking, id=booking_id)
    for lr in booking.lr_numbers.all():
        if lr.pod_files.all():
            return True
    return False


@register.simple_tag
def is_latest_freight(freight_datetime):
    return freight_datetime.date() == datetime.now().date()


@register.simple_tag
def is_freight_uploaded_today():
    return RouteFreight.objects.filter(updated_on__date=datetime.today()).exists()


@register.simple_tag
def is_commission_booking(booking_id):
    return booking_id.startswith('BROKER')


@register.simple_tag
def display_vehicle_number_format(vehicle_number):
    return display_format(vehicle_number)

@register.simple_tag
def number_days_old(dt):
    if isinstance(dt,datetime) or isinstance(dt,date):
        return '{} Days'.format((datetime.now().date()-dt).days)
    return ''

