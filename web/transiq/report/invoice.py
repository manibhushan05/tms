from __future__ import unicode_literals

from datetime import datetime, date
from random import randint

from django.http import Http404
from django.utils.html import format_html
from django.utils.text import slugify
from num2words import num2words

from api import s3util
from api.utils import int_or_none, get_or_none, to_int, format_inr, financial_year_yy
from owner.vehicle_util import compare_format, display_format
from report.util import get_single_booking_invoice_pdf_content, get_company_data, get_invoice_summary_pdf_content, \
    get_invoice_authorized_signature, get_multiple_booking_invoice_pdf_content, get_logo_data
from restapi.helper_api import check_booking_status, create_new_booking_status, update_booking_status
from sme.models import Sme
from team.helper.helper import check_invoice_status
from team.models import ManualBooking, OutWardPayment, Invoice, InvoiceSummary
from utils.models import City

SERVICE_TAX_RATE = 0.05

BOOKING_TYPES = ['full', 'commission']


class InvoiceError(AssertionError):
    pass


def raise_invoice(bookings):
    ManualBooking.objects.filter(id__in=[b.id for b in bookings]).update(invoice_status='invoice_raised')


def validate(bookings, booking_type):
    if len(bookings) == 0:
        raise InvoiceError('Length of bookings array is 0')
    if booking_type not in BOOKING_TYPES:
        raise InvoiceError('Invalid booking_type {}, allowed values are {}'.format(booking_type, repr(BOOKING_TYPES)))
    for booking in bookings:
        if check_invoice_status(booking):
            raise InvoiceError('Invoice already raised for booking {}'.format(booking.booking_id))


def get_billing_info(bookings, form_data):
    booking = bookings[0]
    form_data = form_data or {}
    form_address = form_data.get('billing_address', '').strip() if form_data.get('billing_address', '') else ''
    form_pin_code = form_data.get('pin_code', '').strip() if form_data.get('pin_code', '') else ''
    invoice_date = parse_date(form_data.get('party_invoice_date', '').strip() if form_data.get('party_invoice_date',
                                                                                               '') else None) or booking.billing_invoice_date
    city = get_or_none(City, id=form_data.get('invoice_city'))
    to_be_billed = form_data.get('to_be_billed_to', '')
    try:
        sme = Sme.objects.get(id=to_be_billed)
        gstin = sme.gstin
    except Sme.DoesNotExist:
        sme = None
        gstin = None

    if not invoice_date:
        invoice_date = datetime.today().date()

    return sme, form_address, city, form_pin_code, invoice_date, gstin


def update_booking_invoice(invoice):
    mb = ManualBooking.objects.filter(id__in=invoice.bookings.values_list('id', flat=True))
    sme = get_or_none(Sme, name__profile__name=invoice.company_name)
    if isinstance(sme, Sme):
        for booking in mb:
            booking.customer_to_be_billed_to = sme
            booking.to_be_billed_to = invoice.company_name
            booking.billing_address = invoice.address
            booking.billing_invoice_date = invoice.date
            booking.invoice_number = invoice.invoice_number
            booking.invoice_status = 'invoice_raised'

            booking.save()
            booking_pod_uploaded = check_booking_status(booking, 'invoice_raised')
            if not booking_pod_uploaded:
                create_new_booking_status(booking, 'invoice_raised', invoice.created_by)
            else:
                update_booking_status(booking, 'invoice_raised', 'in_progress', invoice.created_by)


def get_comment_list(bookings, invoice_data):
    comment_data = {}
    star_count = 0

    # collect comments_data
    for booking in bookings:
        comments = get_single_booking_comments(booking)
        if comments:
            star_count += 1
            comment_data[booking.id] = {'comments': comments, 'note_symbol': '*' * star_count}

    # annotate invoice data with note_symbol
    for invoice_row in invoice_data:
        booking_id = invoice_row['booking_id']
        invoice_row['note_symbol'] = '' if booking_id not in comment_data else comment_data[booking_id]['note_symbol']

    # make a comment list
    comment_list = []
    for booking in bookings:
        if booking.id in comment_data:
            comments = comment_data[booking.id]['comments']
            note_symbol = comment_data[booking.id]['note_symbol']
            for comment in comments:
                comment_list.append({'comment': comment, 'note_symbol': note_symbol})

    return comment_list


