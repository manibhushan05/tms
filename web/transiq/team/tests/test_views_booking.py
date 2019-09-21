from __future__ import print_function, absolute_import, division

from django.contrib.auth.models import User
from django.test import TestCase, Client

from broker.models import Broker
from driver.models import Driver
from utils.models import City, AahoOffice, State, VehicleCategory, Bank
from sme.models import Sme

from team.models import ManualBooking
from team.models import OutWardPayment


# class FetchFullBookingPageTest(TestCase):
#
#     def setUp(self):
#         self.user = User.objects.create_user(username='ravindra@aaho.in', password='transiq123')
#         self.client = Client()
#         self.client.login(username='ravindra@aaho.in', password='transiq123')
#         # self.booking = ManualBooking.objects.create(total_amount_to_owner=100000)
#
#     def test_fetch_full_booking_page_views(self):
#         response = self.client.post(path='/team/fetch-full-booking-data-page/')
#
#         self.assertEqual(response.status_code, 200)
#
# class FullBookingPageTest(TestCase):
#
#     def setUp(self):
#         self.user = User.objects.create_user(username='ravindra@aaho.in', password='transiq123')
#         self.client = Client()
#         self.client.login(username='ravindra@aaho.in', password='transiq123')
#
#         customer_placed_order = User.objects.create_user(username='John Doe', password='transiq123')
#         self.sme_placed_order = Sme.objects.create(name=customer_placed_order, is_gst_applicable='no')
#
#         customer_to_be_billed = User.objects.create_user(username='Landis', password='transiq123')
#         self.sme_to_be_billed = Sme.objects.create(name=customer_to_be_billed, is_gst_applicable='no')
#
#         state, _ = State.objects.get_or_create(name='Chhattisgarh')
#         city, _ = City.objects.get_or_create(name='Raipur', state=state)
#         self.source_office, _ = AahoOffice.objects.get_or_create(branch=city)
#         self.source_office.address = 'Shop No.-3, Plot No.- W/2/41, Block-8, Parking-6, Near Goyal Bhawan, Transport Nagar, Rawabhata'
#         self.source_office.branch_head = 'Amit Kumar'
#         self.source_office.email = 'amit@aaho.in'
#         self.source_office.pin = '492001'
#         self.source_office.save()
#
#         state, _ = State.objects.get_or_create(name='Maharashtra')
#         city, _ = City.objects.get_or_create(name='Mumbai', state=state)
#         self.dest_office, _ = AahoOffice.objects.get_or_create(branch=city)
#         self.dest_office.address = 'Shop No.-3, Plot No.- W/2/41, Block-8, Parking-6, Near Goyal Bhawan, Transport Nagar, Rawabhata'
#         self.dest_office.branch_head = 'Ravindra'
#         self.dest_office.email = 'ravindra@aaho.in'
#         self.dest_office.pin = '400706'
#         self.dest_office.save()
#
#         self.driver = Driver.objects.create(name='James Bond', phone='8978937498')
#         broker_user = User.objects.create_user(username='John Murray', password='transiq123')
#         self.broker = Broker.objects.create(name=broker_user)
#
#
#     def test_full_booking_page_views(self):
#         response = self.client.get('/team/full-booking-page/', {
#             'source_office': self.source_office.id,
#             'destination_office': self.dest_office.id,
#             'customer_placed_order': self.sme_placed_order.id,
#             'customer_to_be_billed': self.sme_to_be_billed.id,
#             'truck_driver_id': self.driver.id,
#             'supplier_id': self.broker.id,
#             'gst_liability': 'consignor',
#             'shipment_datetime': '21-Apr-2018 09:00 AM',
#             'number_of_lr': 1,
#             'vehicle_number': 'MH12ML9090',
#             'billing_type': 'T.B.B.',
#             'from': 'Mumbai',
#             'to': 'Delhi',
#             'refund': 100,
#             'supplier_charged_weight': 10,
#             'supplier_rate': 2000,
#             'charged_weight': 10,
#             'party_rate': 2000,
#             'loaded_weight': 10,
#             'generate-booking-and-finish': '',
#             'is_print_payment_mode_instruction': 'no',
#         })
#
#         self.assertEqual(response.status_code, 200)