import io
import os
from datetime import datetime, date, timedelta, time

import pandas as pd
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from api import s3util
from api.helper import EMP_GROUP1, EMP_GROUP2, EMP_GROUP3, EMP_GROUP4
from api.utils import get_or_none
from authentication.models import Profile
from employee.models import TaskEmail, Employee, Task
from owner.models import FuelCard
from sme.models import Sme
from utils.models import Bank, AahoOffice, BankHolidays

BASE_DIR = settings.BASE_DIR

JSON_DATE_TIME_FORMAT = '%d-%b-%Y %I:%M %p'
JSON_DATE_FORMAT = '%d-%b-%Y'


def is_blank(string):
    return not (string and string.strip())


def django_date_format(date):
    if is_blank(date):
        return None
    elif date == 'None':
        return None
    else:
        return datetime.strptime(date, '%d-%b-%Y')


def to_int(value):
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return 0


def to_float(value):
    return 0 if not value else float(value)


def format_datetime(date_obj):
    if not isinstance(date_obj, datetime):
        return ""
    return date_obj.strftime(JSON_DATE_TIME_FORMAT)


def format_date(date_obj):
    if not isinstance(date_obj, date):
        return ""
    return date_obj.strftime(JSON_DATE_FORMAT)


def format_numeric(number):
    try:
        return '{0:.2f}'.format(number)
    except:
        return '0.00'


def to_date_format_1(date_obj):
    if is_blank(date_obj):
        return None
    return datetime.strptime(date_obj, '%m/%d/%Y')


def to_date_format_2(date_obj):
    if is_blank(date_obj):
        return None
    return datetime.strptime(date_obj, '%d %B %Y - %H:%M %p')


def to_str(val):
    if val:
        return str(val)
    else:
        return ''


def download_manual_booking_csv():
    from team.models import ManualBooking
    bookings = ManualBooking.objects.all()
    data = []
    for value in bookings:
        temp = []
        temp.append(format_date(value.shipment_date))
        temp.append(value.booking_id)
        lr_number = '\n'.join(value.lr_numbers.values_list('lr_number', flat=True))
        temp.append(lr_number)
        temp.append(value.truck_broker_owner_name)
        temp.append(value.truck_broker_owner_phone)
        temp.append(value.from_city)
        temp.append(value.to_city)
        temp.append(value.lorry_number)
        temp.append(value.total_amount_to_company)
        temp.append(value.total_in_ward_amount)
        temp.append(value.total_amount_to_owner)
        temp.append(value.total_out_ward_amount)
        temp.append(value.charged_weight)
        temp.append(value.party_rate)
        temp.append(value.supplier_rate)
        temp.append(value.get_pod_status_display())
        invoice_number = ''
        for inv in value.invoices.all():
            invoice_number += inv.invoice_number + ', '
        for inv in value.to_pay_invoice.all():
            invoice_number += inv.invoice_number + ', '
        temp.append(invoice_number[:-2])
        data.append(temp)
    df = pd.DataFrame(data, columns=['Shipment Date', 'Booking ID', 'LR Number', 'Comapny Name', 'Supplier Name',
                                     'Supplier Phone', 'Source', 'Destination', 'Lorry Number', 'Amount from Company',
                                     'Inward Amount', 'Amount to Owner', 'Outward Amount', 'Charged Weight',
                                     'Party Rate', 'Supplier Rate', 'POD Satatus', 'Invoice Number'])
    file_name = 'MB20170202001' + '.csv'
    bytes_io = io.BytesIO()
    df.to_csv(bytes_io, index=False)
    s3util.save_to_s3_downloads(filename=file_name, content=bytes_io)
    return df


def download_outward_payment():
    pass


