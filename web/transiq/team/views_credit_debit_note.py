import json
from datetime import datetime

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_exempt

from api.helper import json_success_response, json_400_incorrect_use
from api.utils import to_int, get_or_none
from restapi.helper_api import generate_credit_note_customer_serial_number, generate_credit_note_supplier_serial_number, \
    generate_debit_note_customer_serial_number, generate_debit_note_supplier_serial_number, \
    generate_credit_note_customer_direct_advance_serial_number, \
    generate_debit_note_supplier_direct_advance_serial_number
from restapi.serializers.team import CreditNoteCustomerSerializer, CreditNoteSupplierSerializer, \
    DebitNoteCustomerSerializer, DebitNoteSupplierSerializer, CreditNoteCustomerDirectAdvanceSerializer, \
    DebitNoteSupplierDirectAdvanceSerializer
from team.decorators import authenticated_user
from team.models import CreditDebitNoteReason, CreditNoteCustomer, CreditNoteSupplier, DebitNoteSupplier, \
    DebitNoteCustomer, CreditNoteCustomerDirectAdvance, DebitNoteSupplierDirectAdvance, Invoice


def credit_debit_note_reason_data(request):
    rows = to_int(request.GET.get('page'))
    credit_debit_note_reasons = CreditDebitNoteReason.objects.exclude(Q(deleted=True))

    search_value = request.GET.get('search')
    if search_value:
        credit_debit_note_reasons = CreditDebitNoteReason.objects.filter(name__icontains=search_value).exclude(
            Q(deleted=True))
    data = []
    for credit_debit_note_reason in credit_debit_note_reasons[:rows]:
        data.append({
            'id': credit_debit_note_reason.id,
            'text': '{}'.format(credit_debit_note_reason.name)
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def issue_credit_note_customer_page(request):
    return render(request=request, template_name='team/credit_debit_note/issue/issue_cnc.html')


def issue_credit_note_supplier_page(request):
    return render(request=request, template_name='team/credit_debit_note/issue/issue_cns.html')


def issue_debit_note_customer_page(request):
    return render(request=request, template_name='team/credit_debit_note/issue/issue_dnc.html')


def issue_debit_note_supplier_page(request):
    return render(request=request, template_name='team/credit_debit_note/issue/issue_dns.html')


def issue_credit_note_customer_direct_advance_page(request):
    return render(request=request, template_name='team/credit_debit_note/issue/issue_cnca.html')


def issue_debit_note_supplier_direct_advance_page(request):
    return render(request=request, template_name='team/credit_debit_note/issue/issue_dnsa.html')


@csrf_exempt
@authenticated_user
def create_issue_credit_note_customer(request):
    data = json.loads(request.body.decode('utf-8'))
    credit_note_customer_serializer = CreditNoteCustomerSerializer(data=data)
    # data["credit_note_number"] = generate_credit_note_customer_serial_number(data['customer'])
    if credit_note_customer_serializer.is_valid():
        credit_note_customer_serializer.save()
        return json_success_response(
            msg='Credit Note ID {} is generated'.format(credit_note_customer_serializer.data['credit_note_number']))
    return json_400_incorrect_use()


@csrf_exempt
@authenticated_user
def create_issue_credit_note_supplier(request):
    data = json.loads(request.body.decode('utf-8'))
    data["changed_by"] = request.user.username
    data["created_by"] = request.user.username
    data["credit_note_number"] = generate_credit_note_supplier_serial_number(data['broker'])
    credit_note_supplier_serializer = CreditNoteSupplierSerializer(data=data)

    if credit_note_supplier_serializer.is_valid():
        credit_note_supplier_serializer.save()
        return json_success_response(
            msg='Credit Note ID {} is generated'.format(credit_note_supplier_serializer.data['credit_note_number']))
    return json_400_incorrect_use()


@csrf_exempt
@authenticated_user
def create_issue_debit_note_customer(request):
    data = json.loads(request.body.decode('utf-8'))
    data["changed_by"] = request.user.username
    data["created_by"] = request.user.username
    data["debit_note_number"] = generate_debit_note_customer_serial_number(data['customer'])
    debit_note_customer_serializer = DebitNoteCustomerSerializer(data=data)
    if debit_note_customer_serializer.is_valid():
        debit_note_customer_serializer.save()
        return json_success_response(
            msg='Debit Note ID {} is generated'.format(debit_note_customer_serializer.data['debit_note_number']))
    return json_400_incorrect_use()


@csrf_exempt
@authenticated_user
def create_issue_debit_note_supplier(request):
    data = json.loads(request.body.decode('utf-8'))

    data["changed_by"] = request.user.username
    data["created_by"] = request.user.username
    data["debit_note_number"] = generate_debit_note_supplier_serial_number(data['broker'])
    debit_note_supplier_serializer = DebitNoteSupplierSerializer(data=data)
    if debit_note_supplier_serializer.is_valid():
        debit_note_supplier_serializer.save()
        return json_success_response(
            msg='Debit Note ID {} is generated'.format(debit_note_supplier_serializer.data['debit_note_number']))
    return json_400_incorrect_use()


@csrf_exempt
@authenticated_user
def create_issue_credit_note_customer_direct_advance(request):
    data = json.loads(request.body.decode('utf-8'))
    data["changed_by"] = request.user.username
    data["created_by"] = request.user.username
    data["credit_note_number"] = generate_credit_note_customer_direct_advance_serial_number(data['customer'])
    credit_note_customer_serializer = CreditNoteCustomerDirectAdvanceSerializer(data=data)
    if credit_note_customer_serializer.is_valid():
        credit_note_customer_serializer.save()
        return json_success_response(
            msg='Credit Note ID {} is generated'.format(credit_note_customer_serializer.data['credit_note_number']))
    return json_400_incorrect_use()


@csrf_exempt
@authenticated_user
def create_issue_debit_note_supplier_direct_advance(request):
    data = json.loads(request.body.decode('utf-8'))
    data["changed_by"] = request.user.username
    data["created_by"] = request.user.username
    data["debit_note_number"] = generate_debit_note_supplier_direct_advance_serial_number(data['broker'])
    debit_note_supplier_serializer = DebitNoteSupplierDirectAdvanceSerializer(data=data)
    if debit_note_supplier_serializer.is_valid():
        debit_note_supplier_serializer.save()
        return json_success_response(
            msg='Debit Note ID {} is generated'.format(debit_note_supplier_serializer.data['debit_note_number']))
    return json_400_incorrect_use()


def approve_credit_note_customer_data():
    data = []
    for row in CreditNoteCustomer.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_cnc_form': 'approve_cnc_form_{}'.format(row.id),
            'approve_cnc_btn': 'approve_cnc_btn_{}'.format(row.id),
            'reject_cnc_btn': 'reject_cnc_btn_{}'.format(row.id),
            'input_reject_cnc_remarks': 'input_reject_cnc_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return data


@csrf_exempt
@authenticated_user
def update_credit_note_customer(request, pk):
    data = json.loads(request.body.decode('utf-8'))
    data["changed_by"] = request.user.username
    credit_note_customer = get_or_none(CreditNoteCustomer, id=pk)
    if not isinstance(credit_note_customer, CreditNoteCustomer):
        return json_400_incorrect_use()
    if data['status'] == 'approved' and credit_note_customer.bookings.count() == 1:
        data['adjusted_amount'] = credit_note_customer.credit_amount
        data['status'] = 'adjusted'
        data['adjusted_by'] = request.user.username
        data['adjusted_on'] = datetime.now()
        if Invoice.objects.filter(bookings__in=credit_note_customer.bookings.all()).exists():
            data['invoice'] = Invoice.objects.filter(bookings__in=credit_note_customer.bookings.all()).last().id
    credit_note_customer_serializer = CreditNoteCustomerSerializer(
        instance=credit_note_customer,
        data=data,
        partial=True
    )
    if credit_note_customer_serializer.is_valid():
        credit_note_customer_serializer.save()
        return json_success_response(msg='success')
    return json_400_incorrect_use()


def approve_credit_note_customer_page(request):
    data = []
    for row in CreditNoteCustomer.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_cnc_form': 'approve_cnc_form_{}'.format(row.id),
            'approve_cnc_btn': 'approve_cnc_btn_{}'.format(row.id),
            'reject_cnc_btn': 'reject_cnc_btn_{}'.format(row.id),
            'input_reject_cnc_remarks': 'input_reject_cnc_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/approve/cnc.html',
                  context={'data': data})


def approve_debit_note_customer_data():
    data = []
    for row in DebitNoteCustomer.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'dnc_id': row.id,
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.debit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'debit_note_number': row.debit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'debit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_dnc_form': 'approve_dnc_form_{}'.format(row.id),
            'approve_dnc_btn': 'approve_dnc_btn_{}'.format(row.id),
            'reject_dnc_btn': 'reject_dnc_btn_{}'.format(row.id),
            'input_reject_dnc_remarks': 'input_reject_dnc_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return data


@csrf_exempt
@authenticated_user
def update_debit_note_customer(request, pk):
    data = json.loads(request.body.decode('utf-8'))
    data["changed_by"] = request.user.username
    debit_note_customer = get_or_none(DebitNoteCustomer, id=pk)
    if not isinstance(debit_note_customer, DebitNoteCustomer):
        return json_400_incorrect_use()
    if data['status'] == 'approved' and debit_note_customer.bookings.count() == 1:
        data['adjusted_amount'] = debit_note_customer.debit_amount
        data['status'] = 'adjusted'
        data['adjusted_by'] = request.user.username
        data['adjusted_on'] = datetime.now()
        if Invoice.objects.filter(bookings__in=debit_note_customer.bookings.all()).exists():
            data['invoice'] = Invoice.objects.filter(bookings__in=debit_note_customer.bookings.all()).last().id
    debit_note_customer_serializer = DebitNoteCustomerSerializer(
        instance=debit_note_customer,
        data=data,
        partial=True
    )
    if debit_note_customer_serializer.is_valid():
        debit_note_customer_serializer.save()
        return json_success_response(msg='success')
    return json_400_incorrect_use()


def approve_debit_note_customer_page(request):
    data = []
    for row in DebitNoteCustomer.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'dnc_id': row.id,
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.debit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'debit_note_number': row.debit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'debit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_dnc_form': 'approve_dnc_form_{}'.format(row.id),
            'approve_dnc_btn': 'approve_dnc_btn_{}'.format(row.id),
            'reject_dnc_btn': 'reject_dnc_btn_{}'.format(row.id),
            'input_reject_dnc_remarks': 'input_reject_dnc_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/approve/dnc.html',
                  context={'data': data})


