from datetime import datetime, date, timedelta, time

from django.contrib.auth.models import User
from django.utils.text import slugify

from api.helper import EMP_GROUP2, EMP_GROUP3
from api.utils import to_int
from restapi.serializers.team import PendingInwardPaymentEntrySerializer, OutWardPaymentSerializer
from restapi.utils import get_or_none
from sme.models import Sme
from team.helper.helper import to_float
from team.models import PendingInwardPaymentEntry, Invoice, ManualBooking, DebitNoteSupplierDirectAdvance, \
    CreditNoteCustomerDirectAdvance, DebitNoteCustomer, CreditNoteCustomer, OutWardPayment, DebitNoteSupplier
from team.payments.accounting import placed_order_accounting_summary, billed_customer_accounting_summary
from utils.models import BankHolidays, Bank


def adjust_pending_inward_payment_data():
    data = {'common_inward_payment_remarks': '1233', 'payment_id': '112',
            'booking': [
                {'booking_id': '2326', 'amount': '16000', 'tds': '0', 'balance': '0', 'remarks': '23'},
                {'booking_id': '2846', 'amount': '2950', 'tds': '0', 'balance': '0', 'remarks': '443'},
                {'booking_id': '2878', 'amount': '44100', 'tds': '0', 'balance': '0', 'remarks': '222'},
                {'booking_id': '2907', 'amount': '44100', 'tds': '0', 'balance': '0', 'remarks': '222'},
                {'booking_id': '2905', 'amount': '18850', 'tds': '0', 'balance': '33650', 'remarks': '22122'},
                {'booking_id': '2906', 'amount': '0', 'tds': '0', 'balance': '0'},
                {'booking_id': '2920', 'amount': '0', 'tds': '0', 'balance': '0'}
            ]}
    parsed_data = []
    pending_payment = get_or_none(PendingInwardPaymentEntry, id=data.get('payment_id'))
    if isinstance(pending_payment, PendingInwardPaymentEntry):
        received_from = pending_payment.customer.get_name() if isinstance(pending_payment.customer, Sme) else None,
        trn = pending_payment.trn
        payment_mode = pending_payment.payment_mode
        payment_date = pending_payment.payment_date
    else:
        received_from = None,
        trn = None
        payment_mode = None
        payment_date = None

    for row in data.get('booking', []):
        if to_int(row['amount']) > 0:
            parsed_data.append({
                'booking_id': [row.get('booking_id')],
                'received_from': received_from,
                'tds': to_float(row['tds']),
                'actual_amount': to_float(row['amount']),
                'expected_amount': to_float(row['amount']),
                'payment_mode': payment_mode,
                'trn': trn,
                'remarks': row.get('remarks') if row.get('remarks', None) else data.get('common_inward_payment_remarks',
                                                                                        None),
                'payment_date': payment_date
            })


def pending_payments_data():
    data = []
    for payment in PendingInwardPaymentEntry.objects.filter(adjusted_flag=False).order_by('payment_date'):
        payment_data = payment.to_json()
        payment_data['save_id'] = '{}_{}'.format('save', payment.id)
        payment_data['proceed_id'] = '{}_{}'.format('proceed', payment.id)
        payment_data['accept_choice'] = '{}_{}'.format('accept_choice', payment.id)
        payment_data['amount_id'] = '{}_{}'.format('amount', payment.id)
        payment_data['tds_id'] = '{}_{}'.format('tds', payment.id)
        payment_data['form_pending_inward_id'] = '{}_{}'.format('form_pending_inward_id', payment.id)
        data.append(payment_data)
    return data


