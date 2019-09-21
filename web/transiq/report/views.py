from decimal import Decimal

from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta

from django.utils.html import format_html

from report.invoice import make_invoice
from report.lr_html import get_lr_data
from report.util import get_receipt_pdf_content, get_lr_pdf_content, get_single_booking_invoice_pdf_content, \
    get_company_data, \
    get_invoice_authorized_signature, get_logo_data
from team.models import ManualBooking
from utils.models import AahoOffice, State, City


def test_booking_invoice(request):
    booking = ManualBooking.objects.get(booking_id='AAHO01591')
    invoice_number, content = make_invoice(booking, booking_type='commission', return_html=True)
    return HttpResponse(content)


def get_dummy_receipt_data():
    receipt_number = 'OP-DEM007'
    filename = '%s.pdf' % (receipt_number or 'untitled')
    data = {
        'receipt_number': receipt_number,
        'filename': filename,
        'owner_name': 'Shobhit Vashistha',
        'owner_pan': 'AOKLB4947N',
        'bill_number': receipt_number,
        'vehicle_number': 'MH 03 BR 9878',
        'from_city': 'Ahmedabad',
        'to_city': 'Vishakhapatnam',
        'loading_date': '17-Feb-2017',
        'weight': '21.876 MT',
        'rate': '1600',
        'bill_date': '27-Feb-2017',
        'freight_charge': '35000.0',
        'loading_charge': '100.0',
        'unloading_charge': '300.0',
        'detention_charge': '900.0',
        'other_charge': '100.0',
        'commission_charge': '500.0',
        'lr_charge': '200.0',
        'deduction_for_advance': '450.0',
        'deduction_for_balance': '300.0',
        'deduction_for_balance2': '300.0',
        'date1': '17-Feb-2017',
        'date2': '02-Feb-2017',
        'date3': '27-Feb-2017',
        'paid_via_account': '10000.0',
        'advance_by_cash': 5000.0,
        'balance_by_neft': 19950.0,
        'total_payable_amount': 34950.0,
        'payment_data': {
            'payment_list': [
                {'payment_date': '17-Feb-2017', 'remarks': 'Paid by so and so via so and so, such details, much wow',
                 'amount': 2000.0},
                {'payment_date': '17-Feb-2017', 'remarks': 'Paid by details', 'amount': 2000.0},
                {'payment_date': '17-Feb-2017', 'remarks': 'NEFT Yaass!!', 'amount': 2000.0},
                {'payment_date': '17-Feb-2017', 'remarks': 'Cash Cash Cash', 'amount': 2000.0},
                {'payment_date': '17-Feb-2017', 'remarks': 'Paid by so and so via so and so, such details, much wow',
                 'amount': 2000.0},
                {'payment_date': '17-Feb-2017', 'remarks': 'Paid by so and so via so and so, such details, much wow',
                 'amount': 2000.0},
                {'payment_date': '17-Feb-2017', 'remarks': 'Paid by details', 'amount': 2000.0},
                {'payment_date': '17-Feb-2017', 'remarks': 'NEFT Yaass!!', 'amount': 2000.0},
                {'payment_date': '17-Feb-2017', 'remarks': 'Cash Cash Cash', 'amount': 2000.0},
            ],
            'total_amount': 16000.0
        }
    }
    return data


def test_receipt_view(request):
    pdf = request.GET.get('t', 'h') == 'p'
    data = get_dummy_receipt_data()
    file_name = data['filename']
    if pdf:
        content = get_receipt_pdf_content(data)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        response.write(content)
        return response
    else:
        return render(request, 'receipt/main.html', data)


def get_dummy_invoice_data():
    invoice_number = 'TB-DEM1001'
    filename = '%s.pdf' % (invoice_number or 'untitled')
    data = {
        'invoice_number': invoice_number,
        'booking_type': 'full',
        'filename': filename,
        'invoice_date': datetime.now(),
        'company_name': 'Canpac Trends Pvt. Ltd.',
        'address': '3rd Lane, Gulabshah Estate, Behind Kurla Depot, Kurla West, Mumbai-400065',
        'lorry_number': 'MH04 BR 1023',
        'lr_number': 'DEM170303005\nDEM170303005\nDEM170303005',
        'from_city': 'Ahmedabad',
        'to_city': 'Vishakhapatnam',
        'charged_weight': '28.843',
        'party_rate': u'\u20b9\xa05,150',
        'freight': u'\u20b9\xa01,52,492',
        'other_charge': u'\u20b9\xa018,47,508',
        'total_amount': u'\u20b9\xa020,00,000',
        'total_amount_in_rupee': 'one lakh, twenty-three thousand, four hundred and fifty-four',
        'date': datetime.now() - timedelta(days=7),
        'gst_liability_remarks': "GST Payable under Reverse Charge by recipient of services as per notification no. 13/2017 dated 28th June 2017",
        'remarks': [u'ADD :- One day detention charges : Rs. 1000',
                    u'LESS :- Rs 1000 detention not paid by client..not recoverable : Rs. 1000'],
        'transiq': get_company_data(),
        'gstin': '',
        'authorized_signature': get_invoice_authorized_signature()
    }
    return data


