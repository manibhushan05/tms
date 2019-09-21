import base64
import json
import math
import time
import zipfile
from datetime import datetime, timedelta
from io import BytesIO
from multiprocessing import Pool

import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q
from django.http.response import HttpResponse
from django.utils import timezone
from requests.exceptions import Timeout

from api import s3util
from api.decorators import api_get, api_post
from api.helper import json_response, json_400_incorrect_use, json_401_wrong_credentials, \
    json_401_inactive_user, json_error_response, json_success_response
from api.models import S3Upload
from api.utils import format_date, get_or_none, parse_iso, format_iso, random_id, int_or_none
from authentication.models import Profile
from broker.models import BrokerVehicle, BrokerDriver, BrokerOwner, BrokerAccount, Broker
from customer.sql import get_ranking_results
from driver.models import Driver, VEHICLE_STATUS_CHOICES, TempoGoGPSDeviceLog, WaytrackerGPSDeviceLog, SecuGPSDeviceLog, \
    MahindraGPSDeviceLog, TracknovateGPSDeviceLog
from employee.models import Employee
from fileupload.helper import validate_pod_uploaded
from fileupload.models import VehicleFile, OwnerFile, DriverFile, PODFile
from fileupload.views import get_new_serial
from fms.decorators import authenticated_user
from fms.doc import downloadable_documents_data
from fms.email import send_documents_email
from fms.helper import vehicles_data_gps
from owner.models import Vehicle, Owner
from owner.vehicle_util import compare_format
from team.models import LrNumber, ManualBooking
from transaction.models import UserVendor, Transaction, LoadingUnloadingAddress, VehicleRequest, VehicleRequestQuote
from utils.models import City, VehicleCategory, Address, IDDetails, Bank, TaxationID


def validate_url(url):
    try:
        validate = URLValidator()
        validate(url)
        return True
    except (ValueError, ValidationError):
        return False


@api_get
def login_status(request):
    if request.user and request.user.is_authenticated:
        if request.user.is_active:
            return json_response({'status': 'success', 'state': 'logged_in', 'msg': 'user logged in and active'})
        else:
            return json_response({'status': 'success', 'state': 'inactive', 'msg': 'user logged in but inactive'})
    else:
        return json_response({'status': 'success', 'state': 'logged_out', 'msg': 'user logged out'})


@api_post
def api_login(request):
    print(request.data)
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if not username or not password:
        return json_400_incorrect_use()
    user = authenticate(username=username, password=password)
    if user is None:
        return json_401_wrong_credentials()
    if not user.is_active:
        return json_401_inactive_user()
    login(request, user)
    return json_response({'status': 'success', 'msg': 'login successful'})


@api_post
def api_login_employees(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if not username or not password:
        return json_400_incorrect_use()
    user = authenticate(username=username, password=password)
    if user is None:
        return json_401_wrong_credentials()
    if not user.is_active:
        return json_401_inactive_user()
    login(request, user)
    aaho_office_id = ''
    try:
        emp = Employee.objects.get(username=user)
        aaho_office_id = emp.office.id
        # print(aaho_office_id)
    except Employee.DoesNotExist:
        logout(request)
        return json_401_wrong_credentials()

    data = {'aaho_office_id': aaho_office_id}

    if any(g.name == 'sales' for g in request.user.groups.all()):
        return json_response({'status': 'success', 'msg': 'login successful', 'data': data})
    else:
        if request.user and request.user.is_authenticated():
            logout(request)
        return json_response({'status': 'failure', 'msg': 'login unsuccessful: only emp_group1 allowed'})


@api_post
def api_logout(request):
    if request.user and request.user.is_authenticated:
        logout(request)
        return json_response({'status': 'success', 'msg': 'logout successful'})
    else:
        return json_response({'status': 'success', 'msg': 'already logged out'})


@api_post
@authenticated_user
def change_password(request):
    current_password = request.data.get('current_password', None)
    new_password = request.data.get('new_password', None)

    if not current_password or not new_password:
        return json_400_incorrect_use()

    if not request.user.check_password(current_password):
        return json_response({'status': 'error', 'msg': 'incorrect password'}, status=403)

    if len(new_password) < 8:
        return json_response({'status': 'error', 'msg': 'password should be minimum 8 characters long'}, status=400)

    request.user.set_password(new_password)
    request.user.save()
    return json_response({'status': 'success', 'msg': 'password changed'})


@api_post
def forgot_password(request):
    print(request.body)
    new_password = request.data.get('new_password', None)
    username = request.data.get('username', None)

    if not new_password or not username:
        return json_400_incorrect_use()

    if len(new_password) < 8:
        return json_response({'status': 'error', 'msg': 'password should be minimum 8 characters long'}, status=400)
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        return json_response({'status': 'success', 'msg': 'password changed'})

    except User.DoesNotExist:
        return json_400_incorrect_use()


@api_get
def get_phone_forgot_password(request, user_data):
    if Broker.objects.filter(name__username=user_data).exists():
        try:
            broker = Broker.objects.get(name__username=user_data)
            if broker.name:
                phone = broker.name.profile.phone
                if phone:
                    data = {
                        'phone': phone,
                        'authkey': '115151AKpRGb9tug57565bd3',
                        'username': broker.name.username
                    }
                    return json_response({'status': 'success', 'msg': 'phone found', 'data': data})
                else:
                    return json_response(
                        {'status': 'error', 'msg': 'Phone does not exits, Please contact to AAHO'}, status=404)
            else:
                return json_response({'status': 'error', 'msg': 'User does not exit exists, Please contact to AAHO'},
                                     status=404)
        except Broker.DoesNotExist:
            return json_response({'status': 'error', 'msg': 'User does not exit exists, Please contact to AAHO'},
                                 status=404)
        except Broker.MultipleObjectsReturned:
            return json_response({'status': 'error', 'msg': 'Multiple user with same phone number exits'}, status=404)

    elif Broker.objects.filter(name__profile__phone=user_data).exists():
        try:
            broker = Broker.objects.get(name__profile__phone=user_data)
            if broker.name:
                phone = broker.name.profile.phone
                if phone:
                    data = {
                        'phone': phone,
                        'authkey': '115151AKpRGb9tug57565bd3',
                        'username': broker.name.username
                    }
                    return json_response({'status': 'success', 'msg': 'phone found', 'data': data})
                else:
                    return json_response(
                        {'status': 'error', 'msg': 'Phone does not exit exists, Please contact to AAHO'}, status=404)
            else:
                return json_response({'status': 'error', 'msg': 'Phone does not exists, Please contact to AAHO'},
                                     status=404)
        except Broker.DoesNotExist:
            return json_response({'status': 'error', 'msg': 'User doe snot exists, Please contact to AAHO'}, status=404)
        except Broker.MultipleObjectsReturned:
            if user_data:
                return json_response(
                    {'status': 'error', 'msg': 'Multiple user with %s phone number exists' % (user_data)}, status=404)
            else:
                return json_response({'status': 'error', 'msg': 'Phone does not exit exists, Please contact to AAHO'},
                                     status=404)
    else:
        return json_response({'status': 'error', 'msg': 'User does not exists, Please contact to AAHO'}, status=404)


@api_post
@authenticated_user
def edit_profile(request):
    broker = request.broker
    owner = request.owner
    profile = get_or_none(Profile, user=request.user)
    profile_mod = False
    if not profile:
        profile = Profile(user=request.user, name=request.user.first_name, email=request.user.email)
        profile_mod = True

    if 'full_name' in request.data:
        request.user.first_name = request.data['full_name']
        request.user.save()
        profile.name = request.data['full_name']
        profile_mod = True

    if 'contact_name' in request.data:
        profile.contact_person_name = request.data['contact_name']
        profile_mod = True

    if 'address' in request.data and request.data['address']:
        profile.address = request.data['address']
        profile_mod = True
        save_broker_address(broker, request.data['address'])

    if 'phone' in request.data:
        profile.phone = request.data['phone']
        profile_mod = True

    if 'email' in request.data:
        request.user.email = request.data['email']
        request.user.save()
        profile.email = request.data['email']
        profile_mod = True

    if 'city_id' in request.data:
        broker.city = get_or_none(City, id=request.data['city_id'])
        profile_mod = True

    if 'designation' in request.data:
        profile.designation = request.data['designation']
        profile_mod = True

    if profile_mod:
        profile.save()

    data = request.data

    doc_key = 'pan_doc'
    if doc_key in data and broker and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        if not OwnerFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None),
            )
            OwnerFile.objects.create(
                uploaded_by=request.broker.name,
                owner=owner,
                document_category='PAN',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(OwnerFile, owner=owner),
                s3_upload=s3_upload
            )
        taxation_details = broker.taxation_details or TaxationID()
        taxation_details.pan = doc_id
        taxation_details.save()
        broker.taxation_details = taxation_details
        broker.save()

    doc_key = 'dec_doc'
    if doc_key in data and owner and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        if not OwnerFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None),
            )
            OwnerFile.objects.create(
                uploaded_by=request.broker.name,
                owner=owner,
                document_category='DEC',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(OwnerFile, owner=owner),
                s3_upload=s3_upload,
            )
        validity = data[doc_key].get('validity', None)
        owner.declaration_validity = None if not validity else parse_iso(validity)
        owner.save()

    return json_success_response('profile edited', user=get_user_data(request.user, profile, broker, owner))


