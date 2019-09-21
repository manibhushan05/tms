from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

from api.models import S3Upload
from api.utils import get_or_none
from authentication.models import Profile
from employee.models import TaskEmail
from sme.models import Sme
from team.models import OutWardPayment, ManualBooking

from team.helper.helper import django_date_format, to_int, email_id_list, get_email_list


def email_outward_payment(payment):
    booking_data = payment.booking_id.all().first()
    booking_id = '' if not booking_data else booking_data.booking_id
    paid_to = payment.paid_to
    actual_amount = payment.actual_amount
    payment_mode = payment.payment_mode
    remarks = payment.remarks
    payment_date = 'Not Available' if not payment.payment_date else payment.payment_date.strftime('%d-%b-%Y')
    lr_number = ''
    for value in booking_data.lr_numbers.all():
        lr_number += value.lr_number + ', '
    lr_number = lr_number[:-2]
    subject = "New Outward Payment for " + booking_id
    prior_amount_data = OutWardPayment.objects.filter(booking_id=booking_data)
    paid_amount = 0
    for value in prior_amount_data:
        paid_amount += value.actual_amount
    paid_amount = to_int(paid_amount)
    if payment.bank_account:
        body = "LR No(s)    : " + lr_number + '\nPaid To      : ' + payment.paid_to + '\nAccount Holder Name: ' + payment.bank_account.account_holder_name + '\nAmount      : ' + actual_amount + '\nMode         : ' + payment_mode + "\nDate           : " + payment_date + "\nRemarks    : " + remarks + "\n\n" + "Payments made for " + booking_id + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + booking_id + ": Rs. " + str(
            booking_data.total_amount_to_owner)
    elif payment.fuel_card:
        body = "LR No(s)    : " + lr_number + '\nPaid To      : ' + paid_to + '\nFuel Card Number: ' + payment.fuel_card.card_number + '\nAmount      : ' + actual_amount + '\nMode         : ' + payment_mode + "\nDate           : " + payment_date + "\nRemarks    : " + remarks + "\n\n" + "Payments made for " + booking_id + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + booking_id + ": Rs. " + str(
            booking_data.total_amount_to_owner)
    else:
        body = "LR No(s)    : " + str(lr_number) + '\nPaid To      : ' + str(
            paid_to) + '\nAmount      : ' + actual_amount + '\nMode         : ' + payment.get_payment_mode_display() + "\nDate           : " + payment_date + "\nRemarks    : " + str(
            remarks) + "\n\n" + "Payments made for " + str(booking_id) + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + str(booking_id) + ": Rs. " + str(
            booking_data.total_amount_to_owner)

    to_email_list = get_email_list(booking_data)
    email = EmailMessage(subject, body, 'AAHO OUTWARD PAYMENT', to=to_email_list)
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


def email_updated_outward_payment(request, booking_id, payment, old_amount, new_amount):
    booking_data = ManualBooking.objects.get(booking_id=booking_id)
    paid_to = request.POST.get('paid_to')
    payment_mode = request.POST.get('outward_payment_mode')
    remarks = request.POST.get('remarks')
    payment_date = django_date_format(request.POST.get('outward_payment_date')).strftime('%d-%b-%Y')
    lr = ''
    for value in booking_data.lr_numbers.all():
        lr += value.lr_number + ', '
    subject = "Updated Outward Payment for " + booking_data.booking_id
    prior_amount_data = OutWardPayment.objects.filter(booking_id=booking_data)
    paid_amount = 0
    for value in prior_amount_data:
        paid_amount += value.actual_amount
    paid_amount = to_int(paid_amount)
    if payment.bank_account:
        body = "LR No(s)    : " + lr + '\nPaid To      : ' + payment.paid_to + '\nAccount Holder Name: ' + payment.bank_account.account_holder_name + '\nPrevious Amount      : ' + old_amount + '\nUpdated Amount      : ' + new_amount + '\nMode         : ' + payment_mode + "\nDate           : " + payment_date + "\nRemarks    : " + remarks + "\n\n" + "Payments made for " + booking_id + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + booking_id + ": Rs. " + str(
            booking_data.total_amount_to_owner)
    elif payment.fuel_card:
        body = "LR No(s)    : " + lr + '\nPaid To      : ' + paid_to + '\nFuel Card Number: ' + payment.fuel_card.card_number + '\nPrevious Amount      : ' + old_amount + '\nUpdated Amount      : ' + new_amount + '\nMode         : ' + payment_mode + "\nDate           : " + payment_date + "\nRemarks    : " + remarks + "\n\n" + "Payments made for " + booking_id + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + booking_id + ": Rs. " + str(
            booking_data.total_amount_to_owner)
    else:
        body = "LR No(s)    : " + lr + '\nPaid To      : ' + paid_to + '\nPrevious Amount      : ' + old_amount + '\nUpdated Amount      : ' + new_amount + '\nMode         : ' + payment.get_payment_mode_display() + "\nDate           : " + payment_date + "\nRemarks    : " + remarks + "\n\n" + "Payments made for " + booking_id + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + booking_id + ": Rs. " + str(
            booking_data.total_amount_to_owner)

    to_email_list = get_email_list(booking_data)
    email = EmailMessage(subject, body, 'AAHO UPDATED OUTWARD PAYMENT', to=to_email_list)
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


