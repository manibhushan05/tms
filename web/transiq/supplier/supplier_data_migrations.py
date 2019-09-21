from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q, Count
import pandas as pd
from api.utils import get_or_none
from authentication.models import Profile
from broker.models import Broker, BrokerVehicle, BrokerDriver
from driver.models import Driver as d_driver
from supplier.models import Driver as s_driver, DriverPhone, DriverVehicle
from owner.models import Owner, Vehicle as o_vehicle
from supplier.models import Vehicle as s_vehicle, Supplier, SupplierVehicle
from team.models import ManualBooking
from utils.models import Bank


def check_multiple_owner_vehicle():
    ManualBooking.objects.filter(Q(truck_owner_name=None) | Q(truck_owner_name='')).exclude(
        booking_status='cancelled').update(truck_owner_name=None)
    ManualBooking.objects.filter(Q(truck_owner_phone=None) | Q(truck_owner_phone='')).exclude(
        booking_status='cancelled').update(truck_owner_phone=None)
    for vehicle in o_vehicle.objects.all():
        if vehicle.manualbooking_set.filter(shipment_date__gte='2017-12-01').exclude(
                booking_status='cancelled').count() > 0:
            booking_owner_name = set(
                vehicle.manualbooking_set.exclude(truck_owner_name=None).exclude(
                    booking_status='cancelled').values_list('truck_owner_name', flat=True))
            booking_owner_phone = set(
                vehicle.manualbooking_set.exclude(truck_owner_phone=None).exclude(
                    booking_status='cancelled').values_list('truck_owner_phone', flat=True))

            lorry_number = set(
                vehicle.manualbooking_set.exclude(lorry_number=None).values_list('lorry_number', flat=True))

            if len(booking_owner_phone) == 1 and not vehicle.owner:
                booking_owner_phone = list(booking_owner_phone)[0]
                user = get_or_none(User, username=booking_owner_phone)

                owner = Owner.objects.filter(Q(name__profile__phone=booking_owner_phone))
                print(booking_owner_name, booking_owner_phone, lorry_number, vehicle.owner,
                      get_or_none(User, username=booking_owner_phone), owner)


def make_broker_owner_user_active():
    """
    update user as active for all broker and owner so that deactived user trated as deleted
    :return:
    """
    broker_users = User.objects.filter(id__in=Broker.objects.values_list('name__id', flat=True))
    owner_users = User.objects.filter(id__in=Owner.objects.values_list('name__id', flat=True))
    broker_users.update(is_active=True)
    owner_users.update(is_active=True)
    print(broker_users.count(), owner_users.count())


def create_vehicle_booking():
    """
    Create vehicle whose manual bookings exists
    :return: None
    """
    for vehicle in o_vehicle.objects.all():
        bookings = vehicle.manualbooking_set.exclude(booking_status='cancelled')
        if bookings.count() > 0 and not s_vehicle.objects.filter(vehicle_number=vehicle.vehicle_number).exists():
            s_vehicle.objects.create(
                vehicle_number=vehicle.vehicle_number,
                vehicle_type=vehicle.vehicle_type
            )


def owner_without_vehicle():
    for owner in Owner.objects.all():
        vo = owner.vehicle_owner.all()
        if not vo:
            print(owner, vo)


def add_owner_in_supplier():
    for owner in Owner.objects.all():
        if owner.vehicle_owner.filter(
                vehicle_number__in=s_vehicle.objects.values_list('vehicle_number', flat=True)).exists():
            try:
                supplier = Supplier.objects.get(user=owner.name)
            except Supplier.DoesNotExist:
                supplier = Supplier.objects.create(user=owner.name)
            for vehicle in owner.vehicle_owner.filter(
                    vehicle_number__in=s_vehicle.objects.values_list('vehicle_number', flat=True)):
                try:
                    v = s_vehicle.objects.get(vehicle_number=vehicle.vehicle_number)
                    if not SupplierVehicle.objects.filter(supplier=supplier, vehicle=v, ownership='O').exists():
                        SupplierVehicle.objects.create(supplier=supplier, vehicle=v, ownership='O')
                except s_vehicle.DoesNotExist:
                    v = None


