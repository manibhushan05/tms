from . import views
from django.conf.urls import url

mobile_url_pattern = [
    # Outward Payment
    url(r'^outward-payment-page/$', views.outward_payment_page),
    url(r'^outward-payment/$', views.m_outward_payment),
    url(r'^dashboard/$', views.dashboard),
    url(r'^login/$', views.m_login),
    url(r'^register-driver/$', views.register_driver),
    url(r'^register-beneficiary-account/$', views.register_beneficiary_bank_account),
    url(r'^fetch-bank-details-using-ifsc/$', views.fetch_bank_details_using_ifsc),
    url(r'^create-beneficiary-account/$', views.create_beneficiary_account),
    url(r'^error-exceeding-amount', views.error_exceeding_outward_amount),
]
