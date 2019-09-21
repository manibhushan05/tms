import json

from model_mommy import mommy
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from supplier.models import Vehicle


class GetVehicleGPSDataTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.getvehiclegpsdata_url = reverse('get_vehicle_gps_data')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harshadasawant89@gmail.com',
                                             password='abc12345')

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'abc12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        self.vehicle = mommy.make(Vehicle)

    def test_get_vehicle_gps_data_401_no_header(self):
        # Negative test for getting vehicle gps data with no HTTP Header Authorization token
        response = self.client.get("/api/get-vehicle-gps-data/?vehicle_id={}".format(self.vehicle.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_vehicle_gps_data_401_wrong_token(self):
        # Negative test case for getting vehicle gps data with wrong HTTP Header Authorization token
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/get-vehicle-gps-data/?vehicle_id={}".format(self.vehicle.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_vehicle_gps_data_401_expired_token(self):
        # Negative test case for getting vehicle gps data with expired HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/get-vehicle-gps-data/?vehicle_id={}".format(self.vehicle.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_vehicle_gps_data_405_wrong_method(self):
        # Negative test for getting vehicle gps data with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/get-vehicle-gps-data/?vehicle_id={}".format(self.vehicle.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_vehicle_data_data_400_no_vehicle_id(self):
        # Negative test for getting vehicle gps data with no vehicle id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-vehicle-gps-data/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_vehicle_gps_data_400_wrong_vehicle_id(self):
        # Negative test for getting vehicle gps data with wrong category id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.vehicle.id = 100
        response = self.client.get("/api/get-vehicle-gps-data/?vehicle_id={}".format(self.vehicle.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_vehicle_gps_data_400_vehicle_id_as_string(self):
        # Negative test for getting vehicle gps data with vehicle id as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.vehicle.id = "fjgjk"
        response = self.client.get("/api/get-vehicle-gps-data/?vehicle_id={}".format(self.vehicle.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_vehicle_gps_data_400_with_other_objects(self):
        # Negative test for getting vehicle gps data with other objects
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.abcd = "dgdgkgd"
        response = self.client.get("/api/get-bookings-data/?vehicle_id={}&abcd={}".format(self.vehicle.id, self.abcd))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_vehicle_gps_data_200(self):
        # Positive test for getting bookings data with correct vehicle id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-vehicle-gps-data/?vehicle_id={}".format(self.vehicle.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
