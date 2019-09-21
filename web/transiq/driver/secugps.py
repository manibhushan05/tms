import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from django.db.utils import DataError

from driver.models import SecuGPSDevice, SecuGPSDeviceLog
from owner.models import Vehicle
from owner.vehicle_util import compare_format

day_endings = {
    1: 'st',
    2: 'nd',
    3: 'rd',
    21: 'st',
    22: 'nd',
    23: 'rd',
    31: 'st'
}


def custom_strftime(format, t):
    return datetime.strftime(format, t).replace('{TH}', str(t[2]) + day_endings.get(t[2], 'th'))


def format_secugps_datetime(log_time):
    try:
        return datetime.strptime(log_time, '%a %d %b %Y %H:%M:%S')
    except:
        return datetime.utcnow().now()


def update_secugps_device(df):
    for i, rows in df.iterrows():
        try:
            veh = Vehicle.objects.get(vehicle_number=compare_format(rows['vehicle_number']))
            if SecuGPSDevice.objects.filter(device_id__iexact=rows['deviceID']):
                gps = SecuGPSDevice.objects.get(device_id__iexact=rows['deviceID'])
                gps.imei = rows['imei']
                gps.latitude = rows['latitude']
                gps.longitude = rows['longitude']
                gps.address = rows['address']
                gps.status = rows['status']
                gps.vehicle_number = rows['vehicle_number']
                gps.location_time = datetime.utcnow().now()
                if veh.driver:
                    gps.driver_name = veh.driver.name
                    gps.driver_number = veh.driver.phone
                    gps.driver = veh.driver
                    gps.driving_licence_number = veh.driver.driving_licence_number
                gps.save()
            else:
                secugps_device = SecuGPSDevice.objects.create(
                    device_id=rows['deviceID'],
                    imei=rows['imei'],
                    latitude=rows['latitude'],
                    longitude=rows['longitude'],
                    address=rows['address'],
                    status=rows['status'],
                    vehicle_number=rows['vehicle_number'],
                    location_time=datetime.utcnow().now(),

                )
                if veh.driver:
                    if veh.driver:
                        secugps_device.driver_name = veh.driver.name
                        secugps_device.driver_number = veh.driver.phone
                        secugps_device.driver = veh.driver
                        secugps_device.driving_licence_number = veh.driver.driving_licence_number
                        secugps_device.save()


        except (Vehicle.DoesNotExist, Vehicle.MultipleObjectsReturned) as e:
            pass


def update_secugps_device_log(df, device_id):
    for i, rows in df.iterrows():
        try:
            veh = Vehicle.objects.get(vehicle_number=compare_format(rows['vehicle_number']))
            if SecuGPSDevice.objects.filter(device_id__iexact=device_id):
                secugps_device_log = SecuGPSDeviceLog.objects.create(
                    device=SecuGPSDevice.objects.get(device_id__iexact=device_id),
                    datetime=format_secugps_datetime(rows['datetime']),
                    vehicle_id=device_id,
                    latitude=rows['latitude'],
                    longitude=rows['longitude'],
                    speed=rows['latitude'],
                    vehicle_number=rows['vehicle_number'],
                )
                if veh.driver:
                    secugps_device_log.driver_name = veh.driver.name
                    secugps_device_log.driver_number = veh.driver.phone
                    secugps_device_log.driving_licence_number = veh.driver.driving_licence_number
                    secugps_device_log.save()
        except (Vehicle.DoesNotExist, Vehicle.MultipleObjectsReturned, DataError) as e:
            raise


def parse_secugps(html_data):
    table = BeautifulSoup(html_data, 'lxml')
    table = table.tbody
    records = []
    for tr in table.findAll("tr"):
        trs = tr.findAll("td")
        record = []
        try:
            record.append((compare_format(trs[2].text).replace('\n', '')))
            record.append(trs[3].text)
            record.append(re.findall(r'\d+', trs[2].a['onclick'])[0])
            record.append('|'.join([re.findall(r'\d+', trs[2].a['onclick'])[0], ((trs[2].text).replace('\n', ''))]))
            record.append(trs[4].text)
            address = trs[8].text.replace('\t', '').strip()
            record.append(re.sub(r'\(.*\)', '', address))
            location = ((trs[9].a['href'])[38:]).split(',')
            record.append(float(location[0]))
            record.append(float(location[1]))
            records.append(record)
        except IndexError:
            # print tr
            pass
    df = pd.DataFrame(data=records,
                      columns=['vehicle_number', 'status', 'imei', 'deviceID', 'Total Kms', 'address', 'latitude',
                               'longitude'])
    return df


def parse_secugps_speed(html_data):
    table = BeautifulSoup(html_data, 'lxml')
    table = table.tbody
    records = []
    for tr in table.findAll("tr"):
        trs = tr.findAll("td")
        record = []
        try:
            record.append((compare_format(trs[0].text).replace('\n', '')))
            log_time = trs[1].text
            record.append(log_time[:6] + log_time[8:])
            record.append(float((trs[2].text).split(' ')[0]))
            location = ((trs[3].a['href'])[38:]).split(',')
            record.append(float(location[0]))
            record.append(float(location[1]))
            records.append(record)
        except IndexError:
            pass
    df = pd.DataFrame(data=records, columns=['vehicle_number', 'datetime', 'speed', 'latitude', 'longitude'])
    return df


def secugps_device_log_updates():
    session = requests.session()
    login_data = {
        'account': 'JDKHALSA',
        'password': '12345678',
        'rememberme': 'fasle',
    }
    login_response = session.post('http://54.169.20.116/gpslite/login-exec.php', data=login_data)
    if login_response.status_code != 200:
        raise AssertionError('Could not login to secugps')
    secu_gps_device_df = parse_secugps(html_data=login_response.content)
    update_secugps_device(secu_gps_device_df)
    for i, rows in secu_gps_device_df.iterrows():
        data = {
            'imei': rows['deviceID'],
            'startdate': datetime.utcnow().now() - timedelta(minutes=16),
            'enddate': datetime.utcnow().now(),
            'minSpeed': '0',
            'maxSpeed': '200',
            'minFuel': '',
            'maxFuel': '',
            'minOdo': '',
            'maxOdo': '',
            'reportType': 'speed',
            'eventInterval': '',
            'geozoneid': '',
            'geozonetype': '',
            'frfirstDerivative': '',
            'ftfirstDerivative': '',
            'frsecondDerivative': '',
            'ftsecondDerivative': '',
            'frspeed': '',
            'ftspeed': '',
            'frIgnitionStatus': '',
            'ftIgnitionStatus': '',
            'frIdleWaitingTime': '',
            'ftIdleWaitingTime': ''
        }
        response = session.post('http://54.169.20.116/gpslite/getPerformanceReport.php', data=data)
        secu_gps_device_log_df = parse_secugps_speed(response.content)
        update_secugps_device_log(secu_gps_device_log_df, device_id=rows['deviceID'])
