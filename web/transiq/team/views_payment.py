import json
from datetime import datetime

import pandas as pd
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.html import format_html
from django.utils.text import slugify

from api.decorators import authenticated_user, api_get
from api.helper import json_success_response, json_error_response, EMP_GROUP2, EMP_GROUP3
from api.models import S3Upload
from api.s3util import save_to_s3_bulk_inward_payments
from api.utils import get_or_none, to_str
from broker.models import Broker
from fileupload.models import ChequeFile
from owner.models import FuelCard
from restapi.helper_api import check_booking_status, create_new_booking_status, update_booking_status
from sme.models import Sme
from team.decorators import only_post
from team.models import PendingInwardPaymentEntry, Invoice, LrNumber, CreditNoteCustomer, DebitNoteCustomer, \
    CreditNoteCustomerDirectAdvance, DebitNoteSupplierDirectAdvance, DebitNoteSupplier, \
    PendingInwardPaymentCreditDebitNoteCustomer
from team.services import full_booking, commission_booking
from team.services import payments
from team.services.create_new_tables import outward_payment, inward_payment
from team.helper.helper import manual_booking_id_list, to_int, django_date_format, to_float, payment_mode_date
from django.conf import settings
from utils.models import Bank
from .models import ManualBooking, InWardPayment
from .models import OutWardPayment


@authenticated_user
def in_ward_payments(request):
    if request.method == 'POST':
        inward_payment(receive_from=request.POST.get('received_from'), amount=request.POST.get('actual_amount'),
                       payment_mode=request.POST.get('payment_mode'),
                       tds_amount=request.POST.get('inward_tds_amount', None),
                       date=request.POST.get('inward_payment_date'), trn=request.POST.get('trn'),
                       invoice_number=request.POST.get('invoice_number'), remarks=request.POST.get('remarks'),
                       booking_id_list=request.POST.getlist('booking_id[]'), username=request.user.username)
    booking_ids = manual_booking_id_list(username=request.user.username,
                                         user_group_list=request.user.groups.values_list('name', flat=True))
    booking_data = ManualBooking.objects.filter(id__in=booking_ids)
    return render(request, 'team/payments/add_inward_payment.html', {'booking_data': booking_data})


@authenticated_user
def inward_payments_edit_booking(request):
    payment = inward_payment(
        receive_from=request.POST.get('received_from'), amount=request.POST.get('actual_amount'),
        payment_mode=request.POST.get('inward_payment_mode'),
        date=request.POST.get('inward_payment_date'),
        invoice_number=request.POST.get('invoice_number'), remarks=request.POST.get('remarks'),
        trn=request.POST.get('trn'),
        tds_amount=request.POST.get('inward_tds_amount', None),
        booking_id_list=[request.POST.get('booking_id')],
        username=request.user.username
    )
    booking = get_or_none(ManualBooking, id=request.POST.get('booking_id'))
    if isinstance(booking, ManualBooking):
        pi = PendingInwardPaymentEntry.objects.create(
            customer=booking.customer_to_be_billed_to,
            customer_name=booking.customer_to_be_billed_to.get_name() if isinstance(
                booking.customer_to_be_billed_to, Sme) else None,
            payment_date=django_date_format(request.POST.get('inward_payment_date')),
            payment_mode=request.POST.get('inward_payment_mode'),
            amount=to_int(request.POST.get('actual_amount')),
            tds=to_int(request.POST.get('inward_tds_amount')),
            adjusted_flag=True,
            adjusted_datetime=datetime.now(),
            adjusted_by=request.user,
            credited_flag=True,
            uploaded_datetime=datetime.now(),
            uploaded_by=request.user,
            trn=request.POST.get('trn')
        )
        pi.inward_payment.add(payment)
        pi.bookings.add(booking)
    full_booking.save_existing_manual_booking_data(request, booking_id=request.POST.get('booking_id'))
    return HttpResponse('Success')