def make_invoice(bookings, booking_type, form_data=None, return_html=False, created_by=None, summary_required=False,
                 combined_invoice=False):
    if isinstance(bookings, ManualBooking):
        bookings = [bookings]

    elif all(
            [isinstance(booking, ManualBooking) for booking in bookings]) and bookings.count() > 2 and summary_required:
        summary_required = True

    validate(bookings, booking_type)
    raise_invoice(bookings)
    if combined_invoice:
        amount_data = get_amount_data(bookings, form_data, booking_type)

        # invoice table data
        invoice_data = get_invoice_data(bookings, booking_type)

        # comment data
        invoice = create_invoice(bookings=bookings, form_data=form_data, amount_data=amount_data,
                                 created_by=created_by, summary_required=summary_required)
        # update_booking_invoice(invoice=invoice)

        data = get_multiple_booking_invoice_data(
            invoice=invoice, bookings=bookings, booking_type=booking_type
        )
        filename, s3_upload = make_invoice_pdf(data, return_html=return_html, multiple=True)
        Invoice.objects.filter(id=invoice.id).update(s3_upload=s3_upload)
        return

    for booking in bookings:
        amount_data = get_amount_data([booking], form_data, booking_type)
        invoice = create_invoice(bookings=[booking], form_data=form_data, amount_data=amount_data,
                                 created_by=created_by, summary_required=summary_required)

        # update_booking_invoice(invoice=invoice)
        data = get_single_booking_pdf_data(invoice)
        filename, s3_upload = make_invoice_pdf(data, return_html=return_html)
        Invoice.objects.filter(id=invoice.id).update(s3_upload=s3_upload)
    if summary_required:
        invoices_summary_data = get_invoices_summary_data(bookings=bookings)
        invoices_summary_pdf_data = get_invoice_summary_pdf_data(bookings=bookings, booking_type=booking_type,
                                                                 invoice_summary_data=invoices_summary_data)
        file_name, s3_upload = make_invoices_summary_pdf(data=invoices_summary_pdf_data, return_html=return_html)
        invoice_summary_obj = InvoiceSummary.objects.create(
            ref_number=randint(10000000, 99999999),
            datetime=invoices_summary_pdf_data['summary_date'],
            s3_upload=s3_upload, created_by=created_by
        )
        for booking in bookings:
            if isinstance(booking, ManualBooking):
                ManualBooking.objects.filter(id=booking.id).update(invoice_summary=invoice_summary_obj)
        return invoice_summary_obj
    else:
        return None


def gst_liability_remarks(booking):
    if booking.shipment_date < date(2017, 7, 1):
        if booking.gst_liability == 'consignor':
            msg = 'N.B. Service tax to be paid by Consignor'
        elif booking.gst_liability == 'consignee':
            msg = 'N.B. Service tax to be paid by Consignee'
        elif booking.gst_liability == 'carrier':
            msg = 'N.B. Service tax to be paid by Carrier'
        elif booking.gst_liability == 'exempted':
            msg = 'N.B.: This transaction is exempt from Service Tax'
        else:
            msg = ''
    else:
        if booking.gst_liability == 'consignor':
            msg = format_html(
                """GST Payable under Reverse Charge by recipient of services as per notification no. 13/2017 dated 28th June 2017""")
        elif booking.gst_liability == 'consignee':
            msg = format_html(
                """GST Payable under Reverse Charge by recipient of services as per notification no. 13/2017 dated 28th  June 2017""")
        elif booking.gst_liability == 'carrier':
            msg = format_html(
                """GST Payable under Reverse Charge by recipient of services as per notification no. 13/2017 dated 28th  June 2017""")
        elif booking.gst_liability == 'exempted':
            msg = "GST exempt as per notification no. 12/2017 dated 28th June 2017"
        else:
            msg = format_html(
                """GST Payable under Reverse Charge by recipient of services as per notification no. 13/2017 dated 28th June 2017""")
    return msg


def get_amount_data(bookings, form_data, booking_type):
    booking = bookings[0]
    form_data = form_data or {}
    gst_liability = form_data.get('gst_liability', '').strip() if form_data.get('gst_liability',
                                                                                '') else '' or booking.gst_liability
    advance_amount = int_or_none(
        form_data.get('advance_from_company', '').strip() if form_data.get('advance_from_company', '') else 0)
    if not advance_amount:
        advance_amount = sum(map(to_int, [booking.advance_amount_from_company for booking in bookings]))
        advance_amount += sum([booking.adjusted_cnca_amount for booking in bookings])

    freight = sum([booking.freight_from_company() for booking in bookings])
    additional_charges = sum([booking.additional_charges_for_company for booking in bookings])
    deductions = sum([booking.deductions_for_company for booking in bookings])
    total_amount = float(freight + additional_charges - deductions)

    if should_apply_service_tax(booking_type, gst_liability):
        service_tax = total_amount * SERVICE_TAX_RATE
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
        'gst_liability': gst_liability
    }


