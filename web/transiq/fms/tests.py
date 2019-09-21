from django.contrib.auth.models import User, Group

from django.test import Client
from django.test import TestCase
from requests import Request

from api.abstract import GetFmsAuthApiTestCase, UnAbstractAuth, GetApiTestCase, UnAbstract, user_details, \
    PostFmsAuthApiTestCase, UnAbstractAuth400
from broker.models import Broker
from customer.schema import customer_new_booking_schema, customer_add_vendor_schema, customer_delete_vendor_schema
from customer.test_helper import setup_for_vendor_request, get_vendor_request_data, \
    confirm_vendor_request_result, setup_for_new_booking, get_cached_booking_request_data, confirm_new_booking_result, \
    get_add_vendor_data, confirm_add_vendor_result, setup_for_delete_vendor, get_delete_vendor_data, \
    confirm_delete_vendor_result, check_403_on_delete_vendor
from fms.email import doc_download_link
from fms.schema import fms_app_data_schema, fms_login_status_schema, fms_list_vehicles_schema, fms_list_drivers_schema, \
    fms_driver_detail_schema, fms_vehicle_detail_schema, fms_available_loads_schema, fms_track_vehicles_schema
from fms.test_helper import add_vehicle_driver_data, add_vehicle_data, add_booking_data, add_tracking_data
from fms.views import get_expiry_key

import json

"""# post
    url(r'^booking-history-data/$', csrf_exempt(trip_history.booking_history_data)),
    url(r'^vehicle-trip-data/$', csrf_exempt(trip_history.vehicle_trip_data)),
    url(r'^complete-trip-details/$', csrf_exempt(trip_history.complete_trip_details)),
"""


