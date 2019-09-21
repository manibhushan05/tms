from datetime import date, datetime, timedelta

from django.db.models import Q, F
from django.shortcuts import render

from api.models import S3Upload
from api.utils import format_inr, to_int
from sme.models import Sme
from team.data import daily_mail_pending_pod_test_data
from team.helper_tasks import INVOICE_EMAIL_PERIOD, notify_excess_outward_payment_data
from team.models import ManualBooking, Invoice
from utils.models import AahoOffice, City


def daily_mail_pending_pod(request):
    mb = ManualBooking.objects.filter(
        Q(destination_office=AahoOffice.objects.get(id=2)) & Q(
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
    return render(request=request, template_name='team/emails/pod_status.html', context={'mb': mb})


def notify_admins_about_to_pay_booking(request):
    office = AahoOffice.objects.get(id=2)
    mb = ManualBooking.objects.filter(
        (Q(source_office=office) | Q(destination_office=office))
        & Q(billing_type='To Pay')
        & Q(total_amount_to_company__gt=F('total_in_ward_amount') + F('tds_deducted_amount'))
        & Q(shipment_date__gte='2017-01-01')
    ).exclude(
        booking_status='cancelled'
    ).order_by(
        'shipment_date'
    )
    return render(request=request, template_name='team/emails/notify_to_pay_booking_updates.html', context={'mb': mb})


def notify_weekly_partial_tbb(request):
    office = AahoOffice.objects.get(id=2)
    mb = ManualBooking.objects.filter(
        Q(source_office=office) & Q(billing_type='T.B.B.') & Q(
            shipment_date__gte='2017-01-01')
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
    total_open_booking = mb.count()
    pod_pending = mb.filter(pod_status='pending').count()
    pod_received_invoice_not_raised = mb.filter(
        Q(pod_status='completed') & Q(invoice_status='no_invoice')).count()
    pod_received_outward_payment_pending = mb.filter(Q(pod_status='completed') & (
            Q(outward_payment_status='no_payment_made') | Q(outward_payment_status='partial'))).count()
    pod_received_inward_payment_pending = mb.filter(Q(pod_status='completed') & (
            Q(inward_payment_status='no_payment') | Q(inward_payment_status='partial_received'))).count()
    context = {
        'mb': mb,
        'total_open_booking': total_open_booking,
        'pod_pending': pod_pending,
        'pod_received_invoice_not_raised': pod_received_invoice_not_raised,
        'pod_received_outward_payment_pending': pod_received_outward_payment_pending,
        'pod_received_inward_payment_pending': pod_received_inward_payment_pending
    }
    return render(request=request, template_name='team/emails/weekly_tbb_booking_update.html', context=context)


def notify_pod_received_invoice_not_raised(request):
    office = AahoOffice.objects.get(id=2)
    mb = ManualBooking.objects.filter(
        Q(source_office=office) & Q(pod_status='completed') & Q(
            invoice_status='no_invoice')
    ).exclude(
        Q(total_in_ward_amount__gte=F('total_amount_to_company') - F('tds_deducted_amount')) & Q(
            total_out_ward_amount__exact=F('total_amount_to_owner')) | Q(booking_status='cancelled')
    ).select_related(
        'company__name__profile'
    ).prefetch_related(
        'lr_numbers'
    ).order_by('shipment_date')
    return render(request=request, template_name='team/emails/notify_pod_received_invoice_not_raised.html',
                  context={'mb': mb})


def notify_customer_dispatch_details(request):
    return render(
        request=request, template_name='team/emails/notify_customer_dispatch_details.html',
        context=daily_mail_pending_pod_test_data())


def notify_invoice_customers_email_page(request):
    sme = Sme.objects.get(company_code='ACJ')
    invoices_data = []
    number_of_shipment = 0
    invoices = Invoice.objects.filter(
        created_on__date=(datetime.now() - timedelta(days=INVOICE_EMAIL_PERIOD)).date(), customer_fk=sme)
    pod_files = []
    invoices_file = []
    for invoice in invoices:
        number_of_shipment += invoice.bookings.count()
        invoices_data.append({
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.date.strftime('%d-%b-%Y') if invoice.date else '',
            'invoice_amount': '{}'.format(format_inr(invoice.total_amount)),
            'due_date': invoice.date.strftime('%d-%b-%Y') if invoice.date else ''
        })
        if isinstance(invoice.s3_upload, S3Upload):
            invoices_file.append(invoice.s3_upload.public_url())
        for booking in invoice.bookings.all():
            for pod in booking.podfile_set.filter(verified=True, is_valid=True).all():
                if isinstance(pod.s3_upload, S3Upload):
                    pod_files.append(pod.s3_upload.public_url())
    email_id_list = []
    if sme.aaho_poc_email:
        email_id_list.append(sme.aaho_poc_email)
    if sme.sme_email:
        email_id_list.append(sme.sme_email)
    if sme.sme_alt_email:
        email_id_list.append(sme.sme_alt_email)
    data = {
        'invoices_data': invoices_data,
        'number_of_shipment': number_of_shipment,
        'email_id_list': email_id_list,
        'invoices_file': invoices_file,
        'pod_files': pod_files,
        'credit_period': to_int(sme.credit_period)
    }
    return render(request=request, template_name='team/emails/notify_invoice_customers_email.html', context=data)


def notify_excess_outward_payment(request):
    return render(request=request, template_name='team/emails/excess-outward-payment.html',
                  context={'bookings': notify_excess_outward_payment_data()})
