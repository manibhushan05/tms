import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class DynamoGPSTests(APITestCase):

    def setUp(self):
        self.login_url = reverse('login')
        self.dynamogps_device_url = reverse('dynamo_gps_device_create_table')
        self.gps_create_url = reverse('dynamo_gps_device_create_item')

        self.user = User.objects.create_user(username='raviaaho',email='anujapatil@gmail.com',password='trans123')
        self.login_data = self.client.post(self.login_url, {'username': "raviaaho", 'password': 'trans123'}).content

        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = 'Token {}'.format(self.login_data['token'])
        # self.is_active = (('True', '1'), ('False', '0'))
        self.vehicle_status = (
            ('unloaded', 'unloaded'),
            ('loading', 'loading'),
            ('loaded', 'loaded'),
            ('unloading', 'unloading'),)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "deleted" : 1,
            "deleted_on" : "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_number": "MH00AP2000",
            "vehicle_type": "Tata Ace",
            "vehicle_status": 'unloading',
            "location_time": "2008-09-15T15:53:00",
            "address": "Mumbai",
            "is_active": 1,
            "latitude": 33.91,
            "longitude": 24.28}),
                                    content_type = 'application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #self.device_id = response.data['data']['device_id']
        self.device_id = "27"


class GPSDeviceCreateTableTests(DynamoGPSTests):

    """
              Test ID:TS01DY00001
              Created By:Anuja
              Created On:28/01/2019
              Scenario:dynamo-gps-device-location-create-table/
              Status:failure
              Message:Authorization Header
              Status code:400
        """

    def test_GPSDevice_400_Bad_Req(self):
        # Negative test case for creating GPS Device table with no HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response =self.client.post(self.dynamogps_device_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device Table already exist")

        """
               Test ID:TS01DY00002
               Created By:Anuja
               Created On:28/01/2019
               Scenario:dynamo-gps-device-location-create-table/
               Status:failure
               Message:Authorization Header
               Status code:401
        """

    def test_GPSDevice_Create_401_no_header(self):
        # Negative test case for creating GPS Device with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(self.dynamogps_device_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

        """
                Test ID:TS01DY00003
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-create-table/
                Status:failure
                Message:wrong Method
                Status code:405
        """

    def test_GPSDevice_Create_405_Method_Not_Allowed(self):
        # Negative test for creating req with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.dynamogps_device_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        """
                Test ID:TS01DY00004
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-create-table/
                Status:failure
                Message: invalid token
                Status code:401
        """

    def test_GPSDevice_Create_401_wrong_token(self):
        # Negative test case for creating GPS Device table with HTTP Header Authorization and wrong token
        self.token = 'Token 123'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.dynamogps_device_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

class GPSDeviceCreateItemTest(DynamoGPSTests):

    """
                Test ID:TS01DY00006
                Created By:Anuja
                reated On:28/01/2019
                Scenario:dynamo-gps-device-location-create-item/
                Status:failure
                Message: blank gps_device_provider
                Status code:400
    """

    def test_GPSDevice_create_400_blank_GPS(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token and blank gps_provider
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_number": "MH00AP2000",
            "vehicle_type": "Tata Ace",
            "vehicle_status": '',
            "location_time": "2008-09-15T15:53:00",
            "address": "Mumbai",
            "is_active": "1",
            "latitude": 33.91,
            "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['gps_device_provider'][0],
                         "This field may not be blank.")

        """
                    Test ID:TS01DY00007
                    Created By:Anuja
                    Created On:28/01/2019
                    Scenario:dynamo-gps-device-location-create-item/
                    Status:failure
                    Message: created_on must be in valid format
                    Status code:400
        """

    def test_GPSDevice_create_400_wrong_format(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token and created_on field wrong format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "",
            "created_on": "2008-09-15",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_status": 'loaded',
            "location_time": "2008-09-15T15:53:00",
            "address": "Mumbai",
            "is_active": "1",
            "latitude": 33.91,
            "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['created_on'][0],
            "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].")

        """
                 Test ID:TS01DY00008
                 Created By:Anuja
                 Created On:28/01/2019
                 Scenario:dynamo-gps-device-location-create-item/
                 Status:failure
                 Message: wrong vehicle_status
                 Status code:400
        """

    def test_GPSDevice_Create_400_vehicle_status(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token and vehicle status as invalid
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "driving_licence_number": "123456AB",
            "vehicle_number": "MH00AP2000",
            "vehicle_type": "Tata Ace",
            "vehicle_status": 'ongoing',
            "location_time": "2008-09-15T15:53:00",
            "address": "Mumbai",
            "is_active": "1",
            "latitude": 33.91,
            "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['vehicle_status'][0],
                         "\"ongoing\" is not a valid choice.")

        """
            Test ID:TS01DY00009
            Created By:Anuja
            Created On:28/01/2019
            Scenario:dynamo-gps-device-location-create-item/
            Status:failure
            Message: vehicle_status as blank
            Status code:400
         """

    def test_GPSDevice_Create_400_wrong_vehicle_status(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token and vehicle status as null
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_number": "MH00AP2000",
            "vehicle_type": "Tata Ace",
            "vehicle_status": '',
            "location_time": "2008-09-15T15:53:00",
            "address": "Mumbai",
            "is_active": "1",
            "latitude": 33.91,
            "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['vehicle_status'][0],
                         "\"\" is not a valid choice.")

        """
            Test ID:TS01DY00010
            Created By:Anuja
            Created On:28/01/2019
            Scenario:dynamo-gps-device-location-create-item/
            Status:failure
            Message: wrong format of location_time 
            Status code:400
        """

    def test_create_400_Wrong_format(self):
      # Negative test case for creating GPSDevice with HTTP Header Authorization token with field location_time as wrong format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_type": "Tata Ace",
            "vehicle_status": '',
            "location_time": "2008-09-15",
            "is_active": "yes",
            "latitude": 33.91,
            "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['location_time'][0],
        "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].")

        """
             Test ID:TS01DY00011
             Created By:Anuja
             Created On:28/01/2019
             Scenario:dynamo-gps-device-location-create-item/
             Status:failure
             Message: latitude as blank
             Status code:400
         """

    def test_create_400_Blank_latitude(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token with blank latitude
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_number": "MH00AP2000",
            "vehicle_type": "Tata Ace",
            "vehicle_status": '',
            "location_time": "2008-09-15",
            "address": "Mumbai",
            "is_active": "yes",
            "latitude": "",
            "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['latitude'][0],
                         "A valid number is required.")

        """
                 Test ID:TS01DY00012
                 Created By:Anuja
                 Created On:28/01/2019
                 Scenario:dynamo-gps-device-location-create-item/
                 Status:failure
                 Message: wrong format of latitude
                 Status code:400
         """

    def test_create_400_Wrong_latitude(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token with wrong latitude format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_number": "MH00AP2000",
            "vehicle_type": "Tata Ace",
            "vehicle_status": '',
            "location_time": "2008-09-15",
            "address": "Mumbai",
            "is_active": "yes",
            "latitude": 3399,
            "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['latitude'][0],
                         "Ensure that there are no more than 2 digits before the decimal point.")

        """
                 Test ID:TS01DY00013
                 Created By:Anuja
                 Created On:28/01/2019
                 Scenario:dynamo-gps-device-location-create-item/
                 Status:failure
                 Message: longitude as blank
                 Status code:400
         """

    def test_create_400_Blank_longitude(self):
            # Negative test case for creating GPSDevice with HTTP Header Authorization token with blank longitude
            self.client.credentials(HTTP_AUTHORIZATION=self.token)
            response = self.client.post(self.gps_create_url, json.dumps({
                "device_id": "1",
                "created_by": "Anuja",
                "gps_device_provider": "TempoGo",
                "created_on": "2008-09-15T15:53:00",
                "imei": 8765310,
                "driver_name": "Rohit Kumar",
                "driver_number": 8485000217,
                "driving_licence_number": "123456AB",
                "vehicle_number": "MH00AP2000",
                "vehicle_type": "Tata Ace",
                "vehicle_status": '',
                "location_time": "2008-09-15",
                "address": "Mumbai",
                "is_active": "yes",
                "latitude": 33.99,
                "longitude": ""}), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['status'], "failure")
            self.assertEqual(response.data['msg'], "GPS Device not Created")
            self.assertEqual(response.data['data']['longitude'][0],
                             "A valid number is required.")

            """
                    Test ID:TS01DY00014
                    Created By:Anuja
                    Created On:28/01/2019
                    Scenario:dynamo-gps-device-location-create-item/
                    Status:failure
                    Message: wrong formatof longitude
                    Status code:400
            """

    def test_create_400_Wrong_longitude(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token with wrong longitude format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_number": "MH00AP2000",
            "vehicle_type": "Tata Ace",
            "vehicle_status": '',
            "location_time": "2008-09-15",
            "address": "Mumbai",
            "is_active": "yes",
            "latitude": 33.99,
            "longitude": 2490}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['longitude'][0],
                         "Ensure that there are no more than 2 digits before the decimal point.")

        """
                Test ID:TS01DY00015
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-create-item/
                Status:failure
                Message: is_active should be in boolean format
                Status code:400
         """

    def test_create_400_Invalid_choice(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token with is_active as not a boolean
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_number": "MH00AP2000",
            "vehicle_type": "Tata Ace",
            "vehicle_status": '',
            "location_time": "2008-09-15T15:53:00",
            "address": "Mumbai",
            "is_active": "",
            "latitude": 33.91,
            "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['is_active'][0],
                         "\"\" is not a valid boolean.")

        """
             Test ID:TS01DY00016
             Created By:Anuja
             Created On:28/01/2019
             Scenario:dynamo-gps-device-location-create-item/
             Status:failure
             Message: "deleted" field format
             Status code:400
        """

    def test_create_400_deleted_field_format(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token with field "deleted" as blank.
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response =  self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "deleted" : "",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_type": "Tata Ace",
            "vehicle_status": '',
            "location_time": "2008-09-15",
            "is_active": "yes",
            "latitude": 33.91,
            "longitude": 24.28

        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['deleted'][0],
                         "\"\" is not a valid boolean.")

        """
                 Test ID:TS01DY00017
                 Created By:Anuja
                 Created On:28/01/2019
                 Scenario:dynamo-gps-device-location-create-item/
                 Status:failure
                 Message: wrong format of "deleted_on"
                 Status code:400
        """

    def test_create_400_deleted_on_field_format(self):
      # Negative test case for creating GPSDevice with HTTP Header Authorization token with field "deleted_on" wrong format.
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "deleted": 1,
            "deleted_on" : "",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_type": "Tata Ace",
            "vehicle_status": '',
            "location_time": "2008-09-15",
            "is_active": "yes",
            "latitude": 33.91,
            "longitude": 24.28

        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['deleted_on'][0],
        "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].")

        """
                Test ID:TS01DY00018
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-create-item/
                Status:failure
                Message: gps_device_provider could not be exceed than 25 char
                Status code:400
        """

    def test_create_400_invalid_gps_device_provider(self):
            # Negative test case for creating GPSDevice with HTTP Header Authorization token with field
            # gps_device_provider more than 25 character

            self.client.credentials(HTTP_AUTHORIZATION=self.token)
            response = self.client.post(self.gps_create_url, json.dumps({
                "device_id": "1",
                "created_by": "Anuja",
                "gps_device_provider": "ejbdgwu4itlghlvjuigvugtevhgjbdgwu4itlghlvjuigvugtevhgtiuiiugg",
                "created_on": "2008-09-15T15:53:00",
                "location_time": "2008-09-15",
                "address": "Mumbai",
                "is_active": "yes",
                "latitude": 33.99
            }), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['status'], "failure")
            self.assertEqual(response.data['msg'], "GPS Device not Created")
            self.assertEqual(response.data['data']['gps_device_provider'][0],
                             "Ensure this field has no more than 25 characters.")

            """
                    Test ID:TS01DY00019
                    Created By:Anuja
                    Created On:28/01/2019
                    Scenario:dynamo-gps-device-location-create-item/
                    Status:failure
                    Message: driver_number should be in valid mobile number
                    Status code:400
            """

    def test_create_400_driver_number_format(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token and wrong driver_number format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "vehicle_number" : "MH76FD2000",
            "driver_number" : 25687
                        }), content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['driver_number'][0], "Ensure this field has at least 10 characters.",
            "This value does not match the required pattern.")

        """
                Test ID:TS01DY00020
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-create-item/
                Status:failure
                Message: driver_number not exceed than 10 digit
                Status code:400
        """

    def test_create_400_driver_number(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token and wrong driver_number format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "vehicle_number" : "MH76FD2000",
            "driver_number" : 256887657617
                        }), content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['driver_number'][0], "Ensure this field has no more than 10 characters.",
            "This value does not match the required pattern.")

        """
                Test ID:TS01DY00021
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-create-item/
                Status:failure
                Message: vehicle_number should be in valid format
                Status code:400
        """

    def test_Create_400_vehicle_number_format(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token and wrong vehicle_number format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "vehicle_number" : "MH76FD20000"
                        }), content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['vehicle_number'][0], "This value does not match the required pattern.")

        """
                Test ID:TS01DY00022
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-create-item/
                Status:failure
                Message: vehicle_type out of range
                Status code:400
        """

    def test_create_400_vehicle_type(self):
        # Negative test case for creating GPSDevice with HTTP Header Authorization token and wrong vehicle_type format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "vehicle_number": "MH76FD2000",
            "vehicle_type": "iuwyiqwuhviuwyiqwuhvqdjhbsvjhbsvjhbsjvkbgfjh"
                        }), content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Created")
        self.assertEqual(response.data['data']['vehicle_type'][0], "Ensure this field has no more than 40 characters.")

        """
            Test ID:TS01DY00023
            Created By:Anuja
            Created On:28/01/2019
            Scenario:dynamo-gps-device-location-create-item/
            Status:failure
            Message: driving_licence_number out of range
            Status code:400
        """

    def test_create_400_driving_licence_num(self):
            # Negative test case for creating GPSDevice with HTTP Header Authorization token with field
            # driving_licence_num more than 20 character

            self.client.credentials(HTTP_AUTHORIZATION=self.token)
            response = self.client.post(self.gps_create_url, json.dumps({
                "device_id": "1",
                "created_by": "Anuja",
                "gps_device_provider": "TempoGo",
                "created_on": "2008-09-15T15:53:00",
                "imei": 8765310,
                "driver_name": "Rohit Kumar",
                "driver_number": 8485000217,
                "driving_licence_number": "gkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjh",
                "vehicle_number": "MH00AP2000",
                "vehicle_type": "Tata Ace",
                "location_time": "2008-09-15",
                "address": "Mumbai",
                "is_active": "yes",
                "latitude": 33.99}), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['status'], "failure")
            self.assertEqual(response.data['msg'], "GPS Device not Created")
            self.assertEqual(response.data['data']['driving_licence_number'][0],
                             "Ensure this field has no more than 20 characters.")

            """
                    Test ID:TS01DY00024
                    Created By:Anuja
                    Created On:28/01/2019
                    Scenario:dynamo-gps-device-location-create-item/
                    Status:failure
                    Message: driver_name out of range
                    Status code:400
             """

    def test_create_400_driver_name(self):
            # Negative test case for creating GPSDevice with HTTP Header Authorization token with field
            # driver_name more than 50 character

            self.client.credentials(HTTP_AUTHORIZATION=self.token)
            response = self.client.post(self.gps_create_url, json.dumps({
                "device_id": "1",
                "created_by": "Anuja",
                "gps_device_provider": "TempoGo",
                "created_on": "2008-09-15T15:53:00",
                "imei": 8765310,
                "driver_name": "gkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdc",
                "driver_number": 8485000217,
                "driving_licence_number": "786gf",
                "vehicle_number": "MH00AP2000",
                "vehicle_type": "Tata Ace",
                "location_time": "2008-09-15",
                "address": "Mumbai",
                "is_active": "yes",
                "latitude": 33.99
            }), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['status'], "failure")
            self.assertEqual(response.data['msg'], "GPS Device not Created")
            self.assertEqual(response.data['data']['driver_name'][0],
                             "Ensure this field has no more than 50 characters.")

            """
                    Test ID:TS01DY00025
                    Created By:Anuja
                    Created On:28/01/2019
                    Scenario:dynamo-gps-device-location-create-item/
                    Status:failure
                    Message: imei out of range
                    Status code:400
            """

    def test_create_400_invalid_imei(self):
            # Negative test case for creating GPSDevice with HTTP Header Authorization token with field
            # imei more than 40 character

            self.client.credentials(HTTP_AUTHORIZATION=self.token)
            response = self.client.post(self.gps_create_url, json.dumps({
                "device_id": "1",
                "created_by": "Anuja",
                "gps_device_provider": "TempoGo",
                "created_on": "2008-09-15T15:53:00",
                "imei": "gkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdc",
                "driver_name": "Sopan",
                "driver_number": 8485000217,
                "driving_licence_number": "786gf",
                "vehicle_number": "MH00AP2000",
                "vehicle_type": "Tata Ace",
                "location_time": "2008-09-15",
                "address": "Mumbai",
                "is_active": "yes",
                "latitude": 33.99
               }), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['status'], "failure")
            self.assertEqual(response.data['msg'], "GPS Device not Created")
            self.assertEqual(response.data['data']['imei'][0],
                             "Ensure this field has no more than 40 characters.")

            """
                    Test ID:TS01DY00025
                    Created By:Anuja
                    Created On:28/01/2019
                    Scenario:dynamo-gps-device-location-create-item/
                    Status:failure
                    Message: address out of range
                    Status code:400
            """

    def test_create_400_invalid_address(self):
            # Negative test case for creating GPSDevice with HTTP Header Authorization token with field
            # imei more than 40 character

            self.client.credentials(HTTP_AUTHORIZATION=self.token)
            response = self.client.post(self.gps_create_url, json.dumps({
                "device_id": "1",
                "created_by": "Anuja",
                "gps_device_provider": "TempoGo",
                "created_on": "2008-09-15T15:53:00",
                "imei": "ighcfnb2124",
                "driver_name": "Sopan",
                "driver_number": 8485000217,
                "driving_licence_number": "786gf",
                "vehicle_number": "MH00AP2000",
                "vehicle_type": "Tata Ace",
                "location_time": "2008-09-15",
                "address": "gkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdc",
                "is_active": "yes",
                "latitude": 33.99
                }), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['status'], "failure")
            self.assertEqual(response.data['msg'], "GPS Device not Created")
            self.assertEqual(response.data['data']['address'][0],
                             "Ensure this field has no more than 500 characters.")

            """
                    Test ID:TS01DY00026
                    Created By:Anuja
                    Created On:28/01/2019
                    Scenario:dynamo-gps-device-location-create-item/
                    Status:failure
                    Message: wrong method
                    Status code:405
             """

    def test_GPSDevice_Create_405_Method_Not_Allowed(self):
        # Negative test for creating item with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.gps_create_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        """
                Test ID:TS01DY00027
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-create-item/
                Status:failure
                Message: wrong content_type
                Status code:415
         """

    def test_GPSDevice_Create_415(self):
        # Negative test case for creating req with HTTP Header Authorization token and wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "created_by": "Anuja",
            "gps_device_provider": "",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217
        }), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(response.data['detail'], "Unsupported media type \"application/pdf\" in request.")

        """
                Test ID:TS01DY00028
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-create-item/
                Status:failure
                Message: No Authorization header
                Status code:401
        """
    def test_GPSDevice_Create_401_no_header(self):
        # Negative test case for creating GPS Device with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(self.dynamogps_device_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

        """
                Test ID:TS01DY00029
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-create-item/
                Status:failure
                Message: Wrong token
                Status code:401
        """

    def test_GPSDevice_CreateItem_401_wrong_token(self):
        # Negative test case for creating GPS Device, HTTP Header Authorization with wrong token
        self.token = 'Token 123'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.dynamogps_device_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

        """
                Test ID:TS01DY00031
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-create-item/
                Status:failure
                Message: GPS device item created
                Status code:201
        """

    def test_GPSDevice_201_created(self):
        # Positive test case for creating GPS Device Item with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.gps_create_url, json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_number": "MH00AP2000",
            "vehicle_type": "Tata Ace",
            "vehicle_status": 'loading',
            "location_time": "2008-09-15T15:53:00",
            "address": "Mumbai",
            "is_active": "1",
            "latitude": 33.91,
            "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Dynamo GPS Device Item Created")

class GPSDeviceTests(DynamoGPSTests):


    """
             Test ID:TS01DY00032
             Created By:Anuja
             Created On:28/01/2019
             Scenario:dynamo-gps-device-location-get-item/<device_id>/
             Status:success
             Message: GPS device item Retrieved
             Status code:200
     """
    
    def test_get_GPSDevice_200(self):
        # Positive test case for getting GPS Device with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/dynamo-gps-device-location-get-item/{}/".format(self.device_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Dynamo GPS Device Item Retrieved")

    """
            Test ID:TS01DY00033
            Created By:Anuja
            Created On:28/01/2019
            Scenario:dynamo-gps-device-location-get-item/<device_id>/
            Status:failure
            Message: Wrong Method
            Status code:405
     """

    def test_get_GPSDevice_405(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-get-item/{}/".format(self.device_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data['detail'], "Method \"POST\" not allowed.")

        """
              Test ID:TS01DY00034
              Created By:Anuja
              Created On:28/01/2019
              Scenario:dynamo-gps-device-location-get-item/<device_id>/
              Status:failure
              Message: No Authorization Header
              Status code:401
         """

    def test_GPSDevice_get_401_no_header(self):
        # Negative test case for getting GPS Device with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/dynamo-gps-device-location-get-item/{}/".format(self.device_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

        """
                  Test ID:TS01DY00035
                  Created By:Anuja
                  Created On:28/01/2019
                  Scenario:dynamo-gps-device-location-get-item/<device_id>/
                  Status:failure
                  Message: wrong content_type
                  Status code:415
         """

    def test_GPSDevice_get_wrong_content_type(self):
        # Negative test case for getting GPS Device with HTTP Header Authorization token and wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/dynamo-gps-device-location-get-item/{}/".format(self.device_id),
                                   content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Wrong Content Type. Must be application/json")

        """
                Test ID:TS01DY00036
                Created By:Anuja
                Created On:28/01/2019
                Scenario:dynamo-gps-device-location-get-item/<device_id>/
                Status:failure
                Message: Expired Token
                Status code:401
        """

    def test_GPSDevice_get_401_wrong_token(self):
        # Negative test case for getting GPS Device with no HTTP Header Authorization with wrong token
        self.token = 'Token 123'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/dynamo-gps-device-location-get-item/{}/".format(self.device_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

        """
              Test ID:TS01DY00037
              Created By:Anuja
              Created On:28/01/2019
              Scenario:dynamo-gps-device-location-get-item/<wrong device_id>/
              Status:failure
              Message: Wrong device_id
              Status code:400
         """

    def test_GPSDevice_get_400_wrong_ID(self):
        # Negative test case for getting GPS Device with HTTP Header Authorization token and wrong device_id
        self.device_id = "49"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/dynamo-gps-device-location-get-item/{}/".format(self.device_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Dynamo GPS Device Item Not Found")

class GPSDeviceDeleteTests(DynamoGPSTests):

    """
            Test ID:TS01DY00038
            Created By:Anuja
            Created On:28/01/2019
            Scenario:dynamo-gps-device-location-delete-item/<device_id>/
            Status:success
            Message: GPS device get deleted
            Status code:200
     """
    def test_delete_GPSDevice_200(self):
        # Positive test for deleting GPS device Device
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-delete-item/{}/".format(self.device_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Dynamo GPS Device Item Deleted")

    """
                   Test ID:TS01DY00039
                   Created By:Anuja
                   Created On:28/01/2019
                   Scenario:dynamo-gps-device-location-delete-item/<device_id>/
                   Status:failure
                   Message: No authorization Header
                   Status code:401
    """

    def test_delete_GPSDevice_401_no_header(self):
        # Negative test case for  deleting GPSDevice with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/dynamo-gps-device-location-delete-item/{}/".format(self.device_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

        """
                       Test ID:TS01DY00040
                       Created By:Anuja
                       Created On:28/01/2019
                       Scenario:dynamo-gps-device-location-delete-item/<device_id>/
                       Status:failure
                       Message: No authorization Header
                       Status code:401
        """

    def test_delete_GPSDevice_401_wrong_token(self):
        # Negative test case for  deleting GPSDevice with wrong token
        self.token = 'Token 123'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-delete-item/{}/".format(self.device_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

        """
                       Test ID:TS01DY00041
                       Created By:Anuja
                       Created On:28/01/2019
                       Scenario:dynamo-gps-device-location-delete-item/<device_id>/
                       Status:failure
                       Message: Wrong Method
                       Status code:405
        """

    def test_delete_GPSDevice_405_wrong_method(self):
        # Negative test for destroying GPSDevice with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/dynamo-gps-device-location-delete-item/{}/".format(self.device_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        """
             Test ID:TS01DY00042
             Created By:Anuja
             Created On:28/01/2019
             Scenario:dynamo-gps-device-location-delete-item/<wrong device_id>/
             Status:failure
             Message: Wrong device_id
             Status code:400
        """

    def test_delete_GPSDevice_400_wrong_id(self):
        # Negative test for deleting GPS device with wrong_id
        self.device_id = 88
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-delete-item/{}/".format(self.device_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], "GPS Device not Found")


class GPSDeviceUpdateTests(DynamoGPSTests):

    """
         Test ID:TS01DY00043
         Created By:Anuja
         Created On:28/01/2019
         Scenario:dynamo-gps-device-location-update-item/<device_id>/
         Status:failure
         Message: Wrong method
         Status code:405
    """
    def test_update_GPSDevice_405_wrong_method(self):
        # Negative test for destroying GPSDevice with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id))
        self.assertEqual(response.status_code,status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01DY00044
         Created By:Anuja
         Created On:28/01/2019
         Scenario:dynamo-gps-device-location-update-item/<device_id>/
         Status:failure
         Message: No authorization Header
         Status code:401
    """

    def test_update_GPSDevice_401_noAuthorization_header(self):
        # Negative test for updating GPSDevice with no authorization header
        self.client.credentials()
        response = self.client.get("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
             Test ID:TS01DY00045
             Created By:Anuja
             Created On:28/01/2019
             Scenario:dynamo-gps-device-location-update-item/<device_id>/
             Status:failure
             Message: Wrong token
             Status code:401
    """

    def test_update_GPSDevice_401_worng_token(self):
            # Negative test case for  updating GPSDevice with wrong token
        self.token = 'Token 123'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
           Test ID:TS01DY00046
           Created By:Anuja
           Created On:28/01/2019
           Scenario:dynamo-gps-device-location-update-item/<device_id>/
           Status:failure
           Message: Content type not json
           Status code:415
    """

    def test_update_GPSDevice_415_unsupported_mediaType(self):
        # Negative test case for updating GPSDevice with HTTP Header Authorization token and wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),json.dumps({
            "device_id": "1",
            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_number": "MH00AP2000",
            "vehicle_type": "Tata Ace",
            "vehicle_status": 'loading',
            "location_time": "2008-09-15T15:53:00",
            "address": "Mumbai",
            "is_active": "1",
            "latitude": 33.91,
            "longitude": 24.28}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
              Test ID:TS01DY00047
              Created By:Anuja
              Created On:28/01/2019
              Scenario:dynamo-gps-device-location-update-item/<device_id>/
              Status:failure
              Message: created_by as blank
              Status code:400
     """

    def test_update_GPSDevice_400_Bad_Req(self):
        # Negative test for updating GPSDevice with field created_by is blank
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "",
                                        "gps_device_provider": "TempoGo",
                                        "created_on": "2008-09-15T15:53:00",
                                        "vehicle_status": 'loading',
                                        "location_time": "2008-09-15T15:53:00",
                                        "address": "Mumbai",
                                        "is_active": "1",
                                        "latitude": 33.91,
                                        "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['created_by'][0], "This field may not be blank.")

        """
           Test ID:TS01DY00048
           Created By:Anuja
           Created On:28/01/2019
           Scenario:dynamo-gps-device-location-update-item/<device_id>/
           Status:failure
           Message: blank gps_device_provider
           Status code:400
        """

    def test_update_GPSDevice_400_device_provider(self):
        # Negative test for updating GPSDevice with field gps_device_provider as blank
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "AAHO",
                                        "gps_device_provider": "",
                                        "created_on": "2008-09-15T15:53:00",
                                        "vehicle_status": 'loading',
                                        "location_time": "2008-09-15T15:53:00",
                                        "is_active": "1",
                                        "latitude": 33.91,
                                        "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['gps_device_provider'][0], "This field may not be blank.")

        """
             Test ID:TS01DY00049
             Created By:Anuja
             Created On:28/01/2019
             Scenario:dynamo-gps-device-location-update-item/<device_id>/
             Status:failure
             Message: blank created_on 
             Status code:400
        """

    def test_update_GPSDevice_400(self):
        # Negative test for updating GPSDevice with field created_on as wrong format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "AAHO",
                                        "gps_device_provider": "Google",
                                        "created_on": "",
                                        "vehicle_status": 'loading',
                                        "location_time": "2008-09-15T15:53:00",
                                        "is_active": "1",
                                        "latitude": 33.91,
                                        "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['created_on'][0], "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].")

    """
           Test ID:TS01DY00050
           Created By:Anuja
           Created On:28/01/2019
           Scenario:dynamo-gps-device-location-update-item/<device_id>/
           Status:failure
           Message: blank vehicle_status
           Status code:400
    """

    def test_update_GPSDevice_400_vehicle_status(self):
        # Negative test for updating GPSDevice with field vehicle_status as blank
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "AAHO",
                                        "gps_device_provider": "Google",
                                        "created_on": "2008-09-15T15:53:0",
                                        "vehicle_status": '',
                                        "location_time": "2008-09-15T15:53:00",
                                        "is_active": "1",
                                        "latitude": 33.91,
                                        "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['vehicle_status'][0], "\"\" is not a valid choice.")

    """
            Test ID:TS01DY00051
            Created By:Anuja
            Created On:28/01/2019
            Scenario:dynamo-gps-device-location-update-item/<device_id>/
            Status:failure
            Message: Invalid vehicle_status
            Status code:400
    """

    def test_update_GPSDevice_400_vehicle(self):
        # Negative test for updating GPSDevice with field vehicle_status as invalid
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "AAHO",
                                        "gps_device_provider": "Google",
                                        "created_on": "2008-09-15T15:53:0",
                                        "vehicle_status": 'load',
                                        "location_time": "2008-09-15T15:53:00",
                                        "is_active": "1",
                                        "latitude": 33.91,
                                        "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['vehicle_status'][0], "\"load\" is not a valid choice.")

    """
           Test ID:TS01DY00052
           Created By:Anuja
           Created On:28/01/2019
           Scenario:dynamo-gps-device-location-update-item/<device_id>/
           Status:failure
           Message: blank location_time
           Status code:400
    """

    def test_update_GPSDevice_400_location_time(self):
        # Negative test for updating GPSDevice with field location_time as blank
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "AAHO",
                                        "gps_device_provider": "Google",
                                        "created_on": "2008-09-15T15:53:0",
                                        "vehicle_status": 'loaded',
                                        "location_time": "",
                                        "is_active": "1",
                                        "latitude": 33.91,
                                        "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['location_time'][0], "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].")

        """
               Test ID:TS01DY00053
               Created By:Anuja
               Created On:28/01/2019
               Scenario:dynamo-gps-device-location-update-item/<device_id>/
               Status:failure
               Message: is_active should be boolean
               Status code:400
        """

    def test_update_GPSDevice_400_is_active(self):
        # Negative test for updating GPSDevice with field is_active as invalid boolean
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "AAHO",
                                        "gps_device_provider": "Google",
                                        "created_on": "2008-09-15T15:53:0",
                                        "vehicle_status": 'loaded',
                                        "location_time": "2008-09-15T15:53:00",
                                        "is_active": 3,
                                        "latitude": 33.91,
                                        "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['is_active'][0], "\"3\" is not a valid boolean.")

        """
             Test ID:TS01DY00054
             Created By:Anuja
             Created On:28/01/2019
             Scenario:dynamo-gps-device-location-update-item/<device_id>/
             Status:failure
             Message: blank latitude
             Status code:400
        """

    def test_update_GPSDevice_400_blank_latitude(self):
        # Negative test for updating GPSDevice with field latitude as blank
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "AAHO",
                                        "gps_device_provider": "Google",
                                        "created_on": "2008-09-15T15:53:0",
                                        "vehicle_status": 'loaded',
                                        "location_time": "2008-09-15T15:53:00",
                                        "is_active": "1",
                                        "latitude": "",
                                        "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['latitude'][0], "A valid number is required.")

        """
               Test ID:TS01DY00055
               Created By:Anuja
               Created On:28/01/2019
               Scenario:dynamo-gps-device-location-update-item/<device_id>/
               Status:failure
               Message: Invalid latitude
               Status code:400
        """

    def test_update_GPSDevice_400_invalid_latitude(self):
        # Negative test for updating GPSDevice with field latitude as invalid
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "AAHO",
                                        "gps_device_provider": "Google",
                                        "created_on": "2008-09-15T15:53:0",
                                        "vehicle_status": 'loaded',
                                        "location_time": "2008-09-15T15:53:00",
                                        "is_active": "1",
                                        "latitude": 3391,
                                        "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['latitude'][0], "Ensure that there are no more than 2 digits before the decimal point.")

        """
             Test ID:TS01DY00056
             Created By:Anuja
             Created On:28/01/2019
             Scenario:dynamo-gps-device-location-update-item/<device_id>/
             Status:failure
             Message: Blank longitude
             Status code:400
        """

    def test_update_GPSDevice_400_blank_longitude(self):
        # Negative test for updating GPSDevice with field longitude as blank
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "AAHO",
                                        "gps_device_provider": "Google",
                                        "created_on": "2008-09-15T15:53:0",
                                        "vehicle_status": 'loaded',
                                        "location_time": "2008-09-15T15:53:00",
                                        "is_active": "1",
                                        "latitude": 33.91,
                                        "longitude": ""}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['longitude'][0], "A valid number is required.")

        """
            Test ID:TS01DY00057
            Created By:Anuja
            Created On:28/01/2019
            Scenario:dynamo-gps-device-location-update-item/<device_id>/
            Status:failure
            Message: Invalid longitude
            Status code:400
        """

    def test_update_GPSDevice_400_invalid_longitude(self):
        # Negative test for updating GPSDevice with field longitude as wrong fomat
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "AAHO",
                                        "gps_device_provider": "Google",
                                        "created_on": "2008-09-15T15:53:0",
                                        "vehicle_status": 'loaded',
                                        "location_time": "2008-09-15T15:53:00",
                                        "is_active": "1",
                                        "latitude": 33.91,
                                        "longitude": 2428}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['longitude'][0], "Ensure that there are no more than 2 digits before the decimal point.")

        """
             Test ID:TS01DY00058
             Created By:Anuja
             Created On:28/01/2019
             Scenario:dynamo-gps-device-location-update-item/<device_id>/
             Status:failure
             Message: deleted should be boolean
             Status code:400
        """

    def test_update_400_deleted_field_format_boolean(self):
        # Negative test case for updating GPSDevice with HTTP Header Authorization token with field "deleted" as blank.
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response =  self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({

            "created_by": "Anuja",
            "deleted" : "",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_type": "Tata Ace",
            "location_time": "2008-09-15",
            "is_active": "yes",
            "latitude": 33.91,
            "longitude": 24.28

        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['deleted'][0],
                         "\"\" is not a valid boolean.")

        """
              Test ID:TS01DY00059
              Created By:Anuja
              Created On:28/01/2019
              Scenario:dynamo-gps-device-location-update-item/<device_id>/
              Status:failure
              Message: Invalid field deleted_on
              Status code:400
        """

    def test_update_400_deleted_on_field_format_datetime(self):
      # Negative test case for updating GPSDevice with HTTP Header Authorization token with field "deleted_on" as blank.
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({

            "created_by": "Anuja",
            "deleted": 1,
            "deleted_on" : "2019-01-15T15:53:10",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "driver_number": 8485000217,
            "driving_licence_number": "123456AB",
            "vehicle_type": "Tata Ace",
            "location_time": "2008-09-15",
            "is_active": "yes",
            "latitude": 33.91,
            "longitude": 24.28

        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        #self.assertEqual(response.data['data']['deleted_on'][0], "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].")

        """
             Test ID:TS01DY00060
             Created By:Anuja
             Created On:28/01/2019
             Scenario:dynamo-gps-device-location-update-item/<device_id>/
             Status:failure
             Message: driver_name out of range
             Status code:400
        """
    def test_update_400_driver_name(self):
            # Negative test case for updating GPSDevice with HTTP Header Authorization token with field
            # driver_name more than 50 character

            self.client.credentials(HTTP_AUTHORIZATION=self.token)
            response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({

                "created_by": "Anuja",
                "gps_device_provider": "TempoGo",
                "created_on": "2008-09-15T15:53:00",
                "imei": 8765310,
                "driver_name": "gkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdc",
                "driver_number": 8485000217,
                "driving_licence_number": "786gf",
                "vehicle_number": "MH00AP2000",
                "vehicle_type": "Tata Ace",
                "location_time": "2008-09-15",
                "address": "Mumbai",
                "is_active": "yes",
                "latitude": 33.99,
                "longitude": ""}), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['status'], "failure")
            self.assertEqual(response.data['msg'], "GPS Device not Updated")
            self.assertEqual(response.data['data']['driver_name'][0],
                             "Ensure this field has no more than 50 characters.")

            """
                  Test ID:TS01DY00061
                  Created By:Anuja
                  Created On:28/01/2019
                  Scenario:dynamo-gps-device-location-update-item/<device_id>/
                  Status:failure
                  Message: driving_licence_number out of range
                  Status code:400
            """

    def test_update_400_driving_licence_num(self):
            # Negative test case for updating GPSDevice with HTTP Header Authorization token with field
            # driving_licence_num more than 20 character

            self.client.credentials(HTTP_AUTHORIZATION=self.token)
            response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({

                "created_by": "Anuja",
                "gps_device_provider": "TempoGo",
                "created_on": "2008-09-15T15:53:00",
                "imei": 8765310,
                "driver_name": "Rohit Kumar",
                "driver_number": 8485000217,
                "driving_licence_number": "gkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdc",
                "vehicle_number": "MH00AP2000",
                "vehicle_type": "Tata Ace",
                "location_time": "2008-09-15",
                "address": "Mumbai",
                "is_active": "yes",
                "latitude": 33.99,
                "longitude": ""}), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['status'], "failure")
            self.assertEqual(response.data['msg'], "GPS Device not Updated")
            self.assertEqual(response.data['data']['driving_licence_number'][0],
                             "Ensure this field has no more than 20 characters.")

            """
                 Test ID:TS01DY00062
                 Created By:Anuja
                 Created On:28/01/2019
                 Scenario:dynamo-gps-device-location-update-item/<device_id>/
                 Status:failure
                 Message: address out of range
                 Status code:400
            """

    def test_update_400_invalid_address(self):
            # Negative test case for updating GPSDevice with HTTP Header Authorization token with field
            # imei more than 40 character

            self.client.credentials(HTTP_AUTHORIZATION=self.token)
            response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({

                "created_by": "Anuja",
                "gps_device_provider": "TempoGo",
                "created_on": "2008-09-15T15:53:00",
                "imei": "ighcfnb2124",
                "driver_name": "Sopan",
                "driver_number": 8485000217,
                "driving_licence_number": "786gf",
                "vehicle_number": "MH00AP2000",
                "vehicle_type": "Tata Ace",
                "location_time": "2008-09-15",
                "address": "gkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdcgkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdc",
                "is_active": "yes",
                "latitude": 33.99,
                "longitude": ""}), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['status'], "failure")
            self.assertEqual(response.data['msg'], "GPS Device not Updated")
            self.assertEqual(response.data['data']['address'][0],
                             "Ensure this field has no more than 500 characters.")

            """
                   Test ID:TS01DY00063
                   Created By:Anuja
                   Created On:28/01/2019
                   Scenario:dynamo-gps-device-location-update-item/<device_id>/
                   Status:failure
                   Message: address out of range
                   Status code:400
            """

    def test_update_400_invalid_imei(self):
            # Negative test case for updating GPSDevice with HTTP Header Authorization token with field
            # imei more than 40 character

            self.client.credentials(HTTP_AUTHORIZATION=self.token)
            response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({

                "created_by": "Anuja",
                "gps_device_provider": "TempoGo",
                "created_on": "2008-09-15T15:53:00",
                "imei": "gkjghjkhgjhbjhgjhjkjbkjjwqhggkjghjkhgjhbjhgjhjkjbkjjwqhgfgyibhjcdygfebhjghebjdbhdcfgyibhjcdygfebhjghebjdbhdc",
                "driver_name": "Sopan",
                "driver_number": 8485000217,
                "driving_licence_number": "786gf",
                "vehicle_number": "MH00AP2000",
                "vehicle_type": "Tata Ace",
                "location_time": "2008-09-15",
                "address": "Mumbai",
                "is_active": "yes",
                "latitude": 33.99,
                "longitude": ""}), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['status'], "failure")
            self.assertEqual(response.data['msg'], "GPS Device not Updated")
            self.assertEqual(response.data['data']['imei'][0],
                             "Ensure this field has no more than 40 characters.")

            """
                   Test ID:TS01DY00064
                   Created By:Anuja
                   Created On:28/01/2019
                   Scenario:dynamo-gps-device-location-update-item/<device_id>/
                   Status:failure
                   Message: gps_device_provider out of range
                   Status code:400
            """

    def test_update_400_invalid_gps_device_provider(self):
            # Negative test case for updating GPSDevice with HTTP Header Authorization token with field
            # gps_device_provider more than 25 character

            self.client.credentials(HTTP_AUTHORIZATION=self.token)
            response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({

                "created_by": "Anuja",
                "gps_device_provider": "ejbdgwu4itlghlvjuigvugtevhgjbdgwu4itlghlvjuigvugtevhgtiuiiugg",
                "created_on": "2008-09-15T15:53:00",
                "location_time": "2008-09-15",
                "address": "Mumbai",
                "is_active": "yes",
                "latitude": 33.99
            }), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['status'], "failure")
            self.assertEqual(response.data['msg'], "GPS Device not Updated")
            self.assertEqual(response.data['data']['gps_device_provider'][0],
                             "Ensure this field has no more than 25 characters.")

            """
                    Test ID:TS01DY00065
                    Created By:Anuja
                    Created On:28/01/2019
                    Scenario:dynamo-gps-device-location-update-item/<device_id>/
                    Status:failure
                    Message: driver_number out of range
                    Status code:400
            """

    def test_update_400_driver_number_format(self):
        # Negative test case for updating GPSDevice with HTTP Header Authorization token and wrong driver_number format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({

            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "vehicle_number" : "MH76FD2000",
            "driver_number" : 25687
                        }), content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['driver_number'][0], "Ensure this field has at least 10 characters.",
            "This value does not match the required pattern.")

        """
                   Test ID:TS01DY00066
                   Created By:Anuja
                   Created On:28/01/2019
                   Scenario:dynamo-gps-device-location-update-item/<device_id>/
                   Status:failure
                   Message: driver_number out of range
                   Status code:400
        """

    def test_update_400_driver_number(self):
        # Negative test case for updating GPSDevice with HTTP Header Authorization token and wrong driver_number format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({

            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "vehicle_number" : "MH76FD2000",
            "driver_number" : 256887657617
                        }), content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['driver_number'][0], "Ensure this field has no more than 10 characters.",
            "This value does not match the required pattern.")

        """
                 Test ID:TS01DY00067
                 Created By:Anuja
                 Created On:28/01/2019
                 Scenario:dynamo-gps-device-location-update-item/<device_id>/
                 Status:failure
                 Message: Invalid vehicle_number format
                 Status code:400
        """

    def test_update_400_vehicle_number_format(self):
        # Negative test case for updating GPSDevice with HTTP Header Authorization token and wrong vehicle_number format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({

            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "vehicle_number" : "MH76FD20000"
                        }), content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['vehicle_number'][0], "This value does not match the required pattern.")

        """
               Test ID:TS01DY00068
               Created By:Anuja
               Created On:28/01/2019
               Scenario:dynamo-gps-device-location-update-item/<device_id>/
               Status:failure
               Message: vehicle_type out of range
               Status code:400
        """

    def test_update_400_vehicle_type(self):
        # Negative test case for updating GPSDevice with HTTP Header Authorization token and wrong vehicle_type format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({

            "created_by": "Anuja",
            "gps_device_provider": "TempoGo",
            "created_on": "2008-09-15T15:53:00",
            "imei": 8765310,
            "driver_name": "Rohit Kumar",
            "vehicle_number": "MH76FD2000",
            "vehicle_type": "iuwyiqwuhviuwyiqwuhvqdjhbsvjhbsvjhbsjvkbgfjh"
                        }), content_type='application/json')

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "GPS Device not Updated")
        self.assertEqual(response.data['data']['vehicle_type'][0], "Ensure this field has no more than 40 characters.")


        """
                Test ID:TS01DY00069
                Created By:Anuja
                Created On:04/02/2019
                Scenario:dynamo-gps-device-location-update-item/<wrong_device_id>/
                Status:success
                Message: Device id 8756 does not exists
                Status code:400
        """

    def test_update_wrong_device_id(self):
        # Negative test case for updating GPSDevice with HTTP Header Authorization token and wrong device_id
        self.device_id = 8756
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id), json.dumps({
            "address": "Andheri East",
            "vehicle_number": "CV56RT7856",
            "driving_licence_number": "iut76",
            "is_active": 1,
            "latitude": 23,
            "longitude": 47

         }), content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Device id 8756 does not exists")

        """
               Test ID:TS01DY00070
               Created By:Anuja
               Created On:28/01/2019
               Scenario:dynamo-gps-device-location-update-item/<device_id>/
               Status:success
               Message: GPS device item updated
               Status code:202
        """

    def test_update_GPSDevice_202(self):
        # Positive test case for updating GPSDevice with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/dynamo-gps-device-location-update-item/{}/".format(self.device_id),
                                    json.dumps({
                                        "created_by": "Ashok",
                                        "gps_device_provider": "TempoGo",
                                        "created_on": "2008-09-15T15:53:00",
                                        "vehicle_status": 'loading',
                                        "location_time": "2008-09-15T15:53:00",
                                        "address": "Mumbai",
                                        "is_active": "1",
                                        "vehicle_number" : "MH00DF3030",
                                        "latitude": 33.91,
                                        "longitude": 24.28}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Dynamo GPS Device Item Updated")