@authenticated_user
def inward_payments_commission_edit_booking(request):
    payment = inward_payment(
        receive_from=request.POST.get('received_from'), amount=request.POST.get('actual_amount'),
        payment_mode=request.POST.get('inward_payment_mode'),
        date=request.POST.get('inward_payment_date'),
        trn=request.POST.get('trn'),
        tds_amount=request.POST.get('inward_tds_amount', None),
        invoice_number=request.POST.get('invoice_number'), remarks=request.POST.get('remarks'),
        booking_id_list=[request.POST.get('booking_id')],
        username=request.user.username
    )
    booking = get_or_none(ManualBooking, id=request.POST.get('booking_id'))
    if isinstance(booking, ManualBooking):
        pi = PendingInwardPaymentEntry.objects.create(
            customer=booking.customer_to_be_billed_to,
            customer_name=booking.customer_to_be_billed_to.get_name() if isinstance(
                booking.customer_to_be_billed_to, Sme) else None,
            payment_date=django_date_format(request.POST.get('inward_payment_date')),
            payment_mode=request.POST.get('inward_payment_mode'),
            amount=to_int(request.POST.get('actual_amount')),
            tds=to_int(request.POST.get('inward_tds_amount')),
            adjusted_flag=True,
            adjusted_datetime=datetime.now(),
            adjusted_by=request.user,
            credited_flag=True,
            uploaded_datetime=datetime.now(),
            uploaded_by=request.user,
            trn=request.POST.get('trn')
        )
        pi.inward_payment.add(payment)
        pi.bookings.add(booking)
    commission_booking.update_commission_booking(request)
    return HttpResponse('Success')


def test_excess_payment_adjustment():
    amount = 460
    booking = ManualBooking.objects.get(id=8290)
    supplier = Broker.objects.get(id=439)
    for mb in ManualBooking.objects.filter(supplier=supplier, outward_payment_status='excess').exclude(
            booking_status='cancelled').exclude(supplier=None).exclude(id=booking.id):
        if amount >= abs(mb.balance_for_supplier):
            adjusted_amount = mb.outward_amount - mb.total_amount_to_owner
            amount -= mb.outward_amount - mb.total_amount_to_owner
        else:
            adjusted_amount = amount
            amount = 0
        if amount > 0:
            print(adjusted_amount)


def adjust_outward_payment_adjustment_mode(payment_id, username):
    try:
        payment = OutWardPayment.objects.get(id=payment_id)
        booking = payment.booking_id.last()
        if isinstance(booking, ManualBooking):
            supplier = booking.supplier
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
            if ManualBooking.objects.filter(supplier=supplier, outward_payment_status='excess').exclude(
                    booking_status='cancelled').exclude(supplier=None).exists():
                for mb in ManualBooking.objects.filter(supplier=supplier, outward_payment_status='excess').exclude(
                        booking_status='cancelled').exclude(supplier=None).exclude(id=booking.id):
                    if amount >= abs(mb.balance_for_supplier):
                        adjusted_amount = mb.outward_amount - mb.total_amount_to_owner
                        amount -= mb.outward_amount - mb.total_amount_to_owner
                    else:
                        adjusted_amount = amount
                        amount = 0
                    if adjusted_amount > 0:
                        op = outward_payment(
                            paid_to=payment.paid_to,
                            amount=-adjusted_amount,
                            date=datetime.now().date().strftime('%d-%b-%Y'),
                            fuel_card=None,
                            remarks=payment.remarks,
                            booking_id_list=[mb.id],
                            account_id=None,
                            payment_mode='adjustment',
                            is_sms=None,
                            username=username,
                            is_refund_amount=False
                        )
                        payment.adjusted_outward_payments.add(op)
    except OutWardPayment.DoesNotExist:
        pass
    except TypeError:
        pass


@authenticated_user
def outward_payments_edit_booking(request):
    ManualBooking.objects.filter(id=request.POST.get('booking_id')).exclude(
        booking_status__icontains='cancelled').update(
        total_amount_to_owner=to_int(request.POST.get('total_amount_to_owner')))
    if request.POST.get('is_refund_amount') == 'y' or check_total_paid_amount_to_owner(
            [request.POST.get('booking_id')], request.POST.get('actual_amount')):
        payment = outward_payment(
            paid_to=request.POST.get('paid_to'),
            amount=request.POST.get('actual_amount'),
            date=request.POST.get('outward_payment_date'),
            fuel_card=request.POST.get('fuel_card_number'),
            remarks=request.POST.get('remarks'),
            booking_id_list=[request.POST.get('booking_id')],
            account_id=request.POST.get('bank_account_number'),
            payment_mode=request.POST.get('outward_payment_mode'),
            is_sms=request.POST.get('send_sms_supplier'),
            username=request.user.username,
            is_refund_amount=request.POST.get('is_refund_amount')
        )
        if payment.payment_mode == 'adjustment':
            adjust_outward_payment_adjustment_mode(payment_id=payment.id, username=request.user.username)
        full_booking.save_existing_manual_booking_data(request, booking_id=request.POST.get('booking_id'))

        return json_success_response("Success")
    else:
        return json_error_response("ERROR", status=409)


