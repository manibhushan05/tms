from datetime import datetime, timedelta
from io import BytesIO, StringIO

import pandas as pd
from django.conf import settings
from django.core.mail.message import EmailMessage
from django.db.models import Q
from django.template.loader import get_template
from django.utils import timezone

from api import email
from api.models import PaymentFile
from api.s3util import save_to_s3_payment, save_to_s3_daily_sales_report
from api.utils import to_int, get_or_none
from employee.models import TaskEmail
from restapi.service.tallyintegration import bank_transfer_payments
from team.models import OutWardPayment, ManualBooking


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


def get_today_payments():
    outward = OutWardPayment.objects.filter(payment_date__lte=datetime.now().today()).exclude(
        bank_account=None).exclude(status__in=['paid', 'reconciled'])
    if outward.exists():
        bank_transfer_payments(payments=outward)
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
            if payment.booking_id.exclude(lr_numbers=None).exists():
                booking = payment.booking_id.first()
                lr_number = booking.lr_numbers.all().first().lr_number
                narration = '{}OW{}'.format(lr_number[:12], str(payment.id).zfill(6))
            else:
                booking = payment.booking_id.first()
                narration = '{}OW{}'.format(booking.booking_id[:12], str(payment.id).zfill(6))
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
        send_payment_file_email(filename=new_file_name, link=dl_url, to=email_id_list)
        return dl_url
    return None


def send_sales_report():
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

        string_io = StringIO()
        df.to_csv(string_io, index=False, header=False)
        content = string_io.getvalue() or '\n'
        filename = datetime.now().strftime('%d%b%Y%I%M') + '.csv'
        s3_upload = save_to_s3_daily_sales_report(filename, content)
        s3_url = s3_upload.public_url()
        subject = '[Aaho] Daily Sales Report for ' + (datetime.now().date() - timedelta(days=1)).strftime(
            '%d-%b-%Y')
        body = get_template('team/emails/last-day-bookings.html').render(context={'mb': mb, 's3_url': s3_url})
        email = EmailMessage(subject, body,
                             to=['harsh@aaho.in', 'tp.ananth@aaho.in', 'rohit@aaho.in', 'pankaj@aaho.in'])
        email.content_subtype = 'html'
        if settings.ENABLE_MAIL and not settings.TESTING:
            email.send()
        return s3_url
    return None


def send_payment_summary_email(filename, link, to):
    subject = 'Payment Summary File %s' % filename
    text_body = 'Visit this link to download the file - %s' % link
    html_body = 'Click <a href="%s" download="%s">here</a> to download the file' % (link, filename)
    email.send(subject, body=text_body, html=html_body, to=to)


def payment_summary_today():
    outward = OutWardPayment.objects.filter(payment_date__lte=datetime.now().today()).exclude(
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
