from datetime import datetime, timedelta, date
from io import StringIO

import pandas as pd
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.db.models import Q, F
from django.template.loader import get_template

from api.models import S3Upload
from api.s3util import save_to_s3_daily_sales_report
from api.sms import send_sms
from api.sms_template import delayed_pod_warning_message
from api.utils import get_or_none, to_str
from authentication.models import Profile
from broker.models import Broker
from driver.crawl_gps.tempogo import update_tempogo_devices_locations
from driver.mahindra import mahindra_digisense_location_services
from driver.secugps import secugps_device_log_updates
from employee.models import TaskEmail, Employee
from owner.models import Vehicle
from owner.vehicle_util import compare_format
from sme.models import Sme
from supplier.models import Supplier
from team.helper.helper import to_int, get_email_list, dest_sms_employee_mobiles, manual_booking_id_list, \
    weekly_status_email_id_list
from team.helper_tasks import get_invoice_customers_email_data, get_customers_dispatched_shipment_email_data, \
    notify_admins_about_to_pay_booking_data, notify_weekly_partial_tbb_data, vehicle_booking_summary_data, \
    supplier_booking_summary_data, notify_excess_outward_payment_data
from team.models import ManualBooking, OutWardPayment, InWardPayment, NotifyCompletedTaskEmail, LrNumber, \
    ManualBookingSummary, BookingStatusColor
from team.payments.accounting import supplier_accounting_summary, vehicle_accounting_summary, \
    billed_customer_accounting_summary, placed_order_accounting_summary
from transiq.celery import app
from utils.models import AahoOffice, Bank


@app.task
def email_lr(booking_id):
    booking = ManualBooking.objects.get(id=booking_id)
    lr_list = booking.lr_numbers.values_list('lr_number', flat=True)
    lr_number = ', '.join(lr_list)
    from_city = booking.from_city_fk.name if booking.from_city_fk else ''
    to_city = booking.to_city_fk.name if booking.to_city_fk else ''
    subject = 'LR(s) ' + lr_number + ' for ' + from_city + ' to ' + to_city + ' ' + booking.shipment_date.strftime(
        '%d-%b-%Y') if booking.shipment_date else ''
    body = 'PFA'

    to_email_list = get_email_list(booking, task_id=3)
    email = EmailMessage(subject, body, 'AAHO LR', to=to_email_list)
    for lr in booking.lr_numbers.all():
        s3_uploads = S3Upload.objects.filter(folder='lr', filename__iexact='{}.pdf'.format(lr.lr_number)).exclude(
            deleted=True, uploaded=False)
        if s3_uploads.exists():
            s3_upload = s3_uploads.last()
            email.attach(s3_upload.filename, s3_upload.read(), "application/pdf")
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


@app.task
def update_fms_booking_summary(user_id):
    for booking in ManualBooking.objects.filter(supplier__name__id=user_id).exclude(
            Q(booking_status='cancelled') | Q(deleted=True)):
        pass
    pass


@app.task
def email_commission_booking(booking_id):
    booking = ManualBooking.objects.get(id=booking_id)
    from_city = booking.from_city
    to_city = booking.to_city
    vehicle_number = booking.supplier_vehicle.number() if booking.supplier_vehicle else ''
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