@api_get
@authenticated_user
def app_data(request):
    cities = City.objects.filter(state_id__isnull=False).order_by('name').values('id', 'name', 'state__name')
    cities = [{'id': c['id'], 'name': c['name'], 'state': c['state__name']} for c in cities]
    vehicle_data = list(VehicleCategory.objects.order_by('-priority').values('id', 'vehicle_type', 'capacity'))
    vendor_data = list(UserVendor.objects.filter(user=request.user).order_by('id').values('id', 'name', 'phone'))

    broker = request.broker
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, name=request.user.first_name, email=request.user.email)
    city_scores, address_scores = get_ranking_results(request.user.id)

    ac_ids = dict(BrokerAccount.objects.filter(broker=broker).values_list('account_id', 'relation'))
    accounts = Bank.objects.filter(id__in=ac_ids.keys())
    accounts_data = []
    for ac in accounts:
        ac_data = ac.to_json()
        ac_data['relation'] = ac_ids[ac.id]
        accounts_data.append(ac_data)

    data = {
        'cities': cities,
        'vehicles': vehicle_data,
        'vendors': vendor_data,
        'city_scores': city_scores,
        'address_scores': address_scores,
        'user': get_user_data(request.user, profile, broker, request.owner),
        'accounts_data': accounts_data,
        'aaho_office': broker.aaho_office.to_json() if broker.aaho_office else {},
    }
    return json_response({'status': 'success', 'msg': 'app data', 'data': data})


@api_get
@authenticated_user
def vehicle_details(request, vehicle_id):
    if not vehicle_id:
        return json_400_incorrect_use()
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return json_error_response('vehicle does not exist', 404)
    except Vehicle.MultipleObjectsReturned:
        return json_error_response('multiple vehicle exist with same id', 409)
    data = vehicle.to_json()
    try:
        broker_vehicle = BrokerVehicle.objects.get(vehicle=vehicle, broker=request.broker)
        if broker_vehicle.account_details_id:
            data['account'] = broker_vehicle.account_details.to_json()
    except BrokerVehicle.DoesNotExist:
        pass
    return json_response({'status': 'success', 'msg': 'vehicle details', 'data': data})


@api_post
@authenticated_user
def edit_vehicle_status(request):
    data = request.data

    vehicle_id = data.get('id', None)
    vehicle_status = data.get('vehicle_status', None)

    if not vehicle_id or not vehicle_status:
        return json_400_incorrect_use()
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return json_error_response('vehicle does not exist', 404)

    if vehicle_status not in dict(VEHICLE_STATUS_CHOICES):
        return json_response({'status': 'error', 'msg': 'not a valid vehicle_status'}, status=400)

    Vehicle.objects.filter(id=vehicle.id).update(status=vehicle_status)
    if vehicle.driver_app_user:
        vehicle.driver_app_user.vehicle_status = vehicle_status
        vehicle.driver_app_user.save()

    return json_response({'status': 'success', 'msg': 'vehicle_status updated', 'vehicle_status': vehicle_status})


@api_get
@authenticated_user
def driver_details(request, driver_id):
    if not driver_id:
        return json_400_incorrect_use()
    try:
        driver = Driver.objects.get(id=driver_id)
    except Driver.DoesNotExist:
        return json_error_response('driver does not exist', 404)
    return json_response({'status': 'success', 'msg': 'vehicle details', 'data': driver.to_json()})


def get_vehicle_current_data(vehicle_number):
    vehicle_numbers = [vehicle_number]
    data = vehicles_data_gps(vehicle_numbers)
    return data


