from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from customer import views, views_booking

api_customer_url_patterns = [
    # get
    url(r'app-data/$', views.app_data),
    url(r'login-status/$', views.login_status),

    # post
    url(r'login/$', csrf_exempt(views.api_login)),
    url(r'logout/$', csrf_exempt(views.api_logout)),
    url(r'new-booking/$', csrf_exempt(views_booking.booking_save)),
    url(r'vendor-request/$', csrf_exempt(views_booking.booking_vendor_request)),

    url(r'add-vendor/$', csrf_exempt(views_booking.add_vendor)),
    url(r'delete-vendor/$', csrf_exempt(views_booking.delete_vendor)),
    url(r'edit-profile/$', csrf_exempt(views.edit_profile)),
    url(r'change-password/$', csrf_exempt(views.change_password)),
    url(r'^customer-bookings-data/$', views.team_customer_booking_data),
]