def add_broker_in_supplier():
    for broker in Broker.objects.all():
        if not Supplier.objects.filter(user=broker.name).exists():
            if broker.broker_vehicle.exclude(vehicle=None).exists():
                for bv in broker.broker_vehicle.all():
                    vehicle = get_or_none(s_vehicle, vehicle_number=bv.vehicle.vehicle_number)
                    if vehicle:
                        try:
                            supplier = Supplier.objects.get(user=broker.name)
                        except Supplier.DoesNotExist:
                            supplier = Supplier.objects.create(user=broker.name)
                        if not SupplierVehicle.objects.filter(supplier=supplier, vehicle=vehicle,
                                                              ownership='B').exists():
                            SupplierVehicle.objects.create(supplier=supplier, vehicle=vehicle, ownership='B')


def update_vehicle_status():
    o_vehicle.objects.filter(vehicle_number__in=s_vehicle.objects.values_list('vehicle_number', flat=True)).update(
        active=True)


def make_owner_broker_inactive():
    for broker in Broker.objects.all():
        if Supplier.objects.filter(user=broker.name):
            broker.active = True
            User.objects.filter(username=broker.name.username).update(is_active=False)
    for owner in Owner.objects.all():
        if Supplier.objects.filter(user=owner.name):
            owner.active = True
            User.objects.filter(username=owner.name.username).update(is_active=False)


def analyse_duplicate_brokers():
    brokers = Broker.objects.values('name__profile__phone').exclude(name__profile__phone='').annotate(
        phone_count=Count('name__profile__phone')).filter(
        phone_count__gt=1).order_by('phone_count')
    print(brokers)
    data = []
    for broker in brokers:
        if Owner.objects.exclude(name__profile__phone=broker['name__profile__phone']).exists():
            temp = []
            temp.append(broker['name__profile__phone'])
            temp.append(broker['phone_count'])
            for profile in Profile.objects.filter(phone=broker['name__profile__phone']):
                if not Owner.objects.filter(name=profile.user).exists():
                    temp.append(profile.name)
            data.append(temp)
    df = pd.DataFrame(data=data)
    df.to_excel('duplicate brokers.xlsx', index=False)


def analyse_duplicate_supplier():
    suppliers = Supplier.objects.values('user__profile__phone').exclude(user__profile__phone='').annotate(
        phone_count=Count('user__profile__phone')).filter(
        phone_count__gt=1).order_by('phone_count')
    for supplier in suppliers:
        print(supplier)


def add_driver():
    for driver in d_driver.objects.all():
        try:
            user = User.objects.get(username=driver.phone)
        except User.DoesNotExist:
            user = User.objects.create_user(username=driver.phone, password='TrU@86865')
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user, name=driver.name, phone=driver.phone)
        else:
            Profile.objects.filter(user=user).update(name=driver.name, phone=driver.phone)
        try:
            vehicle = o_vehicle.objects.get(driver=driver)
            vehicle = get_or_none(s_vehicle, vehicle_number=vehicle.vehicle_number)
            if not s_driver.objects.filter(user=user).exists():
                d = s_driver.objects.create(user=user, driving_licence_number=driver.driving_licence_number,
                                            driving_licence_location=driver.driving_licence_location,
                                            driving_licence_validity=driver.driving_licence_validity)
                DriverPhone.objects.create(driver=d, phone=driver.phone)
                DriverVehicle.objects.create(driver=d, vehicle=vehicle)
        except o_vehicle.DoesNotExist:
            if ManualBooking.objects.filter(driver_phone=driver.phone).exists():
                if not s_driver.objects.filter(user=user).exists():
                    d = s_driver.objects.create(user=user, driving_licence_number=driver.driving_licence_number,
                                                driving_licence_location=driver.driving_licence_location,
                                                driving_licence_validity=driver.driving_licence_validity)
                    DriverPhone.objects.create(driver=d, phone=driver.phone)
                    vehicle = ManualBooking.objects.filter(driver_phone=driver.phone).exclude(
                        vehicle=None).last().vehicle
                    DriverVehicle.objects.create(driver=d,
                                                 vehicle=s_vehicle.objects.get(vehicle_number=vehicle.vehicle_number))


