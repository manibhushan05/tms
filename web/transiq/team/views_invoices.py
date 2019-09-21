import io
import json
import zipfile

import requests
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.http.response import HttpResponse, Http404
from django.shortcuts import render
from django.utils.html import format_html

from api import s3util
from api.decorators import authenticated_user
from api.helper import EMP_GROUP2, EMP_GROUP3, EMP_GROUP1
from api.models import S3Upload
from api.s3util import redirect_to_s3_file
from api.utils import get_or_none
from report import invoice
from report.lr_html import generate_lorry_receipt
from sme.models import Sme
from team import views_booking
from team.decorators import only_get, only_post
from team.helper.helper import check_invoice_status, manual_booking_id_list, to_int
from team.models import Invoice, ManualBooking, LrNumber, OutWardPayment, InvoiceSummary
from team.services import full_booking, commission_booking


def invoice_form_data(request):
    customer = get_or_none(Sme, id=request.POST.get('to_be_billed_to'))
    return {
        'billing_address': request.POST.get('billing_address'),
        'invoice_city': request.POST.get('invoice_city'),
        'pin_code': request.POST.get('invoice_pin'),
        'to_be_billed_to': customer.id if isinstance(customer, Sme) else '',
        'party_invoice_date': request.POST.get('billing_invoice_date'),
        'gst_liability': request.POST.get('gst_liability'),
        'advance_from_company': request.POST.get('advance_from_company'),
        'created_by': get_or_none(User, username=request.user.username)
    }


@only_post
@authenticated_user
def save_edited_booking_data(request):
    try:
        submit_type = request.POST.get('submit_type')
        booking = ManualBooking.objects.get(id=request.POST['booking_id'])
        booking = full_booking.save_existing_manual_booking_data(request, booking.id)
        if submit_type == 'save_only':
            return HttpResponseRedirect('/team/full-booking-history/')
        elif submit_type == 'save_and_print':
            zip_s3_upload = generate_lorry_receipt(booking)
            return HttpResponseRedirect(redirect_to=zip_s3_upload.public_url())
        elif submit_type == 'print_invoice':
            if check_invoice_status(booking):
                return HttpResponseRedirect('/team/duplicate-invoice-gen/')
            try:
                invoice.make_invoice(
                    ManualBooking.objects.filter(id=booking.id),
                    booking_type='full',
                    form_data=invoice_form_data(request=request),
                    created_by=request.user
                )
                return HttpResponseRedirect('/team/booking-edit/?booking_id={}'.format(booking.id))
            except invoice.InvoiceError:
                return HttpResponseRedirect('/team/duplicate-invoice-gen/')
        elif submit_type == 'download_lr':
            lr_numbers = booking.lr_numbers.values_list('lr_number', flat=True)
            zip_file_name = ''
            iteration_number = 0
            for value in lr_numbers:
                if iteration_number == 0:
                    zip_file_name += value[0:12]
                    iteration_number += 1
                else:
                    zip_file_name += '_' + value[9:12]
            zip_file_name = '{}.zip'.format(zip_file_name)
            return redirect_to_s3_file(zip_file_name)
        elif submit_type == 'download_invoice':
            inv = Invoice.objects.filter(bookings=booking).last()
            if inv and isinstance(inv.s3_upload, S3Upload):
                return HttpResponseRedirect(inv.s3_upload.public_url())
            else:
                raise Http404
        else:
            raise Http404
    except ManualBooking.DoesNotExist:
        raise Http404


@authenticated_user
def save_edited_commission_only_booking_data(request):
    booking = ManualBooking.objects.get(id=request.POST.get('booking_id'))
    submit_type = request.POST.get('submit_type')
    commission_booking.update_commission_booking(request)
    if submit_type == 'save_only':
        return HttpResponseRedirect('/team/partial-booking-history/')
    elif submit_type == 'print_invoice':
        if check_invoice_status(booking):
            return HttpResponseRedirect('/team/duplicate-invoice-gen/')
        try:
            invoice.make_invoice(
                ManualBooking.objects.filter(id=booking.id),
                booking_type='commission',
                form_data=invoice_form_data(request=request),
                created_by=request.user
            )
            return HttpResponseRedirect('/team/booking-edit/?booking_id={}'.format(booking.id))
        except invoice.InvoiceError:
            return HttpResponseRedirect('/team/duplicate-invoice-gen/')
    elif submit_type == 'download_invoice':
        inv = Invoice.objects.filter(bookings=booking).last()
        if inv and isinstance(inv.s3_upload, S3Upload):
            return HttpResponseRedirect(inv.s3_upload.public_url())
        else:
            raise Http404
    else:
        raise Http404


