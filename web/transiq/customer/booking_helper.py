from django.contrib.auth.models import User
from django.core.mail import EmailMessage

from api.helper import json_response, json_error_response, json_400_incorrect_use
from api.sms import send_sms
from api.utils import parse_iso, random_letters, random_digits
from customer.sql import get_ranking_results
from employee.models import TaskEmail, Task
from transaction.models import Transaction, LoadingUnloadingAddress, UserVendor, TransactionVendorRequest, \
    VehicleRequest
from utils.models import City, VehicleCategory
from sme.models import Sme


def do_delete_vendor(request):
    vendor_id = request.data.get('id', None)
    if vendor_id is None:
        return json_400_incorrect_use()
    try:
        vendor = UserVendor.objects.get(id=vendor_id)
    except UserVendor.DoesNotExist:
        return json_400_incorrect_use()

    if not vendor.user == request.user:
        return json_response({'status': 'error', 'msg': 'user does not own the object'}, status=403)

    UserVendor.objects.filter(id=vendor_id).delete()

    vendor_data = list(UserVendor.objects.filter(user=request.user).order_by('id').values('id', 'name', 'phone'))
    return json_response({'status': 'success', 'msg': 'vendor added', 'vendors': vendor_data})


def do_add_vendor(request):
    name = request.data.get('name', None)
    phone = request.data.get('phone', None)
    name = None if name is None else name.strip()
    phone = None if phone is None else phone.strip()
    if not name or not phone:
        return json_400_incorrect_use()
    UserVendor.objects.get_or_create(user=request.user, name=name, phone=phone)
    vendor_data = list(UserVendor.objects.filter(user=request.user).order_by('id').values('id', 'name', 'phone'))
    return json_response({'status': 'success', 'msg': 'vendor added', 'vendors': vendor_data})


def do_booking_vendor_request(request):
    user = request.user
    data = request.data

    transaction_id = data.get('booking_id', None)
    vendor_data = data.get('vendors', None)

    if transaction_id is None or not vendor_data:
        return json_400_incorrect_use()

    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return json_error_response('no such transaction exits, id=' + transaction_id, 400)

    vendors = []
    for ven in vendor_data:
        try:
            vendors.append(UserVendor.objects.get(user=user, id=ven['id']))
        except UserVendor.DoesNotExist:
            return json_error_response('no such vendor exits, id=' + ven['id'], 400)

    TransactionVendorRequest.objects.bulk_create(
        [TransactionVendorRequest(transaction=transaction, user=user, vendor=v) for v in vendors]
    )

    send_vendor_request_sms()

    return json_response({'status': 'success', 'msg': 'requests successfully sent to vendors'})


def send_vendor_request_sms():
    # TODO: send actual sms here
    pass


def do_booking_save(request):
    user = request.user
    data = request.data

    pickup_data = data.get('pickups', None)
    drop_data = data.get('drops', None)
    vehicle_data = data.get('vehicles', None)
    contact_person = data.get('contact_person', None)
    contact_number = data.get('contact_number', None)
    shipment_datetime = data.get('shipment_datetime', None)
    material = data.get('material', None)
    rate = data.get('rate', None)

    if not (pickup_data and drop_data and vehicle_data and contact_number and contact_person and shipment_datetime):
        return json_error_response('insufficient data to process booking', 400)

    trans = create_new_transaction(user, contact_person, contact_number, shipment_datetime, material, rate)

    for p in pickup_data:
        create_stop_point('loading', trans, p['address'], p['city']['id'])

    for d in drop_data:
        create_stop_point('unloading', trans, d['address'], d['city']['id'])

    for vehicle in vehicle_data:
        if 'id' in vehicle:
            v_cat = VehicleCategory.objects.get(id=vehicle['id'])
            VehicleRequest.objects.create(transaction=trans, vehicle_category=v_cat, vehicle_type=v_cat.vehicle_type,
                                          vehicle_capacity=v_cat.capacity, quantity=vehicle['count'])
        else:
            VehicleRequest.objects.create(transaction=trans, vehicle_type=vehicle['name'],
                                          vehicle_capacity=vehicle['capacity'], quantity=vehicle['count'])

    send_booking_email(user, pickup_data, drop_data, contact_number, shipment_datetime, material)
    send_booking_sms(user, pickup_data, drop_data, contact_number, shipment_datetime)

    city_scores, address_scores = get_ranking_results(request.user.id)
    vendor_data = list(UserVendor.objects.filter(user=request.user).values('id', 'name', 'phone'))

    return json_response({'status': 'success', 'msg': 'booked', 'booking_id': trans.id,
                          'city_scores': city_scores, 'address_scores': address_scores,
                          'vendors': vendor_data})


