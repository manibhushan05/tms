import time

import pandas as pd
from io import StringIO
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Q
from team.helper.helper import to_int
from api.s3 import get_client
from api.s3util import save_to_s3_weekly_inquiry_report
from api.sms import send_sms
from api.utils import get_or_none
from employee.models import Employee
from fms.models import Requirement
from report.lr_html import generate_lorry_receipt
from sme.models import Sme
from team.models import ManualBooking
from transiq.celery import app
import datetime
from datetime import timedelta
from django.template.loader import get_template

from utils.models import AahoOffice


@app.task
def send_otp_sms(mobiles, text):
    send_sms(mobiles, text)


@app.task
def send_otp_email(email, text):
    email = EmailMessage("AAHO OTP", text, to=email)
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()




@app.task(ignore_result=True)
def send_booking_status_expired_notifications():
    from restapi.models import BookingStatuses
    booking_statuses = BookingStatuses.objects.all()
    bses = BookingStatusExpirySwitcher(booking_statuses)
    for bs in booking_statuses:
        time.sleep(10)
        bses.case(bs.status, bs.time_limit)


@app.task(ignore_result=True)
def generate_lorry_receipt_task(id):
    booking = get_or_none(ManualBooking, id=id)
    if isinstance(booking, ManualBooking):
        generate_lorry_receipt(booking)


