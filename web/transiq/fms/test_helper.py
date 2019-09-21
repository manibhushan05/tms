import uuid
import random

from datetime import timedelta, datetime

from django.contrib.auth.models import User
from django.utils import timezone

from api.abstract import PASSWORD
from api.utils import in_mb, random_ids, random_id
from broker.models import BrokerVehicle, BrokerDriver, BrokerOwner, Broker
from customer.test_helper import add_app_data, add_vehicle_categories
from driver.models import Driver, DriverAppUser, GPSLogNew
from fms.models import Document
from owner.models import Owner, Vehicle
from sme.models import Sme
from transaction.models import Transaction, LoadingUnloadingAddress, VehicleRequest
from utils.models import VehicleCategory, City, Bank, TaxationID


def add_vehicle_driver_data(test, user):
    add_app_data()
    vc1, vc2 = add_vehicle_categories(test)
    test.owner, _ = Owner.objects.get_or_create(name=user)
    driver1 = Driver.objects.create(name='James Bond', phone='8978937498')
    driver2 = Driver.objects.create(name='Jason Bourne', phone='9666666666')
    driver3 = Driver.objects.create(name='Adolph Fiddler', phone='9666666665')
    test.drivers = [driver1, driver2, driver3]
    v1 = Vehicle.objects.create(vehicle_number='AB01 AB 0001', driver=driver1, owner=test.owner, vehicle_type=vc1)
    v2 = Vehicle.objects.create(vehicle_number='AB02 AB 0002', driver=driver2, owner=test.owner, vehicle_type=vc1)
    v3 = Vehicle.objects.create(vehicle_number='AB03 AB 0003', driver=driver3, owner=test.owner, vehicle_type=vc2)
    v4 = Vehicle.objects.create(vehicle_number='AB04 AB 0004', owner=test.owner, vehicle_type=vc2)
    test.vehicles = [v1, v2, v3, v4]
    BrokerVehicle.objects.bulk_create([BrokerVehicle(broker=test.broker, vehicle=v) for v in test.vehicles])
    BrokerDriver.objects.bulk_create([BrokerDriver(broker=test.broker, driver=d) for d in test.drivers])
    BrokerOwner.objects.get_or_create(broker=test.broker, owner=test.owner)


def get_bank_details():
    return dict(bank='SBI', account_holder_name='James Bond', account_number='007007007007007', account_type='SA',
                ifsc='SBIN007')


def add_vehicle_dependencies(test, user):
    test.owner, _ = Owner.objects.get_or_create(name=user)
    test.driver = Driver.objects.create(name='James Bond', phone='8978937498')
    test.driver_app_user = DriverAppUser.objects.create(
        device_id=str(uuid.uuid4()), driver_name=test.driver.name, driver_number=test.driver.phone,
        number_verified=True, driver=test.driver
    )
    test.vc = VehicleCategory.objects.create(vehicle_type='Volvo', capacity='21 Ton')


def add_vehicle_without_docs(test, user):
    add_vehicle_dependencies(test, user)
    test.vehicle = Vehicle.objects.create(
        vehicle_number='AB01 AB 0001', driver=test.driver, owner=test.owner, vehicle_type=test.vc,
        driver_app_user=test.driver_app_user, status=test.driver_app_user.vehicle_status
    )
    test.driver_app_user.vehicle_number = test.vehicle.vehicle_number
    test.driver_app_user.vehicle_type = test.vc.name()
    test.driver_app_user.save()
    account = Bank.objects.create(**get_bank_details())
    BrokerVehicle.objects.create(broker=test.broker, vehicle=test.vehicle, account_details=account)
    BrokerDriver.objects.create(broker=test.broker, driver=test.driver)
    BrokerOwner.objects.get_or_create(broker=test.broker, owner=test.owner)
    test.vehicle_id = test.vehicle.id
    test.driver_id = test.driver.id