def test_single_booking_invoice_view(request):
    pdf = request.GET.get('t', 'h') == 'p'
    data = get_dummy_invoice_data()
    file_name = data['filename']
    if pdf:
        content = get_single_booking_invoice_pdf_content(data)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        response.write(content)
        return response
    else:
        return render(request, 'invoice/single_booking_invoice.html', data)


def get_dummy_multiple_invoice_data():
    data = {
        "invoice_number": "AH/IDL/1805002",
        "invoice_date": "15-Aug-2018",
        "customer_name": "Canpac Trends Pvt. Ltd.",
        "customer_address": "3rd Lane, Gulabshah Estate, Behind Kurla Depot, Kurla West, Mumbai-400065",
        "gstin": "CBPPK6928P1234",
        "is_full_booking": False,
        "is_other_charges": False,
        "gst_liability_remarks": "GST Payable under Reverse Charge by recipient of services as per notification no. 13/2017 dated 28th  June 2017",
        "remarks": 'In case of any descrepancy',
        "logo": get_logo_data(),
        'authorized_signature':get_invoice_authorized_signature(),
        "invoice_data": [
            {
                "date": "25-Aug-2018",
                "source": "Vishakhapatnam",
                "destination": "Ahmedabad",
                "lr_numbers": "VVR180606110",
                "vehicle_number": "MH16 AR 9870",
                "rate": 23.45,
                "quantity": 234,
                "other_charges": 234,
                "amount": 23443
            },
            {
                "date": "25-Aug-2018",
                "source": "Vishakhapatnam",
                "destination": "Ahmedabad",
                "lr_numbers": format_html("""
                VVR180606110</br>VVR180606112"""),
                "vehicle_number": "MH16 AR 9870",
                "rate": 23.45,
                "quantity": 234,
                "other_charges": 234,
                "amount": 23443
            },
            {
                "date": "25-Aug-2018",
                "source": "Vishakhapatnam",
                "destination": "Ahmedabad",
                "lr_numbers": "VVR180606110",
                "vehicle_number": "MH16 AR 9870",
                "rate": 23.45,
                "quantity": 234,
                "other_charges": 234,
                "amount": 23443
            },
            {
                "date": "25-Aug-2018",
                "source": "Vishakhapatnam",
                "destination": "Ahmedabad",
                "lr_numbers": format_html("""
                VVR180606110</br>VVR180606112"""),
                "vehicle_number": "MH16 AR 9870",
                "rate": 23.45,
                "quantity": 234,
                "other_charges": 234,
                "amount": 23443
            },
            {
                "date": "25-Aug-2018",
                "source": "Vishakhapatnam",
                "destination": "Ahmedabad",
                "lr_numbers": format_html("""
                VVR180606110</br>VVR180606112"""),
                "vehicle_number": "MH16 AR 9870",
                "rate": 23.45,
                "quantity": 234,
                "other_charges": 234,
                "amount": 23443
            },
            {
                'total_amount':5677,
                "other_charges":9899
            }
        ]
    }
    return data


def test_multiple_booking_invoice_view(request):
    pdf = request.GET.get('t', 'h') == 'p'
    data = get_dummy_multiple_invoice_data()
    file_name = data['invoice_number']
    if pdf:
        content = get_single_booking_invoice_pdf_content(data)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        response.write(content)
        return response
    else:
        return render(request, 'invoice/multiple_booking_invoice.html', data)


def test_lr_view(request):
    pdf = request.GET.get('t', 'h') == 'p'
    data = get_lr_data(ManualBooking.objects.get(id=7238))
    data['lr_date'] = timezone.now().date().strftime('%d-%b-%Y')
    data['lr_number'] = 'FAK170310007'
    file_name = data['lr_number'] + '.pdf'
    if pdf:
        content = get_lr_pdf_content(data)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        response.write(content)
        return response
    else:
        return render(request, 'lr/main.html', data)


