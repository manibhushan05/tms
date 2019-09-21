from django.conf.urls import url

from report import views

report_url_patterns = [
    url(r'^test-lr/$', views.test_lr_view),
    url(r'^test-single-booking-invoice/$', views.test_single_booking_invoice_view),
    url(r'^test-multiple-booking-invoice/$', views.test_multiple_booking_invoice_view),
    url(r'^test-invoice-summary/$', views.invoice_summary_test),
    url(r'^test-booking-invoice/$', views.test_booking_invoice),
    url(r'^test-receipt/$', views.test_receipt_view),
]
