from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone

from api.abstract import PASSWORD
from api.utils import format_iso, get_or_none
from transaction.models import Transaction, UserVendor, TransactionVendorRequest
from utils.models import City, State, VehicleCategory


def add_app_data():
    State.objects.bulk_create(
        State(id=i, name=n) for i, n in [(1, 'UP'), (2, 'Punjab'), (3, 'Maharashtra')]
    )
    City.objects.bulk_create(
        City(state_id=s, name=n) for s, n in
        [(1, 'Lucknow'), (1, 'Varanasi'), (2, 'Amritsar'), (3, 'Nasik'), (3, 'Mumbai')]
    )


def add_vehicle_categories(test):
    vc1 = VehicleCategory.objects.create(vehicle_type='Volvo', capacity='21 Ton')
    vc2 = VehicleCategory.objects.create(vehicle_type='TATA', capacity='24 Ton')
    test.vcs = [vc1, vc2]
    return vc1, vc2


def setup_for_vendor_request(test):
    test.transaction = Transaction.objects.create(transaction_id='TEST007', booking_agent=test.user)
    vendor_data = [('Vendor One', '9111111111'), ('Vendor Two', '9111111112'), ('Vendor Three', '9111111113')]
    test.user_vendors = [UserVendor.objects.create(user=test.user, name=n, phone=p) for n, p in vendor_data]


def get_vendor_request_data(test):
    return {'booking_id': test.transaction.id, 'vendors': [{'id': v.id} for v in test.user_vendors]}


def confirm_vendor_request_result(test):
    all_created = all(TransactionVendorRequest.objects.filter(
        user=test.user, transaction=test.transaction, vendor=v
    ).exists() for v in test.user_vendors)
    test.assertTrue(all_created, 'All TransactionVendorRequests not created')


def setup_for_new_booking(test):
    add_app_data()
    test.admin = User.objects.create_user(username='admin', email='info+99@aaho.in', password=PASSWORD)
    test.vc, _ = add_vehicle_categories(test)
    test.city1, test.city2 = City.objects.all()[:2]
    test.ship_datetime = timezone.now() + timedelta(days=4)
    test.cached_data = None


def get_cached_booking_request_data(test):
    if test.cached_data is None:
        test.cached_data = get_booking_request_data(test.city1, test.city2, test.vc, test.ship_datetime)
    return test.cached_data


def confirm_new_booking_result(test):
    json_resp = test.response_json()
    test.assertIsNotNone(json_resp, 'no json response available')
    booking_id = json_resp.get('booking_id', None)
    test.assertIsNotNone(booking_id, 'server must send back a booking id')
    transaction = get_or_none(Transaction, id=booking_id)
    test.assertIsNotNone(transaction, 'no transaction found for id = %s' % booking_id)
    print (transaction.shipment_datetime, test.ship_datetime)
    test.assertEqual(transaction.shipment_datetime, test.ship_datetime, 'shipment_datetime does not match')


def get_booking_request_data(city1, city2, vc, ship_dt):
    city1_data = {'id': city1.id, 'name': city1.name, 'state': city1.state.name}
    city2_data = {'id': city2.id, 'name': city2.name, 'state': city2.state.name}
    date_str = format_iso(ship_dt)
    print('formatted = ', date_str)
    return {
        'pickups': [
            {'city': city1_data, 'address': '01, Pick Up Address, First Street'},
            {'city': city1_data, 'address': '02, Pick Up Address, Second Street'}
        ],
        'drops': [
            {'city': city2_data, 'address': '101, Drop Address, A Street'},
            {'city': city2_data, 'address': '201, Drop Address, B Street'}
        ],
        'vehicles': [
            {'count': 5, 'id': vc.id},
            {'count': 3, 'name': 'Volvo Heavy', 'capacity': '31.7 Tons'}
        ],
        'contact_person': 'Devil Satan',
        'contact_number': '6666666666',
        'shipment_datetime': date_str,
        'material': 'Souls',
        'rate': None
    }


def get_add_vendor_data():
    return {'name': 'Salman Khan', 'phone': '9999999999'}


def confirm_add_vendor_result(test):
    created = UserVendor.objects.filter(user=test.user, phone=test.data()['phone']).exists()
    test.assertTrue(created, 'Vendor not created')


def setup_for_delete_vendor(test):
    test.user_vendor = UserVendor.objects.create(user=test.user, name='Salman Khan', phone='9999999999')
    test.other_user = User.objects.create_user(username='other_user', password=PASSWORD, email='info+4@aaho.in')
    test.other_user_vendor = UserVendor.objects.create(user=test.other_user, name='Amir Khan', phone='9999099990')


def get_delete_vendor_data(test):
    return {'id': test.user_vendor.id}


def confirm_delete_vendor_result(test):
    test.assertFalse(UserVendor.objects.filter(id=test.user_vendor.id).exists(), 'Vendor not deleted')


def check_403_on_delete_vendor(test):
    test.login()
    response = test.get_response(data={'id': test.other_user_vendor.id})
    test.assert_response_code(test.url(), response, 403, 'Should give 403 response while deleting other\'s vendor')

