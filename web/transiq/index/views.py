from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import PermissionDenied
from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render

from api.models import google_reverse_geocode
from api.sms import send_sms
from driver.models import DriverAppUser, GPSLogNew, GPSDeviceLog, TracknovateGPSDevice, \
    TracknovateGPSDeviceLog, WaytrackerGPSDevice, WaytrackerGPSDeviceLog, TempoGoGPSDevice, TempoGoGPSDeviceLog, \
    SecuGPSDevice, SecuGPSDeviceLog, MahindraGPSDevice, MahindraGPSDeviceLog, GPSDevice
from index.models import PhoneOTP, EmailOTP, Route
from owner.vehicle_util import compare_format, display_format
from restapi.helper_api import check_booking_status, get_gps_device_location_from_dynamo
from restapi.models import BookingStatusesMappingLocation
from team.models import LrNumber, ManualBooking


def find_group_name(username):
    user_object = User.objects.get(username=username)
    return user_object.groups.all()[0].name


def checkUserPermission(username):
    try:
        user = User.objects.get(username=username)
        return user.groups.all()[0].name
    except:
        raise PermissionDenied


def daily_freight_page(request):
    route = Route.objects.all()
    return render(request=request, template_name='index/daily_freight.html', context={'route': route})


def index(request):
    return render(request, 'index/index-gloify.html')


def privacy_policy(request):
    return render(request=request, template_name='index/privacy-policy.html')


def shipment_gps_data(booking):
    vehicle_number = compare_format(booking.lorry_number)
    if GPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).exists():
        # gps_data = GPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).last()
        gps_data = get_gps_device_location_from_dynamo(vehicle_number)
    elif TempoGoGPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).exists():
        gps_data = TempoGoGPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).last()
    elif SecuGPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).exists():
        gps_data = SecuGPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).last()
    elif MahindraGPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).exists():
        gps_data = MahindraGPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).last()
    elif TracknovateGPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).exists():
        gps_data = TracknovateGPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).last()
    elif WaytrackerGPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).exists():
        gps_data = WaytrackerGPSDevice.objects.filter(vehicle_number=vehicle_number).exclude(is_active=False).last()

    else:
        gps_data = None

    bsm_location = BookingStatusesMappingLocation.objects.filter(
        booking_status_mapping__manual_booking=booking).order_by('-id')[:1]
    location_data = {}
    if bsm_location or gps_data:
        if not bsm_location or \
                (gps_data and bsm_location and gps_data.location_time > bsm_location[
                    0].created_on):
            location_data['latitude'] = gps_data.latitude
            location_data['longitude'] = gps_data.longitude
            location_data['driver_name'] = gps_data.driver_name
            location_data['driver_number'] = gps_data.driver_number
            location_data['location_time'] = gps_data.location_time
            location_data['vehicle_number'] = gps_data.vehicle_number
        else:
            location_data['latitude'] = bsm_location[0].latitude
            location_data['longitude'] = bsm_location[0].longitude
            location_data['driver_name'] = booking.driver_name
            location_data['driver_number'] = booking.driver_phone
            location_data['location_time'] = bsm_location[0].created_on
            location_data['vehicle_number'] = booking.vehicle_number
    else:
        location_data = None
    return location_data


def track_shipment_page(request):
    return render(request=request, template_name='index/track_shipment_page.html')


