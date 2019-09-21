from django.conf.urls import url

from . import views

dataCollectionUrlPattern = [
    url(r'^vehicle-temp-data/$', views.vehicle_temp_data),
    url(r'^others-temp-data/$', views.others_temp_data),
]