@api_get
@authenticated_user
def vehicle_gps_data(request, vehicle_id):
    logs_classes = ['TempoGoGPSDeviceLog', 'WaytrackerGPSDeviceLog', 'SecuGPSDeviceLog', 'MahindraGPSDeviceLog',
                    'TracknovateGPSDeviceLog']
    vehicle = get_or_none(Vehicle, id=vehicle_id)
    if not isinstance(vehicle, Vehicle):
        return json_400_incorrect_use()
    data = []
    for logs_class in logs_classes:
        gps_data = eval(logs_class).objects.filter(
            vehicle_number=compare_format(vehicle.vehicle_number)).filter(
            datetime__gte=datetime.now() - timedelta(hours=48)).order_by('-datetime')

        if not gps_data:
            continue

        data.append({
            'latitude': str(gps_data[0].latitude),
            'longitude': str(gps_data[0].longitude),
            'timestamp': format_date(gps_data[0].datetime)
        })
        last_time = (gps_data[0].datetime - timedelta(minutes=15)).time()
        for gps in gps_data:
            if last_time > gps.datetime.time():
                last_time = (gps.datetime - timedelta(minutes=15)).time()
                data.append({
                    'latitude': str(gps.latitude),
                    'longitude': str(gps.longitude),
                    'timestamp': format_date(gps.datetime)
                })
        if len(data) > 0:
            break
    current_location = {
        'from_address': '',
        'to_address': '',
        'from_gps': data[0] if data else {},
        'to_gps': data[0] if data else {},
        'total_distance': 0,
        'distance_covered': 0,
        'distance_remaining': 0,
    }
    return json_response(
        {'status': 'success', 'msg': 'GPS Log',
         'data': {'gps_data': data, 'current_location': current_location, 'max_gps_log_days': 7}})


def vehicle_gpss_data(request, vehicle_id):
    vehicle = get_or_none(Vehicle, id=vehicle_id)
    if not isinstance(vehicle, Vehicle):
        return json_400_incorrect_use()
    now = datetime.now()
    data = []
    gps_data = TempoGoGPSDeviceLog.objects.filter(vehicle_number=compare_format(vehicle.vehicle_number))
    if gps_data.exists():
        for value in range(0, 240, 5):
            gps = gps_data.filter(
                datetime__range=[now - timedelta(minutes=value), now - timedelta(minutes=value - 5)]).last()
            print(gps)
            if gps:
                data.append({
                    'latitude': str(gps.latitude),
                    'longitude': str(gps.longitude),
                    'timestamp': format_date(gps.datetime)
                })
    return json_response({'status': 'success', 'msg': 'GPS Log', 'data': data})


@api_get
@authenticated_user
def list_vehicles(request):
    data, owners_data, drivers_data, accounts_data = broker_vehicle_data(request.broker)
    return json_response({
        'status': 'success',
        'msg': 'list vehicles',
        'data': data,
        'owners_data': owners_data,
        'drivers_data': drivers_data,
        'accounts_data': accounts_data,
    })


def broker_vehicle_data(broker):
    vehicle_ids = list(BrokerVehicle.objects.filter(broker=broker).values_list('vehicle_id', flat=True))
    vehicles = Vehicle.objects.filter(id__in=vehicle_ids).values(
        'id', 'vehicle_number', 'vehicle_type_id', 'vehicle_model')
    vehicle_data = [{
        'id': v['id'],
        'vehicle_number': v['vehicle_number'],
        'vehicle_type': v['vehicle_type_id'] if v['vehicle_type_id'] else 74,
        'vehicle_model': v['vehicle_model']
    } for v in vehicles]

    driver_ids = list(set(BrokerDriver.objects.filter(broker=broker).values_list('driver_id', flat=True)))
    drivers = Driver.objects.filter(id__in=driver_ids).values('id', 'name', 'phone', 'driving_licence_number')
    drivers_data = list(drivers)

    owner_ids = list(set(BrokerOwner.objects.filter(broker=broker).values_list('owner_id', flat=True)))
    owners = Owner.objects.filter(id__in=owner_ids)
    owners_data = []
    for o in owners:
        name, phone = o.name_phone()
        owners_data.append({
            'id': o.id,
            'name': name or ('' if not o.name_id else o.name.username),
            'phone': phone,
        })

    ac_ids = dict(BrokerAccount.objects.filter(broker=broker).values_list('account_id', 'relation'))
    accounts = Bank.objects.filter(id__in=ac_ids.keys())
    accounts_data = []
    for ac in accounts:
        ac_data = ac.to_json()
        ac_data['relation'] = ac_ids[ac.id]
        accounts_data.append(ac_data)
    return vehicle_data, owners_data, drivers_data, accounts_data


@api_get
@authenticated_user
def list_drivers(request):
    return json_response({'status': 'success', 'msg': 'list drivers', 'data': broker_drivers_data(request.broker)})


def broker_drivers_data(broker):
    driver_ids = list(set(BrokerDriver.objects.filter(broker=broker).values_list('driver_id', flat=True)))
    drivers = Driver.objects.filter(id__in=driver_ids).values('id', 'name', 'phone', 'driving_licence_number')
    driver_data = list(drivers)
    return driver_data


@api_get
@authenticated_user
def tracking_data(request):
    vehicle_ids = list(BrokerVehicle.objects.filter(broker=request.broker).values_list('vehicle_id', flat=True))
    vehicles = Vehicle.objects.filter(id__in=vehicle_ids).values_list('vehicle_number', flat=True)
    return json_response({'status': 'success', 'msg': 'tracking data', 'data': vehicles_data_gps(vehicles)})


def bearing(lat1, lon1, lat2, lon2):
    sin, cos, atan2, rad, deg = math.sin, math.cos, math.atan2, math.radians, math.degrees
    phi1 = rad(lat1)
    phi2 = rad(lat2)
    delta_lambda = rad(lon2 - lon1)

    y = sin(delta_lambda) * cos(phi2)
    x = cos(phi1) * sin(phi2) - sin(phi1) * cos(phi2) * cos(delta_lambda)
    return deg(atan2(y, x))


