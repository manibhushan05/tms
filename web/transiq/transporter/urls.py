from django.conf.urls import url

from . import views
transporterUrlPattern = [
    url(r'^new-booking/$', views.new_booking),
]