def get_email_id_list_for_lr(source, destination):
    raipur_emails = ['rohit@aaho.in', 'pankaj@aaho.in', 'amit@aaho.in', 'pranav.vicks@gmail.com',
                     'pkrathoretcil80@gmail.com', 'venkatgboss@gmail.com']
    mumbai_emails = ['pankaj@aaho.in', 'asim.sheikh@aaho.in', 'rohit@aaho.in', 'harsh@aaho.in',
                     'akashpanday.2015@rediffmail.com', 'pinumathew@gmail.com']
    # bhiwandi_emails = ['pankaj@aaho.in', 'asim.sheikh@aaho.in', 'rohit@aaho.in', 'harsh@aaho.in',
    #                    'akashpanday.2015@rediffmail.com']
    bhiwandi_emails = ['harsh@aaho.in', 'pinumathew@gmail.com']
    ahmedabad_emails = ['pankaj@aaho.in', 'aaho.hemil@gmail.com', 'rohit@aaho.in', 'harsh@aaho.in',
                        'sanjay.aaho123@gmail.com', 'mile.rahulkumarsingh@gmail.com']
    visakhapatnam_emails = ['rohit@aaho.in', 'pankaj@aaho.in', 'nareshchvj@gmail.com', ]
    if source == 'Raipur':
        source = raipur_emails
    elif source == 'Mumbai':
        source = mumbai_emails
    elif source == 'Bhiwandi':
        source = bhiwandi_emails
    elif source == 'Ahmedabad':
        source = ahmedabad_emails
    elif source == 'Visakhapatnam':
        source = visakhapatnam_emails
    else:
        source = ['mani@aaho.in', 'pankaj@aaho.in', 'rohit@aaho.in']

    if destination == 'Raipur':
        destination = raipur_emails
    elif destination == 'Mumbai':
        destination = mumbai_emails
    elif destination == 'Bhiwandi':
        destination = bhiwandi_emails
    elif destination == 'Ahmedabad':
        destination = ahmedabad_emails
    elif destination == 'Visakhapatnam':
        destination = visakhapatnam_emails
    else:
        destination = ['mani@aaho.in', 'pankaj@aaho.in', 'rohit@aaho.in']
    return source, destination


def get_email_list(booking, task_name='demo', task_id=1):
    to_email_list = []
    if booking.company == Sme.objects.get(name=User.objects.get(username='sme')):
        task_email = TaskEmail.objects.filter(task__name=task_name).last()
        if task_email:
            to_email_list = list(task_email.employee.values_list('username__profile__email', flat=True))

    if not to_email_list:
        to_email_list = email_id_list(task_id=task_id, booking=booking)

    return to_email_list


def email_id_list(task_id, booking):
    try:
        task = TaskEmail.objects.get(task_id=task_id, office_id=booking.destination_office_id)
        destination = list(task.employee.values_list('username__profile__email', flat=True))
    except TaskEmail.DoesNotExist:
        destination = []
    try:
        task = TaskEmail.objects.get(task_id=task_id, office_id=booking.source_office_id)
        source = list(task.employee.values_list('username__profile__email', flat=True))
    except TaskEmail.DoesNotExist:
        source = []
    email_list = source + list(set(destination) - set(source))

    return email_list


def check_invoice_status(booking):
    from team.models import Invoice
    if Invoice.objects.filter(bookings=booking).exists():
        return True
    else:
        return False


def update_inward_payments(booking):
    amount_list = booking.inward_booking.values_list('actual_amount', flat=True)
    booking.total_in_ward_amount = sum(amount_list)
    booking.tds_deducted_amount = sum(booking.inward_booking.values_list('tds', flat=True))
    booking.save()
    payment_plus_tds = sum(amount_list) + booking.tds_deducted_amount
    if payment_plus_tds == 0:
        booking.inward_payment_status = 'no_payment'
    elif payment_plus_tds < booking.total_amount_to_company:
        booking.inward_payment_status = 'partial_received'
    elif payment_plus_tds == booking.total_amount_to_company:
        booking.inward_payment_status = 'full_received'
    elif payment_plus_tds > booking.total_amount_to_company:
        booking.inward_payment_status = 'excess'
    booking.save()