@api_post
@authenticated_user
def add_edit_vehicle(request):
    data = request.data
    vehicle_id = data.get('id', None)

    if vehicle_id and isinstance(vehicle_id, int):
        vehicle = get_or_none(Vehicle, id=int_or_none(vehicle_id))
        if not isinstance(vehicle, Vehicle):
            return json_error_response('Vehicle with id=%s does not exist' % vehicle_id, 404)
    else:
        vehicle = Vehicle()

    vehicle_number = data.get('vehicle_number', None)
    if not vehicle_number and not vehicle_id:
        return json_error_response('vehicle number required', 400)

    owner_id = (data.get('owner', None) or {}).get('id', None)
    owner = None
    if owner_id and isinstance(owner_id, int):
        owner = get_or_none(Owner, id=int_or_none(owner_id))
        if not isinstance(owner, Owner):
            return json_error_response('Owner with id=%s does not exist' % owner_id, 404)

    ac_id = (data.get('account', None) or {}).get('id', None)
    account = None
    if ac_id and isinstance(ac_id, int):
        account = get_or_none(Bank, id=int_or_none(ac_id))
        if not isinstance(account, Bank):
            return json_error_response('Bank account with id=%s does not exist' % ac_id, 404)

    driver_id = (data.get('driver', None) or {}).get('id', None)
    driver = None
    if driver_id and isinstance(driver_id, int):
        driver = get_or_none(Driver, id=int_or_none(driver_id))
        if not isinstance(driver, Driver):
            return json_error_response('Driver with id=%s does not exist' % driver_id, 404)

    current_city_id = data.get('current_city', None)
    current_city = None
    if current_city_id and isinstance(current_city_id, int):
        current_city = get_or_none(City, id=int_or_none(current_city_id))
        if not isinstance(current_city, City):
            return json_error_response('City with id=%s does not exist' % current_city_id, 404)

    vehicle_type_id = data.get('vehicle_type', None)
    vehicle_type = None
    has_vehicle_type_data = 'vehicle_type' in data
    if vehicle_type_id and isinstance(vehicle_type_id, int):
        vehicle_type = get_or_none(VehicleCategory, id=int_or_none(vehicle_type_id))
        if not vehicle_type:
            return json_error_response('VehicleCategory with id=%s does not exist' % vehicle_type_id, 404)
    else:
        new_category_type = data.get('new_vehicle_category_type', None)
        new_category_capacity = data.get('new_vehicle_category_capacity', None)
        new_category_type = None if not new_category_type else new_category_type.strip()
        new_category_capacity = None if not new_category_capacity else new_category_capacity.strip()
        if new_category_type:
            has_vehicle_type_data = True
            vehicle_type, _ = VehicleCategory.objects.get_or_create(
                vehicle_type=new_category_type, capacity=new_category_capacity)

    if 'owner' in data:
        vehicle.owner = owner

    if 'driver' in data:
        Vehicle.objects.filter(driver=driver).update(driver=None)
        vehicle.driver = driver

    if 'current_city' in data:
        vehicle.current_city = current_city

    if has_vehicle_type_data:
        vehicle.vehicle_type = vehicle_type

    normal_fields = [
        'vehicle_number', 'vehicle_model', 'chassis_number', 'engine_number', 'sim_number',
        'sim_operator', 'gps_enabled'
    ]

    for field in normal_fields:
        if field in data:
            setattr(vehicle, field, data.get(field, None))

    vehicle_status = data.get('status', None)
    if vehicle_status:
        if vehicle_status not in dict(VEHICLE_STATUS_CHOICES):
            return json_response({'status': 'error', 'msg': 'not a valid vehicle_status'}, status=400)
        vehicle.status = vehicle_status
        if vehicle.driver_app_user:
            vehicle.driver_app_user.vehicle_status = vehicle_status
            vehicle.driver_app_user.save()

    vehicle.save()

    broker_vehicle, _created = BrokerVehicle.objects.get_or_create(broker=request.broker, vehicle=vehicle)
    if 'account' in data:
        broker_vehicle.account_details = account
        broker_vehicle.save()

    if owner:
        BrokerOwner.objects.get_or_create(broker=request.broker, owner=owner)
    if driver:
        BrokerDriver.objects.get_or_create(broker=request.broker, driver=driver)

    edited = False

    doc_key = 'rc_doc'
    if doc_key in data and data[doc_key].get('url'):

        if not VehicleFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None)
            )
            VehicleFile.objects.create(
                uploaded_by=request.broker.name,
                vehicle=vehicle,
                document_category='REG',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(VehicleFile, vehicle=vehicle),
                s3_upload=s3_upload
            )

        registration_year = data[doc_key].get('manufacture_year', None)
        validity = data[doc_key].get('validity', None)

        registration_year = None if not registration_year else registration_year.strip()
        try:
            registration_year = int(registration_year)
        except ValueError:
            registration_year = None
        vehicle.registration_year = datetime(year=registration_year, month=1,
                                             day=1).date() if 1980 < registration_year < 2070 else None
        vehicle.registration_validity = None if not validity else parse_iso(validity)
        edited = True

    doc_key = 'permit_doc'
    if doc_key in data and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)

        if not VehicleFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None)
            )
            VehicleFile.objects.create(
                uploaded_by=request.broker.name,
                vehicle=vehicle,
                document_category='PERM',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(VehicleFile, vehicle=vehicle),
                s3_upload=s3_upload
            )
        permit_type = data[doc_key].get('permit_type', None)
        validity = data[doc_key].get('validity', None)
        vehicle.permit_type = permit_type
        vehicle.permit_validity = None if not validity else parse_iso(validity)
        vehicle.permit = doc_id
        edited = True

    doc_key = 'insurance_doc'
    if doc_key in data and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)

        if not VehicleFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None)
            )
            VehicleFile.objects.create(
                uploaded_by=request.broker.name,
                vehicle=vehicle,
                document_category='INS',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(VehicleFile, vehicle=vehicle),
                s3_upload=s3_upload
            )
        insurer_name = data[doc_key].get('insurer_name', None)
        validity = data[doc_key].get('validity', None)

        vehicle.insurer = insurer_name
        vehicle.insurance_validity = None if not validity else parse_iso(validity)
        vehicle.insurance_number = doc_id
        edited = True

    doc_key = 'fitness_doc'
    if doc_key in data and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)

        if not VehicleFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None)
            )
            VehicleFile.objects.create(
                uploaded_by=request.broker.name,
                vehicle=vehicle,
                document_category='FIT',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(VehicleFile, vehicle=vehicle),
                s3_upload=s3_upload
            )
        validity = data[doc_key].get('validity', None)

        vehicle.fitness_certificate_validity_date = None if not validity else parse_iso(validity)
        vehicle.fitness_certificate_number = doc_id
        edited = True

    doc_key = 'puc_doc'
    if doc_key in data and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)

        if not VehicleFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None),
            )
            VehicleFile.objects.create(
                uploaded_by=request.broker.name,
                vehicle=vehicle,
                document_category='PUC',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(VehicleFile, vehicle=vehicle),
                s3_upload=s3_upload,
            )
        validity = data[doc_key].get('validity', None)

        vehicle.puc_certificate_validity_date = None if not validity else parse_iso(validity)
        vehicle.puc_certificate_number = doc_id
        edited = True

    if edited:
        vehicle.save()

    doc_key = 'owner_pan_doc'
    if doc_key in data and vehicle.owner and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        if not OwnerFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None),
            )
            OwnerFile.objects.create(
                uploaded_by=request.broker.name,
                owner=owner,
                document_category='PAN',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(OwnerFile, owner=owner),
                s3_upload=s3_upload
            )
        taxation_details = vehicle.owner.taxation_details or TaxationID()
        taxation_details.pan = doc_id
        taxation_details.save()

        owner = vehicle.owner
        owner.taxation_details = taxation_details
        owner.save()
        vehicle.owner = owner

    doc_key = 'owner_dec_doc'
    if doc_key in data and vehicle.owner and data[doc_key].get('url'):

        if not OwnerFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None),
            )
            OwnerFile.objects.create(
                uploaded_by=request.broker.name,
                owner=owner,
                document_category='DEC',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(OwnerFile, owner=owner),
                s3_upload=s3_upload,
            )
        validity = data[doc_key].get('validity', None)

        owner = vehicle.owner
        owner.declaration_validity = None if not validity else parse_iso(validity)
        owner.save()
        vehicle.owner = owner

    doc_key = 'driver_dl_doc'
    if doc_key in data and vehicle.driver and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)

        if not DriverFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None),
            )
            DriverFile.objects.create(
                uploaded_by=request.broker.name,
                driver=driver,
                document_category='DL',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(DriverFile, driver=driver),
                s3_upload=s3_upload,
            )
        validity = data[doc_key].get('validity', None)
        issue_loc = data[doc_key].get('issue_location', None)

        driver = vehicle.driver

        driver.driving_licence_number = doc_id
        driver.driving_licence_location = issue_loc
        driver.driving_licence_validity = None if not validity else parse_iso(validity)
        driver.save()

        vehicle.driver = driver

    return json_success_response(
        'vehicle details %s' % ('edited' if vehicle_id else 'saved'),
        data=vehicle.to_json()
    )