def approve_credit_note_supplier_data():
    data = []
    for row in CreditNoteSupplier.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'broker': row.broker.get_name() if row.broker else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_cns_form': 'approve_cns_form_{}'.format(row.id),
            'approve_cns_btn': 'approve_cns_btn_{}'.format(row.id),
            'reject_cns_btn': 'reject_cns_btn_{}'.format(row.id),
            'input_reject_cns_remarks': 'input_reject_cns_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return data


@csrf_exempt
@authenticated_user
def update_issue_credit_note_supplier(request, pk):
    data = json.loads(request.body.decode('utf-8'))
    data["changed_by"] = request.user.username
    credit_note_supplier = get_or_none(CreditNoteSupplier, id=pk)
    if not isinstance(credit_note_supplier, CreditNoteSupplier):
        return json_400_incorrect_use()
    if data['status'] == 'approved' and credit_note_supplier.bookings.count() == 1:
        data['adjusted_amount'] = credit_note_supplier.credit_amount
        data['status'] = 'adjusted'
        data['adjusted_by'] = request.user.username
        data['adjusted_on'] = datetime.now()
        if Invoice.objects.filter(bookings__in=credit_note_supplier.bookings.all()).exists():
            data['invoice'] = Invoice.objects.filter(bookings__in=credit_note_supplier.bookings.all()).last().id
    credit_note_supplier_serializer = CreditNoteSupplierSerializer(
        instance=credit_note_supplier,
        data=data,
        partial=True
    )
    if credit_note_supplier_serializer.is_valid():
        credit_note_supplier_serializer.save()
        return json_success_response(msg='success')
    return json_400_incorrect_use()