def adjust_inward_payment(payment, user):
    tds_amount = to_int(payment.tds)
    total_amount = to_int(payment.amount)
    try:
        tds_rate = tds_amount / (total_amount + tds_amount)
    except ZeroDivisionError:
        tds_rate = 0
    user_group = user.groups.values_list('name', flat=True)[0]
    if user_group == EMP_GROUP2 or user_group == EMP_GROUP3:
        invoices = Invoice.objects.filter(
            customer_fk=payment.customer, payment_received=False,
            bookings__in=ManualBooking.objects.filter(customer_to_be_billed_to=payment.customer).exclude(
                billing_type='contract')).distinct().order_by('date')
    else:
        invoices = Invoice.objects.filter(customer_fk=payment.customer, payment_received=False).order_by('date')
    invoices_data = []
    for invoice in invoices:
        if sum([booking.balance_for_customer for booking in invoice.bookings.exclude(booking_status='cancelled')]) != 0:
            data = {}
            data['invoice_date'] = invoice.date
            data['invoice_number'] = slugify(invoice.invoice_number)
            data['amount'] = invoice.total_amount
            data['remarks'] = invoice.remarks
            data['to_receive'] = sum(
                [booking.balance_for_customer for booking in invoice.bookings.exclude(booking_status='cancelled')])
            data['btnFullPaymentReceived'] = '_'.join(['btnFullPaymentReceived', slugify(invoice.invoice_number)])
            data['btnResetPaymentReceived'] = '_'.join(['btnResetPaymentReceived', slugify(invoice.invoice_number)])
            data['txtToReceiveInvoice'] = '_'.join(['txtToReceiveInvoice', slugify(invoice.invoice_number)])
            bookings = []
            for booking in invoice.bookings.exclude(booking_status='cancelled').order_by('shipment_date'):
                amount_to_be_received = to_int(booking.balance_for_customer)
                if amount_to_be_received != 0:
                    if to_float(amount_to_be_received) < total_amount and total_amount > 0:
                        received_amount = to_int(amount_to_be_received - amount_to_be_received * tds_rate)
                        received_tds = to_int(amount_to_be_received * tds_rate)
                        balance_amount = amount_to_be_received - received_amount - received_tds
                        if balance_amount == 1:
                            received_amount += 1
                            balance_amount = 0
                        total_amount -= received_amount
                        tds_amount -= received_tds
                    elif to_float(amount_to_be_received) > total_amount and total_amount > 0:
                        received_amount = to_int(total_amount - total_amount * tds_rate)
                        received_tds = to_int(total_amount * tds_rate)
                        balance_amount = amount_to_be_received - received_amount - received_tds
                        total_amount = 0
                        if balance_amount == 1:
                            received_amount += 1
                            balance_amount = 0
                        tds_amount -= received_tds
                    else:
                        total_amount = 0
                        tds_amount = 0
                        received_amount = None
                        received_tds = None
                        balance_amount = to_int(amount_to_be_received) - to_int(received_amount) - to_int(
                            received_tds)
                    received_amount = 0
                    received_tds = 0
                    balance_amount = 0
                    bookings.append({
                        'mb_id': booking.id,
                        'booking_id': booking.booking_id,
                        'lr_numbers': booking.booking_id if not '\n'.join(
                            booking.lr_numbers.values_list('lr_number', flat=True)) else '\n'.join(
                            booking.lr_numbers.values_list('lr_number', flat=True)),
                        'weight': booking.charged_weight,
                        'rate': booking.party_rate,
                        'total_amount': booking.total_amount_to_company,
                        'amount_to_be_received': amount_to_be_received,
                        'received_amount': received_amount,
                        'received_tds': received_tds,
                        'balance_amount': balance_amount,
                        'amountId': '_'.join([booking.booking_id, 'receivedAmountId']),
                        'tdsId': '_'.join([booking.booking_id, 'tdsId']),
                        'remarksId': '_'.join([booking.booking_id, 'remarksId']),
                        'balanceId': '_'.join([booking.booking_id, 'balanceId']),
                    })

            data['bookings'] = bookings
            invoices_data.append(data)

    data = invoices_data
    return data, tds_amount, total_amount, tds_rate


