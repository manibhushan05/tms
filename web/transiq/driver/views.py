import json
import zlib
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models.aggregates import Min
from django.db.utils import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from api.decorators import api_post, api_get, no_test
from api.helper import json_response, json_400_incorrect_use, json_error_response, json_success_response
from api.sms import send_sms
from api.utils import merge, is_unique_constraint_error, in_mb, from_timestamp, get_or_none
from driver.decorator import token_required
from driver.models import GPSLogNew, DriverAppUser, VEHICLE_STATUS_CHOICES, OTP, Driver, GPSDevice
from owner.models import Vehicle
from restapi.serializers.driver import GPSDeviceSerializer
from transaction.models import VehicleAllocated


def driver_app_data(driver):
    can_upload_pod, no_pod_reason, alloc_vehicle = get_can_upload_pod(driver)

    if driver.vehicle_status != 'unloaded':
        can_upload_pod, no_pod_reason = False, 'Vehicle needs to be unloaded first'
    data = {
        'device_id': driver.device_id,
        'driver_name': driver.driver_name,
        'driver_number': driver.driver_number,
        'number_verified': driver.number_verified,
        'driving_licence_number': driver.driving_licence_number,
        'vehicle_number': driver.vehicle_number,
        'vehicle_type': driver.vehicle_type,
        'vehicle_status': driver.vehicle_status,
        'can_upload_pod': can_upload_pod,
        'no_pod_reason': no_pod_reason,
        'pod_details': None if not alloc_vehicle else alloc_vehicle.pod_details(),
    }
    return data


def get_can_upload_pod(driver):
    if not driver.number_verified:
        return False, 'You must verify your phone number before uploading a POD', None

    try:
        vehicle = Vehicle.objects.filter(driver_app_user=driver)[0]
    except IndexError:
        vehicle = None

    if not vehicle:
        return False, 'No vehicle Associated with driver', None

    try:
        alloc_vehicle = VehicleAllocated.objects.filter(vehicle_number=vehicle).latest('updated_on')
    except VehicleAllocated.DoesNotExist:
        alloc_vehicle = None

    if not alloc_vehicle:
        return False, 'Vehicle not allocated to any trips', None

    return True, None, alloc_vehicle


@api_post
def register(request):
    data = request.data
    device_id = data.get('device_id', None)
    if not device_id:
        return json_response({'status': 'error', 'msg': 'cannot register without device id'}, status=400)

    driver_name = data.get('driver_name', None)
    driver_number = data.get('driver_number', None)
    vehicle_number = data.get('vehicle_number', None)
    vehicle_type = data.get('vehicle_type', None)

    driver_number = None if not driver_number else driver_number.strip()

    created = False
    try:
        driver_app_user = DriverAppUser.objects.get(device_id=device_id)
    except DriverAppUser.DoesNotExist:
        driver_app_user = DriverAppUser(device_id=device_id)
        created = True

    if driver_number and driver_number != driver_app_user.driver_number:
        driver_app_user.number_verified = False
    driver = get_or_none(Driver, phone=driver_number)

    driver_app_user.driver_name = driver_name
    driver_app_user.driver_number = driver_number
    driver_app_user.vehicle_number = vehicle_number
    driver_app_user.vehicle_type = vehicle_type
    driver_app_user.driver = driver
    driver_app_user.save()

    vehicle = set_vehicle_driverapp_user(driver_app_user)
    data = {
        'imei': data.get('device_id', None),
        'device_id': data.get('device_id', None),
        'driver_name': driver_name,
        'driver_number': driver_number,
        'vehicle_number': vehicle_number,
        'vehicle': vehicle.id if isinstance(vehicle, Vehicle) else None,
        'driver': driver.id if isinstance(driver, Driver) else None,
        'vehicle_type': vehicle_type,
        'device_provider': 7
    }
    gps_device_serializer = GPSDeviceSerializer(data=data)
    if gps_device_serializer.is_valid():
        gps_device_serializer.save()
    print(gps_device_serializer.errors)
    data = merge({
        'status': 'success',
        'msg': 'registered' if created else 'registration updated',
        'auth_token': driver_app_user.auth_token,
    }, driver_app_data(driver_app_user))

    return json_response(data)


@api_post
@token_required
def send_otp(request):
    driver = request.driverapp_user
    if driver.driver_number:
        send_otp_sms(driver.driver_number)
        return json_success_response("otp sent")
    else:
        return json_error_response("no phone number to send otp to", 400)


