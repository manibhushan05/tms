import pandas as pd
from django.db.models import Count, F, Q

from owner.models import Vehicle
from owner.vehicle_util import compare_format
from team.models import ManualBooking
from utils.models import City, State, VehicleCategory


def consignor_city_update():
    for booking in ManualBooking.objects.exclude(consignor_city=None):
        try:
            city = City.objects.get(name__iexact=booking.consignor_city)
        except City.DoesNotExist:
            city = None
        except City.MultipleObjectsReturned:
            city = City.objects.filter(name__iexact=booking.consignor_city).exclude(state=None).last()
        booking.consignor_city_fk = city
        booking.save()


def consignee_city_update():
    for booking in ManualBooking.objects.exclude(consignee_city=None):
        try:
            city = City.objects.get(name__iexact=booking.consignee_city)
        except City.DoesNotExist:
            city = None
        except City.MultipleObjectsReturned:
            city = City.objects.filter(name__iexact=booking.consignee_city).exclude(state=None).last()
        booking.consignee_city_fk = city
        booking.save()


def change_booking_city():
    # bookings = ManualBooking.objects.filter(from_city_fk=City.objects.get(id=648))
    # bookings.update(from_city_fk=City.objects.get(id=230))
    #
    # bookings = ManualBooking.objects.filter(to_city_fk=City.objects.get(id=648))
    # bookings.update(to_city_fk=City.objects.get(id=230))
    #
    bookings = ManualBooking.objects.filter(from_city='Dahisar')
    bookings.update(from_city_fk=City.objects.get(id=326))

    bookings = ManualBooking.objects.filter(to_city='Dahisar')
    bookings.update(to_city_fk=City.objects.get(id=326))


def check_null_value():
    exclude_kwargs = Q(total_in_ward_amount__gte=F('total_amount_to_company') - F('tds_deducted_amount')) & Q(
        total_out_ward_amount__exact=F('total_amount_to_owner')) | Q(booking_status='cancelled')
    bookings = ManualBooking.objects.filter(to_city_fk=None).exclude(exclude_kwargs).values('to_city').annotate(
        Count('to_city')).order_by('to_city__count')
    for booking in bookings:
        pass


def city_cleanup():
    df = pd.read_excel('../../data/cities-v7.xlsx')
    for i, row in df.iterrows():
        if row['Status'] == 'Delete':
            continue
        try:
            city = City.objects.get(code=row['Code'])
            try:
                state = State.objects.get(name__icontains=row['State'])
            except State.DoesNotExist:
                if row['State'] == 'Telengana':
                    state = State.objects.get(name__icontains='TELANGANA')
                else:
                    state = None
            if not city.state:
                city.state = state
                city.save()
        except City.DoesNotExist:
            pass


def update_booking_vehicle_category():
    bookings = ManualBooking.objects.filter(vehicle_category=None)
    for booking in bookings:
        try:
            vehicle = Vehicle.objects.get(vehicle_number=compare_format(booking.lorry_number))
            if isinstance(vehicle.vehicle_type, VehicleCategory) and not booking.vehicle_category:
                booking.vehicle_category = vehicle.vehicle_type
                booking.save()
        except Vehicle.DoesNotExist:
            pass


def manual_booking_city_data():
    data = []
    for booking in ManualBooking.objects.all().order_by('-shipment_date'):
        data.append([
            booking.id,
            booking.booking_id,
            booking.shipment_date,
            booking.consignor_city,
            booking.consignor_city_fk.name if booking.consignor_city_fk else '',
            booking.consignee_city,
            booking.consignee_city_fk.name if booking.consignee_city_fk else '',
            booking.from_city,
            booking.from_city_fk.name if booking.from_city_fk else '',
            booking.to_city,
            booking.to_city_fk.name if booking.to_city_fk else ''
        ])
    df = pd.DataFrame(data=data, columns=['ID', 'Booking ID', 'Shipment Date', 'Consignor City', 'Consignor City FK',
                                          'Consignee City', 'Consignee City FK', 'From City', 'From City FK', 'To City',
                                          'To City FK'])
    df.to_excel('Updated cities in bookings v2.xlsx', index=False)


def update_vehicle_fk():
    for booking in ManualBooking.objects.filter(vehicle=None):
        try:
            vehicle = Vehicle.objects.get(vehicle_number=compare_format(booking.lorry_number))
            if isinstance(vehicle, Vehicle) and not isinstance(booking.vehicle, Vehicle):
                booking.vehicle = vehicle
                booking.save()
            else:
                pass
        except Vehicle.DoesNotExist:
            if booking.lorry_number != 'NA':
                vehicle = Vehicle.objects.create(vehicle_number=compare_format(booking.lorry_number),
                                                 vehicle_type=VehicleCategory.objects.get(id=74))
                booking.vehicle = vehicle
                booking.save()

