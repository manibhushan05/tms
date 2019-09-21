from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError

from api import s3util
from api.decorators import authenticated_user
from api.helper import json_success_response, json_error_response, json_400_incorrect_use, json_401_wrong_credentials, \
    json_401_inactive_user, json_response
from api.utils import get_or_none, get_ext
from owner.models import FuelCard
from team import tasks
from team.models import ManualBooking, OutWardPayment
from team.services.create_new_tables import outward_payment
from team.services.emails import email_add_new_beneficiary
from django.conf import settings
from utils.models import Bank, IfscDetail


def to_int(value):
    if not value:
        return 0
    try:
        return int(str(value))
    except ValueError:
        return int(float(str(value)))


def error_exceeding_outward_amount(request):
    return render(request=request, template_name='mobile/error_exceeded_payment.html')


def check_total_paid_amount_to_owner(booking_id_list, amount):
    manual_bookings = ManualBooking.objects.filter(id__in=booking_id_list)
    print (to_int(sum(
        OutWardPayment.objects.filter(booking_id__in=manual_bookings).values_list('actual_amount',
                                                                                  flat=True))))
    return (to_int(sum(
        OutWardPayment.objects.filter(booking_id__in=manual_bookings).values_list('actual_amount',
                                                                                  flat=True))) + to_int(
        amount)) <= to_int(sum(manual_bookings.values_list('total_amount_to_owner', flat=True)))


def m_login(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    print(username, password)
    if not username or not password:
        return json_400_incorrect_use()
    user = authenticate(username=username, password=password)
    if user is None:
        return json_401_wrong_credentials()
    if not user.is_active:
        return json_401_inactive_user()
    login(request, user)
    return json_success_response(msg='success')


def m_login_page(request):
    return render(request=request, template_name='mobile/login.html')


@authenticated_user
def outward_payment_page(request):
    booking = ManualBooking.objects.exclude(
        Q(outward_payment_status='complete') | Q(outward_payment_status='excess')).exclude(
        booking_status__iexact='cancelled')
    fuel_card = FuelCard.objects.exclude(card_number=None)
    bank_account = Bank.objects.filter(status='active')
    context = {
        'booking': booking,
        'fuel_card': fuel_card,
        'bank_account': bank_account
    }
    return render(request=request, template_name='mobile/outward_payment.html', context=context)


@authenticated_user
def m_outward_payment(request):
    if check_total_paid_amount_to_owner([request.POST.get('booking_id')], request.POST.get('actual_amount')):
        payment = outward_payment(
            paid_to=request.POST.get('paid_to'), amount=request.POST.get('actual_amount'),
            date=request.POST.get('outward_payment_date'),
            fuel_card=request.POST.get('fuel_card_number'),
            remarks=request.POST.get('remarks'), booking_id_list=[request.POST.get('booking_id')],
            account_id=request.POST.get('bank_account_number'),
            payment_mode=request.POST.get('outward_payment_mode'),
            is_sms=request.POST.get('send_sms_supplier'),
            username=request.user.username
        )
        if settings.ENABLE_MAIL:
            tasks.email_outward_payment.delay(payment.id)
        return HttpResponse("Success")
    else:
        return json_error_response("ERROR", status=409)


@authenticated_user
def dashboard(request):
    return render(request=request, template_name='mobile/dashboard.html')


@authenticated_user
def register_driver(request):
    return render(request=request, template_name='mobile/register-driver.html')


def register_beneficiary_bank_account(request):
    return render(request=request, template_name='mobile/fetch-bank-details-using-ifsc.html')


def fetch_bank_details_using_ifsc(request):
    try:
        ifsc = IfscDetail.objects.get(ifsc_code__iexact=request.GET.get('fetch_ifsc'))
    except IfscDetail.DoesNotExist:
        ifsc = []
    return render(request=request, template_name='mobile/register_beneficiary_bank_account.html',
                  context={'ifsc': ifsc})


def create_beneficiary_account(request):
    account_number = request.POST.get('account_number')

    bank = get_or_none(Bank, account_number=account_number)
    if bank:
        return render(request=request, template_name='mobile/beneficiary_exists.html', context={'bank': bank})

    try:
        account_document = request.FILES['account_document']
    except MultiValueDictKeyError:
        account_document = None

    bank = Bank.objects.create(
        bank=request.POST.get('bank_name'),
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

    return json_success_response('success')
