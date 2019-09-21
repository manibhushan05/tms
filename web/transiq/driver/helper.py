import csv
import json
import urllib
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from decimal import Decimal
from xml.etree import ElementTree
from lxml import etree

import requests
from django.utils import timezone, dateparse

from driver.models import GPSDevice, GPSDeviceLog, TracknovateGPSDevice, TracknovateGPSDeviceLog, WaytrackerGPSDevice, \
    WaytrackerGPSDeviceLog
from owner.models import Vehicle
from owner.vehicle_util import compare_format
from team.helper.helper import to_float


def load_devices():
    reader = csv.reader('aaho-gps-devices.csv')
    existing_gps_ids = set(list(GPSDevice.objects.values_list('gps_id', flat=True)))
    to_add = []
    for index, row in enumerate(reader):
        if index == 0:
            continue
        if len(row) != 5:
            raise AssertionError('invalid csv')
        sno, phone, sim_no, imei, gps_id = row
        if gps_id not in existing_gps_ids:
            to_add.append(GPSDevice(phone=phone, sim_number=sim_no, gps_imei=imei, gps_id=gps_id))
    if to_add:
        GPSDevice.objects.bulk_create(to_add)


def do_waytracker_update():
    try:
        data = get_new_waytracker_data()
    except Exception as e:
        return
    existing_vehicle_ids = dict(WaytrackerGPSDevice.objects.values_list('vehicle_id', 'id'))
    to_create = []
    for row in data:
        vehicle_id = row['vehicle_id']
        vehicle_type, vehicle_status, driver_name, driver_number = get_vehicle_details(vehicle_id)
        if vehicle_id in existing_vehicle_ids:
            WaytrackerGPSDevice.objects.filter(id=existing_vehicle_ids[vehicle_id]).update(
                vehicle_type=vehicle_type, vehicle_status=vehicle_status,
                driver_name=driver_name, driver_number=driver_number, latitude=row['latitude'],
                longitude=row['longitude'], location_time=row['datetime']
            )
        else:
            to_create.append(
                WaytrackerGPSDevice(
                    vehicle_id=vehicle_id, vehicle_number=vehicle_id, vehicle_type=vehicle_type,
                    vehicle_status=vehicle_status, driver_name=driver_name, driver_number=driver_number,
                    latitude=row['latitude'], longitude=row['longitude'], location_time=row['datetime']
                )
            )
    WaytrackerGPSDevice.objects.bulk_create(to_create)

    vehicle_ids = [r['vehicle_id'] for r in data]
    vmap = {x.vehicle_id: x.id for x in WaytrackerGPSDevice.objects.filter(vehicle_id__in=vehicle_ids)}

    WaytrackerGPSDeviceLog.objects.bulk_create([
        WaytrackerGPSDeviceLog(
            datetime=row['datetime'],
            vehicle_id=row['vehicle_id'],
            latitude=row['latitude'], longitude=row['longitude'],
            speed=row['speed'],
            engine_on=row['engine_on'],
            device_id=vmap[row['vehicle_id']],
            vehicle_number=row['vehicle_id'],
            fuel=row['fuel'],
            nearest_site=row['nearest_site'],
            nearest_location=row['nearest_location'],
            idle_time=row['idle_time'],
        ) for row in data
    ])


def parse_waytracker_data(html_data):
    table = BeautifulSoup(html_data, 'lxml')
    table = table.tbody
    records = []
    for tr in table.findAll("tr"):
        trs = tr.findAll("td")
        gps = ((trs[3].a['onclick'])[14:-7]).split(',')
        records.append({
            "latitude": to_float(gps[0]),
            "longitude": to_float(gps[1]),
            "vehicle_id": compare_format(gps[4].replace("'", "")),
            "sno": gps[3].replace("'", ""),
            "vehicle_no": compare_format(gps[4].replace("'", "")),
            "datetime": datetime.strptime(trs[4].text, '%d %b %Y %H:%M'),
            "engine_on": (trs[5].text).lower() != 'off',
            "fuel": trs[6].text,
            "nearest_site": trs[8].text,
            "nearest_location": trs[9].text,
            "speed": trs[10].text,
            "idle_time": trs[11].text}
        )
    return records