@authenticated_user
@only_post
def outward_payments_commission_edit_booking(request):
    ManualBooking.objects.filter(id=request.POST.get('booking_id')).exclude(
        booking_status__icontains='cancelled').update(
        total_amount_to_owner=to_int(request.POST.get('total_amount_to_owner')))
    if request.POST.get('is_refund_amount') == 'y' or check_total_paid_amount_to_owner(
            [request.POST.get('booking_id')], request.POST.get('actual_amount')):
        payment = outward_payment(
            paid_to=request.POST.get('paid_to'), amount=request.POST.get('actual_amount'),
            date=request.POST.get('outward_payment_date'),
            fuel_card=request.POST.get('fuel_card_number'),
            remarks=request.POST.get('remarks'), booking_id_list=[request.POST.get('booking_id')],
            account_id=request.POST.get('bank_account_number'),
            payment_mode=request.POST.get('outward_payment_mode'),
            is_sms=request.POST.get('send_sms_supplier'),
            username=request.user.username,
            is_refund_amount=request.POST.get('is_refund_amount')
        )
        if payment.payment_mode == 'adjustment':
            adjust_outward_payment_adjustment_mode(payment_id=payment.id, username=request.user.username)
        commission_booking.update_commission_booking(request)
        return HttpResponse("Success")
    else:
        return json_error_response("ERROR", status=409)


def check_total_paid_amount_to_owner(booking_id_list, amount):
    amount = to_int(amount)
    manual_bookings = ManualBooking.objects.filter(id__in=booking_id_list).exclude(
        booking_status__icontains='cancelled')
    if manual_bookings.count() == 1:
        booking = manual_bookings.last()
        return amount <= booking.balance_for_supplier

    return (to_int(sum(
        OutWardPayment.objects.filter(booking_id__in=manual_bookings).exclude(is_refund_amount=True).values_list(
            'actual_amount', flat=True))) + to_int(amount)) <= to_int(
        sum(manual_bookings.values_list('total_amount_to_owner', flat=True)))


@authenticated_user
def error_exceeding_outward_amount(request):
    return render(request=request, template_name='team/payments/error_exceeded_payment.html')


@authenticated_user
@api_get
def outward_payment_page(request):
    booking_ids = manual_booking_id_list(username=request.user.username,
                                         user_group_list=request.user.groups.values_list('name', flat=True))
    booking_data = ManualBooking.objects.filter(id__in=booking_ids).exclude(
        Q(outward_payment_status='excess') | Q(outward_payment_status='complete')).exclude(
        booking_status__icontains='cancelled').order_by('-shipment_date')
    fuel_card = FuelCard.objects.exclude(card_number=None)
    bank_account = Bank.objects.filter(status='active')
    return render(request, 'team/payments/add_outward_payment.html',
                  {'booking_data': booking_data, 'fuel_card': fuel_card, 'bank_account': bank_account})


@authenticated_user
def outward_payments(request):
    if check_total_paid_amount_to_owner(request.POST.getlist('booking_id[]'), request.POST.get('actual_amount')):
        payment = outward_payment(
            paid_to=request.POST.get('paid_to'), amount=request.POST.get('actual_amount'),
            date=request.POST.get('outward_payment_date'),
            fuel_card=request.POST.get('fuel_card_number'),
            remarks=request.POST.get('remarks'),
            booking_id_list=request.POST.getlist('booking_id[]'),
            account_id=request.POST.get('bank_account_number'),
            payment_mode=request.POST.get('outward_payment_mode'),
            is_sms=request.POST.get('send_sms_supplier'),
            username=request.user.username
        )
    else:
        return json_error_response("Amount Exceeded", status=409)
    return json_success_response(msg='Payment successful')


@authenticated_user
def update_in_ward_payment(request):
    inward_payment = InWardPayment.objects.get(id=request.GET.get('payment_id'))
    booking_id = inward_payment.booking_id.last()
    booking_data = ManualBooking.objects.exclude(
        Q(inward_payment_status='full_received') | Q(inward_payment_status='excess'))
    return render(request, 'team/payments/update_inward_payment.html',
                  {'payment_id': inward_payment, 'booking_id': booking_id, 'booking_data': booking_data})


@authenticated_user
def save_updated_in_ward_payment(request):
    payments.update_inward_payment(
        received_from=request.POST.get('received_from'),
        amount=request.POST.get('actual_amount'),
        tds_amount=request.POST.get('inward_tds_amount'),
        payment_mode=request.POST.get('inward_payment_mode'),
        date=request.POST.get('inward_payment_date'),
        invoice_number=request.POST.get('invoice_number'),
        remarks=request.POST.get('remarks'),
        booking_id_list=request.POST.getlist('booking_id[]'),
        payment_id=request.POST.get('payment_id'),
        trn=request.POST.get('trn')
    )
    return HttpResponseRedirect('/team/inward-payment-history/')


