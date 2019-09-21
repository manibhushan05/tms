import json

from model_mommy import mommy
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User, Group

from broker.models import Broker
from owner.models import Owner, Vehicle
from restapi.models import UserCategory
from sme.models import Sme
from team.models import ManualBooking


class GetBookingsDataTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.getbookingsdata_url = reverse('get_bookings_data')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harshadasawant89@gmail.com',
                                             password='abc12345')

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'abc12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        self.customer_user = User.objects.create_user(username='david',
                                                      email='harshadasawant89@gmail.com',
                                                      password='pqr12345'
                                                      )
        self.sme = mommy.make(Sme, name=self.customer_user)
        self.sme_group = mommy.make(Group, name='sme')
        self.usercategory = mommy.make(UserCategory, category='Customer')
        self.customer_category_id = self.usercategory.id

        self.login_data = self.client.post(self.login_url, {'username': 'david', 'password': 'pqr12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.customer_token = "Token {}".format(self.login_data["token"])

        self.supplier_user = User.objects.create_user(username='james',
                                                      email='harshadasawant89@gmail.com',
                                                      password='pwd12345'
                                                      )
        self.supplier = mommy.make(Broker, name=self.supplier_user)
        self.user_supplier_category = mommy.make(UserCategory, category='Supplier')
        self.supplier_category_id = self.user_supplier_category.id

        self.login_data = self.client.post(self.login_url, {'username': 'james', 'password': 'pwd12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.supplier_token = "Token {}".format(self.login_data["token"])

        self.usercategory = mommy.make(UserCategory, category='test')
        self.category_id = self.usercategory.id
        self.booking1 = mommy.make(ManualBooking, company=self.sme, shipment_date='2018-07-04')
        self.booking2 = mommy.make(ManualBooking, supplier=self.supplier, shipment_date='2018-07-05')
        self.vehicle = mommy.make(Vehicle)
        self.owner = mommy.make(Owner)

    def test_get_booking_data_401_no_header(self):
        # Negative test for getting bookings data with no HTTP Header Authorization token
        response = self.client.get("/api/get-bookings-data/?category_id={}".format(self.category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_booking_data_401_wrong_token(self):
        # Negative test case for getting bookings data with wrong HTTP Header Authorization token
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/get-bookings-data/?category_id={}".format(self.category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_booking_data_401_expired_token(self):
        # Negative test case for getting bookings data with expired HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/get-bookings-data/?category_id={}".format(self.category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_booking_data_405_wrong_method(self):
        # Negative test for getting bookings data with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/get-bookings-data/?category_id={}".format(self.category_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_booking_data_400_no_category_id(self):
        # Negative test for getting bookings data with no category id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.getbookingsdata_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_booking_data_400_wrong_category_id(self):
        # Negative test for getting bookings data with wrong category id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.category_id = 100
        response = self.client.get("/api/get-bookings-data/?category_id={}".format(self.category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_booking_data_400_category_id_of_neither_customer_and_supplier(self):
        # Negative test for getting bookings data with category id of neither customer and supplier
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-bookings-data/?category_id={}".format(self.owner.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_bookings_data_400_category_id_as_string(self):
        # Negative test for getting bookings data with category id as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.category_id = "fjgjk"
        response = self.client.get("/api/get-bookings-data/?category_id={}".format(self.category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_booking_data_400_wrong_vehicle_id(self):
        # Negative test for getting bookings data with wrong vehicle id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.vehicle_id = 100
        response = self.client.get("/api/get-bookings-data/?category_id={}&vehicle_id={}".format(self.category_id, self.vehicle.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_bookings_data_400_vehicle_id_as_string(self):
        # Negative test for getting bookings data with vehicle id as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.vehicle_id = "fjgjk"
        response = self.client.get("/api/get-bookings-data/?category_id={}&vehicle_id={}".format(self.category_id, self.vehicle.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_bookings_data_400_with_other_objects(self):
        # Negative test for getting bookings data with other objects
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.abcd = "dgdgkgd"
        response = self.client.get("/api/get-bookings-data/?category_id={}&vehicle_id={}&abcd={}".format(self.category_id, self.vehicle.id, self.abcd))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_bookings_data_400_supplier_token_and_customer_id(self):
        # Negative test for getting bookings data with supplier token and customer_id
        self.client.credentials(HTTP_AUTHORIZATION=self.supplier_token)
        response = self.client.get("/api/get-bookings-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_bookings_data_400_customer_token_and_supplier_id(self):
        # Negative test for getting bookings data with customer token and supplier_id
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.get("/api/get-bookings-data/?category_id={}".format(self.supplier_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_bookings_data_200_customer_token_and_customer_id(self):
        # Positive test for getting bookings data with custom token and customer_id
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.get("/api/get-bookings-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.req = response.data['data']
        self.total_count = response.data['count']
        self.next = response.data['next']
        self.each_count = len(self.req)

        while self.next is not None:
            response = self.client.get(self.next)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.req = response.data['data']
            self.each_count += len(self.req)
            self.next = response.data['next']

        self.assertEqual(self.total_count, self.each_count)

    def test_get_bookings_data_200_supplier_token_and_supplier_id(self):
        # Positive test for getting bookings data with supplier token and supplier_id
        self.client.credentials(HTTP_AUTHORIZATION=self.supplier_token)
        response = self.client.get("/api/get-bookings-data/?category_id={}".format(self.supplier_category_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.req = response.data['data']
        self.total_count = response.data['count']
        self.next = response.data['next']
        self.each_count = len(self.req)

        while self.next is not None:
            response = self.client.get(self.next)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.req = response.data['data']
            self.each_count += len(self.req)
            self.next = response.data['next']

        self.assertEqual(self.total_count, self.each_count)

