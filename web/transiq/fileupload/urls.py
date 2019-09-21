# encoding: utf-8
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from fileupload import views
from fileupload.views import ChequeFileListView, InvoiceReceiptListView

urlpatterns = [
    url(r'^pod/$', views.upload_pod_page),
    url(r'^pod-create/$', csrf_exempt(views.upload_pod)),
    url(r'^pod-delete/(?P<pk>[0-9]+)$', csrf_exempt(views.delete_pod), name='upload-delete'),
    url(r'^pod-list/$', views.pod_list),
    url(r'^weighing-slip-docs-create/$', csrf_exempt(views.upload_weighing_slip_docs)),
    url(r'^weighing-slip-list/$', views.weighing_slip_list),
    url(r'^weighing-slip-delete/(?P<pk>[0-9]+)$', csrf_exempt(views.delete_weighing_slip), name='upload-delete'),
    url(r'^upload-vehicle-document-page/$', views.upload_vehicle_document_page),
    url(r'^vehicle-docs-create/$', csrf_exempt(views.upload_vehicle_docs)),
    url(r'^vehicle-list/$', views.vehicle_list),
    url(r'^vehile-delete/(?P<pk>[0-9]+)$', csrf_exempt(views.delete_vehicle), name='upload-delete'),
    url(r'^upload-supplier-document-page/$', views.upload_supplier_document_page),
    url(r'^supplier-docs-create/$', csrf_exempt(views.upload_supplier_docs)),
    url(r'^supplier-list/$', views.supplier_list),
    url(r'^supplier-delete/(?P<pk>[0-9]+)$', csrf_exempt(views.delete_supplier), name='upload-delete'),
    url(r'^upload-driver-document-page/$', views.upload_driver_document_page),
    url(r'^driver-docs-create/$', csrf_exempt(views.upload_driver_docs)),
    url(r'^driver-list/$', views.driver_list),
    url(r'^driver-delete/(?P<pk>[0-9]+)$', csrf_exempt(views.delete_driver), name='upload-delete'),
    url(r'^upload-cheque-document-page/$', views.upload_cheque_document_page),
    url(r'^cheque-docs-create/$', csrf_exempt(views.upload_cheque_docs)),
    url(r'^cheque-list/$', views.cheque_list),
    url(r'^cheque-view/$', ChequeFileListView.as_view(), name='upload-view'),
    url(r'^cheque-delete/(?P<pk>[0-9]+)$', csrf_exempt(views.delete_cheque), name='upload-delete'),

    url(r'^upload-invoice-receipt-document-page/$', views.upload_invoice_receipt_page),
    url(r'^invoice-receipt-docs-create/$', csrf_exempt(views.upload_invoice_receipt_docs)),
    url(r'^invoice-receipt-list/$', views.invoice_receipt_list),
    url(r'^invoice-receipt-view/$', InvoiceReceiptListView.as_view(), name='upload-view'),
    url(r'^invoice-receipt-delete/(?P<pk>[0-9]+)$', csrf_exempt(views.delete_invoice_receipt), name='upload-delete'),
]