@app.task
def email_outward_payment(payment_id):
    if settings.TESTING:
        return
    payment = OutWardPayment.objects.get(id=payment_id)
    booking_data = payment.booking_id.all().first()
    booking_id = '' if not booking_data else booking_data.booking_id
    paid_to = payment.paid_to
    actual_amount = str(payment.actual_amount)
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
    paid_amount = str(to_int(paid_amount))
    if payment.bank_account:
        body = "LR No(s)    : " + lr_number + '\nPaid To      : ' + payment.paid_to + '\nAccount Holder Name: ' + payment.bank_account.account_holder_name + '\nAccount Number: ' + payment.bank_account.account_number + '\nAmount      : ' + actual_amount + '\nMode         : ' + payment_mode + "\nDate           : " + payment_date + "\nRemarks    : " + remarks + '\nVehicle Number   :' + booking_data.supplier_vehicle.number() if booking_data.supplier_vehicle else '' + "\n\n" + "Payments made for " + booking_id + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + booking_id + ": Rs. " + str(
            booking_data.total_amount_to_owner) + '\nPOD Status:  ' + booking_data.get_pod_status_display() + '\nVehicle Number' + booking_data.supplier_vehicle.number() if booking_data.supplier_vehicle else ''
    elif payment.fuel_card:
        body = "LR No(s)    : " + lr_number + '\nPaid To      : ' + paid_to + '\nFuel Card Number: ' + payment.fuel_card.card_number + '\nAmount      : ' + actual_amount + '\nMode         : ' + payment_mode + "\nDate           : " + payment_date + "\nRemarks    : " + remarks + '\nVehicle Number   :' + booking_data.supplier_vehicle.number() if booking_data.supplier_vehicle else '' + "\n\n" + "Payments made for " + booking_id + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + booking_id + ": Rs. " + str(
            booking_data.total_amount_to_owner) + '\nPOD Status:  ' + booking_data.get_pod_status_display()
    else:
        body = "LR No(s)    : " + str(lr_number) + '\nPaid To      : ' + str(
            paid_to) + '\nAmount      : ' + actual_amount + '\nMode         : ' + payment.get_payment_mode_display() + "\nDate           : " + payment_date + "\nRemarks    : " + str(
            remarks) + '\nVehicle Number   :' +booking_data.supplier_vehicle.number() if booking_data.supplier_vehicle else '' + "\n\n" + "Payments made for " + str(
            booking_id) + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + str(booking_id) + ": Rs. " + str(
            booking_data.total_amount_to_owner) + '\nPOD Status:  ' + booking_data.get_pod_status_display()

    to_email_list = get_email_list(booking_data)

    # email = EmailMessage(subject, body, 'AAHO OUTWARD PAYMENT', to=['mani@aaho.in'])
    email = EmailMessage(subject, body, 'AAHO OUTWARD PAYMENT', to=to_email_list)
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


@app.task
def sms_outward_payment(payment_id):
    payment = get_or_none(OutWardPayment, id=payment_id)
    if isinstance(payment, OutWardPayment):
        try:
            lr_numbers = ','.join([','.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in
                                   payment.booking_id.all()])
            mobiles = ', '.join(
                [booking.accounting_supplier.phone if booking.supplier else '' for booking in payment.booking_id.all()])
            if mobiles:

                payment_mode = to_str(payment.payment_mode)
                amount = str(int(payment.actual_amount))
                lorry_number = to_str(payment.lorry_number)
                payment_date = payment.payment_date.strftime('%d-%b-%Y') if isinstance(payment.payment_date,
                                                                                       date) else ''
                if payment_mode in ['neft', 'imps', 'rtgs', 'hdfc_internal_account']:
                    payment_type = 'NEFT'
                elif payment_mode in ['cash', 'happay']:
                    payment_type = 'Cash'
                elif payment_mode is 'fuel_card':
                    payment_type = 'Fuel Card'
                elif payment_mode is 'cheque':
                    payment_type = 'Cheque'
                else:
                    payment_type = payment_mode
                if lr_numbers:
                    msg = "Rs. " + amount + ' will be paid on ' + payment_date + ' by ' + payment_type + " for your truck " + lorry_number + " for LR no. " + lr_numbers
                else:
                    msg = "Rs. " + amount + ' will be paid on ' + payment_date + ' by ' + payment_type + " for your truck " + lorry_number
                send_sms(mobiles, msg)
        except TypeError:
            raise


@app.task
def email_accounts_last_day_payments():
    inward_payments = InWardPayment.objects.filter(payment_mode__in=['happay', 'cash']).filter(
        created_on__date=datetime.today() - timedelta(days=1))

    outward_payments = OutWardPayment.objects.filter(payment_mode__in=['happay', 'cash']).filter(
        created_on__date=datetime.today() - timedelta(days=1))
    context = {'outward_payments': outward_payments, 'inward_payments': inward_payments}
    subject = '[Aaho]  Cash/Happay Payments' + (datetime.today() - timedelta(days=1)).strftime('%d-%b-%Y')
    body = get_template('team/emails/last_day_payments.html').render(context=context)

    email = EmailMessage(subject, body, to=['harsh@aaho.in', 'accounts@aaho.in'])
    email.content_subtype = 'html'
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()
    from restapi.service.tallyintegration import cash_payments, fuel_card_payment
    cash_payments()
    fuel_card_payment()