def add_vehicle_data(test, user):
    add_vehicle_without_docs(test, user)
    add_vehicle_docs(test, user)


def test_s3_doc_keys():
    return ['test1.png', 'test2.png', 'test3.png', 'test4.png', 'test5.png', 'test6.png', 'test7.png', 'test8.png']


def create_docs(user, vehicle, owner, driver):
    s3_keys = test_s3_doc_keys()
    doc_ids = random_ids(8, num_digits=9)
    data = [
        (vehicle, 'registration_certificate', 'REG'),
        (vehicle, 'permit_certificate', 'PERM'),
        (vehicle, 'insurance_certificate', 'INS'),
        (vehicle, 'fitness_certificate', 'FIT'),
        (vehicle, 'puc_doc', 'PUC'),
        (owner, 'taxation_details', 'PAN'),
        (owner, 'declaration', 'DEC'),
        (driver, 'driving_licence', 'DL')
    ]
    docs = []
    for k, i, (b, f, t) in zip(s3_keys, doc_ids, data):
        doc = Document.new(user=user, bearer=b, field_name=f, document_type=t, document=k, doc_id=i, thumb=k)
        doc.save()
        docs.append(doc)
    return docs


def add_vehicle_docs(test, user):
    vehicle = test.vehicle
    docs = create_docs(user, vehicle, vehicle.owner, vehicle.driver)
    rc_doc, perm_doc, ins_doc, fit_doc, puc_doc, pan_doc, dec_doc, dl_doc = docs
    validity = (timezone.now() + timedelta(days=750)).date()

    vehicle.registration_certificate = rc_doc
    vehicle.registration_year = datetime(year=2015, month=1, day=1).date()
    vehicle.registration_validity = validity

    vehicle.permit_certificate = perm_doc
    vehicle.permit_type = 'All-India'
    vehicle.permit_validity = validity
    vehicle.permit = perm_doc.id

    vehicle.insurance_certificate = ins_doc
    vehicle.insurer = 'LIC'
    vehicle.insurance_validity = validity
    vehicle.insurance_number = ins_doc.id

    vehicle.fitness_certificate = fit_doc
    vehicle.fitness_certificate_validity_date = validity
    vehicle.fitness_certificate_number = fit_doc.id

    vehicle.puc_certificate = puc_doc
    vehicle.puc_certificate_validity_date = validity
    vehicle.puc_certificate_number = puc_doc.id

    owner = vehicle.owner
    taxation_details = owner.taxation_details or TaxationID()
    taxation_details.pan_doc = pan_doc
    taxation_details.pan = pan_doc.id
    taxation_details.save()

    owner.taxation_details = taxation_details
    owner.declaration = dec_doc.document
    owner.declaration_doc = dec_doc
    owner.declaration_validity = validity
    owner.save()

    driver = vehicle.driver
    driver.driving_licence_number = dl_doc.id
    driver.driving_licence = dl_doc
    driver.driving_licence_location = 'Mumbai'
    driver.driving_licence_validity = validity
    driver.save()

    vehicle.driver = driver
    vehicle.owner = owner
    vehicle.save()


def add_booking_data(test):
    add_app_data()
    vc1, vc2 = add_vehicle_categories(test)

    email, phone, admin_email = 'info+1@aaho.in', '9900700707', 'info+2@aaho.in'
    customer = User.objects.create_user(username='John Doe', password=PASSWORD, email=email)
    admin = User.objects.create_user(username='admin', password=PASSWORD, email=email)
    transaction_id = random_id(9)
    sme = Sme.objects.create(name=customer, latest_lr_serial_number=0)
    city_ids = City.objects.values_list('id', flat=True)

    test.transaction = Transaction.objects.create(
        transaction_id=transaction_id, booking_agent=customer, total_vehicle_requested='', material='rice',
        contact_person='John Doe', contact_number=phone, transaction_managed_by=admin,
        shipment_datetime=(timezone.now() + timedelta(days=4)), expected_rate='300.0'
    )
    data = [
        ('loading', 'J-007, Secret Ally, Nowhere', city_ids[0]),
        ('loading', 'S-666, Bad Road, Hell', city_ids[0]),
        ('unloading', 'P-100, Super Street, Utopia', city_ids[1]),
        ('unloading', '0, Infinity Lane, Everywhere', city_ids[1]),
    ]
    for t, a, c in data:
        LoadingUnloadingAddress.objects.create(type=t, transaction=test.transaction, address=a, city_id=c)

    test.vehicle_requests = []
    for vc, q in [(vc1, 3), (vc2, 4)]:
        test.vehicle_requests.append(VehicleRequest.objects.create(
            transaction=test.transaction, vehicle_category=vc, vehicle_type=vc.vehicle_type,
            vehicle_capacity=vc.capacity,
            quantity=q
        ))


