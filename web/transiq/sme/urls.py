from django.conf.urls import url
from django.urls import re_path, path

from sme.views import BookingListView, DashboardPageView, CustomerPageView, customer_login_page, InvoiceListView

smeUrlPattern = [
    path(r'', customer_login_page),
    re_path(r'^booking-list/$', BookingListView.as_view(), name="customer_booking_list"),
    re_path(r'^invoice-list/$', InvoiceListView.as_view(), name="customer_invoice_list"),
    re_path(r'^dashboard/$', DashboardPageView.as_view(), name="customer_dashboard"),
    re_path(r'^bookings/$', CustomerPageView.as_view({'get': 'bookings'}), name="customer_bookings"),
    re_path(r'^policy/$', CustomerPageView.as_view({'get': 'policy'}), name="customer_policy"),
    re_path(r'^contact-us/$', CustomerPageView.as_view({'get': 'contact_us'}), name="contact_us"),
    re_path(r'^change-password/$', CustomerPageView.as_view({'get': 'change_password'}), name="change_password"),
    re_path(r'^invoices/$', CustomerPageView.as_view({'get': 'invoices'}), name="invoices"),
]

smeAppUrlPattern = [

]