@app.task
def email_updated_outward_payment(booking_id, payment_id, old_amount, new_amount):
    payment = OutWardPayment.objects.get(id=payment_id)
    booking_data = ManualBooking.objects.get(booking_id=booking_id)
    paid_to = payment.paid_to
    payment_mode = payment.get_payment_mode_display()
    remarks = payment.remarks
    payment_date = '' if not payment.payment_date else payment.payment_date.strftime('%d-%b-%Y')
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
        body = "LR No(s)    : " + lr + '\nPaid To      : ' + payment.paid_to + '\nAccount Holder Name: ' + payment.bank_account.account_holder_name + '\nPrevious Amount      : ' + old_amount + '\nUpdated Amount      : ' + new_amount + '\nMode         : ' + payment_mode + "\nDate           : " + payment_date + "\nRemarks    : " + remarks + '\nVehicle Number   :' + booking_data.supplier_vehicle.number() if booking_data.supplier_vehicle else '' + "\n\n" + "Payments made for " + booking_id + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + booking_id + ": Rs. " + str(
            booking_data.total_amount_to_owner) + '\nPOD Status:  ' + booking_data.get_pod_status_display() + '\nPOD Status:  ' + booking_data.get_pod_status_display()
    elif payment.fuel_card:
        body = "LR No(s)    : " + lr + '\nPaid To      : ' + paid_to + '\nFuel Card Number: ' + payment.fuel_card.card_number + '\nPrevious Amount      : ' + old_amount + '\nUpdated Amount      : ' + new_amount + '\nMode         : ' + payment_mode + "\nDate           : " + payment_date + "\nRemarks    : " + remarks + '\nVehicle Number   :' + booking_data.supplier_vehicle.number() if booking_data.supplier_vehicle else '' + "\n\n" + "Payments made for " + booking_id + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + booking_id + ": Rs. " + str(
            booking_data.total_amount_to_owner) + '\nPOD Status:  ' + booking_data.get_pod_status_display() + '\nPOD Status:  ' + booking_data.get_pod_status_display()
    else:
        body = "LR No(s)    : " + lr + '\nPaid To      : ' + paid_to + '\nPrevious Amount      : ' + old_amount + '\nUpdated Amount      : ' + new_amount + '\nMode         : ' + payment.get_payment_mode_display() + "\nDate           : " + payment_date + "\nRemarks    : " + remarks + '\nVehicle Number   :' + booking_data.supplier_vehicle.number() if booking_data.supplier_vehicle else '' + "\n\n" + "Payments made for " + booking_id + ": Rs. " + str(
            paid_amount) + "\nTotal amount to owner for " + booking_id + ": Rs. " + str(
            booking_data.total_amount_to_owner) + '\nPOD Status:  ' + booking_data.get_pod_status_display() + '\nPOD Status:  ' + booking_data.get_pod_status_display()

    to_email_list = get_email_list(booking_data)
    email = EmailMessage(subject, body, 'AAHO OUTWARD PAYMENT', to=to_email_list)
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


@app.task
def send_commission_booking_sms(message, mobiles):
    send_sms(message=message, mobiles=mobiles)


@app.task
def full_booking_sms_customer(booking_id):
    mb = ManualBooking.objects.get(id=booking_id)
    lr_list = ', '.join(mb.lr_numbers.values_list('lr_number', flat=True))
    try:
        sme = Sme.objects.get(id=mb.company_id)
        sme_phone = sme.name.profile.phone if sme else ''
    except Sme.DoesNotExist:
        sme_phone = ''
    mobiles = sme_phone if sme_phone else '8978937498'
    if len(lr_list) > 1:
        msg = "Vehicle number " + mb.supplier_vehicle.number() if mb.supplier_vehicle else '' + " has been assigned for trip from " + mb.from_city + " to " + mb.to_city + ", with loading date " + str(
            mb.shipment_date.strftime('%d-%b-%y')) + ". LR numbers are " + lr_list + "."
    else:
        msg = "Vehicle number " + mb.supplier_vehicle.number() if mb.supplier_vehicle else '' + " has been assigned for trip from " + mb.from_city + " to " + mb.to_city + ", with loading date " + str(
            mb.shipment_date.strftime('%d-%b-%y')) + ". LR number is " + lr_list + "."

    msg = ' '.join([msg, 'The capacity of this truck is approximately', vehicle_capacity(mb.supplier_vehicle.vehicle_capacity if mb.supplier_vehicle else ''), '.'])
    send_sms(mobiles, msg)


@app.task
def tracking_sms_customer(booking_id):
    mb = ManualBooking.objects.get(id=booking_id)
    lr_list = ', '.join(mb.lr_numbers.values_list('lr_number', flat=True))
    try:
        sme = Sme.objects.get(id=mb.company_id)
        sme_phone = sme.name.profile.phone if sme else ''
    except Sme.DoesNotExist:
        sme_phone = ''
    mobiles = sme_phone if sme_phone else '8978937498'
    msg = 'You can track the progress of your shipment number {} on our website www.aaho.in.'.format(lr_list)
    send_sms(mobiles, msg)