def create_suppliers():
    make_broker_owner_user_active()
    create_vehicle_booking()
    add_owner_in_supplier()
    add_broker_in_supplier()
    # make_owner_broker_inactive()
    update_vehicle_status()


def get_supplier_data():
    data = []
    for supplier in Supplier.objects.exclude(deleted=True):
        data.append([
            supplier.user.username,
            supplier.name,
            supplier.phone,
            supplier.alt_phone,
            '\n'.join(
                ['{} ({})'.format(sv.vehicle.vehicle_number, sv.get_ownership_display()) for sv in
                 supplier.suppliervehicle_set.all()])
        ])
    df = pd.DataFrame(data=data, columns=['Username', 'Name', 'Phone', 'Alt Phone', 'Vehicles'])
    df.to_excel('Suppliers.xlsx', index=False)


def get_vehicles_data():
    data = []
    for vehicle in s_vehicle.objects.exclude(deleted=True):
        data.append([
            vehicle.vehicle_number,
            vehicle.vehicle_category
        ])
    df = pd.DataFrame(data=data, columns=['Vehicle Number', 'Category'])
    df.to_excel('Vehicles.xlsx', index=False)


def get_supplier_vehicle_data():
    data = []
    for sv in SupplierVehicle.objects.exclude(deleted=True):
        data.append([
            sv.supplier.name,
            sv.vehicle.vehicle_number,
            sv.get_ownership_display()
        ])
    df = pd.DataFrame(data=data, columns=['Supplier', 'Vehicle', 'Ownership'])
    df.to_excel('SupplierVehicle.xlsx', index=False)


def remove_dupplicate_supplier(username1, username2):
    broker1 = Broker.objects.get(name=User.objects.get(username=username1))
    broker2 = Broker.objects.get(name=User.objects.get(username=username2))
    ManualBooking.objects.filter(supplier=broker1).update(supplier=broker2)
    # Owner.objects.filter(name=User.objects.get(username=username1)).update(name=User.objects.get(username=username2))
    for bv in BrokerVehicle.objects.filter(broker=broker1):
        print(bv)
        try:
            BrokerVehicle.objects.filter(id=bv.id).update(broker=broker2)
        except IntegrityError:
            print(bv)
            pass
        # BrokerVehicle.objects.filter(broker=broker1).update(broker=None)
    for bv in BrokerDriver.objects.filter(broker=broker1):
        print(bv)
        try:
            BrokerDriver.objects.filter(id=bv.id).update(broker=broker2)
        except IntegrityError:
            print(bv)
            pass
            # BrokerDriver.objects.filter(broker=broker1).update(broker=None)

    # Broker.objects.filter(
    #     name=User.objects.get(username='9853534696')).update(name=User.objects.get(username='gbehera'))
    Bank.objects.filter(
        user=User.objects.get(username=username1)).update(user=User.objects.get(username=username2))


def check_dupplicate_supplier():
    profiles = Profile.objects.filter(name__iexact='Bharti Transport')
    # Broker.objects.filter(
    #     name=User.objects.get(username='9853534696')).update(name=User.objects.get(username='gbehera'))
    username1 = 'altafaliansari'
    username2 = '9327778044'
    remove_dupplicate_supplier(username1, username2)
    # Bank.objects.filter(
    #     user=User.objects.get(username=username1)).update(user=User.objects.get(username=username2))

    for profile in profiles:
        print(Broker.objects.filter(name=profile.user), profile.user)
        print(Owner.objects.filter(name=profile.user), profile.user)
