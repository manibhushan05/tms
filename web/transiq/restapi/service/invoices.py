from django.contrib.auth.models import User

from api.helper import EMP_GROUP3, EMP_GROUP1, EMP_GROUP2
from report import invoice
from restapi.utils import get_or_none
from sme.models import Sme
from team.models import OutWardPayment, ManualBooking


def check_invoice_status(booking):
    from team.models import Invoice
    if Invoice.objects.filter(bookings=booking).exists():
        return True
    else:
        return False


def get_single_booking_invoice_data(booking, booking_type):
    row = {
        'id': booking.id,
        'booking_id': booking.booking_id,
        'date': booking.shipment_date,
        'from_city': booking.from_city,
        'to_city': booking.to_city,
        'lorry_number': booking.supplier_vehicle.number() if booking.supplier_vehicle else None,
        'charged_weight': booking.charged_weight,
        'party_rate': booking.party_rate,
        'freight': booking.freight_from_company(),
        'pod_status': booking.get_pod_status_display()
    }

    if booking_type == 'full':
        row['lr_number'] = '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True))
    return row


def get_invoice_data(manual_bookings, booking_type):
    data = [get_single_booking_invoice_data(booking, booking_type) for booking in manual_bookings]
    data.append({
        'id': '',
        'booking_id': '',
        'date': '',
        'from_city': '',
        'to_city': '',
        'lorry_number': '',
        'charged_weight': sum(item['charged_weight'] for item in data),
        'party_rate': '',
        'freight': sum(item['freight'] for item in data),
        'pod_status': ''
    })
    return data


def get_comment_list(bookings, invoice_data):
    comment_data = {}
    star_count = 0

    # collect comments_data
    for booking in bookings:
        comments = invoice.get_single_booking_comments(booking)
        if comments:
            star_count += 1
            comment_data[booking.booking_id] = {'comments': comments, 'note_symbol': '*' * star_count}
    # annotate invoice data with note_symbol
    for invoice_row in invoice_data:
        booking_id = invoice_row['booking_id']
        invoice_row['note_symbol'] = '' if booking_id not in comment_data else comment_data[booking_id]['note_symbol']
    # make a comment list
    comment_list = []
    for booking in bookings:
        if booking.booking_id in comment_data:
            comments = comment_data[booking.booking_id]['comments']
            note_symbol = comment_data[booking.booking_id]['note_symbol']
            for comment in comments:
                comment_list.append({'comment': comment, 'note_symbol': note_symbol})

    return comment_list


def get_amount_data(bookings, booking_type):
    booking = bookings[0]
    gst_liability = booking.gst_liability

    advance_amount = float(sum(map(int, [booking.advance_amount_from_company for booking in bookings])))

    freight = sum([booking.freight_from_company() for booking in bookings])
    additional_charges = sum([booking.additional_charges_for_company for booking in bookings])
    deductions = sum([booking.deductions_for_company for booking in bookings])
    total_amount = float(freight + additional_charges - deductions)

    if invoice.should_apply_service_tax(booking_type, gst_liability):
        service_tax = total_amount * invoice.SERVICE_TAX_RATE
    else:
        service_tax = 0

    balance_amount = total_amount - advance_amount + service_tax

    outward_payment = OutWardPayment.objects.filter(booking_id__in=[b.id for b in bookings])
    amount_to_transiq = float(sum([op.actual_amount for op in outward_payment]))
    balance_payable_to_lorry_driver = total_amount - amount_to_transiq

    return {
        'total_amount': total_amount,
        'balance_amount': balance_amount,
        'advance_amount': advance_amount,
        'service_tax': service_tax,
        'freight': freight,
        'amount_to_transiq': amount_to_transiq,
        'balance_payable_to_lorry_driver': balance_payable_to_lorry_driver,
        'gst_liability': gst_liability,
        'gst_liability_remarks': invoice.gst_liability_remarks(booking=booking),
        'total_amount_with_stax': total_amount + service_tax
    }


def full_booking_invoice_data(customer):
    bookings = ManualBooking.objects.filter(customer_to_be_billed_to=customer.id).exclude(party_rate=0). \
        exclude(charged_weight=0).exclude(booking_status='cancelled').exclude(deleted=True).order_by(
        'shipment_date')
    user_group = EMP_GROUP1
    if EMP_GROUP2 == user_group or EMP_GROUP3 == user_group:
        bookings = bookings.exclude(billing_type='contract')
    message = None
    message_next_page_dict = {}
    list_of_ids = []
    for booking in bookings:
        if not check_invoice_status(booking):
            list_of_ids.append(booking.id)

    bookings = ManualBooking.objects.filter(id__in=list_of_ids, invoice_status='no_invoice').order_by('shipment_date')
    if bookings:
        if 0 in bookings.values_list('total_amount_to_company', flat=True):
            booking_id_with_zero_amount = bookings.filter(total_amount_to_company=0).values_list('booking_id',
                                                                                                 flat=True)
            inward_msg = []
            for bking in booking_id_with_zero_amount:
                inward_msg.append(bking)
                message_next_page = '*Inward Amount is not update for {}'.format(bking)
                message_next_page_dict.update({bking: message_next_page})
        gst_liability = bookings.last().gst_liability
        booking_ids = ','.join(map(str, bookings.values_list('id', flat=True)))
        invoice_data = get_invoice_data(bookings, 'full')
        comment_list = get_comment_list(bookings, invoice_data)
        invoice_amount_data = get_amount_data(bookings=bookings, booking_type='full')
    else:
        message = '*No bookings found for Customer {} who will make payment'.format(customer.get_name())
        gst_liability = ''
        booking_ids = ''
        invoice_data = ''
        comment_list = ''
        invoice_amount_data = ''
    return {'booking_data': invoice_data, 'customer': customer,
            'gst_liability': gst_liability,
            'booking_ids': booking_ids,
            'comment_list': comment_list,
            'invoice_amount_data': invoice_amount_data,
            'message_next_page_dict': message_next_page_dict,
            'error_message': message}


def parse_single_invoice_data(data):
    customer = get_or_none(Sme, id=data.get('to_be_billed_to'))
    return {
        'billing_address': data.get('billing_address'),
        'invoice_city': data.get('invoice_city'),
        'pin_code': data.get('invoice_pin'),
        'to_be_billed_to': customer.id if isinstance(customer, Sme) else '',
        'party_invoice_date': data.get('billing_invoice_date'),
        'gst_liability': data.get('gst_liability', 'consignor'),
        'advance_from_company': data.get('advance_from_company'),
        'created_by': get_or_none(User, username=data.get('username'))
    }
