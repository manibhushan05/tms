import datetime
import json
import logging

import pandas as pd
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render

from api.decorators import authenticated_user
from api.utils import int_or_none
from driver.models import GPSLogNew, DriverAppUser, TracknovateGPSDevice, \
    TracknovateGPSDeviceLog, WaytrackerGPSDevice, WaytrackerGPSDeviceLog, TempoGoGPSDevice, TempoGoGPSDeviceLog, \
    SecuGPSDevice, SecuGPSDeviceLog, MahindraGPSDevice, MahindraGPSDeviceLog, GPSDevice


@authenticated_user
def track_vehicles(request):
    data = get_gps_data()

    df = pd.DataFrame(data,
                      columns=['latitude', 'longitude', 'vehicle_number', 'vehicle_type', 'driver_name',
                               'driver_number', 'datetime', 'vehicle_status', 'device_id', 'id'])
    data_json = df.reset_index().to_json(orient='records')
    data_json = json.loads(data_json)
    return render(request, 'team/track/track_vehicles.html', {'data': data, 'data_json': data_json})


@authenticated_user
def track_individual_veh(request):
    device_id = request.GET.get('gps_log_id')
    if not device_id:
        return HttpResponseRedirect('/team/track-vehicles/')
    dtype, did = device_id.split('-', 1)
    did = int_or_none(did)
    if dtype == 'tempogo':
        gps_data = TempoGoGPSDevice.objects.get(id=did)
    elif dtype == 'mahindra':
        gps_data = MahindraGPSDevice.objects.get(id=did)
    elif dtype == 'gpsdevice':
        gps_data = GPSDevice.objects.get(id=did)
    elif dtype == 'tracknovate':
        gps_data = TracknovateGPSDevice.objects.get(id=did)
    elif dtype == 'waytracker':
        gps_data = WaytrackerGPSDevice.objects.get(id=did)
    elif dtype == 'secugps':
        gps_data = SecuGPSDevice.objects.get(id=did)

    else:
        raise Http404

    data = get_gps_data()
    df = pd.DataFrame(data,
                      columns=['latitude', 'longitude', 'vehicle_number', 'vehicle_type', 'driver_name',
                               'driver_number', 'datetime', 'vehicle_status', 'device_id', 'id'])
    data_json = df.reset_index().to_json(orient='records')
    data_json = json.loads(data_json)
    return render(request, 'team/track/track_individual_vehicle.html', {'gps': gps_data, 'data_json': data_json})


def get_gps_data():
    """
    ['latitude', 'longitude', 'vehicle_number', 'vehicle_type', 'driver_name',
                               'driver_number', 'datetime', 'vehicle_status', 'device_id', 'id']
    """
    data = []
    devices = DriverAppUser.objects.all().exclude(latitude=None).exclude(is_active=False)
    for value in devices:
        temp = []
        try:
            temp.append(str(value.latitude))
            temp.append(str(value.longitude))
            temp.append(str(value.number()))
            temp.append(str(value.vehicle_type))
            temp.append(str(value.driver_name))
            temp.append(str(value.driver_number))
            temp.append(
                str((value.location_time + datetime.timedelta(hours=5, minutes=30)).strftime('%d, %b %Y %I:%M %p')))
            temp.append(str(value.vehicle_status))
            temp.append(str(value.device_id))
            temp.append(str('driverapp-' + str(value.id)))
            data.append(temp)
        except GPSLogNew.DoesNotExist:
            logging.error("GPS Log New does not exists for " + value.device_id)
    tdevice = WaytrackerGPSDevice.objects.exclude(is_active=False).exclude(latitude=None)
    for value in tdevice:
        temp = []
        try:
            temp.append(str(value.latitude))
            temp.append(str(value.longitude))
            temp.append(str(value.number()))
            temp.append(str(value.vehicle_type))
            temp.append(str(value.driver_name))
            temp.append(str(value.driver_number))
            temp.append(str(value.location_time.strftime('%d, %b %Y %I:%M %p')))
            temp.append(str(value.vehicle_status))
            temp.append(str(value.vehicle_id))
            temp.append(str('waytracker-' + str(value.id)))
            data.append(temp)
        except WaytrackerGPSDeviceLog.DoesNotExist:
            logging.error("Waytracker GPS Device Log does not exists for " + value.vehicle_id)
    tdevice = TempoGoGPSDevice.objects.exclude(is_active=False).exclude(latitude=None)
    for value in tdevice:
        temp = []
        try:
            temp.append(str(value.latitude))
            temp.append(str(value.longitude))
            temp.append(str(value.number()))
            temp.append(str(value.vehicle_type))
            temp.append(str(value.driver_name))
            temp.append(str(value.driver_number))
            temp.append(str(value.location_time.strftime('%d, %b %Y %I:%M %p')))
            temp.append(str(value.vehicle_status))
            temp.append(str(value.device_id))
            temp.append(str('tempogo-' + str(value.id)))
            data.append(temp)
        except TempoGoGPSDeviceLog.DoesNotExist:
            logging.error("Tempogo GPS Device Log does not exists for " + value.device_id)
    tdevice = MahindraGPSDevice.objects.exclude(is_active=False).exclude(latitude=None)
    for value in tdevice:
        temp = []
        try:
            temp.append(str(value.latitude))
            temp.append(str(value.longitude))
            temp.append(str(value.number()))
            temp.append(str(value.vehicle_type))
            temp.append(str(value.driver_name))
            temp.append(str(value.driver_number))
            temp.append(str(value.location_time.strftime('%d, %b %Y %I:%M %p')))
            temp.append(str(value.vehicle_status))
            temp.append(str(value.device_id))
            temp.append(str('mahindra-' + str(value.id)))
            data.append(temp)
        except MahindraGPSDeviceLog.DoesNotExist:
            logging.error("Mahindra GPS Device Log does not exists for " + value.device_id)
    tdevice = SecuGPSDevice.objects.exclude(is_active=False).exclude(latitude=None)
    for value in tdevice:
        temp = []
        try:
            temp.append(str(value.latitude))
            temp.append(str(value.longitude))
            temp.append(str(value.number()))
            temp.append(str(value.vehicle_type))
            temp.append(str(value.driver_name))
            temp.append(str(value.driver_number))
            temp.append(str(value.location_time.strftime('%d, %b %Y %I:%M %p')))
            temp.append(str(value.vehicle_status))
            temp.append(str(value.device_id))
            temp.append(str('secugps-' + str(value.id)))
            data.append(temp)
        except SecuGPSDeviceLog.DoesNotExist:
            logging.error("Secu GPS Device Log does not exists for " + value.device_id)
    return data
