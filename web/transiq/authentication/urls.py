from django.conf.urls import url

from . import views

authUrlPattern = [
    url(r'web-login/$', views.login_web),
    url(r'android-login/$', views.login_android),
    url(r'reset-password/$', views.reset_password),
    url(r'register/$', views.register),
    url(r'logout/$', views.logout),
    url(r'server-error-message/$', views.server_error_message),
]
