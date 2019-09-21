from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from fms import views, views_booking, views_requirement, views_appversions
from . import trip_history

api_fms_url_patterns = [
    # post
    url(r'^edit-driver/$', csrf_exempt(views.add_edit_driver)),
    url(r'^edit-owner/$', csrf_exempt(views.add_edit_owner)),
    url(r'^edit-vehicle/$', csrf_exempt(views.add_edit_vehicle)),
    url(r'^send-quote/$', csrf_exempt(views.vehicle_request_quote)),
    url(r'^edit-vehicle-status/$', csrf_exempt(views.edit_vehicle_status)),
    url(r'^edit-account/$', csrf_exempt(views.add_edit_account)),

    url(r'^login/$', csrf_exempt(views.api_login)),
    url(r'^login_employees/$', csrf_exempt(views.api_login_employees)),
    url(r'^logout/$', csrf_exempt(views.api_logout)),

    url(r'^edit-profile/$', csrf_exempt(views.edit_profile)),
    url(r'^change-password/$', csrf_exempt(views.change_password)),
    url(r'^forgot-password-reset/$', csrf_exempt(views.forgot_password)),
    url(r'^get-phone-number/(?P<user_data>[a-zA-Z0-9]+)/$', views.get_phone_forgot_password),
    url(r'^vehicle/send-document-email/$', csrf_exempt(views.vehicle_documents_email)),

    # team booking data
    url(r'^bookings-data/(?P<vehicle_id>[0-9]+)/$', trip_history.team_booking_data),
    url(r'^customer-bookings-data/$', trip_history.team_customer_booking_data),
    url(r'^trip-data/(?P<booking_id>[0-9]+)/$', trip_history.trip_details),
    url(r'^customer-trip-data/(?P<booking_id>[0-9]+)/$', trip_history.customer_trip_details),
    url(r'^create-pod/$', csrf_exempt(views.create_pod)),
    url(r'^upload-pod/$', csrf_exempt(views.upload_pod)),

    # booking related
    url(r'new-booking/$', csrf_exempt(views_booking.booking_save)),
    url(r'vendor-request/$', csrf_exempt(views_booking.booking_vendor_request)),
    url(r'add-vendor/$', csrf_exempt(views_booking.add_vendor)),
    url(r'delete-vendor/$', csrf_exempt(views_booking.delete_vendor)),

    # requirement related
    url(r'^new-requirement/$', csrf_exempt(views_requirement.add_new_requirement)),
    url(r'^update-requirement/$', csrf_exempt(views_requirement.update_requirement)),
    url(r'^delete-requirement/$', csrf_exempt(views_requirement.delete_requirement)),
    url(r'^get-all-requirements/$', csrf_exempt(views_requirement.get_all_requirements)),
    url(r'^get-requirement/$', csrf_exempt(views_requirement.get_requirement)),
    url(r'^get-filtered-requirements/$', csrf_exempt(views_requirement.get_filtered_requirements)),
    url(r'^get-my-requirements/$', csrf_exempt(views_requirement.get_my_requirements)),

    url(r'^send-app-update-sms-to-fms-users/$', csrf_exempt(views_requirement.send_app_update_sms_to_fms_users)),

    # get
    url(r'app-data/$', views.app_data),
    url(r'login-status/$', views.login_status),

    url(r'list-vehicles/$', views.list_vehicles),
    url(r'available-loads/$', views.open_bookings),
    url(r'list-drivers/$', views.list_drivers),
    url(r'track-vehicles/$', views.tracking_data),

    url(r'vehicle/(?P<vehicle_id>[0-9]+)/$', views.vehicle_details),
    url(r'vehicle/download-documents/(?P<vehicle_id>[0-9]+)/$', views.documents_download),
    url(r'driver/(?P<driver_id>[0-9]+)/$', views.driver_details),
    url(r'vehicle-gps-data/(?P<vehicle_id>[0-9]+)/$', views.vehicle_gps_data),

    # App version related
    url(r'^app-version-check/$', csrf_exempt(views_appversions.app_version_check)),
    url(r'^app-version-add/$', csrf_exempt(views_appversions.app_version_add)),
    url(r'^get-all-app-versions/$', csrf_exempt(views_appversions.get_all_app_versions)),
]