class BookingStatusExpirySwitcher(object):

    def __init__(self, booking_statuses):
        self.booking_statuses = booking_statuses
        self.present_date = datetime.datetime.now()

    def case(self, key, time_limit):
        method_name = 'booking_status_expired_' + str(key)
        method = getattr(self, method_name, lambda: 'Invalid Booking Status')
        return method(time_limit)

    def booking_status_expired_confirmed(self, time_limit):
        from restapi.models import BookingStatusesMapping
        from restapi.signals import send_booking_status_expired_notification
        print('Booking status expiry confirmed')
        confirmed_bookings = BookingStatusesMapping.objects.filter(booking_status_chain__booking_status__status='confirmed').\
            exclude(deleted=True).values_list('manual_booking_id', flat=True)
        loaded_bookings = BookingStatusesMapping.objects.filter(booking_status_chain__booking_status__status='loaded').\
            exclude(deleted=True).values_list('manual_booking_id', flat=True)
        only_confirmed_bookings = [x for x in confirmed_bookings if x not in loaded_bookings]
        expired_confirmed_bookings = []
        only_confirmed_bookings_objects = BookingStatusesMapping.objects.filter(
            manual_booking__id__in=only_confirmed_bookings, booking_status_chain__booking_status__status='confirmed')
        for cb in only_confirmed_bookings_objects:
            if (cb.created_on + timedelta(minutes=time_limit)) < self.present_date:
                expired_confirmed_bookings.append({
                    'booking_id': cb.manual_booking.booking_id,
                    'app': 'AE',
                    'aaho_office_id': cb.manual_booking.source_office.id,
                    'title_text': 'Loading',
                    'functionality': 'pending_lr',
                    'is_count_update': False
                })
        send_booking_status_expired_notification(expired_confirmed_bookings)
        return

    def booking_status_expired_loaded(self, time_limit):
        from restapi.models import BookingStatusesMapping
        from restapi.signals import send_booking_status_expired_notification
        print('Booking status expiry loaded')
        loaded_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status='loaded'). \
            exclude(deleted=True).values_list('manual_booking_id', flat=True)
        lr_generated_bookings = BookingStatusesMapping.objects.filter(booking_status_chain__booking_status__status='lr_generated'). \
            exclude(deleted=True).values_list('manual_booking_id', flat=True)
        only_loaded_bookings = [x for x in loaded_bookings if x not in lr_generated_bookings]
        expired_loaded_bookings = []
        only_loaded_bookings_objects = BookingStatusesMapping.objects.filter(
            manual_booking__id__in=only_loaded_bookings, booking_status_chain__booking_status__status='loaded')
        for cb in only_loaded_bookings_objects:
            if (cb.created_on + timedelta(minutes=time_limit)) < self.present_date:
                expired_loaded_bookings.append({
                    'booking_id': cb.manual_booking.booking_id,
                    'app': 'WB',
                    'aaho_office_id': cb.manual_booking.source_office.id,
                    'title_text': 'LR Generation',
                    'functionality': 'lr_generation',
                    'is_count_update': False
                })
        send_booking_status_expired_notification(expired_loaded_bookings)
        return

    def booking_status_expired_lr_generated(self, time_limit):
        from restapi.models import BookingStatusesMapping
        from restapi.signals import send_booking_status_expired_notification
        print('Booking status expiry lr generated')
        lr_generated_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status='lr_generated'). \
            exclude(deleted=True).values_list('manual_booking_id', flat=True)
        unloaded_bookings = BookingStatusesMapping.objects.filter(booking_status_chain__booking_status__status='unloaded'). \
            exclude(deleted=True).values_list('manual_booking_id', flat=True)
        advance_paid_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status='advance_paid'). \
            exclude(deleted=True).values_list('manual_booking_id', flat=True)
        only_lr_generated_not_unloaded_bookings = [x for x in lr_generated_bookings if x not in unloaded_bookings]
        only_lr_generated_advance_not_paid_bookings = [x for x in lr_generated_bookings if x not in advance_paid_bookings]
        expired_lr_generated_not_unloaded_bookings = []
        only_lr_generated_not_unloaded_bookings_objects = BookingStatusesMapping.objects.filter(
            manual_booking__id__in=only_lr_generated_not_unloaded_bookings, booking_status_chain__booking_status__status='lr_generated')
        for cb in only_lr_generated_not_unloaded_bookings_objects:
            if (cb.created_on + timedelta(minutes=time_limit)) < self.present_date:
                expired_lr_generated_not_unloaded_bookings.append({
                    'booking_id': cb.manual_booking.booking_id,
                    'app': 'AE',
                    'aaho_office_id': cb.manual_booking.source_office.id,
                    'title_text': 'Unloading',
                    'functionality': 'in_transit',
                    'is_count_update': False
                })
        send_booking_status_expired_notification(expired_lr_generated_not_unloaded_bookings)

        expired_lr_generated_advance_not_paid_bookings = []
        only_lr_generated_advance_not_paid_bookings_objects = BookingStatusesMapping.objects.filter(
            manual_booking__id__in=only_lr_generated_advance_not_paid_bookings, booking_status_chain__booking_status__status='lr_generated')
        for cb in only_lr_generated_advance_not_paid_bookings_objects:
            if (cb.created_on + timedelta(minutes=time_limit)) < self.present_date:
                expired_lr_generated_advance_not_paid_bookings.append({
                    'booking_id': cb.manual_booking.booking_id,
                    'app': 'WB',
                    'aaho_office_id': cb.manual_booking.source_office.id,
                    'title_text': 'Advance Payment',
                    'functionality': 'pay_advance',
                    'is_count_update': False
                })
        send_booking_status_expired_notification(expired_lr_generated_advance_not_paid_bookings)
        return

    def booking_status_expired_advance_paid(self, time_limit):
        # expiry for reconcile
        print('Booking status expiry advance paid')
        return

    def booking_status_expired_reconciled(self, time_limit):
        print('Booking status expiry reconciled')
        return

    def booking_status_expired_unloaded(self, time_limit):
        print('Booking status expiry unloaded')
        # expiry for pod upload/delivered
        from restapi.models import BookingStatusesMapping
        from restapi.signals import send_booking_status_expired_notification
        pod_uploaded_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__in=[
                'unloaded']).exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        pod_verified_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__in=[
                'pod_uploaded', 'pod_verified', 'invoice_raised', 'invoice_confirmed',
                'balance_paid',
                'party_invoice_sent', 'inward_followup_completed']).exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        unloaded_bookings = [x for x in pod_uploaded_bookings if x not in pod_verified_bookings]
        expired_unloaded_bookings = []
        unloaded_bookings_objects = BookingStatusesMapping.objects.filter(
            manual_booking__id__in=unloaded_bookings, booking_status_chain__booking_status__status='unloaded')
        for cb in unloaded_bookings_objects:
            if cb.due_date:
                if cb.due_date < self.present_date:
                    ovedue_date_filter = True
                else:
                    ovedue_date_filter = False
            else:
                ovedue_date_filter = True

            if (cb.created_on + timedelta(minutes=time_limit)) < self.present_date and ovedue_date_filter:
                print('appending')
                expired_unloaded_bookings.append({
                    'booking_id': cb.manual_booking.booking_id,
                    'app': 'AE',
                    'aaho_office_id': cb.manual_booking.source_office.id,
                    'title_text': 'Upload PoD',
                    'functionality': 'delivered',
                    'is_count_update': False
                })
        send_booking_status_expired_notification(expired_unloaded_bookings)
        # expiry for invoice raised
        return

    def booking_status_expired_pod_uploaded(self, time_limit):
        print('Booking status expiry pod_uploaded')
        from restapi.models import BookingStatusesMapping
        from restapi.signals import send_booking_status_expired_notification
        pod_uploaded_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status='pod_uploaded'). \
            exclude(deleted=True).values_list('manual_booking_id', flat=True)
        pod_verified_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status='pod_verified'). \
            exclude(deleted=True).values_list('manual_booking_id', flat=True)
        pod_unverified_bookings = [x for x in pod_uploaded_bookings if x not in pod_verified_bookings]
        expired_pod_unverified_bookings = []
        pod_unverified_bookings_objects = BookingStatusesMapping.objects.filter(
            manual_booking__id__in=pod_unverified_bookings, booking_status_chain__booking_status__status='pod_uploaded')
        for cb in pod_unverified_bookings_objects:
            if (cb.created_on + timedelta(minutes=time_limit)) < self.present_date:
                print('appending')
                expired_pod_unverified_bookings.append({
                    'booking_id': cb.manual_booking.booking_id,
                    'app': 'WB',
                    'aaho_office_id': cb.manual_booking.source_office.id,
                    'title_text': 'Verify PoD',
                    'functionality': 'verify_pod',
                    'is_count_update': False
                })
        send_booking_status_expired_notification(expired_pod_unverified_bookings)
        return

    def booking_status_expired_pod_verified(self, time_limit):
        print('Booking status expiry pod_verified')
        # expiry for invoice raised
        from restapi.models import BookingStatusesMapping
        from restapi.signals import send_booking_status_expired_notification
        pod_verified_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='pod_verified').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        invoice_raised_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='invoice_raised').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        invoice_not_raised_bookings = [x for x in pod_verified_bookings if x not in invoice_raised_bookings]
        expired_invoice_not_raised_bookings = []
        invoice_not_raised_bookings_objects = BookingStatusesMapping.objects.filter(
            manual_booking__id__in=invoice_not_raised_bookings, booking_status_chain__booking_status__status='pod_verified')
        for cb in invoice_not_raised_bookings_objects:
            if (cb.created_on + timedelta(minutes=time_limit)) < self.present_date:
                print('appending')
                expired_invoice_not_raised_bookings.append({
                    'booking_id': cb.manual_booking.booking_id,
                    'app': 'WB',
                    'aaho_office_id': cb.manual_booking.source_office.id,
                    'title_text': 'Raise Invoice',
                    'functionality': 'raise_invoice',
                    'is_count_update': False
                })
        send_booking_status_expired_notification(expired_invoice_not_raised_bookings)
        return

    def booking_status_expired_invoice_raised(self, time_limit):
        print('Booking status expiry invoice_raised')
        # expiry for party invoice sent
        from restapi.models import BookingStatusesMapping
        from restapi.signals import send_booking_status_expired_notification
        invoice_raised_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='invoice_raised').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='party_invoice_sent').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        invoice_not_sent_bookings = [x for x in invoice_raised_bookings if x not in party_invoice_sent_bookings]

        expired_invoice_not_sent_bookings = []
        invoice_not_sent_bookings_objects = BookingStatusesMapping.objects.filter(
            manual_booking__id__in=invoice_not_sent_bookings,
            booking_status_chain__booking_status__status='invoice_raised')
        for cb in invoice_not_sent_bookings_objects:
            if (cb.created_on + timedelta(minutes=time_limit)) < self.present_date:
                print('appending')
                expired_invoice_not_sent_bookings.append({
                    'booking_id': cb.manual_booking.booking_id,
                    'app': 'WB',
                    'aaho_office_id': cb.manual_booking.source_office.id,
                    'title_text': 'Send Invoice',
                    'functionality': 'send_invoice',
                    'is_count_update': False
                })
        send_booking_status_expired_notification(expired_invoice_not_sent_bookings)
        return

    def booking_status_expired_invoice_confirmed(self, time_limit):
        print('Booking status expiry invoice_confirmed')
        # expiry for inward followup
        from restapi.models import BookingStatusesMapping, SmePaymentFollowupComments
        from restapi.signals import send_booking_status_expired_notification
        invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='invoice_confirmed').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        complete_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='inward_followup_completed').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        pending_payments_bookings = [x for x in invoice_confirmed_bookings if x not in complete_bookings]

        expired_pending_payments_bookings = []
        pending_payments_bookings_objects = BookingStatusesMapping.objects.filter(
            manual_booking__id__in=pending_payments_bookings,
            booking_status_chain__booking_status__status='invoice_confirmed')
        for cb in pending_payments_bookings_objects:
            sme_id = cb.manual_booking.customer_to_be_billed_to.id
            latest_sme_comment = SmePaymentFollowupComments.objects.filter(sme__id=sme_id, due_date__isnull=False).exclude(deleted=True).last()
            if latest_sme_comment:
                if latest_sme_comment.due_date < self.present_date.date():
                    ovedue_date_filter = True
                else:
                    ovedue_date_filter = False
            else:
                ovedue_date_filter = True
            if (cb.created_on + timedelta(minutes=time_limit)) < self.present_date and ovedue_date_filter:
                print('appending')
                expired_pending_payments_bookings.append({
                    'booking_id': cb.manual_booking.booking_id,
                    'app': 'AE',
                    'aaho_office_id': cb.manual_booking.source_office.id,
                    'title_text': 'Pending Payment',
                    'functionality': 'pending_payments',
                    'is_count_update': False
                })
        send_booking_status_expired_notification(expired_pending_payments_bookings)
        return

    def booking_status_expired_balance_paid(self, time_limit):
        # expiry for reconcile
        print('Booking status expiry balance_paid')
        return

    def booking_status_expired_party_invoice_sent(self, time_limit):
        print('Booking status expiry party_invoice_sent')
        # expiry for invoice confirmation
        from restapi.models import BookingStatusesMapping
        from restapi.signals import send_booking_status_expired_notification
        party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='party_invoice_sent').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='invoice_confirmed').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        invoice_not_confirmed_bookings = [x for x in party_invoice_sent_bookings if x not in invoice_confirmed_bookings]
        expired_invoice_not_confirmed_bookings = []
        invoice_not_confirmed_bookings_objects = BookingStatusesMapping.objects.filter(
            manual_booking__id__in=invoice_not_confirmed_bookings,
            booking_status_chain__booking_status__status='party_invoice_sent')
        for cb in invoice_not_confirmed_bookings_objects:
            if (cb.created_on + timedelta(minutes=time_limit)) < self.present_date:
                print('appending')
                expired_invoice_not_confirmed_bookings.append({
                    'booking_id': cb.manual_booking.booking_id,
                    'app': 'WB',
                    'aaho_office_id': cb.manual_booking.source_office.id,
                    'title_text': 'Confirm Invoice',
                    'functionality': 'confirm_invoice',
                    'is_count_update': False
                })
        send_booking_status_expired_notification(expired_invoice_not_confirmed_bookings)
        return

    def booking_status_expired_inward_followup_completed(self, time_limit):
        # expiry for complete
        print('Booking status expiry inward_followup_completed')
        return

    def booking_status_expired_complete(self, time_limit):
        print('Booking status expiry complete')
        return