def approve_issue_credit_note_supplier_page(request):
    data = []
    for row in CreditNoteSupplier.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'broker': row.broker.get_name() if row.broker else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_cns_form': 'approve_cns_form_{}'.format(row.id),
            'approve_cns_btn': 'approve_cns_btn_{}'.format(row.id),
            'reject_cns_btn': 'reject_cns_btn_{}'.format(row.id),
            'input_reject_cns_remarks': 'input_reject_cns_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/approve/cns.html',
                  context={'data': data})


def approve_debit_note_supplier_data():
    data = []
    for row in DebitNoteSupplier.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'broker': row.broker.get_name() if row.broker else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.debit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.debit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_dns_form': 'approve_dns_form_{}'.format(row.id),
            'approve_dns_btn': 'approve_dns_btn_{}'.format(row.id),
            'reject_dns_btn': 'reject_dns_btn_{}'.format(row.id),
            'input_reject_dns_remarks': 'input_reject_dns_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return data


@csrf_exempt
@authenticated_user
def update_debit_note_supplier(request, pk):
    data = json.loads(request.body.decode('utf-8'))
    data["changed_by"] = request.user.username
    debit_note_supplier = get_or_none(DebitNoteSupplier, id=pk)
    if not isinstance(debit_note_supplier, DebitNoteSupplier):
        return json_400_incorrect_use()
    if data['status'] == 'approved' and debit_note_supplier.bookings.count() == 1:
        data['adjusted_amount'] = debit_note_supplier.debit_amount
        data['status'] = 'adjusted'
        data['adjusted_by'] = request.user.username
        data['adjusted_on'] = datetime.now()
        if Invoice.objects.filter(bookings__in=debit_note_supplier.bookings.all()).exists():
            data['invoice'] = Invoice.objects.filter(bookings__in=debit_note_supplier.bookings.all()).last().id
    debit_note_supplier_serializer = DebitNoteSupplierSerializer(
        instance=debit_note_supplier,
        data=data,
        partial=True
    )
    if debit_note_supplier_serializer.is_valid():
        debit_note_supplier_serializer.save()
        return json_success_response(msg='success')
    return json_400_incorrect_use()