@api_post
@authenticated_user
def add_edit_driver(request):
    data = request.data
    print(data)
    driver_id = data.get('id', None)

    if driver_id:
        driver = get_or_none(Driver, id=int_or_none(driver_id))
        if not driver:
            return json_error_response('Driver with id=%s does not exist' % driver_id, 404)
    else:
        driver = Driver()

    ac_id = (data.get('account', None) or {}).get('id', None)
    account = None
    if ac_id:
        account = get_or_none(Bank, id=int_or_none(ac_id))
        if not account:
            return json_error_response('Bank account with id=%s does not exist' % ac_id, 404)

    if 'address' in data:
        address_data = data.get('address', None)
        if address_data and not address_data.get('id', None) and driver.address_id:
            address_data['id'] = driver.address_id
        driver.address = None if not address_data else save_address(address_data)

    if 'account_details' in data:
        bank_data = data.get('account_details', None)
        if bank_data and not bank_data.get('id', None) and driver.account_details_id:
            bank_data['id'] = driver.account_details_id
        driver.account_details = None if not bank_data else save_account_details(bank_data)

    rest_fields = ['name', 'phone']
    if Driver.objects.filter(phone=data.get('phone', None)).exclude(id=driver.id).exists():
        return json_error_response('Driver with Phone Number %s already  exist' % data.get('phone', None), 409)
    for field in rest_fields:
        if field in data:
            setattr(driver, field, data.get(field, None))

    if 'account' in data:
        if not Driver.objects.filter(account_details=account).exists():
            driver.account_details = account

    driver.save()

    BrokerDriver.objects.get_or_create(broker=request.broker, driver=driver)

    doc_key = 'pan_doc'
    if doc_key in data and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        if not DriverFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None),
            )
            DriverFile.objects.create(
                uploaded_by=request.broker.name,
                driver=driver,
                document_category='PAN',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(DriverFile, driver=driver),
                s3_upload=s3_upload,
            )

        taxation_id = driver.taxation_id or TaxationID()
        taxation_id.pan = doc_id
        taxation_id.save()

        driver.taxation_id = taxation_id
        driver.save()

    doc_key = 'dl_doc'
    if doc_key in data and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        if not DriverFile.objects.filter(
                Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None)).exists():
            s3_upload = s3util.get_or_create_s3_upload(
                bucket=data[doc_key].get('bucketName', None),
                folder=data[doc_key].get('folderName', None),
                filename=data[doc_key].get('fileName', None),
                verified=False,
                is_valid=False,
                uuid=data[doc_key].get('uuid', None),
            )
            DriverFile.objects.create(
                uploaded_by=request.broker.name,
                driver=driver,
                document_category='DL',
                s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(data[doc_key].get('thumb_url')) else None,
                serial=get_new_serial(DriverFile, driver=driver),
                s3_upload=s3_upload,
            )
        validity = data[doc_key].get('validity', None)
        issue_loc = data[doc_key].get('issue_location', None)

        driver.driving_licence_number = doc_id
        driver.driving_licence_location = issue_loc
        driver.driving_licence_validity = None if not validity else parse_iso(validity)
        driver.save()

    return json_success_response('driver details %s' % ('edited' if driver_id else 'saved'),
                                 data=driver.to_json())


@api_post
@authenticated_user
def add_edit_account(request):
    data = request.data
    ac_id = data.get('id', None)

    if ac_id:
        account = get_or_none(Bank, id=int_or_none(ac_id))
        if not account:
            return json_error_response('Bank account with id=%s does not exist' % ac_id, 404)
    else:
        bank = Bank()

    bank_name = data.get('bank', None)
    account_holder_name = data.get('account_holder_name', None)
    account_number = data.get('account_number', None)
    account_type = data.get('account_type', None)
    ifsc = data.get('ifsc', None)

    if not account_holder_name and not account_number and not account_type and not ifsc:
        return json_400_incorrect_use()

    if 'bank' in data:
        bank.bank = bank_name

    if 'account_holder_name' in data:
        bank.account_holder_name = account_holder_name

    if 'account_number' in data:
        bank.account_number = account_number

    if 'account_type' in data:
        bank.account_type = account_type

    if 'ifsc' in data:
        bank.ifsc = ifsc

    bank.save()

    BrokerAccount.objects.get_or_create(broker=request.broker, account=bank)

    return json_success_response('account details %s' % ('edited' if ac_id else 'saved'),
                                 data=bank.to_json())