def vehicle_capacity(vehicle_number):
    try:
        vehicle = Vehicle.objects.get(vehicle_number=compare_format(vehicle_number))
        if vehicle.vehicle_type:
            if vehicle.vehicle_type.capacity:
                return vehicle.vehicle_type.capacity
        return ''
    except Vehicle.DoesNotExist:
        return ''


@app.task
def full_booking_sms_employee(booking_id):
    mb = ManualBooking.objects.get(id=booking_id)
    veh = Vehicle.objects.get(vehicle_number=compare_format(mb.supplier_vehicle.number() if mb.supplier_vehicle else ''))
    lr_list = ', '.join(mb.lr_numbers.values_list('lr_number', flat=True))
    msg = mb.supplier_vehicle.number() if mb.supplier_vehicle else '' + " Driver no." + mb.driver_phone + ' placed from ' + mb.from_city + " to " + mb.to_city + " on " + str(
        mb.shipment_date.strftime('%d-%b-%y')) + ". LR numbers are " + lr_list + "."
    send_sms(mobiles=dest_sms_employee_mobiles(booking=mb), message=msg)


@app.task
def commission_booking_sms_customer(booking_id):
    booking = ManualBooking.objects.get(id=booking_id)
    if booking.company:
        sme_phone = '' if not booking.company.name.profile else booking.company.name.profile.phone
    else:
        sme_phone = ''
    mobiles = sme_phone if sme_phone else '8978937498'
    msg = "Vehicle number " + booking.supplier_vehicle.number() if booking.supplier_vehicle else '' + " has been assigned for trip from " + booking.from_city + " to " + booking.to_city + ", with loading date " + str(
        booking.shipment_date.strftime('%d-%b-%y'))
    send_sms(message=msg, mobiles=mobiles)


@app.task
def commission_booking_sms_employee(booking_id):
    mb = ManualBooking.objects.get(id=booking_id)
    msg = mb.supplier_vehicle.number() if mb.supplier_vehicle else '' + " Driver no." + mb.driver_phone + ' placed from ' + mb.from_city + " to " + mb.to_city + " on " + str(
        mb.shipment_date.strftime('%d-%b-%y')) + "."
    send_sms(mobiles=dest_sms_employee_mobiles(booking=mb), message=msg)


# run daily at 9 PM
@app.task
def notify_admins_about_pending_pod():
    booking_ids = manual_booking_id_list('mani@aaho.in',
                                         user_group_list=['emp_group1'])
    for office in AahoOffice.objects.all():
        mb = ManualBooking.objects.filter(
            Q(destination_office=office) & Q(id__in=booking_ids) & Q(
                pod_status='pending') & Q(shipment_date__gte='2017-01-01')
        ).exclude(
            Q(total_in_ward_amount__gte=F('total_amount_to_company') - F('tds_deducted_amount')) & Q(
                total_out_ward_amount__exact=F('total_amount_to_owner')) | Q(booking_status='cancelled')
        ).select_related(
            'company__name__profile'
        ).prefetch_related(
            'lr_numbers'
        ).exclude(
            booking_status='cancelled'
        ).order_by('shipment_date')

        if mb:
            subject = '[Aaho] Daily POD Pending Status Update for ' + office.branch.name + ' office till ' + datetime.today().strftime(
                '%d-%b-%Y %I:%M')
            body = get_template('team/emails/pod_status.html').render(context={'mb': mb})
            email_ids = weekly_status_email_id_list(aaho_office_id=office.id)
            email = EmailMessage(subject, body, to=email_ids)
            email.content_subtype = 'html'
            if settings.ENABLE_MAIL and not settings.TESTING:
                email.send()


# run daily at 09:05 PM
@app.task
def notify_admins_about_to_pay_booking():
    for data in notify_admins_about_to_pay_booking_data():
        if data['number_of_open_booking'] > 0:
            subject = '[Aaho] Weekly To Pay Booking Status Update for ' + data[
                'branch_name'] + ' office till ' + datetime.today().strftime(
                '%d-%b-%Y %I:%M')
            body = get_template('team/emails/notify_to_pay_booking_updates.html').render(context=data)
            email = EmailMessage(subject, body, to=data['email_id_list'])
            # email = EmailMessage(subject, body, to=['mani@aaho.in'])
            email.content_subtype = 'html'
            if settings.ENABLE_MAIL and not settings.TESTING:
                email.send()


