import time

import requests
from api.models import google_reverse_geocode
from team.models import ManualBooking


def reverse_geocoding(lat, lng):
    login_url = 'http://bharatgps.in/authentication/create'
    session = requests.session()
    session.get(login_url)
    login_data = {
        'email': 'rohit@aaho.in',
        'password': '123456',
    }
    session.post('http://bharatgps.in/authentication/store', data=login_data)
    address = session.get('http://bharatgps.in/api/geo_address', params={
        'lat': lat,
        'lon': lng
    })
    return address


def create_dynamo_gps_device_item(gps_device):
    from restapi.dynamo.gps_serialiser import GPSDeviceSerializers
    gps_device_provider = gps_device['device_provider']
    gps_device.pop('device_provider')
    gps_device.update({'gps_device_provider': gps_device_provider})
    gps_device.pop('driver')
    gps_device.pop('vehicle')
    gps_device.update({'is_active': True})
    gps_device.update({'latitude': 0.0})
    gps_device.update({'longitude': 0.0})
    # time.sleep(2)
    gps_device_serializer = GPSDeviceSerializers(data=gps_device)
    if gps_device_serializer.is_valid():
        gps_device_serializer.save()


def update_dynamo_gps_device_item(device_id, gps_device):
    from restapi.dynamo.config import DynamoTablesEnvConfiguration
    from restapi.dynamo.gps_serialiser import GPSDeviceSerializers
    from restapi.dynamo.utils import DynamoTable
    # time.sleep(3)
    dtc = DynamoTablesEnvConfiguration()
    gps_dt = DynamoTable(dtc.GPS_LOCATION)
    item = gps_dt.get_item(device_id)
    gps_device_serializer = GPSDeviceSerializers(instance=item, data=gps_device)
    if gps_device_serializer.is_valid():
        gps_device_serializer.save()


def update_booking_status_mapping_location(gps_device):
    from restapi.models import BookingStatusesMapping, BookingStatusesMappingLocation
    from restapi.serializers.task_dashboard import BookingStatusesMappingLocationSerializer
    if gps_device:
        booking = gps_device.vehicle.manualbooking_set.exclude(booking_status='cancelled').order_by('id').last()
        if isinstance(booking, ManualBooking):
            bsm = BookingStatusesMapping.objects.filter(manual_booking=booking).order_by('-id')[:1]
            if bsm:
                reverse_geocode = google_reverse_geocode(gps_device.latitude, gps_device.longitude)
                data = {
                    'booking_status_mapping_id': bsm[0].id,
                    'city': reverse_geocode['district'],
                    'district': reverse_geocode['district'],
                    'state': reverse_geocode['state'],
                    'latitude': reverse_geocode['latitude'],
                    'longitude': reverse_geocode['longitude'],
                    'country': 'India'
                }
                booking_statuses_mapping_location_serializer = BookingStatusesMappingLocationSerializer(data=data)
                if booking_statuses_mapping_location_serializer.is_valid():
                    bsmls = booking_statuses_mapping_location_serializer.save()
                    BookingStatusesMappingLocation.objects.filter(id=bsmls.id).update(created_on=gps_device.location_time)
                else:
                    print('GPS Location update did not work '+ str(booking_statuses_mapping_location_serializer.errors))
            else:
                print('BookingStatusesMapping Not found for vehicle:' + gps_device.vehicle.vehicle_number)


#For testing purpose
# def createGPSDeviceandUpdateBSM():
#     # vehicle_obj = get_or_none(Vehicle, vehicle_number='MH23JK8980')
#     # instance = GPSDevice.objects.create(latitude=19.08, longitude=72.78, location_time=datetime.now(),
#     #                          driver_name="Fakhar Zaman", driver_number="7878787878",
#     #                          driving_licence_number="MH78JKK90898990", vehicle_number="MH78NK9000",
#     #                          address="Mumbai choupati goregaon jksjfks", vehicle=vehicle_obj)
#     instance = GPSDevice.objects.get(id=15)
#     update_booking_status_mapping_location(instance)
