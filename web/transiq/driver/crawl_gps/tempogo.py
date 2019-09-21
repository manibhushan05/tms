from datetime import datetime, timedelta

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from api.utils import get_or_none
from driver.crawl_gps.common import reverse_geocoding, update_booking_status_mapping_location, \
    update_dynamo_gps_device_item, create_dynamo_gps_device_item
from driver.models import TempoGoGPSDevice, Driver, TempoGoGPSDeviceLog, GPSDevice
from owner.models import Vehicle
from owner.vehicle_util import compare_format


def get_config(client_id, client_secret_id):
    config = {}
    config['domain'] = 'https://api.tempogo.com/'
    config['accessTokenUri'] = config['domain'] + 'oauth/token'
    config['vehiclesUri'] = config['domain'] + 'v1/vehicles'
    config['clientId'] = client_id
    config['clientSecret'] = client_secret_id
    return config


TEMPOGO_USERS = [
    {'client_id': '5304602913', 'client_secret_id': 'JgkKcJWD8LAmTAEmD9BpP384IPln02J6'},
    {'client_id': '8786079392', 'client_secret_id': '9lpAoJdv1qtVKAiwp0kkoEJydUISS8wJ'}
]


def update_tempogo_devices_locations():
    from restapi.serializers.driver import TempoGoGPSDeviceSerializer, GPSDeviceSerializer, \
        TempoGoGPSDeviceLogSerializer
    for user in TEMPOGO_USERS:
        config = get_config(client_id=user['client_id'], client_secret_id=user['client_secret_id'])
        client_id = config['clientId']
        client_secret = config['clientSecret']
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        oauth.fetch_token(
            token_url=config['accessTokenUri'], client_id=client_id, client_secret=client_secret)
        from_datetime = (datetime.utcnow() - timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
        to_datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        vehicle_list_response = oauth.get(config['vehiclesUri']).json()
        if vehicle_list_response.get('status', False):
            for vehicle in vehicle_list_response['data']:
                vehicle_obj = get_or_none(Vehicle,
                                          vehicle_number=compare_format(vehicle.get('registration_number', None)))
                driver_obj = vehicle_obj.driver if isinstance(vehicle_obj, Vehicle) else None
                gps_device_data = {
                    'device_id': vehicle.get('id', None),
                    'imei': vehicle.get('imei', None),
                    'vehicle_number': vehicle_obj.vehicle_number if isinstance(vehicle_obj, Vehicle) else None,
                    'device_provider': 1,
                    'driver_name': driver_obj.name if isinstance(driver_obj, Driver) else None,
                    'driver_number': driver_obj.phone if isinstance(driver_obj, Driver) else None,
                    'driving_licence_number': driver_obj.driving_licence_number if isinstance(
                        driver_obj, Driver) else None,
                    'driver': driver_obj.id if isinstance(driver_obj, Driver) else None,
                    'vehicle_type': vehicle_obj.vehicle_category if vehicle_obj else None,
                    'vehicle': vehicle_obj.id if isinstance(vehicle_obj, Vehicle) else None,
                }
                gps_device_serializer = GPSDeviceSerializer(data=gps_device_data)
                if gps_device_serializer.is_valid():
                    gps_device = gps_device_serializer.save()
                create_dynamo_gps_device_item(gps_device_data)
                gps_device = GPSDevice.objects.filter(device_id=vehicle.get('id', None), device_provider=1).last()
                tempogo_gps_device_serializer = TempoGoGPSDeviceSerializer(data=gps_device_data)
                if tempogo_gps_device_serializer.is_valid():
                    tempogo_gps_device_serializer.save()
                tempogo_device = TempoGoGPSDevice.objects.filter(device_id=vehicle.get('id', None)).last()

                if gps_device:
                    gps_log_response = oauth.get(
                        '{}/{}/locations?from_datetime={}&to_datetime={}'.format(
                            config['vehiclesUri'], gps_device.device_id, from_datetime, to_datetime)
                    ).json()
                    if gps_log_response.get('status', False):
                        for gps_log in gps_log_response['data']:
                            tempogo_gps_log_data = dict(
                                device=tempogo_device.id,
                                gps_log_id=gps_log['id'],
                                datetime=gps_log['timestamp'],
                                vehicle_id=gps_device.device_id,
                                latitude='{0:.8f}'.format(float(gps_log['location'][1])),
                                longitude='{0:.8f}'.format(float(gps_log['location'][0])),
                                speed=gps_log['speed'],

                                # driver and vehicle info
                                driver_name=gps_device.driver_name,
                                driver_number=gps_device.driver_number,
                                driving_licence_number=gps_device.driving_licence_number,
                                vehicle_number=gps_device.vehicle_number,
                            )
                            tempogo_gps_log_serializer = TempoGoGPSDeviceLogSerializer(data=tempogo_gps_log_data)
                            if tempogo_gps_log_serializer.is_valid():
                                tempogo_gps_log_serializer.save()
                if isinstance(tempogo_device, TempoGoGPSDevice) and isinstance(gps_device, GPSDevice):
                    tempogo_gps_log = tempogo_device.device_logs.last()
                    if isinstance(tempogo_gps_log, TempoGoGPSDeviceLog):
                        address = reverse_geocoding(lat=tempogo_gps_log.latitude,
                                                    lng=tempogo_gps_log.longitude).content.decode("utf-8")
                        print(address)
                        update_data = {
                                'latitude': tempogo_gps_log.latitude,
                                'longitude': tempogo_gps_log.longitude,
                                'location_time': tempogo_gps_log.datetime+timedelta(hours=5,minutes=30),
                                'driver_name': tempogo_gps_log.driver_name,
                                'driver_number': tempogo_gps_log.driver_number if tempogo_gps_log.driver_number else None,
                                'driving_licence_number': tempogo_gps_log.driving_licence_number if tempogo_gps_log.driving_licence_number else None,
                                'vehicle_number': tempogo_gps_log.vehicle_number if tempogo_gps_log.vehicle_number else None,
                                'address': address
                            }
                        gps_device_serializer = GPSDeviceSerializer(
                            instance=gps_device,
                            data={
                                'latitude': tempogo_gps_log.latitude,
                                'longitude': tempogo_gps_log.longitude,
                                'location_time': tempogo_gps_log.datetime+timedelta(hours=5,minutes=30),
                                'driver_name': tempogo_gps_log.driver_name,
                                'driver_number': tempogo_gps_log.driver_number,
                                'driving_licence_number': tempogo_gps_log.driving_licence_number,
                                'vehicle_number': tempogo_gps_log.vehicle_number,
                                'address': address
                            },
                            partial=True)
                        if gps_device_serializer.is_valid():
                            gps_device_latest_instance=gps_device_serializer.save()
                        update_dynamo_gps_device_item(vehicle.get('id', None), update_data)
                        tempogo_gps_device_serializer = TempoGoGPSDeviceSerializer(
                            instance=tempogo_device, data={
                                'latitude': tempogo_gps_log.latitude,
                                'longitude': tempogo_gps_log.longitude,
                                'location_time': tempogo_gps_log.datetime,
                                'driver_name': tempogo_gps_log.driver_name,
                                'driver_number': tempogo_gps_log.driver_number,
                                'driving_licence_number': tempogo_gps_log.driving_licence_number,
                                'vehicle_number': tempogo_gps_log.vehicle_number,

                            }, partial=True)
                        if tempogo_gps_device_serializer.is_valid():
                            tempogo_gps_device_serializer.save()