@authenticated_user
def update_out_ward_payment(request):
    payment_id = OutWardPayment.objects.get(id=request.GET.get('payment_id'))
    booking_id = request.GET.get('booking_id')
    booking_id = ManualBooking.objects.get(booking_id=booking_id)
    booking_data = ManualBooking.objects.all()
    fuel_card = FuelCard.objects.exclude(card_number=None)
    bank_account = Bank.objects.filter(status='active')
    return render(request, 'team/payments/update_outward_payment.html',
                  {'payment_id': payment_id, 'booking_id': booking_id, 'booking_data': booking_data,
                   'fuel_card': fuel_card, 'bank_account': bank_account})


@authenticated_user
def save_updated_out_ward_payment(request):
    payments.update_outward_payment(
        booking_id_list=request.POST.getlist('booking_id[]'),
        paid_to=request.POST.get('paid_to'),
        amount=request.POST.get('actual_amount'),
        remarks=request.POST.get('remarks'),
        date=request.POST.get('outward_payment_date'),
        fuel_card=request.POST.get('fuel_card_number'),
        payment_mode=request.POST.get('outward_payment_mode'),
        payment_id=request.POST.get('payment_id')
    )
    return HttpResponseRedirect('/team/partial-booking-history/')


def get_pending_inward_id(payment_id):
    payment = InWardPayment.objects.get(id=payment_id)
    if payment.pendinginwardpaymententry_set.exists():
        pending_inward = payment.pendinginwardpaymententry_set.last()
        return pending_inward.id
    return '-'


