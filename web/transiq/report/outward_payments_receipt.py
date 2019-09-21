from datetime import datetime

from api import s3util
from api.utils import merge
from report.util import get_receipt_pdf_content
from team.models import OutWardPayment, OutWardPaymentBill
from team.helper.helper import format_date

TITLE = 'supplier receipt'
AUTHOR = 'Trans IQ Technology Pvt. Ltd.'


def doc_outward_payment_receipt(data):
    filename = data['bill_number'] + '.pdf'
    content = get_receipt_pdf_content(data)
    return s3util.save_to_s3_invoice(filename=filename, content=content)


def get_rate_data(booking):
    rate_data = {
        'bill_date': format_date(datetime.today()),
        'freight': int(booking.supplier_charged_weight * booking.supplier_rate),
        'total_payable_amount': booking.total_amount_to_owner,
        'loading_charge': booking.loading_charge,
        'unloading_charge': booking.unloading_charge,
        'detention_charge': booking.detention_charge,
        'note_for_additional_owner_charges': booking.note_for_additional_owner_charges,
        'additional_charges_for_owner': booking.additional_charges_for_owner,
        'commission': booking.commission,
        'lr_charge': booking.lr_cost,
        'deduction_for_advance': booking.deduction_for_advance,
        'deduction_for_balance': booking.deduction_for_balance,
        'remarks_about_deduction': booking.remarks_about_deduction,
        'other_deduction': booking.other_deduction,
    }
    return rate_data


def get_booking_data(booking, bill_number):
    booking_data = {
        'booking_id': booking.booking_id,
        'bill_number': 'OPB-' + bill_number,
        'vehicle_number': booking.lorry_number,
        'from_city': booking.from_city,
        'to_city': booking.to_city,
        'loading_date': format_date(booking.shipment_date),
        'quantity': booking.supplier_charged_weight,
        'rate': booking.supplier_rate,
    }
    return booking_data


def get_payment_data(payments_id):
    payment_list = []
    for payment in OutWardPayment.objects.filter(id__in=payments_id):
        payment_list.append({
            'payment_date': format_date(payment.payment_date),
            'remarks': payment.remarks,
            'amount': payment.actual_amount
        })
    total_amount = sum([p['amount'] for p in payment_list])
    return {
        'payment_list': payment_list,
        'total_amount': total_amount
    }


DEFAULT_ADDRESS = "610-611, Shivai Plaza Premises Co-Operative Society Limited, Marol Industrial Estate, Marol, Andheri East, Mumbai - 400059"


def get_address(office):
    if not office:
        return DEFAULT_ADDRESS
    try:
        return '%s, %s, %s - %s' % (office.address, office.branch.name, office.branch.state.name, office.pin)
    except Exception as e:
        return DEFAULT_ADDRESS


def get_header_details(booking):
    office = booking.source_office
    address = get_address(office)
    header_content = {
        'company_name': "TRANS IQ TECHNOLOGIES PVT. LTD., " + office.branch.name,
        'address': address,
        'phone': '' if not office else office.phone,
        'email': 'info@aaho.in',
        'lr_number': ''.join(booking.lr_numbers.all()[:1].values_list('lr_number', flat=True))
    }
    return header_content


def get_bill_number():
    try:
        number = max(OutWardPaymentBill.objects.all().values_list('bill_number', flat=True))
    except ValueError:
        return '10001'
    try:
        return str(int(number) + 1)
    except ValueError:
        return '10001'


def create_outward_payment_table(booking, payment_id):
    pass


def get_receipt_data(booking, bill_number, payments_id):
    data = merge(get_booking_data(booking=booking, bill_number=bill_number),
                 get_rate_data(booking=booking))
    data = merge(data, get_header_details(booking=booking))
    data['payment_data'] = get_payment_data(payments_id=payments_id)

    return data


def create_outward_payment_bill(bill_number, booking, outward_payments, created_by):
    bill_obj = OutWardPaymentBill.objects.create(
        bill_number=bill_number,
        booking=booking,
        bill_date=datetime.today(),
        amount=sum(outward_payments.all().values_list('actual_amount', flat=True)),
        vehicle_number=booking.lorry_number,
        lr_number=', '.join(booking.lr_numbers.all().values_list('lr_number', flat=True)),
        from_city=booking.from_city,
        to_city=booking.to_city,
        loading_date=booking.shipment_date,
        weight=booking.supplier_charged_weight,
        created_by=created_by
    )
    for payments in outward_payments:
        bill_obj.outward_pmt.add(payments)
    return bill_obj


def generate_receipt(booking, payments_id, created_by):
    bill_number = get_bill_number()
    data = get_receipt_data(booking, bill_number, payments_id)
    s3_upload = doc_outward_payment_receipt(data=data)
    outward_payments = OutWardPayment.objects.filter(id__in=payments_id)
    bill_obj = create_outward_payment_bill(bill_number, booking, outward_payments, created_by)
    return bill_obj.bill_number, s3_upload