@app.task
def notify_pod_received_invoice_not_raised():
    for office in AahoOffice.objects.all():
        mb = ManualBooking.objects.filter(
            (Q(source_office=office) | Q(destination_office=office))
            & Q(pod_status='completed') & Q(invoice_status='no_invoice')
            & Q(shipment_date__gte='2017-01-01')
        ).exclude(
            Q(booking_status='cancelled') | Q(total_amount_to_company=0)
        ).order_by(
            'shipment_date'
        )
        if mb:
            subject = '[Aaho] Unraised Invoices for {} Office till {} '.format(
                office.branch.name, datetime.today().strftime('%d-%b-%Y %I:%M'))
            body = get_template('team/emails/notify_pod_received_invoice_not_raised.html').render(context={'mb': mb})
            email_ids = weekly_status_email_id_list(aaho_office_id=office.id)
            email = EmailMessage(subject, body, to=email_ids, cc=['accounts@aaho.in'])
            email.content_subtype = 'html'
            if settings.ENABLE_MAIL and not settings.TESTING:
                email.send()


@app.task
def notify_weekly_partial_tbb():
    for data in notify_weekly_partial_tbb_data():
        if data['number_of_open_booking'] > 0:
            subject = '[Aaho] Weekly TBB Booking Status Update for ' + data[
                'branch_name'] + ' office till ' + datetime.today().strftime(
                '%d-%b-%Y %I:%M')
            body = get_template('team/emails/weekly_tbb_booking_update.html').render(context=data)
            email = EmailMessage(subject, body, to=data['email_id_list'])
            # email = EmailMessage(subject, body, to=['mani@aaho.in'])
            email.content_subtype = 'html'
            if settings.ENABLE_MAIL and not settings.TESTING:
                email.send()


# Tues Friday 8:05
@app.task
def notify_outward_payment_status():
    for office in AahoOffice.objects.all():
        mb = ManualBooking.objects.filter(
            Q(source_office=office)
            & Q(pod_status='completed')
            & Q(total_amount_to_owner__gt=F('total_out_ward_amount'))
            & Q(shipment_date__gte='2017-01-01')
        ).exclude(
            Q(total_in_ward_amount__gte=F('total_amount_to_company') - F('tds_deducted_amount')) & Q(
                total_out_ward_amount__exact=F('total_amount_to_owner')) | Q(booking_status='cancelled')
        ).order_by(
            '-shipment_date'
        )
        if mb:
            obj = NotifyCompletedTaskEmail.objects.create(task='notify_outward_payment_status', office=office)
            for booking in mb:
                obj.bookings.add(booking)
            subject = '[Aaho] Daily Outward Status Update for ' + office.branch.name + ' office till ' + datetime.today().strftime(
                '%d-%b-%Y %I:%M')
            body = get_template('team/emails/outward_payment_status.html').render(context={'mb': mb})
            email_ids = weekly_status_email_id_list(aaho_office_id=office.id)
            email = EmailMessage(subject, body, to=email_ids)
            email.content_subtype = 'html'
            if settings.ENABLE_MAIL and not settings.TESTING:
                email.send()


@app.task
def notify_daily_sales_report():
    from restapi.models import BookingStatusesMapping
    bookings_id = BookingStatusesMapping.objects.filter(
        created_on__date=datetime.now().date() - timedelta(days=1),
        booking_status_chain__booking_status__status='lr_generated').values_list('manual_booking_id', flat=True)
    mb = ManualBooking.objects.filter(Q(id__in=bookings_id) | (Q(booking_id__istartswith='AB') & Q(
        created_on__date=datetime.now().date() - timedelta(days=1)))).exclude(
        booking_status='cancelled').order_by('-id', '-shipment_date')
    if mb.exists():
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
                    booking.total_amount_to_company - booking.total_amount_to_owner - booking.refund_amount,
                    booking.refund_amount,
                    "{0:.2f}".format(((
                                              booking.total_amount_to_company - booking.total_amount_to_owner - booking.refund_amount) / booking.total_amount_to_owner) * 100)
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
                    booking.total_amount_to_company - booking.total_amount_to_owner - booking.refund_amount,
                    booking.refund_amount,
                    'Amount to owner is zero'
                ])

        df = pd.DataFrame(data=data,
                          columns=['Booking ID', 'LR Number(s)', 'From City', 'To City', 'Party Rate', 'Party Weight',
                                   'Party Amount', 'Supplier Rate', 'Supplier Weight', 'Supplier Amount', 'Profit',
                                   'Refund', '% Profit'])
        string_io = StringIO()
        df.to_csv(string_io, index=False)
        filename = datetime.now().strftime('%d%b%Y%I%M') + '.csv'
        s3_upload = save_to_s3_daily_sales_report(filename, string_io.getvalue())
        s3_url = s3_upload.public_url()
        subject = '[Aaho] Daily Sales Report for ' + (datetime.now().date() - timedelta(days=1)).strftime(
            '%d-%b-%Y')
        body = get_template('team/emails/last-day-bookings.html').render(context={'mb': mb, 's3_url': s3_url})
        task = TaskEmail.objects.get(id=26)
        email_id_list = list(
            task.employee.exclude(username__profile__email=None).values_list('username__profile__email', flat=True))
        email = EmailMessage(subject, body,
                             to=email_id_list)
        email.content_subtype = 'html'
        if settings.ENABLE_MAIL and not settings.TESTING:
            email.send()


