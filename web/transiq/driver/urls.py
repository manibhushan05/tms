from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from . import views

api_driver_url_patterns = [
    url(r'register/$', csrf_exempt(views.register)),
    url(r'edit-details/$', csrf_exempt(views.edit_driver_details)),
    url(r'location-update-new/$', csrf_exempt(views.location_update_new)),
    url(r'vehicle-status/$', csrf_exempt(views.edit_vehicle_status)),
    url(r'send-otp/$', csrf_exempt(views.send_otp)),
    url(r'verify-otp/$', csrf_exempt(views.verify_otp)),
    url(r'update-pod/$', csrf_exempt(views.update_pod)),
    url(r'pod-details/$', views.get_pod_details),
    url(r'plot-page/$', views.plot_page),
    url(r'plot-data/$', csrf_exempt(views.plot_data)),
]
