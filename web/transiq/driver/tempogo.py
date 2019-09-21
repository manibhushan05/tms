from datetime import datetime, timedelta

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from api.utils import get_or_none
from driver.models import TempoGoGPSDevice, Driver, TempoGoGPSDeviceLog
from owner.models import Vehicle
from owner.vehicle_util import compare_format
from restapi.serializers.driver import TempoGoGPSDeviceSerializer
from restapi.serializers.owner import VehicleSerializer
from transiq.celery import app


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


def update_tempogo_devices():
    for user in TEMPOGO_USERS:
        config = get_config(client_id=user['client_id'], client_secret_id=user['client_secret_id'])
        client_id = config['clientId']
        client_secret = config['clientSecret']
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=config['accessTokenUri'], client_id=client_id,
                                  client_secret=client_secret)
        server_response = oauth.get(config['vehiclesUri'])
        json_response = server_response.json()

        if json_response['status']:
            for response in json_response['data']:
                if not Vehicle.objects.filter(
                        vehicle_number__iexact=compare_format(response['registration_number'])).exists():
                    vehicle_serializer = VehicleSerializer(
                        data={'vehicle_number': compare_format(response['registration_number']),
                              'changed_by': 'harsh@aaho.in'})
                    if vehicle_serializer.is_valid():
                        vehicle_serializer.save()
                vehicle = get_or_none(Vehicle, vehicle_number=compare_format(response['registration_number']))
                if isinstance(vehicle, Vehicle):
                    is_driver = isinstance(vehicle.driver, Driver)
                    vehicle_serializer = VehicleSerializer(instance=vehicle).data
                    tempogo_device_serializer = TempoGoGPSDeviceSerializer(
                        data=dict(
                            device_id=response['id'],
                            imei=response['imei'],
                            driver_name=vehicle_serializer['driver_data']['name'] if is_driver else None,
                            driver_number=vehicle_serializer['driver_data']['phone'] if is_driver else None,
                            driving_licence_number=vehicle_serializer['driver_data']['dl_number'],
                            driver=vehicle_serializer['driver_data']['id'] if is_driver else None,
                            vehicle_number=vehicle_serializer['vehicle_number'],
                            changed_by='mani@aaho.in'
                        )

                    )
                    if tempogo_device_serializer.is_valid():
                        pass
                    print(tempogo_device_serializer.errors)


def update_tempogo_devices_locations():
    for user in TEMPOGO_USERS:
        try:
            config = get_config(client_id=user['client_id'], client_secret_id=user['client_secret_id'])
            client_id = config['clientId']
            client_secret = config['clientSecret']
            client = BackendApplicationClient(client_id=client_id)
            oauth = OAuth2Session(client=client)
            token = oauth.fetch_token(token_url=config['accessTokenUri'], client_id=client_id,
                                      client_secret=client_secret)
            from_datetime = (datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            to_datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            for device in TempoGoGPSDevice.objects.all():
                server_response = oauth.get(config[
                                                'vehiclesUri'] + '/' + device.device_id + '/locations?from_datetime=' + from_datetime + '&to_datetime=' + to_datetime)
                json_response = server_response.json()
                if json_response['status']:
                    for gps in json_response['data']:
                        if not TempoGoGPSDeviceLog.objects.filter(gps_log_id=gps['id']).exists():
                            TempoGoGPSDeviceLog.objects.create(
                                device=device,
                                gps_log_id=gps['id'],
                                datetime=gps['timestamp'],
                                vehicle_id=device.device_id,
                                latitude=gps['location'][1],
                                longitude=gps['location'][0],
                                speed=gps['speed'],

                                # driver and vehicle info
                                driver_name=device.driver_name,
                                driver_number=device.driver_number,
                                driving_licence_number=device.driving_licence_number,
                                vehicle_number=device.vehicle_number,
                            )
                        TempoGoGPSDevice.objects.filter(device_id=device.device_id).update(
                            location_time=gps['timestamp'],
                            latitude=gps['location'][1],
                            longitude=gps['location'][0],
                            driver_name=device.driver_name,
                            driver_number=device.driver_number,
                        )
        except:
            raise