@app.task
def update_tempogo_gps_locations():
    update_tempogo_devices_locations()


@app.task
def update_secugps_locations():
    secugps_device_log_updates()


@app.task
def update_bharat_gps_tracker_locations():
    from driver.crawl_gps.bharat_gps import update_bharat_gps_tracker_log
    update_bharat_gps_tracker_log()


@app.task
def landing_page_enquiry(msg):
    email = EmailMessage(subject="Landing Page Enquiry {}".format(datetime.now().strftime('%d-%b-%Y %H:%M')), body=msg,
                         to=['info@aaho.in'])
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


@app.task
def update_mahindra_digisense_locations():
    mahindra_digisense_location_services()


@app.task
def notify_invoice_customers_email():
    for data in get_invoice_customers_email_data():
        if data['enable_email']:
            subject = 'New Freight Invoice(s) from Trans IQ Technologies ({})'.format(data['invoice_created_on'])
            body = get_template('team/emails/notify_invoice_customers_email.html').render(context=data)
            email_ids = data['email_id_list']
            email = EmailMessage(subject, body, to=email_ids, cc=['accounts@aaho.in'])
            # email = EmailMessage(subject, body, to=['mani@aaho.in', 'harsh@aaho.in', 'pankaj@aaho.in', 'rohit@aaho.in'])
            email.content_subtype = 'html'
            for pod in data['pod_files']:
                email.attach(pod.filename, pod.read(), "application/jpeg")
            for inv in data['invoices_file']:
                email.attach(inv.filename, inv.read(), "application/pdf")
            if settings.ENABLE_MAIL and not settings.TESTING:
                email.send()


@app.task
def notify_customers_dispatched_shipment_email():
    for data in get_customers_dispatched_shipment_email_data():
        if data['enable_email']:
            subject = 'Dispatch details for {}'.format(data['dispatch_date'])
            body = get_template('team/emails/notify_customer_dispatch_details.html').render(context=data)
            email_ids = data['email_id_list']
            email = EmailMessage(subject, body, to=email_ids)
            # email = EmailMessage(subject, body, to=['mani@aaho.in', 'harsh@aaho.in', 'pankaj@aaho.in', 'rohit@aaho.in'])
            email.content_subtype = 'html'
            if settings.ENABLE_MAIL and not settings.TESTING:
                email.send()