def pending_payment_adjustment_data(data):
    btn_submit = data.get('accept_choice')
    try:
        payment = PendingInwardPaymentEntry.objects.get(id=data.get('payment_id'))
        payment.customer = get_or_none(Sme, id=data.get('customer'))
        payment.tds = to_int(data.get('tds'))
        payment.save()
        if isinstance(payment.customer, Sme):
            placed_order_accounting_summary(sme_id=payment.customer.id)
            billed_customer_accounting_summary(sme_id=payment.customer.id)
    except PendingInwardPaymentEntry.DoesNotExist:
        return {'msg': "Pending payment does not exists", 'status': 404}
    if btn_submit == 'save':
        return {'msg': 'customer and tds saved successful', 'status': 200}
    elif btn_submit == 'proceed':
        payment = PendingInwardPaymentEntry.objects.get(id=data.get('payment_id'))
        credit_note = CreditNoteCustomer.objects.filter(status__in=['approved', 'partial'], customer=payment.customer)
        debit_note = DebitNoteCustomer.objects.filter(status__in=['approved', 'partial'], customer=payment.customer)
        credit_note_direct_advance = CreditNoteCustomerDirectAdvance.objects.filter(
            status__in=['approved', 'partial'], customer=payment.customer)
        debit_note_direct_advance = DebitNoteSupplierDirectAdvance.objects.filter(
            status__in=['approved', 'partial'], customer=payment.customer)

        invoice_data, tds_amount, total_amount, tds_rate = adjust_inward_payment(
            payment=payment, user=get_or_none(User, username=data.get('username'))
        )
        payment = PendingInwardPaymentEntrySerializer(payment).data
        return {'data': {
            'payment': payment,
            'invoices': invoice_data,
            'total_amount': total_amount,
            'tds_amount': tds_amount,
            'tds_rate': tds_rate,
            'credit_note': credit_note,
            'debit_note': debit_note,
            'credit_note_direct_advance': credit_note_direct_advance,
            'debit_note_direct_advance': debit_note_direct_advance
        }, 'msg': 'success', 'status': 200}
    else:
        return {'msg': 'something went wrong, Please try later', 'status': 400, 'data': {}}


def is_2nd_4th_saturday(dt):
    week_number = (dt.day - 1) // 7 + 1
    return week_number in [2, 4]


def is_neft_holiday(dt):
    if dt.weekday() == 6:
        return True
    elif dt.weekday() == 5 and is_2nd_4th_saturday(dt.date()):
        return True
    elif BankHolidays.objects.filter(date=dt.date()).exists():
        return True
    else:
        return False


def next_neft_working_day(dt):
    while is_neft_holiday(dt):
        dt += timedelta(days=1)
    return dt


def is_neft_hour(current_datetime):
    return time(0, 0) <= current_datetime.time() <= time(17, 0) and not is_neft_holiday(current_datetime)


def is_imps_hour(current_datetime):
    return time(17, 0) < current_datetime.time() <= time(20, 45)


def is_hdfc_bank_account(bank):
    if isinstance(bank, Bank) and bank.ifsc.lower().startswith('hdfc'):
        return True
    else:
        return False


