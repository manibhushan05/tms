from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from notification import views

notification_url_pattern = [
    url(r'^create-notification-device/$', csrf_exempt(views.create_notification_device)),
    url(r'^get-all-mobile-devices/$', csrf_exempt(views.get_all_mobile_devices)),
]
