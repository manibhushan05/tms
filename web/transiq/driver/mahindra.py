import datetime
import requests
from bs4 import BeautifulSoup
from lxml import etree

from api.utils import get_or_none
from driver.models import MahindraGPSDeviceLog, MahindraGPSDevice
from owner.models import Vehicle
from owner.vehicle_util import compare_format


def login():
    session = requests.session()
    login_data = {
        'txtUserName': '9999264334',
        'txtPassword': 'Urmila@123',
    }
    session.post('https://www.mahindradigisense.com/Release1.0/LoginPage.aspx', data=login_data)
    return session


def parse_location_data(html_data):
    soup = BeautifulSoup(html_data, 'lxml')
    tables = soup.find_all('table', attrs={'class': 'menuoff'})
    data = []
    for table in tables:
        data.append({
            'latitude': table.find('a').find('div', attrs={'class': 'latitude'}).contents[0].strip(),
            'longitude': table.find('a').find('div', attrs={'class': 'longitude'}).contents[0].strip(),
            'FuelEfficency': table.find('a').find('div', attrs={'class': 'FuelEfficency'}).contents[0].strip(),
            'VehicleHours': table.find('a').find('div', attrs={'class': 'VehicleHours'}).contents[0].strip(),
            'vehList': table.find('a').find('div', attrs={'class': 'vehList'}).contents[0].strip(),
            'vehType': table.find('a').find('div', attrs={'class': 'vehType'}).contents[0].strip(),
            'vehAddress': table.find('a').find('div', attrs={'class': 'vehAddress'}).contents[0].strip(),
            'StatusName': table.find('a').find('div', attrs={'class': 'alertImg'}).
                find('span', attrs={'class': 'StatusName'}).contents[0].strip(),
        })
    return data


def update_location_data(data):
    for row in data:
        vehicle = get_or_none(Vehicle, rc_number=compare_format(row['vehList']))
        if vehicle:
            MahindraGPSDeviceLog.objects.create(
                device=get_or_none(MahindraGPSDevice, device_id=compare_format(row['vehList'])),
                datetime=datetime.datetime.now(),
                vehicle_id=None if not vehicle else vehicle.vehicle_number,
                latitude=row['latitude'],
                longitude=row['longitude'],
                speed=0,
                fuel_efficiency=row['FuelEfficency'],
                address=None,
                status=row['StatusName'],

                # driver and vehicle info
                driver_name=vehicle.driver.name if vehicle.driver else None,
                driver_number=vehicle.driver.phone if vehicle.driver else None,
                driving_licence_number=vehicle.driver.driving_licence_number if vehicle.driver else None,
                vehicle_number=vehicle.vehicle_number,
                vehicle_type=row['vehType'],
                vehicle_status=row['StatusName']

            )


def update_vehicle_data(data):
    for row in data:
        vehicle = get_or_none(Vehicle, rc_number=compare_format(row['vehList']))
        try:
            MahindraGPSDevice.objects.get(device_id=compare_format(row['vehList']))
            MahindraGPSDevice.objects.filter(device_id=compare_format(row['vehList'])).update(
                imei=None,

                driver_name=vehicle.driver.name if vehicle.driver else None,
                driver_number=vehicle.driver.phone if vehicle.driver else None,
                driver=vehicle.driver,

                driving_licence_number=vehicle.driver.driving_licence_number if vehicle.driver else None,
                vehicle_number=vehicle.vehicle_number,
                vehicle_type=row['vehType'],
                vehicle_status=row['StatusName'],

                location_time=datetime.datetime.now(),
                latitude=row['latitude'],
                longitude=row['longitude'],
                address=None,
                status=row['StatusName']
            )
        except MahindraGPSDevice.DoesNotExist:
            MahindraGPSDevice.objects.create(
                device_id=compare_format(row['vehList']),
                imei=None,

                driver_name=vehicle.driver.name if vehicle.driver else None,
                driver_number=vehicle.driver.phone if vehicle.driver else None,
                driver=vehicle.driver,

                driving_licence_number=vehicle.driver.driving_licence_number if vehicle.driver else None,
                vehicle_number=vehicle.vehicle_number,
                vehicle_type=row['vehType'],
                vehicle_status=row['StatusName'],

                location_time=datetime.datetime.now(),
                latitude=row['latitude'],
                longitude=row['longitude'],
                address=None,
                status=row['StatusName']
            )


def mahindra_digisense_location_services():
    login_url = 'https://www.mahindradigisense.com/Release1.0/LoginPage.aspx'
    home_url = 'https://www.mahindradigisense.com/Release1.0/LocationServices.aspx'

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
        'txtUserName': '9999264334',
        'txtPassword': 'Urmila@123',
        'btnLogin': 'Login',
        'submit': 'Log In'
    }
    session.post(login_url, data=login_data)
    html_data = session.get(home_url)
    data = parse_location_data(html_data.content)
    update_location_data(data=data)
    update_vehicle_data(data=data)
