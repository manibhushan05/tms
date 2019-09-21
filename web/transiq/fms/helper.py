from __future__ import absolute_import, print_function, division
from api.utils import get_or_none
from broker.models import BrokerVehicle, Broker
from driver.models import WaytrackerGPSDevice, TempoGoGPSDevice, SecuGPSDevice, MahindraGPSDevice
from owner.models import Vehicle
from owner.vehicle_util import compare_format


def vehicles_data_gps(vehicles):
    data = []
    gps_devices = WaytrackerGPSDevice.objects.filter(vehicle_number__in=vehicles).exclude(is_active=False).exclude(
        latitude=None)
    for gps_device in gps_devices:
        vehicle = get_or_none(Vehicle, vehicle_number=compare_format(gps_device.vehicle_number))
        data.append({
            'bearing': 0.0, 'vehicle_id': vehicle.id if isinstance(vehicle, Vehicle) else '',
            'vehicle_status': u'unloaded',
            'vehicle_number': gps_device.vehicle_number,
            'driver': gps_device.driver_json(), 'location': gps_device.location(), 'path': []
        })

    gps_devices = SecuGPSDevice.objects.filter(vehicle_number__in=vehicles).exclude(is_active=False).exclude(
        latitude=None)
    for gps_device in gps_devices:
        vehicle = get_or_none(Vehicle, vehicle_number=compare_format(gps_device.vehicle_number))
        data.append({
            'bearing': 0.0, 'vehicle_id': vehicle.id if isinstance(vehicle, Vehicle) else '',
            'vehicle_status': u'unloaded',
            'vehicle_number': gps_device.vehicle_number,
            'driver': gps_device.driver_json(), 'location': gps_device.location(), 'path': []
        })

    gps_devices = TempoGoGPSDevice.objects.filter(vehicle_number__in=vehicles).exclude(is_active=False).exclude(
        latitude=None)
    for gps_device in gps_devices:
        vehicle = get_or_none(Vehicle, vehicle_number=compare_format(gps_device.vehicle_number))
        data.append({
            'bearing': 0.0, 'vehicle_id': vehicle.id if isinstance(vehicle, Vehicle) else '',
            'vehicle_status': u'unloaded',
            'vehicle_number': gps_device.vehicle_number,
            'driver': gps_device.driver_json(), 'location': gps_device.location(), 'path': []
        })

    gps_devices = MahindraGPSDevice.objects.filter(vehicle_number__in=vehicles).exclude(is_active=False).exclude(
        latitude=None)
    for gps_device in gps_devices:
        vehicle = get_or_none(Vehicle, vehicle_number=compare_format(gps_device.vehicle_number))
        data.append({
            'bearing': 0.0, 'vehicle_id': vehicle.id if isinstance(vehicle, Vehicle) else '',
            'vehicle_status': u'unloaded',
            'vehicle_number': gps_device.vehicle_number,
            'driver': gps_device.driver_json(), 'location': gps_device.location(), 'path': []
        })
    return data


def vehicles_gps_data():
    vehicle_ids = list(
        BrokerVehicle.objects.filter(broker=Broker.objects.get(id=439)).values_list('vehicle_id', flat=True))
    vehicles = Vehicle.objects.filter(id__in=vehicle_ids).values_list('vehicle_number', flat=True)
    print(vehicles_data_gps(vehicles))
