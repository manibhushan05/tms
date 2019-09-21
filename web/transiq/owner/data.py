from django.db.models import Q

from owner.models import Vehicle, Owner
import pandas as pd

from owner.vehicle_util import compare_format
from team.models import ManualBooking


def vehicle_booking_data():
    data = []
    for vehicle in Vehicle.objects.order_by('-id'):
        data.append([
            vehicle.id,
            vehicle.vehicle_number,
            vehicle.vehicle_category,
            vehicle.manualbooking_set.exclude(booking_status='cancelled').count(),
            vehicle.manualbooking_set.exclude(booking_status='cancelled').order_by('shipment_date')[
                0].shipment_date.strftime('%d-%b-%Y') if vehicle.manualbooking_set.exclude(
                booking_status='cancelled').exists() else None,
            vehicle.manualbooking_set.exclude(booking_status='cancelled').order_by('-shipment_date')[
                0].shipment_date.strftime('%d-%b-%Y') if vehicle.manualbooking_set.exclude(
                booking_status='cancelled').exists() else None,
        ])
    df = pd.DataFrame(data=data,
                      columns=['ID', 'Vehicle Number', 'Vehicle Category', 'Number of Booking', 'First Booking Date',
                               'Latest Booking Date'])
    df.to_excel('vehicle_booking_data.xlsx', index=False)


def owner_booking_data():
    bookings=ManualBooking.objects.exclude(Q(truck_owner_name=None)&Q(truck_owner_phone=None))
    data = []
    for booking in bookings.order_by('-shipment_date'):
        try:
            vehicle = Vehicle.objects.get(vehicle_number=compare_format(booking.lorry_number))
            if not vehicle.owner:
                data.append([
                    booking.booking_id,
                    booking.shipment_date,
                    booking.vehicle.vehicle_number,
                    booking.truck_owner_name,
                    booking.truck_owner_phone
                ])
        except Vehicle.DoesNotExist:
            pass
    df = pd.DataFrame(data=data,columns=['Booking ID','Shipment Date','Vehicle Number','Owner','Phone'])
    df.to_excel('owner_without_vehicle.xlsx',index=False)