@api_post
@authenticated_user
def add_edit_owner(request):
    data = request.data
    owner_id = int_or_none(data.get('id', None))

    if owner_id:
        owner = get_or_none(Owner, id=int_or_none(owner_id))
        if not owner:
            return json_error_response('Owner with id=%s does not exist' % owner_id, 404)
    else:
        owner = Owner()

    name = data.get('name', None)
    phone = data.get('phone', None)

    if not name and not phone:
        return json_400_incorrect_use()

    if not owner.name_id:
        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            user = User.objects.create(username=phone)
            user.set_password('owner.1900')
        user.first_name = name
        user.save()
        owner.name_id = user.id

    try:
        profile = Profile.objects.get(user_id=owner.name_id)
    except Profile.DoesNotExist:
        profile = Profile(user_id=owner.name_id)
    profile.name = name
    profile.phone = phone
    profile.save()

    if 'address' in data:
        address_data = data.get('address', None)
        if address_data and not address_data.get('id', None) and owner.address_id:
            address_data['id'] = owner.address_id
        owner.address = None if not address_data else save_address(address_data)

    if 'account_details' in data:
        bank_data = data.get('account_details', None)
        if bank_data and not bank_data.get('id', None) and owner.account_details_id:
            bank_data['id'] = owner.account_details_id
        owner.account_details = None if not bank_data else save_account_details(bank_data)

    if 'taxation_details' in data:
        taxation_data = data.get('taxation_details', None)
        if taxation_data and not taxation_data.get('id', None) and owner.taxation_details_id:
            taxation_data['id'] = owner.taxation_details_id
        owner.taxation_details = None if not taxation_data else save_taxation_id(taxation_data)

    if 'vehicles_detail' in data:
        owner.vehicles_detail = data.get('vehicles_detail', None)

    owner.save()

    BrokerOwner.objects.get_or_create(broker=request.broker, owner=owner)

    return json_success_response('owner details %s' % ('edited' if owner_id else 'saved'),
                                 data=owner.to_json())


@api_get
@authenticated_user
def open_bookings(request):
    time_now = timezone.now()
    cutoff_date = datetime(year=time_now.year, month=time_now.month, day=time_now.day, tzinfo=time_now.tzinfo)
    bookings = Transaction.objects.filter(
        transaction_status__in=['open', 'pending'], shipment_datetime__gt=cutoff_date
    ).order_by('shipment_datetime').values_list('id', 'transaction_id', 'shipment_datetime')

    booking_ids = [b[0] for b in bookings]

    loading_unloading_locations = LoadingUnloadingAddress.objects.filter(
        transaction_id__in=booking_ids
    ).values_list('transaction_id', 'type', 'city__name', 'city__state__name')

    loading_unloading_map = {}
    for i, addr_type, city, state in loading_unloading_locations:
        if i in loading_unloading_map:
            if addr_type in loading_unloading_map[i]:
                loading_unloading_map[i][addr_type].append((city, state))
            else:
                loading_unloading_map[i][addr_type] = [(city, state)]
        else:
            loading_unloading_map[i] = {addr_type: [(city, state)]}

    bookings_data_map = {}
    for i, tid, ship_date in bookings:
        from_cities = loading_unloading_map.get(i, {}).get('loading', [])
        to_cities = loading_unloading_map.get(i, {}).get('unloading', [])

        from_city, from_state = (None, None) if not from_cities else from_cities[0]
        to_city, to_state = (None, None) if not to_cities else to_cities[0]

        bookings_data_map[i] = {
            'id': i,
            'transaction_id': tid,
            'shipment_datetime': format_date(ship_date),
            'from_city': from_city,
            'from_state': from_state,
            'to_city': to_city,
            'to_state': to_state,
        }

    requested_vehicles = VehicleRequest.objects.filter(
        transaction_id__in=booking_ids
    ).select_related('vehicle_category')
    requested_vehicle_ids = [v.id for v in requested_vehicles]
    broker_quotes = VehicleRequestQuote.objects.filter(user=request.user, vehicle_request_id__in=requested_vehicle_ids)
    broker_quotes_map = {q.vehicle_request_id: q.to_json() for q in broker_quotes}

    requested_vehicles_data = []
    for req_vehicle in requested_vehicles:
        vehicle_category = None if not req_vehicle.vehicle_category else req_vehicle.vehicle_category.name()
        vehicle_category = vehicle_category or req_vehicle.name()
        transaction_data = bookings_data_map[req_vehicle.transaction_id]
        requested_vehicles_data.append({
            'vehicle_request_id': req_vehicle.id,
            'vehicle_category_id': req_vehicle.vehicle_category_id,
            'vehicle_category': vehicle_category,
            'vehicle_quantity': req_vehicle.quantity,
            'transaction_id': transaction_data['id'],
            'transaction_number': transaction_data['transaction_id'],
            'shipment_datetime': transaction_data['shipment_datetime'],
            'from_city': transaction_data['from_city'],
            'from_state': transaction_data['from_state'],
            'to_city': transaction_data['to_city'],
            'to_state': transaction_data['to_state'],
            'quote': broker_quotes_map.get(req_vehicle.id, None)
        })
    return json_success_response('success', data=requested_vehicles_data)


@api_post
@authenticated_user
def vehicle_request_quote(request):
    vehicle_request_id = request.data.get('vehicle_request_id', None)
    quantity = request.data.get('quantity', None)
    amount = request.data.get('amount', None)
    comments = request.data.get('comments', None)

    if not vehicle_request_id or not quantity or not amount:
        return json_400_incorrect_use()

    vehicle_request = get_or_none(VehicleRequest, id=int_or_none(vehicle_request_id))
    if not vehicle_request:
        return json_error_response('VehicleRequest with id=%s does not exist' % vehicle_request_id, 404)

    if quantity < 1:
        return json_error_response('need to provide at least one vehicle', status=400)

    if quantity > vehicle_request.quantity:
        return json_error_response('can not provide more vehicles than requested', status=400)

    try:
        quote = VehicleRequestQuote.objects.get(vehicle_request=vehicle_request, user=request.user)
    except VehicleRequestQuote.DoesNotExist:
        quote = VehicleRequestQuote(
            vehicle_request=vehicle_request, user=request.user, transaction_id=vehicle_request.transaction_id
        )

    quote.quantity = quantity
    quote.amount = amount
    quote.comments = comments
    quote.save()

    return json_success_response('quote saved', data=quote.to_json())


@api_post
@authenticated_user
def vehicle_documents_email(request):
    vehicle_id = request.data.get('id', None)
    emails = request.data.get('emails', None) or []
    excluded = request.data.get('excluded', None) or []

    if vehicle_id is None or not emails:
        return json_400_incorrect_use()
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return json_error_response('vehicle does not exist', 404)

    vehicle_documents = downloadable_documents_data(vehicle, excluded)

    try:
        broker_vehicle = BrokerVehicle.objects.get(broker=request.broker, vehicle=vehicle)
        account = broker_vehicle.account_details
    except BrokerVehicle.DoesNotExist:
        account = None

    if not vehicle_documents and (not account or "ac" in excluded):
        return json_error_response('vehicle has no associated documents', 404)

    send_documents_email(vehicle, account, vehicle_documents, emails, excluded, get_expiry_key())
    return json_success_response('email sent')