def full_booking_invoice_fetch_data():
    bookings = [
        {'id': booking.id, 'booking_id': booking.booking_id,
         'lr_numbers': ','.join(booking.lr_numbers.values_list('lr_number', flat=True))}
        for booking in ManualBooking.objects.filter(Q(booking_id__istartswith='AH') | Q(
            booking_id__istartswith='AAHO')).
            filter(invoice_status='no_invoice').exclude(booking_status='cancelled').order_by('-shipment_date')
    ]
    customers = [{'id': sme.id, 'name': sme.get_name(), 'code': sme.company_code} for sme in Sme.objects.all()]
    return {'bookings': bookings, 'customers': customers}


def commission_invoice_fetch_data():
    bookings = [
        {'id': booking.id, 'booking_id': booking.booking_id, 'company_code': booking.company_code}
        for booking in ManualBooking.objects.filter(Q(booking_id__istartswith='AB') | Q(
            booking_id__istartswith='BROKER')).
            filter(invoice_status='no_invoice').exclude(booking_status='cancelled').order_by('-shipment_date')
    ]
    customers = [{'id': sme.id, 'name': sme.get_name(), 'code': sme.company_code} for sme in Sme.objects.all()]
    return {'bookings': bookings, 'customers': customers}


# @authenticated_user
def fetch_full_booking_invoice_data_page(request):
    return render(request=request, template_name='team/invoices/fetch_full_booking_invoice_data.html')


@authenticated_user
def fetch_commission_invoice_data_page(request):
    return render(request=request, template_name='team/invoices/fetch-commission-invoice.html',
                  context=commission_invoice_fetch_data())


@authenticated_user
def commission_invoice_page(request):
    customer = get_or_none(Sme, id=request.GET.get('customer_to_be_billed'))
    bookings = ManualBooking.objects.filter(id__in=request.GET.getlist('booking_id[]'))
    if not bookings.exists() or not isinstance(customer, Sme):
        return HttpResponseRedirect('/team/commission-invoice-data-page/')
    invoice_data = get_invoice_data(bookings, 'commission')
    comment_list = get_comment_list(bookings, invoice_data)
    return render(request, 'team/invoices/commission_booking_invoice.html',
                  {'booking_data': invoice_data, 'customer': customer,
                   'gst_liability': bookings.last().gst_liability,
                   'booking_ids': ','.join(map(str, bookings.values_list('id', flat=True))),
                   'comment_list': comment_list,
                   'invoice_amount_data': get_amount_data(bookings=bookings, booking_type='full'),
                   })


