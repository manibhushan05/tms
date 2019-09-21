import json

from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import Profile
from driver.models import Driver, DriverAppUser
from owner.models import Owner, Route, Vehicle, FuelCard, FuelCardTransaction
from utils.models import City, Address, Bank, TaxationID, VehicleCategory
from datetime import datetime


class OwnerAppSetup(APITestCase):
    """
        Setup dummy data for File Upload Setup
    """

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.test_user = User.objects.create_user('testUser', 'test@example.com', 'testPassword')
        self.test_user2 = User.objects.create_user('testUser2', 'test2@example.com', 'testPassword2')
        self.test_profile = Profile.objects.create(user=self.test_user, phone="2323232323")
        self.login_data = self.client.post(self.login_url, {"username": "testUser", "password": "testPassword"}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        self.source = mommy.make(City)
        self.destination = mommy.make(City)
        self.address = mommy.make(Address)
        self.account_details = mommy.make(Bank)
        self.driver = mommy.make(Driver)
        self.driver_app_user = mommy.make(DriverAppUser)
        self.vehicle_type = mommy.make(VehicleCategory)
        self.taxation_details = mommy.make(TaxationID)

        self.route = mommy.make(Route)
        self.city = mommy.make(City)
        self.city2 = mommy.make(City)
        self.owner = mommy.make(Owner, name=self.test_user, city=self.city)
        self.owner2 = mommy.make(Owner, name=self.test_user2, city=self.city2)
        self.owner_vehicle = mommy.make(Vehicle)
        self.fuel_card = mommy.make(FuelCard, _fill_optional=['card_number'])
        self.fuel_card_transaction = mommy.make(FuelCardTransaction)


class RouteTest(OwnerAppSetup):
    """
        Test cases for Route
    """

    def setUp(self):
        super().setUp()
        self.route_data = {
            "deleted": False,
            "deleted_on": None,
            "source": self.source.id,
            "destination": self.destination.id
        }
        self.minimum_valid_data = {
            "source": self.source.id,
            "destination": self.destination.id
        }

        self.create_url = reverse("owner_route_create")
        self.update_url = reverse("owner_route_update", kwargs={"pk": self.route.id})
        self.partial_update_url = reverse("owner_route_partial_update", kwargs={"pk": self.route.id})
        self.retrieve_url = reverse("owner_route_retrieve", kwargs={"pk": self.route.id})

    def test_create_route_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted to minimum data
    def test_create_route_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted on to minimum data
    def test_create_route_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_route_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_route_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.route_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.route_data.copy()
        data["source"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["source"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["source"] = self.source.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.route_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.route_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.route_data.copy()
        data["created_by"] = self.test_user.id
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_route_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_route_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_route_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"source": self.source.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_route(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_route(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("owner_route_retrieve",
                                   kwargs={"pk": self.route.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OwnerTest(OwnerAppSetup):
    """
        Test cases for Owner
    """

    def setUp(self):
        super().setUp()
        self.owner_data = {
            "owner_address": "Sand village",
            "pin": "234354",
            "route_temp": "test",
            "pan": "CBPPK6928P",
            "declaration": "http://04d5fdd4-74db-41e8-bc9a-203ffd9cc3fb.jpg",
            "declaration_validity": "2016-10-27",

            "deleted": False,
            "deleted_on": None,
            "name": "testOwner",
            "city": self.source.id,
            "account_details": self.account_details.id,
            "address": self.address.id,
            "taxation_details": self.taxation_details.id,
            "route": [self.route.id],
            "phone": "3434343434"
        }
        self.minimum_valid_data = {
            "name": "testOwner",
            "city": self.source.id,
            "phone": "3434343434"
        }

        self.create_url = reverse("owner_owner_create")
        self.update_url = reverse("owner_owner_update", kwargs={"pk": self.owner.id})
        self.partial_update_url = reverse("owner_owner_partial_update", kwargs={"pk": self.owner.id})
        self.retrieve_url = reverse("owner_owner_retrieve", kwargs={"pk": self.owner.id})
        self.filter_url = reverse("owner_owner_list")

    def test_create_owner_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_with_invalid_data_format(self):
        pass

    def test_create_owner_with_valid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = "some_valid_name"
        data['phone'] = '8978937491'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = "aahouser786"
        data['phone'] = '8978937492'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = "s" * 200
        data['phone'] = '8978937494'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = None
        data['phone'] = '8978937495'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_with_invalid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["name"] = "s"
        data['phone'] = '8978937497'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["name"] = "           "
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["name"] = "s" * 201
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_valid_owner_address(self):
        data = self.minimum_valid_data.copy()

        data["owner_address"] = "abc"
        data['phone'] = '8978935645'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["owner_address"] = "a" * 300
        data['phone'] = '8978935643'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["owner_address"] = None
        data['phone'] = '8978935644'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_with_invalid_owner_address(self):
        data = self.minimum_valid_data.copy()

        data["owner_address"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner_address"] = "       "
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner_address"] = "ab"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner_address"] = "a" * 301
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_valid_pan(self):
        data = self.minimum_valid_data.copy()

        data["pan"] = "CBPPK6928P"
        data['phone'] = '8978937401'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pan"] = "cbPpk6928P"
        data['phone'] = '8978937786'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pan"] = " CBPPK6922P"
        data['phone'] = '8978937787'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pan"] = "CBPPK6923P "
        data['phone'] = '8978937788'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pan"] = None
        data['phone'] = '8978937789'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_with_invalid_pan(self):
        data = self.minimum_valid_data.copy()

        data["pan"] = "CBPPK69289"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = "8BPPK6928P"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = "C8PPK6928P"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = "CB9PK6928P"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = "CBPZK6928P"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = "CB9Z86928P"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = "CBPPKA928P"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = "CBPPK6Y28P"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = "CBPPK6Y28PP"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = "KCBPPK6Y28P"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_valid_route(self):
        data = self.minimum_valid_data.copy()

        data["route_temp"] = "abc"
        data['phone'] = '8978937401'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["route_temp"] = "its_correct_route_keep_going"
        data['phone'] = '8978937402'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["route_temp"] = "i" * 300
        data['phone'] = '8978937403'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_with_invalid_route(self):
        data = self.minimum_valid_data.copy()

        data["route_temp"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["route_temp"] = "a"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["route_temp"] = "ab"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["route_temp"] = "a" * 301
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_valid_contact_person_name(self):
        data = self.minimum_valid_data.copy()

        data["contact_person_name"] = "some_name"
        data["phone"] = "8978937403"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_person_name"] = "a" * 69
        data["phone"] = "8978937401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_person_name"] = "a" * 70
        data["phone"] = "8978937407"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_person_name"] = None
        data["phone"] = "8978937408"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_with_invalid_contact_person_name(self):
        data = self.minimum_valid_data.copy()

        data["contact_person_name"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_name"] = "a" * 71
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_name"] = "         "
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_valid_contact_person_phone(self):
        data = self.minimum_valid_data.copy()

        data["phone"] = 9939717009
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = "8978937498"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = u"8978937497"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_person_phone"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = " 9939717008"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = "9939717008 "
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_invalid_contact_person_phone(self):
        data = self.minimum_valid_data.copy()

        data["contact_person_phone"] = "993971700p"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = "99397170088"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = "939717008"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = "transiq tec"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_address(self):
        data = self.minimum_valid_data.copy()

        data["owner_address"] = "Some address"
        data["phone"] = "7867897898"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["owner_address"] = "S" * 300
        data["phone"] = "7867897891"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_with_invalid_address(self):
        data = self.minimum_valid_data.copy()

        data["owner_address"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner_address"] = "a"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner_address"] = "ab"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner_address"] = "a" * 301
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_with_valid_pin(self):
        data = self.minimum_valid_data.copy()
        data["pin"] = "123456"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_driver_with_invalid_pin(self):
        data = self.minimum_valid_data.copy()

        data["pin"] = "12345"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = "1234567"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = "pin"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = "-123456"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_valid_email(self):
        data = self.minimum_valid_data.copy()
        data["email"] = "xyz@example.com"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_invalid_email(self):
        data = self.minimum_valid_data.copy()

        data["email"] = "invalidemail"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "{}@gmail.com".format('a' * 91)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "invalid@email"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "invalid.email"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_valid_phone(self):
        data = self.minimum_valid_data.copy()
        data["phone"] = "1234098700"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = u"8978937498"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = 8978937497
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = " 9939717008"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = "9939717009 "
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_with_invalid__phone(self):
        data = self.minimum_valid_data.copy()

        data["phone"] = "993971700p"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "99397170088"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = " 939717008"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "transiq tec"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["declaration_validity"] = "2016-07-14T10:03:59.517090"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.minimum_valid_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.minimum_valid_data.copy()
        data["pin"] = "More than 6 letters"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = "FIVE"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.minimum_valid_data.copy()
        data["city"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = self.source.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_invalid_city(self):
        data = self.minimum_valid_data.copy()

        data["city"] = -10  # negative id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = 0  # zero id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = 12345675890  # out of range value id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = 123.456  # floating value id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = "aaho"  # string  id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = None  # None value as id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = ""  # empty string as id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = "@3&!#1!"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = [self.source.id, self.source.id + 1, self.source.id + 2]
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.minimum_valid_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.minimum_valid_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.owner_data.copy()
        data["created_by"] = self.test_user.id
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_owner_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.minimum_valid_data["name"] = self.test_user.id
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_owner_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.owner_data["name"] = self.test_user.id
        response = self.client.put(self.update_url, self.owner_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_owner_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"source": self.source.id, 'pin': '400072'}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("owner_owner_retrieve",
                                   kwargs={"pk": self.owner.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_owner_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.owner.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.owner.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class OwnerVehicleTest(OwnerAppSetup):
    """
        Test cases for Owner Vehicle
    """

    def setUp(self):
        super().setUp()
        self.owner_vehicle_data = {

            "vehicle_number": "TE 01 SLA 2018",
            "rc_number": "test",
            "permit": "test",
            "permit_validity": "2018-06-27",
            "permit_type": "2018-06-27",
            "vehicle_capacity": 2,
            "body_type": "open",
            "vehicle_model": "Mercedes",
            "chassis_number": "12123sad",
            "engine_number": "23asdas",
            "insurer": "test",
            "insurance_number": None,
            "insurance_validity": None,
            "registration_year": None,
            "registration_validity": "2018-06-27",
            "fitness_certificate_number": None,
            "fitness_certificate_issued_on": None,
            "fitness_certificate_validity_date": "2018-06-27",
            "puc_certificate_number": None,
            "puc_certificate_issued_on": "2018-06-27",
            "puc_certificate_validity_date": "2018-06-27",
            "status": "unloaded",
            "gps_enabled": True,
            "supplier_name": "test",
            "supplier_phone": "1232123212",
            "owner_name": "test",
            "owner_phone": "123213123",
            "owner": self.owner.id,
            "driver": self.driver.id,
            "driver_app_user": self.driver_app_user.id,
            "vehicle_type": self.vehicle_type.id,
            "deleted": False,
            "deleted_on": None,
            "route": [self.route.id]
        }
        self.minimum_valid_data = {
            "owner": self.owner.id,
            "vehicle_number": "UP 23 TN 1987",
            "body_type": "open",
            "gps_enabled": True

        }

        self.create_url = reverse("owner_owner_vehicle_create")
        self.update_url = reverse("owner_owner_vehicle_update", kwargs={"pk": self.owner_vehicle.id})
        self.partial_update_url = reverse("owner_owner_vehicle_partial_update",
                                          kwargs={"pk": self.owner_vehicle.id})
        self.retrieve_url = reverse("owner_owner_vehicle_retrieve", kwargs={"pk": self.owner_vehicle.id})
        self.filter_url = reverse("owner_owner_vehicle_list")

    def test_create_owner_vehicle_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_different_data_format(self):
        pass

    def test_create_owner_vehicle_with_valid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = self.vehicle_type.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = -12
        data["vehicle_number"] = "AS 34 RKJ 2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] = 0
        data["vehicle_number"] = "AS 34 RKJ 2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] = datetime.now()
        data["vehicle_number"] = "AS 34 RKJ 2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] = str(datetime.now())
        data["vehicle_number"] = "AS 34 RKJ 2003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_type"] =123.34
        data["vehicle_number"] = "AS 34 RKJ 2004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



    def test_create_owner_vehicle_with_valid_owner_data(self):
        data = self.minimum_valid_data.copy()
        data["owner"] = self.owner2.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_owner_data(self):
        data = self.minimum_valid_data.copy()

        data["owner"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner"] = 123454544
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["owner"] = [1, 2, 3]
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = 'mh03bk1523'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh 03 bk 1524'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh-03-bk-1525'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'MH03BK1526'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh.03.bk.1527'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh03 bk1529'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh03 bk1510'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh 03bk1511'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh03bk 1512'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'MH03BK1513'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh03tbk1514'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh03k1515'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh031516'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh.03-bk 1517'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = 'mh3bk1518'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = 'mhe03bk1523'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = 'm03bk1523'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = 'mh035bk1523'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = 'mhbk1523'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = 'mh03bkty1523'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # data["vehicle_number"] = 'mh03bk15236'
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = 'mh03bk152'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = 'mh03bk15'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = 'mh03bk1'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = 'mh03bk'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # data["vehicle_number"] = 'mh--03--bk1523'
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = ''
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = '7867986789'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = '03mhbk1523'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_rc_number(self):
        data = self.minimum_valid_data.copy()

        data["rc_number"] = "test"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rc_number"] = "a" * 19
        data["vehicle_number"] = "UP 01 AKB 1999"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rc_number"] = "ta12@_#"
        data["vehicle_number"] = "UP 01 AKB 1998"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rc_number"] = "t" * 20
        data["vehicle_number"] = "UP 01 AKB 1997"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_rc_number(self):
        data = self.minimum_valid_data.copy()

        data["rc_number"] = "e"
        data["vehicle_number"] = "UP 01 AKB 1996"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rc_number"] = "ab"
        data["vehicle_number"] = "UP 01 AKB 1995"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rc_number"] = "a" * 21
        data["vehicle_number"] = "UP 01 AKB 1994"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_test_with_valid_permit_number(self):
        data = self.minimum_valid_data.copy()

        data["permit"] = "test"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit"] = "a" * 24
        data["vehicle_number"] = "UP 01 AKB 1999"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit"] = "ta12@_#"
        data["vehicle_number"] = "UP 01 AKB 1998"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit"] = "t" * 25
        data["vehicle_number"] = "UP 01 AKB 1997"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_permit_number(self):
        data = self.minimum_valid_data.copy()

        data["permit"] = "e"
        data["vehicle_number"] = "UP 01 AKB 1996"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["permit"] = "ab"
        data["vehicle_number"] = "UP 01 AKB 1995"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["permit"] = "a" * 26
        data["vehicle_number"] = "UP 01 AKB 1994"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_test_with_valid_vehicle_model(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_model"] = "test"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_model"] = "a" * 29
        data["vehicle_number"] = "UP 01 AKB 1999"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_model"] = "ta12@_#"
        data["vehicle_number"] = "UP 01 AKB 1998"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_model"] = "t" * 30
        data["vehicle_number"] = "UP 01 AKB 1997"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_vehicle_model(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_model"] = "e"
        data["vehicle_number"] = "UP 01 AKB 1996"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_model"] = "ab"
        data["vehicle_number"] = "UP 01 AKB 1995"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_model"] = "a" * 31
        data["vehicle_number"] = "UP 01 AKB 1994"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_test_with_valid_insurer(self):
        data = self.minimum_valid_data.copy()

        data["insurer"] = "test"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurer"] = "a" * 99
        data["vehicle_number"] = "UP 01 AKB 1999"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurer"] = "ta12@_#"
        data["vehicle_number"] = "UP 01 AKB 1998"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurer"] = "t" * 100
        data["vehicle_number"] = "UP 01 AKB 1997"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_insurer(self):
        data = self.minimum_valid_data.copy()

        data["insurer"] = "e"
        data["vehicle_number"] = "UP 01 AKB 1996"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurer"] = "ab"
        data["vehicle_number"] = "UP 01 AKB 1995"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurer"] = "a" * 101
        data["vehicle_number"] = "UP 01 AKB 1994"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_body_type(self):
        data = self.minimum_valid_data.copy()

        data["body_type"] = "open"
        data["vehicle_number"] = "TM 01 CHH 1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["body_type"] = "closed"
        data["vehicle_number"] = "TM 01 CHH 1203"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["body_type"] = "semi"
        data["vehicle_number"] = "TM 01 CHH 1205"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["body_type"] = "half"
        data["vehicle_number"] = "TM 01 CHH 1207"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["body_type"] = "containerized"
        data["vehicle_number"] = "TM 01 CHH 1209"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_body_type(self):
        data = self.minimum_valid_data.copy()

        data["body_type"] = "OpEn"
        data["vehicle_number"] = "TM 01 CHH 1301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["body_type"] = "invalid_type"
        data["vehicle_number"] = "TM 01 CHH 1303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["body_type"] = "Semi"
        data["vehicle_number"] = "TM 01 CHH 1305"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["body_type"] = 123
        data["vehicle_number"] = "TM 01 CHH 1307"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["body_type"] = None
        data["vehicle_number"] = "TM 01 CHH 1309"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["body_type"] = ""
        data["vehicle_number"] = "TM 01 CHH 1311"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_gps_availability(self):
        data = self.minimum_valid_data.copy()

        data["gps_enabled"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gps_enabled"] = False
        data["vehicle_number"] = "BH 34 PTN 2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gps_enabled"] = "True"
        data["vehicle_number"] = "BH 34 PTN 2020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gps_enabled"] = "False"
        data["vehicle_number"] = "BH 34 PTN 2022"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gps_enabled"] = "0"
        data["vehicle_number"] = "BH 34 PTN 2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gps_enabled"] = "1"
        data["vehicle_number"] = "BH 34 PTN 2023"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_valid_vehicle_capacity(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_capacity"] = 2147483647
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_capacity"] = 2147483646
        data["vehicle_number"] = "AP 34 HYD 2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_capacity"] = -2147483648
        data["vehicle_number"] = "AP 34 HYD 2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_capacity"] = -2147483647
        data["vehicle_number"] = "AP 34 HYD 2003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_capacity"] = 0
        data["vehicle_number"] = "AP 34 HYD 2004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_capacity"] = "2147483646"
        data["vehicle_number"] = "AP 34 HYD 2006"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_vehicle_capacity(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_capacity"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_capacity"] = -2147483649
        data["vehicle_number"] = "AP 34 HYD 2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_capacity"] = "invalid"
        data["vehicle_number"] = "AP 34 HYD 2003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_capacity"] = datetime.now()
        data["vehicle_number"] = "AP 34 HYD 2004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_registration_year(self):
        data = self.minimum_valid_data.copy()

        data["registration_year"] = "2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["registration_year"] = "1900"
        data["vehicle_number"] = 'JH 14 ISH 3002'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["registration_year"] = "2018"
        data["vehicle_number"] = 'JH 14 ISH 3003'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_registration_year(self):
        data = self.minimum_valid_data.copy()

        data["registration_year"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["registration_year"] = "-2016"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_permit_type(self):
        data = self.minimum_valid_data.copy()

        data["permit_type"] = "valid_permit_type"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_type"] = str(datetime.now())
        data["vehicle_number"] = "LH 12 AR 1199"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_type"] = datetime.now()
        data["vehicle_number"] = "LH 12 AR 1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_type"] = "1b@#"
        data["vehicle_number"] = "LH 12 AR 1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_type"] = "v" * 69
        data["vehicle_number"] = "LH 12 AR 1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_type"] = "a" * 70
        data["vehicle_number"] = "LH 12 AR 1203"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_permit_type(self):
        data = self.minimum_valid_data.copy()

        data["permit_type"] = "v"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["permit_type"] = "av"
        data["vehicle_number"] = "LH 12 AR 1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["permit_type"] = "a" * 71
        data["vehicle_number"] = "LH 12 AR 1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_with_valid_permit_validity(self):
        data = self.minimum_valid_data.copy()

        data["permit_validity"] = "12-Dec-2020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["permit_validity"] = "2025-12-12"
        data["vehicle_number"] = "SR 21 dec 2300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_with_invalid_permit_validity(self):
        data = self.minimum_valid_data.copy()

        data["permit_validity"] = "2018/12/09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["permit_validity"] = "09-12-18"
        data["vehicle_number"] = "SR 20 dec 2300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["permit_validity"] = "18-12-09"
        data["vehicle_number"] = "SR 20 dec 2301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["permit_validity"] = "09-12-18"
        data["vehicle_number"] = "SR 20 dec 2302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["permit_validity"] = "invalid_date"
        data["vehicle_number"] = "SR 20 dec 2303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_test_with_valid_engine_number(self):
        data = self.minimum_valid_data.copy()

        data["engine_number"] = "test"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["engine_number"] = "a" * 254
        data["vehicle_number"] = "UP 01 AKB 1999"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["engine_number"] = "ta12@_#"
        data["vehicle_number"] = "UP 01 AKB 1998"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["engine_number"] = "t" * 255
        data["vehicle_number"] = "UP 01 AKB 1997"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_engine_number(self):
        data = self.minimum_valid_data.copy()

        data["engine_number"] = "e"
        data["vehicle_number"] = "UP 01 AKB 1996"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["engine_number"] = "ab"
        data["vehicle_number"] = "UP 01 AKB 1995"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["engine_number"] = "a" * 256
        data["vehicle_number"] = "UP 01 AKB 1994"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_test_with_valid_chassis_number(self):
        data = self.minimum_valid_data.copy()

        data["chassis_number"] = "test"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["chassis_number"] = "a" * 254
        data["vehicle_number"] = "UP 01 AKB 1999"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["chassis_number"] = "ta12@_#"
        data["vehicle_number"] = "UP 01 AKB 1998"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["chassis_number"] = "t" * 255
        data["vehicle_number"] = "UP 01 AKB 1997"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_chassis_number(self):
        data = self.minimum_valid_data.copy()

        data["chassis_number"] = "e"
        data["vehicle_number"] = "UP 01 AKB 1996"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["chassis_number"] = "ab"
        data["vehicle_number"] = "UP 01 AKB 1995"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["chassis_number"] = "a" * 256
        data["vehicle_number"] = "UP 01 AKB 1994"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_test_with_valid_insurance_number(self):
        data = self.minimum_valid_data.copy()

        data["insurance_number"] = "test"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_number"] = "a" * 29
        data["vehicle_number"] = "UP 01 AKB 1999"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_number"] = "ta12@_#"
        data["vehicle_number"] = "UP 01 AKB 1998"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_number"] = "t" * 30
        data["vehicle_number"] = "UP 01 AKB 1997"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_insurance_number(self):
        data = self.minimum_valid_data.copy()

        data["insurance_number"] = "e"
        data["vehicle_number"] = "UP 01 AKB 1996"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurance_number"] = "ab"
        data["vehicle_number"] = "UP 01 AKB 1995"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurance_number"] = "a" * 31
        data["vehicle_number"] = "UP 01 AKB 1994"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_insurance_validity(self):
        data = self.minimum_valid_data.copy()

        data["insurance_validity"] = "12-Dec-2022"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_validity"] = "2024-12-01"
        data["vehicle_number"] = "GO 11 CPP 2004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_insurance_validity(self):
        data = self.minimum_valid_data.copy()

        # data["insurance_validity"] = "12-Dec-2000"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #
        # data["insurance_validity"] = "2015-12-01"
        # data["vehicle_number"] = "GO 11 CPP 2004"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurance_validity"] = "invalid_validity"
        data["vehicle_number"] = "GO 11 CPP 2005"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_test_with_valid_fitness_certificate_number(self):
        data = self.minimum_valid_data.copy()

        data["fitness_certificate_number"] = "test"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["fitness_certificate_number"] = "a" * 254
        data["vehicle_number"] = "UP 02 AKB 1999"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["fitness_certificate_number"] = "ta12@_#"
        data["vehicle_number"] = "UP 02 AKB 1998"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["fitness_certificate_number"] = "t" * 255
        data["vehicle_number"] = "UP 02 AKB 1997"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_test_with_invalid_fitness_certificate_number(self):
        data = self.minimum_valid_data.copy()

        data["fitness_certificate_number"] = "e"
        data["vehicle_number"] = "UP 01 AKB 1996"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fitness_certificate_number"] = "ab"
        data["vehicle_number"] = "UP 01 AKB 1995"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fitness_certificate_number"] = "a" * 256
        data["vehicle_number"] = "UP 01 AKB 1994"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_fitness_certificate_issued_on(self):
        data = self.minimum_valid_data.copy()

        data["fitness_certificate_issued_on"] = "12-Dec-2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["fitness_certificate_issued_on"] = "2018-12-09"
        data["vehicle_number"] = "QW 03 QR 4300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # data["fitness_certificate_issued_on"] = datetime.now()
        # data["vehicle_number"] = "QW 03 QR 4301"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_fitness_certificate_issued_on(self):
        data = self.minimum_valid_data.copy()

        # data["fitness_certificate_issued_on"] = "12-Dec-2025"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fitness_certificate_issued_on"] = "2018/12/09"
        data["vehicle_number"] = "QW 03 QR 4300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fitness_certificate_issued_on"] = "18-12-09"
        data["vehicle_number"] = "QW 03 QR 4301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fitness_certificate_issued_on"] = "invalid_date"
        data["vehicle_number"] = "QW 03 QR 4303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_fitness_certificate_validity(self):
        data = self.minimum_valid_data.copy()

        data["fitness_certificate_validity_date"] = "12-Dec-2022"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["fitness_certificate_validity_date"] = "2025-12-09"
        data["vehicle_number"] = "QW 03 QR 4300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # data["fitness_certificate_issued_on"] = datetime.now()
        # data["vehicle_number"] = "QW 03 QR 4301"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_fitness_certificate_validity(self):
        data = self.minimum_valid_data.copy()

        # data["fitness_certificate_issued_on"] = "12-Dec-2016"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fitness_certificate_validity_date"] = "2018/12/09"
        data["vehicle_number"] = "QW 03 QR 4300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fitness_certificate_validity_date"] = "18-12-09"
        data["vehicle_number"] = "QW 03 QR 4301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fitness_certificate_validity_date"] = "invalid_date"
        data["vehicle_number"] = "QW 03 QR 4303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_test_with_valid_puc_certificate_number(self):
        data = self.minimum_valid_data.copy()

        data["puc_certificate_number"] = "test"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["puc_certificate_number"] = "a" * 254
        data["vehicle_number"] = "UP 02 AKB 1999"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["puc_certificate_number"] = "ta12@_#"
        data["vehicle_number"] = "UP 02 AKB 1998"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["puc_certificate_number"] = "t" * 255
        data["vehicle_number"] = "UP 02 AKB 1997"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_test_with_invalid_puc_certificate_number(self):
        data = self.minimum_valid_data.copy()

        data["puc_certificate_number"] = "e"
        data["vehicle_number"] = "UP 01 AKB 1996"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["puc_certificate_number"] = "ab"
        data["vehicle_number"] = "UP 01 AKB 1995"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["puc_certificate_number"] = "a" * 256
        data["vehicle_number"] = "UP 01 AKB 1994"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_puc_certificate_issued_on(self):
        data = self.minimum_valid_data.copy()

        data["puc_certificate_issued_on"] = "12-Dec-2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["puc_certificate_issued_on"] = "2018-12-09"
        data["vehicle_number"] = "QW 03 QR 4300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # data["puc_certificate_issued_on"] = datetime.now()
        # data["vehicle_number"] = "QW 03 QR 4301"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_puc_certificate_issued_on(self):
        data = self.minimum_valid_data.copy()

        # data["puc_certificate_issued_on"] = "12-Dec-2025"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["puc_certificate_issued_on"] = "2018/12/09"
        data["vehicle_number"] = "QW 03 QR 4300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["puc_certificate_issued_on"] = "18-12-09"
        data["vehicle_number"] = "QW 03 QR 4301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["puc_certificate_issued_on"] = "invalid_date"
        data["vehicle_number"] = "QW 03 QR 4303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_fitness_puc_certificate_validity_date(self):
        data = self.minimum_valid_data.copy()

        data["puc_certificate_validity_date"] = "12-Dec-2022"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["puc_certificate_validity_date"] = "2025-12-09"
        data["vehicle_number"] = "QW 03 QR 4300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # data["puc_certificate_validity_date"] = datetime.now()
        # data["vehicle_number"] = "QW 03 QR 4301"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_fitness_puc_certificate_validity_date(self):
        data = self.minimum_valid_data.copy()

        # data["puc_certificate_validity_date"] = "12-Dec-2016"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["puc_certificate_validity_date"] = "2025/12/09"
        data["vehicle_number"] = "QW 03 QR 4300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["puc_certificate_validity_date"] = "20-12-09"
        data["vehicle_number"] = "QW 03 QR 4301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["puc_certificate_validity_date"] = "invalid_date"
        data["vehicle_number"] = "QW 03 QR 4303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_created_by(self):
        data = self.minimum_valid_data.copy()

        data["created_by"] = "testUser"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["created_by"] = "testUser2"
        data["vehicle_number"] = "TR 01 UK 2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_created_by(self):
        data = self.minimum_valid_data.copy()

        data["created_by"] = "@45z#$%^&"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["created_by"] = "a" * 151
        data["vehicle_number"] = "TR 01 UK 2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["created_by"] = None
        data["vehicle_number"] = "TR 01 UK 2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_with_valid_changed_by(self):
        data = self.minimum_valid_data.copy()

        data["changed_by"] = "testUser"
        data["vehicle_number"] = "TR 01 UK 2003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["changed_by"] = 'testUser2'
        data["vehicle_number"] = "TR 01 UK 2004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_invalid_changed_by(self):
        data = self.minimum_valid_data.copy()

        data["changed_by"] = "@45z#$%^&"
        data["vehicle_number"] = "TR 01 UK 2005"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["changed_by"] = "a" * 151
        data["vehicle_number"] = "TR 01 UK 2006"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["changed_by"] = None
        data["vehicle_number"] = "TR 01 UK 2007"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Adding driver field to minimum valid data
    def test_create_owner_vehicle_with_driver(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.minimum_valid_data["driver"] = self.driver.id
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding chassis_number field to minimum valid data
    def test_create_owner_vehicle_with_chassis_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.minimum_valid_data["chassis_number"] = "junkNumber"
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_duplicate_vehicle_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.owner_vehicle_data.copy()
        data["vehicle_number"] = self.owner_vehicle.vehicle_number
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_vehicle_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.owner_vehicle_data.copy()
        data["puc_certificate_issued_on"] = "2016-07-14T10:03:59.517090"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.owner_vehicle_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.owner_vehicle_data.copy()
        data["driver"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = self.driver.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.owner_vehicle_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.owner_vehicle_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.owner_vehicle_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.owner_vehicle_data.copy()
        data["created_by"] = self.test_user.id
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_owner_vehicle_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_owner_vehicle_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.owner_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_owner_vehicle_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"driver": self.driver.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_owner_vehicle(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_owner_vehicle(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("owner_owner_vehicle_retrieve",
                                   kwargs={"pk": self.owner_vehicle.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_owner_vehicle_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.owner_vehicle.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_vehicle_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.owner_vehicle.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_vehicle_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class FuelCardTest(OwnerAppSetup):
    """
        Test cases for Fuel Card
    """

    def setUp(self):
        super().setUp()
        self.fuel_card_data = {
            "deleted": False,
            "deleted_on": None,
            "customer_id": "1001507486",
            "card_number": "SomeUniqueNumber",
            "issue_date": None,
            "expiry_date": "27-Jun-2016"
        }
        self.minimum_valid_data = {}

        self.create_url = reverse("owner_fuel_card_create")
        self.update_url = reverse("owner_fuel_card_update", kwargs={"pk": self.fuel_card.id})
        self.partial_update_url = reverse("owner_fuel_card_partial_update", kwargs={"pk": self.fuel_card.id})
        self.retrieve_url = reverse("owner_fuel_card_retrieve", kwargs={"pk": self.fuel_card.id})

    def test_create_fuel_card_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_fuel_card_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_vehicle_with_duplicate_vehicle_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.fuel_card_data.copy()
        data["card_number"] = self.fuel_card.card_number
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_fuel_card_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.fuel_card_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.fuel_card_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.fuel_card_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.fuel_card_data.copy()
        data["created_by"] = self.test_user.id
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_fuel_card_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_fuel_card_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.fuel_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_fuel_card_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"customer_id": "23123213"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_fuel_card(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_fuel_card(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("owner_fuel_card_retrieve",
                                   kwargs={"pk": self.fuel_card.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FuelCardTransactionTest(OwnerAppSetup):
    """
        Test cases for Fuel Card Transaction
    """

    def setUp(self):
        super().setUp()
        self.fuel_card_transaction_data = {
            "deleted": False,
            "deleted_on": None,
            "payment_date": "2016-05-03T00:00:00",
            "vehicle": self.owner_vehicle.id,
            "fuel_card": self.fuel_card.id,
            "paid_to": "Test",
            "amount": 2500,
        }
        self.minimum_valid_data = {
            "payment_date": "2016-05-03T00:00:00",
            "vehicle": self.owner_vehicle.id,
            "fuel_card": self.fuel_card.id

        }

        self.create_url = reverse("owner_fuel_card_transaction_create")
        self.update_url = reverse("owner_fuel_card_transaction_update", kwargs={"pk": self.fuel_card_transaction.id})
        self.partial_update_url = reverse("owner_fuel_card_transaction_partial_update",
                                          kwargs={"pk": self.fuel_card_transaction.id})
        self.retrieve_url = reverse("owner_fuel_card_transaction_retrieve",
                                    kwargs={"pk": self.fuel_card_transaction.id})

    def test_create_fuel_card_transaction_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding amount to minimum valid data
    def test_create_fuel_card_transaction_with_valid_amount(self):
        data = self.minimum_valid_data.copy()
        data["amount"] = 4300
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding paid_to to minimum valid data
    def test_create_fuel_card_transaction_with_valid_paid_to(self):
        data = self.minimum_valid_data.copy()
        data["paid_to"] = "Mr.X"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted to minimum valid data
    def test_create_fuel_card_transaction_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_fuel_card_transaction_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_fuel_card_transaction_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.fuel_card_transaction_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.fuel_card_transaction_data.copy()
        data["vehicle"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = self.owner_vehicle.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.fuel_card_transaction_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.fuel_card_transaction_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.fuel_card_transaction_data.copy()
        data["created_by"] = self.test_user.id
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_fuel_card_transaction_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_fuel_card_transaction_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.fuel_card_transaction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_fuel_card_transaction_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"vehicle": self.owner_vehicle.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_fuel_card_transaction(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_fuel_card_transaction(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("owner_fuel_card_transaction_retrieve",
                                   kwargs={"pk": self.fuel_card_transaction.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
