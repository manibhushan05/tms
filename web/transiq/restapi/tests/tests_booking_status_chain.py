import json

from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import Profile
from restapi.models import BookingStatuses


class BookingStatusChainTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.bookingstatuschainlist_url = reverse('booking_status_chain_list/')
        self.bookingstatuschaincreate_url = reverse('booking_status_chain_create/')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harshadasawant89@gmail.com',
                                             password='abc12345')
        Profile.objects.create(
            user=self.user,
            name='John_Doe',
            phone='9619125174',
        )

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'abc12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = 'Token {}'.format(self.login_data['token'])

        self.bookingstatus = mommy.make(BookingStatuses, status='lr_generated')
        self.bookingstatus_id = self.bookingstatus.id

        self.primarypreceded = mommy.make(BookingStatuses, status='loaded')
        self.primarypreceded_id = self.primarypreceded.id

        self.primarysucceeded = mommy.make(BookingStatuses, status='unloaded')
        self.primarysucceeded_id= self.primarysucceeded.id

        self.secondarypreceded = mommy.make(BookingStatuses, status='loaded')
        self.secondarypreceded_id = self.primarypreceded.id

        self.secondarysucceeded = mommy.make(BookingStatuses, status='advance_paid')
        self.secondarysucceeded_id = self.primarysucceeded.id

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.bookingstatuschain_id = response.data['data']['id']