def get_single_booking_invoice_data(booking, booking_type):
    row = {
        'id': booking.id,
        'booking_id': booking.booking_id,
        'date': booking.shipment_date,
        'from_city': booking.from_city,
        'to_city': booking.to_city,
        'lorry_number': booking.lorry_number,
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


@authenticated_user
def full_booking_multi_invoice_booking_data(request):
    rows = to_int(request.GET.get('page'))
    search_value = request.GET.get('search')
    exclude_kwargs = Q(booking_status__iexact='cancelled') | Q(deleted=True) | Q(booking_id__istartswith='AB') | Q(
        booking_id__istartswith='BROKER')
    bookings = ManualBooking.objects.filter(Q(invoice_status__iexact='no_invoice')).exclude(
        exclude_kwargs).order_by('-id', '-shipment_date')
    if search_value:
        bookings = ManualBooking.objects.filter(
            Q(invoice_status__iexact='no_invoice') & (Q(booking_id__icontains=search_value) | Q(
                id__in=LrNumber.objects.filter(
                    lr_number__icontains=search_value).values_list('booking__id', flat=True)))).exclude(
            exclude_kwargs).order_by('-id', '-shipment_date')
    data = []
    user_group = request.user.groups.values_list('name', flat=True)[0]
    if EMP_GROUP2 == user_group or EMP_GROUP3 == user_group:
        bookings = bookings.exclude(billing_type='contract')
    for booking in bookings[:rows]:
        data.append({
            'id': booking.id,
            'text': '{}( {} )'.format(booking.booking_id, ', '.join(
                booking.lr_numbers.values_list(
                    'lr_number', flat=True))) if booking.lr_numbers.exists() else booking.booking_id
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


@authenticated_user
def get_singlecustomer_bookingdata(request):
    try:
        bookingid = request.GET.get('booking_id')
        to_be_billed_id = request.GET.get('customer_to_be_billed')
        bookings = ManualBooking.objects.filter(id=bookingid).exclude(party_rate=0).exclude(charged_weight=0). \
            exclude(booking_status='cancelled').exclude(deleted=True).order_by('shipment_date')
    except ValueError:
        return JsonResponse({'status': 'failure', 'message': 'Pls check booking id'})

    blank_to_be_billed = False
    no_bookings = False
    if not bookings:
        no_bookings = True
    else:
        for booking in bookings:
            if not booking.customer_to_be_billed_to:
                blank_to_be_billed = True
                break
    invoice_data = get_invoice_data(bookings, 'full')
    return_data = {'status': 'success', 'booking_data': invoice_data,
                   'blank_to_be_billed': blank_to_be_billed, 'no_bookings': no_bookings}
    return JsonResponse(return_data)


# @authenticated_user
def full_booking_invoice_page(request):
    customer = get_or_none(Sme, id=request.GET.get('customer_to_be_billed'))
    bookings = ManualBooking.objects.filter(customer_to_be_billed_to=customer.id).exclude(party_rate=0). \
        exclude(charged_weight=0).exclude(booking_status='cancelled').exclude(deleted=True).order_by('shipment_date')
    user_group = EMP_GROUP1
    if EMP_GROUP2 == user_group or EMP_GROUP3 == user_group:
        bookings = bookings.exclude(billing_type='contract')
    message = None
    message_next_page_dict = {}
    list_of_ids = []
    for booking in bookings:
        if not check_invoice_status(booking):
            list_of_ids.append(booking.id)

    bookings = ManualBooking.objects.filter(id__in=list_of_ids).order_by('shipment_date')
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

    # if message:
    #     messages.error(request,
    #                    message=message)
    #     return render(request=request, template_name='team/invoices/fetch_full_booking_invoice_data.html',
    #                   context=full_booking_invoice_fetch_data())

    return render(request, 'team/invoices/full_booking_invoices.html',
                  {'booking_data': invoice_data, 'customer': customer,
                   'gst_liability': gst_liability,
                   'booking_ids': booking_ids,
                   'comment_list': comment_list,
                   'invoice_amount_data': invoice_amount_data,
                   'message_next_page_dict': message_next_page_dict,
                   'error_message': message})


# @authenticated_user
def invoice_multiple_full_booking_post(request):
    bookings = ManualBooking.objects.filter(id__in=request.POST.get('booking_ids').split(','))
    summary_required = True if request.POST.get('invoice_summary') == 'on' and bookings.count() > 2 else False
    combined_invoice = True if request.POST.get('combined_invoice') == 'on' else False

    try:
        unique_booking_ids = request.POST.get('booking_ids').split(',')
        customer_to_be_billed_to = request.POST.get('to_be_billed_to')
        for id in unique_booking_ids:
            update_data = {'booking_id': id, 'to_be_billed_to': customer_to_be_billed_to}
            views_booking.update_booking_field(update_data)

        # bookings = ManualBooking.objects.filter(booking_id__in=request.POST.get('booking_ids').split(','))
        invoice_summary = invoice.make_invoice(bookings, booking_type='full', form_data=request.POST,
                                               created_by=request.user, summary_required=summary_required,
                                               combined_invoice=combined_invoice)
        data = []
        if combined_invoice:
            booking = bookings.last()
            inv = Invoice.objects.filter(bookings=booking).last()
            if isinstance(inv, Invoice) and inv.s3_upload:
                data.append({
                    's3_url': inv.s3_upload.public_url(),
                    'filename': inv.s3_upload.filename
                })
                return render(request=request, template_name='team/invoices/download-generated-invoice-pdf.html',
                              context={'download_invoice': False, 'data': data})

        zip_filename = "invoices.zip"
        zip_bytes_io = io.BytesIO()
        zf = zipfile.ZipFile(zip_bytes_io, "w")

        for booking in bookings:
            if Invoice.objects.filter(bookings=booking).exclude(deleted=True).exists():
                inv = Invoice.objects.filter(bookings=booking).exclude(deleted=True).last()
                if isinstance(inv, Invoice) and inv.s3_upload:
                    data.append({
                        's3_url': inv.s3_upload.public_url(),
                        'filename': inv.s3_upload.filename
                    })
                    file_response = requests.get(inv.s3_upload.public_url())
                    zf.writestr(inv.s3_upload.filename, file_response.content)
        if isinstance(invoice_summary, InvoiceSummary) and invoice_summary.s3_upload:
            data.append({
                's3_url': invoice_summary.s3_upload.public_url(),
                'filename': invoice_summary.s3_upload.filename
            })
            file_response = requests.get(invoice_summary.s3_upload.public_url())
            zf.writestr(invoice_summary.s3_upload.filename, file_response.content)
        zf.close()
        zip_s3_upload = s3util.save_to_s3_invoice(filename=zip_filename, content=zip_bytes_io.getvalue())
        data.append({
            's3_url': zip_s3_upload.public_url(),
            'filename': 'Download All'
        })
        return render(request=request, template_name='team/invoices/download-generated-invoice-pdf.html',
                      context={'download_invoice': True, 'data': data})
    except invoice.InvoiceError:
        return HttpResponseRedirect('/team/fetch-full-booking-invoice-data-page/')


@only_get
def invoice_multiple_commission_booking_page(request):
    booking_data = ManualBooking.objects.filter(Q(booking_id__istartswith='AB') | Q(
        booking_id__istartswith='BROKER')).exclude(booking_status='cancelled')
    return render(request, 'team/invoices/commission_booking_invoice.html',
                  {'template': 'fetch_data', 'booking_data': booking_data})


@only_post
def invoice_multiple_commission_booking_post(request):
    data_fetch_type = request.POST.get('data_fetch_type')
    booking_ids = request.POST.getlist('booking_id[]')
    if data_fetch_type != 'yes':
        try:
            bookings = ManualBooking.objects.filter(id__in=request.POST.get('booking_ids').split(','))
            invoice.make_invoice(bookings, booking_type='commission', form_data=request.POST, created_by=request.user)
            return HttpResponseRedirect('/team/commission-invoice-data-page/')
        except IndexError:
            return HttpResponse('Error: IndexError')
    else:
        booking_data = ManualBooking.objects.filter(id__in=request.POST.getlist('booking_id[]'))
        inv = Invoice.objects.filter(bookings__id__in=request.POST.getlist('booking_id[]'))
        if inv.exists():
            return HttpResponseRedirect('/team/duplicate-invoice-gen/')
        return render(request, 'team/invoices/commission_booking_invoice.html',
                      {'template': 'gen_invoices', 'booking_data': booking_data,
                       'booking_id': booking_ids})


@authenticated_user
def invoices_data(request):
    start = to_int(request.GET.get('start'))
    end = start + to_int(request.GET.get('length'))
    booking_ids = manual_booking_id_list(username=request.user.username,
                                         user_group_list=request.user.groups.values_list('name', flat=True))
    user_group = request.user.groups.values_list('name', flat=True)[0]
    if user_group == EMP_GROUP2 or user_group == EMP_GROUP3:
        bookings = ManualBooking.objects.filter(id__in=booking_ids).exclude(billing_type='contract').exclude(
            booking_status__iexact='cancelled')
    else:
        bookings = ManualBooking.objects.filter(id__in=booking_ids).exclude(
            booking_status__iexact='cancelled')
    if request.GET.get('search[value]'):
        search_value = request.GET.get('search[value]').strip()
        invoices = Invoice.objects.filter(
            bookings__in=ManualBooking.objects.filter(Q(id__in=booking_ids) & (
                    Q(booking_id__icontains=search_value) | Q(lorry_number__icontains=search_value))))
        if invoices.exists():
            invoices = invoices
        else:
            try:
                search_value = int(search_value)
                search_kwargs = Q(total_amount=search_value)
                invoices = Invoice.objects.filter(
                    bookings__in=bookings).filter(search_kwargs).order_by('-date').distinct()
            except ValueError:
                if LrNumber.objects.filter(lr_number__icontains=search_value).exists():
                    booking_ids = LrNumber.objects.filter(lr_number__icontains=search_value).values_list('booking__id')
                    invoices = Invoice.objects.filter(
                        bookings__in=bookings).order_by('-date').distinct()
                else:
                    search_kwargs = Q(company_name__icontains=search_value) | Q(invoice_number__icontains=search_value)
                    invoices = Invoice.objects.filter(
                        bookings__in=bookings).filter(search_kwargs).order_by('-date').distinct()
    else:
        invoices = Invoice.objects.filter(
            bookings__in=bookings).order_by('-date').distinct()

    data = []
    for inv in invoices[start:end if end != -1 else invoices.count()]:
        data.append([
            inv.date.strftime('%d-%b-%Y') if inv.date else '',
            inv.invoice_number,
            inv.company_name,
            '<br>'.join(inv.bookings.values_list('booking_id', flat=True)),
            '<br>'.join(['<br>'.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in
                         inv.bookings.all()]),
            to_int(inv.total_amount),
            '-' if not inv.s3_upload else format_html(
                '''<a href="{}" download><i class="fa fa-download" aria-hidden="true"></i></a>''',
                inv.s3_upload.public_url())

        ])
    data = {
        "draw": to_int(request.GET.get('draw')),
        "recordsTotal": invoices.count(),
        "recordsFiltered": invoices.count(),
        "data": data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


@authenticated_user
def invoice_list(request):
    return render(request, 'team/invoices/invoice_list.html')


@authenticated_user
def invoices_summary_data(request):
    invoices_summary = InvoiceSummary.objects.exclude(deleted=True).order_by('-id', '-datetime')
    start = to_int(request.GET.get('start'))
    end = start + to_int(request.GET.get('length'))
    if request.GET.get('search[value]'):
        search_value = request.GET.get('search[value]').strip()
        invoices_summary = InvoiceSummary.objects.exclude(deleted=True).filter(
            Q(s3_upload__filename__icontains=search_value)).order_by('-id', '-datetime')
        try:
            search_value = int(search_value)
            invoices_summary = InvoiceSummary.objects.exclude(deleted=True).filter(
                Q(s3_upload__filename__icontains=search_value) | Q(id=search_value)).order_by('-id', '-datetime')
        except ValueError:
            invoices_summary = InvoiceSummary.objects.exclude(deleted=True).filter(
                Q(s3_upload__filename__icontains=search_value)).order_by('-id', '-datetime')
    data = []
    for row in invoices_summary[start:end if end != -1 else invoices_summary.count()]:
        data.append([
            row.datetime.strftime('%d-%b-%Y') if row.datetime else '',
            row.id,
            row.ref_number,
            '<br>'.join(row.booking.values_list('booking_id', flat=True)),
            '<br>'.join(['<br>'.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in
                         row.booking.all()]),
            format_html('''<a href="{}" download><i class="fa fa-download" aria-hidden="true"></i></a>''',
                        row.s3_upload.public_url() if row.s3_upload else ''),
            row.s3_upload.filename if row.s3_upload else ''
        ])
    data = {
        "draw": to_int(request.GET.get('draw')),
        "recordsTotal": invoices_summary.count(),
        "recordsFiltered": invoices_summary.count(),
        "data": data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


@authenticated_user
def invoice_summary_list(request):
    return render(request=request, template_name='team/invoices/invoice_summary_statement.html')


@authenticated_user
def invoice_number_data(request):
    rows = to_int(request.GET.get('page'))
    invoices = Invoice.objects.exclude(Q(deleted=True))

    search_value = request.GET.get('search')
    if search_value:
        invoices = Invoice.objects.filter(invoice_number__icontains=search_value).exclude(deleted=True)
    data = []
    for invoice in invoices[:rows]:
        data.append({
            'id': invoice.id,
            'text': '{}'.format(invoice.invoice_number)
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