def approve_debit_note_supplier_page(request):
    data = []
    for row in DebitNoteSupplier.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'broker': row.broker.get_name() if row.broker else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.debit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.debit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_dns_form': 'approve_dns_form_{}'.format(row.id),
            'approve_dns_btn': 'approve_dns_btn_{}'.format(row.id),
            'reject_dns_btn': 'reject_dns_btn_{}'.format(row.id),
            'input_reject_dns_remarks': 'input_reject_dns_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/approve/dns.html',
                  context={'data': data})


def approve_debit_note_supplier_direct_advance_data():
    data = []
    for row in DebitNoteSupplierDirectAdvance.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'broker': row.broker.get_name() if row.broker else '-',
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.debit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.debit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_dnsa_form': 'approve_dnsa_form_{}'.format(row.id),
            'approve_dnsa_btn': 'approve_dnsa_btn_{}'.format(row.id),
            'reject_dnsa_btn': 'reject_dnsa_btn_{}'.format(row.id),
            'input_reject_dnsa_remarks': 'input_reject_dnsa_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return data


@csrf_exempt
@authenticated_user
def update_debit_note_supplier_direct_advance(request, pk):
    data = json.loads(request.body.decode('utf-8'))
    data["changed_by"] = request.user.username
    debit_note_supplier = get_or_none(DebitNoteSupplierDirectAdvance, id=pk)
    if not isinstance(debit_note_supplier, DebitNoteSupplierDirectAdvance):
        return json_400_incorrect_use()
    if data['status'] == 'approved' and debit_note_supplier.bookings.count() == 1:
        data['adjusted_amount'] = debit_note_supplier.debit_amount
        data['status'] = 'adjusted'
        data['adjusted_by'] = request.user.username
        data['adjusted_on'] = datetime.now()
        if Invoice.objects.filter(bookings__in=debit_note_supplier.bookings.all()).exists():
            data['invoice'] = Invoice.objects.filter(bookings__in=debit_note_supplier.bookings.all()).last().id
    debit_note_supplier_serializer = DebitNoteSupplierDirectAdvanceSerializer(
        instance=debit_note_supplier,
        data=data,
        partial=True
    )
    if debit_note_supplier_serializer.is_valid():
        debit_note_supplier_serializer.save()
        return json_success_response(msg='success')
    return json_400_incorrect_use()


def approve_debit_note_supplier_direct_advance_page(request):
    data = []
    for row in DebitNoteSupplierDirectAdvance.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'broker': row.broker.get_name() if row.broker else '-',
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.debit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.debit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_dnsa_form': 'approve_dnsa_form_{}'.format(row.id),
            'approve_dnsa_btn': 'approve_dnsa_btn_{}'.format(row.id),
            'reject_dnsa_btn': 'reject_dnsa_btn_{}'.format(row.id),
            'input_reject_dnsa_remarks': 'input_reject_dnsa_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/approve/dnsa.html',
                  context={'data': data})