def email_add_new_beneficiary(bank):
    subject = "New Beneficiary Account Added"
    body = "\n Beneficiary Code: " + bank.beneficiary_code + "\n Account Holder Name: " + bank.account_holder_name + "\n Account Number: " + bank.account_number + "\n IFSC Code: " + bank.ifsc + "\n Account Type: " + bank.get_account_type_display() + "\n Transaction Type: " + bank.get_transaction_type_display() + "\n Bank Name: " + bank.bank + "\n Address: " + bank.address + "\n City: " + bank.city
    email_address = list(
        TaskEmail.objects.filter(task__name='new_beneficiary').last().employee.values_list('username__profile__email',
                                                                                           flat=True))
    email = EmailMessage(subject, body, 'NEW BENEFICIARY ACCOUNT', to=email_address)
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


def email_lorry_receipt(booking_id):
    booking = ManualBooking.objects.get(booking_id=booking_id)
    lr_list = booking.lr_numbers.values_list('lr_number', flat=True)
    lr_number = ', '.join(lr_list)
    from_city = booking.from_city
    to_city = booking.to_city
    subject = 'LR(s) ' + lr_number + ' for ' + from_city + ' to ' + to_city + ' ' + booking.shipment_date.strftime(
        '%d-%b-%Y')
    body = 'PFA'
    to_email_list = get_email_list(booking, task_id=3)
    lr_filenames = ['%s.pdf' % l for l in lr_list]
    email = EmailMessage(subject, body, 'AAHO LR', to=to_email_list)
    s3_uploads = S3Upload.objects.filter(filename__in=lr_filenames).exclude(deleted=True, uploaded=False)

    for upload in s3_uploads:
        email.attach(upload.filename, upload.read(), "application/pdf")

    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


def email_commission_booking(booking):
    from_city = booking.from_city
    to_city = booking.to_city
    vehicle_number = booking.lorry_number
    driver_name = booking.driver_name
    driver_phone = booking.driver_phone
    driver_dl = booking.driver_dl_number
    supplier_name = booking.truck_broker_owner_name
    supplier_phone = booking.truck_broker_owner_phone
    weight = str(booking.charged_weight)
    supplier_rate = str(booking.supplier_rate)
    party_rate = str(booking.party_rate)
    try:
        sme = booking.company
        if sme:
            profile = get_or_none(Profile, user=sme.name)
            company = ('' if not profile else profile.name) or ''
        else:
            company = ''
    except Sme.DoesNotExist:
        company = ''
    subject = 'Comm. only booking from ' + from_city + ' to ' + to_city + ' Date: ' + booking.shipment_date.strftime(
        '%d-%b-%Y') + ' for ' + company
    body = ' Company Name: ' + company + '\n From City: ' + from_city + '\n To City: ' + to_city + '\n Vehicle Number: ' + vehicle_number + '\n Driver Name: ' + driver_name + '\n Driver Phone: ' + driver_phone + '\n Driver DL No.: ' + driver_dl + '\n Supplier Name: ' + supplier_name + '\n Supplier Phone: ' + supplier_phone + '\n Weight: ' + weight + '\n Supplier Rate: ' + supplier_rate + '\n Party Rate: ' + party_rate
    to_email_list = get_email_list(booking, task_id=3)
    email = EmailMessage(subject, body, 'AAHO LR', to=to_email_list)
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()