@api_post
@token_required
def edit_driver_details(request):
    data = request.data
    driver_number = data.get('driver_number', None)
    driver_number = None if not driver_number else driver_number.strip()

    driverapp_user = request.driverapp_user
    driverapp_user.driver_name = data.get('driver_name', None)
    driverapp_user.driver_number = data.get('driver_number', None)
    driverapp_user.vehicle_number = data.get('vehicle_number', None)
    driverapp_user.vehicle_type = data.get('vehicle_type', None)
    driverapp_user.driver = get_or_none(Driver, phone=driver_number)

    if driver_number and driver_number != driverapp_user.driver_number:
        driverapp_user.number_verified = False

    driverapp_user.save()
    driver = get_or_none(Driver, phone=driverapp_user.driver_number)

    vehicle = set_vehicle_driverapp_user(driverapp_user)
    print(vehicle)
    data = {
        'imei': data.get('device_id', None),
        'device_id': data.get('device_id', None),
        'driver_name': data.get('driver_name', None),
        'driver_number': driver_number,
        'vehicle_number': data.get('driver_number', None),
        'vehicle': vehicle.id if isinstance(vehicle, Vehicle) else None,
        'driver': driver.id if isinstance(driver, Driver) else None,
        'vehicle_type': data.get('vehicle_type', None),
        'device_provider': 7
    }
    gps_device_serializer = GPSDeviceSerializer(data=data)
    if gps_device_serializer.is_valid():
        gps_device_serializer.save()
    print(gps_device_serializer.errors)
    data = merge({
        'status': 'success',
        'msg': 'details edited',
        'auth_token': driverapp_user.auth_token,
    }, driver_app_data(driverapp_user))

    return json_response(data)


def set_vehicle_driverapp_user(driver):
    if not driver:
        return
    # if not driver.number_verified:
    #     return
    Vehicle.objects.filter(driver_app_user=driver).update(driver_app_user=None)
    if not driver.vehicle_number:
        return
    vehicle = Vehicle.find(driver.vehicle_number)
    if vehicle:
        vehicle.driver_app_user = driver
        vehicle.save()
        return vehicle


def send_otp_sms(phone):
    otp = OTP.generate(phone)
    text = '%s is your OTP for Aaho Driver App phone number verification' % otp
    send_sms(phone, text)


@api_post
@token_required
def verify_otp(request):
    data = request.data
    otp = data.get('otp', None)
    driverapp_user = request.driverapp_user
    phone = driverapp_user.driver_number
    if not phone or not otp:
        return json_400_incorrect_use()

    verified, msg = OTP.verify(phone, otp)
    if not verified:
        return json_error_response('OTP not valid: ' + msg, status=401)

    driverapp_user.number_verified = True
    try:
        driver_model = Driver.objects.get(phone=phone)
    except Driver.DoesNotExist:
        try:
            driver_model = Driver.objects.filter(alt_phone=phone)[0]
        except IndexError:
            driver_model = None
    driverapp_user.driver = driver_model
    driverapp_user.save()

    set_vehicle_driverapp_user(driverapp_user)
    if driverapp_user.number_verified:
        Vehicle.objects.filter(driver_app_user=driverapp_user).update(status=driverapp_user.vehicle_status)

    return json_success_response('number verified')


@api_post
@token_required
def edit_vehicle_status(request):
    data = request.data

    vehicle_status = data.get('vehicle_status', None)
    if vehicle_status not in dict(VEHICLE_STATUS_CHOICES):
        return json_response({'status': 'error', 'msg': 'not a valid vehicle_status'}, status=400)

    driver = request.driverapp_user
    driver.vehicle_status = vehicle_status
    driver.save()
    if isinstance(driver,DriverAppUser):
        try:
            gps_device = GPSDevice.objects.get(device_id=driver.device_id, device_provider_id=7)
            gps_device_serializer=GPSDeviceSerializer(partial=True,instance=gps_device,data={
                'vehicle_status':vehicle_status
            })
            if gps_device_serializer.is_valid():
                gps_device_serializer.save()
        except GPSDevice.DoesNotExist:
            pass

    if driver.number_verified:
        Vehicle.objects.filter(driver_app_user=driver).update(status=driver.vehicle_status)

    data = merge({
        'status': 'success',
        'msg': 'vehicle_status updated',
    }, driver_app_data(driver))

    return json_response(data)


@api_get
@token_required
def get_pod_details(request):
    driver = request.driverapp_user

    data = merge({
        'status': 'success',
        'msg': 'pod details',
    }, driver_app_data(driver))

    return json_response(data)


