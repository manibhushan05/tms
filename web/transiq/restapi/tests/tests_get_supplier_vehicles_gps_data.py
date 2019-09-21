import json

from model_mommy import mommy
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User

from broker.models import Broker, BrokerVehicle
from supplier.models import Vehicle, SupplierVehicle
from supplier.models import Supplier


class GetSupplierVehiclesGPSDataTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.getsuppliervehiclesgpsdata_url = reverse('get_supplier_vehicles_gps_data')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harshadasawant89@gmail.com',
                                             password='abc12345')

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'abc12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        self.supplier_user = User.objects.create_user(username='ross',
                                                      email='harshadasawant89@gmail.com',
                                                      password='rmr12345'
                                                      )

        self.supplier = mommy.make(Supplier, user=self.supplier_user)
        self.login_data = self.client.post(self.login_url, {'username': 'ross', 'password': 'rmr12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.supplier_token = "Token {}".format(self.login_data["token"])

        self.vehicle = mommy.make(Vehicle)
        self.supplier_vehicle = mommy.make(SupplierVehicle, supplier=self.supplier, vehicle=self.vehicle, ownership='O')

    def test_get_supplier_vehicles_gps_data_401_no_header(self):
        # Negative test for getting supplier vehicles gps data with no HTTP Header Authorization token
        response = self.client.get(self.getsuppliervehiclesgpsdata_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_supplier_vehicles_gps_data_401_wrong_token(self):
        # Negative test case for getting supplier vehicles gps data with wrong HTTP Header Authorization token
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.getsuppliervehiclesgpsdata_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_supplier_vehicles_gps_data_401_expired_token(self):
        # Negative test case for getting supplier vehicles gps data with expired HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.getsuppliervehiclesgpsdata_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_supplier_vehicles_gps_data_405_wrong_method(self):
        # Negative test for getting supplier vehicles gps data with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.getsuppliervehiclesgpsdata_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_supplier_vehicles_gps_data_400_non_supplier_token(self):
        # Negative test for getting supplier vehicles gps data with non supplier token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.getsuppliervehiclesgpsdata_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_supplier_vehicles_gps_data_400_with_other_objects(self):
        # Negative test for getting supplier vehicles gps data with other objects
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.abcd = "dgdgkgd"
        response = self.client.get("/api/get-supplier-vehicles-gps-data/?abcd={}".format(self.abcd))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_supplier_vehicles_gps_data_200(self):
        # Positive test for getting supplier vehicles gps data with correct vehicle id
        self.client.credentials(HTTP_AUTHORIZATION=self.supplier_token)
        response = self.client.get(self.getsuppliervehiclesgpsdata_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