def create_invoice_summary_pdf(filename, data, return_html=False):
    content = get_invoice_summary_pdf_content(data, return_html=return_html)
    if return_html:
        return filename, content
    else:
        return filename, s3util.save_to_s3_invoice(filename=filename, content=content)


def create_invoice_pdf(filename, data, return_html=False, multiple=False):
    if multiple:
        content = get_multiple_booking_invoice_pdf_content(data, return_html=return_html)
    else:
        content = get_single_booking_invoice_pdf_content(data, return_html=return_html)
    if return_html:
        return data['invoice_number'], content
    else:
        return data['invoice_number'], s3util.save_to_s3_invoice(filename=filename, content=content)


def make_invoice_pdf(data, return_html=False, multiple=False):
    data['transiq'] = get_company_data()
    return create_invoice_pdf(filename=data['filename'], data=data, return_html=return_html, multiple=multiple)


def make_invoices_summary_pdf(data, return_html=False):
    data['transiq'] = get_company_data()
    return create_invoice_summary_pdf(data['filename'], data, return_html=return_html)


def get_single_booking_invoice_data(booking, booking_type):
    row = {
        'booking_id': booking.id,
        'date': booking.shipment_date,
        'from_city': booking.from_city,
        'to_city': booking.to_city,
        'lorry_number': booking.supplier_vehicle.number() if booking.supplier_vehicle else '',
        'charged_weight': booking.charged_weight,
        'party_rate': booking.party_rate,
        'freight': booking.freight_from_company()
    }

    if booking_type == 'full':
        row['lr_number'] = '<br />'.join(booking.lr_numbers.values_list('lr_number', flat=True))

    return row


def get_invoice_data(manual_bookings, booking_type):
    data = [get_single_booking_invoice_data(booking, booking_type) for booking in manual_bookings]
    data.append({
        'booking_id': '',
        'date': '',
        'from_city': '',
        'to_city': '',
        'lorry_number': '',
        'charged_weight': sum(item['charged_weight'] for item in data),
        'party_rate': '',
        'freight': sum(item['freight'] for item in data)
    })
    return data


def get_single_invoice_data(booking):
    row = {}
    if Invoice.objects.filter(bookings=booking).exists():
        try:
            invoice = Invoice.objects.get(bookings=booking)
            row['invoice_number'] = invoice.invoice_number
            row['invoice_date'] = invoice.date.strftime('%d-%b-%Y') if invoice.date else ''
        except Invoice.MultipleObjectsReturned:
            invoice = Invoice.objects.filter(booking=booking).last()
            row['invoice_number'] = invoice.invoice_number
            row['invoice_date'] = invoice.date.strftime('%d-%b-%Y') if invoice.date else ''
    else:
        row['invoice_number'] = ''
        row['invoice_date'] = ''
    if booking.lr_numbers.exists():
        row['lr_number'] = '<br />'.join(booking.lr_numbers.values_list('lr_number', flat=True))
    row['from_city'] = booking.from_city
    row['to_city'] = booking.to_city
    row['vehicle_number'] = booking.supplier_vehicle.number() if booking.supplier_vehicle else ''
    row['weight'] = booking.charged_weight
    row['rate'] = to_int(booking.party_rate)
    row['shipment_date'] = booking.shipment_date.strftime('%d-%b-%Y') if booking.shipment_date else ''
    row['other_charges'] = booking.additional_charges_for_company - booking.deductions_for_company
    row['gross_amount'] = to_int(booking.charged_weight * booking.party_rate + row['other_charges'])
    return row