def payment_mode_date(current_datetime, bank, amount, payment_date):
    if not isinstance(bank, Bank) and not isinstance(payment_date, datetime):
        return None, payment_date
    if is_hdfc_bank_account(bank=bank):
        mode = 'hdfc_internal_account'
        if payment_date.weekday() == 6:
            payment_date = (payment_date + timedelta(days=1))
        else:
            payment_date = payment_date
    elif payment_date > current_datetime:
        while is_neft_holiday(payment_date):
            payment_date = next_neft_working_day(payment_date)
        if is_hdfc_bank_account(bank=bank):
            mode = 'hdfc_internal_account'
        else:
            mode = 'neft' if to_int(amount) <= 200000 else 'rtgs'
    elif is_neft_hour(current_datetime):
        if is_hdfc_bank_account(bank=bank):
            mode = 'hdfc_internal_account'
            payment_date = current_datetime
        else:
            mode = 'neft' if to_int(amount) <= 200000 else 'rtgs'
            payment_date = current_datetime

    elif is_imps_hour(current_datetime):
        if is_hdfc_bank_account(bank=bank):
            mode = 'hdfc_internal_account'
            if current_datetime.weekday() == 6:
                payment_date = (current_datetime + timedelta(days=1))
            else:
                payment_date = current_datetime
        else:
            if current_datetime.weekday() == 6:
                if is_neft_holiday(current_datetime + timedelta(days=1)):
                    mode = 'imps'
                    payment_date = (current_datetime + timedelta(days=1))
                else:
                    mode = 'neft' if to_int(amount) <= 200000 else 'rtgs'
                    payment_date = (current_datetime + timedelta(days=1))
            else:
                mode = 'imps'
                payment_date = current_datetime.date()
    elif is_neft_holiday(
            payment_date) and payment_date.date() == current_datetime.date() and current_datetime.weekday() != 6 and (
            time(0, 0) <= current_datetime.time() <= time(17, 0) or is_imps_hour(current_datetime)):
        mode = 'imps'
        payment_date = current_datetime.date()
    else:
        payment_date = payment_date + timedelta(days=1)
        while is_neft_holiday(payment_date):
            payment_date = next_neft_working_day(payment_date)
        if is_hdfc_bank_account(bank=bank):
            mode = 'hdfc_internal_account'
        else:
            mode = 'neft' if to_int(amount) <= 200000 else 'rtgs'
    return mode, payment_date.date() if isinstance(payment_date, datetime) else payment_date


def adjust_outward_payment_adjustment_mode(payment_id, username):
    try:
        payment = OutWardPayment.objects.get(id=payment_id)
        booking = payment.booking_id.last()
        if isinstance(booking, ManualBooking):
            booking_supplier = booking.booking_supplier
            amount = to_int(payment.actual_amount)
            dn_amount = amount
            for dn in DebitNoteSupplier.objects.filter(status__in=['approved', 'partial']).exclude(deleted=True):
                if amount > dn.debit_amount - dn.adjusted_amount:
                    adjusted_amount = dn.debit_amount - dn.adjusted_amount
                    dn_amount -= dn.debit_amount - dn.adjusted_amount
                else:
                    adjusted_amount = dn_amount
                dn.adjusted_amount += adjusted_amount
                if to_int(dn.debit_amount - dn.adjusted_amount) == 0:
                    dn.status = 'adjusted'
                else:
                    dn.status = 'partial'
                dn.save()
            if ManualBooking.objects.filter(booking_supplier=booking_supplier, outward_payment_status='excess').exclude(
                    booking_status='cancelled').exclude(booking_supplier=None).exists():
                for mb in ManualBooking.objects.filter(booking_supplier=booking_supplier, outward_payment_status='excess').exclude(
                        booking_status='cancelled').exclude(booking_supplier=None).exclude(id=booking.id):
                    if amount >= abs(mb.balance_for_supplier):
                        adjusted_amount = mb.outward_amount - mb.total_amount_to_owner
                        amount -= mb.outward_amount - mb.total_amount_to_owner
                    else:
                        adjusted_amount = amount
                        amount = 0
                    if adjusted_amount > 0:
                        payment_data = {
                            'booking_id': [mb.id],
                            'paid_to': payment.paid_to,
                            'tds': 0,
                            'actual_amount': -adjusted_amount,
                            'payment_mode': 'adjustment',
                            'remarks': payment.remarks,
                            'payment_date': datetime.now().date().strftime('%d-%b-%Y'),
                            'changed_by': username
                        }
                        outward_payment_serializer = OutWardPaymentSerializer(data=payment_data)
                        if outward_payment_serializer.is_valid():
                            op = outward_payment_serializer.save()
                            payment.adjusted_outward_payments.add(op)
    except OutWardPayment.DoesNotExist:
        pass
    except TypeError:
        pass