def update_outward_payments(booking):
    from team.models import OutWardPayment
    amount_list = OutWardPayment.objects.filter(booking_id=booking).exclude(is_refund_amount=True).values_list(
        'actual_amount', flat=True)
    outward_payment = sum(amount_list)
    # update amount
    booking.total_out_ward_amount = sum(amount_list)
    booking.save()
    if outward_payment == 0:
        booking.outward_payment_status = 'no_payment_made'
    elif outward_payment < booking.total_amount_to_owner:
        booking.outward_payment_status = 'partial'
    elif outward_payment == booking.total_amount_to_owner:
        booking.outward_payment_status = 'complete'
    elif outward_payment > booking.total_amount_to_owner:
        booking.outward_payment_status = 'excess'
    booking.save()


def update_invoice_status(booking):
    if check_invoice_status(booking):
        if booking.invoice_status == 'no_invoice':
            booking.invoice_status = 'invoice_raised'
            booking.save()


def fuel_card_obj(card_id):
    if card_id:
        if FuelCard.objects.filter(id=card_id).exists():
            return FuelCard.objects.filter(id=card_id).last()
    return None


def aaho_office(username):
    employee = get_or_none(Employee, username=get_or_none(User, username=username))
    if employee:
        return employee.office_multiple.all()
    else:
        raise PermissionDenied


def manual_booking_id_list(username, user_group_list):
    from team.models import ManualBooking
    office_obj = aaho_office(username=username)
    if EMP_GROUP3 in user_group_list or EMP_GROUP2 in user_group_list:
        booking_history = ManualBooking.objects.filter(
            Q(source_office__in=office_obj) | Q(destination_office__in=office_obj)).exclude(
            booking_status__icontains='cancelled').values_list('id', flat=True)
    elif EMP_GROUP1 in user_group_list or EMP_GROUP4 in user_group_list:
        booking_history = ManualBooking.objects.exclude(
            booking_status__icontains='cancelled').values_list('id', flat=True)
    else:
        booking_history = []
    return booking_history


def dest_sms_employee_mobiles(booking):
    try:
        task_emp = TaskEmail.objects.filter(
            Q(office=booking.destination_office) & Q(task=Task.objects.get(name='dest_emp_sms')))
        mobiles = ', '.join(task_emp.last().employee.values_list('username__profile__phone', flat=True))
    except (
            TaskEmail.DoesNotExist, TaskEmail.MultipleObjectsReturned, Task.MultipleObjectsReturned,
            Task.DoesNotExist) as e:
        mobiles = '8978937498'
    return mobiles


def verify_profile_phone(username, phone, alt_phone):
    if not phone:
        return True, "Phone is empty"
    if not username:
        return True, "User is not registered"
    if alt_phone:
        if Profile.objects.filter(Q(phone=phone) | Q(phone=alt_phone) | Q(alternate_phone=phone) | Q(
                alternate_phone=alt_phone)).exclude(user=get_or_none(User, username=username)).exists():
            return True, "Phone Already Exists"
        else:
            return False, "Phone Doesn't Exists"
    else:
        if Profile.objects.filter(Q(phone=phone) | Q(alternate_phone=phone)).exclude(
                user=get_or_none(User, username=username)).exists():
            return True, "Phone Already Exists"
        else:
            return False, "Phone Doesn't Exists"


def verify_profile_email(username, email, alt_email):
    if not email:
        return False, "Email is empty"
    if not username:
        return True, "User is not registered"
    if not alt_email:
        if Profile.objects.filter(Q(email=email) | Q(alternate_email=email)).exclude(
                user=get_or_none(User, username=username)).exists():
            return True, "Email Already Exists"
        else:
            return False, "Email Doesn't Exists"
    else:
        if Profile.objects.filter(Q(email=email) | Q(email=alt_email) | Q(alternate_email=email) | Q(
                alternate_email=alt_email)).exclude(user=get_or_none(User, username=username)).exists():
            return True, "Email Already Exists"
        else:
            return False, "Email Doesn't Exists"


def is_2nd_4th_saturday(dt):
    week_number = (dt.day - 1) // 7 + 1
    return week_number in [2, 4]