def get_multiple_booking_invoice_data(invoice, bookings, booking_type):
    if not isinstance(invoice, Invoice):
        raise Http404
    invoice_number = invoice.invoice_number
    data = {
        'filename': '{}.pdf'.format(slugify(invoice_number)),
        "invoice_number": invoice_number,
        "invoice_date": invoice.date.strftime('%d-%b-%Y') if isinstance(invoice, Invoice) else '',
        "customer_name": invoice.customer_fk.get_name(),
        "customer_address": invoice.address,
        "gstin": invoice.gstin,
        "is_full_booking": True if booking_type == 'full' else False,
        "is_other_charges": True,
        "gst_liability_remarks": gst_liability_remarks(bookings[0]),
        "logo": get_logo_data(),
        'authorized_signature': get_invoice_authorized_signature(),
        "invoice_data": [
            {
                "date": booking.shipment_date.strftime("%d-%b-%Y") if isinstance(booking.shipment_date, date) else '',
                "source": booking.from_city_fk.name if isinstance(booking.from_city_fk, City) else '',
                "destination": booking.to_city_fk.name if isinstance(booking.to_city_fk, City) else '',
                "lr_numbers": format_html("<br>".join([lr.lr_number for lr in booking.lr_numbers.all()])),
                "vehicle_number": booking.supplier_vehicle.number(),
                "rate": booking.party_rate,
                "quantity": booking.charged_weight,
                "other_charges": booking.additional_charges_for_company - booking.deductions_for_company,
                "amount": to_int(
                    booking.party_rate * booking.charged_weight + booking.additional_charges_for_company - booking.deductions_for_company)
            } for booking in bookings
        ]
    }
    advance_from_company = sum([booking.advance_amount_from_company for booking in bookings])
    advance_from_company += sum([booking.adjusted_cnca_amount for booking in bookings])
    is_advance_from_company = True if advance_from_company > 0 else False
    total_amount = sum([amount['amount'] for amount in data['invoice_data']])
    balance_amount = total_amount - advance_from_company
    other_charges = sum([amount['other_charges'] for amount in data['invoice_data']])
    total_quantity = sum(quantity['quantity'] for quantity in data['invoice_data'])
    data['is_other_charges'] = any([amount['other_charges'] != 0 for amount in data['invoice_data']])
    data['invoice_data'] += [
        {'total_amount': total_amount, 'other_charges': other_charges, 'total_quantity': total_quantity,
         'is_advance_from_company': is_advance_from_company, 'advance_from_company': advance_from_company,
         'balance_amount': balance_amount}]

    return data


def check_invoice_data():
    invoice = Invoice.objects.get(id=3924)
    # get_multiple_booking_invoice_data(invoice, bookings=invoice.bookings.all(), booking_type='full')
    get_invoice_number(bookings=invoice.bookings.all(), invoice_date=invoice.date,
                       customer_code='ske')


def get_invoices_summary_data(bookings):
    data = [get_single_invoice_data(booking) for booking in bookings]
    data.append({
        'invoice_number': '',
        'invoice_date': '',
        'from_city': '',
        'to_city': '',
        'vehicle_number': '',
        'weight': sum(item['weight'] for item in data),
        'rate': '',
        'shipment_date': '',
        'other_charges': sum(item['other_charges'] for item in data),
        'gross_amount': sum(item['gross_amount'] for item in data),
    })
    return data


def get_single_booking_comments(booking):
    booking_comments = []

    add_remarks = booking.invoice_remarks_for_additional_charges
    add_charges = booking.additional_charges_for_company
    if add_remarks and add_charges > 0:
        booking_comments.append('ADD :- {} : Rs. {}'.format(add_remarks, add_charges))

    deduction_remarks = booking.invoice_remarks_for_deduction_discount
    deduction_charges = booking.deductions_for_company
    if deduction_remarks and deduction_charges > 0:
        booking_comments.append('LESS :- {} : Rs. {}'.format(deduction_remarks, deduction_charges))

    return booking_comments


def get_office_data(booking):
    # city = booking.source_office.branch.name + ' - ' + booking.source_office.pin
    city = 'Mumbai-400072'
    footer = booking.source_office.address + ', ' + city
    footer = '610-611, Shivai Plaza Premises Co-Operative Society Limited, Marol Industrial Estate, Marol, Andheri East, Mumbai - 400059'
    office_phone = str(booking.source_office.phone)
    return city, footer, office_phone


def should_apply_service_tax(booking_type, gst_liability):
    return booking_type == 'full' and gst_liability == 'carrier'


def create_invoice(bookings, form_data, amount_data, summary_required, created_by=None, ):
    booking = bookings[0]
    invoice_number = booking.booking_id

    to_be_billed, billing_address, city, pin, invoice_date, gstin = get_billing_info(bookings, form_data)

    if Invoice.objects.filter(invoice_number=invoice_number).exists():
        raise InvoiceError('Invoice: {} already exists'.format(invoice_number))

    comment_text = get_single_booking_comments(booking=booking)

    invoice = Invoice.objects.create(
        invoice_number=get_invoice_number(bookings=bookings, invoice_date=invoice_date,
                                          customer_code=to_be_billed.company_code if isinstance(to_be_billed,
                                                                                                Sme) else ''),
        date=invoice_date,
        company_name=to_be_billed.get_name() if isinstance(to_be_billed, Sme) else None,
        customer_fk=to_be_billed if isinstance(to_be_billed, Sme) else None,
        address=billing_address,
        gstin=gstin,
        city=city,
        pin=pin,
        total_amount=amount_data['total_amount'],
        advance_payment=amount_data['advance_amount'],
        remarks=comment_text,
        service_tax_paid_by=amount_data['gst_liability'],
        created_by=created_by,
        changed_by=created_by,
        summary_required=summary_required
    )
    for booking in bookings:
        invoice.bookings.add(booking)
    update_booking_invoice(invoice=invoice)
    return invoice