def inward_payments_data(request):
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
        search_value = request.GET.get('search[value]')
        # implement search on booking
        inward_payments = InWardPayment.objects.filter(
            Q(booking_id__in=bookings.filter(booking_id__icontains=search_value)) | Q(trn__icontains=search_value))
        if inward_payments.exists():
            inward_payments = inward_payments
        else:
            try:
                search_value = int(search_value)
                search_kwargs = Q(id=search_value) | Q(actual_amount=search_value)
                inward_payments = InWardPayment.objects.filter(
                    booking_id__in=bookings).filter(
                    search_kwargs).order_by('-payment_date')
            except ValueError:
                if LrNumber.objects.filter(lr_number__icontains=search_value).exists():
                    booking_ids = LrNumber.objects.filter(lr_number__icontains=search_value).values_list('booking__id')
                    inward_payments = InWardPayment.objects.filter(
                        booking_id__in=bookings).order_by('-payment_date')
                else:
                    search_kwargs = Q(invoice_number__icontains=search_value) | Q(
                        received_from__icontains=search_value) | Q(payment_mode__icontains=search_value) | Q(
                        remarks__icontains=search_value)
                    inward_payments = InWardPayment.objects.filter(
                        booking_id__in=bookings).filter(search_kwargs).order_by('-payment_date')
    else:
        inward_payments = InWardPayment.objects.filter(
            booking_id__in=bookings).order_by('-payment_date')

    data = {
        "draw": to_int(request.GET.get('draw')),
        "recordsTotal": inward_payments.count(),
        "recordsFiltered": inward_payments.count(),
        "data": [[
            payment.payment_date.strftime('%d-%b-%Y' if payment.payment_date else ''),
            get_pending_inward_id(payment.id) if get_pending_inward_id(payment.id) else '-',
            format_html(''' <form action="/team/update-in-ward-payment/" method="GET">
                                  <input type="hidden" name="payment_id" value="{}">
                                  <button class="transaction-button" type="submit">{}</button> </form>''',
                        payment.id, payment.id),
            '\n'.join(payment.booking_id.values_list('booking_id', flat=True)),
            '\n'.join(['<br>'.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in
                       payment.booking_id.exclude(lorry_number=None)]),
            payment.invoice_number,
            payment.received_from,
            to_str(payment.actual_amount),
            to_str(payment.tds),
            payment.get_payment_mode_display(),
            payment.trn,
            payment.remarks
        ] for payment in
            inward_payments.order_by('-payment_date', '-id')[start:end if end != -1 else inward_payments.count()]]
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


@authenticated_user
def inward_payment_history(request):
    return render(request, 'team/payments/inward_payment_history.html')


def outward_payments_data(request):
    start = to_int(request.GET.get('start'))
    end = start + to_int(request.GET.get('length'))
    booking_ids = manual_booking_id_list(username=request.user.username,
                                         user_group_list=request.user.groups.values_list('name', flat=True))
    if request.GET.get('search[value]'):
        search_value = request.GET.get('search[value]')
        # implement search on booking
        outward_payments = OutWardPayment.objects.filter(
            Q(booking_id__in=ManualBooking.objects.filter(Q(id__in=booking_ids) & (
                    Q(booking_id__icontains=search_value) | Q(lorry_number__icontains=search_value))).exclude(
                booking_status='cancelled')) | Q(
                status__istartswith=search_value))
        if outward_payments.exists():
            outward_payments = outward_payments
        else:
            try:
                search_value = int(search_value)
                search_kwargs = Q(id=search_value) | Q(actual_amount=search_value) | Q(
                    bank_account__account_number__icontains=search_value) | Q(fuel_card__card_number=search_value) | Q(
                    status__istartswith=search_value)
                outward_payments = OutWardPayment.objects.filter(
                    booking_id__in=ManualBooking.objects.filter(Q(id__in=booking_ids)).exclude(
                        booking_status='cancelled')).filter(
                    search_kwargs).order_by('-payment_date')
            except ValueError:
                if LrNumber.objects.filter(lr_number__icontains=search_value).exists():
                    booking_ids = LrNumber.objects.filter(lr_number__icontains=search_value).values_list('booking__id')
                    outward_payments = OutWardPayment.objects.filter(
                        booking_id__in=ManualBooking.objects.filter(Q(id__in=booking_ids)).exclude(
                            booking_status='cancelled')).order_by('-payment_date')
                else:
                    search_kwargs = Q(paid_to__icontains=search_value) | Q(payment_mode__icontains=search_value) | Q(
                        remarks__icontains=search_value) | Q(bank_account__account_number__icontains=search_value) | Q(
                        bank_account__account_holder_name__icontains=search_value) | Q(
                        fuel_card__card_number=search_value) | Q(status__istartswith=search_value)
                    outward_payments = OutWardPayment.objects.filter(
                        booking_id__in=ManualBooking.objects.filter(Q(id__in=booking_ids)).exclude(
                            booking_status='cancelled')).filter(
                        search_kwargs).order_by('-payment_date')
    else:
        outward_payments = OutWardPayment.objects.filter(
            booking_id__in=ManualBooking.objects.filter(id__in=booking_ids).exclude(
                booking_status='cancelled')).order_by('-payment_date')
    data = {
        "draw": to_int(request.GET.get('draw')),
        "recordsTotal": outward_payments.count(),
        "recordsFiltered": outward_payments.count(),
        "data": [[
            payment.payment_date.strftime('%d-%b-%Y') if payment.payment_date else '',
            to_str(payment.id),
            '\n'.join(payment.booking_id.values_list('booking_id', flat=True)),
            '\n'.join(['<br>'.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in
                       payment.booking_id.all()]),
            '\n'.join(payment.booking_id.values_list('lorry_number', flat=True)),
            payment.paid_to,
            to_str(payment.actual_amount),
            payment.status,
            'Yes' if payment.is_refund_amount else 'No',
            payment.fuel_card.card_number if payment.fuel_card else '',
            payment.get_payment_mode_display(),
            payment.remarks,
            '%s - %s' % (payment.bank_account.account_holder_name,
                         payment.bank_account.account_number) if payment.bank_account else ''
        ] for payment in outward_payments[start:end if end != -1 else outward_payments.count()]]
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


# @authenticated_user
def outward_payment_history(request):
    return render(request, 'team/payments/outward_payment_history.html')


@authenticated_user
def pending_inward_payment_entry_template(request):
    return render(request=request, template_name='team/payments/add_received_payment.html')


def pending_inward_payment(request):
    sme = get_or_none(Sme, id=request.POST.get('customer'))
    if request.POST.get('payment_mode') == 'cash':
        PendingInwardPaymentEntry.objects.create(
            customer=get_or_none(Sme, id=request.POST.get('customer')),
            customer_name=sme.get_name() if sme else None,
            payment_mode=request.POST.get('payment_mode'),
            amount=request.POST.get('amount'),
            payment_date=django_date_format(request.POST.get('payment_date')),
            trn=request.POST.get('trn'),
            additional_remark=request.POST.get('narration'),
            uploaded_by=request.user,
            uploaded_datetime=datetime.now(),
            created_by=request.user,
            changed_by=request.user
        )
    else:
        if PendingInwardPaymentEntry.objects.filter(trn=request.POST.get('trn'), payment_date=django_date_format(
                request.POST.get('payment_date'))).exists():
            return json_error_response(msg="Already exists", status=409)
        else:
            PendingInwardPaymentEntry.objects.create(
                customer=get_or_none(Sme, id=request.POST.get('customer')),
                customer_name=sme.get_name() if sme else None,
                payment_mode=request.POST.get('payment_mode'),
                amount=request.POST.get('amount'),
                payment_date=django_date_format(request.POST.get('payment_date')),
                trn=request.POST.get('trn'),
                additional_remark=request.POST.get('narration'),
                uploaded_by=request.user,
                uploaded_datetime=datetime.now(),
                created_by=request.user,
                changed_by=request.user,
            )
    return json_success_response('success')


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


@authenticated_user
def pending_payment_list(request):
    return render(
        request=request,
        template_name='team/payments/pending-payment-list.html',
        context={
            'pending_payments': pending_payments_data(),
        }
    )


def uncredited_cheques(request):
    cheques = ChequeFile.objects.filter(resolved=False).order_by('cheque_date').values(
        'cheque_number', 'cheque_date', 'customer_name', 'amount', 'remarks').annotate(Count('cheque_number'))
    data = []
    for cheque in cheques:
        cheque_number = cheque['cheque_number']
        data.append({
            'id': ','.join([str(row.id) for row in ChequeFile.objects.filter(cheque_number=cheque_number)]),
            'cheque_number': cheque_number,
            'cheque_date': cheque['cheque_date'],
            'customer_name': cheque['customer_name'],
            'amount': cheque['amount'],
            'remarks': cheque['remarks'],
            'images': [row.s3_upload.public_url() for row in ChequeFile.objects.filter(cheque_number=cheque_number)]
        })
    return render(
        request=request,
        template_name='team/payments/uncredited-cheques.html',
        context={'cheques': data}
    )


def resolve_cheque(request):
    cheque_ids = request.POST.get('cheque_id').split(',')
    ChequeFile.objects.filter(id__in=cheque_ids).update(
        cheque_number=request.POST.get('cheque_number'),
        customer_name=request.POST.get('customer_name'),
        amount=request.POST.get('amount'),
        remarks=request.POST.get('remarks'),
        resolved=True,
        resolved_by=request.user,
        resolved_datetime=datetime.now()
    )
    return HttpResponseRedirect('/team/uncredited-cheques/')


@authenticated_user
def upload_bulk_credited_payment(request):
    try:
        save_to_s3_bulk_inward_payments(datetime.now().strftime('%Y%m%d%H%M') + '.xlsx',
                                        request.FILES['payment_file'])
    except:
        raise
    try:
        filename = S3Upload.objects.filter(folder__iexact='uploads/creditinward').latest('created_on').public_url()
        df = pd.read_excel(filename)
        df = df.fillna('')
        invalid_format = False
        invalid_format_error = []
        for i, row in df.iterrows():
            try:
                if not isinstance(row['Date'], datetime):
                    datetime.strptime(row['Date'], '%d/%m/%y')
            except ValueError:
                invalid_format = True
                invalid_format_error.append('Date Format Error for TRN: %s, Date: %s, Amount: %s' % (
                    row['ChqUTR No.'], row['Date'], str(row['Amount'])))
            payment_mode = row['Mode']
            if payment_mode and payment_mode.lower() in ['cash', 'neft', 'imps', 'cheque', 'rtgs',
                                                         'hdfc_internal_account']:
                payment_mode.lower()
            else:
                invalid_format = True
                invalid_format_error.append('Payment Mode Format Error for TRN: %s, Date: %s, Amount: %s' % (
                    row['ChqUTR No.'], row['Date'], str(row['Amount'])))
            try:
                float(row['Amount'])
            except ValueError:
                invalid_format = True
                invalid_format_error.append('Amount Format Error for TRN: %s, Date: %s, Amount: %s' % (
                    row['ChqUTR No.'], row['Date'], str(row['Amount'])))
        if invalid_format:
            return render(
                request=request,
                template_name='team/payments/add_received_payment.html',
                context={
                    'duplicate_payments': [],
                    'success_payments': [],
                    'upload_file': True,
                    'invalid_format_error': invalid_format_error
                }
            )
        success_payment_id = []
        duplicate_payment_id = []
        for i, row in df.iterrows():
            payment_date = datetime.strptime(row['Date'], '%d/%m/%y') if not isinstance(row['Date'], datetime) else \
                row['Date']
            if PendingInwardPaymentEntry.objects.filter(
                    trn=row['ChqUTR No.'], payment_date=payment_date).exists():
                for value in PendingInwardPaymentEntry.objects.filter(
                        trn=row['ChqUTR No.'], payment_date=payment_date):
                    duplicate_payment_id.append(value.id)
            else:

                payment_mode = row['Mode']
                if payment_mode and payment_mode.lower() in ['cash', 'neft', 'imps', 'cheque', 'rtgs',
                                                             'hdfc_internal_account']:
                    payment_mode = payment_mode.lower()
                else:
                    payment_mode = None
                pending_payment_entry = PendingInwardPaymentEntry.objects.create(
                    customer_name=row['Party Name'],
                    payment_mode=payment_mode,
                    amount=to_int(row['Amount']),
                    payment_date=payment_date,
                    additional_remark=row['Narration'],
                    trn=row['ChqUTR No.'],
                    uploaded_by=request.user,
                    uploaded_datetime=datetime.now(),
                )
                success_payment_id.append(pending_payment_entry.id)
        return render(
            request=request,
            template_name='team/payments/add_received_payment.html',
            context={
                'duplicate_payments': PendingInwardPaymentEntry.objects.filter(id__in=duplicate_payment_id),
                'success_payments': PendingInwardPaymentEntry.objects.filter(id__in=success_payment_id),
                'upload_file': True,
            }
        )
    except:
        raise


def inward_payment_adjustment_page(request):
    btn_submit = request.GET.get('accept_choice')
    try:
        payment = PendingInwardPaymentEntry.objects.get(id=request.GET.get('payment_id'))
        payment.customer = get_or_none(Sme, id=request.GET.get('customer_id'))
        payment.tds = to_int(request.GET.get('tds'))
        payment.save()
    except PendingInwardPaymentEntry.DoesNotExist:
        return json_error_response(msg="Pending payment does not exists", status=404)
    if btn_submit == 'save':
        return json_success_response('customer and tds saved successful')
    elif btn_submit == 'proceed':
        payment = PendingInwardPaymentEntry.objects.get(id=request.GET.get('payment_id'))
        credit_note = CreditNoteCustomer.objects.filter(status__in=['approved', 'partial'], customer=payment.customer)
        debit_note = DebitNoteCustomer.objects.filter(status__in=['approved', 'partial'], customer=payment.customer)
        credit_note_direct_advance = CreditNoteCustomerDirectAdvance.objects.filter(
            status__in=['approved', 'partial'], customer=payment.customer)
        debit_note_direct_advance = DebitNoteSupplierDirectAdvance.objects.filter(
            status__in=['approved', 'partial'], customer=payment.customer)

        invoice_data, tds_amount, total_amount, tds_rate = adjust_inward_payment(
            payment=payment, user=request.user
        )
        return render(
            request=request,
            template_name='team/payments/payment-adjustment-page.html',
            context={
                'payment': payment,
                'invoices': invoice_data,
                'total_amount': total_amount,
                'tds_amount': tds_amount,
                'tds_rate': tds_rate,
                'credit_note': credit_note,
                'debit_note': debit_note,
                'credit_note_direct_advance': credit_note_direct_advance,
                'debit_note_direct_advance': debit_note_direct_advance
            }
        )
    else:
        raise Http404


def adjust_inward_payment(payment, user):
    tds_amount = to_int(payment.tds)
    total_amount = to_int(payment.amount)
    tds_rate = tds_amount / (total_amount + tds_amount)
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
        if sum([booking.balance_for_customer for booking in invoice.bookings.exclude(booking_status='cancelled')]) > 10:
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
            for booking in invoice.bookings.order_by('shipment_date'):
                amount_to_be_received = to_int(booking.balance_for_customer)
                if amount_to_be_received > 0:
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


def inward_payment_adjustments(request):
    payment = PendingInwardPaymentEntry.objects.get(id=request.POST.get('payment_id'))
    for cnc_id, cnc_amount in zip(request.POST.getlist('cnc_id[]'), request.POST.getlist('cnc_adjusted_amount[]')):
        if to_int(cnc_amount) > 0:
            cnc = get_or_none(CreditNoteCustomer, id=cnc_id)
            if isinstance(cnc, CreditNoteCustomer):
                cnc.adjusted_amount = cnc.adjusted_amount + to_int(cnc_amount)
                cnc.adjusted_by = request.user
                cnc.adjusted_on = datetime.now()
                cnc.status = 'adjusted' if to_int(cnc.adjusted_amount) == cnc.credit_amount else 'partial'
                cnc.save()
                PendingInwardPaymentCreditDebitNoteCustomer.objects.create(
                    cnc=cnc, pending_inward=payment,
                    adjusted_amount=to_int(cnc_amount),
                    created_by=request.user,
                    changed_by=request.user
                )
    for dnc_id, dnc_amount in zip(request.POST.getlist('dnc_id[]'), request.POST.getlist('dnc_adjusted_amount[]')):
        if to_int(dnc_amount) > 0:
            dnc = get_or_none(DebitNoteCustomer, id=dnc_id)
            if isinstance(dnc, DebitNoteCustomer):
                dnc.adjusted_amount = dnc.adjusted_amount + to_int(dnc_amount)
                dnc.adjusted_by = request.user
                dnc.adjusted_on = datetime.now()
                dnc.status = 'adjusted' if to_int(dnc.adjusted_amount) == dnc.debit_amount else 'partial'
                dnc.save()
                PendingInwardPaymentCreditDebitNoteCustomer.objects.create(
                    dnc=dnc, adjusted_amount=to_int(dnc_amount),
                    pending_inward=payment,
                    created_by=request.user,
                    changed_by=request.user
                )

    invoices = Invoice.objects.filter(customer_fk=payment.customer, payment_received=False).order_by('date')
    for invoice in invoices:
        for booking in invoice.bookings.all():
            received_amount = request.POST.get(booking.booking_id + '_receivedAmountId')
            if to_int(received_amount) > 0:
                remarks = request.POST.get(booking.booking_id + '_remarksId', None) if request.POST.get(
                    booking.booking_id + '_remarksId', None) else request.POST.get('common_remarks', None)
                inward_pmt = inward_payment(
                    receive_from=payment.customer.get_name(),
                    amount=received_amount,
                    payment_mode=payment.payment_mode,
                    tds_amount=request.POST.get(booking.booking_id + '_tdsId'),
                    date=payment.payment_date.strftime('%d-%b-%Y'),
                    trn=payment.trn,
                    invoice_number=invoice.invoice_number,
                    remarks=remarks,
                    booking_id_list=[booking.id],
                    username=request.user.username
                )
                payment.bookings.add(booking)
                payment.inward_payment.add(inward_pmt)
        if -20 < sum(invoice.bookings.values_list('total_amount_to_company', flat=True)) - (
                sum(invoice.bookings.values_list('total_in_ward_amount', flat=True)) + sum(
            invoice.bookings.values_list('tds_deducted_amount', flat=True))) < 20:
            invoice.payment_received = True
            invoice.save()
            for booking in invoice.bookings.all():
                booking_inv_raised = check_booking_status(booking, 'invoice_raised')
                if booking_inv_raised:
                    booking_inv_sent = check_booking_status(booking, 'party_invoice_sent')
                    if not booking_inv_sent:
                        create_new_booking_status(booking, 'party_invoice_sent', User.objects.get(username='admin'))
                    else:
                        update_booking_status(booking, 'party_invoice_sent', 'in_progress', User.objects.get(username='admin'))
                    booking_inv_confirmed = check_booking_status(booking, 'invoice_confirmed')
                    if not booking_inv_confirmed:
                        create_new_booking_status(booking, 'invoice_confirmed', User.objects.get(username='admin'))
                    else:
                        update_booking_status(booking, 'invoice_confirmed', 'in_progress',
                                              User.objects.get(username='admin'))

    payment.adjusted_by = request.user
    payment.adjusted_flag = True
    payment.credited_flag = True
    payment.adjusted_datetime = datetime.now()
    payment.save()
    return json_success_response("success")


def payment_mode_date_message(request):
    payment_mode = request.GET.get('payment_mode')
    bank_account_id = request.GET.get('account_id')
    fuel_card_id = request.GET.get('fuel_card')
    date = request.GET.get('payment_date')
    amount = to_int(request.GET.get('amount'))
    if payment_mode == 'bank_transfer':
        bank = get_or_none(Bank, id=bank_account_id)
        if isinstance(bank, Bank) and isinstance(django_date_format(date), datetime):
            mode, payment_date = payment_mode_date(current_datetime=datetime.now(), bank=bank, amount=amount,
                                                   payment_date=django_date_format(date))
            return json_success_response(msg='Payment will be processed on {} to Account {}({})'.format(
                payment_date.strftime('%d-%b-%Y') if payment_date else 'Unknown', bank.account_number,
                bank.account_holder_name))
        else:
            return json_error_response(msg="Information is incorrect ", status=400)
    elif payment_mode == 'fuel_card':
        fuel_card = get_or_none(FuelCard, id=fuel_card_id)
        if isinstance(fuel_card, FuelCard):
            payment_date = django_date_format(date)
            return json_success_response(msg='Payment will be processed on {} to Fuel Card {}'.format(
                payment_date.strftime('%d-%b-%Y') if payment_date else 'Unknown', fuel_card.card_number))
        else:
            return json_error_response(msg="Information is incorrect ", status=400)
    return json_success_response(msg='Payment will be processed on {} through {} '.format(date, payment_mode))


@authenticated_user
def pending_inward_data(request):
    pass


@authenticated_user
def pending_inward_data_page(request):
    pass


@authenticated_user
def uploaded_cheque_data(request):
    pass


@authenticated_user
def uploaded_cheque_records_page(request):
    pass