def invoice_summary_test(request):
    data = {'address': u'Plot No. 3, Road No. 1, Kathwada GIDC, Ahmedabad - 382430',
            'summary_remarks': 'GST Payable under Reverse Charge by recipient of services as per notification no. 13/2017 dated 28th June 2017',
            'invoice_summary_data': [
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'gross_amount': 26000, 'weight': Decimal('1.000'), 'vehicle_number': u'HR39 B 1601',
                 'other_charges': 0, 'lr_number': u'MCC180329302', 'invoice_date': '02-Apr-2018',
                 'shipment_date': '02-Apr-2018',
                 'to_city': u'Hoshiarpur', 'rate': 26000, 'from_city': u'Ahmedabad', 'invoice_number': u'AAHO05969'},
                {'to_city': '', 'rate': '', 'other_charges': 0, 'shipment_date': '02-Apr-2018',
                 'weight': Decimal('1.000'), 'vehicle_number': '',
                 'from_city': '', 'invoice_number': '', 'gross_amount': 26000, 'invoice_date': ''}],
            'filename': 'mehta-cad-cam-systems-pvt-ltd-02Apr2018084203.pdf', 'office_city_pin': 'Mumbai-400072',
            'footer': '610-611, Shivai Plaza Premises Co-Operative Society Limited, Marol Industrial Estate, Marol, Andheri East, Mumbai - 400059',
            'summary_date': datetime.now(), 'booking_type': u'full',
            'office_phone': '7987768461, 9111008628', 'company_name': u'MEHTA CAD CAM SYSTEMS PVT. LTD.',
            'gstin': u'24AACCM4397B1ZO',
            'transiq': get_company_data(),

            }

    return render(request=request, template_name='invoice/invoice_summary.html', context=data)


def get_test_lr_request():
    state, _ = State.objects.get_or_create(name='Chhattisgarh')
    city, _ = City.objects.get_or_create(name='Raipur', state=state)
    aaho_office, _ = AahoOffice.objects.get_or_create(branch=city)
    aaho_office.address = 'Shop No.-3, Plot No.- W/2/41, Block-8, Parking-6, Near Goyal Bhawan, Transport Nagar, Rawabhata'
    aaho_office.branch_head = 'Amit Kumar'
    aaho_office.email = 'amit@aaho.in'
    aaho_office.pin = '492001'
    aaho_office.save()

    data = {
        'consignor_name': 'EXAMPLE CONSIGNOR',
        'consignor_address': '000, EXAMPLE STREET, EXAMPLE LENGTHY NAME TOWN, NOWHERE STATE',
        'consignor_city': 'SOMEWHERE CITY',
        'consignor_pin': '421124',
        'consignor_phone': '8978937498',
        'consignor_cst_tin': 'DEEZ00NUTS007',
        'consignee_name': 'AMAZING CONSIGNEE',
        'consignee_address': '666, AWESOME STREET, QUITE FINE TOWN, ELSEWHERE STATE',
        'consignee_city': 'OTHER CITY',
        'consignee_pin': '124421',
        'consignee_phone': '9666666666',
        'consignee_cst_tin': '1CAN0HA2CHEESE8URGER',
        'from': 'Somewhere City',
        'to': 'Other city',
        'lorry_number': 'XX00 XX 0000',
        'driver_dl_number': 'DL666DIAL007',
        'driver_phone': '9314159265',
        'party_invoice_number': 'EXA10067',
        'party_invoice_amount': '10000.00',
        'road_permit_number': 'PERMIT666007',
        'number_of_package': '50',
        'loaded_weight': '10 Tons',
        'charged_weight': '10 Tons',
        'supplier_rate': '1000.0',
        'material': 'Unobtainium, a hypothetical material with all the desired design properties',
        'insured': 'insured',
        'insurance_provider': 'NICE Insurance Provider',
        'insurance_policy_number': 'NICE00101',
        'insurance_date': '10-Mar-2017',
        'insurance_amount': '5000.00',
        'insurance_risk': '',
        'gst_liability': 'consignee',
        'billing_type': 'To Pay',
        'source_office': str(aaho_office.id),
        'is_print_payment_mode_instruction': 'yes',
        'pod_reporting_datetime': '10:00 AM, 12-Mar-2017',
        'pod_unloading_datetime': '11:00 AM, 12-Mar-2017',
        'party_invoice_date': '03/10/2017'
    }
    return FakeRequest(data)


class FakeRequest(object):

    def __init__(self, data):
        self.POST = data
