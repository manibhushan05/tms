import json
from datetime import datetime
from authentication.models import Profile

from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from employee.models import Employee
from restapi.helper_api import generate_random_string
from supplier.models import Service, Supplier, ContactPerson, Driver, DriverPhone, Vehicle, DriverVehicle, \
    VehicleStatus, VehicleInsurer, VehicleInsurance, VehiclePUC, VehicleFitness, VehiclePermit, SupplierVehicle
from utils.models import State, City, AahoOffice, Bank, VehicleBodyCategory, VehicleCategory


class SupplierSetup(APITestCase):
    """
        Setup dummy data for tesing purpose
    """

    def setUp(self):
        self.login_url = reverse('login')
        self.test_user = User.objects.create_user('testUser', 'test@example.com', 'testPassword')
        self.test_user2 = User.objects.create_user('testUser2', 'test@example.com', 'testPassword2')
        self.test_user3 = User.objects.create_user('testUser3', 'test@example.com', 'testPassword3')
        self.test_profile = mommy.make(Profile, user=self.test_user)
        self.test_profile1 = mommy.make(Profile, user=self.test_user2)
        self.test_profile3 = mommy.make(Profile, user=self.test_user3)
        self.login_data = self.client.post(self.login_url, {"username": "testUser", "password": "testPassword"}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        self.state = mommy.make(State)
        self.city = mommy.make(City)
        self.aaho_office = mommy.make(AahoOffice)
        self.aaho_poc = mommy.make(Employee)
        self.account_details = mommy.make(Bank)
        self.service = mommy.make(Service)
        self.supplier = mommy.make(Supplier)
        self.dummy_user = mommy.make(User)
        self.contact_person = mommy.make(ContactPerson, user=self.dummy_user)
        self.driver = mommy.make(Driver, user=self.dummy_user)
        self.driver_phone = mommy.make(DriverPhone, driver=self.driver)
        self.vehicle_body_category = mommy.make(VehicleBodyCategory)
        self.vehicle_category = mommy.make(VehicleCategory)
        self.vehicle = mommy.make(Vehicle)
        self.driver_vehicle = mommy.make(DriverVehicle)
        self.vehicle_status = mommy.make(VehicleStatus)
        self.vehicle_insurer = mommy.make(VehicleInsurer)
        self.vehicle_insurance = mommy.make(VehicleInsurance)
        self.vehicle_puc = mommy.make(VehiclePUC)
        self.vehicle_fitness = mommy.make(VehicleFitness)
        self.vehicle_permit = mommy.make(VehiclePermit)
        self.supplier_vehicle = mommy.make(SupplierVehicle)


class ServiceTest(SupplierSetup):
    """
        Test cases for Services
    """

    def setUp(self):
        super().setUp()
        self.service_data = {
            "name": "Assasination",
            "deleted": True,
            "deleted_on": "2018-06-22T15:41:01.470178",
        }
        self.service_minimum_data = {

        }
        self.create_url = reverse("supplier_service_create")
        self.update_url = reverse("supplier_service_update", kwargs={"pk": self.service.id})
        self.partial_update_url = reverse("supplier_service_partial_update", kwargs={"pk": self.service.id})
        self.retrieve_url = reverse("supplier_service_retrieve", kwargs={"pk": self.service.id})

    def test_create_service_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.service_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_service_with_other_data_format(self):
        pass

    def test_create_service_with_valid_name(self):
        data = self.service_minimum_data.copy()

        data["name"] = "aaho_service786"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = generate_random_string(49)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = generate_random_string(50)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_service_with_invalid_name(self):
        data = self.service_minimum_data.copy()

        data["name"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_service_with_valid_deleted(self):
        data = self.service_minimum_data.copy()

        data["deleted"] = True
        data["name"] = "valid123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["name"] = "valid124"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["name"] = "valid125"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["name"] = "valid126"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_service_with_valid_deleted_on(self):
        data = self.service_minimum_data.copy()

        data["deleted_on"] = datetime.now()
        data["name"] = "valid120"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["name"] = "valid121"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        data["name"] = "valid122"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_service_with_invalid_deleted_on(self):
        data = self.service_minimum_data.copy()

        data["deleted_on"] = "invalid_format"
        data["name"] = "valid120"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        data["name"] = "valid121"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        data["name"] = "valid121"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_service_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_service_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.service_data.copy()
        data["deleted_on"] = "2018-06-22"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.service_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.service_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_service_with_invalid_method(self):
        data = self.service_data.copy()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # update service test

    def test_update_service_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_service_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_service_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"name": "newName"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_service_with_valid_name(self):
        data = self.service_minimum_data.copy()

        data["name"] = "valid1234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["name"] = generate_random_string(49)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["name"] = generate_random_string(50)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_service_with_invalid_name(self):
        data = self.service_minimum_data.copy()

        data["name"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_service_with_valid_deleted(self):
        data = self.service_minimum_data.copy()

        data["deleted"] = True
        data["name"] = "aaho100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_service_with_valid_deleted_on(self):
        data = self.service_minimum_data.copy()

        data["deleted_on"] = datetime.now()
        data["name"] = "aaho100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = str(datetime.now())
        data["name"] = "aaho101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = None
        data["name"] = "aaho102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_service_with_invalid_deleted_on(self):
        data = self.service_minimum_data.copy()

        data["deleted_on"] = "invalid_format"
        data["name"] = "aaho100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12-Dec-2021"
        data["name"] = "aaho101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_service_with_invalid_method(self):
        data = self.service_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_retrieve_existing_service(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_service(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_service_retrieve",
                                   kwargs={"pk": self.service.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SupplierTest(SupplierSetup):
    """
        Test cases for supplier
    """

    def setUp(self):
        super().setUp()
        self.supplier_data = {
            "code": "KTVR",
            "address": "Konoha",
            "pin": "213212",
            "route": "through great Naruto bridge",
            "deleted": True,
            "deleted_on": "2018-05-02T13:06:00.672262",
            "user": self.test_user.username,
            "city": self.city.id,
            "aaho_office": self.aaho_office.id,
            "aaho_poc": self.aaho_poc.id,
            "services": [self.service.id],
            "serving_states": [self.state.id],
            "phone": "2312231232",
            'pan': 'CBPPK8768P'
        }
        self.minimum_valid_data = {
            "user": self.test_user.username,
            "phone": "2312231232",
            'pan': None,
            "serving_states": [self.state.id],
        }
        self.create_url = reverse("supplier_supplier_create")
        self.update_url = reverse("supplier_supplier_update", kwargs={"pk": self.supplier.id})
        self.partial_update_url = reverse("supplier_supplier_partial_update", kwargs={"pk": self.supplier.id})
        self.retrieve_url = reverse("supplier_supplier_retrieve", kwargs={"pk": self.supplier.id})

    def test_create_supplier_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_valid_code(self):
        data = self.minimum_valid_data.copy()

        data["code"] = "B@1b"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["code"] = generate_random_string(4)
        data["phone"] = "1231231200"
        data['pan'] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["code"] = None
        data["phone"] = "1231231201"
        data['pan'] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_valid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = "valid_address"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = generate_random_string(299)
        data["phone"] = "1231231200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = generate_random_string(300)
        data["phone"] = "1231231201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = None
        data["phone"] = "1231231202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_invalid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = generate_random_string(301)
        data["phone"] = "1231231200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_with_valid_pin(self):
        data = self.minimum_valid_data.copy()

        data["pin"] = "620015"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pin"] = '400078'
        data["phone"] = "1231231200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = None
        data["phone"] = "1231231202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_invalid_pin(self):
        data = self.minimum_valid_data.copy()

        data["pin"] = generate_random_string(5)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = generate_random_string(7)
        data["phone"] = "1231231200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["address"] = ""
        data["phone"] = "1231231202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_with_valid_route(self):
        data = self.minimum_valid_data.copy()

        data["route"] = "valid_route"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["route"] = generate_random_string(254)
        data["phone"] = "1231231200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["route"] = generate_random_string(255)
        data["phone"] = "1231231201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["route"] = None
        data["phone"] = "1231231202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_invalid_route(self):
        data = self.minimum_valid_data.copy()

        data["route"] = generate_random_string(256)
        data["phone"] = "1231231200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        data["phone"] = "1212120000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["phone"] = "1212120001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["phone"] = "1212120002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["phone"] = "1212120003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        data["phone"] = "1212120000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["phone"] = "1212120001"
        data['pan'] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        data["phone"] = "1212120002"
        data['pan'] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_valid_user(self):
        data = self.minimum_valid_data.copy()

        data["user"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_valid_city(self):
        data = self.minimum_valid_data.copy()

        data["city"] = self.city.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["city"] = None
        data["phone"] = "1234567002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_invalid_city(self):
        data = self.minimum_valid_data.copy()

        data["supplier_city"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_city"] = 0
        data["phone"] = "1234567000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_city"] = 12.2345
        data["phone"] = "1234567001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_city"] = "invalid_city"
        data["phone"] = "1234567002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_city"] = datetime.now()
        data["phone"] = "1234567003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_city"] = str(datetime.now())
        data["phone"] = "1234567004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_with_valid_aaho_office(self):
        data = self.minimum_valid_data.copy()

        data["aaho_office"] = self.aaho_office.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["aaho_office"] = None
        data["phone"] = "1234567002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_invalid_aaho_office(self):
        data = self.minimum_valid_data.copy()

        data["aaho_office"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = 0
        data["phone"] = "1234567000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = 12.2345
        data["phone"] = "1234567001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = "invalid_office"
        data["phone"] = "1234567002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = datetime.now()
        data["phone"] = "1234567003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = str(datetime.now())
        data["phone"] = "1234567004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_with_valid_aaho_poc(self):
        data = self.minimum_valid_data.copy()

        data["aaho_poc"] = self.aaho_poc.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["aaho_poc"] = None
        data["phone"] = "1234567002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_invalid_aaho_poc(self):
        data = self.minimum_valid_data.copy()

        data["aaho_poc"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = 0
        data["phone"] = "1234567000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = 12.2345
        data["phone"] = "1234567001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = "invalid_poc"
        data["phone"] = "1234567002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = datetime.now()
        data["phone"] = "1234567003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = str(datetime.now())
        data["phone"] = "1234567004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_with_valid_services(self):
        data = self.minimum_valid_data.copy()

        data["services"] = [self.service.id]
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_supplier_with_invalid_services(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["services"] = -123
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["services"] = 0
    #     data["phone"] = "1234567000"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["services"] = 12.2345
    #     data["phone"] = "1234567001"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["services"] = "invalid_service"
    #     data["phone"] = "1234567002"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["services"] = datetime.now()
    #     data["phone"] = "1234567003"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["services"] = str(datetime.now())
    #     data["phone"] = "1234567004"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["services"] = None
    #     data["phone"] = "1234567005"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_with_valid_serving_states(self):
        data = self.minimum_valid_data.copy()

        data["serving_states"] = [self.state.id]
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_invalid_serving_states(self):
        data = self.minimum_valid_data.copy()

        data["serving_states"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["serving_states"] = 0
        data["phone"] = "1234567000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["serving_states"] = 12.2345
        data["phone"] = "1234567001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["serving_states"] = "invalid_service"
        data["phone"] = "1234567002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["serving_states"] = datetime.now()
        data["phone"] = "1234567003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["serving_states"] = str(datetime.now())
        data["phone"] = "1234567004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["serving_states"] = None
        data["phone"] = "1234567005"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_with_code(self):
        data = self.minimum_valid_data.copy()
        data["code"] = "ERST"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.supplier_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.supplier_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_supplier_with_invalid_request(self):
        data = self.minimum_valid_data.copy()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_supplier_with_minimum_valid_date(self):
        data = self.minimum_valid_data.copy()
        data['pan'] = 'CBPPK6928P'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_supplier_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_supplier(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_supplier(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_supplier_retrieve",
                                   kwargs={"pk": self.supplier.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ContactPersonTest(SupplierSetup):
    """
        Test cases for Contact Person
    """

    def setUp(self):
        super().setUp()
        self.contact_person_data = {
            "active": False,
            "deleted": False,
            "deleted_on": None,
            "user": self.test_user.username,
            "supplier": self.supplier.id
        }
        self.minimum_valid_data = {
            "supplier": self.supplier.id,
            "user": self.test_user.username
        }
        self.create_url = reverse("supplier_contact_person_create")
        self.update_url = reverse("supplier_contact_person_update", kwargs={"pk": self.contact_person.id})
        self.partial_update_url = reverse("supplier_contact_person_partial_update",
                                          kwargs={"pk": self.contact_person.id})
        self.retrieve_url = reverse("supplier_contact_person_retrieve", kwargs={"pk": self.contact_person.id})

    def test_create_contact_person_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_contact_person_with_valid_active(self):
        data = self.minimum_valid_data.copy()

        data["active"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["active"] = False
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["active"] = 1
        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_contact_person_with_invalid_active(self):
        data = self.minimum_valid_data.copy()

        data["active"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["active"] = -123
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_contact_person_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_contact_person_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -123
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_contact_person_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_contact_person_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_contact_person_name_with_valid_user(self):
        data = self.minimum_valid_data.copy()

        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_contact_person_name_with_invalid_user(self):
        data = self.minimum_valid_data.copy()

        data["user"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_contact_person_with_valid_supplier(self):
        data = self.minimum_valid_data.copy()

        data["supplier"] = self.supplier.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_contact_person_with_invalid_supplier(self):
        data = self.minimum_valid_data.copy()

        data["supplier"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = 0
        data["phone"] = "1234567000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = 12.2345
        data["phone"] = "1234567001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = "invalid_service"
        data["phone"] = "1234567002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = datetime.now()
        data["phone"] = "1234567003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = str(datetime.now())
        data["phone"] = "1234567004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = None
        data["phone"] = "1234567005"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_contact_person_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.contact_person_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_supplier_with_duplicatie_user(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     data = self.contact_person_data.copy()
    #     data["user"] = self.contact_person.user.username
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_contact_person_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.contact_person_data.copy()
        data["deleted_on"] = "2018-06-22"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.contact_person_data.copy()
        data["supplier"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = "InvalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = self.service.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.contact_person_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.contact_person_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.contact_person_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.contact_person_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.contact_person_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.contact_person_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_contact_person_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_contact_person_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_contact_person_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.contact_person_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_contact_person_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_contact_person(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_contact_person(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_contact_person_retrieve",
                                   kwargs={"pk": self.contact_person.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DriverTest(SupplierSetup):
    """
        Test cases for Driver
    """

    def setUp(self):
        super().setUp()
        self.driver_data = {
            "address": "21 Baker Street",
            "driving_licence_number": "1232dasd1221",
            "driving_licence_location": "Village hidden in the rain",
            "driving_licence_validity": "2018-06-22",
            "smartphone_available": False,

            "deleted": False,
            "deleted_on": None,
            "user": self.test_user.username,
        }
        self.minimum_valid_data = {
            "user": self.test_user.username
        }
        self.create_url = reverse("supplier_supplier_driver_create")
        self.update_url = reverse("supplier_supplier_driver_update", kwargs={"pk": self.driver.id})
        self.partial_update_url = reverse("supplier_supplier_driver_partial_update",
                                          kwargs={"pk": self.driver.id})
        self.retrieve_url = reverse("supplier_supplier_driver_retrieve", kwargs={"pk": self.driver.id})

    def test_create_driver_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_with_valid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = generate_random_string(299)
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = generate_random_string(300)
        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_driver_with_invalid_address(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["address"] = generate_random_string(301)
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_with_valid_driving_licence_number(self):
        data = self.minimum_valid_data.copy()

        data["driving_licence_number"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = generate_random_string(49)
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = generate_random_string(50)
        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_driver_with_invalid_driving_licence_number(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["driving_licence_number"] = generate_random_string(51)
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_with_valid_driving_licence_location(self):
        data = self.minimum_valid_data.copy()

        data["driving_licence_location"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_location"] = generate_random_string(49)
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_location"] = generate_random_string(50)
        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_driver_with_invalid_driving_licence_location(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["driving_licence_location"] = generate_random_string(51)
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_with_valid_driving_licence_validity(self):
        data = self.minimum_valid_data.copy()

        data["driving_licence_validity"] = "12-Dec-2022"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_validity"] = "2024-12-09"
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_validity"] = None
        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_driver_with_invalid_driving_licence_validity(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["driving_licence_validity"] = "09/12/2018"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["driving_licence_validity"] = "18-12-09"
    #     data["user"] = self.test_user2.username
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["driving_licence_validity"] = "09-12-18"
    #     data["user"] = self.test_user3.username
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_with_valid_smartphone_available(self):
        data = self.minimum_valid_data.copy()

        data["smartphone_available"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["smartphone_available"] = False
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["smartphone_available"] = 1
        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        data["user"] = self.test_user3.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_driver_with_invalid_deleted_on(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["deleted_on"] = "invalid_format"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["deleted_on"] = "09/12/2018"
    #     data["user"] = self.test_user2.username
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["deleted_on"] = "12/09/18"
    #     data["user"] = self.test_user3.username
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_with_valid_user(self):
        data = self.minimum_valid_data.copy()

        data["user"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["user"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_driver_with_invalid_user(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["user"] = "invalid_user"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["user"] = ""
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["user"] = None
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driving_licence_validity field to minimum valid data

    def test_create_driver_with_driving_licence_validity(self):
        self.minimum_valid_data["driving_licence_validity"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_supplier_with_duplicatie_user(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     data = self.driver_data.copy()
    #     data["user"] = self.driver.user.username
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_driver_invalid_data(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     data = self.driver_data.copy()
    #     data["driving_licence_validity"] = "2018-06-22T17:59:01.048782"
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data = self.driver_data.copy()
    #     data["user"] = -1
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["user"] = "InvalidId"
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["user"] = self.test_user.id * 100
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.driver_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.driver_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_driver_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_driver_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_driver_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_driver_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_driver(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_driver(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_supplier_driver_retrieve",
                                   kwargs={"pk": self.driver.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DriverPhoneTest(SupplierSetup):
    """
        Test cases for Driver phone
    """

    def setUp(self):
        super().setUp()
        self.driver_phone_data = {
            "phone": "1232112321",
            "active": True,
            "deleted": False,
            "deleted_on": None,
            "driver": self.driver.id
        }
        self.minimum_valid_data = {
            "phone": "1232112321"
        }
        self.create_url = reverse("supplier_supplier_driver_phone_create")
        self.update_url = reverse("supplier_supplier_driver_phone_update", kwargs={"pk": self.driver_phone.id})
        self.partial_update_url = reverse("supplier_supplier_driver_phone_partial_update",
                                          kwargs={"pk": self.driver_phone.id})
        self.retrieve_url = reverse("supplier_supplier_driver_phone_retrieve", kwargs={"pk": self.driver_phone.id})

    def test_create_driver_phone_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_phone_with_valid_phone(self):
        data = self.minimum_valid_data.copy()

        data["phone"] = "1234567890"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = "9234567890"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_phone_with_invalid_phone(self):
        data = self.minimum_valid_data.copy()

        data["phone"] = "0234567890"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "123456789"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "12345678911"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_phone_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        data["phone"] = "1212120000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["phone"] = "1212120001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["phone"] = "1212120002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["phone"] = "1212120003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_phone_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        data["phone"] = "1212120000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        data["phone"] = "1212120001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_phone_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        data["phone"] = "1212120000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["phone"] = "1212120001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        data["phone"] = "1212120002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_phone_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        data["phone"] = "1212120000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        data["phone"] = "1212120001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        data["phone"] = "1212120002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_phone_with_valid_driver(self):
        data = self.minimum_valid_data.copy()

        data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_phone_with_invalid_driver(self):
        data = self.minimum_valid_data.copy()

        data["driver"] = "invalid_driver"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = -123
        data["phone"] = "7887034700"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = 0
        data["phone"] = "7887034701"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = 123678356
        data["phone"] = "7887034702"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = 1.233
        data["phone"] = "7887034704"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = datetime.now()
        data["phone"] = "7887034706"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_phone_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.driver_phone_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_phone_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.driver_phone_data.copy()
        data["deleted_on"] = "2018-06-22"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.driver_phone_data.copy()
        data["driver"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = "InvalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = self.driver.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.driver_phone_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.driver_phone_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.driver_phone_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.driver_phone_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.driver_phone_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.driver_phone_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_driver_phone_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_driver_phone_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_driver_phone_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.driver_phone_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_driver_phone_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_driver_phone(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_driver_phone(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_supplier_driver_phone_retrieve",
                                   kwargs={"pk": self.driver_phone.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VehicleBodyCategoryTest(SupplierSetup):
    """
        Test cases for Vehicle Body Category
    """

    def setUp(self):
        super().setUp()
        self.vehicle_body_category_data = {
            "name": "prime",
            "deleted": False,
            "deleted_on": None,
        }
        self.minimum_valid_data = {
            "name": "optimus"
        }
        self.create_url = reverse("supplier_vehicle_body_category_create")
        self.update_url = reverse("supplier_vehicle_body_category_update", kwargs={"pk": self.vehicle_body_category.id})
        self.partial_update_url = reverse("supplier_vehicle_body_category_partial_update",
                                          kwargs={"pk": self.vehicle_body_category.id})
        self.retrieve_url = reverse("supplier_vehicle_body_category_retrieve",
                                    kwargs={"pk": self.vehicle_body_category.id})

    def test_create_vehicle_body_category_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_body_category_with_valid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = "super"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = generate_random_string(99)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = generate_random_string(100)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_body_category_with_invalid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = generate_random_string(101)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["name"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_body_category_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_body_category_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_body_category_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_body_category_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_body_category_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_body_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_body_category_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_body_category_data.copy()
        data["deleted_on"] = "2018-06-22"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.vehicle_body_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_body_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_body_category_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.vehicle_body_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_body_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_body_category_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vehicle_body_category_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_vehicle_body_category_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_vehicle_body_category_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.vehicle_body_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_vehicle_body_category_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_vehicle_body_category(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_vehicle_body_category(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_vehicle_body_category_retrieve",
                                   kwargs={"pk": self.vehicle_body_category.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VehicleCategoryTest(SupplierSetup):
    """
        Test cases for Vehicle Category
    """

    def setUp(self):
        super().setUp()
        self.vehicle_category_data = {
            "vehicle_type": "10 Tyre Taurus",
            "capacity": "16 tons",
            "truck_body_type": "Hotshot",
            "description": "A massive one",
            "priority": "1",
            "deleted": False,
            "deleted_on": None,
            "truck_body": self.vehicle_body_category.id
        }
        self.minimum_valid_data = {
            "vehicle_type": "10 Tyre Taurus",
        }
        self.create_url = reverse("supplier_vehicle_category_create")
        self.update_url = reverse("supplier_vehicle_category_update", kwargs={"pk": self.vehicle_category.id})
        self.partial_update_url = reverse("supplier_vehicle_category_partial_update",
                                          kwargs={"pk": self.vehicle_category.id})
        self.retrieve_url = reverse("supplier_vehicle_category_retrieve", kwargs={"pk": self.vehicle_category.id})
        self.filter_url = reverse('supplier_vehicle_category_list')

    def test_create_vehicle_category_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_category_with_valid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = "12Type Open body"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = generate_random_string(99)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = generate_random_string(100)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_category_with_invalid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = generate_random_string(101)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_category_with_valid_capacity(self):
        data = self.minimum_valid_data.copy()

        data["capacity"] = "120000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["capacity"] = generate_random_string(29)
        data["vehicle_type"] = "valid100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["capacity"] = generate_random_string(30)
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_category_with_invalid_capacity(self):
        data = self.minimum_valid_data.copy()

        data["capacity"] = generate_random_string(31)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["capacity"] = None
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_category_with_valid_truck_body_type(self):
        data = self.minimum_valid_data.copy()

        data["truck_body_type"] = "semi_open"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_body_type"] = generate_random_string(49)
        data["vehicle_type"] = "valid100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_body_type"] = generate_random_string(50)
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_category_with_invalid_truck_body_type(self):
        data = self.minimum_valid_data.copy()

        data["truck_body_type"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_body_type"] = None
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_category_with_valid_description(self):
        data = self.minimum_valid_data.copy()

        data["description"] = "10_tyre_semi_closed"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["description"] = generate_random_string(499)
        data["vehicle_type"] = "valid100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["description"] = generate_random_string(500)
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_category_with_invalid_description(self):
        data = self.minimum_valid_data.copy()

        data["description"] = generate_random_string(501)
        data["vehicle_type"] = "valid100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["description"] = None
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_category_with_valid_priority(self):
        data = self.minimum_valid_data.copy()

        data["priority"] = "VALID123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["priority"] = generate_random_string(9)
        data["vehicle_type"] = "valid100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["priority"] = generate_random_string(10)
        data["vehicle_type"] = "valid1001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_category_with_invalid_priority(self):
        data = self.minimum_valid_data.copy()

        data["priority"] = generate_random_string(11)
        data["vehicle_type"] = "valid100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["priority"] = None
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_category_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["vehicle_type"] = "valid100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["vehicle_type"] = "valid102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_category_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_category_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["vehicle_type"] = "valid100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_category_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        data["vehicle_type"] = "valid100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        data["vehicle_type"] = "valid102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_category_with_valid_truck_body(self):
        data = self.minimum_valid_data.copy()

        data["truck_body"] = self.vehicle_body_category.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_category_with_invalid_truck_body(self):
        data = self.minimum_valid_data.copy()

        data["truck_body"] = "invalid12"
        data["vehicle_type"] = "valid100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_body"] = -123
        data["vehicle_type"] = "valid101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_body"] = 0
        data["vehicle_type"] = "valid102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_body"] = 123678356
        data["vehicle_type"] = "valid103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_body"] = 1.233
        data["vehicle_type"] = "valid104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_body"] = datetime.now()
        data["vehicle_type"] = "valid105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_category_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Added field capacity to minimum valid data
    def test_create_vehicle_category_with_capacity(self):
        self.vehicle_category_data["capacity"] = "10 tonnes"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_category_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_category_data.copy()
        data["deleted_on"] = "2018-06-22"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.vehicle_category_data.copy()
        data["truck_body"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_body"] = "InvalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_body"] = self.vehicle_body_category.id * 223
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.vehicle_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_category_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.vehicle_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_category_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vehicle_category_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_vehicle_category_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_vehicle_category_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.vehicle_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_vehicle_category_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_vehicle_category(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_vehicle_category(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_vehicle_category_retrieve",
                                   kwargs={"pk": self.vehicle_category.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_supplier_vehicle_filter_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class VehicleTest(SupplierSetup):
    """
        Test cases for Vehicle
    """

    def setUp(self):
        super().setUp()
        self.vehicle_data = {
            "vehicle_number": "mh12nx2273",
            "vehicle_capacity": 213,
            "chassis_number": "some number",
            "engine_number": "some number",
            "registration_year": "2018",
            "registration_validity": None,
            "gps_enabled": False,

            "deleted": False,
            "deleted_on": None,
            "vehicle_type": self.vehicle_category.id
        }
        self.minimum_valid_data = {
            "vehicle_number": "mh12nx2273",
        }
        self.logout_url = reverse('logout')
        self.create_url = reverse("supplier_vehicle_create")
        self.update_url = reverse("supplier_vehicle_update", kwargs={"pk": self.vehicle.id})
        self.partial_update_url = reverse("supplier_vehicle_partial_update",
                                          kwargs={"pk": self.vehicle.id})
        self.retrieve_url = reverse("supplier_vehicle_retrieve", kwargs={"pk": self.vehicle.id})
        self.filter_url = reverse("supplier_vehicle_list")

    def test_create_vehicle_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_valid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = "mh12ncx2212"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = "MH12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = "MH12Mx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = "MH-12-MX-2203"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_invalid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = generate_random_string(12)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_with_valid_vehicle_capacity(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_capacity"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_capacity"] = 9999
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_capacity"] = 10000
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_capacity"] = None
        data["vehicle_number"] = "mh12ncx2202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_invalid_vehicle_capacity(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_capacity"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_capacity"] = 10001
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_capacity"] = "invalid_capacity"
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_with_valid_chassis_number(self):
        data = self.minimum_valid_data.copy()

        data["chassis_number"] = generate_random_string(16)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["chassis_number"] = generate_random_string(17)
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["chassis_number"] = None
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_invalid_chassis_number(self):
        data = self.minimum_valid_data.copy()

        data["chassis_number"] = generate_random_string(18)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_with_valid_engine_number(self):
        data = self.minimum_valid_data.copy()

        data["engine_number"] = generate_random_string(14)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["engine_number"] = generate_random_string(15)
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["engine_number"] = None
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_invalid_engine_number(self):
        data = self.minimum_valid_data.copy()

        data["engine_number"] = generate_random_string(16)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_with_valid_registration_year(self):
        data = self.minimum_valid_data.copy()

        data["registration_year"] = "2018"
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["registration_year"] = None
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_invalid_registration_year(self):
        data = self.minimum_valid_data.copy()

        data["registration_year"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["registration_year"] = "09/12/2018"
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["registration_year"] = "09-12-18"
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["registration_year"] = "18-12-09"
        data["vehicle_number"] = "mh12ncx2202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_with_valid_registration_validity(self):
        data = self.minimum_valid_data.copy()

        data["registration_validity"] = "12-Dec-2024"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["registration_validity"] = "2022-12-09"
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["registration_validity"] = None
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_invalid_registration_validity(self):
        data = self.minimum_valid_data.copy()

        data["registration_validity"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["registration_validity"] = "09/12/2024"
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["registration_validity"] = "09-12-22"
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["registration_validity"] = "25-12-09"
        data["vehicle_number"] = "mh12ncx2202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle__with_valid_gps_enabled(self):
        data = self.minimum_valid_data.copy()

        data["gps_enabled"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gps_enabled"] = False
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gps_enabled"] = 0
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gps_enabled"] = 1
        data["vehicle_number"] = "mh12ncx2202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_invalid_gps_enabled(self):
        data = self.minimum_valid_data.copy()

        data["gps_enabled"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gps_enabled"] = -12
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["vehicle_number"] = "mh12ncx2202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_valid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = self.vehicle_category.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_invalid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = "invalid12"
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] = -123
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] = 0
        data["vehicle_number"] = "mh12ncx2202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] = 123678356
        data["vehicle_number"] = "mh12ncx2203"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] = 1.233
        data["vehicle_number"] = "mh12ncx2204"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] = datetime.now()
        data["vehicle_number"] = "mh12ncx2205"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Adding registration_validity field to minimum valid data
    def test_create_vehicle_with_registration_validity(self):
        self.minimum_valid_data["registration_validity"] = "2018-06-22"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_type field to minimum valid data

    def test_create_vehicle_with_vehicle_type(self):
        self.minimum_valid_data["vehicle_type"] = self.vehicle_category.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_data.copy()
        data["registration_validity"] = "2018-06-22T17:59:01.048782"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.vehicle_data.copy()
        data["vehicle_type"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] = "InvalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] = self.vehicle_category.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vehicle_with_invalid_request(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_vehicle_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_vehicle_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_data
        data['registration_year'] = '2018-03-01'
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_vehicle_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False, 'vehicle_number': 'mh08ty9897'}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_vehicle(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_vehicle(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_vehicle_retrieve",
                                   kwargs={"pk": self.vehicle.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_vehicle_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.vehicle.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.vehicle.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vehicle_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vehicle_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vehicle_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class DriverVehicleTest(SupplierSetup):
    """
        Test cases for Driver Vehicle
    """

    def setUp(self):
        super().setUp()
        self.driver_vehicle_data = {
            "driver": self.driver.id,
            "vehicle": self.vehicle.id,
            "active": False,
            "deleted": False,
            "deleted_on": None

        }
        self.minimum_valid_data = {
            "driver": self.driver.id,
            "vehicle": self.vehicle.id,
            "active": False,
        }
        self.create_url = reverse("supplier_driver_vehicle_create")
        self.update_url = reverse("supplier_driver_vehicle_update", kwargs={"pk": self.driver_vehicle.id})
        self.partial_update_url = reverse("supplier_driver_vehicle_partial_update",
                                          kwargs={"pk": self.driver_vehicle.id})
        self.retrieve_url = reverse("supplier_driver_vehicle_retrieve", kwargs={"pk": self.driver_vehicle.id})

    def test_create_driver_vehicle_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_vehicle_with_valid_driver(self):
        data = self.minimum_valid_data.copy()

        data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_vehicle_with_invalid_driver(self):
        data = self.minimum_valid_data.copy()

        data["driver"] = "invalid123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = 1.234
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_vehicle_with_valid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = self.vehicle.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_vehicle_with_invalid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = "invalid123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 1.234
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_vehicle__with_valid_active(self):
        data = self.minimum_valid_data.copy()

        data["active"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["active"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["active"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["active"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_vehicle_with_valid_active(self):
        data = self.minimum_valid_data.copy()

        data["active"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["active"] = -12
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_vehicle_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_vehicle_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_vehicle_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_vehicle_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_vehicle_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.driver_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_vehicle_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.driver_vehicle_data.copy()
        data["deleted_on"] = "2018-06-22"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.driver_vehicle_data.copy()
        data["driver"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = "InvalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = self.driver.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.driver_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.driver_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.driver_vehicle_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.driver_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.driver_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.driver_vehicle_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_driver_vehicle_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_driver_vehicle_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_driver_vehicle_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.driver_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_driver_vehicle_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_driver_vehicle(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_driver_vehicle(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_driver_vehicle_retrieve",
                                   kwargs={"pk": self.driver_vehicle.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VehicleStatusTest(SupplierSetup):
    """
        Test cases for Vehicle Status
    """

    def setUp(self):
        super().setUp()
        self.vehicle_status_data = {
            "status": 'UD',
            "vehicle": self.vehicle.id,
            "active": False,
            "deleted": False,
            "deleted_on": None

        }
        self.minimum_valid_data = {

            "vehicle": self.vehicle.id
        }
        self.create_url = reverse("supplier_vehicle_status_create")
        self.update_url = reverse("supplier_vehicle_status_update", kwargs={"pk": self.vehicle_status.id})
        self.partial_update_url = reverse("supplier_vehicle_status_partial_update",
                                          kwargs={"pk": self.vehicle_status.id})
        self.retrieve_url = reverse("supplier_vehicle_status_retrieve", kwargs={"pk": self.vehicle_status.id})

    def test_create_vehicle_status_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_status_with_valid_status(self):
        data = self.minimum_valid_data.copy()

        data["status"] = "LD"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = "LG"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = "UD"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = "UG"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_status_with_invalid_status(self):
        data = self.minimum_valid_data.copy()

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = 123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_status_with_valid_active(self):
        data = self.minimum_valid_data.copy()

        data["active"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["active"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["active"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["active"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_status_with_invalid_active(self):
        data = self.minimum_valid_data.copy()

        data["active"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["active"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_status_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_status_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_status_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_status_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_status_with_valid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = self.vehicle.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_status_with_invalid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = "invalid12"
        data["vehicle_number"] = "mh12ncx2200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = -123
        data["vehicle_number"] = "mh12ncx2201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 0
        data["vehicle_number"] = "mh12ncx2202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 123678356
        data["vehicle_number"] = "mh12ncx2203"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 1.233
        data["vehicle_number"] = "mh12ncx2204"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = datetime.now()
        data["vehicle_number"] = "mh12ncx2205"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_status_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_status_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding field status to minimum valid data
    def test_create_vehicle_status_with_status(self):
        self.vehicle_status_data["status"] = "UD"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_status_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_status_data.copy()
        data["deleted_on"] = "2018-06-22"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.vehicle_status_data.copy()
        data["vehicle"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = "InvalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = self.vehicle.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.vehicle_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_status_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.vehicle_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_status_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vehicle_status_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_vehicle_status_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_vehicle_status_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.vehicle_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_vehicle_status_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_vehicle_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_vehicle_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_vehicle_status_retrieve",
                                   kwargs={"pk": self.vehicle_status.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VehicleInsurerTest(SupplierSetup):
    """
        Test cases for Vehicle Insurer
    """

    def setUp(self):
        super().setUp()
        self.vehicle_insurer_data = {
            "name": 'Test',
            "deleted": False,
            "deleted_on": None

        }
        self.minimum_valid_data = {

        }
        self.create_url = reverse("supplier_vehicle_insurer_create")
        self.update_url = reverse("supplier_vehicle_insurer_update", kwargs={"pk": self.vehicle_insurer.id})
        self.partial_update_url = reverse("supplier_vehicle_insurer_partial_update",
                                          kwargs={"pk": self.vehicle_insurer.id})
        self.retrieve_url = reverse("supplier_vehicle_insurer_retrieve", kwargs={"pk": self.vehicle_insurer.id})

    def test_create_vehicle_insurer_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurer_with_valid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = "Mr.X"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = generate_random_string(99)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = generate_random_string(100)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurer_with_invalid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["name"] = generate_random_string(101)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_insurer_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurer_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_insurer_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurer_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_insurer_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_insurer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurer_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_insurer_data.copy()
        data["deleted_on"] = "2018-06-22"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.vehicle_insurer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_insurer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_insurer_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.vehicle_insurer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_insurer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_insurer_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vehicle_insurer_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_vehicle_insurer_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_vehicle_insurer_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.vehicle_insurer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_vehicle_insurer_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_vehicle_insurer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_vehicle_insurer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_vehicle_insurer_retrieve",
                                   kwargs={"pk": self.vehicle_insurer.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VehicleInsuranceTest(SupplierSetup):
    """
        Test cases for Vehicle
    """

    def setUp(self):
        super().setUp()
        self.vehicle_insurance_data = {
            "insurance_number": "adsbhjhasdb",
            "issued_on": "2018-06-23",
            "expired_by": "2018-06-23",
            "deleted": False,
            "deleted_on": None,
            "vehicle": self.vehicle.id,
            "insurer": self.vehicle_insurer.id
        }
        self.minimum_valid_data = {
            "vehicle": self.vehicle.id,"expired_by": "2018-06-23",
        }
        self.create_url = reverse("supplier_vehicle_insurance_create")
        self.update_url = reverse("supplier_vehicle_insurance_update", kwargs={"pk": self.vehicle_insurance.id})
        self.partial_update_url = reverse("supplier_vehicle_insurance_partial_update",
                                          kwargs={"pk": self.vehicle_insurance.id})
        self.retrieve_url = reverse("supplier_vehicle_insurance_retrieve", kwargs={"pk": self.vehicle_insurance.id})

    def test_create_vehicle_insurance_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurance_with_valid_insurance_number(self):
        data = self.minimum_valid_data.copy()

        data["insurance_number"] = "INs1234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_number"] = generate_random_string(24)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_number"] = generate_random_string(25)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_number"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurance_with_invalid_insurance_number(self):
        data = self.minimum_valid_data.copy()

        data["insurance_number"] = generate_random_string(26)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_insurance_with_valid_issued_on(self):
        data = self.minimum_valid_data.copy()

        data["issued_on"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["issued_on"] = "2018-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["issued_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurance_with_invalid_issued_on(self):
        data = self.minimum_valid_data.copy()

        data["issued_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_on"] = "09-12-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_insurance_with_valid_expired_by(self):
        data = self.minimum_valid_data.copy()

        data["expired_by"] = "12-Dec-2022"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["expired_by"] = "2024-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



    def test_create_vehicle_insurance_with_invalid_expired_by(self):
        data = self.minimum_valid_data.copy()

        data["expired_by"] = "09/12/2023"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expired_by"] = "09-12-2024"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expired_by"] = "09-12-24"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expired_by"] = "22-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expired_by"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_insurance_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurance_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_insurance_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurance_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        data["vehicle_number"] = "mh12ncx2202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_insurance_with_valid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = self.vehicle.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurance_with_invalid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = "invalid12"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 123678356
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 1.233
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_insurance_with_valid_insurer(self):
        data = self.minimum_valid_data.copy()

        data["insurer"] = self.vehicle_insurer.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurance_with_invalid_insurer(self):
        data = self.minimum_valid_data.copy()

        data["insurer"] = "invalid12"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurer"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurer"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurer"] = 123678356
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurer"] = 1.233
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurer"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Adding expired_by field to minimum valid data
    def test_create_vehicle_insurance_with_expired_by(self):
        self.minimum_valid_data["expired_by"] = "2018-06-22"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding insurer field to minimum valid data

    def test_create_vehicle_insurance_with_vehicle_insurer(self):
        self.minimum_valid_data["insurer"] = self.vehicle_insurer.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurance_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_insurance_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_insurance_data.copy()
        data["issued_on"] = "2018-06-22T17:59:01.048782"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.vehicle_insurance_data.copy()
        data["vehicle"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = "InvalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = self.vehicle.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.vehicle_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_insurance_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.vehicle_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_insurance_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vehicle_insurance_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_vehicle_insurance_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_vehicle_insurance_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.vehicle_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_vehicle_insurance_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_vehicle_insurance(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_vehicle_insurance(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_vehicle_insurance_retrieve",
                                   kwargs={"pk": self.vehicle_insurance.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VehiclePUCTest(SupplierSetup):
    """
        Test cases for Vehicle PUC
    """

    def setUp(self):
        super().setUp()
        self.vehicle_puc_data = {
            "issued_date": "2018-06-23",
            "expiry_date": "2018-06-23",
            "readings": "23",
            "created_on": "2018-06-23T14:31:46.134127",
            "updated_on": "2018-06-23T14:31:46.134147",
            "deleted": False,
            "deleted_on": None,
            "serial_number": "newNumber",
            "vehicle": self.vehicle.id
        }
        self.minimum_valid_data = {
            "vehicle": self.vehicle.id, "expiry_date": "2018-06-23"
        }
        self.create_url = reverse("supplier_vehicle_puc_create")
        self.update_url = reverse("supplier_vehicle_puc_update", kwargs={"pk": self.vehicle_puc.id})
        self.partial_update_url = reverse("supplier_vehicle_puc_partial_update",
                                          kwargs={"pk": self.vehicle_puc.id})
        self.retrieve_url = reverse("supplier_vehicle_puc_retrieve", kwargs={"pk": self.vehicle_puc.id})

    def test_create_vehicle_puc_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_puc_with_valid_serial_number(self):
        data = self.minimum_valid_data.copy()

        data["serial_number"] = "valid1234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["serial_number"] = generate_random_string(29)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["serial_number"] = generate_random_string(30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["serial_number"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_puc_with_invalid_serial_number(self):
        data = self.minimum_valid_data.copy()

        data["serial_number"] = generate_random_string(31)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_puc_with_valid_readings(self):
        data = self.minimum_valid_data.copy()

        data["readings"] = "valid1234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["readings"] = generate_random_string(249)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["readings"] = generate_random_string(250)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["readings"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_puc_with_invalid_readings(self):
        data = self.minimum_valid_data.copy()

        data["readings"] = generate_random_string(251)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_puc_with_valid_issued_date(self):
        data = self.minimum_valid_data.copy()

        data["issued_date"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["issued_date"] = "2018-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["issued_date"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_puc_with_invalid_issued_date(self):
        data = self.minimum_valid_data.copy()

        data["issued_date"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_date"] = "18/12/09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_date"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_puc_with_valid_expiry_date(self):
        data = self.minimum_valid_data.copy()

        data["expiry_date"] = "12-Dec-2024"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["expiry_date"] = "2022-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_puc_with_invalid_expiry_date(self):
        data = self.minimum_valid_data.copy()

        data["expiry_date"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expiry_date"] = "18/12/09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expiry_date"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_puc_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_puc_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_puc_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_puc_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        data["vehicle_number"] = "mh12ncx2202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_puc_with_valid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = self.vehicle.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_puc_with_invalid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = "invalid12"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 123678356
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 1.233
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Adding expiry_date field to minimum valid data
    def test_create_vehicle_puc_with_expired_date(self):
        self.minimum_valid_data["expiry_date"] = "2018-06-22"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_puc_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_puc_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_puc_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_puc_data.copy()
        data["issued_date"] = "2018-06-22T17:59:01.048782"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.vehicle_puc_data.copy()
        data["vehicle"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = "InvalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = self.vehicle.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.vehicle_puc_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_puc_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_puc_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.vehicle_puc_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_puc_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_puc_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vehicle_poc_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_vehicle_puc_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_vehicle_puc_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.vehicle_puc_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_vehicle_puc_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_vehicle_puc(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_vehicle_puc(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_vehicle_puc_retrieve",
                                   kwargs={"pk": self.vehicle_puc.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VehicleFitnessTest(SupplierSetup):
    """
        Test cases for Vehicle Fitness
    """

    def setUp(self):
        super().setUp()
        self.vehicle_fitness_data = {
            "issued_date": "2018-06-23",
            "expiry_date": "2018-06-23",
            "deleted": False,
            "deleted_on": None,
            "serial_number": "newNumber",
            "vehicle": self.vehicle.id
        }
        self.minimum_valid_data = {
            "vehicle": self.vehicle.id,"expiry_date": "2018-06-23"
        }
        self.create_url = reverse("supplier_vehicle_fitness_create")
        self.update_url = reverse("supplier_vehicle_fitness_update", kwargs={"pk": self.vehicle_fitness.id})
        self.partial_update_url = reverse("supplier_vehicle_fitness_partial_update",
                                          kwargs={"pk": self.vehicle_fitness.id})
        self.retrieve_url = reverse("supplier_vehicle_fitness_retrieve", kwargs={"pk": self.vehicle_fitness.id})

    def test_create_vehicle_fitness_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_fitness_with_valid_serial_number(self):
        data = self.minimum_valid_data.copy()

        data["serial_number"] = "valid1234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["serial_number"] = generate_random_string(29)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["serial_number"] = generate_random_string(30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["serial_number"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_fitness_with_invalid_serial_number(self):
        data = self.minimum_valid_data.copy()

        data["serial_number"] = generate_random_string(31)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_fitness_with_valid_issued_date(self):
        data = self.minimum_valid_data.copy()

        data["issued_date"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["issued_date"] = "2018-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["issued_date"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_fitness_with_invalid_issued_date(self):
        data = self.minimum_valid_data.copy()

        data["issued_date"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_date"] = "18/12/09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_date"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_fitness_with_valid_expiry_date(self):
        data = self.minimum_valid_data.copy()

        data["expiry_date"] = "12-Dec-2024"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["expiry_date"] = "2022-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_vehicle_fitness_with_invalid_expiry_date(self):
        data = self.minimum_valid_data.copy()

        data["expiry_date"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expiry_date"] = "18/12/09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expiry_date"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_fitness_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_fitness_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_fitness_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_fitness_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        data["vehicle_number"] = "mh12ncx2202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_fitness_with_valid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = self.vehicle.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_fitness_with_invalid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = "invalid12"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 123678356
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 1.233
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Adding expiry_date field to minimum valid data
    def test_create_vehicle_fitness_with_expired_date(self):
        self.minimum_valid_data["expiry_date"] = "2018-06-22"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_fitness_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_fitness_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_fitness_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_fitness_data.copy()
        data["issued_date"] = "2018-06-22T17:59:01.048782"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.vehicle_fitness_data.copy()
        data["vehicle"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = "InvalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = self.vehicle.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.vehicle_fitness_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_fitness_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_fitness_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.vehicle_fitness_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_fitness_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_fitness_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vehicle_fitness_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_vehicle_fitness_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_vehicle_fitness_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.vehicle_fitness_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_vehicle_fitness_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_vehicle_fitness(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_vehicle_fitness(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_vehicle_fitness_retrieve",
                                   kwargs={"pk": self.vehicle_fitness.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VehiclePermitTest(SupplierSetup):
    """
        Test cases for Vehicle Permit
    """

    def setUp(self):
        super().setUp()
        self.vehicle_permit_data = {
            "permit_type": "supreme",
            "issued_date": "2018-06-23",
            "expiry_date": "2018-06-23",
            "deleted": False,
            "deleted_on": None,
            "permit_number": "newNumber",
            "vehicle": self.vehicle.id
        }
        self.minimum_valid_data = {"expiry_date": "2018-06-23"}
        self.create_url = reverse("supplier_vehicle_permit_create")
        self.update_url = reverse("supplier_vehicle_permit_update", kwargs={"pk": self.vehicle_permit.id})
        self.partial_update_url = reverse("supplier_vehicle_permit_partial_update",
                                          kwargs={"pk": self.vehicle_permit.id})
        self.retrieve_url = reverse("supplier_vehicle_permit_retrieve", kwargs={"pk": self.vehicle_permit.id})

    def test_create_vehicle_permit_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_permit_with_other_data_format(self):
        pass

    def test_create_vehicle_permit_with_valid_permit_number(self):
        data = self.minimum_valid_data.copy()

        data["permit_number"] = "valid1234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_number"] = generate_random_string(29)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_number"] = generate_random_string(30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_number"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_vehicle_permit_with_invalid_serial_number(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["serial_number"] = generate_random_string(31)
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_permit_with_invalid_permit_number(self):
        data = self.minimum_valid_data.copy()

        data["permit_number"] = generate_random_string(31)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_permit_with_valid_permit_type(self):
        data = self.minimum_valid_data.copy()

        data["permit_type"] = "valid1234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_type"] = generate_random_string(99)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_type"] = generate_random_string(100)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_type"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_permit_with_invalid_permit_type(self):
        data = self.minimum_valid_data.copy()

        data["permit_type"] = generate_random_string(101)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_permit_with_valid_issued_date(self):
        data = self.minimum_valid_data.copy()

        data["issued_date"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["issued_date"] = "2018-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["issued_date"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_permit_with_invalid_issued_date(self):
        data = self.minimum_valid_data.copy()

        data["issued_date"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_date"] = "18/12/09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_date"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_date"] = "12-09-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["issued_date"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_permit_with_valid_expiry_date(self):
        data = self.minimum_valid_data.copy()

        data["expiry_date"] = "12-Dec-2024"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["expiry_date"] = "2022-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_permit_with_invalid_expiry_date(self):
        data = self.minimum_valid_data.copy()

        data["expiry_date"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expiry_date"] = "18/12/09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expiry_date"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_permit_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_permit_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_permit_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_permit_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        data["vehicle_number"] = "mh12ncx2202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_permit_with_valid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = self.vehicle.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_permit_with_invalid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = "invalid12"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 123678356
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 1.233
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Adding expiry_date field to minimum valid data
    def test_create_vehicle_permit_with_expired_date(self):
        self.minimum_valid_data["expiry_date"] = "2018-06-22"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle field to minimum valid data

    def test_create_vehicle_permit_with_vehicle(self):
        self.minimum_valid_data["vehicle"] = self.vehicle.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_permit_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_permit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_permit_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_permit_data.copy()
        data["issued_date"] = "2018-06-22T17:59:01.048782"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.vehicle_permit_data.copy()
        data["vehicle"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = "InvalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = self.vehicle.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.vehicle_permit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_permit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_permit_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.vehicle_permit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_permit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_permit_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vehicle_permit_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_vehicle_permit_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_vehicle_permit_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.vehicle_permit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_vehicle_permit_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_vehicle_permit(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_vehicle_permit(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_vehicle_permit_retrieve",
                                   kwargs={"pk": self.vehicle_permit.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SupplierVehicleTest(SupplierSetup):
    """
        Test cases for Supplier Vehicle
    """

    def setUp(self):
        super().setUp()
        self.supplier_vehicle_data = {
            "ownership": "B",
            "active": True,
            "deleted": False,
            "deleted_on": None,
            "vehicle": self.vehicle.id,
            "supplier": self.supplier.id
        }
        self.minimum_valid_data = {
            "vehicle": self.vehicle.id,
            "supplier": self.supplier.id,
            "ownership": "B"
        }
        self.create_url = reverse("supplier_supplier_vehicle_create")
        self.update_url = reverse("supplier_supplier_vehicle_update", kwargs={"pk": self.supplier_vehicle.id})
        self.partial_update_url = reverse("supplier_supplier_vehicle_partial_update",
                                          kwargs={"pk": self.supplier_vehicle.id})
        self.retrieve_url = reverse("supplier_supplier_vehicle_retrieve", kwargs={"pk": self.supplier_vehicle.id})

    def test_create_supplier_vehicle_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_vehicle_with_other_data_format(self):
        pass

    def test_create_supplier_vehicle_with_valid_ownership(self):
        data = self.minimum_valid_data.copy()

        data["ownership"] = "B"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["ownership"] = "O"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_vehicle_with_invalid_ownership(self):
        data = self.minimum_valid_data.copy()

        data["ownership"] = "invalid123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ownership"] = "o"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_vehicle_with_valid_active(self):
        data = self.minimum_valid_data.copy()

        data["active"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["active"] = False
        data["ownership"] = "O"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_vehicle_with_invalid_active(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        data["ownership"] = "O"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_vehicle_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["ownership"] = "O"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_vehicle_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        data["ownership"] = "O"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_vehicle_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["ownership"] = "O"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_vehicle_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/2018"
        data["ownership"] = "O"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12/09/18"
        data["ownership"] = "B"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_vehicle_with_valid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = self.vehicle.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_vehicle_with_invalid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = "invalid12"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 123678356
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = 1.233
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_vehicle_with_valid_supplier(self):
        data = self.minimum_valid_data.copy()

        data["supplier"] = self.supplier.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_vehicle_with_invalid_supplier(self):
        data = self.minimum_valid_data.copy()

        data["supplier"] = "invalid12"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = 123678356
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = 1.233
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_vehicle_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.supplier_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_supplier_vehicle_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.supplier_vehicle_data.copy()
        data["deleted_on"] = "2018-06-22"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.supplier_vehicle_data.copy()
        data["vehicle"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = "InvalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = self.vehicle.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.supplier_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.supplier_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.supplier_vehicle_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.supplier_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.supplier_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.supplier_vehicle_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_supplier_vehicle_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_supplier_vehicle_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_supplier_vehicle_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.supplier_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_supplier_vehicle_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"deleted": False}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"supplier": self.supplier.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_supplier_vehicle(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_supplier_vehicle(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("supplier_supplier_vehicle_retrieve",
                                   kwargs={"pk": self.supplier_vehicle.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