def create_new_transaction(user, contact_person, contact_number, shipment_datetime, material, rate):
    transaction = Transaction()
    transaction.transaction_id = get_new_transaction_id(user)
    transaction.booking_agent = user
    transaction.total_vehicle_requested = ''
    transaction.material = material
    transaction.contact_person = contact_person
    transaction.contact_number = contact_number
    transaction.transaction_managed_by = User.objects.get(username='admin')
    transaction.shipment_datetime = parse_iso(shipment_datetime)
    transaction.expected_rate = rate
    transaction.save()
    return transaction


def create_stop_point(stop_type, transaction, address, city_id):
    LoadingUnloadingAddress.objects.create(type=stop_type, transaction=transaction, address=address,
                                           city=City.objects.get(id=city_id))


def send_booking_email(user, pickup_data, drop_data, contact_number, shipment_datetime, material):
    subject = "New Booking from " + user.username

    body_template = BOOKING_EMAIL_TEMPLATE
    format_data = {
        'user_full_name': user.get_full_name(),
        'pickup_address': pickup_data[0]['address'],
        'pickup_city': pickup_data[0]['city']['name'],
        'drop_address': drop_data[0]['address'],
        'drop_city': drop_data[0]['city']['name'],
        'shipment_datetime': shipment_datetime,
        'material': material,
        'contact_number': contact_number
    }

    body = body_template.format(**format_data)
    email = EmailMessage(subject, body, to=['mani@aaho.in', 'rohit@aaho.in', 'harsh@aaho.in', 'pankaj@aaho.in'])
    # email = EmailMessage(subject, body, to=['mani@aaho.in'])
    email.send()


def send_booking_sms(user, pickup_data, drop_data, contact_number, shipment_datetime):
    # mobiles = str(','.join(
    #     TaskEmail.objects.filter(task=Task.objects.get(name='sme_booking_sms')).last().employee.values_list(
    #         'username__profile__phone', flat=True)))
    mobiles='8978937498'
    sms_msg_template = SMS_MSG_TEMPLATE
    format_data = {
        'username': user.username,
        'pickup_city': pickup_data[0]['city']['name'],
        'drop_city': drop_data[0]['city']['name'],
        'shipment_datetime': shipment_datetime,
        'contact_number': contact_number
    }
    sms_msg = sms_msg_template.format(**format_data)
    # send_sms(mobiles, sms_msg)


def get_company_name(user):
    sme = Sme.objects.get(name=User.objects.get(username=user))
    return str(sme.name.first_name) + str(sme.name.last_name)


def get_new_transaction_id(user):
    try:
        sme_booking_data = Sme.objects.get(name=user)
    except Sme.DoesNotExist:
        sme_booking_data = None
    if sme_booking_data:
        new_transaction_id = allocate_transaction_id(sme_booking_data.latest_lr_serial_number)
        sme_booking_data.latest_lr_serial_number = new_transaction_id
        sme_booking_data.save()
    else:
        new_transaction_id = get_new_transaction_id_no_sme()
    return new_transaction_id


def allocate_transaction_id(transaction_id):
    id = str(transaction_id)
    temp = int(id[3:]) + 1
    trans_id = id[0:3] + '{0:05d}'.format(temp)
    return trans_id


def get_new_transaction_id_no_sme():
    tids = set(Transaction.objects.values_list('transaction_id', flat=True))
    new_tid = generate_random_transaction_id()
    while new_tid in tids:
        new_tid = generate_random_transaction_id()
    return new_tid


def generate_random_transaction_id():
    return random_letters(num_digits=3) + random_digits(num_digits=5)


# templates

BOOKING_EMAIL_TEMPLATE = """

A new booking request has been received from {user_full_name} on {shipment_datetime}.

The key details are:

From: {pickup_address}, {pickup_city}
To: {drop_address}, {drop_city}
Date: {shipment_datetime}
Material: {material}
Contact No.: {contact_number}

You can also login to the admin page at www.aaho.in/admin to look at the details.

Regards,
Aaho Booking""".strip()

SMS_MSG_TEMPLATE = """

New booking for {pickup_city} to {drop_city} on {shipment_datetime} received from {username}, contact {contact_number}. Login to admin page to see detail.
""".strip()