EXPIRY_LIMIT = 7 * 24 * 60 * 60


def get_expiry_key():
    link_time = str(time.time())
    # key = base64.b64encode(link_time, '-_').replace('=', '')
    key = base64.b64encode(link_time.encode())
    key = key.decode().replace('=', '')
    key = key.encode()
    return key


def get_link_time(key):
    if not key:
        return None
    padded_key = str(key + ('=' * (-len(key) % 4)))
    try:
        link_time = float(base64.b64decode(padded_key, '-_'))
    except (TypeError, ValueError):
        link_time = None
    return link_time


@api_get
def documents_download(request, vehicle_id):
    if vehicle_id is None:
        return json_400_incorrect_use()
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return json_error_response('vehicle does not exist', 404)

    # check for expiration
    key = request.GET.get('k', None)
    key = None if not key else key.strip()
    if not key:
        return json_error_response('document download key missing', 400)
    link_time = get_link_time(key)
    if not link_time:
        return json_error_response('invalid document download key', 400)
    if time.time() - link_time > EXPIRY_LIMIT:
        return json_error_response('document download link has expired', 404)

    excluded = (request.GET.get('ex', None) or '').split(',')

    data = downloadable_documents_data(vehicle, excluded)
    if not data:
        return HttpResponse('No documents to download')

    zip_filename = compare_format(vehicle.vehicle_number) + '_documents.zip'

    # download data async
    pool = Pool(processes=8)
    dl_data = [(doc_data['filename'], doc_data['s3_url']) for key, doc_data in data.items()]
    results = pool.map(download, dl_data)
    pool.close()

    # return error if unable to download a document
    for (filename, url), content in results:
        if not content:
            if settings.DEBUG:
                msg = 'Error: could not fetch %s' % url
            else:
                msg = 'Error: Server is currently under heavy load, Please try again in a few minutes'
            return HttpResponse(msg, status=503)

    # Open BytesIO to grab in-memory ZIP contents
    byte_io = BytesIO()

    # The zip compressor
    zip_file = zipfile.ZipFile(byte_io, 'w')

    for (filename, url), content in results:
        zip_file.writestr(filename, content)

    # Must close zip for all contents to be written
    zip_file.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(byte_io.getvalue(), content_type='application/x-zip-compressed')
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp


MAX_RETRIES = 10
TIMEOUT = 0.2


def download(data):
    """
    Public S3 urls seem to timeout rather frequently and shamelessly, therefore, low timeout + more retries
    """
    i = 0
    file_name, url = data
    max_retries = MAX_RETRIES
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=TIMEOUT + i * 0.1)
            return data, response.content
        except Timeout:
            continue
    if i != 0:
        pass
    return data, None


def get_user_data(user, profile, broker, owner):
    address = broker.address
    address_data = {} 
    data = {
        'full_name': user.first_name or '',
        'contact_name': profile.contact_person_name or '',
        'address': address_data,
        'username': user.username or '',
        'phone': profile.phone or '',
        'email': profile.email or '',
        'designation': profile.designation or '',
        'id': user.id
    }

    tax = broker.taxation_details
    if tax:
        data['pan_doc'] = {
            'url': None if not tax.pan_doc else tax.pan_doc.document,
            'thumb_url': None if not tax.pan_doc else tax.pan_doc.document_thumb,
            'doc_id': tax.pan,
            'validity': None
        }

    if owner:
        data['owner_dec_doc'] = {
            'url': None if not owner.declaration_doc else owner.declaration_doc.document,
            'thumb_url': None if not owner.declaration_doc else owner.declaration_doc.document_thumb,
            'doc_id': None,
            'validity': format_iso(owner.declaration_validity)
        }

    return data


def save_id_proof(id_data):
    id_proof_id = id_data.get('id', None)

    if id_proof_id:
        id_proof = get_or_none(IDDetails, id=int_or_none(id_proof_id))
        if not id_proof:
            return
    else:
        id_proof = IDDetails()

    id_type = id_data.get('id_type', None)
    id_number = id_data.get('id_number', None)

    if (not id_type or not id_number) and not id_proof_id:
        return

    if 'id_type' in id_data:
        id_proof.id_type = id_type

    if 'id_number' in id_data:
        id_proof.id_number = id_number

    if 'id_issued_in' in id_data:
        id_proof.id_issued_in = id_data.get('id_issued_in', None)

    if 'validity' in id_data:
        id_proof.validity = get_date(id_data.get('validity', None))

    if 'issue_date' in id_data:
        id_proof.issue_date = get_date(id_data.get('issue_date', None))

    id_proof.save()

    return id_proof


def save_account_details(bank_data):
    account_details_id = bank_data.get('id', None)

    if account_details_id:
        account_details = get_or_none(Bank, id=int_or_none(account_details_id))
        if not account_details:
            return
    else:
        account_details = Bank()

    bank = bank_data.get('bank', None)
    account_holder_name = bank_data.get('account_holder_name', None)
    account_number = bank_data.get('account_number', None)
    account_type = bank_data.get('account_type', None)
    ifsc = bank_data.get('ifsc', None)

    if (not account_holder_name or not account_number or not ifsc) and not account_details_id:
        return

    if 'bank' in bank_data:
        account_details.bank = bank

    if 'account_holder_name' in bank_data:
        account_details.account_holder_name = account_holder_name

    if 'account_number' in bank_data:
        account_details.account_number = account_number

    if 'account_type' in bank_data:
        account_details.account_type = account_type

    if 'ifsc' in bank_data:
        account_details.ifsc = ifsc

    account_details.save()

    return account_details


def save_taxation_id(taxation_data):
    taxation_id_id = taxation_data.get('id', None)

    if taxation_id_id:
        taxation_id = get_or_none(TaxationID, id=int_or_none(taxation_id_id))
        if not taxation_id:
            return
    else:
        taxation_id = TaxationID()

    service_tax_number = taxation_data.get('service_tax_number', None)
    tan_number = taxation_data.get('tan_number', None)
    pan = taxation_data.get('pan', None)

    if 'service_tax_number' in taxation_data:
        taxation_id.service_tax_number = service_tax_number

    if 'tan_number' in taxation_data:
        taxation_id.tan_number = tan_number

    if 'pan' in taxation_data:
        taxation_id.pan = pan

    taxation_id.save()

    return taxation_id


def get_date(value):
    return None if not value else value


