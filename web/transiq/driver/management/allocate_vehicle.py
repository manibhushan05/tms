import logging

from api.utils import get_or_none
from broker.models import Broker, BrokerVehicle
from driver.models import TempoGoGPSDevice
from owner.models import Vehicle


def add_gps_device_to_broker(vehicle_number, username='shobhit'):
    broker = Broker.objects.get(name__username=username)
    vehicle = get_or_none(Vehicle, vehicle_number=vehicle_number)
    if vehicle:
        if not BrokerVehicle.objects.filter(broker=broker, vehicle=vehicle).exists():
            BrokerVehicle.objects.create(broker=broker, vehicle=vehicle)
    logging.info(msg="Vehicle Attached")


def add_gps_device():
    for vehicle in TempoGoGPSDevice.objects.values_list('vehicle_number', flat=True):
        add_gps_device_to_broker(vehicle_number=vehicle)


