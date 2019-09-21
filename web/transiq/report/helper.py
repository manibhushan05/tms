from __future__ import absolute_import, print_function, division
from report.invoice import get_invoice_summary_pdf_data, get_invoices_summary_data
from team.models import ManualBooking


def invoice_summary_data():
    for booking in ManualBooking.objects.filter(booking_id__iexact='AAHO05861'):
        invoices_summary_data = get_invoices_summary_data(bookings=[booking])
        invoices_summary_pdf_data = get_invoice_summary_pdf_data(bookings=[booking], booking_type='full',
                                                                 invoice_summary_data=invoices_summary_data)