def approve_credit_note_customer_direct_advance_data():
    data = []
    for row in CreditNoteCustomerDirectAdvance.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'broker': row.broker.get_name() if row.broker else '-',
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_cnca_form': 'approve_cnca_form_{}'.format(row.id),
            'approve_cnca_btn': 'approve_cnca_btn_{}'.format(row.id),
            'reject_cnca_btn': 'reject_cnca_btn_{}'.format(row.id),
            'input_reject_cnca_remarks': 'input_reject_cnca_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return data


@csrf_exempt
@authenticated_user
def update_credit_note_customer_direct_advance(request, pk):
    data = json.loads(request.body.decode('utf-8'))
    data["changed_by"] = request.user.username
    credit_note_customer_direct_advance = get_or_none(CreditNoteCustomerDirectAdvance, id=pk)
    if not isinstance(credit_note_customer_direct_advance, CreditNoteCustomerDirectAdvance):
        return json_400_incorrect_use()
    if data['status'] == 'approved' and credit_note_customer_direct_advance.bookings.count() == 1:
        data['adjusted_amount'] = credit_note_customer_direct_advance.credit_amount
        data['status'] = 'adjusted'
        data['adjusted_by'] = request.user.username
        data['adjusted_on'] = datetime.now()
        if Invoice.objects.filter(bookings__in=credit_note_customer_direct_advance.bookings.all()).exists():
            data['invoice'] = Invoice.objects.filter(
                bookings__in=credit_note_customer_direct_advance.bookings.all()).last().id
    credit_note_customer_direct_advance_serializer = CreditNoteCustomerDirectAdvanceSerializer(
        instance=credit_note_customer_direct_advance,
        data=data,
        partial=True
    )
    if credit_note_customer_direct_advance_serializer.is_valid():
        credit_note_customer_direct_advance_serializer.save()
        return json_success_response(msg='success')
    return json_400_incorrect_use()


def approve_credit_note_customer_direct_advance_page(request):
    data = []
    for row in CreditNoteCustomerDirectAdvance.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'broker': row.broker.get_name() if row.broker else '-',
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': '\n'.join(
                [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id, booking.booking_id)
                 for booking in row.bookings.all()]),
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_cnca_form': 'approve_cnca_form_{}'.format(row.id),
            'approve_cnca_btn': 'approve_cnca_btn_{}'.format(row.id),
            'reject_cnca_btn': 'reject_cnca_btn_{}'.format(row.id),
            'input_reject_cnca_remarks': 'input_reject_cnca_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
            'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/approve/cnca.html',
                  context={'data': data})


def approve_credit_debit_note_page(request):
    data = {
        'cnc': approve_credit_note_customer_data(),
        'dnc': approve_debit_note_customer_data(),
        'cns': approve_credit_note_supplier_data(),
        'dns': approve_debit_note_supplier_data(),
        'cnca': approve_credit_note_customer_direct_advance_data(),
    }
    return render(request=request, template_name='team/credit_debit_note/approve/approve_credit_debit_note_page.html',
                  context=data)


def issue_credit_debit_note_page(request):
    return render(request=request, template_name='team/credit_debit_note/issue/issue-credit-debit-note.html')


def adjust_credit_debit_note_page(request):
    return render(request=request, template_name='team/credit_debit_note/adjust/credit-debit-note.html')