def gps_log_data(device_id):
    return [
        device_id, 'fused', 28.215999603271484, 0, 0, 0, 9, 3887656960,
        1131442176, 226492416, 0, 'OnePlus', 'OnePlus', 'OnePlus2', 'OnePlus2', 'ONE A2003', '0.1.1', 30, '6.0.1', 23
    ]


def get_path_data():
    s0 = 0.02
    speeds = [(s0, s0)]
    for i in range(32):
        sx, sy = speeds[-1]
        mag = (sx ** 2 + sy ** 2) ** 0.5
        new_mag = mag + (random.random() - 0.5) * 0.1 * mag

        new_sx = sx + (random.random() - 0.5) * 0.05 * s0
        new_sy = sy + (random.random() - 0.5) * 0.05 * s0
        new_ex_mag = (new_sx ** 2 + new_sy ** 2) ** 0.5

        new_sx = new_sx * new_mag / new_ex_mag
        new_sy = new_sy * new_mag / new_ex_mag

        speeds.append((new_sx, new_sy))

    path = [(19.1112867, 72.8979114)]
    for slat, slon in speeds:
        lt, ln = path[-1]
        new_lat = lt + slat * 0.4
        new_lon = ln + slon * 0.4
        path.append((new_lat, new_lon))

    log_times = [timezone.now() - timedelta(minutes=(15 * i)) for i in range(len(path))]

    return list(zip(log_times, path))


def get_new_log(driver, log_time, lat, lon):
    (device_id, provider, accuracy, altitude, speed, course, battery, total_memory,
     available_memory, threshold, low_memory, brand, manufacturer, device, product, model, version_name, version_code,
     android_release, android_sdk_int) = gps_log_data(driver.device_id)

    return GPSLogNew(
        device_id=device_id, datetime=log_time, provider=provider, accuracy=accuracy,
        latitude=lat, longitude=lon, altitude=altitude, speed=speed, course=course,
        battery=battery, total_memory=in_mb(total_memory), available_memory=in_mb(available_memory),
        threshold=in_mb(threshold), low_memory=bool(low_memory),
        brand=brand, manufacturer=manufacturer, device=device, product=product, model=model,
        version_name=version_name, version_code=version_code,
        android_release=android_release, android_sdk_int=android_sdk_int,
        driver=driver, driver_name=driver.driver_name, driver_number=driver.driver_number,
        driving_licence_number=driver.driving_licence_number, vehicle_number=driver.vehicle_number,
        vehicle_type=driver.vehicle_type, vehicle_status=driver.vehicle_status,
    )


def add_tracking_data(test, user):
    add_vehicle_without_docs(test, user)
    path_data = get_path_data()
    log_time, (latitude, longitude) = path_data[0]
    new_logs = [get_new_log(test.driver_app_user, log_time, lat, lon) for log_time, (lat, lon) in path_data]
    GPSLogNew.objects.bulk_create(new_logs)
    test.driver_app_user.location_time = log_time
    test.driver_app_user.latitude = latitude
    test.driver_app_user.longitude = longitude
    test.driver_app_user.save()