@app.task
def notify_weekly_inquiry_report():
    columns = ['City', 'Open', 'Cancelled', 'Fulfilled', 'Unverified', 'Lapsed']
    mgmt_data = []
    mgmt_emp_emails = list(Employee.objects.filter(Q(employee_role_mapping__employee_role__role__in=['management', 'tech'])
                                        & Q(employee_role_mapping__employee_status='active')).\
        exclude(username__profile__email=None).values_list('username__profile__email', flat=True))
    city_head_emps = Employee.objects.filter(Q(employee_role_mapping__employee_role__role__in=['city_head'])
                                        & Q(employee_role_mapping__employee_status='active')).\
        exclude(username__profile__email=None)
    unique_cities = set(city_head_emps.values_list('office__branch_name', flat=True))
    total_count = 0
    for office in AahoOffice.objects.all():
        inquiry_city_count = []
        inquiries = Requirement.objects.filter(Q(
            from_shipment_date__gte=(datetime.datetime.now().date() - timedelta(days=7))) & Q(aaho_office=office)).exclude(deleted=True)
        inquiry_row = [
            office.branch_name,
            inquiries.filter(req_status='open').count(),
            inquiries.filter(req_status='cancelled').count(),
            inquiries.filter(req_status='fulfilled').count(),
            inquiries.filter(req_status='unverified').count(),
            inquiries.filter(req_status='lapsed').count()
        ]
        inquiry_city_count.append(inquiry_row)
        mgmt_data.append(inquiry_row)
        if office.branch_name in unique_cities:
            each_city_head_emails = list(city_head_emps.filter(office__branch_name=office.branch_name).values_list('username__profile__email', flat=True))
            df = pd.DataFrame(data=inquiry_city_count, columns=columns)
            send_inquiry_status_emails(df, inquiries.count(), inquiry_city_count, each_city_head_emails)
        total_count += inquiries.count()
    df = pd.DataFrame(data=mgmt_data, columns=columns)
    send_inquiry_status_emails(df, total_count, mgmt_data, mgmt_emp_emails)


