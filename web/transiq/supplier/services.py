from datetime import datetime

import pandas as pd
from django.contrib.auth.models import User
from django.db.models import Count

from api.utils import get_or_none
from authentication.models import Profile
from broker.models import Broker
from driver.models import Driver as d_Driver
from fileupload.models import OwnerFile, VehicleFile, DriverFile
from owner.models import Vehicle as o_Vehicle, Owner
from owner.vehicle_util import compare_format
from restapi.helper_api import generate_random_lowercase_string, generate_random_uppercase_string
from supplier.models import Driver as s_Driver, DriverPhone, DriverVehicle, Vehicle as s_Vehicle, Supplier, \
    SupplierVehicle, SupplierAccountingSummary
from team.models import ManualBooking, CreditNoteSupplier, DebitNoteSupplier, CreditNoteCustomerDirectAdvance


def create_drivers():
    for driver in d_Driver.objects.all():

        if not s_Driver.objects.filter(user__profile__phone=driver.phone).exists():
            print(driver, driver.id)
            try:
                if not User.objects.filter(username=driver.phone).exists():
                    username = driver.phone
                else:
                    username = generate_random_lowercase_string(N=12)
                user = User.objects.create_user(username=username,
                                                email=None,
                                                password='aaho1234@12')
                Profile.objects.create(user=user, name=driver.name, phone=driver.phone)
                s_driver = s_Driver.objects.create(
                    user=user,
                    driving_licence_number=driver.driving_licence_number,
                    driving_licence_validity=driver.driving_licence_validity,
                    driving_licence_location=driver.driving_licence_location,
                    smartphone_available=driver.smartphone_available,
                    created_by=User.objects.get(username='mani@aaho.in'),
                    changed_by=User.objects.get(username='mani@aaho.in')
                )
                DriverPhone.objects.create(driver=s_driver, phone=driver.phone,
                                           created_by=User.objects.get(username='mani@aaho.in'),
                                           changed_by=User.objects.get(username='mani@aaho.in'))
            except:
                print(driver.phone)


def create_vehicles():
    for vehicle in o_Vehicle.objects.all():
        if not s_Vehicle.objects.filter(vehicle_number=compare_format(vehicle.vehicle_number)).exists():
            print(vehicle)
            s_vehicle = s_Vehicle.objects.create(
                vehicle_number=compare_format(vehicle.vehicle_number),
                vehicle_type=vehicle.vehicle_type,
                vehicle_capacity=vehicle.vehicle_capacity,
                created_by=User.objects.get(username='mani@aaho.in'),
                changed_by=User.objects.get(username='mani@aaho.in')
            )
            if vehicle.driver and s_Driver.objects.filter(user__profile__phone=vehicle.driver.phone).exists():
                DriverVehicle.objects.create(
                    driver=s_Driver.objects.get(user__profile__phone=vehicle.driver.phone),
                    vehicle=s_vehicle,
                    created_by=User.objects.get(username='mani@aaho.in'),
                    changed_by=User.objects.get(username='mani@aaho.in')
                )


def generate_supplier_code():
    code = generate_random_uppercase_string(N=4)
    while Supplier.objects.filter(code=code).exists():
        code = generate_random_uppercase_string(N=4)
    return code


