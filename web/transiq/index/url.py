from django.conf.urls import url

from . import views
indexUrlPattern = [
    url(r'^search-account/$', views.search_account),
    url(r'^privacy-policy/$', views.privacy_policy),
    url(r'^account-security-tips/$', views.account_security_tips),
    url(r'^verify-otp/$', views.verify_reset_password_otp),
    url(r'^reset-password/$', views.reset_password),
    url(r'^daily-freight/$', views.daily_freight_page),
]