def adjust_credit_note_customer_page(request):
    data = []
    for row in CreditNoteCustomer.objects.filter(Q(status='approved') | Q(status='partial')).order_by('approved_on'):
        data.append({
            'cnc_id': row.id,
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': [{'id': booking.id, "booking_id": booking.booking_id} for booking in row.bookings.all()],
            'invoice': {'id': row.invoice.id, 'invoice_number': row.invoice.invoice_number} if row.invoice else {},
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'approved_on': row.approved_on.strftime('%d-%b-%Y') if row.approved_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'approved_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'form_adjust_cnc': 'form_adjust_cnc_{}'.format(row.id),
            'btn_adjust_cnc': 'btn_adjust_cnc_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/adjust/cnc.html', context={'data': data})


def adjust_credit_note_customer_direct_advance_page(request):
    data = []
    for row in CreditNoteCustomerDirectAdvance.objects.filter(Q(status='approved') | Q(status='partial')).order_by(
            'approved_on'):
        data.append({
            'cnca_id': row.id,
            'customer': row.customer.get_name() if row.customer else '-',
            'broker': row.broker.get_name() if row.broker else '-',
            'bookings': [{'id': booking.id, "booking_id": booking.booking_id} for booking in row.bookings.all()],
            'invoice': {'id': row.invoice.id, 'invoice_number': row.invoice.invoice_number} if row.invoice else {},
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'approved_on': row.approved_on.strftime('%d-%b-%Y') if row.approved_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'approved_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'form_adjust_cnca': 'form_adjust_cnca_{}'.format(row.id),
            'btn_adjust_cnca': 'btn_adjust_cnca_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/adjust/cnca.html', context={'data': data})


def adjust_debit_note_supplier_direct_advance_page(request):
    data = []
    for row in DebitNoteSupplierDirectAdvance.objects.filter(Q(status='approved') | Q(status='partial')).order_by(
            'approved_on'):
        data.append({
            'dnsa_id': row.id,
            'customer': row.customer.get_name() if row.customer else '-',
            'broker': row.broker.get_name() if row.broker else '-',
            'bookings': [{'id': booking.id, "booking_id": booking.booking_id} for booking in row.bookings.all()],
            'invoice': {'id': row.invoice.id, 'invoice_number': row.invoice.invoice_number} if row.invoice else {},
            'amount': row.debit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'approved_on': row.approved_on.strftime('%d-%b-%Y') if row.approved_on else '-',
            'debit_note_number': row.debit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'approved_by': row.created_by.username if row.created_by else '-',
            'debit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'form_adjust_dnsa': 'form_adjust_dnsa_{}'.format(row.id),
            'btn_adjust_dnsa': 'btn_adjust_dnsa_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/adjust/dnsa.html', context={'data': data})


def adjust_credit_note_supplier_page(request):
    data = []
    for row in CreditNoteSupplier.objects.filter(Q(status='approved') | Q(status='partial')).order_by('approved_on'):
        data.append({
            'cns_id': row.id,
            'broker': row.broker.get_name() if row.broker else '-',
            'bookings': [{'id': booking.id, "booking_id": booking.booking_id} for booking in row.bookings.all()],
            'invoice': {'id': row.invoice.id, 'invoice_number': row.invoice.invoice_number} if row.invoice else {},
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'approved_on': row.approved_on.strftime('%d-%b-%Y') if row.approved_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'approved_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'form_adjust_cns': 'form_adjust_cns_{}'.format(row.id),
            'btn_adjust_cns': 'btn_adjust_cns_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/adjust/cns.html', context={'data': data})


def adjust_debit_note_supplier_page(request):
    data = []
    for row in DebitNoteSupplier.objects.filter(Q(status='approved') | Q(status='partial')).order_by('approved_on'):
        data.append({
            'dns_id': row.id,
            'broker': row.broker.get_name() if row.broker else '-',
            'bookings': [{'id': booking.id, "booking_id": booking.booking_id} for booking in row.bookings.all()],
            'invoice': {'id': row.invoice.id, 'invoice_number': row.invoice.invoice_number} if row.invoice else {},
            'amount': row.debit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'approved_on': row.approved_on.strftime('%d-%b-%Y') if row.approved_on else '-',
            'debit_note_number': row.debit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'approved_by': row.created_by.username if row.created_by else '-',
            'debit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'form_adjust_dns': 'form_adjust_dns_{}'.format(row.id),
            'btn_adjust_dns': 'btn_adjust_dns_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/adjust/dns.html', context={'data': data})


def adjust_debit_note_customer_page(request):
    data = []
    for row in DebitNoteCustomer.objects.filter(Q(status='approved') | Q(status='partial')).order_by('approved_on'):
        data.append({
            'dnc_id': row.id,
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': [{'id': booking.id, "booking_id": booking.booking_id} for booking in row.bookings.all()],
            'invoice': {'id': row.invoice.id, 'invoice_number': row.invoice.invoice_number} if row.invoice else {},
            'amount': row.debit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'approved_on': row.approved_on.strftime('%d-%b-%Y') if row.approved_on else '-',
            'debit_note_number': row.debit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'approved_by': row.created_by.username if row.created_by else '-',
            'debit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'form_adjust_dnc': 'form_adjust_dnc_{}'.format(row.id),
            'btn_adjust_dnc': 'btn_adjust_dnc_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
        })
    return render(request=request, template_name='team/credit_debit_note/adjust/dnc.html', context={'data': data})


def credit_debit_note_archive(request):
    return render(request=request,template_name='')