def create_supplier():
    df = pd.read_excel('../../data/owner.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        if not row['correct owner'] or row['id'] == row['correct owner']:
            supplier = Supplier.objects.create(user=User.objects.get(username=row['username']),
                                               created_by=User.objects.get(username='mani@aaho.in'),
                                               changed_by=User.objects.get(username='mani@aaho.in'),
                                               code=generate_supplier_code()
                                               )
            for vehicle in row['vehicles'].split('\n'):
                if vehicle:
                    vehicle_instance = get_or_none(s_Vehicle, vehicle_number=vehicle)
                    if isinstance(vehicle_instance, s_Vehicle):
                        print(vehicle)
                        SupplierVehicle.objects.create(vehicle=vehicle_instance, supplier=supplier, ownership='O',
                                                       created_by=User.objects.get(username='mani@aaho.in'),
                                                       changed_by=User.objects.get(username='mani@aaho.in'))


def create_broker_supplier():
    df = pd.read_excel('../../data/brokers.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        if not row['correct broker'] or row['id'] == row['correct broker']:
            if not Supplier.objects.filter(user=User.objects.get(username=row['username'])).exists():
                supplier = Supplier.objects.create(user=User.objects.get(username=row['username']),
                                                   created_by=User.objects.get(username='mani@aaho.in'),
                                                   changed_by=User.objects.get(username='mani@aaho.in'),
                                                   code=generate_supplier_code()
                                                   )
                for vehicle in row['vehicles'].split('\n'):
                    vehicle = compare_format(vehicle)
                    if vehicle:
                        vehicle_instance = get_or_none(s_Vehicle, vehicle_number=vehicle)
                        if isinstance(vehicle_instance, s_Vehicle):
                            print(vehicle)
                            try:
                                SupplierVehicle.objects.create(vehicle=vehicle_instance, supplier=supplier,
                                                               ownership='B',
                                                               created_by=User.objects.get(username='mani@aaho.in'),
                                                               changed_by=User.objects.get(username='mani@aaho.in'))
                            except:
                                pass


def create_broker_vehicle():
    for supplier in Supplier.objects.all():
        broker = get_or_none(Broker, name=supplier.user)
        if isinstance(broker, Broker):
            for bv in broker.broker_vehicle.all():
                vehicle_number = compare_format(bv.vehicle.vehicle_number)
                s_vehicle = get_or_none(s_Vehicle, vehicle_number=vehicle_number)
                if isinstance(s_vehicle, s_Vehicle) and not SupplierVehicle.objects.filter(supplier=supplier,
                                                                                           vehicle=s_vehicle,
                                                                                           ownership='B').exists():
                    SupplierVehicle.objects.create(supplier=supplier, vehicle=s_vehicle, ownership='B')


def merge_supplier_vehicles():
    os = Supplier.objects.get(id=873)
    ds = Supplier.objects.get(id=876)
    print(ds.suppliervehicle_set.exclude(vehicle_id__in=os.suppliervehicle_set.values_list('id', flat=True)))
    for sv in ds.suppliervehicle_set.exclude(vehicle_id__in=os.suppliervehicle_set.values_list('id', flat=True)):
        print(sv.vehicle)
        try:
            if not SupplierVehicle.objects.filter(supplier=os, vehicle=sv.vehicle, ownership='B').exists():
                SupplierVehicle.objects.filter(supplier=ds, vehicle=sv.vehicle).update(supplier=os)
            if SupplierVehicle.objects.filter(supplier=ds, vehicle=sv.vehicle,
                                              ownership='O').exists() and SupplierVehicle.objects.filter(supplier=os,
                                                                                                         vehicle=sv.vehicle,
                                                                                                         ownership='B').exists():
                SupplierVehicle.objects.filter(supplier=ds, vehicle=sv.vehicle, ownership='O').update(ownership='B')
                SupplierVehicle.objects.filter(supplier=os, vehicle=sv.vehicle, ownership='B').update(ownership='O')


        except:
            pass


def delete_duplicate_owner_broker():
    # supplier = Supplier.objects.get(id=4660)
    for supplier in Supplier.objects.all():
        print(supplier)
        svs = supplier.suppliervehicle_set.values('vehicle_id').annotate(Count('id')).order_by().filter(id__count__gt=1)
        for row in svs:
            sv = SupplierVehicle.objects.filter(supplier=supplier, vehicle_id=row['vehicle_id'])
            sv.exclude(id=sv.first().id).update(deleted=True, deleted_on=datetime.now())


def merge_owner_data():
    oo = Owner.objects.get(id=2305)
    do = Owner.objects.get(id=2243)
    supplier = get_or_none(Supplier, user=oo.name)
    for vehicle in do.vehicle_owner.all():
        s_vehicle = get_or_none(s_Vehicle, vehicle_number=compare_format(vehicle.vehicle_number))
        if isinstance(s_vehicle, s_Vehicle):
            if not SupplierVehicle.objects.filter(vehicle=s_vehicle, ownership='O').exists():
                SupplierVehicle.objects.create(vehicle=s_vehicle, supplier=supplier,
                                               ownership='O',
                                               created_by=User.objects.get(username='mani@aaho.in'),
                                               changed_by=User.objects.get(username='mani@aaho.in'))


def get_supplier_data():
    data = []
    for supplier in Supplier.objects.all():
        data.append([
            supplier.id,
            supplier.name,
            supplier.phone,
            supplier.code,
            ','.join(
                ['{} ({})'.format(sv.vehicle.number(), sv.get_ownership_display()) for sv in
                 supplier.suppliervehicle_set.all()]),
            ''
        ])
    df = pd.DataFrame(data=data, columns=['id', 'name', 'phone', 'code', 'vehicles', 'correct_supplier'])


def update_manualbooking_supplier_data():
    for booking in ManualBooking.objects.order_by('-id'):
        if isinstance(booking.supplier, Broker):
            booking_supplier = get_or_none(Supplier, user=booking.supplier.name)
        else:
            booking_supplier = None
        if isinstance(booking.owner, Owner):
            owner_supplier = get_or_none(Supplier, user=booking.owner.name)
        else:
            owner_supplier = None
        ManualBooking.objects.filter(id=booking.id).update(booking_supplier=booking_supplier,
                                                           accounting_supplier=booking_supplier,
                                                           owner_supplier=owner_supplier)


def update_manualbooking_vehicle_data():
    for booking in ManualBooking.objects.order_by('-id'):
        print(booking)
        vehicle = get_or_none(s_Vehicle, vehicle_number=compare_format(
            booking.vehicle.vehicle_number)) if booking.vehicle else None
        ManualBooking.objects.filter(id=booking.id).update(supplier_vehicle=vehicle)


def update_manualbooking_driver_data():
    for booking in ManualBooking.objects.order_by('-id'):
        driver = get_or_none(s_Driver, user__profile__phone=booking.driver.phone) if booking.driver else None
        if isinstance(driver, s_Driver):
            print(booking.id)
            ManualBooking.objects.filter(id=booking.id).update(driver_supplier=driver)


def update_cns():
    for cns in CreditNoteSupplier.objects.all():
        supplier = get_or_none(Supplier, user=cns.broker.name) if cns.broker else None
        if isinstance(supplier, Supplier) and not CreditNoteSupplier.objects.filter(
                accounting_supplier=supplier).exists():
            print(cns)
            cns.accounting_supplier = supplier
            cns.save()


def update_dns():
    for dns in DebitNoteSupplier.objects.all():
        supplier = get_or_none(Supplier, user=dns.broker.name) if dns.broker else None
        if not DebitNoteSupplier.objects.filter(accounting_supplier=supplier).exists():
            dns.accounting_supplier = supplier
            dns.save()


def update_cnca():
    for cnca in CreditNoteCustomerDirectAdvance.objects.all():
        supplier = get_or_none(Supplier, user=cnca.broker.name) if cnca.broker else None
        if not CreditNoteCustomerDirectAdvance.objects.filter(accounting_supplier=supplier).exists():
            cnca.accounting_supplier = supplier
            cnca.save()


def cns_data():
    data = []
    for instance in CreditNoteSupplier.objects.order_by('-id'):
        data.append([
            instance.id,
            instance.broker.get_name() if instance.broker else None,
            instance.broker.get_phone() if instance.broker else None,
            instance.accounting_supplier.name if instance.accounting_supplier else None,
            instance.accounting_supplier.phone if instance.accounting_supplier else None,
            instance.accounting_supplier.id if instance.accounting_supplier else None,

        ])
    df = pd.DataFrame(data=data, columns=['id', 'broker_name', 'broker_phone', 'supplier_name', 'supplier_phone',
                                          'accounting_supplier'])
    df.to_excel('cns_data.xlsx', index=False)


def dns_data():
    data = []
    for instance in DebitNoteSupplier.objects.order_by('-id'):
        data.append([
            instance.id,
            instance.broker.get_name() if instance.broker else None,
            instance.broker.get_phone() if instance.broker else None,
            instance.accounting_supplier.name if instance.accounting_supplier else None,
            instance.accounting_supplier.phone if instance.accounting_supplier else None,
            instance.accounting_supplier.id if instance.accounting_supplier else None,

        ])
    df = pd.DataFrame(data=data, columns=['id', 'broker_name', 'broker_phone', 'supplier_name', 'supplier_phone',
                                          'accounting_supplier'])
    df.to_excel('dns_data.xlsx', index=False)


def cnca_data():
    data = []
    for instance in CreditNoteCustomerDirectAdvance.objects.order_by('-id'):
        data.append([
            instance.id,
            instance.broker.get_name() if instance.broker else None,
            instance.broker.get_phone() if instance.broker else None,
            instance.accounting_supplier.name if instance.accounting_supplier else None,
            instance.accounting_supplier.phone if instance.accounting_supplier else None,
            instance.accounting_supplier.id if instance.accounting_supplier else None,

        ])
    df = pd.DataFrame(data=data, columns=['id', 'broker_name', 'broker_phone', 'supplier_name', 'supplier_phone',
                                          'accounting_supplier'])
    df.to_excel('cnca_data.xlsx', index=False)


def supplier_data():
    data = []
    for supplier in Supplier.objects.exclude(deleted=True).order_by('user__profile__name'):
        print(supplier)
        data.append([
            supplier.id,
            supplier.user.username if supplier.user else None,
            supplier.name,
            supplier.phone,
            supplier.pan,
            supplier.aaho_office.branch_name if supplier.aaho_office else None,
            ','.join(
                ['{} ({})'.format(sv.vehicle.vehicle_number, sv.ownership) for sv in
                 supplier.suppliervehicle_set.all()])
        ])
    df = pd.DataFrame(data=data, columns=['id', 'username', 'name', 'phone', 'pan', 'aaho_office', 'vehicles'])
    df.to_excel('suppliers.xlsx', index=False)


def update_owner_fileupload():
    for instance in OwnerFile.objects.order_by('-id'):
        supplier = get_or_none(Supplier, user=instance.owner.name) if instance.owner else None
        instance.supplier = supplier
        instance.save()


def update_vehicle_fileupload():
    for instance in VehicleFile.objects.order_by('-id'):
        vehicle = get_or_none(s_Vehicle, vehicle_number=instance.vehicle.vehicle_number) if instance.vehicle else None
        instance.supplier_vehicle = vehicle
        instance.save()


def update_driver_fileupload():
    for instance in DriverFile.objects.order_by('-id'):
        driver = get_or_none(s_Driver, user__profile__phone=instance.driver.phone) if instance.driver else None
        instance.supplier_driver = driver
        instance.save()


def owner_file_data():
    data = []
    for instance in OwnerFile.objects.order_by('-id'):
        data.append([
            instance.id,
            instance.supplier.name if instance.supplier else None,
            instance.supplier.id if instance.supplier else None,
            instance.owner.get_name() if instance.owner else None,
        ])
    df = pd.DataFrame(data=data, columns=['id', 'supplier_name', 'supplier_id', 'broker_name'])
    df.to_excel('owner_file.xlsx', index=False)


def driver_file_data():
    data = []
    for instance in DriverFile.objects.order_by('-id'):
        data.append([
            instance.id,
            instance.driver.phone if instance.driver else None,
            instance.supplier_driver.user.profile.phone if instance.supplier_driver else None,
            instance.supplier_driver.id if instance.supplier_driver else None
        ])
    df = pd.DataFrame(data=data, columns=['id', 'driver_phone', 's_driver_phone', 's_driver_id'])
    df.to_excel('driver_file.xlsx', index=False)


def vehicle_file_data():
    data = []
    for instance in VehicleFile.objects.order_by('-id'):
        data.append([
            instance.id,
            instance.supplier_vehicle.vehicle_number if instance.supplier_vehicle else None,
            instance.supplier_vehicle.id if instance.supplier_vehicle else None,
            instance.vehicle.vehicle_number if instance.vehicle else None
        ])
    df = pd.DataFrame(data=data, columns=['id', 'supplier_vehicle', 'supplier_vehicle_id', 'vehicle'])
    df.to_excel('vehicle_file.xlsx', index=False)


def manual_booking_data():
    data = []
    for booking in ManualBooking.objects.order_by('-id')[:28]:
        print(booking)
        data.append([
            booking.id,
            booking.booking_id,
            booking.shipment_date,
            booking.vehicle.vehicle_number if booking.vehicle else None,
            booking.lorry_number,
            booking.supplier_vehicle.id if booking.supplier_vehicle else None,
            booking.supplier_vehicle.vehicle_number if booking.supplier_vehicle else None,
            booking.supplier.get_name() if booking.supplier else None,
            booking.supplier.get_phone() if booking.supplier else None,
            booking.truck_broker_owner_name,
            booking.truck_broker_owner_phone,
            booking.booking_supplier.id if booking.booking_supplier else None,
            booking.booking_supplier.name if booking.booking_supplier else None,
            booking.booking_supplier.phone if booking.booking_supplier else None,
            booking.accounting_supplier.id if booking.accounting_supplier else None,
            booking.accounting_supplier.name if booking.accounting_supplier else None,
            booking.accounting_supplier.phone if booking.accounting_supplier else None,
            booking.owner.get_name() if booking.owner else None,
            booking.owner.get_phone() if booking.owner else None,
            booking.truck_owner_name,
            booking.truck_owner_phone,
            booking.owner_supplier.id if booking.owner_supplier else None,
            booking.owner_supplier.name if booking.owner_supplier else None,
            booking.owner_supplier.phone if booking.owner_supplier else None,
            booking.driver_supplier.id if booking.driver_supplier else None,
            booking.driver_supplier.name if booking.driver_supplier else None,
            booking.driver_supplier.phone if booking.driver_supplier else None,
            booking.driver_supplier.driving_licence_number if booking.driver_supplier else None,
            booking.driver_supplier.driving_licence_validity if booking.driver_supplier else None,
            booking.driver.name if booking.driver else None,
            booking.driver.phone if booking.driver else None,
            booking.driver.driving_licence_number if booking.driver else None,
            booking.driver.driving_licence_validity if booking.driver else None,
            booking.driver_name,
            booking.driver_phone,
            booking.driver_dl_number,
            booking.driver_dl_validity
        ])
    df = pd.DataFrame(data=data, columns=[
        'id', 'booking_id', 'shipment_date', 'owner_vehicle_number', 'vehicle_number', 'supplier_vehicle_id',
        'supplier_vehicle_number',
        'broker_name', 'broker_phone', 'truck_broker_owner_name', 'truck_broker_owner_phone', 'booking_supplier_id',
        'booking_supplier_name',
        'booking_supplier_phone', 'accounting_supplier_id', 'accounting_supplier_name', 'accounting_supplier_phone',
        'owner_name', 'owner_phone',
        'truck_owner_name', 'truck_owner_phone', 'owner_supplier_id', 'owner_supplier_name', 'owner_supplier_phone',
        'driver_supplier_id', 'driver_supplier_name',
        'driver_supplier_phone', 'driver_supplier_dl', 'driver_supplier_dl_validity', 'driver_name', 'driver_phone',
        'driver_dl', 'driver_dl_validity', 'driver_name', 'driver_phone', 'driver_dl_number', 'driver_dl_validity'])
    df.to_excel('manual_booking_data.xlsx', index=False)


def merge_owner_in_web():
    oo = Owner.objects.get(id=2305)
    do = Owner.objects.get(id=2243)
    supplier = get_or_none(Supplier, user=oo.name)
    db = get_or_none(Broker, name=do.name)
    if isinstance(db, Broker):
        ManualBooking.objects.filter(supplier=db).update(booking_supplier=supplier, accounting_supplier=supplier)
        CreditNoteSupplier.objects.filter(broker=db).update(accounting_supplier=supplier)
        DebitNoteSupplier.objects.filter(broker=db).update(accounting_supplier=supplier)
        CreditNoteCustomerDirectAdvance.objects.filter(broker=db).update(accounting_supplier=supplier)
        ManualBooking.objects.filter(owner=do).update(owner_supplier=supplier)
    OwnerFile.objects.filter(owner=do).update(supplier=supplier)


def update_supplier_owner_info():
    for supplier in Supplier.objects.all():
        owner = get_or_none(Owner, name=supplier.user)
        if isinstance(owner, Owner):
            supplier.address = owner.owner_address
            supplier.city = owner.city
            supplier.pan = owner.pan
            # supplier.aaho_office=owner.aaho_office
            try:
                supplier.save()
            except:
                pass


def update_supplier_broker_info():
    for supplier in Supplier.objects.all():
        broker = get_or_none(Broker, name=supplier.user)
        if isinstance(broker, Broker):
            print(supplier)
            if not supplier.city:
                supplier.city = broker.city
            if not supplier.pan:
                supplier.pan = broker.pan
            supplier.aaho_office = broker.aaho_office
            supplier.save()
            for state in broker.destination_state.all():
                supplier.serving_states.add(state)


def add_latest_added_vehicle():
    for booking in ManualBooking.objects.filter(shipment_date__gte='2019-03-01', supplier_vehicle=None):
        try:
            vehicle = s_Vehicle.objects.get(vehicle_number=booking.vehicle.vehicle_number)
        except:
            vehicle = s_Vehicle.objects.create(vehicle_number=booking.vehicle_number,
                                               vehicle_type=booking.vehicle.vehicle_type,
                                               vehicle_capacity=booking.vehicle.vehicle_capacity,
                                               created_by=User.objects.get(username='mani@aaho.in'),
                                               changed_by=User.objects.get(username='mani@aaho.in'))
        ManualBooking.objects.filter(id=booking.id).update(supplier_vehicle=vehicle)


def add_latest_broker():
    for broker in Broker.objects.filter(created_on__date__gte='2019-03-01'):
        if not Supplier.objects.filter(user=broker.name):
            print(broker)
            supplier = Supplier.objects.create(user=broker.name, city=broker.city, aaho_office=broker.aaho_office)
            for state in broker.destination_state.all():
                supplier.serving_states.add(state)


def update_mb_booking_supplier():
    for booking in ManualBooking.objects.filter(booking_supplier=None):
        supplier = get_or_none(Supplier, user=booking.owner.name) if booking.owner else None
        if supplier:
            print(supplier)
            ManualBooking.objects.filter(id=booking.id).update(owner_supplier=supplier)


def update_mb_driver():
    print(ManualBooking.objects.filter(driver_supplier=None).count())
    for booking in ManualBooking.objects.filter(driver_supplier=None):
        print(booking.shipment_date)
        # driver=get_or_none(s_Driver,user__profile__phone=booking.driver_phone) if booking.driver_phone else None
        # if isinstance(driver,s_Driver):
        #     print(driver)
        #     ManualBooking.objects.filter(id=booking.id).update(driver_supplier=driver)
    #     else:
    #         driver = get_or_none(s_Driver, user__profile__phone=booking.driver_phone) if booking.driver else None
    #         ManualBooking.objects.filter(id=booking.id).update(driver_supplier=driver)


def update_supplier_vehicle_data():
    for supplier in Supplier.objects.filter(id__gte=2754):
        broker = get_or_none(Broker, name=supplier.user)
        owner = get_or_none(Owner, name=supplier.user)
        if isinstance(owner, Owner):
            supplier.pan = owner.pan
            supplier.save()
            for ov in owner.vehicle_owner.all():
                s_vehicle = get_or_none(s_Vehicle, vehicle_number=ov.vehicle_number)
                if isinstance(s_vehicle, s_Vehicle):
                    SupplierVehicle.objects.create(
                        supplier=supplier,
                        ownership='O',
                        vehicle=s_vehicle,
                        created_by=User.objects.get(username='mani@aaho.in'),
                        changed_by=User.objects.get(username='mani@aaho.in')
                    )
        if isinstance(broker, Broker):
            for bv in broker.broker_vehicle.all():
                vehicle_number = compare_format(bv.vehicle.vehicle_number)
                s_vehicle = get_or_none(s_Vehicle, vehicle_number=vehicle_number)
                if isinstance(s_vehicle, s_Vehicle) and not SupplierVehicle.objects.filter(supplier=supplier,
                                                                                           vehicle=s_vehicle,
                                                                                           ownership='B').exists():
                    SupplierVehicle.objects.create(supplier=supplier, vehicle=s_vehicle, ownership='B')


def merge_supplier():
    df = pd.read_excel('suppliers.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        if row['Merge'] and row['Merge'] != 'D':
            try:
                original_supplier = Supplier.objects.get(id=row['Merge'])
                duplicate_supplier = Supplier.objects.get(id=row['id'])
                original_profile = Profile.objects.get(user=original_supplier.user)
                duplicate_profile = Profile.objects.get(user=duplicate_supplier.user)
                print(original_supplier)
                if not original_profile.phone:
                    original_profile.phone = duplicate_profile.phone
                    original_profile.save()

                elif not original_profile.alternate_phone:
                    original_profile.alternate_phone = duplicate_profile.phone
                    original_profile.save()

                if not original_supplier.pan:
                    original_supplier.pan = duplicate_supplier.pan

                if not original_supplier.address:
                    original_supplier.address = duplicate_supplier.address

                if not original_supplier.city:
                    original_supplier.city = duplicate_supplier.city

                if not original_supplier.aaho_office:
                    original_supplier.aaho_office = duplicate_supplier.aaho_office

                if not original_supplier.aaho_poc:
                    original_supplier.aaho_poc = duplicate_supplier.aaho_poc

                original_supplier.save()
                duplicate_supplier.deleted = True
                duplicate_supplier.deleted_on = datetime.now()
                duplicate_supplier.save()
                OwnerFile.objects.filter(supplier=duplicate_supplier).update(supplier=original_supplier)
                ManualBooking.objects.filter(booking_supplier=duplicate_supplier).update(
                    booking_supplier=original_supplier)
                ManualBooking.objects.filter(accounting_supplier=duplicate_supplier).update(
                    accounting_supplier=original_supplier)
                ManualBooking.objects.filter(owner_supplier=duplicate_supplier).update(owner_supplier=original_supplier)
                SupplierAccountingSummary.objects.filter(supplier=duplicate_supplier).update(deleted=True,
                                                                                             deleted_on=datetime.now())
                CreditNoteSupplier.objects.filter(accounting_supplier=duplicate_supplier).update(
                    accounting_supplier=original_supplier)
                DebitNoteSupplier.objects.filter(accounting_supplier=duplicate_supplier).update(
                    accounting_supplier=original_supplier)
                CreditNoteCustomerDirectAdvance.objects.filter(accounting_supplier=duplicate_supplier).update(
                    accounting_supplier=original_supplier)
                for sv in duplicate_supplier.suppliervehicle_set.exclude(
                        vehicle_id__in=original_supplier.suppliervehicle_set.values_list('id', flat=True)):
                    try:
                        if not SupplierVehicle.objects.filter(supplier=original_supplier, vehicle=sv.vehicle,
                                                              ownership='B').exists():
                            SupplierVehicle.objects.filter(supplier=duplicate_supplier, vehicle=sv.vehicle).update(
                                supplier=original_supplier)
                        if SupplierVehicle.objects.filter(supplier=duplicate_supplier, vehicle=sv.vehicle,
                                                          ownership='O').exists() and SupplierVehicle.objects.filter(
                            supplier=original_supplier, vehicle=sv.vehicle, ownership='B').exists():
                            SupplierVehicle.objects.filter(supplier=duplicate_supplier, vehicle=sv.vehicle,
                                                           ownership='O').update(
                                ownership='B')
                            SupplierVehicle.objects.filter(supplier=original_supplier, vehicle=sv.vehicle,
                                                           ownership='B').update(
                                ownership='O')

                    except:
                        SupplierVehicle.objects.filter(supplier=duplicate_supplier, vehicle=sv.vehicle).update(
                            deleted=True)
            except Supplier.DoesNotExist:
                print(row)


def add_supplier_owner():
    owner = Owner.objects.get(id=2424)
    supplier = get_or_none(Supplier, user=owner.name)
    if not isinstance(supplier, Supplier):
        supplier = Supplier.objects.create(user=owner.name, pan=owner.pan, city=owner.city, changed_by=owner.changed_by,
                                           created_by=owner.created_by)
        ManualBooking.objects.filter(owner=owner).update(owner_supplier=supplier)
        for o_vehicle in owner.vehicle_owner.all():
            s_vehicle = get_or_none(s_Vehicle, vehicle_number=o_vehicle.vehicle_number)
            if isinstance(s_vehicle, s_Vehicle) and not SupplierVehicle.objects.filter(supplier=supplier,
                                                                                       vehicle=s_vehicle,
                                                                                       ownership='O'):
                SupplierVehicle.objects.create(supplier=supplier, vehicle=s_vehicle, ownership='O',
                                               changed_by=owner.changed_by, created_by=owner.created_by)
            if isinstance(s_vehicle, s_Vehicle):
                VehicleFile.objects.filter(vehicle=o_vehicle).update(supplier_vehicle=s_vehicle)