def send_inquiry_status_emails(df, total_inquiries_count, inquiries_list_count, email_ids):
    string_io = StringIO()
    df.to_csv(string_io, index=False)
    filename = 'Inquiry_status_' + datetime.datetime.now().strftime('%d%b%Y%I%M') + '.csv'
    s3_upload = save_to_s3_weekly_inquiry_report(filename, string_io.getvalue())
    s3_url = s3_upload.public_url()
    subject = '[Aaho] Weekly Inquiry Status Report for ' + (datetime.datetime.now().date()).strftime('%d-%b-%Y')
    body = get_template('team/emails/weekly_inquiries.html').render(context={'inq_counts': total_inquiries_count,
                                                                             'inquiries': inquiries_list_count,
                                                                             's3_url': s3_url})
    email = EmailMessage(subject, body,
                         to=email_ids)
    email.content_subtype = 'html'
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


@app.task
def send_customer_welcome_email(sme_id):
    sme = get_or_none(Sme, id=sme_id)
    if not isinstance(sme, Sme):
        return
    client = get_client()
    s3_obj1 = client.get_object(Bucket='aahodocuments', Key='company_docs/PAN Card.jpg')
    s3_obj2 = client.get_object(Bucket='aahodocuments', Key='company_docs/Trans IQ TDS Declaration FY18-19.pdf')
    s3_obj3 = client.get_object(Bucket='aahodocuments', Key='company_docs/Udyog Aadhaar Acknowledgement.xps')

    subject = 'Welcome to Aaho Trucking!'
    body = get_template('team/emails/customer_welcome_email_template.html').render(context={'customer_cp': to_int(sme.credit_period)})

    email = EmailMessage(subject, body, to=[sme.sme_email])
    email.content_subtype = 'html'
    email.attach('PAN Card.jpg', s3_obj1['Body'].read(), "application/jpeg")
    email.attach('Trans IQ TDS Declaration FY18-19.pdf', s3_obj2['Body'].read(), "application/pdf")
    email.attach('Udyog Aadhaar Acknowledgement.xps', s3_obj3['Body'].read(), "application/oxps")

    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()