from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from api.utils import get_or_none
from driver.models import GPSDevice, Driver, BharatGPSTrackerLog
from owner.models import Vehicle
from restapi.serializers.driver import BharatGPSTrackerLogSerializer, GPSDeviceSerializer


def update_bharat_gps_tracker_log():
    login_url = 'http://bharatgps.in/authentication/create'
    session = requests.session()
    session.get(login_url)
    login_data = {
        'email': 'rohit@aaho.in',
        'password': '123456',
    }
    login_response = session.post('http://bharatgps.in/authentication/store', data=login_data)
    device_list_soup = BeautifulSoup(login_response.content, 'lxml')
    device_list = device_list_soup.find('select', {"class": "devices_list"})
    for option in device_list.find_all('option'):
        from_datetime = (datetime.now() - timedelta(minutes=35)).strftime('%Y-%m-%d %H:%M')
        to_datetime = (datetime.now()).strftime('%Y-%m-%d %H:%M')
        payload = {
            'device_id': option['value'],
            'from_date': from_datetime[:10],
            'from_time': from_datetime[11:],
            'to_date': to_datetime[:10],
            'to_time': to_datetime[11:]
        }
        location_data = session.get('http://bharatgps.in/history/positions', params=payload)
        html_data = location_data.content
        table = BeautifulSoup(html_data, 'lxml')
        table = table.tbody
        gps_device = get_or_none(GPSDevice, device_id=option['value'])
        if not isinstance(gps_device, GPSDevice):
            gps_device_serializer = GPSDeviceSerializer(data={
                'device_id': option['value'],
                'imei': option.text,
                'device_provider': 2,

            })
            if gps_device_serializer.is_valid():
                gps_device = gps_device_serializer.save()
        vehicle = gps_device.vehicle if gps_device else None
        driver = vehicle.driver if isinstance(vehicle, Vehicle) else None
        for tr in table.findAll("tr"):
            data = {
                'latitude': '{0:.8f}'.format(float(tr['data-lat'])),
                'longitude': '{0:.8f}'.format(float(tr['data-lng'])),
                'speed': tr['data-speed'],
                'position_id': tr['data-position_id'],
                'datetime': tr['data-time'],
                'device': gps_device.id,
                'driver_name': driver.name if isinstance(driver, Driver) else None,
                'driver_number': driver.phone if isinstance(driver, Driver) else None,
                'driving_licence_number': driver.driving_licence_number if isinstance(driver, Driver) else None,
                'driver': driver.id if isinstance(driver, Driver) else None,
                'vehicle_number': vehicle.vehicle_number if isinstance(vehicle, Vehicle) else None,
                'vehicle_type':vehicle.vehicle_category
            }
            bharat_gps_log_serializer = BharatGPSTrackerLogSerializer(data=data)
            if bharat_gps_log_serializer.is_valid():
                bharat_gps_log_serializer.save()
        latest_gps_data = gps_device.bharatgpstrackerlog_set.last()
        address = session.get('http://bharatgps.in/api/geo_address', params={
            'lat': latest_gps_data.latitude,
            'lon': latest_gps_data.longitude
        })
        if isinstance(latest_gps_data, BharatGPSTrackerLog):
            gps_data = {
                'driver_name': driver.name if isinstance(driver, Driver) else None,
                'driver_number': driver.phone if isinstance(driver, Driver) else None,
                'driving_licence_number': driver.driving_licence_number if isinstance(driver, Driver) else None,
                'driver': driver.id if isinstance(driver, Driver) else None,
                'vehicle_number': vehicle.vehicle_number if isinstance(vehicle, Vehicle) else None,
                'location_time': latest_gps_data.datetime,
                'latitude': latest_gps_data.latitude,
                'longitude': latest_gps_data.longitude,
                'address': (address.content).decode("utf-8")
            }
            gps_device_serializer = GPSDeviceSerializer(instance=gps_device, data=gps_data, partial=True)
            if gps_device_serializer.is_valid():
                gps_device_serializer.save()