def save_address(address_data):
    line1 = address_data.get('line1', None)
    line2 = address_data.get('line2', None)
    line3 = address_data.get('line3', None)
    pin = address_data.get('pin', None)
    landmark = address_data.get('landmark', None)
    city_data = address_data.get('city', None)
    city_id = None if not city_data else city_data.get('id', None)
    city = get_or_none(City, id=int_or_none(city_id))

    if not line1 or not city:
        return

    address_id = address_data.get('id', None)
    try:
        address_id = int(address_id)
    except ValueError:
        address_id = None

    if address_id:
        address = get_or_none(Address, id=int_or_none(address_id))
        if not address:
            return
    else:
        address = Address()

    address.line1 = line1
    address.line2 = line2
    address.line3 = line3
    address.pin = pin
    address.landmark = landmark
    address.city_id = city.id
    address.save()

    return address


def save_broker_address(broker, address_data):
    address_id = broker.address_id
    address = get_or_none(Address, id=int_or_none(address_id)) or Address()

    address.line1 = address_data

    address.save()
    broker.address = address
    broker.save()


def create_pod(request):
    print(request.data.url)
    url = "https://s3.ap-south-1.amazonaws.com/aahodocuments/uploads/pod/005qymh307ozv6usvkgwudbw8/crp170412003.jpeg"
    url_details = url.split('/')
    S3Upload.objects.filter(uuid='005qymh307ozv6usvkgwudbw8').delete()
    if url_details and url_details[5] == 'pod':
        s3_upload = S3Upload.objects.create(
            folder='/'.join(url_details[4:6]),
            filename=url_details[7],
            bucket=url_details[3],
            uuid=url_details[6],
            uploaded=True,
            uploaded_on=datetime.now()
        )


def parse_pod_data():
    json_data = {u'uuid': u'c0e28be3-126f-4f2f-af92-a289048a3b3d',
                 u'url': u'https://fmsdocuments.s3.amazonaws.com/uploads/pod/c0e28be3-126f-4f2f-af92-a289048a3b3d/dem180224002.jpg',
                 u'lr_number': u'DEM180224002', u'fileName': u'dem180224002.jpg', u'bucketName': u'fmsdocuments',
                 u'podData': u'[{"bucketname":"fmsdocuments","displayUrl":"https://s3-ap-southeast-1.amazonaws.com/fmsdocuments/uploads/pod/c6292b9a-3113-4e44-a3b4-d005c67cb934/dem180224002.jpg","filename":"dem180224002.jpg","foldername":"uploads/pod","thumbUrl":"https://fmsdocuments.s3.amazonaws.com/uploads/pod/c6292b9a-3113-4e44-a3b4-d005c67cb934/thumbnail-dem180224002.jpg","url":"https://fmsdocuments.s3.amazonaws.com/uploads/pod/c6292b9a-3113-4e44-a3b4-d005c67cb934/dem180224002.jpg","uuid":"c6292b9a-3113-4e44-a3b4-d005c67cb934"},{"bucketname":"fmsdocuments","displayUrl":"https://s3-ap-southeast-1.amazonaws.com/fmsdocuments/uploads/pod/c0e28be3-126f-4f2f-af92-a289048a3b3d/dem180224002.jpg","filename":"dem180224002.jpg","foldername":"uploads/pod","thumbUrl":"https://fmsdocuments.s3.amazonaws.com/uploads/pod/c0e28be3-126f-4f2f-af92-a289048a3b3d/thumbnail-dem180224002.jpg","url":"https://fmsdocuments.s3.amazonaws.com/uploads/pod/c0e28be3-126f-4f2f-af92-a289048a3b3d/dem180224002.jpg","uuid":"c0e28be3-126f-4f2f-af92-a289048a3b3d"}]',
                 u'displayUrl': u'https://s3-ap-southeast-1.amazonaws.com/fmsdocuments/uploads/pod/c0e28be3-126f-4f2f-af92-a289048a3b3d/dem180224002.jpg',
                 u'thumb_url': u'https://fmsdocuments.s3.amazonaws.com/uploads/pod/c0e28be3-126f-4f2f-af92-a289048a3b3d/thumbnail-dem180224002.jpg',
                 u'folderName': u'uploads/pod'}
    json_data = json.loads(json_data.get('podData'))
    for data in json.loads(json_data.get('podData')):
        s3_upload = s3util.get_or_create_s3_upload(
            bucket=data.get('bucketName', None),
            folder=data.get('folderName', None),
            filename=data.get('fileName', None),
            verified=False,
            is_valid=False,
            uuid=data.get('uuid', None),
        )
        lr = get_or_none(LrNumber, lr_number=json_data.get('lr_number'))
        pod = PODFile.objects.create(
            uploaded_by=User.objects.get(username='mani@aaho.in'),
            lr_number=get_or_none(LrNumber, lr_number=json_data.get('lr_number')),
            booking=lr.booking if isinstance(lr, LrNumber) else get_or_none(ManualBooking,
                                                                            booking_id=data.get('lr_number')),
            serial=random_id(num_digits=8),
            s3_url=data.get('url') if validate_url(data.get('url')) else None,
            s3_thumb_url=data.get('thumb_url') if validate_url(data.get('thumb_url')) else None,
            s3_upload=s3_upload,
        )
        booking = get_or_none(ManualBooking, id=int_or_none(pod.booking_id))
        if isinstance(booking, ManualBooking):
            if validate_pod_uploaded(booking):
                booking.pod_status = 'unverified'
                booking.pod_date = datetime.now()
                booking.save()
    print('success')


@api_post
@authenticated_user
def upload_pod(request):
    json_data = request.data
    for data in json.loads(json_data.get('podData')):
        s3_upload = s3util.get_or_create_s3_upload(
            bucket=data.get('bucketName', None),
            folder=data.get('folderName', None),
            filename=data.get('fileName', None),
            verified=False,
            is_valid=False,
            uuid=data.get('uuid', None),
        )
        lr = get_or_none(LrNumber, lr_number=request.data.get('lr_number'))
        pod = PODFile.objects.create(
            uploaded_by=request.user,
            lr_number=get_or_none(LrNumber, lr_number=request.data.get('lr_number')),
            booking=lr.booking if isinstance(lr, LrNumber) else get_or_none(ManualBooking,
                                                                            booking_id=data.get('lr_number')),
            serial=random_id(num_digits=8),
            s3_url=data.get('url') if validate_url(data.get('url')) else None,
            s3_thumb_url=data.get('thumb_url') if validate_url(data.get('thumb_url')) else None,
            s3_upload=s3_upload,
        )
        booking = get_or_none(ManualBooking, id=pod.booking_id)
        if isinstance(booking, ManualBooking):
            if validate_pod_uploaded(booking):
                booking.pod_status = 'unverified'
                booking.pod_date = datetime.now()
                booking.save()
    return json_success_response(msg='pod uploaded successful')
