from . import views
from django.conf.urls import url,re_path

enquiryUrlPattern = [
    url(r'daily-rate-enquiry', views.daily_rate_enquiry_form),
    re_path(r'^contact-us-landing-page/$', views.contact_us_landing_page),
]
