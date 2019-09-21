from django.conf.urls import url

from . import views

iosUrlPattern = [
    url(r'^place-order/$', views.place_order),
    url(r'^', views.login),
]