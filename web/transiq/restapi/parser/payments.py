from datetime import datetime

from api.utils import to_int
from restapi.helper_api import django_date_format
from restapi.serializers.team import InWardPaymentSerializer
from restapi.service.payments import payment_mode_date
from restapi.utils import get_or_none
from team.models import PendingInwardPaymentEntry, Invoice, ManualBooking, CreditNoteCustomer, DebitNoteCustomer
from utils.models import Bank


def parse_outward_payment_data(data):
    if data.get('outward_payment_mode', None) == 'bank_transfer':
        bank_account = get_or_none(Bank, id=data.get('bank_account'))

        mode, payment_date = payment_mode_date(
            current_datetime=datetime.now(), bank=bank_account, amount=data.get('actual_amount'),
            payment_date=django_date_format(data.get('payment_date', None)))
    else:
        mode, payment_date = data.get('outward_payment_mode', None), django_date_format(data.get('payment_date', None))
    lorry_number=','.join(
            [booking.supplier_vehicle.number() for booking in
             ManualBooking.objects.filter(id__in=data.get('booking_id', [])).exclude(supplier_vehicle=None)])
    parsed_data = {
        'booking_id': data.get('booking_id', []),
        'lorry_number': lorry_number if lorry_number else None,
        'paid_to': data.get('paid_to', None),
        'utr': data.get('utr', None),
        'actual_amount': data.get('actual_amount', 0),
        'expected_amount': data.get('expected_amount', 0),
        'deleted_on': data.get('deleted_on', None),
        'tds': data.get('tds', 0),
        'payment_mode': mode,
        'bank_account': data.get('bank_account', None),
        'fuel_card': data.get('fuel_card', None),
        'payment_date': payment_date.date() if isinstance(payment_date, datetime) else payment_date,
        'remarks': data.get('remarks', None),
        'created_by': data.get('created_by', None),
        'changed_by': data.get('changed_by', None),
        'status': 'paid' if mode not in ['neft', 'rtgs', 'hdfc_internal_account', 'imps'] else 'unpaid',
        'is_sms_supplier': True if data.get('send_sms_supplier', None) == 'yes' else False,
        'is_refund_amount': True if data.get('is_refund_amount') == 'y' else False
    }
    return parsed_data


def parse_pending_inward_adjustment_data(data):
    credit_note_number = ', '.join(
        CreditNoteCustomer.objects.filter(id__in=[row.get('id') for row in data.get('cnc', [])]).values_list(
            'credit_note_number', flat=True))
    debit_note_number = ', '.join(
        DebitNoteCustomer.objects.filter(id__in=[row.get('id') for row in data.get('dnc', [])]).values_list(
            'debit_note_number', flat=True))
    pending_inward = get_or_none(PendingInwardPaymentEntry, id=data.get('payment_id', None))
    bookings_id = []
    inward_payments_data = []
    if isinstance(pending_inward, PendingInwardPaymentEntry):
        for booking in data.get('bookings', []):
            if to_int(booking.get('amount', None)) != 0:
                remarks_data = []
                remarks = booking.get('remarks') if booking.get(
                    'remarks', None) else data.get('common_inward_payment_remarks', None)
                if remarks:
                    remarks_data.append(remarks)
                if credit_note_number:
                    remarks_data.append(credit_note_number)
                if debit_note_number:
                    remarks_data.append(debit_note_number)
                bookings_id.append(booking.get('booking_id', None))
                inward_payments_data.append({
                    'booking_id': [booking.get('booking_id', None)],
                    'received_from': pending_inward.customer.get_name() if pending_inward.customer else pending_inward.customer_name,
                    'actual_amount': to_int(booking.get('amount', 0)),
                    'tds': to_int(booking.get('tds', 0)),
                    'payment_mode': pending_inward.payment_mode,
                    'payment_date': pending_inward.payment_date,
                    'invoice_number': booking.get('invoice_number', None),
                    'trn': pending_inward.trn,
                    'remarks': ', '.join(remarks_data),
                    'created_by': data.get('username', None),
                    'changed_by': data.get('username', None),
                })
    return inward_payments_data, bookings_id