class TestFmsLoginApi(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='ravindra@aaho.in', password='aaho123')
        self.user.groups.add(Group.objects.create(name='fms'))
        self.client = Client()

    def testLogin(self):
        # res = self.client.post(path = '/api/fms/login/',data= {'username':self.user.username, 'password':'aaho123'})
        res = self.client.post(path='/api/fms/login/',
                               data=json.dumps({'username': self.user.username, 'password': 'aaho123'}),
                               content_type='json',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')


# GETs

class TestFmsLoginStatusApi(GetApiTestCase, UnAbstract):

    def url(self):
        return '/api/fms/login-status/'

    def schema(self):
        return fms_login_status_schema()


class TestFmsAppDataApi(GetFmsAuthApiTestCase, UnAbstractAuth):

    def setUp(self):
        super().setUp()
        add_vehicle_driver_data(self, self.user)

    def url(self):
        return '/api/fms/app-data/'

    def schema(self):
        return fms_app_data_schema()


class TestFmsListVehiclesApi(GetFmsAuthApiTestCase, UnAbstractAuth):

    def setUp(self):
        super().setUp()
        add_vehicle_driver_data(self, self.user)

    def url(self):
        return '/api/fms/list-vehicles/'

    def schema(self):
        return fms_list_vehicles_schema()


class TestFmsListDriversApi(GetFmsAuthApiTestCase, UnAbstractAuth):

    def setUp(self):
        super().setUp()
        add_vehicle_driver_data(self, self.user)

    def url(self):
        return '/api/fms/list-drivers/'

    def schema(self):
        return fms_list_drivers_schema()


class TestFmsDriverDetailsApi(GetFmsAuthApiTestCase, UnAbstractAuth):

    def setUp(self):
        super().setUp()
        add_vehicle_data(self, self.user)

    def url(self):
        driver_id = getattr(self, 'driver_id', None)
        return '/api/fms/driver/' + ('' if not driver_id else ('%s/' % driver_id))

    def schema(self):
        return fms_driver_detail_schema()


class TestFmsVehicleDetailsApi(GetFmsAuthApiTestCase, UnAbstractAuth):

    def setUp(self):
        super().setUp()
        add_vehicle_data(self, self.user)

    def url(self):
        vehicle_id = getattr(self, 'vehicle_id', None)
        return '/api/fms/vehicle/' + ('' if not vehicle_id else ('%s/' % vehicle_id))

    def schema(self):
        return fms_vehicle_detail_schema()


class TestFmsAvailableLoadsApi(GetFmsAuthApiTestCase, UnAbstractAuth):

    def setUp(self):
        super().setUp()
        add_booking_data(self)

    def url(self):
        return '/api/fms/available-loads/'

    def schema(self):
        return fms_available_loads_schema()


class TestFmsTrackVehiclesApi(GetFmsAuthApiTestCase, UnAbstractAuth):

    def setUp(self):
        super().setUp()
        add_tracking_data(self, self.user)

    def url(self):
        return '/api/fms/track-vehicles/'

    def schema(self):
        return fms_track_vehicles_schema()


class TestFmsVehicleDocDownloadApi(GetApiTestCase, UnAbstract):

    def is_json(self):
        return False

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(**user_details())
        fms_group = Group.objects.create(name='fms')
        self.broker = Broker.objects.create(name=self.user)
        self.user.groups.add(fms_group)
        add_vehicle_data(self, self.user)

    def url(self):
        vehicle_id = getattr(self, 'vehicle_id', None)
        if not vehicle_id:
            return '/api/fms/vehicle/download-documents/'
        return doc_download_link(vehicle_id, get_expiry_key(), excluded=['puc'])

    def validate_misc_response(self, response):
        content_type_header = response._headers.get('content-type', None)
        self.assertIsNotNone(content_type_header, 'Content type header not present')
        # resp_content_type = content_type_header[1].lower()
        # expected_content_type = 'application/x-zip-compressed'
        # self.assertEqual(resp_content_type, expected_content_type, 'Unknown Content type: %s' % resp_content_type)


# POSTs

class TestVendorRequestApi(PostFmsAuthApiTestCase, UnAbstractAuth400):

    def setUp(self):
        super().setUp()
        setup_for_vendor_request(self)

    def url(self):
        return '/api/fms/vendor-request/'

    def data(self):
        return get_vendor_request_data(self)

    def confirm_result(self):
        confirm_vendor_request_result(self)


#
# class TestNewBookingApi(PostFmsAuthApiTestCase, UnAbstractAuth400):
#
#     def setUp(self):
#         super(TestNewBookingApi, self).setUp()
#         setup_for_new_booking(self)
#
#     def url(self):
#         return '/api/fms/new-booking/'
# 
#     def data(self):
#         return get_cached_booking_request_data(self)
#
#     def schema(self):
#         return customer_new_booking_schema()
#
#     def confirm_result(self):
#         confirm_new_booking_result(self)


class TestAddVendorApi(PostFmsAuthApiTestCase, UnAbstractAuth400):
    def url(self):
        return '/api/fms/add-vendor/'

    def schema(self):
        return customer_add_vendor_schema()

    def data(self):
        return get_add_vendor_data()

    def confirm_result(self):
        confirm_add_vendor_result(self)


class TestDeleteVendorApi(PostFmsAuthApiTestCase, UnAbstractAuth400):
    def setUp(self):
        super().setUp()
        setup_for_delete_vendor(self)

    def url(self):
        return '/api/fms/delete-vendor/'

    def schema(self):
        return customer_delete_vendor_schema()

    def data(self):
        return get_delete_vendor_data(self)

    def confirm_result(self):
        confirm_delete_vendor_result(self)

    def test_403_response(self):
        check_403_on_delete_vendor(self)


"""
class TestAddVehicleApi(PostFmsAuthApiTestCase, UnAbstractAuth400):

    def setUp(self):
        super().setUp()
        add_vehicle_dependencies(self, self.user)
        self.rc_validity = (timezone.now() + timedelta(days=30)).date()
        self.insurance_validity = (timezone.now() + timedelta(days=35)).date()
        self.permit_validity = (timezone.now() + timedelta(days=40)).date()
        self.fitness_validity = (timezone.now() + timedelta(days=45)).date()
        self.puc_validity = (timezone.now() + timedelta(days=50)).date()
        self.dec_validity = (timezone.now() + timedelta(days=55)).date()
        self.dl_validity = (timezone.now() + timedelta(days=60)).date()
        self.dl_location = 'Mumbai',
        self.owner=Owner.objects.last(),
        self.driver=Driver.objects.last(),

    def url(self):
        return '/api/fms/edit-vehicle/'

    def data(self):
        return {
            'vehicle_number': 'MH01 AB 1234', 'owner': {'id': self.owner.id}, 'driver': {'id': self.driver.id},
            'vehicle_type': self.vc.id,
            'rc_doc': {
                'url': 'test1.png', 'thumb_url': 'test1.png', 'validity': format_iso(self.rc_validity),
                'manufacture_year': '2014'
            },
            'insurance_doc': {
                'url': 'test2.png', 'thumb_url': 'test2.png', 'validity': format_iso(self.insurance_validity),
                'doc_id': 'INS100001', 'insurer_name': 'Batman'
            },
            'permit_doc': {
                'url': 'test3.png', 'thumb_url': 'test3.png', 'validity': format_iso(self.permit_validity),
                'permit_type': 'All-India', 'doc_id': 'PERM1000001'
            },
            'fitness_doc': {
                'url': 'test4.png', 'thumb_url': 'test4.png', 'validity': format_iso(self.fitness_validity),
                'doc_id': 'FIT10000001'
            },
            'puc_doc': {
                'url': 'test5.png', 'thumb_url': 'test5.png', 'validity': format_iso(self.puc_validity),
                'doc_id': 'PUC100000001'
            },
            'owner_pan_doc': {'url': 'test6.png', 'thumb_url': 'test6.png', 'doc_id': 'OWNER66PAN'},
            'owner_dec_doc': {'url': 'test7.png', 'thumb_url': 'test7.png', 'validity': format_iso(self.dec_validity)},
            'driver_dl_doc': {'url': 'test8.png', 'thumb_url': 'test8.png', 'doc_id': 'DRIVER665DL',
                              'validity': format_iso(self.dl_validity), 'issue_location': self.dl_location}
        }

    def schema(self):
        return fms_edit_vehicle_schema()

    def confirm_result(self):
        new_vals = self.data()
        vehicle = Vehicle.find(new_vals['vehicle_number'])
        self.assertIsNotNone(vehicle, 'Vehicle not created')
        self.assertEqual(vehicle.driver_id, self.driver.id, 'Driver not updated')
        self.assertEqual(vehicle.owner_id, self.owner.id, 'Owner not updated')
        self.assertEqual(vehicle.vehicle_type_id, self.vc.id, 'Vehicle type not updated')

        broker_vehicle_exists = BrokerVehicle.objects.filter(vehicle=vehicle, broker=self.broker).exists()
        self.assertTrue(broker_vehicle_exists, 'Vehicle Broker association not created')
        broker_driver_exists = BrokerDriver.objects.filter(driver=vehicle.driver, broker=self.broker).exists()
        self.assertTrue(broker_driver_exists, 'Driver Broker association not created')
        broker_owner_exists = BrokerOwner.objects.filter(owner=vehicle.owner, broker=self.broker).exists()
        self.assertTrue(broker_owner_exists, 'Owner Broker association not created')

        # check vehicle docs
        self.check_vehicle_docs(vehicle, new_vals)
        self.check_other_docs(vehicle, new_vals)

    def check_vehicle_docs(self, vehicle, new_vals):
        doc = new_vals['rc_doc']
        check_vehicle_rc(self, vehicle, url=doc['url'], validity=self.rc_validity, year=doc['manufacture_year'])
        doc = new_vals['permit_doc']
        check_vehicle_permit(self, vehicle, url=doc['url'], validity=self.permit_validity,
                             permit_type=doc['permit_type'], permit_number=doc['doc_id'])
        doc = new_vals['fitness_doc']
        check_vehicle_fitness(self, vehicle, url=doc['url'], validity=self.fitness_validity,
                              fitness_number=doc['doc_id'])
        doc = new_vals['insurance_doc']
        check_vehicle_insurance(self, vehicle, url=doc['url'], validity=self.insurance_validity,
                                insurance_number=doc['doc_id'], insurer=doc['insurer_name'])
        doc = new_vals['puc_doc']
        check_vehicle_puc(self, vehicle, url=doc['url'], validity=self.puc_validity, puc_number=doc['doc_id'])

    def check_other_docs(self, vehicle, new_vals):
        owner = get_or_none(Owner, id=vehicle.owner.id)
        doc = new_vals['owner_pan_doc']
        check_owner_pan(self, owner, url=doc['url'], pan_number=doc['doc_id'])
        doc = new_vals['owner_dec_doc']
        check_owner_declaration(self, owner, url=doc['url'], validity=self.dec_validity)
        doc = new_vals['driver_dl_doc']
        check_driver_dl(self, vehicle.driver, url=doc['url'], validity=self.dl_validity, location=self.dl_location,
                        dl_number=doc['doc_id'])


class TestAddDriverApi(PostFmsAuthApiTestCase, UnAbstractAuth):

    def setUp(self):
        super().setUp()
        self.dl_validity = (timezone.now() + timedelta(days=30)).date()
        self.dl_location = 'Mumbai'

    def url(self):
        return '/api/fms/edit-driver/'

    def data(self):
        return {
            'name': 'The Driver', 'phone': '9898989897',
            'pan_doc': {'url': 'test1.png', 'thumb_url': 'test1.png', 'doc_id': 'DRIVER66PAN'},
            'dl_doc': {'url': 'test2.png', 'thumb_url': 'test2.png', 'doc_id': 'DRIVER66DL',
                       'validity': format_iso(self.dl_validity), 'issue_location': self.dl_location}
        }

    def schema(self):
        return fms_edit_driver_schema()

    def confirm_result(self):
        new_vals = self.data()
        driver = get_or_none(Driver, name=new_vals['name'], phone=new_vals['phone'])
        self.assertIsNotNone(driver, 'Driver not created')
        broker_driver_exists = BrokerDriver.objects.filter(driver=driver, broker=self.broker).exists()
        self.assertTrue(broker_driver_exists, 'Driver Broker association not created')
        # pan doc
        check_driver_pan(self, driver, url=self.data()['pan_doc']['url'], pan_number=new_vals['pan_doc']['doc_id'])
        # declaration doc
        check_driver_dl(self, driver, url=new_vals['dl_doc']['url'], validity=self.dl_validity,
                        location=self.dl_location, dl_number=new_vals['dl_doc']['doc_id'])


class TestAddOwnerApi(PostFmsAuthApiTestCase, UnAbstractAuth400):

    def url(self):
        return '/api/fms/edit-owner/'

    def data(self):
        return {'name': 'The Boss', 'phone': '9898989898'}

    def schema(self):
        return fms_edit_owner_schema()

    def confirm_result(self):
        req_data = self.data()
        owner_user = get_or_none(User, username=req_data['phone'])
        self.assertIsNotNone(owner_user, 'User not created')
        owner = get_or_none(Owner, name=owner_user)
        self.assertIsNotNone(owner, 'Owner not created')
        owner_profile = get_or_none(Profile, user=owner_user)
        self.assertIsNotNone(owner_profile, 'Profile not created')
        self.assertEqual(owner_profile.name, req_data['name'], 'name not updated in profile')
        self.assertEqual(owner_profile.phone, req_data['phone'], 'phone not updated in profile')
        broker_owner_exists = BrokerOwner.objects.filter(owner=owner, broker=self.broker).exists()
        self.assertTrue(broker_owner_exists, 'Owner Broker association not created')


class TestSendDocumentEmailApi(PostFmsAuthApiTestCase, UnAbstractAuth400):

    def setUp(self):
        super().setUp()
        add_vehicle_data(self, self.user)

    def url(self):
        return '/api/fms/vehicle/send-document-email/'

    def data(self):
        return {'id': self.vehicle.id, 'emails': ['shobhit.v87@gmail.com', 'info+559@aaho.in']}

    def invalid_data(self):
        return [
            {},
            {'id': self.vehicle.id, 'emails': []},
            {'emails': ['shobhit.v87@gmail.com']}
        ]

    def confirm_result(self):
        self.assertEqual(len(mail.outbox), 1, 'No outgoing mail')
        self.assertListEqual(mail.outbox[0].to, self.data()['emails'], 'Mail not sent to correct email ids')


class TestAddAccountApi(PostFmsAuthApiTestCase, UnAbstractAuth400):

    def url(self):
        return '/api/fms/edit-account/'

    def data(self):
        return get_bank_details()

    def invalid_data(self):
        return [{}, {'bank': 'SBI'}]

    def schema(self):
        return fms_edit_account_schema()

    def confirm_result(self):
        req_data = self.data()
        bank = get_or_none(Bank, **req_data)
        self.assertIsNotNone(bank, 'Bank not created')
        broker_bank_exists = BrokerAccount.objects.filter(account=bank, broker=self.broker).exists()
        self.assertTrue(broker_bank_exists, 'Bank Broker association not created')


class TestSendQuoteApi(PostFmsAuthApiTestCase, UnAbstractAuth400):

    def setUp(self):
        super().setUp()
        add_booking_data(self)
        self.vr = self.vehicle_requests[0]

    def url(self):
        return '/api/fms/send-quote/'

    def data(self):
        return {'vehicle_request_id': self.vr.id, 'quantity': self.vr.quantity, 'amount': 1000.0, 'comments': 'awesome'}

    def invalid_data(self):
        return [
            {'vehicle_request_id': self.vr.id, 'quantity': self.vr.quantity + 1, 'amount': 10000.0},
            {'vehicle_request_id': self.vr.id, 'quantity': self.vr.quantity, 'amount': 0.0},
            {'vehicle_request_id': self.vr.id, 'quantity': 0, 'amount': 10000.0},
        ]

    def error_400_msg(self):
        return 'Quote quantity can not be greater than quantity requested'

    def schema(self):
        return fms_send_quote_schema()

    def confirm_result(self):
        req_data = self.data()
        quote_exists = VehicleRequestQuote.objects.filter(
            vehicle_request_id=self.vr.id, user_id=self.user.id, transaction_id=self.transaction.id,
            quantity=req_data['quantity'], amount=req_data['amount'], comments=req_data['comments']
        ).exists()
        self.assertTrue(quote_exists, 'Quote not created')


class TestEditVehicleStatusApi(PostFmsAuthApiTestCase, UnAbstractAuth400):

    def setUp(self):
        super().setUp()
        add_vehicle_without_docs(self, self.user)
        self.old_status = 'unloading'
        self.new_status = 'loading'
        self.vehicle.vehicle_status = self.old_status
        self.vehicle.save()
        self.driver_app_user.vehicle_status = self.old_status
        self.driver_app_user.save()

    def url(self):
        return '/api/fms/edit-vehicle-status/'

    def data(self):
        return {'id': self.vehicle.id, 'vehicle_status': 'loading'}

    def invalid_data(self):
        return {'id': self.vehicle.id, 'vehicle_status': 'invalid_status'}

    def schema(self):
        return fms_edit_vehicle_status_schema()

    def confirm_result(self):
        # check if the driver vehicle status was changed
        driver = get_or_none(DriverAppUser, id=self.driver_app_user.id)
        vehicle = get_or_none(Vehicle, id=self.vehicle.id)
        self.assertEqual(driver.vehicle_status, self.new_status, 'Status not updated in DriverAppUser')
        self.assertEqual(vehicle.status, self.new_status, 'Status not updated in Vehicle')


class TestChangePasswordApi(PostFmsAuthApiTestCase, UnAbstractAuth400):

    def url(self):
        return '/api/fms/change-password/'

    def data(self):
        self.new_pass = 'OK1lets2do3this!'
        return self.get_data(self.new_pass)

    def invalid_data(self):
        return self.get_data('2.tiny')

    def get_data(self, new_pass, curr_pass=PASSWORD):
        return {'current_password': curr_pass, 'new_password': new_pass}

    def error_400_msg(self):
        return 'Should give 400 response on invalid new password e.g. if the password is too small or something'

    def confirm_result(self):
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password(self.new_pass), 'Password does not match')

    def test_wrong_password(self):
        self.login()
        response = self.get_response(data=self.get_data('valid new password', curr_pass='wrong password'))
        self.assert_response_code(self.url(), response, 403, 'Should give 403 response on incorrect password')


class TestEditProfileApi(PostFmsAuthApiTestCase, UnAbstractAuth400):

    def setUp(self):
        super().setUp()
        self.owner = Owner.objects.create(name=self.user)
        BrokerOwner.objects.create(broker=self.broker, owner=self.owner)
        self.dec_validity = (timezone.now() + timedelta(days=30)).date()

    def url(self):
        return '/api/fms/edit-profile/'

    def data(self):
        return {
            'full_name': 'Notamade Upname', 'contact_name': 'Mitch McLovin', 'phone': '9143143143',
            'email': 'info+66@aaho.in', 'designation': 'Tester',
            'pan_doc': {'url': 'test1.png', 'thumb_url': 'test1.png', 'doc_id': 'DEVIL666PAN'},
            'dec_doc': {'url': 'test2.png', 'thumb_url': 'test2.png', 'validity': format_iso(self.dec_validity)}
        }

    def schema(self):
        return fms_edit_profile_schema()

    def confirm_result(self):
        new_vals = self.data()
        user = User.objects.get(id=self.user.id)
        # profile
        self.assertEqual(user.first_name, new_vals['full_name'], 'Full name not updated')
        profile = get_or_none(Profile, user=user)
        self.assertIsNotNone(profile, 'profile not created')
        self.assertEqual(profile.contact_person_name, new_vals['contact_name'], 'contact_name not updated')
        self.assertEqual(profile.email, new_vals['email'], 'email not updated')
        self.assertEqual(profile.phone, new_vals['phone'], 'phone not updated')
        self.assertEqual(profile.designation, new_vals['designation'], 'designation not updated')
        # pan doc
        check_broker_pan(self, user, url=self.data()['pan_doc']['url'], pan_number=self.data()['pan_doc']['doc_id'])
        # declaration doc
        owner = get_or_none(Owner, name=self.user)
        check_owner_declaration(self, owner, url=self.data()['dec_doc']['url'], validity=self.dec_validity)


def check_document(test, url, doc):
    test.assertIsNotNone(doc, 'document not created')
    test.assertEqual(doc.document, url, 'document url not updated')


def check_taxation_details(test, taxation_details, pan_number, url):
    test.assertIsNotNone(taxation_details, 'taxation details not created')
    test.assertEqual(taxation_details.pan, pan_number, 'pan number not updated')
    check_document(test, url, taxation_details.pan_doc)


def check_broker_pan(test, user, pan_number, url):
    broker = get_or_none(Broker, name=user)
    test.assertIsNotNone(broker, 'supplier not created')
    taxation_details = broker.taxation_details
    check_taxation_details(test, taxation_details, pan_number, url)


def check_driver_pan(test, driver, pan_number, url):
    taxation_details = driver.taxation_id
    check_taxation_details(test, taxation_details, pan_number, url)


def check_owner_pan(test, owner, pan_number, url):
    taxation_details = owner.taxation_details
    check_taxation_details(test, taxation_details, pan_number, url)


def check_vehicle_insurance(test, vehicle, url, validity, insurance_number, insurer):
    test.assertEqual(vehicle.insurer, insurer, 'insurer not updated')
    test.assertEqual(vehicle.insurance_number, insurance_number, 'insurance_number not updated')
    test.assertEqual(vehicle.insurance_validity, validity, 'validity not updated')
    check_document(test, url, vehicle.insurance_certificate)


def check_vehicle_fitness(test, vehicle, url, validity, fitness_number):
    test.assertEqual(vehicle.fitness_certificate_number, fitness_number, 'fitness_certificate_number not updated')
    test.assertEqual(vehicle.fitness_certificate_validity_date, validity, 'validity not updated')
    check_document(test, url, vehicle.fitness_certificate)


def check_vehicle_puc(test, vehicle, url, validity, puc_number):
    test.assertEqual(vehicle.puc_certificate_number, puc_number, 'puc_certificate_number not updated')
    test.assertEqual(vehicle.puc_certificate_validity_date, validity, 'validity not updated')
    check_document(test, url, vehicle.puc_certificate)


def check_vehicle_permit(test, vehicle, url, validity, permit_type, permit_number):
    test.assertEqual(vehicle.permit, permit_number, 'permit_number not updated')
    test.assertEqual(vehicle.permit_type, permit_type, 'permit_type not updated')
    test.assertEqual(vehicle.permit_validity, validity, 'validity not updated')
    check_document(test, url, vehicle.permit_certificate)


def check_vehicle_rc(test, vehicle, url, validity, year):
    test.assertEqual(vehicle.registration_year.year, int(year), 'year not updated')
    test.assertEqual(vehicle.registration_validity, validity, 'validity not updated')
    check_document(test, url, vehicle.registration_certificate)


def check_driver_dl(test, driver, url, validity, location, dl_number):
    test.assertEqual(driver.driving_licence_number, dl_number, 'driving licence number not updated')
    test.assertEqual(driver.driving_licence_location, location, 'driving licence location not updated')
    test.assertEqual(driver.driving_licence_validity, validity, 'driving licence validity not updated')
    check_document(test, url, driver.driving_licence)


def check_owner_declaration(test, owner, url, validity):
    test.assertEqual(owner.declaration, url, 'declaration url not updated')
    test.assertEqual(owner.declaration_validity, validity, 'dec validity not updated')
    check_document(test, url, owner.declaration_doc)
"""