def is_neft_holiday(dt):
    if dt.weekday() == 6:
        return True
    elif dt.weekday() == 5 and is_2nd_4th_saturday(dt.date()):
        return True
    elif BankHolidays.objects.filter(date=dt.date()).exists():
        return True
    else:
        return False


def next_neft_working_day(dt):
    while is_neft_holiday(dt):
        dt += timedelta(days=1)
    return dt


def is_neft_hour(current_datetime):
    return time(0, 0) <= current_datetime.time() <= time(17, 0) and not is_neft_holiday(current_datetime)


def is_imps_hour(current_datetime):
    return time(17, 0) < current_datetime.time() <= time(20, 45)


def is_hdfc_bank_account(bank):
    if isinstance(bank, Bank) and bank.ifsc.lower().startswith('hdfc'):
        return True
    else:
        return False


def payment_mode_date(current_datetime, bank, amount, payment_date):
    if not isinstance(bank, Bank) and not isinstance(payment_date, datetime):
        return None, payment_date
    if is_hdfc_bank_account(bank=bank):
        mode = 'hdfc_internal_account'
        if payment_date.weekday() == 6:
            payment_date = (payment_date + timedelta(days=1))
        else:
            payment_date = payment_date
    elif payment_date > current_datetime:
        while is_neft_holiday(payment_date):
            payment_date = next_neft_working_day(payment_date)
        if is_hdfc_bank_account(bank=bank):
            mode = 'hdfc_internal_account'
        else:
            mode = 'neft' if to_int(amount) <= 200000 else 'rtgs'
    elif is_neft_hour(current_datetime):
        if is_hdfc_bank_account(bank=bank):
            mode = 'hdfc_internal_account'
            payment_date = current_datetime
        else:
            mode = 'neft' if to_int(amount) <= 200000 else 'rtgs'
            payment_date = current_datetime

    elif is_imps_hour(current_datetime):
        if is_hdfc_bank_account(bank=bank):
            mode = 'hdfc_internal_account'
            if current_datetime.weekday() == 6:
                payment_date = (current_datetime + timedelta(days=1))
            else:
                payment_date = current_datetime
        else:
            if current_datetime.weekday() == 6:
                if is_neft_holiday(current_datetime + timedelta(days=1)):
                    mode = 'imps'
                    payment_date = (current_datetime + timedelta(days=1))
                else:
                    mode = 'neft' if to_int(amount) <= 200000 else 'rtgs'
                    payment_date = (current_datetime + timedelta(days=1))
            else:
                mode = 'imps'
                payment_date = current_datetime.date()
    elif is_neft_holiday(
            payment_date) and payment_date.date() == current_datetime.date() and current_datetime.weekday() != 6 and (
            time(0, 0) <= current_datetime.time() <= time(17, 0) or is_imps_hour(current_datetime)):
        mode = 'imps'
        payment_date = current_datetime.date()
    else:
        payment_date = payment_date + timedelta(days=1)
        while is_neft_holiday(payment_date):
            payment_date = next_neft_working_day(payment_date)
        if is_hdfc_bank_account(bank=bank):
            mode = 'hdfc_internal_account'
        else:
            mode = 'neft' if to_int(amount) <= 200000 else 'rtgs'
    return mode, payment_date.date() if isinstance(payment_date, datetime) else payment_date


def check_payment_mode():
    print(payment_mode_date(current_datetime=datetime(2018, 6, 24, 4, 30), bank=Bank.objects.get(id=2058), amount=2000,
                            payment_date=django_date_format('25-Jun-2018')))


def weekly_status_email_id_list(aaho_office_id):
    if isinstance(aaho_office_id, int) and AahoOffice.objects.filter(id=aaho_office_id).exists():
        aaho_office = AahoOffice.objects.get(id=aaho_office_id)
        email_id = aaho_office.employee_office_multiple.filter(
            username__in=User.objects.filter(
                groups__in=Group.objects.filter(name__in=[EMP_GROUP1, EMP_GROUP2]))).exclude(
            status__iexact='inactive').values_list('username__profile__email', flat=True)
        return list(filter(lambda email: email != None, email_id))
    else:
        return []