@api_post
@token_required
def update_pod(request):
    driver = request.driverapp_user

    can_upload_pod, reason, alloc_vehicle = get_can_upload_pod(driver)

    if not can_upload_pod:
        return json_error_response(reason, 400)

    if not driver.vehicle_status == 'unloaded':
        return json_error_response('Switch the status to unloaded before uploading POD', 400)

    data = request.data

    pod = data.get('pod', None)
    pod_thumb = data.get('pod_thumb', None)

    if not pod or not pod_thumb:
        return json_error_response('pod file not sent', 400)

    if alloc_vehicle.pod == pod:
        return json_success_response('nothing to update')

    alloc_vehicle.pod = pod
    alloc_vehicle.pod_thumb = pod_thumb
    alloc_vehicle.pod_date = timezone.now()

    alloc_vehicle.save()

    return json_response({'status': 'success', 'msg': 'pod updated', 'pod_details': alloc_vehicle.pod_details()})


"""
    THIS ORDER IS IMPORTANT!!

        pos.put(id);
        pos.put(deviceId);
        pos.put(time.getTime());
        pos.put(provider);
        try { pos.put(accuracy); } catch (JSONException e) { pos.put(0); }
        try { pos.put(latitude); } catch (JSONException e) { pos.put(0); }
        try { pos.put(longitude); } catch (JSONException e) { pos.put(0); }
        try { pos.put(altitude); } catch (JSONException e) { pos.put(0); }
        try { pos.put(speed); } catch (JSONException e) { pos.put(0); }
        try { pos.put(course); } catch (JSONException e) { pos.put(0); }
        try { pos.put(battery); } catch (JSONException e) { pos.put(0); }
        pos.put(totalMemory);
        pos.put(availMemory);
        pos.put(threshold);
        pos.put(lowMemory);
        pos.put(brand);
        pos.put(manufacturer);
        pos.put(device);
        pos.put(product);
        pos.put(model);
        pos.put(versionName);
        pos.put(versionCode);
        pos.put(androidRelease);
        pos.put(androidSdkInt);
"""


def location_update_new(request):
    """
    NOTE:

    request and response data is kept to a bare minimum,
    request body is a compressed json list,
      - using a dict would at least double the size of request data
      - gzip compression reduces the size by around 33 percent
    response body is blank, only response code is sent

    TODO:

    - this is fine for now, later we should move to a TCP server setup like the one
      traccar uses to ensure minimum data transfer

    - this view should return asap and do the actual database write async using celery

    """

    # if request is compressed, decompress it
    try:
        json_str = zlib.decompress(request.body)
    except zlib.error:
        json_str = request.body

    try:
        data = json.loads(json_str.decode('utf8'))
    except ValueError:
        raise
        # return HttpResponse(status=400)
    print(data)
    try:
        device_id, timestamp, provider, accuracy, latitude, longitude, altitude, speed, course, battery, total_memory, available_memory, threshold, low_memory, brand, manufacturer, device, product, model, version_name, version_code, android_release, android_sdk_int = data
    except ValueError:
        raise
        # return HttpResponse(status=400)

    log_time = from_timestamp(timestamp)

    if not device_id or not log_time:
        raise AssertionError("device_id and timestamp required")
        # return HttpResponse(status=400)

    try:
        driver = DriverAppUser.objects.get(device_id=device_id)
    except DriverAppUser.DoesNotExist:
        driver = None

    if GPSLogNew.objects.filter(device_id=device_id, datetime=log_time).exists():
        # it's okay the log is already there, return success so that the app can delete the entry
        return HttpResponse(status=200)

    new_log = GPSLogNew(
        device_id=device_id, datetime=log_time, provider=provider, accuracy=accuracy,
        latitude=latitude, longitude=longitude, altitude=altitude, speed=speed, course=course,
        battery=battery, total_memory=in_mb(total_memory), available_memory=in_mb(available_memory),
        threshold=in_mb(threshold), low_memory=bool(low_memory),
        brand=brand, manufacturer=manufacturer, device=device, product=product, model=model,
        version_name=version_name, version_code=version_code,
        android_release=android_release, android_sdk_int=android_sdk_int
    )
    try:
        gps_device = GPSDevice.objects.get(device_id=device_id, device_provider_id=7)
        gps_device_serializer=GPSDeviceSerializer(partial=True,instance=gps_device,data={
            'latitude':latitude,'longitude':longitude,'location_time':log_time
        })
        if gps_device_serializer.is_valid():
            gps_device_serializer.save()
    except GPSDevice.DoesNotExist:
        pass
    if driver:
        new_log.driver = driver
        new_log.driver_name = driver.driver_name
        new_log.driver_number = driver.driver_number
        new_log.driving_licence_number = driver.driving_licence_number
        new_log.vehicle_number = driver.vehicle_number
        new_log.vehicle_type = driver.vehicle_type
        new_log.vehicle_status = driver.vehicle_status

    try:
        with transaction.atomic():
            new_log.save()
            if driver:
                DriverAppUser.objects.filter(id=driver.id).update(location_time=log_time,
                                                                  latitude=latitude, longitude=longitude)

    except IntegrityError as e:
        if is_unique_constraint_error(e):
            # this is a race condition, the object was create after we verified it does not exist
            return HttpResponse(status=200)
        else:
            # some other unexpected IntegrityError (like null values etc.) this should not happen
            # raise so that server can throw a 500 error and we can diagnose the issue
            raise


    # we are here, implies new_log.save() was successful
    return HttpResponse(status=200)