def get_invoice_number(bookings, invoice_date, customer_code):
    if len(bookings) == 1:
        booking = bookings[0]
        invoice_number = booking.booking_id
    else:
        if Invoice.objects.filter(invoice_number__istartswith='ah/').exists():
            invoice = Invoice.objects.filter(invoice_number__istartswith='ah/').order_by('id').last()
            invoice_number = 'AH/{}/{}{}{}'.format(
                customer_code.upper(), financial_year_yy(invoice_date),invoice_date.strftime('%m') if isinstance(invoice_date, date) else '',
                str(to_int(invoice.invoice_number[-4:]) + 1).zfill(4)
            )
        else:
            invoice_number = 'AH/{}/{}{}'.format(
                customer_code, invoice_date.strftime('%y%m') if isinstance(invoice_date, date) else '', '0001'
            )
    return invoice_number


def parse_date(date_str):
    if date_str:
        return datetime.strptime(date_str, '%d-%b-%Y')
    else:
        return None


def get_single_booking_pdf_data(invoice):
    invoice_number = invoice.invoice_number
    booking = invoice.bookings.last()
    advance_to_transiq = to_int(booking.advance_amount_from_company)
    advance_to_transiq += to_int(booking.adjusted_cnca_amount)
    other_charges = to_int(booking.total_amount_to_company) - to_int(booking.party_rate * booking.charged_weight)
    if advance_to_transiq > 0:
        balance_amount = to_int(booking.total_amount_to_company) - advance_to_transiq

    else:
        balance_amount = to_int(booking.total_amount_to_company)

    amount_in_words = num2words(balance_amount, to='cardinal', lang='en_IN'
                                ).replace('-', ' ')
    data = {
        'invoice_number': invoice_number,
        'booking_type': 'full',
        'filename': 'inv-{}.pdf'.format(invoice_number.lower()),
        'invoice_date': invoice.date,
        'company_name': invoice.get_company_name(),
        'address': invoice.get_company_address(),
        'lorry_number': booking.supplier_vehicle.number() if booking.supplier_vehicle else '',
        'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
        'from_city': booking.from_city,
        'to_city': booking.to_city,
        'charged_weight': booking.charged_weight,
        'party_rate': format_inr(booking.party_rate),
        'freight': format_inr(to_int(booking.party_rate * booking.charged_weight)),

        'other_charge': format_inr(
            to_int(booking.total_amount_to_company) - to_int(booking.party_rate * booking.charged_weight)),
        'balance_amount': format_inr(balance_amount),
        'advance_to_transiq': advance_to_transiq,
        'advance_to_transiq_inr': format_inr(advance_to_transiq),
        'total_amount': format_inr(to_int(booking.total_amount_to_company)),
        'total_amount_in_rupee': amount_in_words,
        'date': booking.shipment_date,
        'gst_liability_remarks': gst_liability_remarks(booking=booking),
        'remarks': get_single_booking_comments(booking),
        'transiq': get_company_data(),
        'gstin': invoice.gstin if invoice.gstin else '',
        'authorized_signature': get_invoice_authorized_signature()
    }
    return data


def get_invoice_summary_pdf_data(bookings, booking_type, invoice_summary_data):
    office_city_pin, footer, office_phone = get_office_data(bookings[0])
    booking = bookings[0]
    if Invoice.objects.filter(bookings=booking).exists():
        invoice = Invoice.objects.filter(bookings=booking).last()
    else:
        invoice = None
    data = {
        'filename': '{}-{}-{}.pdf'.format(
            'stmt', slugify(invoice.get_company_name()), datetime.now().strftime('%d%b%Y%I%M%S')),
        'booking_type': booking_type,
        'summary_date': invoice.date,
        'invoice_summary_data': invoice_summary_data,
        'office_city_pin': office_city_pin,
        'office_phone': office_phone,
        'footer': footer,
        'company_name': invoice.get_company_name(),
        'address': invoice.get_company_address(),
        'summary_remarks': gst_liability_remarks(booking=booking),
        'gstin': invoice.gstin
    }
    return data