class BookingStatusChainCreateTests(BookingStatusChainTests):
    def setUp(self):
        super().setUp()

        self.bookingstatus = mommy.make(BookingStatuses, status='lr_generated')
        self.bookingstatus_id = self.bookingstatus.id

        self.primarypreceded = mommy.make(BookingStatuses, status='loaded')
        self.primarypreceded_id = self.primarypreceded.id

        self.primarysucceeded = mommy.make(BookingStatuses, status='unloaded')
        self.primarysucceeded_id = self.primarysucceeded.id

        self.secondarypreceded = mommy.make(BookingStatuses, status='loaded')
        self.secondarypreceded_id = self.primarypreceded.id

        self.secondarysucceeded = mommy.make(BookingStatuses, status='advance_paid')
        self.secondarysucceeded_id = self.primarysucceeded.id

    """
          Test ID:TS01TD00140
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-status-chain-create/
          Status:failure
          Message:wrong method
          Status code:405
     """

    def test_booking_status_create_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.bookingstatuschaincreate_url,
                                   {"booking_status_id": self.bookingstatus_id,
                                    "primary_preceded_booking_status_id": self.primarypreceded_id,
                                    "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                    "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                    "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                    "level": "primary"},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00141
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-status-chain-create/
          Status:failure
          Message:no header
          Status code:401
     """

    def test_booking_status_create_401_no_header(self):
        self.client.credentials()
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    {"booking_status_id": self.bookingstatus_id,
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                     "level": "primary"},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00142
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-status-chain-create/
          Status:failure
          Message:expired header
          Status code:401
     """

    def test_booking_status_create_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    {"booking_status_id": self.bookingstatus_id,
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                     "level": "primary"},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00142
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-status-chain-create/
          Status:failure
          Message:wrong token
          Status code:401
     """

    def test_booking_status_create_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                     "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00143
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-create/
         Status:failure
         Message:wrong content type
         Status code:415
    """

    def test_booking_status_create_415_header_with_wrong_content_type(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
         Test ID:TS01TD00144
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-create/
         Status:failure
         Message:blank body
         Status code:400
    """

    def test_booking_status_create_400_blank_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_id'][0], "This field is required.")
        self.assertEqual(response.data['level'][0], "This field is required.")
        self.assertEqual(response.data['primary_preceded_booking_status_id'][0], "This field is required.")
        self.assertEqual(response.data['primary_succeeded_booking_status_id'][0], "This field is required.")
        self.assertEqual(response.data['secondary_preceded_booking_status_id'][0], "This field is required.")
        self.assertEqual(response.data['secondary_succeeded_booking_status_id'][0], "This field is required.")

    """
         Test ID:TS01TD00145
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-create/
         Status:failure
         Message:blank booking status id
         Status code:400
    """

    def test_booking_status_create_400_blank_booking_status_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": "",
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                     "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_id'][0], "A valid integer is required.")

    """
         Test ID:TS01TD00146
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-create/
         Status:failure
         Message:corrupt body
         Status code:400
    """

    def test_booking_status_create_400_corrupt_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": "jdksdjk",
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": "hjgdhgsd",
                                     "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['primary_succeeded_booking_status_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['secondary_succeeded_booking_status_id'][0], "A valid integer is required.")

    """
         Test ID:TS01TD00147
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-create/
         Status:failure
         Message:wrong booking status id
         Status code:400
    """

    def test_booking_status_create_400_wrong_booking_status_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    {"booking_status_id": 6000,
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                     "level": "primary"},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
         Test ID:TS01TD00148
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-create/
         Status:failure
         Message:duplicate data
         Status code:400
    """

    def test_booking_status_chain_create_400_duplicate_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
         Test ID:TS01TD00149
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-create/
         Status:success
         Message:chain create
         Status code:201
    """

    def test_booking_status_chain_create_201(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain Created")

class BookingStatusChainRetrieveTests(BookingStatusChainTests):

    """
         Test ID:TS01TD00160
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-retreive/
         Status:failure
         Message:wrong method
         Status code:405
    """

    def test_booking_status_chain_retrieve_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-status-chain-retrieve/{}/".format(self.bookingstatuschain_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01TD00161
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-retreive/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_booking_status_chain_retrieve_401_no_header(self):
        self.client.credentials()
        response = self.client.get("/api/booking-status-chain-retrieve/{}/".format(self.bookingstatuschain_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01TD00162
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-retreive/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_booking_status_chain_retrieve_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/booking-status-chain-retrieve/{}/".format(self.bookingstatuschain_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00162
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-retreive/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_booking_status_chain_retrieve_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/booking-status-chain-retrieve/{}/".format(self.bookingstatuschain_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00163
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-retreive/
         Status:failure
         Message:wrong id
         Status code:404
    """

    def test_booking_status_chain_retrieve_404_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bookingstatuschain_id = 10000
        response = self.client.get("/api/booking-status-chain-retrieve/{}/".format(bookingstatuschain_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
         Test ID:TS01TD00164
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-retreive/
         Status:success
         Message:retreived
         Status code:200
    """

    def test_booking_status_chain_retrieve_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-status-chain-retrieve/{}/".format(self.bookingstatuschain_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain Retrieved")


class BookingStatusChainUpdateTests(BookingStatusChainTests):

    """
         Test ID:TS01TD00150
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-update/
         Status:failure
         Message:wrong method
         Status code:405
    """

    def test_booking_status_update_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-status-chain-update/{}/".format(self.bookingstatuschain_id),
                                   {"booking_status_id": self.bookingstatus_id,
                                    "primary_preceded_booking_status_id": self.primarypreceded_id,
                                    "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                    "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                    "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                    "level": "primary"},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01TD00151
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-update/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_booking_status_update_401_no_header(self):
        self.client.credentials()
        response = self.client.post("/api/booking-status-chain-update/{}/".format(self.bookingstatuschain_id),
                                    {"booking_status_id": self.bookingstatus_id,
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                     "level": "primary"},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01TD00152
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-update/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_booking_status_update_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-status-chain-update/{}/".format(self.bookingstatuschain_id),
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                     "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00152
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-update/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_booking_status_update_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-status-chain-update/{}/".format(self.bookingstatuschain_id),
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                     "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00153
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-update/
         Status:failure
         Message:wrong content type
         Status code:415
    """

    def test_booking_status_update_415_header_with_wrong_content_type(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-status-chain-update/{}/".format(self.bookingstatuschain_id),
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
         Test ID:TS01TD00154
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-update/
         Status:failure
         Message:blank body
         Status code:400
    """

    def test_booking_status_updatete_400_blank_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-status-chain-update/{}/".format(self.bookingstatuschain_id),
                                    json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_id'][0], "This field is required.")
        self.assertEqual(response.data['level'][0], "This field is required.")
        self.assertEqual(response.data['primary_preceded_booking_status_id'][0], "This field is required.")
        self.assertEqual(response.data['primary_succeeded_booking_status_id'][0], "This field is required.")
        self.assertEqual(response.data['secondary_preceded_booking_status_id'][0], "This field is required.")
        self.assertEqual(response.data['secondary_succeeded_booking_status_id'][0], "This field is required.")

    """
         Test ID:TS01TD00155
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-update/
         Status:failure
         Message:blank booking status id
         Status code:400
    """

    def test_booking_status_update_400_blank_booking_status_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-status-chain-update/{}/".format(self.bookingstatuschain_id),
                                    json.dumps({"booking_status_id": "",
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                     "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_id'][0], "A valid integer is required.")

    """
         Test ID:TS01TD00156
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-update/
         Status:failure
         Message:corrupt body
         Status code:400
    """

    def test_booking_status_update_400_corrupt_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-status-chain-update/{}/".format(self.bookingstatuschain_id),
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": "jdksdjk",
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": "hjgdhgsd",
                                     "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['primary_succeeded_booking_status_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['secondary_succeeded_booking_status_id'][0], "A valid integer is required.")

    """
         Test ID:TS01TD00157
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-update/
         Status:failure
         Message:wrong booking status id
         Status code:400
    """

    def test_booking_status_update_400_wrong_booking_status_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-status-chain-update/{}/".format(self.bookingstatuschain_id),
                                    {"booking_status_id": 6000,
                                     "primary_preceded_booking_status_id": self.primarypreceded_id,
                                     "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                     "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                     "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                     "level": "primary"},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
         Test ID:TS01TD00158
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-update/
         Status:failure
         Message:wrong id
         Status code:400
    """

    def test_booking_status_chain_update_400_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bookingstatuschain_id = 10000
        response = self.client.post("/api/booking-status-chain-update/{}/".format(bookingstatuschain_id),
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "BookingStatusChain Doesn't exists")

    """
         Test ID:TS01TD00159
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-update/
         Status:success
         Message:updated
         Status code:201
    """

    def test_booking_status_chain_update_202(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-status-chain-update/{}/".format(self.bookingstatuschain_id),
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain Updated")


class BookingStatusChainDestroyTests(BookingStatusChainTests):

    """
         Test ID:TS01TD00165
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-destroy/<Valid ID>/
         Status:failure
         Message:wrong method
         Status code:405
    """

    def test_booking_status_chain_destroy_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-status-chain-destroy/{}/".format(self.bookingstatuschain_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01TD00166
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-destroy/<Valid ID>/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_booking_status_chain_destroy_401_no_header(self):
        self.client.credentials()
        response = self.client.post("/api/booking-status-chain-destroy/{}/".format(self.bookingstatuschain_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01TD00167
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-destroy/<Valid ID>/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_booking_status_chain_destroy_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-status-chain-destroy/{}/".format(self.bookingstatuschain_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00167
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-destroy/<Valid ID>/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_booking_status_chain_destroy_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-status-chain-destroy/{}/".format(self.bookingstatuschain_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00168
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-destroy/<Valid ID>/
         Status:failure
         Message:wrong id
         Status code:404
    """

    def test_booking_status_chain_destroy_404_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bookingstatuschain_id = 1000
        response = self.client.post("/api/booking-status-chain-destroy/{}/".format(bookingstatuschain_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
         Test ID:TS01TD00169
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-destroy/<Valid ID>/
         Status:failure
         Message:destroy
         Status code:200
    """

    def test_booking_status_chain_destroy_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-status-chain-destroy/{}/".format(self.bookingstatuschain_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain Deleted")


class BookingStatusChainListTests(BookingStatusChainTests):
    def setUp(self):
        super().setUp()

        self.bookingstatus = mommy.make(BookingStatuses, status='lr_generated')
        self.bookingstatus_id = self.bookingstatus.id

        self.primarypreceded = mommy.make(BookingStatuses, status='loaded')
        self.primarypreceded_id = self.primarypreceded.id

        self.primarysucceeded = mommy.make(BookingStatuses, status='unloaded')
        self.primarysucceeded_id = self.primarysucceeded.id

        self.secondarypreceded = mommy.make(BookingStatuses, status='loaded')
        self.secondarypreceded_id = self.primarypreceded.id

        self.secondarysucceeded = mommy.make(BookingStatuses, status='advance_paid')
        self.secondarysucceeded_id = self.primarysucceeded.id

    """
         Test ID:TS01TD00170
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:failure
         Message:wrong method
         Status code:405
    """

    def test_booking_status_chain_list_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschainlist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01TD00171
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_booking_status_chain_list_401_no_header(self):
        self.client.credentials()
        response = self.client.get(self.bookingstatuschainlist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01TD00172
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_booking_status_chain_list_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.bookingstatuschainlist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00172
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_booking_status_chain_list_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.bookingstatuschainlist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00173
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:success
         Message:booking status chain list
         Status code:200
    """

    def test_booking_status_chain_list_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.bookingstatuschainlist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain List")

    """
         Test ID:TS01TD00174
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:success
         Message:booking status chain list search with valid data
         Status code:200
    """

    def test_booking_status_chain_list_200_search_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employeeroles_id = response.data['data']['id']

        response = self.client.get("/api/booking-status-chain-list/?search=lr_generated",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data'][0]['booking_status']
        self.assertEqual(data, 'Lr Generated')

        response = self.client.get("/api/booking-status-chain-list/?search=primary",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data'][0]['level']
        self.assertEqual(data, 'primary')

        response = self.client.get("/api/booking-status-chain-list/?search={}".format(employeeroles_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data'][0]['id']
        self.assertEqual(data, employeeroles_id)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain List")

    """
         Test ID:TS01TD00175
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:success
         Message:booking status chain list search with invalid data
         Status code:200
    """

    def test_booking_status_chain_list_200_search_with_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-status-chain-list/?search=hjgsas",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data, [])

        response = self.client.get("/api/booking-status-chain-list/?search=svgahm",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data, [])

        response = self.client.get("/api/booking-status-chain-list/?search=100000",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data, [])
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain List")

    """
         Test ID:TS01TD00176
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:success
         Message:booking status chain list valid id
         Status code:200
    """

    def test_booking_status_chain_list_200_valid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employeeroles_id = response.data['data']['id']

        response = self.client.get("/api/booking-status-chain-list/?id={}".format(employeeroles_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data'][0]['id']
        self.assertEqual(data, employeeroles_id)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain List")

    """
         Test ID:TS01TD00177
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:success
         Message:booking status chain list invalid id
         Status code:200
    """

    def test_booking_status_chain_list_200_invalid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-status-chain-list/?id=28829",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data, [])
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain List")

    """
         Test ID:TS01TD00178
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:success
         Message:booking status chain list valid booking status
         Status code:200
    """

    def test_booking_status_chain_list_200_valid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get("/api/booking-status-chain-list/?booking_status=lr_generated",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data'][0]['booking_status']
        self.assertEqual(data, 'Lr Generated')
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain List")

    """
         Test ID:TS01TD00179
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:success
         Message:booking status chain list invalid booking status
         Status code:200
    """

    def test_booking_status_chain_list_200_invalid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-status-chain-list/?booking_status=udhuedlie",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data, [])
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain List")

    """
         Test ID:TS01TD00180
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:success
         Message:booking status chain list valid level
         Status code:200
    """

    def test_booking_status_chain_list_200_valid_level(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuschaincreate_url,
                                    json.dumps({"booking_status_id": self.bookingstatus_id,
                                                "primary_preceded_booking_status_id": self.primarypreceded_id,
                                                "primary_succeeded_booking_status_id": self.primarysucceeded_id,
                                                "secondary_preceded_booking_status_id": self.secondarypreceded_id,
                                                "secondary_succeeded_booking_status_id": self.secondarysucceeded_id,
                                                "level": "primary"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get("/api/booking-status-chain-list/?level=primary",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data'][0]['level']
        self.assertEqual(data, 'primary')
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain List")

    """
         Test ID:TS01TD00181
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-status-chain-list/
         Status:success
         Message:booking status chain list invalid level
         Status code:200
    """

    def test_booking_status_chain_list_200_invalid_level(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-status-chain-list/?level=hjghdbs",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data, [])
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Status Chain List")