def get_new_waytracker_data():
    login_url = 'http://waytracker.in/SiteLogin.aspx?ReturnUrl=%2f'
    home_url = 'http://waytracker.in/newHome.aspx'

    session = requests.session()
    login_page = session.get(login_url)
    login_html = etree.HTML(login_page.content)

    _viewstate = login_html.xpath("//input[@id = '__VIEWSTATE']/@value")[0]
    _viewstategenerator = login_html.xpath("//input[@id = '__VIEWSTATEGENERATOR']/@value")[0]
    _eventvalidation = login_html.xpath("//input[@id = '__EVENTVALIDATION']/@value")[0]

    login_data = {
        '__VIEWSTATE': _viewstate,
        '__VIEWSTATEGENERATOR': _viewstategenerator,
        '__EVENTVALIDATION': _eventvalidation,
        'txtUN': 'prihom',
        'txtPwd': '121212',
        'btnLogin': 'Login'
    }
    session.post(login_url, login_data)
    response = session.get(home_url)
    return parse_waytracker_data(response.content)


def do_tempogo_update():
    devices = GPSDevice.objects.all()
    for device in devices:
        try:
            last_gps_update = GPSDeviceLog.objects.filter(device=device).latest('datetime')
            from_datetime = last_gps_update.datetime.isoformat()
        except GPSDeviceLog.DoesNotExist:
            from_datetime = (timezone.now() - timedelta(days=1)).isoformat()

        request_data = {
            'vehicle_id': device.vehicle_id,
            'from_datetime': from_datetime,
            'to_datetime': timezone.now().isoformat()
        }
        base_url = 'http://54.255.174.193:8400/v1/locations'
        qs = '&'.join(['%s=%s' % (k, v) for k, v in request_data.items()])
        url = '?'.join([base_url, qs])
        req = urllib.Request(url)
        req.add_header('token',
                       'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMjkxMjFhODYtZWI0Zi00ZmUzLTlmYzEtZDgxZGIwZWMzODI5IiwiaWF0IjoxNDk1MjY0NTI1fQ.5dhPi3dUm-42y3VQ-nJc0joGpYL0rDkGDRcRyoGEzyg')
        resp = urllib.urlopen(req)
        content = resp.read()
        json_data = json.loads(content)
        locations = json_data['data']['locations']

        logs_to_add = []

        existing_location_ids = set(
            list(GPSDeviceLog.objects.filter(vehicle_id=device.vehicle_id).values_list('location_id', flat=True)))
        for loc in locations:
            loc_id = loc['id']
            if loc_id in existing_location_ids:
                continue
            lng, lat = [Decimal(l) for l in loc['location']]
            logs_to_add.append(GPSDeviceLog(
                location_id=loc_id,
                datetime=dateparse.parse_datetime(loc['timestamp']),
                vehicle_id=device.vehicle_id,
                latitude=lat, longitude=lng,
                speed=loc['speed'],
                engine_on=loc['engine_running'],
                device=device,
                vehicle_number=device.vehicle_number,
            ))
        GPSDeviceLog.objects.bulk_create(logs_to_add)


def create_test_data():
    try:
        device = GPSDevice.objects.get(vehicle_id='0234a3e8-a74e-4d29-ad55-c8d428dd6151')
    except GPSDevice.DoesNotExist:
        device = GPSDevice.objects.create(phone=9999999999, sim_number=888888888888, gps_imei='MND8888888888',
                                          gps_id='GPS/TEST/00', vehicle_id='0234a3e8-a74e-4d29-ad55-c8d428dd6151',
                                          vehicle_number='xx00xx0000')
    base_url = 'http://54.255.174.193:8400/v1/locations'
    data = {
        'vehicle_id': device.vehicle_id,
        'from_datetime': '2017-05-05T18:30:00.000Z',
        'to_datetime': timezone.now().isoformat()
    }
    qs = '&'.join(['%s=%s' % (k, v) for k, v in data.items()])
    url = '?'.join([base_url, qs])

    req = urllib.Request(url)
    req.add_header('token',
                   'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMjkxMjFhODYtZWI0Zi00ZmUzLTlmYzEtZDgxZGIwZWMzODI5IiwiaWF0IjoxNDk1MjY0NTI1fQ.5dhPi3dUm-42y3VQ-nJc0joGpYL0rDkGDRcRyoGEzyg')
    resp = urllib.urlopen(req)
    content = resp.read()
    json_data = json.loads(content)
    locations = json_data['data']['locations']

    logs_to_add = []

    existing_location_ids = set(
        list(GPSDeviceLog.objects.filter(vehicle_id=device.vehicle_id).values_list('location_id', flat=True)))
    for loc in locations:
        loc_id = loc['id']
        if loc_id in existing_location_ids:
            continue
        lng, lat = [Decimal(l) for l in loc['location']]
        logs_to_add.append(GPSDeviceLog(
            location_id=loc_id,
            datetime=dateparse.parse_datetime(loc['timestamp']),
            vehicle_id=device.vehicle_id,
            latitude=lat, longitude=lng,
            speed=loc['speed'],
            engine_on=loc['engine_running'],
            device=device,
            vehicle_number=device.vehicle_number,
        ))
    GPSDeviceLog.objects.bulk_create(logs_to_add)