DATE_SLIDER_STEP = 1  # in hours (integer)
DATE_SLIDER_TIME_FORMAT = '%Y/%m/%d %H:%M:%S'


def dateslider_parse2utc(dts):
    return timezone.localtime(timezone.make_aware(datetime.strptime(dts, DATE_SLIDER_TIME_FORMAT)), timezone.utc)


def ceil_datetime(dt, step):
    hrs = decimal_hrs(dt)
    for hr_step in range(0, 25, step):
        if hr_step >= hrs:
            # add the time delta this will take care of changing days/months/years
            return datetime(year=dt.year, month=dt.month, day=dt.day, tzinfo=dt.tzinfo) + timedelta(hours=hr_step)


def floor_datetime(dt, step):
    hrs = decimal_hrs(dt)
    for hr_step in reversed(range(0, 24, step)):
        if hr_step <= hrs:
            return datetime(year=dt.year, month=dt.month, day=dt.day, hour=hr_step, tzinfo=dt.tzinfo)


def decimal_hrs(dt):
    return dt.hour + dt.minute / 60.0 + dt.second / (60.0 * 60.0) + dt.microsecond / (60.0 * 60.0 * 1000000.0)


@no_test
def plot_data(request):
    data = json.loads(request.body)
    device_id = data.get('device_id', None)
    start_time = dateslider_parse2utc(data.get('start_time', None))
    end_time = dateslider_parse2utc(data.get('end_time', None))

    logs = GPSLogNew.objects.filter(
        device_id=device_id, datetime__range=(start_time, end_time)
    ).order_by('datetime').only('datetime', 'created_on', 'battery', 'available_memory', 'total_memory')

    version_changes = []
    last_version = None
    send_delays = []
    battery_percents = []
    free_memory_percents = []
    log_delays = []
    last_log_time = None

    for i, log in enumerate(logs):
        log_time = timezone.localtime(log.datetime).strftime(DATE_SLIDER_TIME_FORMAT)
        send_delay = (log.created_on - log.datetime).total_seconds() / 60.0
        log_delay = (0.0 if last_log_time is None else (log.datetime - last_log_time).total_seconds()) / 60.0
        send_delays.append({'x': log_time, 'y': send_delay})
        log_delays.append({'x': log_time, 'y': log_delay})
        battery_percents.append({'x': log_time, 'y': log.battery})
        free_memory_percents.append({'x': log_time, 'y': log.percent_free()})

        last_log_time = log.datetime

        if not last_version == log.version_name:
            version_changes.append({'i': i, 'v': log.version_name})
            last_version = log.version_name

    send_delay_ys = [d['y'] for d in send_delays]
    log_delay_ys = [d['y'] for d in log_delays]
    data = {
        'send_delays': send_delays,
        'battery_percents': battery_percents,
        'free_memory_percents': free_memory_percents,
        'log_delays': log_delays,
        'max_send_delay': 1.0 if not send_delay_ys else max(send_delay_ys),
        'max_log_delay': 5.0 if not log_delay_ys else max(log_delay_ys),
        'version_changes': version_changes,
    }
    return json_response(data)


@no_test
def plot_page(request):
    max_days = timedelta(days=15)
    default_date_range = timedelta(days=1)

    max_end_time = ceil_datetime(timezone.localtime(timezone.now()), DATE_SLIDER_STEP)
    default_end_time = max_end_time

    first_record_time = GPSLogNew.objects.aggregate(first_time=Min('datetime')).get('first_time', None)
    if first_record_time:
        max_start_time = floor_datetime(timezone.localtime(first_record_time), DATE_SLIDER_STEP)
        if (max_end_time - max_start_time) > max_days:
            max_start_time = max_end_time - max_days
    else:
        max_start_time = max_end_time - max_days
    default_start_time = default_end_time - default_date_range

    data = {
        'device_ids': GPSLogNew.objects.values_list('device_id', flat=True).distinct(),
        'default_start_time': default_start_time.strftime(DATE_SLIDER_TIME_FORMAT),
        'default_end_time': default_end_time.strftime(DATE_SLIDER_TIME_FORMAT),
        'max_start_time': max_start_time.strftime(DATE_SLIDER_TIME_FORMAT),
        'max_end_time': max_end_time.strftime(DATE_SLIDER_TIME_FORMAT),
        'step': DATE_SLIDER_STEP
    }
    return render(request, 'plot.html', data)
