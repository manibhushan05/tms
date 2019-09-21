from datetime import datetime, timedelta
from io import BytesIO, StringIO

import pandas as pd
from django.db.models import Q
from django.utils import timezone

from api import email
from api.models import PaymentFile
from api.s3util import save_to_s3_payment
from api.utils import get_or_none
from employee.models import TaskEmail
from team.helper.helper import to_int
from team.models import OutWardPayment


def get_today_payments():
    outward = OutWardPayment.objects.filter(payment_date=datetime.today().date()).exclude(bank_account=None).exclude(
        status='paid')
    payment_list = []
    for payment in outward:
        data = []
        if payment.payment_mode == 'neft':
            mode = 'N'
        elif payment.payment_mode == 'rtgs':
            mode = 'R'
        elif payment.payment_mode == 'imps':
            mode = 'M'
        elif payment.payment_mode == 'hdfc_internal_account':
            mode = 'I'
        else:
            mode = 'I'
        data.append(mode)
        data.append(payment.bank_account.beneficiary_code[:14] if payment.bank_account else '')
        data.append(payment.bank_account.account_number if payment.bank_account else '')
        data.append(str(to_int(payment.actual_amount)))
        data.append(payment.bank_account.account_holder_name if payment.bank_account else '')
        data.append('')
        data.append('')
        data.append('')
        data.append('')
        data.append('')
        data.append('')
        data.append('')
        data.append('')
        booking_full = payment.booking_id.filter(Q(booking_id__istartswith='AH') | Q(
            booking_id__istartswith='AAHO')).first()
        booking_commission = payment.booking_id.filter(
            Q(booking_id__istartswith='AB') | Q(booking_id__istartswith='BROKER')).first()
        if booking_full:
            lr_number = booking_full.lr_numbers.all().first().lr_number
            narration = lr_number + payment.bank_account.beneficiary_code if payment.bank_account else ''
        elif booking_commission:
            narration = booking_commission.booking_id + payment.bank_account.beneficiary_code if payment.bank_account else ''
        else:
            narration = ''
        data.append(narration[:20])
        data.append('')
        data.append('')
        data.append('')
        data.append('')
        data.append('')
        data.append('')
        data.append('')
        data.append('')
        data.append(str(payment.payment_date.strftime('%d/%m/%Y')))
        data.append('')
        data.append(payment.bank_account.ifsc if payment.bank_account else '')
        data.append('')
        data.append('')
        data.append('')
        time = (payment.created_on + timedelta(hours=5, minutes=30)).time()
        # if dt.time(0, 0) <= time < dt.time(17, 20):
        payment_list.append(data)
        payment.status = 'paid'
        payment.save()

    df = pd.DataFrame(payment_list)
    string_io = StringIO()
    df.to_csv(string_io, index=False, header=False)
    content = string_io.getvalue() or '\n'

    date = timezone.now().date()
    new_file_name = PaymentFile.get_next_file_name(date=date)

    dl_url = create_payment_file(new_file_name, date, content)

    task = TaskEmail.objects.get(task_id=4, office_id=1)
    email_id_list = list(task.employee.values_list('username__profile__email', flat=True))
    send_payment_file_email(new_file_name, dl_url, email_id_list)

    return dl_url


def create_payment_file(new_file_name, date, content, summary=False):
    pf = get_or_none(PaymentFile, name=new_file_name)
    if pf:
        pf.upload.delete_from_s3()
        pf.upload.delete()
        pf.delete()
    s3_upload = save_to_s3_payment(new_file_name, content)
    pf = PaymentFile.objects.create(upload=s3_upload, date=date, name=new_file_name, summary=summary)
    dl_url = s3_upload.public_url()
    return dl_url


def send_payment_file_email(filename, link, to):
    subject = 'Payment File %s' % filename
    text_body = 'Visit this link to download the file - %s' % link
    html_body = 'Click <a href="%s" download="%s">here</a> to download the file' % (link, filename)
    email.send(subject, body=text_body, html=html_body, to=to)


def payment_summary_today():
    outward = OutWardPayment.objects.filter(payment_date=datetime.utcnow().date()).exclude(
        bank_account=None).exclude(status='unpaid')
    data = []
    for value in outward:
        temp = []
        booking_id = ', '.join(list(value.booking_id.values_list('booking_id', flat=True)))
        lr_number = ''
        bookings = value.booking_id.all()
        for lr in bookings:
            lr_number += ', '.join(lr.lr_numbers.values_list('lr_number', flat=True))
        temp.append(booking_id)
        temp.append(lr_number)
        temp.append(value.bank_account.account_holder_name)
        temp.append(str(value.actual_amount))
        data.append(temp)

    df = pd.DataFrame(data, columns=['BOOKING ID', 'LR NUMBER', 'BENEFICIARY NAME', 'AMOUNT'])

    string_io = StringIO()
    df.to_csv(string_io, index=False)
    content = string_io.getvalue() or '\n'

    date = timezone.now().date()
    file_name = '%s.csv' % date.strftime('%y%m%d-%H%M%S')

    dl_url = create_payment_file(file_name, date, content, summary=True)
    send_payment_summary_email(file_name, dl_url, ['harsh@aaho.in'])

    return dl_url


def send_payment_summary_email(filename, link, to):
    subject = 'Payment Summary File %s' % filename
    text_body = 'Visit this link to download the file - %s' % link
    html_body = 'Click <a href="%s" download="%s">here</a> to download the file' % (link, filename)
    email.send(subject, body=text_body, html=html_body, to=to)