def update_gps_devices():
    try:
        get_tracknovate_update()
    except Exception as e:
        print (e)
    try:
        do_tempogo_update()
    except Exception as e:
        print (e)
    try:
        do_waytracker_update()
    except Exception as e:
        print (e)


def get_tracknovate_update():
    """
    login url:
    POST http://tracknovate.com/login_tracknovate.php

    Form Data:
    username:Trilokji
    password:123456
    submit:Login

    update url:
    GET http://tracknovate.com/livetracking/test_map.php?q=all
    """

    session = requests.session()
    login_data = {
        'username': 'Trilokji',
        'password': '123456',
        'submit': 'Login'
    }
    login_response = session.post('http://tracknovate.com/login_tracknovate.php', login_data)
    if login_response.status_code != 200:
        raise AssertionError('Could not login to tracknovate')
    response = session.get('http://tracknovate.com/livetracking/test_map.php?q=all')
    data = get_marker_data(response.content)

    existing_vehicle_ids = dict(TracknovateGPSDevice.objects.values_list('vehicle_id', 'id'))

    to_create = []
    for row in data:
        vehicle_id = row['vehicle_id']
        vehicle_type, vehicle_status, driver_name, driver_number = get_vehicle_details(vehicle_id)
        if vehicle_id in existing_vehicle_ids:
            TracknovateGPSDevice.objects.filter(id=existing_vehicle_ids[vehicle_id]).update(
                phone=row['phone_number'], sim_number=row['sim_number'], current_vstatus=row['vstatus'],
                current_duration=row['duration'], vehicle_type=vehicle_type, vehicle_status=vehicle_status,
                driver_name=driver_name, driver_number=driver_number, latitude=row['latitude'],
                longitude=row['longitude'], location_time=row['datetime']
            )
        else:
            to_create.append(
                TracknovateGPSDevice(
                    phone=row['phone_number'], sim_number=row['sim_number'], vehicle_id=vehicle_id,
                    vehicle_number=vehicle_id, current_vstatus=row['vstatus'], current_duration=row['duration'],
                    vehicle_type=vehicle_type, vehicle_status=vehicle_status,
                    driver_name=driver_name, driver_number=driver_number, latitude=row['latitude'],
                    longitude=row['longitude'], location_time=row['datetime']
                )
            )
    TracknovateGPSDevice.objects.bulk_create(to_create)

    vehicle_ids = [r['vehicle_id'] for r in data]
    vmap = {x.vehicle_id: x.id for x in TracknovateGPSDevice.objects.filter(vehicle_id__in=vehicle_ids)}

    TracknovateGPSDeviceLog.objects.bulk_create([
        TracknovateGPSDeviceLog(
            datetime=row['datetime'],
            vehicle_id=row['vehicle_id'],
            latitude=row['latitude'], longitude=row['longitude'],
            speed=row['speed'],
            engine_on=row['engine_on'],
            device_id=vmap[row['vehicle_id']],
            vehicle_number=row['vehicle_id'],
        ) for row in data
    ])


def get_vehicle_details(vehicle_id):
    try:
        vehicle = Vehicle.objects.select_related('driver', 'vehicle_type').get(vehicle_number=vehicle_id)
        vehicle_type = '' if not vehicle.vehicle_type else vehicle.vehicle_type.name()
        vehicle_status = vehicle.status
        driver_name = '' if not vehicle.driver else vehicle.driver.name
        driver_number = '' if not vehicle.driver else vehicle.driver.phone
    except Vehicle.DoesNotExist:
        vehicle_type = ''
        vehicle_status = ''
        driver_name = ''
        driver_number = ''
    return vehicle_type, vehicle_status, driver_name, driver_number


"""

pull additional data for tracknovate vehicles from our database

start regular updates for both

streamlined interface for web for outward payment entry and 

geo-fencing alerts

"""


def get_marker_data(xml_str):
    tree = ElementTree.fromstring(xml_str)
    data = [{
        'latitude': Decimal(m.get('lat')),
        'longitude': Decimal(m.get('lng')),
        'datetime': datetime.strptime(m.get('date'), '%d-%m-%Y %H:%M:%S'),
        'vehicle_number': m.get('Vehicle1').strip(),
        'vehicle_id': m.get('Vehicle1').replace(' ', '').strip().lower(),
        'vstatus': m.get('vstatus'),
        'duration': m.get('duration'),
        'phone_number': m.get('sim_no'),
        'sim_number': m.get('mob_no'),
        'speed': float(m.get('speed')),
        'engine_on': (m.get('ignition').strip().lower() == 'on'),
    } for m in tree.findall('marker')]
    return data
