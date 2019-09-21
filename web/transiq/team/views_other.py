import json
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import FieldError
from django.core.mail.message import EmailMessage
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.html import format_html

from api import s3util
from api.helper import json_success_response
from api.models import S3Upload
from api.s3util import save_to_s3_daily_freight, save_to_s3_daily_sales_report, redirect_to_s3_file
from api.utils import get_or_none, get_ext
from fileupload.models import PODFile
from index.models import RouteFreight, Route, SubRoute
from owner.vehicle_util import display_format, compare_format
from sme.models import Sme
from team.decorators import authenticated_user
from team.services.emails import email_add_new_beneficiary
from team.helper.helper import manual_booking_id_list, to_int
from team.services.payment_auto import get_today_payments, payment_summary_today
from utils.models import Bank, IfscDetail, BankName
from .models import ManualBooking, LrNumber
from .models import Invoice, OutWardPaymentBill


@authenticated_user
def dashboard(request):
    return render(request, 'team/dashboard.html')


@authenticated_user
def supplier_payment_receipt_data(request):
    booking_ids = manual_booking_id_list(username=request.user.username,
                                         user_group_list=request.user.groups.values_list('name', flat=True))
    start = to_int(request.GET.get('start'))
    end = start + to_int(request.GET.get('length'))
    if request.GET.get('search[value]'):
        search_value = request.GET.get('search[value]')
        if LrNumber.objects.filter(lr_number__icontains=search_value).exists():
            booking_ids = LrNumber.objects.filter(lr_number__icontains=search_value).values_list('booking__id')
            payment_receipts = OutWardPaymentBill.objects.filter(
                booking__in=ManualBooking.objects.filter(Q(id__in=booking_ids))).order_by('-id')
        else:
            payment_receipts = OutWardPaymentBill.objects.filter(booking_id__in=booking_ids).filter(
                Q(booking__booking_id__icontains=search_value) | Q(bill_number__icontains=search_value)).order_by('-id')
    else:
        payment_receipts = OutWardPaymentBill.objects.filter(booking_id__in=booking_ids).order_by('-id')
    data = []
    for receipt in payment_receipts[start:end if end != -1 else payment_receipts.count()]:
        data.append([
            receipt.bill_date.strftime('%d-%b-%Y'),
            '{}-{}'.format('OPB', receipt.bill_number),
            format_html('''<a href="{}" download><i class="fa fa-download" aria-hidden="true"></i></a>''',
                        S3Upload.objects.filter(filename__istartswith='{}-{}'.format('OPB', receipt.bill_number),
                                                filename__iendswith='.pdf').last().public_url()) if S3Upload.objects.filter(
                filename__istartswith='{}-{}'.format('OPB', receipt.bill_number),
                filename__iendswith='.pdf').exists() else '',
            receipt.booking.booking_id if receipt.booking else '',
            '<br>'.join(receipt.booking.lr_numbers.values_list('lr_number', flat=True)) if receipt.booking else '',
            '<br>'.join([payment.payment_date.strftime('%d-%b-%Y') if payment.payment_date else '' for payment in
                         receipt.outward_pmt.all()]),
            '<br>'.join([str(to_int(payment.actual_amount)) for payment in receipt.outward_pmt.all()]),
            '<br>'.join([payment.get_payment_mode_display() for payment in receipt.outward_pmt.all()]),
            str(to_int(receipt.amount))
        ])
    data = {
        "draw": to_int(request.GET.get('draw')),
        "recordsTotal": payment_receipts.count(),
        "recordsFiltered": payment_receipts.count(),
        "data": data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


@authenticated_user
def supplier_payment_receipt_page(request):
    return render(request, 'team/payments/supplier_payment_receipt.html')


def downloads_opb_edit_payments(request):
    booking = get_or_none(ManualBooking, id=request.POST.get('booking_id'))
    if booking:
        opb = OutWardPaymentBill.objects.filter(booking=booking)
        if opb:
            try:
                return redirect_to_s3_file("OPB-" + opb.first().bill_number + '.pdf')
            except IOError:
                return HttpResponseRedirect('/team/downloads-bill-payments/')
        else:
            return HttpResponseRedirect('/team/downloads-bill-payments/')
    else:
        return HttpResponseRedirect('/team/downloads-bill-payments/')


@authenticated_user
def pod_archive_data(request):
    booking_ids = manual_booking_id_list(username=request.user.username,
                                         user_group_list=request.user.groups.values_list('name', flat=True))
    start = to_int(request.GET.get('start'))
    end = start + to_int(request.GET.get('length'))
    if request.GET.get('search[value]'):
        search_value = request.GET.get('search[value]')
        pod_files = PODFile.objects.filter(booking_id__in=booking_ids).filter(
            Q(booking__booking_id__icontains=search_value) | Q(
                booking__lr_numbers__lr_number__icontains=search_value) | Q(
                uploaded_by__profile__name=search_value)).order_by('-id')
    else:
        pod_files = PODFile.objects.filter(booking_id__in=booking_ids).order_by('-id')
    data = []
    for pod in pod_files[start:end if end != -1 else pod_files.count()]:
        data.append([
            pod.created_on.strftime('%d-%b-%Y %H:%M'),
            pod.uploaded_by.profile.name if pod.uploaded_by else '',
            pod.booking.booking_id if pod.booking else '',
            pod.lr_number.lr_number if pod.lr_number else '',
            format_html('''<a href="{}" download><i class="fa fa-download" aria-hidden="true"></i></a>''',
                        pod.s3_upload.public_url() if pod.s3_upload else '')
        ])
    data = {
        "draw": to_int(request.GET.get('draw')),
        "recordsTotal": pod_files.count(),
        "recordsFiltered": pod_files.count(),
        "data": data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


@authenticated_user
def pod_archive_page(request):
    return render(request=request, template_name='team/booking/pod-list.html')


def get_lr_details(request):
    if request.method == 'GET' or 'lr_number' not in request.POST:
        return HttpResponseBadRequest()
    try:
        lr_number = LrNumber.objects.get(lr_number=request.POST['lr_number'])
    except LrNumber.DoesNotExist:
        return JsonResponse({
            'error': 'Could not find any entry with LR number {}'
                .format(request.POST['lr_number'])
        })

    booking = lr_number.booking
    data = {
        'lr_number': lr_number.lr_number,
        'id': booking.id,
        'lorry_number': booking.lorry_number,
        'from_city': booking.from_city,
        'to_city': booking.to_city,
        'company': booking.consignor_name,
        'address': booking.consignor_address,
        'city': booking.consignor_city,
        'loaded_weight': booking.loaded_weight,
        'charged_weight': booking.charged_weight,
        'rate': booking.party_rate,
        'total_amount_to_company': booking.total_amount_to_company,
        'advance_amount_from_company': booking.advance_amount_from_company,
        'additional_charges_for_company': booking.additional_charges_for_company,
        'note_for_additional_company_charges': booking.note_for_additional_company_charges,
        'invoice_comment': booking.invoice_remarks,
    }
    return JsonResponse(data)


def register_beneficiary_bank_account(request):
    return render(request=request, template_name='team/registrations/fetch-bank-details-using-ifsc.html')


def fetch_bank_details_using_ifsc(request):
    read_only = False
    try:
        ifsc = IfscDetail.objects.get(ifsc_code__iexact=request.GET.get('fetch_ifsc'))
        read_only=True
    except IfscDetail.DoesNotExist:
        ifsc = None
    return render(request=request, template_name='team/registrations/register_beneficiary_bank_account.html',
                  context={'ifsc': ifsc,
                           "read_only": read_only,
                           'users': User.objects.exclude(
                               Q(profile__name=None) | Q(profile__phone=None)).values(
                               'id', 'profile__name', 'profile__phone', 'username'), 'banks': BankName.objects.all()})


def create_beneficiary_account(request):
    account_number = request.POST.get('account_number')
    bank = get_or_none(Bank, account_number=account_number)
    if bank:
        return render(request=request, template_name='team/registrations/beneficiary_exists.html',
                      context={'bank': bank})

    try:
        account_document = request.FILES['account_document']
    except MultiValueDictKeyError:
        account_document = None

    bank = Bank.objects.create(
        bank=request.POST.get('bank_name'),
        user=get_or_none(User, id=request.POST.get('registered_user')),
        account_holder_name=request.POST.get('account_holder_name'),
        beneficiary_code=request.POST.get('beneficiary_code'),
        account_number=account_number,
        transaction_type=request.POST.get('transaction_type'),
        account_type=request.POST.get('account_type'),
        ifsc=request.POST.get('ifsc'),
        address=request.POST.get('address'),
        city=request.POST.get('city'),
    )
    email_add_new_beneficiary(bank=bank)
    if account_document:
        filename = '%s.%s' % (account_number, get_ext(account_document.name))
        s3util.save_to_s3_uploads_bank_doc(filename, account_document)
    return HttpResponseRedirect('/team/beneficiary-list/')


def update_bank_account_page(request):
    try:
        bank = Bank.objects.get(id=request.GET.get('account_id'))
        return render(request=request, template_name='team/registrations/update-bank-account.html',
                      context={'bank': bank, 'users': User.objects.exclude(
                          Q(profile__name=None) | Q(profile__phone=None)).values(
                          'id', 'profile__name', 'profile__phone'), 'banks': BankName.objects.all()})
    except Bank.DoesNotExist:
        raise Http404


def update_bank_account(request):
    Bank.objects.filter(id=request.POST.get('account_id')).update(
        bank=request.POST.get('bank_name'),
        user=get_or_none(User, id=request.POST.get('registered_user')),
        account_holder_name=request.POST.get('account_holder_name'),
        beneficiary_code=request.POST.get('beneficiary_code'),
        account_number=request.POST.get('account_number'),
        transaction_type=request.POST.get('transaction_type'),
        account_type=request.POST.get('account_type'),
        ifsc=request.POST.get('ifsc'),
        address=request.POST.get('address'),
        city=request.POST.get('city'),
        is_verified=request.POST.get('is_verified'),
        status=request.POST.get('status'),
    )
    return HttpResponseRedirect('/team/beneficiary-list/')


def beneficiary_list(request):
    accounts = Bank.objects.all()
    return render(request, 'team/payments/beneficiary_list.html', {'accounts': accounts})


def download_payment_file_post(request):
    download_file = request.POST.get('download_payment_file', None)
    send_file = request.POST.get('send_payment_file', None)
    send_sales_report = request.POST.get('send_sales_report', None)
    if download_file:
        dl_url = get_today_payments()
        if not dl_url:
            return HttpResponseBadRequest('no url found')
        return HttpResponseRedirect(redirect_to=dl_url)
    if send_file:
        dl_url = payment_summary_today()
        msg = "Email sent to " + ', '.join(
            ['harsh@aaho.in', 'pankaj@aaho.in', 'rohit@aaho.in', 'sandeshlakhan108@gmail.com',
             'sanjay.aaho123@gmail.com', 'amit@aaho.in', 'nareshchvj@gmail.com'])
        messages.error(request, "Mail sent successfully")
        return HttpResponseRedirect(redirect_to=dl_url)
    if send_sales_report:
        mb = ManualBooking.objects.filter(
            created_on__date=datetime.now().date() - timedelta(days=1)
        ).exclude(
            booking_status='cancelled'
        ).order_by(
            '-shipment_date'
        )
        if mb:
            data = []
            for booking in mb:
                try:
                    data.append([
                        booking.booking_id,
                        '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                        booking.from_city,
                        booking.to_city,
                        booking.party_rate,
                        booking.charged_weight,
                        booking.total_amount_to_company,
                        booking.supplier_rate,
                        booking.supplier_charged_weight,
                        booking.total_amount_to_owner,
                        booking.total_amount_to_company - booking.total_amount_to_owner,
                        "{0:.2f}".format(((
                                                  booking.total_amount_to_company - booking.total_amount_to_owner) / booking.total_amount_to_owner) * 100)
                    ])
                except ZeroDivisionError:
                    data.append([
                        booking.booking_id,
                        '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                        booking.from_city,
                        booking.to_city,
                        booking.party_rate,
                        booking.charged_weight,
                        booking.total_amount_to_company,
                        booking.supplier_rate,
                        booking.supplier_charged_weight,
                        booking.total_amount_to_owner,
                        booking.total_amount_to_company - booking.total_amount_to_owner,
                        'Amount to owner is zero'
                    ])

            df = pd.DataFrame(data=data,
                              columns=['Booking ID', 'LR Number(s)', 'From City', 'To City', 'Party Rate',
                                       'Party Weight',
                                       'Party Amount', 'Supplier Rate', 'Supplier Weight', 'Supplier Amount', 'Profit',
                                       '% Profit'])
            bytes_io = BytesIO()
            df.to_csv(bytes_io, index=False)
            bytes_io.seek(0)
            content = bytes_io.getvalue() or '\n'
            filename = datetime.now().strftime('%d%b%Y%I%M') + '.csv'
            s3_upload = save_to_s3_daily_sales_report(filename, content)
            s3_url = s3_upload.public_url()
            subject = '[Aaho] Daily Sales Report for ' + (datetime.now().date() - timedelta(days=1)).strftime(
                '%d-%b-%Y')
            body = get_template('team/emails/last-day-bookings.html').render(context={'mb': mb, 's3_url': s3_url})
            email = EmailMessage(subject, body,
                                 to=['harsh@aaho.in', 'tp.ananth@aaho.in', 'rohit@aaho.in', 'pankaj@aaho.in'])
            email.content_subtype = 'html'
            email.send()
    return HttpResponseRedirect('/team/download-payment-file/')


def download_payment_file_page(request):
    return render(request, 'team/download_outward_payment_file.html')


def customer_accounting_summary(request):
    try:
        bookings = ManualBooking.objects.exclude(booking_status='cancelled').exclude(
            Q(company__name__profile__name=None) | Q(company__name__profile__name='')).values(
            'company__name__profile__name').annotate(
            total_amount_to_company=Sum('total_amount_to_company'),
            total_received_amount=Sum('total_in_ward_amount'),
            number_of_booking=Count('id'))
    except FieldError:
        bookings = {}
    return render(request=request, template_name='team/accounting/placed-order-customer-summary.html',
                  context={'bookings': bookings})


def supplier_accounting_summary_data():
    try:
        bookings = ManualBooking.objects.filter(shipment_date__lte='2018-03-31').exclude(
            booking_status='cancelled').exclude(
            Q(truck_broker_owner_name=None) | Q(truck_broker_owner_name='')).values('truck_broker_owner_name').annotate(
            total_amount_to_owner=Sum('total_amount_to_owner'),
            total_paid_amount=Sum('total_out_ward_amount'),
            number_of_booking=Count('id'))
    except FieldError:
        bookings = {}
    df = pd.DataFrame(data=list(bookings))
    df.to_excel('supplier_accounting_summary_data_till_20180331.xlsx')
    return bookings


def supplier_accounting_summary(request):
    try:
        bookings = ManualBooking.objects.exclude(booking_status='cancelled').exclude(
            Q(truck_broker_owner_name=None) | Q(truck_broker_owner_name='')).values('truck_broker_owner_name').annotate(
            total_amount_to_owner=Sum('total_amount_to_owner'),
            total_paid_amount=Sum('total_out_ward_amount'),
            number_of_booking=Count('id'))
    except FieldError:
        bookings = {}
    return render(request=request, template_name='team/accounting/supplier-summary.html', context={'bookings': bookings})


def owner_accounting_summary(request):
    try:
        bookings = ManualBooking.objects.exclude(booking_status='cancelled').exclude(
            Q(truck_owner_name=None) | Q(truck_owner_name='')).values('truck_owner_name').annotate(
            total_amount_to_owner=Sum('total_amount_to_owner'),
            total_paid_amount=Sum('total_out_ward_amount'),
            number_of_booking=Count('id'))
    except FieldError:
        bookings = {}
    return render(request=request, template_name='team/accounting/vehicle-summary.html', context={'bookings': bookings})




def create_sub_route(route, loading_point, unloading_point):
    return SubRoute.objects.create(
        route=route,
        loading_point=loading_point,
        unloading_point=unloading_point
    )


def create_route_freight(route, freight, material, datetime):
    RouteFreight.objects.create(
        route=route,
        freight=freight,
        material=material,
        datetime=datetime.now()
    )


def upload_daily_freight(request):
    try:
        save_to_s3_daily_freight(datetime.now().strftime('%Y%m%d%H%M') + '.xlsx',
                                 request.FILES['daily_freight'])
    except:
        raise
    try:
        filename = S3Upload.objects.filter(folder__iexact='freight').latest('created_on').public_url()
        df = pd.read_excel(filename)
        for i, rows in df.iterrows():
            route = map(str.strip, map(str, rows['Route'].split('-')))
            if Route.objects.filter(Q(source__iexact=route[0]) & Q(destination__iexact=route[1])).exists():
                route = Route.objects.get(Q(source__iexact=route[0]) & Q(destination__iexact=route[1]))
                route.updated_on = datetime.now()
                route.save()
                if SubRoute.objects.filter(Q(loading_point__iexact=rows['Loading Point']) & Q(
                        unloading_point__iexact=rows['Unloading Point'])).exists():
                    SubRoute.objects.filter(Q(loading_point__iexact=rows['Loading Point']) & Q(
                        unloading_point__iexact=rows['Unloading Point'])).update(updated_on=datetime.now())
                    RouteFreight.objects.create(
                        route=SubRoute.objects.get(Q(loading_point__iexact=rows['Loading Point']) & Q(
                            unloading_point__iexact=rows['Unloading Point'])),
                        freight=rows['Freight (per ton)'],
                        material=rows['Material'],
                        datetime=datetime.now()
                    )
                else:
                    RouteFreight.objects.create(
                        route=create_sub_route(route=route, loading_point=rows['Loading Point'],
                                               unloading_point=rows['Unloading Point']),
                        freight=rows['Freight (per ton)'],
                        material=rows['Material'],
                        datetime=datetime.now()
                    )
            else:
                route = Route.objects.create(source=route[0], destination=route[1])
                if SubRoute.objects.filter(Q(loading_point__iexact=rows['Loading Point']) & Q(
                        unloading_point__iexact=rows['Unloading Point'])).exists():
                    SubRoute.objects.filter(Q(loading_point__iexact=rows['Loading Point']) & Q(
                        unloading_point__iexact=rows['Unloading Point'])).update(updated_on=datetime.now())
                    RouteFreight.objects.create(
                        route=SubRoute.objects.get(Q(loading_point__iexact=rows['Loading Point']) & Q(
                            unloading_point__iexact=rows['Unloading Point'])),
                        freight=rows['Freight (per ton)'],
                        material=rows['Material'],
                        datetime=datetime.now()
                    )
                else:
                    RouteFreight.objects.create(
                        route=create_sub_route(route=route, loading_point=rows['Loading Point'],
                                               unloading_point=rows['Unloading Point']),
                        freight=rows['Freight (per ton)'],
                        material=rows['Material'],
                        datetime=datetime.now()
                    )
        return json_success_response('Uploaded successfully')
    except:
        raise


def download_master_table():
    columns = [
        'Booking ID', 'LR Numbers', 'Shipment Date', 'Billing Type', 'Source Office', 'Destination Office', 'From City',
        'To City', 'Customer who placed order', 'Customer who will make payment', 'Supplier Name', 'Supplier Phone',
        'Owner Name', 'Owner Phone', 'Vehicle Number', 'Driver Name', 'Driver Phone', 'Actual Weight',
        'Charged Weight to Customer', 'Charged Weight for Supplier', 'Customer Rate', 'Supplier Rate',
        'Total Amount from Customer', 'Refundable Amount', 'Deduction for Customer', 'Total Inward Amount', 'TDS',
        'Total Amount to Owner', 'Commission', 'LR Cost', 'Deduction for Advance', 'Deduction for Balance',
        'Other Deduction', 'Deduction Remarks', 'Invoice Status', 'Total Outward Amount', 'Outward Payment Remarks',
        'Invoice Number', 'Invoice Date', 'Invoice Amount', 'OPB Number', 'OPB Date', 'OPB Amount', 'POD Status'
    ]
    data = [[
        booking.booking_id,
        '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
        booking.shipment_date,
        booking.get_billing_type_display(),
        booking.source_office.branch.name if booking.source_office else '',
        booking.destination_office.branch.name if booking.destination_office else '',
        booking.from_city,
        booking.to_city,
        booking.company.get_name() if booking.company else '',
        booking.customer_to_be_billed_to.get_name() if booking.customer_to_be_billed_to else '',
        booking.truck_broker_owner_name,
        booking.truck_broker_owner_phone,
        booking.truck_owner_name,
        booking.truck_owner_phone,
        display_format(compare_format(booking.lorry_number)),
        booking.driver_name,
        booking.driver_phone,
        booking.loaded_weight,
        booking.charged_weight,
        booking.supplier_charged_weight,
        booking.party_rate,
        booking.supplier_rate,
        booking.total_amount_to_company,
        booking.refund_amount,
        booking.deductions_for_company,
        booking.total_in_ward_amount,
        booking.tds_deducted_amount,
        booking.total_amount_to_owner,
        booking.commission,
        booking.lr_cost,
        booking.deduction_for_advance,
        booking.deduction_for_balance,
        booking.other_deduction,
        booking.remarks_about_deduction,
        booking.get_invoice_status_display(),
        sum(booking.outward_booking.values_list('actual_amount', flat=True)),
        '\n'.join([', '.join(map(str, row)) for row in
                   booking.outward_booking.values_list('payment_mode', 'actual_amount', 'remarks')]),
        ''.join(list(booking.invoices.values_list('invoice_number', flat=True)) + list(
            booking.to_pay_invoices.values_list('invoice_number', flat=True))),
        ''.join([invoice_date.strftime('%d-%b-%Y') if invoice_date else '' for invoice_date in
                 list(booking.invoices.values_list('date', flat=True)) + list(
                     booking.to_pay_invoices.values_list('date', flat=True))]),
        ''.join(list(map(str, list(booking.invoices.values_list('total_amount', flat=True)))) + list(
            booking.to_pay_invoices.values_list('amount_payable_to_transiq', flat=True))),
        '\n'.join(booking.outward_payment_bill.values_list('bill_number', flat=True)),
        '\n'.join([opb.bill_date.strftime('%d-%b-%Y') if opb.bill_date else '' for opb in
                   booking.outward_payment_bill.all()]),
        '\n'.join(map(str, booking.outward_payment_bill.values_list('amount', flat=True))),
        booking.pod_status
    ] for booking in
        ManualBooking.objects.filter(Q(company_id=39) | Q(customer_to_be_billed_to__id=39)).filter(
            shipment_date__gte=datetime.today().date() - timedelta(days=300)).exclude(
            booking_status='cancelled').order_by('-shipment_date')]

    df = pd.DataFrame(data=data, columns=columns)
    df.to_excel('booking data from %s to %s.xlsx' % (
        (datetime.now() - timedelta(days=200)).strftime('%d-%b-%Y'), datetime.now().strftime('%d-%b-%Y %H:%M')),
                index=False)
