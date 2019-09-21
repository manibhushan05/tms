import json

from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from restapi.helper_api import generate_random_string
from utils.models import State, City, BankName, Address, IDDetails, IfscDetail, Bank, TaxationID, AahoOffice
from datetime import datetime


class UtilsSetup(APITestCase):
    '''
        Setup dummy data for tesing purpose
    '''

    def setUp(self):
        self.login_url = reverse('login')

        self.test_user = User.objects.create_user('testUser', 'test@example.com', 'testPassword')
        self.login_data = self.client.post(self.login_url, {"username": "testUser", "password": "testPassword"}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        self.state = mommy.make(State)
        self.city = mommy.make(City, _fill_optional=['state'])
        self.address = mommy.make(Address)
        self.id_details = mommy.make(IDDetails)
        self.bank_name = mommy.make(BankName)
        self.ifsc_detail = mommy.make(IfscDetail)
        self.bank = mommy.make(Bank)
        self.taxation_id = mommy.make(TaxationID)
        self.aaho_office = mommy.make(AahoOffice)


class StateTest(UtilsSetup):
    """
        Test cases for State 
    """

    def setUp(self):
        super().setUp()
        self.state_data = {
            "name": "test",
            "deleted": False,
            "deleted_on": None
        }
        self.minimum_valid_data = {
            "name": "test"
        }
        self.create_url = reverse("utils_state_create")
        self.update_url = reverse("utils_state_update", kwargs={"pk": self.state.id})
        self.partial_update_url = reverse("utils_state_partial_update", kwargs={"pk": self.state.id})
        self.retrieve_url = reverse("utils_state_retrieve", kwargs={"pk": self.state.id})
        self.filter_url = reverse('utils_state_list')

    def test_create_state_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_state_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_state_with_valid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = "my_aaho_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = generate_random_string(69)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = generate_random_string(70)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_state_with_invalid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = generate_random_string(71)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_state_with_valid_code(self):
        data = self.minimum_valid_data.copy()

        data["code"] = "MH"
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["code"] = "uP"
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["code"] = "29"
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_state_with_invalid_code(self):
        data = self.minimum_valid_data.copy()

        data["code"] = "A"
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["code"] = "TIM"
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["code"] = None
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_state_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_state_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = None
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_state_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_state_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-2018:20:30:203"
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09:12:18:20:30:230"
        data["name"] = generate_random_string(10)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_state_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_state_with_duplicate_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.state_data.copy()
        data["name"] = self.state.name
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_state_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.state_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.state_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.state_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_state_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_state_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.state_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_state_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"name": "test"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_state_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_state_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("utils_state_retrieve",
                                   kwargs={"pk": self.state.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_state_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CityTest(UtilsSetup):
    """
        Test cases for City
    """

    def setUp(self):
        super().setUp()
        self.city_data = {
            "name": "Abohar",
            "code": "ABR",
            "pin": 234312,
            "latitude": "30.145292800000",
            "longitude": "74.199304300000",
            "deleted": False,
            "deleted_on": None,
            "state": self.state.id
        }
        self.minimum_valid_data = {
            "name": "Abohar",
            "code": "ABR",
            "state": self.state.id
        }
        self.create_url = reverse("utils_city_create")
        self.update_url = reverse("utils_city_update", kwargs={"pk": self.city.id})
        self.partial_update_url = reverse("utils_city_partial_update", kwargs={"pk": self.city.id})
        self.retrieve_url = reverse("utils_city_retrieve", kwargs={"pk": self.city.id})
        self.filter_url = reverse('utils_city_list')

    def test_create_city_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_city_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_city_with_valid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = "MyNameIsKhan"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = generate_random_string(199)
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = generate_random_string(200)
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_city_with_invalid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["name"] = generate_random_string(201)
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_city_with_valid_code(self):
        data = self.minimum_valid_data.copy()

        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_city_with_invalid_code(self):
        data = self.minimum_valid_data.copy()

        data["code"] = generate_random_string(2)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["code"] = generate_random_string(4)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["code"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_city_with_valid_pin(self):
        data = self.minimum_valid_data.copy()

        data["pin"] = "400011"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pin"] = generate_random_string(6)
        data["code"] = generate_random_string(3)
        data["state"] = self.state.id + 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_city_with_invalid_pin(self):
        data = self.minimum_valid_data.copy()

        data["pin"] = generate_random_string(5)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = generate_random_string(7)
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = ""
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_city_with_valid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = 12.2345
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["latitude"] = 1.123456789123
        data["code"] = generate_random_string(3)
        data["state"] = self.state.id + 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_city_with_invalid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = "invalid"
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["latitude"] = 1.1234567891213
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_city_with_valid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = 12.2345
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["longitude"] = 1.123456789123
        data["code"] = generate_random_string(3)
        data["state"] = self.state.id + 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_city_with_invalid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = "invalid"
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["longitude"] = 1.1234567891213
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_city_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["code"] = generate_random_string(3)
        data["state"] = self.state.id + 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_city_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = None
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_city_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["code"] = generate_random_string(3)
        data["state"] = self.state.id + 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_city_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-2018:20:30:203"
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09:12:18:20:30:230"
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_city_with_valid_state(self):
        data = self.minimum_valid_data.copy()

        data["state"] = self.state.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_city_with_invalid_state(self):
        data = self.minimum_valid_data.copy()

        data["state"] = self.state.id * 1000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["state"] = -123
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["state"] = 0
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["state"] = 1223456
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["state"] = "invalid"
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["state"] = datetime.now()
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["state"] = None
        data["code"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_city_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_city_with_duplicate_code(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.city_data.copy()
        data["code"] = self.city.code
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_city_with_non_unique_combination_of_name_and_state(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.city_data.copy()
        data["name"] = self.city.name
        data["state"] = self.city.state.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_city_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.city_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.city_data.copy()
        data["state"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["state"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["state"] = self.state.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.city_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.city_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_city_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_city_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_city_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"name": "test"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_city_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_city_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("utils_city_retrieve",
                                   kwargs={"pk": self.city.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_city_list_page(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AddressTest(UtilsSetup):
    """
        Test cases for Address 
    """

    def setUp(self):
        super().setUp()
        self.address_data = {
            "line1": "Kolkata",
            "line2": None,
            "line3": "Baker 214 street",
            "landmark": "KFC",
            "pin": "122312",
            "latitude": "23.23",
            "longitude": "12.12",
            "deleted": False,
            "deleted_on": None,
            "city": self.city.id
        }
        self.minimum_valid_data = {
            "line1": "Kolkata "
        }
        self.create_url = reverse("utils_address_create")
        self.update_url = reverse("utils_address_update", kwargs={"pk": self.address.id})
        self.partial_update_url = reverse("utils_address_partial_update", kwargs={"pk": self.address.id})
        self.retrieve_url = reverse("utils_address_retrieve", kwargs={"pk": self.address.id})

    def test_create_address_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_with_other_data_format(self):
        pass

    def test_create_address_with_valid_line1(self):
        data = self.minimum_valid_data.copy()

        data["line1"] = generate_random_string(499)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["line1"] = generate_random_string(500)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_with_invalid_line1(self):
        data = self.minimum_valid_data.copy()

        data["line1"] = generate_random_string(501)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_with_valid_line2(self):
        data = self.minimum_valid_data.copy()

        data["line2"] = generate_random_string(199)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["line2"] = generate_random_string(200)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["line2"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_with_invalid_line2(self):
        data = self.minimum_valid_data.copy()

        data["line2"] = generate_random_string(201)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_with_valid_line3(self):
        data = self.minimum_valid_data.copy()

        data["line3"] = generate_random_string(199)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["line3"] = generate_random_string(200)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["line3"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_with_invalid_line3(self):
        data = self.minimum_valid_data.copy()

        data["line3"] = generate_random_string(201)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_with_valid_landmark(self):
        data = self.minimum_valid_data.copy()

        data["landmark"] = generate_random_string(199)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["landmark"] = generate_random_string(200)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["landmark"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_with_invalid_landmark(self):
        data = self.minimum_valid_data.copy()

        data["landmark"] = generate_random_string(201)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_with_valid_pin(self):
        data = self.minimum_valid_data.copy()

        data["pin"] = "400001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pin"] = generate_random_string(6)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["landmark"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_with_invalid_pin(self):
        data = self.minimum_valid_data.copy()

        data["pin"] = generate_random_string(5)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = generate_random_string(7)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_with_valid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = generate_random_string(29)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["latitude"] = generate_random_string(30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["landmark"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_with_invalid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = generate_random_string(31)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_with_valid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = generate_random_string(29)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["longitude"] = generate_random_string(30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["longitude"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_with_invalid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = generate_random_string(31)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_with_valid_deleted(self):
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

    def test_create_address_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-2018:20:30:203"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09:12:18:20:30:230"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_with_valid_city(self):
        data = self.minimum_valid_data.copy()

        data["city"] = self.city.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_with_invalid_city(self):
        data = self.minimum_valid_data.copy()

        data["city"] = self.city.id * 1000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = 1223456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Adding city field to minimum valid data
    def test_create_address_with_city(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["city"] = self.city.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_address_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.address_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.address_data.copy()
        data["city"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = self.city.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.address_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.address_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_address_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_address_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_address_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"line1": "test"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_address_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_address_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("utils_address_retrieve",
                                   kwargs={"pk": self.address.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class IDDetailsTest(UtilsSetup):
    """
        Test cases for ID Details
    """

    def setUp(self):
        super().setUp()
        self.id_details_data = {
            "id_type": "DL",
            "id_number": "3198",
            "id_issued_in": "home",
            "validity": None,
            "issue_date": "2016-12-06",
            "id_image_url": "https://www.google.com",
            "deleted": False,
            "deleted_on": None
        }
        self.minimum_valid_data = {
            "id_number": "123",
            "id_type": "PAN"
        }
        self.create_url = reverse("utils_id_details_create")
        self.update_url = reverse("utils_id_details_update", kwargs={"pk": self.id_details.id})
        self.partial_update_url = reverse("utils_id_details_partial_update", kwargs={"pk": self.id_details.id})
        self.retrieve_url = reverse("utils_id_details_retrieve", kwargs={"pk": self.id_details.id})

    def test_create_id_details_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_id_details_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding issued date to minimum data
    def test_create_id_details_with_valid_issued_date(self):
        data = self.minimum_valid_data.copy()
        data["issue_date"] = "2018-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted to minimum data
    def test_create_id_details_with_minimum_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted on to minimum data
    def test_create_id_details_with_minimum_valid_data(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_id_details_with_full_valid_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_id_details_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.id_details_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.id_details_data.copy()
        data["issue_date"] = "2016-07-14T13:22:30.380211"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.id_details_data.copy()
        data["id_image_url"] = "invalid url"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.id_details_data.copy()
        data["id_type"] = "invalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.id_details_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.id_details_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_id_details_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_id_details_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.id_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_id_details_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"id_issued_in": "test"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_id_details_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_id_details_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("utils_id_details_retrieve",
                                   kwargs={"pk": self.id_details.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BankNameTest(UtilsSetup):
    """
        Test cases for Bank Name
    """

    def setUp(self):
        super().setUp()
        self.bank_name_data = {
            "name": "test",
            "deleted": False,
            "deleted_on": None
        }
        self.minimum_valid_data = {
            "name": "test"
        }
        self.create_url = reverse("utils_bank_name_create")
        self.update_url = reverse("utils_bank_name_update", kwargs={"pk": self.bank_name.id})
        self.partial_update_url = reverse("utils_bank_name_partial_update", kwargs={"pk": self.bank_name.id})
        self.retrieve_url = reverse("utils_bank_name_retrieve", kwargs={"pk": self.bank_name.id})

    def test_create_bank_name_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_name_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted field to minimum data
    def test_create_bank_name_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted on field to minimum data
    def test_create_bank_name_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_name_with_full_valid_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_name_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.bank_name_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.bank_name_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.bank_name_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_bank_name_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_bank_name_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.bank_name_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_bank_name_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"name": "test"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_bank_name_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_bank_name_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("utils_bank_name_retrieve",
                                   kwargs={"pk": self.bank_name.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class IfscDetailTest(UtilsSetup):
    """
        Test cases for Ifsc Detail
    """

    def setUp(self):
        super().setUp()
        self.ifsc_detail_data = {
            "ifsc_code": "ABHY0065001",
            "micr_code": "400065001",
            "branch_name": "RTGS-HO",
            "address": "ABHYUDAYA BANK BLDG., B.NO.71, NEHRU NAGAR, KURLA (E), MUMBAI-400024",
            "contact_details": "25260173",
            "centre": "MUMBAI",
            "district": "GREATER MUMBAI",
            "state": "MAHARASHTRA",
            "deleted": False,
            "deleted_on": None,
            "bank": self.bank_name.id
        }
        self.minimum_valid_data = {
            "ifsc_code": "ABHY0065001"
        }
        self.create_url = reverse("utils_ifsc_detail_create")
        self.update_url = reverse("utils_ifsc_detail_update", kwargs={"pk": self.ifsc_detail.id})
        self.partial_update_url = reverse("utils_ifsc_detail_partial_update", kwargs={"pk": self.ifsc_detail.id})
        self.retrieve_url = reverse("utils_ifsc_detail_retrieve", kwargs={"pk": self.ifsc_detail.id})

    def test_create_ifsc_detail_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ifsc_detail_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_detail_with_valid_ifsc_code(self):
        data = self.minimum_valid_data.copy()

        data["ifsc_code"] = "aaho0abcdef"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["ifsc_code"] = "aaho0123456"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["ifsc_code"] = "wxyz012AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_detail_with_invalid_ifsc_code(self):
        data = self.minimum_valid_data.copy()

        data["ifsc_code"] = "invalidifsc"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc_code"] = "wxyZ012AB3xi"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc_code"] = "aaho2abcdef"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc_code"] = "1aho0123456"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc_code"] = "a2ho0abc123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc_code"] = "aa3o0ab1234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ifsc_details_with_valid_micr_code(self):
        data = self.minimum_valid_data.copy()

        data["micr_code"] = generate_random_string(34)
        data["ifsc_code"] = "wxyz012AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["micr_code"] = generate_random_string(35)
        data["ifsc_code"] = "wxyz013AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["micr_code"] = None
        data["ifsc_code"] = "wxyz014AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_details_with_invalid_micr_code(self):
        data = self.minimum_valid_data.copy()

        data["micr_code"] = generate_random_string(36)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ifsc_details_with_valid_branch_name(self):
        data = self.minimum_valid_data.copy()

        data["branch_name"] = generate_random_string(399)
        data["ifsc_code"] = "wxyz012AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["branch_name"] = generate_random_string(400)
        data["ifsc_code"] = "wxyz013AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["branch_name"] = None
        data["ifsc_code"] = "wxyz014AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_details_with_invalid_branch_name(self):
        data = self.minimum_valid_data.copy()

        data["branch_name"] = generate_random_string(401)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ifsc_details_with_valid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = generate_random_string(399)
        data["ifsc_code"] = "wxyz012AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = generate_random_string(400)
        data["ifsc_code"] = "wxyz013AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = None
        data["ifsc_code"] = "wxyz014AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_details_with_invalid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = generate_random_string(401)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ifsc_details_with_valid_contact_details(self):
        data = self.minimum_valid_data.copy()

        data["contact_details"] = generate_random_string(399)
        data["ifsc_code"] = "wxyz012AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_details"] = generate_random_string(400)
        data["ifsc_code"] = "wxyz013AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_details"] = None
        data["ifsc_code"] = "wxyz014AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_details_with_invalid_contact_details(self):
        data = self.minimum_valid_data.copy()

        data["contact_details"] = generate_random_string(401)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ifsc_details_with_valid_centre(self):
        data = self.minimum_valid_data.copy()

        data["centre"] = generate_random_string(399)
        data["ifsc_code"] = "wxyz012AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["centre"] = generate_random_string(400)
        data["ifsc_code"] = "wxyz013AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["centre"] = None
        data["ifsc_code"] = "wxyz014AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_details_with_invalid_centre(self):
        data = self.minimum_valid_data.copy()

        data["centre"] = generate_random_string(401)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ifsc_details_with_valid_district(self):
        data = self.minimum_valid_data.copy()

        data["district"] = generate_random_string(69)
        data["ifsc_code"] = "wxyz012AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["district"] = generate_random_string(70)
        data["ifsc_code"] = "wxyz013AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["district"] = None
        data["ifsc_code"] = "wxyz014AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_details_with_invalid_district(self):
        data = self.minimum_valid_data.copy()

        data["district"] = generate_random_string(71)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ifsc_details_with_valid_state(self):
        data = self.minimum_valid_data.copy()

        data["state"] = generate_random_string(69)
        data["ifsc_code"] = "wxyz012AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["state"] = generate_random_string(70)
        data["ifsc_code"] = "wxyz013AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["state"] = None
        data["ifsc_code"] = "wxyz014AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_details_with_invalid_state(self):
        data = self.minimum_valid_data.copy()

        data["state"] = generate_random_string(71)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ifsc_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["ifsc_code"] = "wxyz013AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["ifsc_code"] = "wxyz014AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["ifsc_code"] = "wxyz015AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        data["ifsc_code"] = "wxyz013AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = None
        data["ifsc_code"] = "wxyz014AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ifsc_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["ifsc_code"] = "wxyz013AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-2018:20:30:203"
        data["ifsc_code"] = "wxyz013AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09:12:18:20:30:230"
        data["ifsc_code"] = "wxyz014AB3x"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Adding bank field to minimum valid data
    def test_create_ifsc_details_with_bank(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["bank"] = self.bank_name.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_detail_with_full_valid_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ifsc_detail_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.ifsc_detail_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.ifsc_detail_data.copy()
        data["bank"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bank"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bank"] = self.bank_name.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.ifsc_detail_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.ifsc_detail_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_ifsc_detail_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_ifsc_detail_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.ifsc_detail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_ifsc_detail_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"branch_name": "test"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_ifsc_detail_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_ifsc_detail_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("utils_ifsc_detail_retrieve",
                                   kwargs={"pk": self.ifsc_detail.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BankTest(UtilsSetup):
    """
        Test cases for Bank
    """

    def setUp(self):
        super().setUp()
        self.bank_data = {
            "bank": "AXIS BANK",
            "account_holder_name": "Dilip Ghosh",
            "beneficiary_code": "DILIPGHOSHTO",
            "account_number": "913010029016752",
            "transaction_type": "both",
            "account_type": "SA",
            "ifsc": "UTIB0000409",
            "address": "Baker street",
            "city": "test",
            "remarks": "good",
            "is_verified": "yes",
            "status": "active",
            "deleted": False,
            "deleted_on": None,
            "user": self.test_user.username
        }
        self.minimum_valid_data = {
            "account_holder_name": "Dilip Ghosh",
            "account_number": "913010029016752",
            "ifsc": "UTIB0000409",
            "address": "Baker street",
            "account_type": "SA",
            "beneficiary_code": "DILIPGHOSHTO",
            "bank": "AXIS BANK",
            "city": "test",
            "is_verified": "yes",
            "user": self.test_user.username,
            "transaction_type": "both"

        }
        self.create_url = reverse("utils_bank_create")
        self.update_url = reverse("utils_bank_update", kwargs={"pk": self.bank.id})
        self.partial_update_url = reverse("utils_bank_partial_update", kwargs={"pk": self.bank.id})
        self.retrieve_url = reverse("utils_bank_retrieve", kwargs={"pk": self.bank.id})

    def test_create_bank_beneficiary_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_data_format(self):
        pass

    def test_create_bank_beneficiary_with_valid_user(self):
        data = self.minimum_valid_data.copy()

        data["user"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_user(self):
        data = self.minimum_valid_data.copy()

        data["user"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_bank_name(self):
        data = self.minimum_valid_data.copy()

        data["bank"] = "STATE BANK OF INDIA"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["bank"] = "ALLAHABAD BANK"
        data["account_number"] = "913010029016753"
        data["beneficiary_code"] = "ABCDE124"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["bank"] = "UCO BANK"
        data["account_number"] = "913010029016754"
        data["beneficiary_code"] = "ABCDE125"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_bank_name(self):
        data = self.minimum_valid_data.copy()

        # data["bank"] = -1234
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bank"] = ""
        data["account_number"] = "913010029016755"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bank"] = None
        data["account_number"] = "913010029016756"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bank"] = "a" * 256
        data["account_number"] = "913010029016757"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # data["bank"] = "@#$%@!!!"
        # data["account_number"] = "913010029016758"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_account_holder_name(self):
        data = self.minimum_valid_data.copy()

        data["account_holder_name"] = "valid name"
        data["account_number"] = "903010029016753"
        data["beneficiary_code"] = "ABCDE124"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["account_holder_name"] = "a" * 99
        data["account_number"] = "903010029016754"
        data["beneficiary_code"] = "ABCDE123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["account_holder_name"] = "a" * 100
        data["account_number"] = "903010029016755"
        data["beneficiary_code"] = "ABCDE125"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_account_holder_name(self):
        data = self.minimum_valid_data.copy()

        data["account_holder_name"] = "ab"  # length less than 3
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["account_holder_name"] = "a" * 101  # lenght greater than 100
        data["account_number"] = "903010029016759"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["account_holder_name"] = ""  # empty string
        data["account_number"] = "903010029016760"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["account_holder_name"] = None  # Null not allowed
        data["account_number"] = "903010029016761"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_beneficiary_code(self):
        data = self.minimum_valid_data.copy()

        data["beneficiary_code"] = "VALID786"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["beneficiary_code"] = "123"
        data["account_number"] = "803010029016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["beneficiary_code"] = "A1" * 7
        data["account_number"] = "803010029016754"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_beneficiary_code(self):
        data = self.minimum_valid_data.copy()

        data["beneficiary_code"] = "invalid_786"  # lowercase and underscore invalid
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["beneficiary_code"] = "12"  # length less than 3
        data["account_number"] = "803010029016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["beneficiary_code"] = "A13" * 5  # length greater than 14
        data["account_number"] = "803010029016754"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["beneficiary_code"] = ""  # empty string
        data["account_number"] = "803010029016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["beneficiary_code"] = None  # Null not allowed
        data["account_number"] = "803010029016754"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_account_number(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["account_number"] = "123456789"  # min lenth 9
        data["beneficiary_code"] = "ABCDE123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["account_number"] = "alphanumeric1234"  # alphanumeric allowed
        data["beneficiary_code"] = "ABCDE124"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["account_number"] = "alnum1234" * 2  # max length 18
        data["beneficiary_code"] = "ABCDE125"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_account_number(self):
        data = self.minimum_valid_data.copy()

        data["account_number"] = "12345678"  # invalid less than 9
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["account_number"] = "invalid@$_1"  # special character not allowed
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["account_number"] = "1" * 19  # length greater than 18
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["account_number"] = ""  # empty string not allowed
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["account_number"] = None  # None not allowed
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_transaction_type(self):
        data = self.minimum_valid_data.copy()

        data["transaction_type"] = "neft"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["transaction_type"] = "rtgs"
        data["account_number"] = "803010029016753"
        data["beneficiary_code"] = "ABCDE123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["transaction_type"] = "both"
        data["beneficiary_code"] = "ABCDE124"
        data["account_number"] = "803010029016754"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["transaction_type"] = "hdfc_internal_account"
        data["beneficiary_code"] = "ABCDE125"
        data["account_number"] = "803010029016755"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_transaction_type(self):
        data = self.minimum_valid_data.copy()

        data["transaction_type"] = "invalid_choice@#!"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["transaction_type"] = 12
        data["account_number"] = "803010029016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["transaction_type"] = ""
        data["account_number"] = "803010029016757"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # data["transaction_type"] = None
        # data["account_number"] = "803010029016754"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_account_type(self):
        data = self.minimum_valid_data.copy()

        data["account_type"] = "SA"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["account_type"] = "CA"
        data["beneficiary_code"] = "ABCDE123"
        data["account_number"] = "823010029016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["account_type"] = "KCC"
        data["account_number"] = "823010029016754"
        data["beneficiary_code"] = "ABCDE124"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["account_type"] = "RA"
        data["account_number"] = "823010029016755"
        data["beneficiary_code"] = "ABCDE125"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_account_type(self):
        data = self.minimum_valid_data.copy()

        data["account_type"] = "invalid_choice@#!"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["account_type"] = 12
        data["account_number"] = "803010129016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["account_type"] = ""
        data["account_number"] = "803010229016754"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["account_type"] = None
        data["account_number"] = "803010329016755"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_ifsc(self):
        data = self.minimum_valid_data.copy()

        data["ifsc"] = "aaho0abcdef"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["ifsc"] = "aaho0123456"
        data["beneficiary_code"] = "ABCDE123"
        data["account_number"] = "823010029016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["ifsc"] = "wxyz012AB3x"
        data["account_number"] = "823010029016754"
        data["beneficiary_code"] = "ABCDE126"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_ifsc(self):
        data = self.minimum_valid_data.copy()

        data["ifsc"] = "aaho2abcdef"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc"] = "1aho0123456"
        data["account_number"] = "803010029016703"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc"] = "a2ho0abc123"
        data["account_number"] = "80301002901613"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc"] = "aa3o0ab1234"
        data["account_number"] = "803010029016723"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc"] = "aah40abcd12"
        data["account_number"] = "803010029016733"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc"] = "transiq tec"
        data["account_number"] = "803010029016743"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc"] = ""
        data["account_number"] = "803010029016763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["ifsc"] = None
        data["account_number"] = "803010029016773"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = "valid_address"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = "1a@"
        data["account_number"] = "823010029016753"
        data["beneficiary_code"] = "ABCDE123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = "ab$1" * 100
        data["account_number"] = "823010029016754"
        data["beneficiary_code"] = "ABCDE124"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = "A" * 399
        data["account_number"] = "823010029016755"
        data["beneficiary_code"] = "ABCDE125"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = "av"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["address"] = "a" * 401
        data["account_number"] = "803010129016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["address"] = ""
        data["account_number"] = "803010229016754"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["address"] = None
        data["account_number"] = "803010329016755"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_city(self):
        data = self.minimum_valid_data.copy()

        data["city"] = "valid_city"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["city"] = "1a@"
        data["beneficiary_code"] = "ABCDE123"
        data["account_number"] = "823010029016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["city"] = "ab$12" * 14
        data["beneficiary_code"] = "ABCDE124"
        data["account_number"] = "823010029016754"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["city"] = "A" * 69
        data["account_number"] = "823010029016755"
        data["beneficiary_code"] = "ABCDE125"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_city(self):
        data = self.minimum_valid_data.copy()

        data["city"] = "av"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = "a" * 71
        data["account_number"] = "803010129016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = ""
        data["account_number"] = "803010229016754"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = None
        data["account_number"] = "803010329016755"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_remarks(self):
        data = self.minimum_valid_data.copy()

        data["remarks"] = "valid_remark"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_remarks(self):
        data = self.minimum_valid_data.copy()

        data["remarks"] = ''
        data["account_number"] = "803010129016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_status(self):
        data = self.minimum_valid_data.copy()

        data["status"] = "active"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = "inactive"
        data["account_number"] = "123456779998"
        data["beneficiary_code"] = "ABCDE125"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = None
        data["account_number"] = "123456779999"
        data["beneficiary_code"] = "ABCDE126"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_status(self):
        data = self.minimum_valid_data.copy()

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["remarks"] = datetime.now()
        data["account_number"] = "803010129016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_valid_is_verified(self):
        data = self.minimum_valid_data.copy()

        data["is_verified"] = "yes"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_verified"] = "no"
        data["account_number"] = "123456779998"
        data["beneficiary_code"] = "ABCDE125"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_beneficiary_with_invalid_is_verified(self):
        data = self.minimum_valid_data.copy()

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["remarks"] = datetime.now()
        data["account_number"] = "803010129016753"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bank_beneficiary_with_full_valid_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.bank_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.bank_data.copy()
        data["transaction_type"] = "invalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.bank_data.copy()
        data["user"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["user"] = "{}invalid".format(self.test_user.username)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["user"] = self.test_user.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.bank_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.bank_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_bank_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_bank_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.bank_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_bank_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"user": self.test_user.username}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_bank_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_bank_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("utils_bank_retrieve",
                                   kwargs={"pk": self.bank.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TaxationIDTest(UtilsSetup):
    """
        Test cases for Taxation ID
    """

    def setUp(self):
        super().setUp()
        self.taxation_id_data = {
            "service_tax_number": "asd221s",
            "tan_number": "dsetstt23234",
            "pan": "324asd32",
            "deleted": False,
            "deleted_on": None,
        }
        self.minimum_valid_data = {
            }
        self.create_url = reverse("utils_taxation_id_create")
        self.update_url = reverse("utils_taxation_id_update", kwargs={"pk": self.taxation_id.id})
        self.partial_update_url = reverse("utils_taxation_id_partial_update", kwargs={"pk": self.taxation_id.id})
        self.retrieve_url = reverse("utils_taxation_id_retrieve", kwargs={"pk": self.taxation_id.id})

    def test_create_taxation_id_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding user field to minimum valid data
    def test_create_address_with_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["user"] = self.test_user.username
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding tan number field to minimum valid data
    def test_create_address_with_tan_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["tan_number"] = "dsetstt23234"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding deleted on field to minimum valid data
    def test_create_address_with_deleted_on(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_taxation_id_with_full_valid_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_taxation_id_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.taxation_id_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.taxation_id_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.taxation_id_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_taxation_id_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_taxation_id_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.taxation_id_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_taxation_id_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"user": self.test_user.username}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_taxation_id_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_taxation_id_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("utils_taxation_id_retrieve",
                                   kwargs={"pk": self.taxation_id.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AahoOfficeTest(UtilsSetup):
    """
        Test cases for Aaho Office
    """

    def setUp(self):
        super().setUp()
        self.aaho_office_data = {
            "branch_name": "Visakhapatnam",
            "branch_head": "Suresh K S",
            "address": "105B, B Block, Navya Nulife Apartments, Dairy Hospital Road, Sheelanagar",
            "pin": "530012",
            "email": "suresh@aaho.in",
            "phone": "8500695535",
            "t1_name": "Govind Rao",
            "t1_phone": "7799976644",
            "t2_name": "Suresh Kumar",
            "t2_phone": "8500695535",
            "deleted": False,
            "deleted_on": None,
            "branch": self.city.id
        }
        self.minimum_valid_data = {
            "branch_name": "Visakhapatnam",
            "phone": "8500695535",
            "address": "105B, B Block, Navya Nulife Apartments, Dairy Hospital Road, Sheelanagar",
            "branch": self.city.id,
            "branch_head": "Suresh K S",
            "pin": "530012",
            "email": "suresh@aaho.in"
        }
        self.create_url = reverse("utils_aaho_office_create")
        self.update_url = reverse("utils_aaho_office_update", kwargs={"pk": self.aaho_office.id})
        self.partial_update_url = reverse("utils_aaho_office_partial_update", kwargs={"pk": self.aaho_office.id})
        self.retrieve_url = reverse("utils_aaho_office_retrieve", kwargs={"pk": self.aaho_office.id})
        self.filter_url = reverse('utils_aaho_office_list')

    def test_create_aaho_office_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_valid_branch_name(self):
        data = self.minimum_valid_data.copy()

        data["branch_name"] = generate_random_string(199)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["branch_name"] = generate_random_string(200)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_invalid_branch_name(self):
        data = self.minimum_valid_data.copy()

        data["branch_name"] = generate_random_string(201)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["branch_name"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_valid_branch_head(self):
        data = self.minimum_valid_data.copy()

        data["branch_head"] = generate_random_string(99)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["branch_head"] = generate_random_string(100)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_invalid_branch_head(self):
        data = self.minimum_valid_data.copy()

        data["branch_head"] = generate_random_string(101)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["branch_head"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_valid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = generate_random_string(4)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = generate_random_string(5)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = generate_random_string(299)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = generate_random_string(300)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_invalid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = generate_random_string(3)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["address"] = generate_random_string(301)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["address"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_valid_pin(self):
        data = self.minimum_valid_data.copy()

        data["pin"] = generate_random_string(6)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pin"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_invalid_pin(self):
        data = self.minimum_valid_data.copy()

        data["pin"] = generate_random_string(5)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = generate_random_string(7)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_valid_phone(self):
        data = self.minimum_valid_data.copy()

        data["phone"] = "1234567890"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = "9200120000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_invalid_phone(self):
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

        data["phone"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_valid_t1_name(self):
        data = self.minimum_valid_data.copy()

        data["t1_name"] = generate_random_string(34)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["t1_name"] = generate_random_string(35)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["t1_name"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_invalid_t1_name(self):
        data = self.minimum_valid_data.copy()

        data["t1_name"] = generate_random_string(36)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_valid_t1_phone(self):
        data = self.minimum_valid_data.copy()

        data["t1_phone"] = "1234567890"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["t1_phone"] = "9554175000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["t1_phone"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_invalid_t1_phone(self):
        data = self.minimum_valid_data.copy()

        data["t1_phone"] = "0123456789"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["t1_phone"] = "123456789"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["t1_phone"] = "12345678911"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["t1_phone"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["t1_phone"] = "-1234567890"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_valid_t2_name(self):
        data = self.minimum_valid_data.copy()

        data["t2_name"] = generate_random_string(34)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["t2_name"] = generate_random_string(35)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["t2_name"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_invalid_t2_name(self):
        data = self.minimum_valid_data.copy()

        data["t2_name"] = generate_random_string(36)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_valid_t2_phone(self):
        data = self.minimum_valid_data.copy()

        data["t2_phone"] = "1234567890"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["t2_phone"] = "9554175000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["t2_phone"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_invalid_t2_phone(self):
        data = self.minimum_valid_data.copy()

        data["t2_phone"] = "0123456789"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["t12_phone"] = "123456789"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["t2_phone"] = "12345678911"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["t2_phone"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["t2_phone"] = "-1234567890"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_valid_deleted(self):
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

    def test_create_aaho_office_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-2018:20:30:203"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09:12:18:20:30:230"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_valid_branch(self):
        data = self.minimum_valid_data.copy()

        data["branch"] = self.city.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_with_invalid_branch(self):
        data = self.minimum_valid_data.copy()

        data["branch"] = self.city.id * 1000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["branch"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["branch"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["branch"] = 1223456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["branch"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["branch"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_aaho_office_with_full_valid_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_aaho_office_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.aaho_office_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.aaho_office_data.copy()
        data["email"] = "invalidEmail"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.aaho_office_data.copy()
        data["branch"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["branch"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["branch"] = self.city.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.aaho_office_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.aaho_office_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_aaho_office_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_aaho_office_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.aaho_office_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_aaho_office_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"branch": self.city.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_aaho_office_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_aaho_office_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("utils_aaho_office_retrieve",
                                   kwargs={"pk": self.aaho_office.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_aaho_office_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
