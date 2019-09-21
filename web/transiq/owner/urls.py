from __future__ import absolute_import
from owner import views
from django.conf.urls import url

owner_urls = [
    url(r'^vehicle-data/$', views.vehicle_data),
]