@app.task
def notify_excess_outward_payment():
    from restapi.models import EmployeeRolesMapping
    bookings = ManualBooking.objects.filter(outward_payment_status='excess', total_amount_to_owner__gt=10).exclude(
        booking_status='cancelled').order_by('shipment_date')

    data = notify_excess_outward_payment_data(bookings)
    if len(data) > 0:
        email_list = list(set(
            list(EmployeeRolesMapping.objects.filter(
                employee_role__role__in=['management'], employee_status='active').values_list(
                'employee__username__profile__email', flat=True))))

        subject = 'Excess outward payments till {}'.format(
            (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y'))
        body = get_template('team/emails/excess-outward-payment.html').render(
            context={'bookings': data, 'email_list': email_list})
        email = EmailMessage(subject, body, to=email_list)
        # email = EmailMessage(subject, body, to=['mani@aaho.in','harsh@aaho.in'])
        email.content_subtype = 'html'
        if settings.ENABLE_MAIL and not settings.TESTING:
            email.send()
    employees_id = list(set(list(
        EmployeeRolesMapping.objects.filter(
            employee_role__role__in=['city_head', 'traffic', 'office_data_entry'],
            employee_status='active').values_list('employee_id', flat=True))))

    for employee in Employee.objects.filter(id__in=employees_id).exclude(status='inactive').exclude(
            username__profile__email=None):
        data = notify_excess_outward_payment_data(bookings.filter(source_office__in=employee.office_multiple.all()))
        if len(data) > 0:

            subject = 'Excess outward payments till {}'.format(
                (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y'))
            body = get_template('team/emails/excess-outward-payment.html').render(
                context={'bookings': data, 'email_list': [employee.emp_email]})
            email = EmailMessage(subject, body, to=[employee.emp_email])
            # email = EmailMessage(subject, body, to=['mani@aaho.in', 'harsh@aaho.in'])
            email.content_subtype = 'html'
            if settings.ENABLE_MAIL and not settings.TESTING:
                email.send()


'''
SME TASKS EMAIL
'''


@app.task
def delayed_pod_warning_sms_supplier():
    lr_numbers = LrNumber.objects.filter(booking__shipment_date__in=[
        datetime.today() - timedelta(days=7),
        datetime.today() - timedelta(days=15),
    ]).exclude(
        Q(booking__pod_status='completed') | (Q(booking__source_office_id__in=[2, 3, 8])))
    for lr in lr_numbers:
        if settings.ENABLE_SMS:
            msg = delayed_pod_warning_message(
                lr_number=lr.lr_number,
                shipment_date=lr.booking.shipment_date.strftime('%d-%b'),
                vehicle_number=lr.booking.supplier_vehicle.number() if lr.booking.supplier_vehicle else ''
            )
            send_sms(mobiles=lr.booking.truck_broker_owner_phone, message=msg)


@app.task
def daily_rds_backup():
    import os
    # os.system('pwd')
    os.system('sudo chmod 777 ../config/ci/prod/rds_backup.sh')
    os.system('sudo sh ../config/ci/prod/rds_backup.sh')


@app.task
def email_add_new_beneficiary(bank_id):
    bank = get_or_none(Bank, id=bank_id)
    if isinstance(bank, Bank):
        subject = "New Beneficiary Account Added"
        body = "\n Beneficiary Code: " + bank.beneficiary_code + "\n Account Holder Name: " + bank.account_holder_name + "\n Account Number: " + bank.account_number + "\n IFSC Code: " + bank.ifsc + "\n Account Type: " + bank.get_account_type_display() + "\n Transaction Type: " + bank.get_transaction_type_display() + "\n Bank Name: " + bank.bank + "\n Address: " + bank.address + "\n City: " + bank.city
        email_address = list(
            TaskEmail.objects.filter(task__name='new_beneficiary').last().employee.values_list(
                'username__profile__email',
                flat=True))
        email = EmailMessage(subject, body, 'NEW BENEFICIARY ACCOUNT', to=email_address)
        if settings.ENABLE_MAIL and not settings.TESTING:
            email.send()
    return


def inward_payment_status(booking):
    if isinstance(booking, ManualBooking):
        if to_int(booking.amount_received_from_customer) == 0:
            return 'no_payment'
        elif 0 < to_int(booking.amount_received_from_customer) < booking.customer_amount:
            return 'partial_received'
        elif to_int(booking.amount_received_from_customer) == to_int(booking.customer_amount):
            return 'full_received'
        elif to_int(booking.amount_received_from_customer) > to_int(booking.customer_amount):
            return 'excess'
        else:
            return None
    return None


def outward_payment_status(booking):
    if isinstance(booking, ManualBooking):
        if to_int(booking.amount_paid_to_supplier) == 0:
            return 'no_payment_made'
        elif 0 < to_int(booking.amount_paid_to_supplier) < to_int(booking.supplier_amount):
            return 'partial'
        elif to_int(booking.amount_paid_to_supplier) == to_int(booking.supplier_amount):
            return 'complete'
        elif to_int(booking.amount_paid_to_supplier) > to_int(booking.supplier_amount):
            return 'excess'
        else:
            return None
    return None


@app.task
def update_accounting_summary(customer_id=None, vehicle_id=None, supplier_id=None):
    placed_order_accounting_summary(sme_id=customer_id)
    billed_customer_accounting_summary(sme_id=customer_id)


@app.task
def save_manual_booking_data(id):
    booking = get_or_none(ManualBooking, id=id)
    print('Saving Booking Id:', id)
    if isinstance(booking, ManualBooking):
        ManualBooking.objects.filter(id=booking.id).update(
            total_amount_to_company=booking.customer_amount,
            total_amount_to_owner=booking.supplier_amount,
            total_in_ward_amount=booking.inward_amount,
            total_out_ward_amount=booking.outward_amount,
            tds_deducted_amount=booking.tds_amount_customer,
            inward_payment_status=inward_payment_status(booking=booking),
            outward_payment_status=outward_payment_status(booking=booking)
        )
        booking = get_or_none(ManualBooking, id=id)
        if booking.total_amount_to_company == 0:
            color_code = get_or_none(BookingStatusColor, keyword='zblue')
        elif booking.balance_for_customer <= 0:
            color_code = get_or_none(BookingStatusColor, keyword='zgreen')
        elif booking.pod_status == 'completed' and booking.invoice_status == 'no_invoice':
            color_code = get_or_none(BookingStatusColor, keyword='zorange')
        elif booking.pod_status == 'completed' and booking.invoice_status == 'invoice_raised':
            color_code = get_or_none(BookingStatusColor, keyword='zpurple')
        elif booking.pod_status == 'completed' and booking.invoice_status in ['invoice_sent', 'invoice_confirmed']:
            color_code = get_or_none(BookingStatusColor, keyword='zpurple')
        elif booking.pod_status != 'completed':
            color_code = get_or_none(BookingStatusColor, keyword='zred')
        else:
            color_code = get_or_none(BookingStatusColor, keyword='zblack')
        print('Color code Save Booking Id:', id)
        if isinstance(booking.company, Sme):
            placed_order_accounting_summary(sme_id=booking.company_id)
            print('placed_order_accounting_summary Save Booking Id:', id)
        if isinstance(booking.company, Sme):
            billed_customer_accounting_summary(sme_id=booking.customer_to_be_billed_to_id)
            print('billed_customer_accounting_summary Save Booking Id:', id)
        ManualBooking.objects.filter(id=booking.id).update(booking_status_color=color_code)
        print('Saved Booking Id:', id)
        if booking.inward_payment_status == 'full_received':
            from restapi.helper_api import check_booking_status, create_new_booking_status, update_booking_status
            booking_pod_uploaded = check_booking_status(booking, 'complete')
            if not booking_pod_uploaded:
                create_new_booking_status(booking, 'complete', User.objects.get(username='admin'))
            else:
                update_booking_status(booking, 'complete ', 'in_progress', User.objects.get(username='admin'))
        if booking.outward_payment_status == 'complete' or booking.outward_payment_status == 'excess':
            from restapi.helper_api import check_booking_status, create_new_booking_status, update_booking_status
            booking_balance_paid = check_booking_status(booking, 'balance_paid')
            if not booking_balance_paid:
                create_new_booking_status(booking, 'balance_paid', User.objects.get(username='admin'))
            else:
                update_booking_status(booking, 'balance_paid ', 'in_progress', User.objects.get(username='admin'))
        print('Task Completed Booking Id:', id)
    else:
        print('Instance Not Found for Booking Id:', id)


@app.task
def update_booking_summary(mb_id):
    from supplier.models import Vehicle
    booking = get_or_none(ManualBooking, id=mb_id)
    if isinstance(booking, ManualBooking):

        if isinstance(booking.accounting_supplier, Supplier) and isinstance(booking.accounting_supplier.user, User):
            supplier_accounting_summary(booking.accounting_supplier)
        if isinstance(booking.booking_supplier, Supplier) and isinstance(booking.booking_supplier.user, User):
            user_id = booking.booking_supplier.user_id
            data = supplier_booking_summary_data(user_id=user_id)
            try:
                mbs = ManualBookingSummary.objects.get(user_id=user_id)
                mbs.summary = data
                mbs.save()
            except ManualBookingSummary.DoesNotExist:
                ManualBookingSummary.objects.create(user_id=user_id, summary=data)
        if isinstance(booking.supplier_vehicle, Vehicle):
            vehicle_accounting_summary(booking.supplier_vehicle)
            supplier_vehicle_id = booking.supplier_vehicle_id
            user_id = booking.booking_supplier.user_id if booking.booking_supplier else -1
            data = vehicle_booking_summary_data(user_id=user_id, vehicle_id=supplier_vehicle_id)
            try:
                mbs = ManualBookingSummary.objects.get(supplier_vehicle=booking.supplier_vehicle)
                mbs.summary = data
                mbs.save()
            except ManualBookingSummary.DoesNotExist:
                ManualBookingSummary.objects.create(supplier_vehicle=booking.supplier_vehicle, summary=data)


@app.task
def daily_dump():
    from utils.data import s3_dump_full_booking_excel, s3_dump_outward_payment_excel, s3_dump_inward_payment_excel, \
        s3_dump_invoice_excel
    s3_dump_full_booking_excel()
    s3_dump_outward_payment_excel()
    s3_dump_inward_payment_excel()
    s3_dump_invoice_excel()