def track_shipment_display(request):
    try:
        lr_obj = LrNumber.objects.get(lr_number__iexact=request.GET.get('shipment_id'))
        booking_unloaded = check_booking_status(lr_obj.booking, 'unloaded')
        if lr_obj.booking.pod_status == 'completed' or booking_unloaded:
            messages.info(request, 'This shipment has been delivered at the unloading point.')
            return render(request=request, template_name='index/track_shipment.html',
                          context={'booking': lr_obj.booking, 'lr_obj': lr_obj})
        else:
            gps = shipment_gps_data(booking=lr_obj.booking)
            if gps:
                # if gps['location_time'] > datetime.utcnow() - timedelta(hours=24):
                if gps['location_time'].replace(tzinfo=None) > datetime.utcnow() - timedelta(hours=24):
                    gps_data = google_reverse_geocode(gps['latitude'], gps['longitude'])
                    gps_data['driver_name'] = gps['driver_name']
                    gps_data['driver_number'] = gps['driver_number']
                    gps_data['updated_on'] = gps['location_time']
                    gps_data['vehicle_number'] = display_format(gps['vehicle_number'])
                    context = {'lr_obj': lr_obj, 'gps': gps_data}
                    print(context)
                    return render(request=request, template_name='index/track_shipment.html', context=context)
                else:
                    messages.info(request,
                                  'We apologize but location data for this shipment is not available as of now.')
                    return render(request=request, template_name='index/track_shipment.html',
                                  context={'booking': lr_obj.booking, 'lr_obj': lr_obj})
            else:
                messages.info(request, 'We apologize but location data for this shipment is not available as of now.')
                return render(request=request, template_name='index/track_shipment.html',
                              context={'booking': lr_obj.booking, 'lr_obj': lr_obj})
    except LrNumber.DoesNotExist:
        messages.error(request, 'Incorrect LR, please check and try again.')
        return render(request=request, template_name='index/index-gloify.html')


def login_page(request):
    return render(request=request, template_name='index/login.html')


def begin_password_reset(request):
    if request.method == 'POST':
        try:
            u = User.objects.get(username=request.POST.get('username'))
            u.set_password(request.POST.get('new_password'))
            u.save()
            return HttpResponseRedirect('/')
        except User.DoesNotExist:
            messages.error(request, request.POST.get('username') + " Doesn't Exits")
            return render(request=request, template_name='index/verify-otp.html', context={})
    return render(request=request, template_name='index/search_account.html', context={})


def send_otp(phone, email):
    phone_otp = PhoneOTP.generate(phone=phone)
    sms_text = "%s is your code to reset your Aaho password. Don't reply to this message with your code." % phone_otp
    send_sms(phone, sms_text)
    email_otp = EmailOTP.generate(email=email)
    email_text = "This is your one-time password: %s " % email_otp
    email = EmailMessage(subject='Password reset request', body=email_text, reply_to=['info@aaho.in'], to=[email])
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


def search_account(request):
    try:
        user = User.objects.get(username=request.POST.get('account_identifier'))
        try:
            if user.profile.phone and user.profile.email:
                send_otp(phone=user.profile.phone, email=user.profile.email)
                return render(request=request, template_name='index/verify-otp.html',
                              context={"email": user.profile.email, "phone": user.profile.phone,
                                       'username': user.username})
            elif user.profile.phone and not user.profile.email:
                messages.error(request, "Email Doesn't Exits")
                return render(request=request, template_name='index/search_account.html', context={})
            elif not user.profile.phone and user.profile.email:
                messages.error(request, "Phone Doesn't Exits")
                return render(request=request, template_name='index/search_account.html', context={})
            else:
                messages.error(request, "Something went wrong, Please try later or drop mail at info@aaho.in")
                return render(request=request, template_name='index/search_account.html', context={})
        except:
            messages.error(request, "Something went wrong, Please try later or drop mail at info@aaho.in")
            return render(request=request, template_name='index/search_account.html', context={})
    except User.DoesNotExist:
        messages.error(request, "Account Doesn't Exits")
        return render(request=request, template_name='index/search_account.html', context={})


def verify_reset_password_otp(request):
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    username = request.POST.get('username')
    email_otp = request.POST.get('email_otp')
    phone_otp = request.POST.get('phone_otp')
    phone_status = PhoneOTP.verify(phone=phone, otp=phone_otp)
    email_status = EmailOTP.verify(email=email, otp=email_otp)
    if phone_status and email_status:
        return render(request=request, template_name='index/reset-password-new.html',
                      context={'username': username})
    elif phone_status and not email_status:
        return render(request=request, template_name='index/reset-failed.html')
    elif not phone_status and email_status:
        return render(request=request, template_name='index/reset-failed.html')
    else:
        return render(request=request, template_name='index/search_account.html', context={})


def reset_password(request):
    try:
        user = User.objects.get(username=request.POST.get('username'))
        user.set_password(request.POST.get('password'))
        user.save()
        return render(request=request, template_name='index/reset-successfully.html', context={})
    except User.DoesNotExist:
        return render(request=request, template_name='index/reset-failed.html', context={})


def account_security_tips(request):
    return render(request=request, template_name='index/account-security-tips.html')
