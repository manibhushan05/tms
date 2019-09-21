import json
from datetime import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from driver.models import Driver, DriverAppUser, GPSLogNew, OTP, GPSDevice, GPSDeviceLog, TracknovateGPSDevice, \
    TracknovateGPSDeviceLog, WaytrackerGPSDevice, WaytrackerGPSDeviceLog, TempoGoGPSDevice, TempoGoGPSDeviceLog, \
    SecuGPSDevice, SecuGPSDeviceLog, MahindraGPSDevice, MahindraGPSDeviceLog, GPSDeviceProvider
from owner.models import Vehicle
from restapi.helper_api import generate_random_string
from utils.models import Address, Bank, IDDetails, TaxationID


class DriverSetup(APITestCase):
    """
        Setup dummy data for testing purpose
    """

    def setUp(self):
        self.login_url = reverse('login')
        self.test_user = User.objects.create_user('testUser', 'test@example.com', 'testPassword')
        self.login_data = self.client.post(self.login_url, {"username": "testUser", "password": "testPassword"}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        self.address = mommy.make(Address)
        self.account_details = mommy.make(Bank)
        self.driver = mommy.make(Driver,phone='8978937498')
        self.vehicle = mommy.make(Vehicle)
        self.device_provider = mommy.make(GPSDeviceProvider)
        self.id_details = mommy.make(IDDetails)
        self.taxation_id = mommy.make(TaxationID)
        self.driver_app_user = mommy.make(DriverAppUser)
        self.gps_log_new = mommy.make(GPSLogNew)
        self.otp = mommy.make(OTP)
        self.gps_device = mommy.make(GPSDevice)
        self.gps_device_log = mommy.make(GPSDeviceLog)
        self.tracknovate_gps_device = mommy.make(TracknovateGPSDevice)
        self.tracknovate_gps_device_log = mommy.make(TracknovateGPSDeviceLog)
        self.waytracker_gps_device = mommy.make(WaytrackerGPSDevice)
        self.waytracker_gps_device_log = mommy.make(WaytrackerGPSDeviceLog)
        self.tempo_go_gps_device = mommy.make(TempoGoGPSDevice)
        self.tempo_go_gps_device_log = mommy.make(TempoGoGPSDeviceLog)
        self.secu_gps_device = mommy.make(SecuGPSDevice)
        self.secu_gps_device_log = mommy.make(SecuGPSDeviceLog)
        self.mahindra_gps_device = mommy.make(MahindraGPSDevice)
        self.mahindra_gps_device_log = mommy.make(MahindraGPSDeviceLog)



class DriverTest(DriverSetup):
    """
        Test cases for Driver
    """

    def setUp(self):
        super().setUp()
        self.driver_data = {
            "name": "Abbas",
            "phone": "9139263635",
            "driving_licence_number": "ukDl012723",
            "driving_licence_location": "mumbai",
            "driving_licence_validity": "2016-07-24",
            "smartphone_available": True,
            "route": "vaizag",
            "priority_level": "omega",
            "address": self.address.id,
            "id_proof": self.id_details.id,
            "account_details": self.account_details.id,
            "taxation_id": self.taxation_id.id
        }
        self.create_url = reverse("driver_driver_create")
        self.update_url = reverse("driver_driver_update", kwargs={"pk": self.driver.id})
        self.partial_update_url = reverse("driver_driver_partial_update", kwargs={"pk": self.driver.id})
        self.retrieve_url = reverse("driver_driver_retrieve", kwargs={"pk": self.driver.id})
        self.filter_url = reverse('driver_driver_list')


    def test_create_driver_with_minimum_valid_data(self):
        data = {"name": "Abbas", "phone": "9139263635"}
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_with_different_data_format(self):
        pass

    def test_create_driver_with_invalid_mobile_number(self):
        data = {"name": "Abbas", "phone": "91395 63635"}

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = " 139296363"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "0139263635"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "91392636351"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "          "
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "abcdefgh"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "None"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_driver_with_similar_mobile_number(self):
        data = {"name": "Abbas", "phone": "9139263635"}
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_with_invalid_name(self):
        data = {"name": "", "phone": "9139263635"}
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["name"] = "     "
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["name"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["name"] = "a"*36
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_driver_with_address(self):
        data = {"address": self.address.id, "phone": "9139263635", "name": "aaho"}
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.driver_data.copy()
        data["driving_licence_validity"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.driver_data.copy()
        data["address"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["address"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["address"] = self.address.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_with_valid_pan_details(self):
        data ={"name": "aaho", "phone": "1231231230", "pan": "CBPPK6928P"}
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = "1200000000"
        data["pan"] = "cbPpk6928P"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_with_invalid_pan_details(self):
        data ={"name": "aaho", "phone": "1231231230", "pan": "invalid"}

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = "None"
        data["phone"] = "1212121212"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pan"] = "123456aad54"
        data["phone"] = "1122334455"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def create_driver_with_invalid_methods(self):
        data = {"name": "aaho", "phone": "9876543210"}

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


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

    def test_update_driver_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, {"phone": "8978936498", "name": "aaho"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def  test_update_driver_without_making_any_changes(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)


    def test_update_driver_with_for_non_exiting_user(self):
        response = self.client.put(self.update_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_driver_with_for_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        data = {"name": "New name"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_driver_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_driver_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"name": "New name"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"driving_licence_validity": "2018-09-09"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # data = {"address": self.address.id}
        # response = self.client.patch(self.partial_update_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_driver_with_invalid_get_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.update_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_driver_with_invalid_post_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_driver_with_invalid_patch_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.update_url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_partial_update_driver_with_invalid_get_method(self):
        data = {"name": "name", "phone": "1234512345"}
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data["name"] = "New name"
        response = self.client.get(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_driver_with_invalid_post_method(self):
        data = {"name": "name", "phone": "1234512345"}
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data["name"] = "New name"
        response = self.client.post(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_driver_with_invalid_put_method(self):
        data = {"name": "name", "phone": "1234512345"}
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data["name"] = "New name"
        response = self.client.put(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_retrieve_existing_driver(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_driver(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_driver_retrieve",
                                   kwargs={"pk": self.driver.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_retrieve_existing_driver_with_invalid_post_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_retrieve_existing_driver_with_invalid_put_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_retrieve_existing_driver_with_invalid_patch_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_driver_filter_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DriverAppUserTest(DriverSetup):
    """
        Test cases for Driver App User
    """

    def setUp(self):
        super().setUp()
        self.driver_app_user_data = {
            "deleted": False,
            "deleted_on": None,
            "device_id": "353267062439805",
            "auth_token": "76c62fe7d839dc3dd2322ab2",
            "driver_name": "mani sony xperia",
            "driver_number": "+91 84 54 019094",
            "number_verified": False,
            "driving_licence_number": "DL09N6785",
            "vehicle_number": "vehnum",
            "vehicle_type": "test",
            "vehicle_status": "loading",
            "location_time": "2017-01-28T22:22:30.792000",
            "latitude": "19.1165155000",
            "longitude": "72.9090616000",
            "is_active": True,
            "inactive_sms_sent_at": None,
            "driver": self.driver.id,
        }
        self.minimum_valid_data = {
            "device_id": "353267062439805",
            "auth_token": "76c62fe7d83a439dc322abasd"
        }
        self.create_url = reverse("driver_driver_app_user_create")
        self.update_url = reverse("driver_driver_app_user_update", kwargs={"pk": self.driver_app_user.id})
        self.partial_update_url = reverse("driver_driver_app_user_partial_update",
                                          kwargs={"pk": self.driver_app_user.id})
        self.retrieve_url = reverse("driver_driver_app_user_retrieve", kwargs={"pk": self.driver_app_user.id})

    def test_create_driver_app_user_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding name field to minimum valid data required
    def test_create_driver_app_user_with_name(self):
        self.minimum_valid_data["name"] = "Naruto"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding status field to minimum valid data required
    def test_create_driver_app_user_with_status(self):
        self.minimum_valid_data["status"] = "pending"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding location time field to minimum valid data required
    def test_create_driver_app_user_with_location_time(self):
        self.minimum_valid_data["location_time"] = "2017-01-28T22:22:30.792000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_driver_app_user_with_driver(self):
        self.minimum_valid_data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_app_user_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.driver_app_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_app_user_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.driver_app_user_data.copy()
        data["location_time"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.driver_app_user_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.driver_app_user_data.copy()
        data["driver"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = self.driver.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.driver_app_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.driver_app_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.driver_app_user_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.driver_app_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.driver_app_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.driver_app_user_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_driver_app_user_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_driver_app_user_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.driver_app_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_driver_app_user_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"name": "New name"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"location_time": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"driver": self.driver.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_driver_app_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_driver_app_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_driver_app_user_retrieve",
                                   kwargs={"pk": self.driver_app_user.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GPSLogNewTest(DriverSetup):
    """
        Test cases for GPS Log New
    """

    def setUp(self):
        super().setUp()
        self.gps_log_new_data = {
            "deleted": False,
            "deleted_on": None,
            "datetime": "2016-09-16T07:53:42.700000",
            "device_id": "867290027958114",
            "latitude": "21.9200000763",
            "longitude": "82.7799987793",
            "altitude": 0,
            "speed": 0,
            "course": 81,
            "accuracy": None,
            "provider": None,
            "battery": 10,
            "total_memory": 3707.55859375,
            "available_memory": 1428.52734375,
            "threshold": 216,
            "low_memory": False,
            "android_release": "6.0.1",
            "android_sdk_int": 23,
            "version_name": "0.03",
            "version_code": 3,
            "brand": "OnePlus",
            "manufacturer": "OnePlus",
            "product": "OnePlus2",
            "device": "OnePlus2",
            "model": "ONE A2003",
            "driver_name": "shobhit oneplus",
            "driver_number": "9833003508",
            "driving_licence_number": "DL09N6785",
            "vehicle_number": "444",
            "vehicle_type": "truck",
            "vehicle_status": "unloaded",
            "driver": self.driver_app_user.id,
        }
        self.minimum_valid_data = {
            "device_id": "353267062439805",
            "datetime": "2016-09-16T07:53:42.700000"
        }
        self.create_url = reverse("driver_gps_log_new_create")
        self.update_url = reverse("driver_gps_log_new_update", kwargs={"pk": self.gps_log_new.id})
        self.partial_update_url = reverse("driver_gps_log_new_partial_update", kwargs={"pk": self.gps_log_new.id})
        self.retrieve_url = reverse("driver_gps_log_new_retrieve", kwargs={"pk": self.gps_log_new.id})

    def test_create_gps_log_new_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding latitude field to minimum valid data required
    def test_create_gps_log_new_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_gps_log_new_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_gps_log_new_with_driver(self):
        self.minimum_valid_data["driver"] = self.driver_app_user.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_gps_log_new_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.gps_log_new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_gps_log_new_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.gps_log_new_data.copy()
        data["datetime"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.gps_log_new_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.gps_log_new_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.gps_log_new_data.copy()
        data["driver"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = self.driver_app_user.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.gps_log_new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.gps_log_new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.gps_log_new_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.gps_log_new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.gps_log_new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.gps_log_new_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_gps_log_new_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_gps_log_new_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.gps_log_new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_gps_log_new_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"driver_name": "New name"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"datetime": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"driver": self.driver_app_user.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_gps_log_new(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_gps_log_new(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_gps_log_new_retrieve",
                                   kwargs={"pk": self.gps_log_new.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OTPTest(DriverSetup):
    """
        Test cases for OTP Test
    """
    def setUp(self):
        super().setUp()
        self.otp_data = {
            "phone": "8435184317",
            "expires_at": "2016-11-30T17:16:36.716816",
            "otp": "544483",
            "deleted": True,
            "deleted_on": None,
        }
        self.minimum_valid_data = {
            "phone": "8435184317",
            "expires_at": "2016-11-30T17:16:36.716816",
            "otp": "544483"
        }
        self.create_url = reverse("driver_otp_create")
        self.update_url = reverse("driver_otp_update", kwargs={"pk": self.otp.id})
        self.partial_update_url = reverse("driver_otp_partial_update", kwargs={"pk": self.otp.id})
        self.retrieve_url = reverse("driver_otp_retrieve", kwargs={"pk": self.otp.id})

    def test_create_otp_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding deleted on field to minimum valid data required
    def test_create_otp_with_deleted_on(self):
        data =  self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

     #adding deleted field to minimum valid data
    def test_create_otp_with_deleted(self):
        data =  self.minimum_valid_data.copy()
        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_otp_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_otp_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.otp_data.copy()
        data["deleted_on"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.otp_data.copy()
        data["phone"] = None
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_otp_with_invalid_request(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.otp_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.otp_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_update_otp_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_otp_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_otp_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"phone": "1232123212"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"deleted_on": "2016-11-30T17:16:36.716816"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_otp(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_otp(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_otp_retrieve",
                                   kwargs={"pk": self.otp.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GPSDeviceTest(DriverSetup):
    """
        Test cases for GPS Device
    """

    def setUp(self):
        super().setUp()
        self.gps_device_data = {
            "deleted": False,
            "deleted_on": datetime.now(),
            "device_id": "ID123456789",
            "imei": "IMei123456",
            "address": "Mumbai , transiq, 400001",
            "driver_name": "Mr.X",
            "driver_number": "7234567890",
            "driving_licence_number": "DL12331031",
            "vehicle_number": "mh-12-BOM-2018",
            "vehicle_type": "semi open, 12 tyres",
            "vehicle_status": "loading",
            "location_time": datetime.now(),
            "latitude": 1213.231212,
            "longitude": 1232.12312,
            "is_active": True,
            "device_provider": self.device_provider.id,
            "vehicle": self.vehicle.id,
            "driver": self.driver.id,
        }
        self.minimum_valid_data = {
            "device_id": "ID123456789",
            "device_provider": self.device_provider.id
        }
        self.create_url = reverse("driver_gps_device_create")
        self.update_url = reverse("driver_gps_device_update", kwargs={"pk": self.gps_device.id})
        self.partial_update_url = reverse("driver_gps_device_partial_update", kwargs={"pk": self.gps_device.id})
        self.retrieve_url = reverse("driver_gps_device_retrieve", kwargs={"pk": self.gps_device.id})

    def test_create_gps_device_with_minimum_valid_data(self):

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding latitude field to minimum valid data required
    def test_create_gps_device_with_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = "21.9200001212"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_gps_device_with_vehicle_status(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_gps_device_with_driver(self):
        data = self.minimum_valid_data.copy()

        data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_gps_device_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_gps_device_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.gps_device_data.copy()
        data["location_time"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.gps_device_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.gps_device_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.gps_device_data.copy()
        data["driver"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device_provider"] = "invalid"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle"] = self.vehicle.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_gps_device_with_invalid_request(self):
        data = self.gps_device_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_gps_device_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_gps_device_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_gps_device_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"phone": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"location_time": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"driver": self.driver.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_gps_device_retrieve",
                                   kwargs={"pk": self.gps_device.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GPSDeviceLogTest(DriverSetup):
    """
        Test cases for GPS Device Log
    """

    def setUp(self):
        super().setUp()
        self.gps_device_log_data = {

            "location_id": "590d68029ca81c2344818dd8",
            "datetime": "2017-05-06T11:36:30",
            "vehicle_id": "0234a3e8-a74e-4d29-ad55-c8d428dd6151",
            "latitude": "15.5952322222",
            "longitude": "73.8714755556",
            "altitude": None,
            "speed": 2,
            "course": None,
            "accuracy": None,
            "engine_on": True,
            "driver_name": "sasuke",
            "driver_number": "234234",
            "driving_licence_number": "3fkkekdfkk4k43",
            "vehicle_number": "xx00xx0000",
            "vehicle_type": None,
            "vehicle_status": None,
            "device": self.gps_device.id,
        }
        self.minimum_valid_data = {
            "location_id": "590d68029ca81c2344818dd8",
            "vehicle_id": "0234a3e8-a74e-4d29-ad55-c8d428dd6151",
            "datetime": "2017-05-06T11:36:30"
        }
        self.create_url = reverse("driver_gps_device_log_create")
        self.update_url = reverse("driver_gps_device_log_update", kwargs={"pk": self.gps_device_log.id})
        self.partial_update_url = reverse("driver_gps_device_log_partial_update", kwargs={"pk": self.gps_device_log.id})
        self.retrieve_url = reverse("driver_gps_device_log_retrieve", kwargs={"pk": self.gps_device_log.id})

    def test_create_gps_device_log_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding latitude field to minimum valid data required
    def test_create_gps_device_log_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_gps_device_log_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_gps_device_log_with_driver(self):
        self.minimum_valid_data["device"] = self.gps_device.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_gps_device_log_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.gps_device_log_data.copy()
        data["datetime"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.gps_device_log_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.gps_device_log_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.gps_device_log_data.copy()
        data["device"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = self.gps_device.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_gps_device_log_with_invalid_request(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_gps_device_log_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_gps_device_log_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"driver_number": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"datetime": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"device": self.gps_device.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_gps_device_log_retrieve",
                                   kwargs={"pk": self.gps_device_log.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TracknovateGPSDeviceTest(DriverSetup):
    """
        Test cases for Tracknovate GPS Device
    """

    def setUp(self):
        super().setUp()
        self.tracknovate_gps_device_data = {
            "updated_on": "2017-07-03T09:30:13.410522",
            "deleted": False,
            "deleted_on": None,
            "phone": "7340660256",
            "sim_number": "351608080820397",
            "vehicle_id": "cg07aw279",
            "driver_name": None,
            "driver_number": None,
            "number_verified": False,
            "current_duration": "<strong style='color:red;'>Halted from last 18 Min </strong>",
            "current_vstatus": "<strong style='color:red;'>Halted</strong>",
            "driving_licence_number": None,
            "vehicle_number": "cg07aw279",
            "vehicle_type": None,
            "vehicle_status": "unloaded",
            "location_time": None,
            "is_active": True,
            "latitude": None,
            "longitude": None,
            "inactive_sms_sent_at": None,
            "driver": self.driver.id,
        }
        self.minimum_valid_data = {
            "vehicle_id": "cg07aw279",
            "phone": "7340660256",
            "sim_number": "351608080820397"
        }
        self.create_url = reverse("driver_tracknovate_gps_device_create")
        self.update_url = reverse("driver_tracknovate_gps_device_update", kwargs={"pk": self.tracknovate_gps_device.id})
        self.partial_update_url = reverse("driver_tracknovate_gps_device_partial_update",
                                          kwargs={"pk": self.tracknovate_gps_device.id})
        self.retrieve_url = reverse("driver_tracknovate_gps_device_retrieve",
                                    kwargs={"pk": self.tracknovate_gps_device.id})

    def test_create_tracknovate_gps_device_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding latitude field to minimum valid data required
    def test_create_tracknovate_gps_device_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_tracknovate_gps_device_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding is_active field to minimum valid data required
    def test_create_tracknovate_gps_device_with_is_active(self):
        self.minimum_valid_data["is_active"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_tracknovate_gps_device_with_driver(self):
        self.minimum_valid_data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tracknovate_gps_device_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.tracknovate_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tracknovate_gps_device_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.tracknovate_gps_device_data.copy()
        data["location_time"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tracknovate_gps_device_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tracknovate_gps_device_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tracknovate_gps_device_data.copy()
        data["driver"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = self.driver.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.tracknovate_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.tracknovate_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.tracknovate_gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.tracknovate_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.tracknovate_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.tracknovate_gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_tracknovate_gps_device_invalid_request(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_update_tracknovate_gps_device_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_tracknovate_gps_device_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.tracknovate_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_tracknovate_gps_device_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"phone": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"location_time": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"driver": self.driver.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_tracknovate_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_tracknovate_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_tracknovate_gps_device_retrieve",
                                   kwargs={"pk": self.tracknovate_gps_device.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TracknovateGPSDeviceLogTest(DriverSetup):
    """
        Test cases for Tracknovate GPS device Log
    """

    def setUp(self):
        super().setUp()
        self.tracknovate_gps_device_log_data = {

            "datetime": "2017-11-02T11:13:18",
            "vehicle_id": "cg07aw279",
            "latitude": "20.6679560000",
            "longitude": "81.4918930000",
            "altitude": "23.2",
            "speed": 0,
            "course": 23.2,
            "accuracy": 12.1,
            "engine_on": False,
            "driver_name": None,
            "driver_number": None,
            "driving_licence_number": None,
            "vehicle_number": "cg07aw279",
            "vehicle_type": None,
            "vehicle_status": None,
            "device": self.tracknovate_gps_device.id,
        }
        self.minimum_valid_data = {
            "vehicle_id": "0234a3e8-a74e-4d29-ad55-c8d428dd6151",
            "datetime": "2017-05-06T11:36:30"
        }
        self.create_url = reverse("driver_tracknovate_gps_device_log_create")
        self.update_url = reverse("driver_tracknovate_gps_device_log_update",
                                  kwargs={"pk": self.tracknovate_gps_device_log.id})
        self.partial_update_url = reverse("driver_tracknovate_gps_device_log_partial_update",
                                          kwargs={"pk": self.tracknovate_gps_device_log.id})
        self.retrieve_url = reverse("driver_tracknovate_gps_device_log_retrieve",
                                    kwargs={"pk": self.tracknovate_gps_device_log.id})

    def test_create_tracknovate_gps_device_log_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding latitude field to minimum valid data required
    def test_create_tracknovate_gps_device_log_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_tracknovate_gps_device_log_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_tracknovate_gps_device_log_with_driver(self):
        self.minimum_valid_data["device"] = self.tracknovate_gps_device.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tracknovate_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.tracknovate_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tracknovate_gps_device_log_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.tracknovate_gps_device_log_data.copy()
        data["datetime"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tracknovate_gps_device_log_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tracknovate_gps_device_log_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tracknovate_gps_device_log_data.copy()
        data["device"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = self.tracknovate_gps_device.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.tracknovate_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.tracknovate_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.tracknovate_gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.tracknovate_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.tracknovate_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.tracknovate_gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_tracknovate_gps_device_log_invalid_request(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_tracknovate_gps_device_log_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_tracknovate_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.tracknovate_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_tracknovate_gps_device_log_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"driver_number": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"datetime": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"device": self.tracknovate_gps_device.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_tracknovate_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_tracknovate_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_tracknovate_gps_device_log_retrieve",
                                   kwargs={"pk": self.tracknovate_gps_device_log.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WaytrackerGPSDeviceTest(DriverSetup):
    """
        Test cases for Waytracker GPS Device

    """

    def setUp(self):
        super().setUp()
        self.waytracker_gps_device_data = {
            "deleted": False,
            "deleted_on": None,
            "vehicle_id": "cg04mb8168",
            "driver_name": "sakura",
            "driver_number": None,
            "number_verified": False,
            "driving_licence_number": None,
            "vehicle_number": "cg04mb8168",
            "vehicle_type": None,
            "vehicle_status": "unloaded",
            "location_time": "2018-04-02T14:17:00",
            "latitude": "21.6293100000",
            "longitude": "81.7553280000",
            "is_active": True,
            "inactive_sms_sent_at": None,
            "driver": self.driver.id,
        }
        self.minimum_valid_data = {
            "vehicle_id": "cg07aw279"

        }
        self.create_url = reverse("driver_waytracker_gps_device_create")
        self.update_url = reverse("driver_waytracker_gps_device_update", kwargs={"pk": self.waytracker_gps_device.id})
        self.partial_update_url = reverse("driver_waytracker_gps_device_partial_update",
                                          kwargs={"pk": self.waytracker_gps_device.id})
        self.retrieve_url = reverse("driver_waytracker_gps_device_retrieve",
                                    kwargs={"pk": self.waytracker_gps_device.id})

    def test_create_waytracker_gps_device_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding latitude field to minimum valid data required
    def test_create_waytracker_gps_device_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_waytracker_gps_device_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding is_active field to minimum valid data required
    def test_create_waytracker_gps_device_with_is_active(self):
        self.minimum_valid_data["is_active"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_waytracker_gps_device_with_driver(self):
        self.minimum_valid_data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_waytracker_gps_device_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.waytracker_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_waytracker_gps_device_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.waytracker_gps_device_data.copy()
        data["location_time"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.waytracker_gps_device_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.waytracker_gps_device_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.waytracker_gps_device_data.copy()
        data["driver"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = self.driver.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.waytracker_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.waytracker_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.waytracker_gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.waytracker_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.waytracker_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.waytracker_gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_waytracker_gps_device_invalid_request(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_waytracker_gps_device_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_waytracker_gps_device_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.waytracker_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_waytracker_gps_device_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"phone": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"location_time": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"driver": self.driver.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_waytracker_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_waytracker_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_waytracker_gps_device_retrieve",
                                   kwargs={"pk": self.waytracker_gps_device.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WaytrackerGPSDeviceLogTest(DriverSetup):
    """
        Test cases for Waytracker GPS Device Log

    """

    def setUp(self):
        super().setUp()
        self.waytracker_gps_device_log_data = {

            "datetime": "2018-03-13T15:31:00",
            "vehicle_id": "cg04lw9448",
            "latitude": "23.1613650000",
            "longitude": "82.0661120000",
            "altitude": None,
            "speed": 10,
            "course": None,
            "accuracy": None,
            "engine_on": True,
            "fuel": "191",
            "nearest_site": "No Site Nearby",
            "nearest_location": " Bartarai-Anuppur-Madhya Pradesh-India(2.36 KM)",
            "idle_time": " 00:00:00",
            "driver_name": None,
            "driver_number": None,
            "driving_licence_number": None,
            "vehicle_number": "cg04lw9448",
            "vehicle_type": None,
            "vehicle_status": "unloaded",
            "device": self.waytracker_gps_device.id,
        }
        self.minimum_valid_data = {
            "vehicle_id": "cg04lw9448",
            "datetime": "2017-05-06T11:36:30"
        }
        self.create_url = reverse("driver_waytracker_gps_device_log_create")
        self.update_url = reverse("driver_waytracker_gps_device_log_update",
                                  kwargs={"pk": self.waytracker_gps_device_log.id})
        self.partial_update_url = reverse("driver_waytracker_gps_device_log_partial_update",
                                          kwargs={"pk": self.waytracker_gps_device_log.id})
        self.retrieve_url = reverse("driver_waytracker_gps_device_log_retrieve",
                                    kwargs={"pk": self.waytracker_gps_device_log.id})

    def test_create_waytracker_gps_device_log_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding latitude field to minimum valid data required
    def test_create_waytracker_gps_device_log_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_waytracker_gps_device_log_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_waytracker_gps_device_log_with_driver(self):
        self.minimum_valid_data["device"] = self.waytracker_gps_device.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_waytracker_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.waytracker_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_waytracker_gps_device_log_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.waytracker_gps_device_log_data.copy()
        data["datetime"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.waytracker_gps_device_log_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.waytracker_gps_device_log_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.waytracker_gps_device_log_data.copy()
        data["device"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = self.waytracker_gps_device.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.waytracker_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.waytracker_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.waytracker_gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.waytracker_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.waytracker_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.waytracker_gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_waytracker_gps_log_device_invalid_request(self):
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

    def test_update_waytracker_gps_device_log_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_waytracker_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.waytracker_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_waytracker_gps_device_log_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"driver_number": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"datetime": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"device": self.waytracker_gps_device.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_waytracker_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_waytracker_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_waytracker_gps_device_log_retrieve",
                                   kwargs={"pk": self.waytracker_gps_device_log.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TempoGoGPSDeviceTest(DriverSetup):
    """
        Test cases for Tempo Go GPS Device

    """

    def setUp(self):
        super().setUp()
        self.tempo_go_gps_device_data = {
            "deleted": False,
            "deleted_on": None,
            "device_id": "155a146d-04c7-4b8b-a6e9-2979d82852ee",
            "imei": "351608084764245",
            "driver_name": "MANPRIT SINGH",
            "driver_number": "9753985454",
            "number_verified": False,
            "driving_licence_number": "CG07-1985-0010553",
            "vehicle_number": "cg07ba5297",
            "vehicle_type": None,
            "vehicle_status": "unloaded",
            "location_time": "2018-06-19T17:05:06.598000",
            "latitude": "23.0725755556",
            "longitude": "82.3849600000",
            "is_active": True,
            "inactive_sms_sent_at": None,
            "driver": self.driver.id,
        }
        self.minimum_valid_data = {
            "imei": "351608084764245",
            "device_id": "155a146d-04c7-4b8b-a6e9-2979d82852ee"

        }
        self.create_url = reverse("driver_tempo_go_gps_device_create")
        self.update_url = reverse("driver_tempo_go_gps_device_update", kwargs={"pk": self.tempo_go_gps_device.id})
        self.partial_update_url = reverse("driver_tempo_go_gps_device_partial_update",
                                          kwargs={"pk": self.tempo_go_gps_device.id})
        self.retrieve_url = reverse("driver_tempo_go_gps_device_retrieve",
                                    kwargs={"pk": self.tempo_go_gps_device.id})

    def test_create_tempo_go_gps_device_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_other_data_format(self):
        pass

    def test_create_tempo_go_gps_device_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["vehicle_number"] = "IN02BJP2021"
        data["imei"] = "123456782"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["vehicle_number"] = "IN02BJP2022"
        data["imei"] = "123456783"
        data["device_id"] = "DE23455555503"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = None
        data["vehicle_number"] = "IN02BJP2020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        data["vehicle_number"] = "IN02BJP2021"
        data["imei"] = "123456782"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/18"
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09:12:18:20:20:300"
        data["vehicle_number"] = "IN02BJP2020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_device_id(self):
        data = self.minimum_valid_data.copy()

        data["device_id"] = "mh2000"
        data["imei"] = "123456783"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["device_id"] = generate_random_string(49)
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456782"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["device_id"] = generate_random_string(50)
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456785"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_device_id(self):
        data = self.minimum_valid_data.copy()

        data["device_id"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device_id"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data["vehicle_number"] = "IN02BJP2019"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_imei(self):
        data = self.minimum_valid_data.copy()

        data["imei"] = "valid1234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["imei"] = generate_random_string(49)
        data["device_id"] = "DE23455555501"
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["imei"] = generate_random_string(50)
        data["vehicle_number"] = "IN02BJP2020"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_tempo_go_gps_device_with_invalid_imei(self):
        data = self.minimum_valid_data.copy()

        data["imei"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_driver_name(self):
        data = self.minimum_valid_data.copy()

        data["driver_name"] = "valid_name"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = generate_random_string(49)
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = generate_random_string(50)
        data["vehicle_number"] = "IN02BJP2021"
        data["imei"] = "123456782"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = None
        data["vehicle_number"] = "IN02BJP2021"
        data["imei"] = "123456783"
        data["device_id"] = "DE23455555503"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_driver_name(self):
        data = self.minimum_valid_data.copy()

        data["driver_name"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_driver_number(self):
        data = self.minimum_valid_data.copy()

        data["driver_number"] = "1800140020"
        data["imei"] = "123456782"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_number"] = "9878787878"
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_number"] = None
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456783"
        data["device_id"] = "DE23455555503"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_driver_number(self):
        data = self.minimum_valid_data.copy()

        data["driver_number"] = "0123456789"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "123456789"
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "12345678911"
        data["vehicle_number"] = "IN02BJP2020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "12345ab678"
        data["vehicle_number"] = "IN02BJP2021"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "invalid123"
        data["vehicle_number"] = "IN02BJP2022"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_driving_licence_number(self):
        data = self.minimum_valid_data.copy()

        data["driving_licence_number"] = "valid123"
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = generate_random_string(19)
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456782"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = generate_random_string(20)
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456783"
        data["device_id"] = "DE23455555503"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = None
        data["vehicle_number"] = "IN02BJP2021"
        data["imei"] = "123456784"
        data["device_id"] = "DE23455555504"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_driving_licence_number(self):
        data = self.minimum_valid_data.copy()

        data["driving_licence_number"] = generate_random_string(21)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = "MH02MUM2018"
        data["imei"] = "123456789"
        data["device_id"] = "DE23455555555"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = "MH-12-bo-2018"
        data["imei"] = "123456788"
        data["device_id"] = "DE23455555554"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = "mh15b-2018"
        data["imei"] = "123456787"
        data["device_id"] = "DE23455555553"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = None
        data["imei"] = "123456786"
        data["device_id"] = "DE23455555552"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = "12MH2018BOM"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = "M12an2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = "2018MH12BOM"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = "SEMI-OPEN-12-TYRES"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = generate_random_string(39)
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = generate_random_string(40)
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456782"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = None
        data["vehicle_number"] = "IN02BJP2021"
        data["imei"] = "123456783"
        data["device_id"] = "DE23455555503"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = generate_random_string(41)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_device_with_valid_vehicle_status(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_status"] = "loading"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "unloading"
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "loaded"
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456783"
        data["device_id"] = "DE23455555503"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "unloaded"
        data["vehicle_number"] = "IN02BJP2021"
        data["imei"] = "123456784"
        data["device_id"] = "DE23455555504"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_vehicle_status(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_status"] = "LoadIng"
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_status"] = None
        data["vehicle_number"] = "IN02BJP2020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_location_time(self):
        data = self.minimum_valid_data.copy()

        data["location_time"] = datetime.now()
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["location_time"] = str(datetime.now())
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456782"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_location_time(self):
        data = self.minimum_valid_data.copy()

        data["location_time"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["location_time"] = "12:Dec:2018:20:45:2331"
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = 1232333.1231
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["longitude"] = 1.1234567891
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456782"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["longitude"] = None
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456783"
        data["device_id"] = "DE23455555503"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["longitude"] = 1.12345678911
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = 1232333.1231
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["latitude"] = 1.1234567891
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456783"
        data["device_id"] = "DE23455555503"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["latitude"] = None
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456784"
        data["device_id"] = "DE23455555504"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["latitude"] = 1.12345678911
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_tempo_go_gps_device_with_valid_inactive_sms_sent_at(self):
        data = self.minimum_valid_data.copy()

        data["inactive_sms_sent_at"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["inactive_sms_sent_at"] = str(datetime.now())
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["inactive_sms_sent_at"] = None
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456781]2"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_inactive_sms_sent_at(self):
        data = self.minimum_valid_data.copy()

        data["inactive_sms_sent_at"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["inactive_sms_sent_at"] = "12-Dec-2018"
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["inactive_sms_sent_at"] = "12-12-2018:20:20:330"
        data["vehicle_number"] = "IN02BJP2020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_driver(self):
        data = self.minimum_valid_data.copy()

        data["driver"] = self.driver.id

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver"] = None
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_driver(self):
        data = self.minimum_valid_data.copy()

        data["driver"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = -12
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = 0
        data["vehicle_number"] = "IN02BJP2020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = 12345678
        data["vehicle_number"] = "IN02BJP2021"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = datetime.now()
        data["vehicle_number"] = "IN02BJP2022"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = 1.32
        data["vehicle_number"] = "IN02BJP2023"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_number_verified(self):
        data = self.minimum_valid_data.copy()

        data["number_verified"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["number_verified"] = True
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["number_verified"] = 0
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456782"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["number_verified"] = 1
        data["vehicle_number"] = "IN02BJP2021"
        data["imei"] = "123456783"
        data["device_id"] = "DE23455555503"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_number_verified(self):
        data = self.minimum_valid_data.copy()

        data["number_verified"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["number_verified"] = -12
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["number_verified"] = None
        data["vehicle_number"] = "IN02BJP2020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_with_valid_is_active(self):
        data = self.minimum_valid_data.copy()

        data["is_active"] = True
        data["imei"] = "123456781"
        data["device_id"] = "DE23455555501"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_active"] = True
        data["vehicle_number"] = "IN02BJP2019"
        data["imei"] = "123456782"
        data["device_id"] = "DE23455555502"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_active"] = 0
        data["vehicle_number"] = "IN02BJP2020"
        data["imei"] = "123456783"
        data["device_id"] = "DE23455555503"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_active"] = 1
        data["vehicle_number"] = "IN02BJP2021"
        data["imei"] = "123456784"
        data["device_id"] = "DE23455555504"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_invalid_is_active(self):
        data = self.minimum_valid_data.copy()

        data["is_active"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["is_active"] = -12
        data["vehicle_number"] = "IN02BJP2019"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["is_active"] = None
        data["vehicle_number"] = "IN02BJP2021"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # Adding latitude field to minimum valid data required
    def test_create_tempo_go_gps_device_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_tempo_go_gps_device_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding is_active field to minimum valid data required
    def test_create_tempo_go_gps_device_with_is_active(self):
        self.minimum_valid_data["is_active"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_tempo_go_gps_device_with_driver(self):
        self.minimum_valid_data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.tempo_go_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.tempo_go_gps_device_data.copy()
        data["location_time"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tempo_go_gps_device_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tempo_go_gps_device_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tempo_go_gps_device_data.copy()
        data["driver"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = self.driver.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.tempo_go_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.tempo_go_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.tempo_go_gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.tempo_go_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.tempo_go_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.tempo_go_gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_tempo_go_gps_device_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_tempo_go_gps_device_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.tempo_go_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_tempo_go_gps_device_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"driver_number": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"location_time": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"driver": self.driver.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_tempo_go_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_tempo_go_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_tempo_go_gps_device_retrieve",
                                   kwargs={"pk": self.tempo_go_gps_device.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TempoGoGPSDeviceLogTest(DriverSetup):
    """
        Test cases for Tempo Go GPS Device Log

    """

    def setUp(self):
        super().setUp()
        self.tempo_go_gps_device_log_data = {

            "gps_log_id": "59a6827a4824d40814649809",
            "datetime": "2017-08-30T14:07:32",
            "vehicle_id": "57240867-e4c3-471a-9d69-d2ccc6284541",
            "latitude": "17.7029022222",
            "longitude": "83.2226755556",
            "speed": 0,
            "driver_name": "prasad rao",
            "driver_number": "8985118722",
            "driving_licence_number": "AP03520458/2005 VZM",
            "vehicle_number": "ap35x7379",
            "vehicle_type": None,
            "vehicle_status": "unloaded",
            "device": self.tempo_go_gps_device.id,
        }
        self.minimum_valid_data = {
            "gps_log_id": "59a6827a4824d40814649809",
            "vehicle_id": "cg04lw9448",
            "datetime": "2017-05-06T11:36:30"
        }
        self.create_url = reverse("driver_tempo_go_gps_device_log_create")
        self.update_url = reverse("driver_tempo_go_gps_device_log_update",
                                  kwargs={"pk": self.tempo_go_gps_device_log.id})
        self.partial_update_url = reverse("driver_tempo_go_gps_device_log_partial_update",
                                          kwargs={"pk": self.tempo_go_gps_device_log.id})
        self.retrieve_url = reverse("driver_tempo_go_gps_device_log_retrieve",
                                    kwargs={"pk": self.tempo_go_gps_device_log.id})

    def test_create_tempo_go_gps_device_log_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_tempo_go_gps_device_log_with_other_data_format(self):
        pass

    def test_create_tempo_go_gps_device_log_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["gps_log_id"] = "asd1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_log_device_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = None
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/18"
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09:12:18:20:20:300"
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_gps_log_id(self):
        data = self.minimum_valid_data.copy()

        data["gps_log_id"] = "valid_log"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gps_log_id"] = generate_random_string(49)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gps_log_id"] = generate_random_string(50)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_gps_log_id(self):
        data = self.minimum_valid_data.copy()

        data["gps_log_id"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gps_log_id"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_datetime(self):
        data = self.minimum_valid_data.copy()

        data["datetime"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["datetime"] = str(datetime.now())
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_datetime(self):
        data = self.minimum_valid_data.copy()

        data["datetime"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["datetime"] = "09/12/18"
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["datetime"] = "09:12:18:20:20:300"
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = None
        data["gps_log_id"] = "asd1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_vehicle_id(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_id"] = generate_random_string(49)
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_id"] = generate_random_string(50)
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_vehicle_id(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_id"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_id"] = None
        data["gps_log_id"] = "asd1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = 1232333.1231
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["longitude"] = 1.1234567891
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["longitude"] = None
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["longitude"] = 1.12345678911
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = 1232333.1231
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["latitude"] = 1.1234567891
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["latitude"] = None
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["latitude"] = 1.12345678911
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_driver_name(self):
        data = self.minimum_valid_data.copy()

        data["driver_name"] = "MyNameIsKhan"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = generate_random_string(49)
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = generate_random_string(50)
        data["gps_log_id"] = "asd1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = None
        data["gps_log_id"] = "asd1203"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_driver_name(self):
        data = self.minimum_valid_data.copy()

        data["driver_name"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_driver_number(self):
        data = self.minimum_valid_data.copy()

        data["driver_number"] = "1800140020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_number"] = "9878787878"
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_number"] = None
        data["gps_log_id"] = "asd1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_driver_number(self):
        data = self.minimum_valid_data.copy()

        data["driver_number"] = "0123456789"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "123456789"
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "12345678911"
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "12345ab678"
        data["gps_log_id"] = "asd1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "invalid123"
        data["gps_log_id"] = "asd1203"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_driving_licence_number(self):
        data = self.minimum_valid_data.copy()

        data["driving_licence_number"] = "dl12ab35844"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = generate_random_string(19)
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = generate_random_string(20)
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_driving_licence_number(self):
        data = self.minimum_valid_data.copy()

        data["driving_licence_number"] = generate_random_string(21)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = "dl12ab5844"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = "MH-12-Bom-2018"
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = "MH-12-B2018"
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = None
        data["gps_log_id"] = "asd1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = "m12bom2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = "12MH2018BOM"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = "2018MH12SP"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_tempo_go_gps_device_with_valid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = "dl12ab35844"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = generate_random_string(39)
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = generate_random_string(40)
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = None
        data["gps_log_id"] = "asd1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = generate_random_string(41)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_vehicle_status(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_status"] = "loading"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "unloading"
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "loaded"
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "unloaded"
        data["gps_log_id"] = "asd1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = None
        data["gps_log_id"] = "asd1203"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_vehicle_status(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_status"] = "LoadIng"
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_speed(self):
        data = self.minimum_valid_data.copy()

        data["speed"] = 40.00
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["speed"] = 60
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["speed"] = None
        data["gps_log_id"] = "asd1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_speed(self):
        data = self.minimum_valid_data.copy()

        data["speed"] = "invalid_speed"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["speed"] = "-12.00"
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tempo_go_gps_device_log_with_valid_device(self):
        data = self.minimum_valid_data.copy()

        data["device"] = self.tempo_go_gps_device.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["device"] = None
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_invalid_device(self):
        data = self.minimum_valid_data.copy()

        data["device"] = self.mahindra_gps_device.id * 1000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = -12
        data["gps_log_id"] = "asd1200"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = 0
        data["gps_log_id"] = "asd1201"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = 1.32
        data["gps_log_id"] = "asd1202"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = "invalid"
        data["gps_log_id"] = "asd1203"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = datetime.now()
        data["gps_log_id"] = "asd1204"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



    # Adding latitude field to minimum valid data required
    def test_create_tempo_go_gps_device_log_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_tempo_go_gps_device_log_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_tempo_go_gps_device_log_with_driver(self):
        self.minimum_valid_data["device"] = self.tempo_go_gps_device.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.tempo_go_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tempo_go_gps_device_log_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.tempo_go_gps_device_log_data.copy()
        data["datetime"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tempo_go_gps_device_log_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tempo_go_gps_device_log_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.tempo_go_gps_device_log_data.copy()
        data["device"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = self.tempo_go_gps_device.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.tempo_go_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.tempo_go_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.tempo_go_gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.tempo_go_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.tempo_go_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.tempo_go_gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_tempo_go_gps_device_log_with_invalid_method(self):
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


    def test_update_tempo_go_gps_device_log_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_tempo_go_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.tempo_go_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_tempo_go_gps_device_log_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"driver_number": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"datetime": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"device": self.tempo_go_gps_device.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_tempo_go_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_tempo_go_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_tempo_go_gps_device_log_retrieve",
                                   kwargs={"pk": self.tempo_go_gps_device_log.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SecuGPSDeviceTest(DriverSetup):
    """
        Test cases for Secu GPS Device

    """

    def setUp(self):
        super().setUp()
        self.secu_gps_device_data = {
            "deleted": False,
            "deleted_on": None,
            "device_id": "359710047339461|CG 07 AX 6237",
            "imei": "359710047339461",
            "driver_name": "CG07BG6237",
            "driver_number": "9039310192",
            "number_verified": False,
            "driving_licence_number": None,
            "vehicle_number": "cg07ax6237",
            "vehicle_type": None,
            "vehicle_status": "unloaded",
            "location_time": "2018-05-04T16:30:02.363044",
            "latitude": "21.2693567000",
            "longitude": "81.5849617000",
            "address": "Ring Road 2, Loha Bazar, Hirapur Raipur, Chhattisgarh 492099, India",
            "status": "\nRunning 7 hours, 13 minutes\n0.00 km/h\nWaiting 7 hours, 13 minutes\n",
            "is_active": True,
            "inactive_sms_sent_at": None,
            "driver": self.driver.id,
        }
        self.minimum_valid_data = {
            "imei": "351608084764245",
            "device_id": "359710047339461|CG 07 AX 6237"

        }
        self.create_url = reverse("driver_secu_gps_device_create")
        self.update_url = reverse("driver_secu_gps_device_update", kwargs={"pk": self.secu_gps_device.id})
        self.partial_update_url = reverse("driver_secu_gps_device_partial_update",
                                          kwargs={"pk": self.secu_gps_device.id})
        self.retrieve_url = reverse("driver_secu_gps_device_retrieve",
                                    kwargs={"pk": self.secu_gps_device.id})

    def test_create_secu_gps_device_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding latitude field to minimum valid data required
    def test_create_secu_gps_device_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_secu_gps_device_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding is_active field to minimum valid data required
    def test_create_secu_gps_device_with_is_active(self):
        self.minimum_valid_data["is_active"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_secu_gps_device_with_driver(self):
        self.minimum_valid_data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_secu_gps_device_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.secu_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_secu_gps_device_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.secu_gps_device_data.copy()
        data["location_time"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.secu_gps_device_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.secu_gps_device_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.secu_gps_device_data.copy()
        data["driver"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = self.driver.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.secu_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.secu_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.secu_gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.secu_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.secu_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.secu_gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_secu_gps_device_invalid_request(self):
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

    def test_update_secu_gps_device_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_secu_gps_device_with_full_valid_data(self):

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.secu_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_secu_gps_device_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"driver_number": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"location_time": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"driver": self.driver.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_secu_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_secu_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_secu_gps_device_retrieve",
                                   kwargs={"pk": self.secu_gps_device.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SecuGPSDeviceLogTest(DriverSetup):
    """
        Test cases for Secu GPS Device Log

    """

    def setUp(self):
        super().setUp()
        self.secu_gps_device_log_data = {

            "datetime": "2017-11-11T20:17:30",
            "vehicle_id": "358511022368256|CG 07 BG 6237",
            "latitude": "23.2915930000",
            "longitude": "83.9134440000",
            "speed": 23.291593,
            "address": None,
            "status": None,
            "driver_name": "CG07BG6237",
            "driver_number": "9039310192",
            "driving_licence_number": "DL09N6785",
            "vehicle_number": "cg07bg6237",
            "vehicle_type": None,
            "vehicle_status": "unloaded",
            "device": self.secu_gps_device.id,
        }
        self.minimum_valid_data = {

            "vehicle_id": "358511022368256|CG 07 BG 6237",
            "datetime": "2017-05-06T11:36:30"
        }
        self.create_url = reverse("driver_secu_gps_device_log_create")
        self.update_url = reverse("driver_secu_gps_device_log_update",
                                  kwargs={"pk": self.secu_gps_device_log.id})
        self.partial_update_url = reverse("driver_secu_gps_device_log_partial_update",
                                          kwargs={"pk": self.secu_gps_device_log.id})
        self.retrieve_url = reverse("driver_secu_gps_device_log_retrieve",
                                    kwargs={"pk": self.secu_gps_device_log.id})

    def test_create_secu_gps_device_log_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding latitude field to minimum valid data required
    def test_create_secu_gps_device_log_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_secu_gps_device_log_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_secu_gps_device_log_with_driver(self):
        self.minimum_valid_data["device"] = self.secu_gps_device.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_secu_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.secu_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_secu_gps_device_log_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.secu_gps_device_log_data.copy()
        data["datetime"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.secu_gps_device_log_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.secu_gps_device_log_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.secu_gps_device_log_data.copy()
        data["device"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = self.secu_gps_device.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.secu_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.secu_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.secu_gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.secu_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.secu_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.secu_gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_secu_gps_device_log_invalid_request(self):
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

    def test_update_secu_gps_device_log_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_secu_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.secu_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_secu_gps_device_log_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"driver_number": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"datetime": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"device": self.secu_gps_device.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_secu_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_secu_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_secu_gps_device_log_retrieve",
                                   kwargs={"pk": self.secu_gps_device_log.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MahindraGPSDeviceTest(DriverSetup):
    """
        Test cases for Mahindra GPS Device

    """

    def setUp(self):
        super().setUp()
        self.mahindra_gps_device_data = {
            "deleted": False,
            "deleted_on": None,
            "device_id": "dh01h9493",
            "imei": None,
            "driver_name": "CG04LX2551 (Mansingh Gond)",
            "driver_number": "7440332415",
            "number_verified": False,
            "driving_licence_number": "CG12/2007/0003982",
            "vehicle_number": "cg04lx2551",
            "vehicle_type": "Non Tipper",
            "vehicle_status": "unloaded",
            "location_time": "2018-06-19T17:15:01.293985",
            "latitude": "21.3792347222",
            "longitude": "81.6620636111",
            "address": None,
            "status": "Running",
            "is_active": True,
            "inactive_sms_sent_at": None,
            "driver": self.driver.id,
        }
        self.minimum_valid_data = {
            "device_id": "dh01h9493"

        }
        self.create_url = reverse("driver_mahindra_gps_device_create")
        self.update_url = reverse("driver_mahindra_gps_device_update", kwargs={"pk": self.mahindra_gps_device.id})
        self.partial_update_url = reverse("driver_mahindra_gps_device_partial_update",
                                          kwargs={"pk": self.mahindra_gps_device.id})
        self.retrieve_url = reverse("driver_mahindra_gps_device_retrieve",
                                    kwargs={"pk": self.mahindra_gps_device.id})

    def test_create_mahindra_gps_device_with_minimum_valid_data(self):

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_other_data_format(self):
        pass

    def test_create_mahindra_gps_device_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["device_id"] = "mh20001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = None
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        data["device_id"] = "mh20001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/18"
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09:12:18:20:20:300"
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_device_id(self):
        data = self.minimum_valid_data.copy()

        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["device_id"] = generate_random_string(49)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["device_id"] = generate_random_string(50)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_device_id(self):
        data = self.minimum_valid_data.copy()

        data["device_id"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device_id"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_imei(self):
        data = self.minimum_valid_data.copy()

        data["imei"] = "valid1234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["imei"] = generate_random_string(49)
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["imei"] = generate_random_string(50)
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["imei"] = None
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_imei(self):
        data = self.minimum_valid_data.copy()

        data["imei"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_driver_name(self):
        data = self.minimum_valid_data.copy()

        data["driver_name"] = "valid_name"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = generate_random_string(49)
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = generate_random_string(50)
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = None
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_driver_name(self):
        data = self.minimum_valid_data.copy()

        data["driver_name"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_driver_number(self):
        data = self.minimum_valid_data.copy()

        data["driver_number"] = "1800140020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_number"] = "9878787878"
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_number"] = None
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_driver_number(self):
        data = self.minimum_valid_data.copy()

        data["driver_number"] = "0123456789"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "123456789"
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "12345678911"
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "12345ab678"
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "invalid123"
        data["device_id"] = "mh2003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_driving_licence_number(self):
        data = self.minimum_valid_data.copy()

        data["driving_licence_number"] = "valid123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = generate_random_string(19)
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = generate_random_string(20)
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = None
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_driving_licence_number(self):
        data = self.minimum_valid_data.copy()

        data["driving_licence_number"] = generate_random_string(21)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = "MH02MUM2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = "MH-12-bo-2018"
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = "mh15b-2018"
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = None
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = "12MH2018BOM"
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = "M12an2018"
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = "2018-BM-12-AAP"
        data["device_id"] = "mh2003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = "SEMI-OPEN-12-TYRES"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = generate_random_string(39)
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = generate_random_string(40)
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = None
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = generate_random_string(41)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_vehicle_status(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_status"] = "loading"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "unloading"
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "loaded"
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "unloaded"
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_vehicle_status(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_status"] = "LoadIng"
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_status"] = None
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_location_time(self):
        data = self.minimum_valid_data.copy()

        data["location_time"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["location_time"] = str(datetime.now())
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_mahindra_gps_device_with_invalid_location_time(self):
        data = self.minimum_valid_data.copy()

        data["location_time"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["location_time"] = "12:Dec:2018:20:45:2331"
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = 1232333.1231
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["longitude"] = 1.1234567891
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["longitude"] = None
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["longitude"] = 1.12345678911
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = 1232333.1231
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["latitude"] = 1.1234567891
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["latitude"] = None
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["latitude"] = 1.12345678911
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = "valid_address"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = generate_random_string(299)
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = generate_random_string(300)
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = None
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = generate_random_string(301)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_mahindra_gps_device_with_valid_status(self):
        data = self.minimum_valid_data.copy()

        data["status"] = "valid_address"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = generate_random_string(299)
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = generate_random_string(300)
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = None
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_status(self):
        data = self.minimum_valid_data.copy()

        data["status"] = generate_random_string(301)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_inactive_sms_sent_at(self):
        data = self.minimum_valid_data.copy()

        data["inactive_sms_sent_at"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["inactive_sms_sent_at"] = str(datetime.now())
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["inactive_sms_sent_at"] = None
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_inactive_sms_sent_at(self):
        data = self.minimum_valid_data.copy()

        data["inactive_sms_sent_at"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["inactive_sms_sent_at"] = "12-Dec-2018"
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["inactive_sms_sent_at"] = "12-12-2018:20:20:330"
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_driver(self):
        data = self.minimum_valid_data.copy()

        data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver"] = None
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_driver(self):
        data = self.minimum_valid_data.copy()

        data["driver"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = -12
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = 0
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = 12345678
        data["device_id"] = "mh2003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = datetime.now()
        data["device_id"] = "mh2004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = 1.32
        data["device_id"] = "mh2005"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_number_verified(self):
        data = self.minimum_valid_data.copy()

        data["number_verified"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["number_verified"] = True
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["number_verified"] = 0
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["number_verified"] = 1
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_number_verified(self):
        data = self.minimum_valid_data.copy()

        data["number_verified"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["number_verified"] = -12
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["number_verified"] = None
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_is_active(self):
        data = self.minimum_valid_data.copy()

        data["is_active"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_active"] = True
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_active"] = 0
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_active"] = 1
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_invalid_is_active(self):
        data = self.minimum_valid_data.copy()

        data["is_active"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["is_active"] = -12
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["is_active"] = None
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # Adding latitude field to minimum valid data required
    def test_create_mahindra_gps_device_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_mahindra_gps_device_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding is_active field to minimum valid data required
    def test_create_mahindra_gps_device_with_is_active(self):
        self.minimum_valid_data["is_active"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_mahindra_gps_device_with_driver(self):
        self.minimum_valid_data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.mahindra_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.mahindra_gps_device_data.copy()
        data["location_time"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.mahindra_gps_device_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.mahindra_gps_device_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.mahindra_gps_device_data.copy()
        data["driver"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver"] = self.driver.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.mahindra_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.mahindra_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.mahindra_gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.mahindra_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.mahindra_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.mahindra_gps_device_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_mahindra_gps_device_with_invalid_method(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_mahindra_gps_device_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_mahindra_gps_device_with_full_valid_data(self):

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.mahindra_gps_device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_mahindra_gps_device_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"driver_number": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"location_time": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"driver": self.driver.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_mahindra_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_mahindra_gps_device(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_mahindra_gps_device_retrieve",
                                   kwargs={"pk": self.mahindra_gps_device.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MahindraGPSDeviceLogTest(DriverSetup):
    """
        Test cases for Mahindra GPS Device Log

    """

    def setUp(self):
        super().setUp()
        self.mahindra_gps_device_log_data = {

            "datetime": "2017-12-30T15:30:00.815272",
            "vehicle_id": "cg04lx2547",
            "latitude": "22.3190652778",
            "longitude": "82.7222097222",
            "speed": 0,
            "fuel_efficiency": "0 KMPL",
            "address": None,
            "status": "Idle",
            "driver_name": "Cg04lx2547",
            "driver_number": "7766084087",
            "driving_licence_number": "JH05/2008/0002195",
            "vehicle_number": "cg04lx2547",
            "vehicle_type": "Non Tipper",
            "vehicle_status": "unloaded",
            "device": self.mahindra_gps_device.id,
        }
        self.minimum_valid_data = {

            "vehicle_id": "358511022368256|CG 07 BG 6237",
            "datetime": "2017-05-06T11:36:30"
        }
        self.create_url = reverse("driver_mahindra_gps_device_log_create")
        self.update_url = reverse("driver_mahindra_gps_device_log_update",
                                  kwargs={"pk": self.mahindra_gps_device_log.id})
        self.partial_update_url = reverse("driver_mahindra_gps_device_log_partial_update",
                                          kwargs={"pk": self.mahindra_gps_device_log.id})
        self.retrieve_url = reverse("driver_mahindra_gps_device_log_retrieve",
                                    kwargs={"pk": self.mahindra_gps_device_log.id})

    def test_create_mahindra_gps_device_log_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_other_data_format(self):
        pass

    def test_create_mahindra_gps_device_log_with_valid_deleted(self):
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

    def test_create_mahindra_gps_log_device_with_invalid_deleted(self):
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

    def test_create_mahindra_gps_device_log_with_valid_deleted_on(self):
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

    def test_create_mahindra_gps_device_log_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09:12:18:20:20:300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_log_with_valid_datetime(self):
        data = self.minimum_valid_data.copy()

        data["datetime"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["datetime"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_datetime(self):
        data = self.minimum_valid_data.copy()

        data["datetime"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["datetime"] = "09/12/18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["datetime"] = "09:12:18:20:20:300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_vehicle_id(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_id"] = generate_random_string(49)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_id"] = generate_random_string(50)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_vehicle_id(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_id"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_id"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_log_with_valid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = 1232333.1231
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["longitude"] = 1.1234567891
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["longitude"] = None
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_longitude(self):
        data = self.minimum_valid_data.copy()

        data["longitude"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["longitude"] = 1.12345678911
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_log_with_valid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = 1232333.1231
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["latitude"] = 1.1234567891
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["latitude"] = None
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_latitude(self):
        data = self.minimum_valid_data.copy()

        data["latitude"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["latitude"] = 1.12345678911
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_fuel_efficiencyd(self):
        data = self.minimum_valid_data.copy()

        data["fuel_efficiency"] = "36%"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["fuel_efficiency"] = generate_random_string(29)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["fuel_efficiency"] = generate_random_string(30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["fuel_efficiency"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_fuel_efficiency(self):
        data = self.minimum_valid_data.copy()

        data["fuel_efficiency"] = generate_random_string(31)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = "valid_address"
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

        data["address"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = generate_random_string(301)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_status(self):
        data = self.minimum_valid_data.copy()

        data["status"] = "valid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = generate_random_string(299)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = generate_random_string(300)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_status(self):
        data = self.minimum_valid_data.copy()

        data["status"] = generate_random_string(301)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_driver_name(self):
        data = self.minimum_valid_data.copy()

        data["driver_name"] = "MyNameIsKhan"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = generate_random_string(49)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = generate_random_string(50)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_driver_name(self):
        data = self.minimum_valid_data.copy()

        data["driver_name"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_log_with_valid_driver_number(self):
        data = self.minimum_valid_data.copy()

        data["driver_number"] = "1800140020"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_number"] = "9878787878"
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_number"] = None
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_driver_number(self):
        data = self.minimum_valid_data.copy()

        data["driver_number"] = "0123456789"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "123456789"
        data["device_id"] = "mh2000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "12345678911"
        data["device_id"] = "mh2001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "12345ab678"
        data["device_id"] = "mh2002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["driver_number"] = "invalid123"
        data["device_id"] = "mh2003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_driving_licence_number(self):
        data = self.minimum_valid_data.copy()

        data["driving_licence_number"] = "dl12ab35844"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = generate_random_string(39)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = generate_random_string(40)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driving_licence_number"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_driving_licence_number(self):
        data = self.minimum_valid_data.copy()

        data["driving_licence_number"] = generate_random_string(41)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_with_valid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = "dl12ab5844"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = "MH-12-BOM-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = "MH12-Jh2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_number"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_vehicle_number(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_number"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = "2018MH12BJP"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_number"] = "M12sp2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_mahindra_gps_device_log_with_valid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = "dl12ab35844"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = generate_random_string(39)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = generate_random_string(40)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_type"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_vehicle_type(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_type"] = generate_random_string(41)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_log_with_valid_vehicle_status(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_status"] = "loading"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "unloading"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "loaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["vehicle_status"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_vehicle_status(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_status"] = "LoadIng"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_log_with_valid_speed(self):
        data = self.minimum_valid_data.copy()

        data["speed"] = 40.00
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["speed"] = 60
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["speed"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_speed(self):
        data = self.minimum_valid_data.copy()

        data["speed"] = "invalid_speed"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["speed"] = "-12.00"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mahindra_gps_device_log_with_valid_device(self):
        data = self.minimum_valid_data.copy()

        data["device"] = self.mahindra_gps_device.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["device"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_invalid_device(self):
        data = self.minimum_valid_data.copy()

        data["device"] = self.mahindra_gps_device.id * 1000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = 1.32
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # Adding latitude field to minimum valid data required
    def test_create_mahindra_gps_device_log_with_latitude(self):
        self.minimum_valid_data["latitude"] = "21.9200000763"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding vehicle_status field to minimum valid data required
    def test_create_mahindra_gps_device_log_with_vehicle_status(self):
        self.minimum_valid_data["vehicle_status"] = "unloaded"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding driver field to minimum valid data required
    def test_create_mahindra_gps_device_log_with_driver(self):
        self.minimum_valid_data["device"] = self.mahindra_gps_device.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.mahindra_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_mahindra_gps_device_log_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = self.mahindra_gps_device_log_data.copy()
        data["datetime"] = "10-09-2015"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.mahindra_gps_device_log_data.copy()
        data["vehicle_status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.mahindra_gps_device_log_data.copy()
        data["latitude"] = "InvalidLatitude"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.mahindra_gps_device_log_data.copy()
        data["device"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["device"] = self.mahindra_gps_device.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.mahindra_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.mahindra_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.mahindra_gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.mahindra_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.mahindra_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.mahindra_gps_device_log_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_mahindra_gps_device_log_with_invalid_method(self):
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

    def test_update_mahindra_gps_device_log_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_mahindra_gps_device_log_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.mahindra_gps_device_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_mahindra_gps_device_log_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"driver_number": "1234567890"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"datetime": "2017-01-28T22:22:30.792000"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"device": self.mahindra_gps_device.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_mahindra_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_mahindra_gps_device_log(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("driver_mahindra_gps_device_log_retrieve",
                                   kwargs={"pk": self.mahindra_gps_device_log.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
