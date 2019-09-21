import json

from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import GeoLocatedData
from authentication.models import Profile
from restapi.models import BookingStatuses, BookingStatusChain, BookingStatusesMapping
from sme.models import Sme
from team.models import ManualBooking, Invoice
from utils.models import AahoOffice, State, City


class BookingStatusMappingTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.bookingstatusmappinglist_url = reverse('booking_statuses_mapping_list/')
        self.bookingstatusmappingcreate_url = reverse('booking_statuses_mapping_create/')

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

        self.bookingstatuschain = mommy.make(BookingStatusChain, booking_status=self.bookingstatus)
        self.bookingstatus_chain_id = self.bookingstatuschain.id

        self.aahooffice = mommy.make(AahoOffice)
        self.aahooffice_id = self.aahooffice.id

        self.State = mommy.make(State, name="Tamil Nadu")
        self.state = self.State.name

        self.City = mommy.make(City, name="Tiruchirappalli", state=self.State)
        self.city = self.City.name

        self.Location = mommy.make(GeoLocatedData, country="India", district="Tiruchirappalli")
        self.country = self.Location.country
        self.district = self.Location.district

        self.sme = mommy.make(Sme, aaho_office=self.aahooffice, name=self.user)

        self.manualbooking = mommy.make(ManualBooking, make_m2m=True, source_office=self.aahooffice,
                                        invoice_number='AH1908914')
        self.manualbooking_id = self.manualbooking.id

        self.invoice = mommy.make(Invoice, make_m2m=True, bookings=[self.manualbooking], customer_fk=self.sme)
        self.invno = self.invoice.invoice_number

        self.bookingstatusmapping = mommy.make(BookingStatusesMapping, manual_booking=self.manualbooking,
                                               booking_status_chain=self.bookingstatuschain)
        self.booking_status_mapping_id = self.bookingstatusmapping.id


class BookingStatusMappingCreate(BookingStatusMappingTests):

    def test_booking_statuses_mapping_create_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.bookingstatusmappingcreate_url,
                                   {"booking_status_chain_id": self.bookingstatus_chain_id,
                                    "manual_booking_id": self.manualbooking_id,
                                    "booking_stage": "in_progress"},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_statuses_mapping_401_no_header(self):
        # Negative test with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(self.bookingstatusmappingcreate_url,
                                    {"booking_status_chain_id": self.bookingstatus_chain_id,
                                     "manual_booking_id": self.manualbooking_id,
                                     "booking_stage": "in_progress"}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    def test_booking_statuses_mapping_401_expired_token(self):
        # Negative test case for booking status mapping with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.bookingstatusmappingcreate_url,
                                    {"booking_status_chain_id": self.bookingstatus_chain_id,
                                     "manual_booking_id": self.manualbooking_id,
                                     "booking_stage": "in_progress"}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    def test_booking_statuses_mapping_401_wrong_token(self):
        # Negative test case for booking status mapping with expired/logged out HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65dasdfdhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.bookingstatusmappingcreate_url,
                                    {"booking_status_chain_id": self.bookingstatus_chain_id,
                                     "manual_booking_id": self.manualbooking_id,
                                     "booking_stage": "in_progress"}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    def test_booking_statuses_mapping_415_wrong_content_type(self):
        # Negative test case for booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": self.bookingstatus_chain_id,
                                                "manual_booking_id": self.manualbooking_id,
                                                "booking_stage": "in_progress"}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_booking_statuses_mapping_400_empty_body(self):
        # Negative test case for booking status mapping with empty body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusmappingcreate_url,
                                    json.dumps({
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")
        self.assertEqual(response.data['data']['booking_status_chain_id'][0], "This field is required.")
        self.assertEqual(response.data['data']['manual_booking_id'][0], "This field is required.")
        self.assertEqual(response.data['data']['booking_stage'][0], "This field is required.")

    def test_booking_statuses_mapping_400_empty_fields(self):
        # Negative test case for booking status mapping with empty fields
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": "",
                                                "manual_booking_id": "",
                                                "booking_stage": ""
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")
        self.assertEqual(response.data['data']['booking_status_chain_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['data']['manual_booking_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['data']['booking_stage'][0], "\"\" is not a valid choice.")

    def test_booking_statuses_mapping_400_corrupt_fields(self):
        # Negative test case for booking status mapping with corrupt
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": "fgdsf",
                                                "manual_booking_id": "fgg",
                                                "booking_stage": "gdsfd"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")
        self.assertEqual(response.data['data']['booking_status_chain_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['data']['manual_booking_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['data']['booking_stage'][0], "\"gdsfd\" is not a valid choice.")

    def test_booking_statuses_mapping_400_non_existent_booking_status(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": 411,
                                                "manual_booking_id": 8069,
                                                "booking_stage": "in_process"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_statuses_mapping_400_non_existent_manualbooking(self):
        # Negative test case for booking status mapping with corrupt
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": 3,
                                                "manual_booking_id": 811069,
                                                "booking_stage": "in_process"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_statuses_mapping_create_200_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": self.bookingstatus_chain_id,
                                                "manual_booking_id": self.manualbooking_id,
                                                "booking_stage": "in_progress"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BookingStatusMappingUpdateTests(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_update_401_no_header(self):
        # Negative test for updating booking status mapping with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-mapping-update/{}/".format(self.booking_status_mapping_id),
                                    json.dumps({"booking_status_chain_id": 1,
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_update_401_expired_header(self):
        # Negative test case for updating booking status mapping with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-update/{}/".format(self.booking_status_mapping_id),
                                    json.dumps({"booking_status_chain_id": 1,
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_update_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-mapping-update/{}/".format(self.booking_status_mapping_id),
                                    json.dumps({"booking_status_chain_id": 1,
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_update_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-update/{}/".format(self.booking_status_mapping_id),
                                   json.dumps({"booking_status_chain_id": 1,
                                               "manual_booking_id": 231,
                                               "booking_stage": "in_progress"
                                               }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_statuses_mapping_update_415_wrong_content_type(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update/{}/".format(self.booking_status_mapping_id),
                                    json.dumps({"booking_status_chain_id": 1,
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
                   Test ID:TS01AH00074
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong id
                   Status code:400
    """

    def test_booking_status_update_400_body_empty(self):
        # Negative test for updating user category with empty body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update/{}/".format(self.booking_status_mapping_id),
                                    json.dumps({
                                    }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_chain_id'][0], "This field is required.")
        self.assertEqual(response.data['manual_booking_id'][0], "This field is required.")
        self.assertEqual(response.data['booking_stage'][0], "This field is required.")

    """
           Test ID:TS01AH00076
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category empty
           Status code:400
    """

    def test_booking_status_update_400_body_fields_blank(self):
        # Negative test case for updating booking status with body blank
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update/{}/".format(self.booking_status_mapping_id),
                                    json.dumps({"booking_status_chain_id": "",
                                                "manual_booking_id": "",
                                                "booking_stage": ""}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_chain_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['manual_booking_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['booking_stage'][0], "\"\" is not a valid choice.")

    """
           Test ID:TS01AH00077
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category more than 15 characters
           Status code:401
    """

    def test_booking_status_update_400_body_fields_corrupt(self):
        # Negative test case for updating booking status with body corrupt
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update/{}/".format(self.booking_status_mapping_id),
                                    json.dumps({"booking_status_chain_id": "sg",
                                                "manual_booking_id": "dfg",
                                                "booking_stage": "dg"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_chain_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['manual_booking_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['booking_stage'][0], "\"dg\" is not a valid choice.")

    def test_booking_statuses_mapping_update_400_non_existent_booking_status(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update/{}/".format(self.booking_status_mapping_id),
                                    json.dumps({"booking_status_chain_id": 411,
                                                "manual_booking_id": 8069,
                                                "booking_stage": "in_process"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_statuses_mapping_update_400_non_existent_manualbooking(self):
        # Negative test case for booking status mapping with non existent manual booking
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update/{}/".format(self.booking_status_mapping_id),
                                    json.dumps({"booking_status_chain_id": 3,
                                                "manual_booking_id": 811069,
                                                "booking_stage": "in_process"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_statuses_mapping_update_400_invalid_id(self):
        # Negative test case for booking status mapping with invalid id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 100000
        response = self.client.post("/api/booking-statuses-mapping-update/{}/".format(id),
                                    json.dumps({"booking_status_chain_id": 3,
                                                "manual_booking_id": 811069,
                                                "booking_stage": "in_process"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "BookingStatusesMapping Doesn't exists")

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_statuses_mapping_update_202_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update/{}/".format(self.booking_status_mapping_id),
                                    json.dumps({"booking_status_chain_id": self.bookingstatus_chain_id,
                                                "manual_booking_id": self.manualbooking_id,
                                                "booking_stage": "done"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Updated")


class BookingStatusMappingRetreiveTests(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_retreive_401_no_header(self):
        # Negative test for updating booking status mapping with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/booking-statuses-mapping-retrieve/{}/".format(self.booking_status_mapping_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_retreive_401_expired_header(self):
        # Negative test case for updating booking status mapping with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/booking-statuses-mapping-retrieve/{}/".format(self.booking_status_mapping_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_retreive_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/booking-statuses-mapping-retrieve/{}/".format(self.booking_status_mapping_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_retreive_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-retrieve/{}/".format(self.booking_status_mapping_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_statuses_mapping_retreive_404_invalid_id(self):
        # Negative test case for booking status mapping with invalid id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 100000
        response = self.client.get("/api/booking-statuses-mapping-retrieve/{}/".format(id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_statuses_mapping_retreive_200_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-retrieve/{}/".format(self.booking_status_mapping_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Retrieved")


class BookingStatusMappingDestroyTests(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_destroy_401_no_header(self):
        # Negative test for updating booking status mapping with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-mapping-destroy/{}/".format(self.booking_status_mapping_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_destroy_401_expired_header(self):
        # Negative test case for updating booking status mapping with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-destroy/{}/".format(self.booking_status_mapping_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_destroy_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-mapping-destroy/{}/".format(self.booking_status_mapping_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_destroy_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-destroy/{}/".format(self.booking_status_mapping_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_statuses_mapping_retreive_404_invalid_id(self):
        # Negative test case for booking status mapping with invalid id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 100000
        response = self.client.post("/api/booking-statuses-mapping-destroy/{}/".format(id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_statuses_mapping_retreive_200_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-destroy/{}/".format(self.booking_status_mapping_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Deleted")


class BookingStatusMappingListTests(BookingStatusMappingTests):
    """
               Test ID:TS01TD00087
               Created By:Hari
               Created On:13/12/2018
               Scenario:employee-roles-mapping-list/
               Status:failure
               Message:wrong method
               Status code:405
    """

    def test_booking_status_mapping_list_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusmappinglist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
               Test ID:TS01TD00088
               Created By:Hari
               Created On:13/12/2018
               Scenario:employee-roles-mapping-list/
               Status:failure
               Message:no header
               Status code:401
    """

    def test_booking_status_mapping_list_401_no_header(self):
        self.client.credentials()
        response = self.client.get(self.bookingstatusmappinglist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00089
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_booking_status_mapping_list_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.bookingstatusmappinglist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00089
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_booking_status_mapping_list_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.bookingstatusmappinglist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00090
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:success
          Message:employee roles mapping list
          Status code:200
    """

    def test_booking_status_mapping_list_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.bookingstatusmappinglist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping List")

    # Continue from here
    """
           Test ID:TS01TD00091
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles search by name
           Status code:200
     """

    def test_booking_status_mapping_list_200_search_by_valid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-list/?search=3",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping List")

    """
           Test ID:TS01TD00092
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles search by employee status
           Status code:200
    """

    def test_booking_status_mapping_list_200_search_by_invalid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-list/?search=1122",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping List")

    """
           Test ID:TS01TD00094
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles mapping list valid id
           Status code:200
    """

    def test_booking_status_mapping_list_200_valid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-list/?id=9",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping List")

    """
         Test ID:TS01TD00095
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-mapping-list/
         Status:success
         Message:employee roles mapping list range
         Status code:200
    """

    def test_booking_status_mapping_list_200_invalid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-list/?id=1111",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_booking_status_mapping_list_200_valid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-list/?booking_status_chain=Complete",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_booking_status_mapping_list_200_invalid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-list/?booking_status_chain=Confirmedjhg",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_employee_roles_mapping_list_200_valid_manual_booking(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-list/?manual_booking=AH1907567",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_list_200_invalid_manual_booking(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-list/?manual_booking=amitaaho.indygf",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_employee_roles_mapping_list_200_valid_booking_stage(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-list/?booking_stage=in_progress",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_list_200_invalid_booking_stage(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-list/?assignment_status=activeerjh",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping List")


class BookingStatusMappingCreateKeyBasedTests(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_create_key_based_tests_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_create_key_based_tests_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_create_key_based_tests_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_create_key_based_tests_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-create-key-based/",
                                   json.dumps({"booking_status": "loaded",
                                               "manual_booking_id": 231,
                                               "booking_stage": "in_progress"
                                               }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_statuses_mapping_create_key_based_tests_415_wrong_content_type(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
                   Test ID:TS01AH00074
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong id
                   Status code:400
    """

    def test_booking_status_mapping_create_key_based_tests_400_body_empty(self):
        # Negative test for updating user category with empty body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({
                                    }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "booking_status is required field")

    """
           Test ID:TS01AH00076
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category empty
           Status code:400
    """

    def test_booking_status_mapping_create_key_based_tests_400_body_no_manual_booking_id(self):
        # Negative test case for updating booking status with no manualbooking id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({"booking_status": "loaded",
                                                "booking_stage": "in_progress"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    """
           Test ID:TS01AH00077
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category more than 15 characters
           Status code:401
    """

    def test_booking_status_mapping_create_key_based_tests_400_body_fields_no_booking_stage(self):
        # Negative test case for updating booking status with no booking stage
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({"booking_status": "lr_generated",
                                                "manual_booking_id": "7414"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['booking_stage'][0], "This field is required.")
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_create_key_based_tests_400_no_fileds(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({"booking_status": "",
                                                "manual_booking_id": "",
                                                "booking_stage": ""
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_create_key_based_tests_400_corrupt_fields(self):
        # Negative test case for booking status mapping with non existent manual booking
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({"booking_status": "loayyrded",
                                                "manual_booking_id": 811063669,
                                                "booking_stage": "in_procejtdgss"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_create_key_based_tests_400_non_existent_status_body(self):
        # Negative test case for booking status mapping with non existent status body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 100000
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({"booking_status": "isdhn",
                                                "manual_booking_id": 81069,
                                                "booking_stage": "in_process"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_create_key_based_tests_400_non_existent_manual_booking_id(self):
        # Negative test case for booking status mapping with non existent manual booking id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": "810069",
                                                "booking_stage": "in_progress"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_statuses_mapping_create_key_based_tests_201_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based/",
                                    json.dumps({"booking_status": "lr_generated",
                                                "manual_booking_id": self.manualbooking_id,
                                                "booking_stage": "in_progress"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Created")


class BookingStatusMappingCreateKeyBasedBulkTests(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_create_key_based_tests_bulk_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_create_key_based_tests_bulk_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_create_key_based_tests_bulk_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_create_key_based_tests_bulk_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-create-key-based-bulk/",
                                   json.dumps({"booking_status": "loaded",
                                               "manual_booking_id": 231,
                                               "booking_stage": "in_progress"
                                               }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_statuses_mapping_create_key_based_tests_bulk_415_wrong_content_type(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
                   Test ID:TS01AH00074
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong id
                   Status code:400
    """

    def test_booking_status_mapping_create_key_based_tests_bulk_400_body_empty(self):
        # Negative test for updating user category with empty body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({
                                    }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "booking_status is required field")

    """
           Test ID:TS01AH00076
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category empty
           Status code:400
    """

    def test_booking_status_mapping_create_key_based_tests_bulk_400_body_no_manual_booking_id(self):
        # Negative test case for updating booking status with no manualbooking id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "booking_stage": "in_progress"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "manual_booking_id is required field")

    """
           Test ID:TS01AH00077
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category more than 15 characters
           Status code:401
    """

    def test_booking_status_mapping_create_key_based_tests_bulk_400_body_fields_no_booking_stage(self):
        # Negative test case for updating booking status with no booking stage
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({"booking_status": "lr_generated",
                                                "manual_booking_id": "7414"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_create_key_based_tests_bulk_400_no_fileds(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({"booking_status": "",
                                                "manual_booking_id": "",
                                                "booking_stage": ""
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_create_key_based_tests_bulk_400_corrupt_fields(self):
        # Negative test case for booking status mapping with non existent manual booking
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({"booking_status": "loayyrded",
                                                "manual_booking_id": 811063669,
                                                "booking_stage": "in_procejtdgss"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_create_key_based_tests_bulk_400_non_existent_status_body(self):
        # Negative test case for booking status mapping with non existent status body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 100000
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({"booking_status": "isdhn",
                                                "manual_booking_id": 81069,
                                                "booking_stage": "in_process"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_create_key_based_tests_bulk_400_non_existent_manual_booking_id(self):
        # Negative test case for booking status mapping with non existent manual booking id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": "810069",
                                                "booking_stage": "in_progress"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_statuses_mapping_create_key_based_tests_bulk_201_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-create-key-based-bulk/",
                                    json.dumps({"booking_status": "lr_generated",
                                                "manual_booking_id": str(self.manualbooking_id) + ',' + str(
                                                    self.manualbooking_id) + ',' + str(self.manualbooking_id),
                                                "booking_stage": "in_progress"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Created")


class BookingStatusMappingUpdateKeyBasedBulkTests(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_update_key_based_tests_bulk_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_update_key_based_tests_bulk_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_update_key_based_tests_bulk_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_update_key_based_tests_bulk_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-update-key-based-bulk/",
                                   json.dumps({"booking_status": "loaded",
                                               "manual_booking_id": 231,
                                               "booking_stage": "in_progress"
                                               }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_statuses_mapping_update_key_based_tests_bulk_415_wrong_content_type(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": 231,
                                                "booking_stage": "in_progress"}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
                   Test ID:TS01AH00074
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong id
                   Status code:400
    """

    def test_booking_status_mapping_update_key_based_tests_bulk_400_body_empty(self):
        # Negative test for updating user category with empty body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({
                                    }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "booking_status is required field")

    """
           Test ID:TS01AH00076
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category empty
           Status code:400
    """

    def test_booking_status_mapping_update_key_based_tests_bulk_400_body_no_manual_booking_id(self):
        # Negative test case for updating booking status with no manualbooking id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "booking_stage": "in_progress"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "manual_booking_id is required field")

    """
           Test ID:TS01AH00077
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category more than 15 characters
           Status code:401
    """

    def test_booking_status_mapping_update_key_based_tests_bulk_400_body_fields_no_booking_stage(self):
        # Negative test case for updating booking status with no booking stage
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({"booking_status": "lr_generated",
                                                "manual_booking_id": "7414"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_update_key_based_tests_bulk_400_no_fileds(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({"booking_status": "",
                                                "manual_booking_id": "",
                                                "booking_stage": ""
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_update_key_based_tests_bulk_400_corrupt_fields(self):
        # Negative test case for booking status mapping with non existent manual booking
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({"booking_status": "loayyrded",
                                                "manual_booking_id": 811063669,
                                                "booking_stage": "in_procejtdgss"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_update_key_based_tests_bulk_400_non_existent_status_body(self):
        # Negative test case for booking status mapping with non existent status body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({"booking_status": "isdhn",
                                                "manual_booking_id": 81069,
                                                "booking_stage": "in_process"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Not Created")

    def test_booking_statuses_mapping_update_key_based_tests_bulk_400_non_existent_manual_booking_id(self):
        # Negative test case for booking status mapping with non existent manual booking id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({"booking_status": "loaded",
                                                "manual_booking_id": "810069",
                                                "booking_stage": "in_progress"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_statuses_mapping_update_key_based_tests_bulk_201_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-key-based-bulk/",
                                    json.dumps({"booking_status": "lr_generated",
                                                "manual_booking_id": str(self.manualbooking_id) + ',' + str(
                                                    self.manualbooking_id) + ',' + str(self.manualbooking_id),
                                                "booking_stage": "in_progress"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Updated")


class BookingStatusMappingUpdateInvoiceBased(BookingStatusMappingTests):
    """
             Test ID:TS01AH00072
             Created By:Hari
             Created On:05/12/2018
             Scenario:user-category-update/
             Status:failure
             Message:no header
             Status code:401
    """

    def booking_status_mapping_update_invoice_based_tests_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({"booking_status": "loaded",
                                                "invoice_number": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_update_invoice_based_tests_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({"booking_status": "loaded",
                                                "invoice_number": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_update_invoice_based_tests_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({"booking_status": "loaded",
                                                "invoice_number": 231,
                                                "booking_stage": "in_progress"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_update_invoice_based_tests_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-update-invoice-based/",
                                   json.dumps({"booking_status": "loaded",
                                               "invoice_number": 231,
                                               "booking_stage": "in_progress"
                                               }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_statuses_mapping_update_invoice_based_tests_415_wrong_content_type(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({"booking_status": "loaded",
                                                "invoice_number": 231,
                                                "booking_stage": "in_progress"}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
                   Test ID:TS01AH00074
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong id
                   Status code:400
    """

    def test_booking_status_mapping_update_invoice_based_tests_400_body_empty(self):
        # Negative test for updating user category with empty body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({
                                    }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "booking_status is required field")

    """
           Test ID:TS01AH00076
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category empty
           Status code:400
    """

    def test_booking_status_mapping_update_invoice_based_tests_400_body_no_invoice_no(self):
        # Negative test case for updating booking status with no manual booking id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({"booking_status": "loaded",
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "invocie_number is required field")

    """
           Test ID:TS01AH00077
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category more than 15 characters
           Status code:401
    """

    def test_booking_status_mapping_update_invoice_based_tests_400_body_fields_no_booking_stage(self):
        # Negative test case for updating booking status with no booking stage
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({"booking_status": "lr_generated",
                                                "invoice_number": "AH1908914"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Invoice Does Not Exist")

    def test_booking_statuses_mapping_update_invoice_based_tests_400_no_fileds(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({"booking_status": "",
                                                "invoice_number": "",
                                                "booking_stage": ""
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Chain Does Not Exist")

    def test_booking_statuses_mapping_update_invoice_based_tests_400_corrupt_fields(self):
        # Negative test case for booking status mapping with non existent manual booking
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({"booking_status": "loayyrded",
                                                "invoice_number": 811063669,
                                                "booking_stage": "in_procejtdgss"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Chain Does Not Exist")

    def test_booking_statuses_mapping_update_invoice_based_tests_400_non_existent_status_body(self):
        # Negative test case for booking status mapping with non existent status body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({"booking_status": "isdhn",
                                                "invoice_number": 81069,
                                                "booking_stage": "in_process"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Chain Does Not Exist")

    def test_booking_statuses_mapping_update_invoice_based_tests_400_non_existent_invoice(self):
        # Negative test case for booking status mapping with non existent manual booking id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({"booking_status": "loaded",
                                                "invoice_number": "810069",
                                                "booking_stage": "in_progress"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_statuses_mapping_update_invoice_based_tests_201_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-update-invoice-based/",
                                    json.dumps({"booking_status": "lr_generated",
                                                "invoice_number": self.invno,
                                                "booking_stage": "in_progress"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Updated")


class BookingStatusMappingCommentsCreate(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_comments_create_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_comments_create_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_comments_create_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_comments_create_tests_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-create/",
                                   json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                               "comment": "loaded"
                                               }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_status_mapping_comments_create_415_wrong_content_type(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
                   Test ID:TS01AH00074
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong id
                   Status code:400
    """

    def test_booking_status_mapping_comments_create_400_body_empty(self):
        # Negative test for updating user category with empty body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({
                                    }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Not Created")

    """
           Test ID:TS01AH00076
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category empty
           Status code:400
    """

    def test_booking_status_mapping_comments_create_400_body_incorrect_mapping_id(self):
        # Negative test case for updating booking status with no manualbooking id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": "hgvbhd",
                                                "comment": "loaded"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Not Created")

    def test_booking_status_mapping_comments_create_400_no_fileds(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": "",
                                                "comment": ""
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Not Created")

    def test_booking_status_mapping_comments_create_400_corrupt_fields(self):
        # Negative test case for booking status mapping with non existent manual booking
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": "hgvbhd",
                                                "comment": "loadedg"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Not Created")

    def test_booking_status_mapping_comments_create_400_non_existent_mapping_id(self):
        # Negative test case for booking status mapping with non existent status body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 100000
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": "1875",
                                                "comment": "loaded"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_bbooking_status_mapping_comments_create_201_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Created")


class BookingStatusMappingCommentsCreateBulk(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_comments_create_bulk_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-mapping-comments-create-bulk/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_comments_create_bulk_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-comments-create-bulk/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_comments_create_bulk_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create-bulk/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_comments_create_bulk_tests_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-create-bulk/",
                                   json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                               "comment": "loaded"
                                               }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_status_mapping_comments_create_bulk_415_wrong_content_type(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create-bulk/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
                   Test ID:TS01AH00074
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong id
                   Status code:400
    """

    def test_booking_status_mapping_comments_create_bulk_400_body_empty(self):
        # Negative test for updating user category with empty body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create-bulk/",
                                    json.dumps({
                                    }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "booking_status_mapping_id is required field")

    """
           Test ID:TS01AH00076
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category empty
           Status code:400
    """

    def test_booking_status_mapping_comments_create_400_bulk_body_incorrect_mapping_id(self):
        # Negative test case for updating booking status with no manualbooking id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create-bulk/",
                                    json.dumps({"booking_status_mapping_id": "hgvbhd",
                                                "comment": "loaded"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Not Created")

    def test_booking_status_mapping_comments_create_bulk_400_no_fileds(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create-bulk/",
                                    json.dumps({"booking_status_mapping_id": "",
                                                "comment": ""
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Not Created")

    def test_booking_status_mapping_comments_create_bulk_400_corrupt_fields(self):
        # Negative test case for booking status mapping with non existent manual booking
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create-bulk/",
                                    json.dumps({"booking_status_mapping_id": "hgvbhd",
                                                "comment": "loadedg"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Not Created")

    def test_booking_status_mapping_comments_create_bulk_400_non_existent_mapping_id(self):
        # Negative test case for booking status mapping with non existent status body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 100000
        response = self.client.post("/api/booking-statuses-mapping-comments-create-bulk/",
                                    json.dumps({"booking_status_mapping_id": "1875",
                                                "comment": "loaded"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_status_mapping_comments_create_201_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create-bulk/",
                                    json.dumps({"booking_status_mapping_id": str(
                                        self.booking_status_mapping_id) + ',' + str(self.booking_status_mapping_id),
                                                "comment": "loaded"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Created")


class BookingStatusMappingCommentsRetreive(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_comments_retrieve_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get(
            "/api/booking-statuses-mapping-comments-retrieve/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_comments_retrieve_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            "/api/booking-statuses-mapping-comments-retrieve/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_comments_retrieve_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(
            "/api/booking-statuses-mapping-comments-retrieve/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_comments_retrieve_tests_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-retrieve/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def booking_status_mapping_comments_retrieve_404_invalid_id(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        id = 35461256
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-retrieve/{}/".format(id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    def booking_status_mapping_comments_retrieve_200_valid_id(self):
        # Positive test case for updating booking status mapping with wrong HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }),
                                    content_type='application/json')
        id = response.data['data']['id']
        response = self.client.get(
            "/api/booking-statuses-mapping-comments-retrieve/{}/".format(id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Retrieved")


class BookingStatusMappingCommentsUpdate(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_comments_update_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "comment": "loaded"
                        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_comments_update_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "comment": "loaded"
                        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_comments_update_bulk_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "comment": "loaded"
                        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_comments_update_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-comments-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "comment": "loaded"
                        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_status_mapping_comments_update_415_wrong_content_type(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "comment": "loaded"}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
                   Test ID:TS01AH00074
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong id
                   Status code:400
    """

    def test_booking_status_mapping_comments_update_400_body_empty(self):
        # Negative test for updating user category with empty body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({
            }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Booking Statuses Mapping Comments Doesn't exists")

    """
           Test ID:TS01AH00076
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:failure
           Message:category empty
           Status code:400
    """

    def test_booking_status_mapping_comments_update_400_body_incorrect_mapping_id(self):
        # Negative test case for updating booking status with no manualbooking id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": "hgvbhd",
                        "comment": "loaded"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Booking Statuses Mapping Comments Doesn't exists")

    def test_booking_status_mapping_comments_update_400_no_fileds(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": "",
                        "comment": ""
                        }),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Booking Statuses Mapping Comments Doesn't exists")

    def test_booking_status_mapping_comments_update_400_corrupt_fields(self):
        # Negative test case for booking status mapping with non existent manual booking
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": "hgvbhd",
                        "comment": "loadedg"
                        }),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Booking Statuses Mapping Comments Doesn't exists")

    def test_booking_status_mapping_comments_update_400_non_existent_mapping_id(self):
        # Negative test case for booking status mapping with non existent status body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 100000
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": "1875",
                        "comment": "loaded"
                        }),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_status_mapping_comments_update_201_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }),
                                    content_type='application/json')
        ids = response.data['data']['id']
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-update/{}/".format(ids),
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Updated")


class BookingStatusMappingCommentsDestroy(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_comments_destroy_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-destroy/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "comment": "loaded"
                        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_comments_destroy_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-destroy/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "comment": "loaded"
                        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_comments_destroy_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(
            "/api/booking-statuses-mapping-comments-destroy/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "comment": "loaded"
                        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_destroy_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-comments-destroy/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "comment": "loaded"
                        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
                   Test ID:TS01AH00074
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong id
                   Status code:400
    """

    def test_booking_status_mapping_comments_destroy_404_invalid_id(self):
        # Negative test for updating user category with empty body
        id = 11233
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-destroy/{}/".format(id),
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    def test_booking_status_mapping_comments_destroy_201_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }),
                                    content_type='application/json')
        ids = response.data['data']['id']
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-destroy/{}/".format(ids),
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "comment": "loaded"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments Deleted")


class BookingStatusMappingCommentListTests(BookingStatusMappingTests):
    """
               Test ID:TS01TD00087
               Created By:Hari
               Created On:13/12/2018
               Scenario:employee-roles-mapping-list/
               Status:failure
               Message:wrong method
               Status code:405
    """

    def test_booking_status_mapping_commentlist_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-comments-list/", content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
               Test ID:TS01TD00088
               Created By:Hari
               Created On:13/12/2018
               Scenario:employee-roles-mapping-list/
               Status:failure
               Message:no header
               Status code:401
    """

    def test_booking_status_mapping_commentlist_401_no_header(self):
        self.client.credentials()
        response = self.client.get("/api/booking-statuses-mapping-comments-list/", content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00089
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_booking_status_mapping_commentlist_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-comments-list/", content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00089
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_booking_status_mapping_commentlist_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/booking-statuses-mapping-comments-list/", content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00090
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:success
          Message:employee roles mapping list
          Status code:200
    """

    def test_booking_status_mapping_commentlist_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-list/", content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
           Test ID:TS01TD00091
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles search by name
           Status code:200
     """

    def test_booking_status_mapping_commentlist_200_search_by_valid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-list/?search=3",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
           Test ID:TS01TD00092
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles search by employee status
           Status code:200
    """

    def test_booking_status_mapping_commentlist_200_search_by_invalid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-list/?search=1122",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
           Test ID:TS01TD00094
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles mapping list valid id
           Status code:200
    """

    def test_booking_status_mapping_commentlist_200_valid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-list/?id=9",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
         Test ID:TS01TD00095
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-mapping-list/
         Status:success
         Message:employee roles mapping list range
         Status code:200
    """

    def test_booking_status_mapping_commentlist_200_invalid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-list/?id=1111",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_booking_status_mapping_commentlist_200_valid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-comments-list/?booking_status_mapping_id=\"self.booking_status_mapping_id\" ",
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_booking_status_mapping_commentlist_200_invalid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-list/?booking_status_mapping=Confirmedjhg",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_employee_roles_mapping_commentlist_200_valid_booking_status_mapping(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-comments-list/?booking_status_mapping__manual_booking_id=1,2",
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_commentlist_200_invalid_booking_status_mapping(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-comments-list/?booking_status_mapping__manual_booking_id=1,88",
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_employee_roles_mapping_list_200_valid_booking_status_mapping_booking_status_chain(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-comments-list/?booking_status_mapping__booking_status_chain__booking_status__status=1,2,3",
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_list_200_invalid_booking_status_mapping_booking_status_chain(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-comments-list/?booking_status_mapping__booking_status_chain__booking_status__status=111,222,3",
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    def test_employee_roles_mapping_list_200_valid_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-list/?comment=loaded",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_list_200_invalid_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-list/?comment=loadedj gf",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")


class BookingStatusMappingLocationCreate(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_location_create_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": self.city,
                                                "district": self.district,
                                                "state": self.state,
                                                "country": self.country
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_location_create_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": self.city,
                                                "district": self.district,
                                                "state": self.state,
                                                "country": self.country
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_location_create_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": self.city,
                                                "district": self.district,
                                                "state": self.state,
                                                "country": self.country
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_location_create_tests_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-location-create/",
                                   json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                               "city": self.city,
                                               "district": self.district,
                                               "state": self.state,
                                               "country": self.country
                                               }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_status_mapping_location_create_415_wrong_content_type(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": self.city,
                                                "district": self.district,
                                                "state": self.state,
                                                "country": self.country}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
                   Test ID:TS01AH00074
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong id
                   Status code:400
    """

    def test_booking_status_mapping_location_create_400_body_empty(self):
        # Negative test for updating user category with empty body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({
                                    }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Not Created")

    def test_booking_status_mapping_location_create_400_no_fileds(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": "",
                                                "city": "",
                                                "district": "",
                                                "state": "",
                                                "country": ""
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Not Created")

    def test_booking_status_mapping_location_create_400_corrupt_fields(self):
        # Negative test case for booking status mapping with non existent manual booking
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": "hg",
                                                "city": "dhgf",
                                                "district": "fjyie",
                                                "state": "kfhg",
                                                "country": "ufighd"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Not Created")

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_status_mapping_location_create_201_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": self.city,
                                                "district": self.district,
                                                "state": self.state,
                                                "country": self.country
                                                }),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Created")


class BookingStatusMappingLocationSave(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_location_save_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-mapping-location-save/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "google_places": {
                                                    "id": "ChIJRz5CVhWm2TsRpgOBPYUz-Ec",
                                                    "name": "Bhusawal",
                                                    "address": "Bhusawal, Maharashtra, India",
                                                    "websiteUri": "null",
                                                    "longitude": 75.8010962,
                                                    "latitude": 21.045520399999997,
                                                    "viewPort": {
                                                        "southWestCoordinate": {
                                                            "longitude": 75.7544766,
                                                            "latitude": 21.0167808
                                                        },
                                                        "northWestCoordinate": {
                                                            "longitude": 75.86487950000001,
                                                            "latitude": 21.0630713
                                                        }}}}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_location_save_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-location-save/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "google_places": {
                                                    "id": "ChIJRz5CVhWm2TsRpgOBPYUz-Ec",
                                                    "name": "Bhusawal",
                                                    "address": "Bhusawal, Maharashtra, India",
                                                    "websiteUri": "null",
                                                    "longitude": 75.8010962,
                                                    "latitude": 21.045520399999997,
                                                    "viewPort": {
                                                        "southWestCoordinate": {
                                                            "longitude": 75.7544766,
                                                            "latitude": 21.0167808
                                                        },
                                                        "northWestCoordinate": {
                                                            "longitude": 75.86487950000001,
                                                            "latitude": 21.0630713
                                                        }}}}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_location_save_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-mapping-location-save/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "google_places": {
                                                    "id": "ChIJRz5CVhWm2TsRpgOBPYUz-Ec",
                                                    "name": "Bhusawal",
                                                    "address": "Bhusawal, Maharashtra, India",
                                                    "websiteUri": "null",
                                                    "longitude": 75.8010962,
                                                    "latitude": 21.045520399999997,
                                                    "viewPort": {
                                                        "southWestCoordinate": {
                                                            "longitude": 75.7544766,
                                                            "latitude": 21.0167808
                                                        },
                                                        "northWestCoordinate": {
                                                            "longitude": 75.86487950000001,
                                                            "latitude": 21.0630713
                                                        }}}}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_location_save_tests_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-location-save/",
                                   json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                               "google_places": {
                                                   "id": "ChIJRz5CVhWm2TsRpgOBPYUz-Ec",
                                                   "name": "Bhusawal",
                                                   "address": "Bhusawal, Maharashtra, India",
                                                   "websiteUri": "null",
                                                   "longitude": 75.8010962,
                                                   "latitude": 21.045520399999997,
                                                   "viewPort": {
                                                       "southWestCoordinate": {
                                                           "longitude": 75.7544766,
                                                           "latitude": 21.0167808
                                                       },
                                                       "northWestCoordinate": {
                                                           "longitude": 75.86487950000001,
                                                           "latitude": 21.0630713
                                                       }}}}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_status_mapping_location_save_415_wrong_content_type(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-save/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "google_places": {
                                                    "id": "ChIJRz5CVhWm2TsRpgOBPYUz-Ec",
                                                    "name": "Bhusawal",
                                                    "address": "Bhusawal, Maharashtra, India",
                                                    "websiteUri": "null",
                                                    "longitude": 75.8010962,
                                                    "latitude": 21.045520399999997,
                                                    "viewPort": {
                                                        "southWestCoordinate": {
                                                            "longitude": 75.7544766,
                                                            "latitude": 21.0167808
                                                        },
                                                        "northWestCoordinate": {
                                                            "longitude": 75.86487950000001,
                                                            "latitude": 21.0630713
                                                        }}}}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
                   Test ID:TS01AH00074
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong id
                   Status code:400
    """

    def test_booking_status_mapping_location_save_400_body_empty(self):
        # Negative test for updating user category with empty body
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-save/",
                                    json.dumps({
                                    }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Not Created")

    def test_booking_status_mapping_location_save_400_no_fileds(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-save/",
                                    json.dumps({"booking_status_mapping_id": "djfh",
                                                "google_places": {
                                                    "id": "ChIJRz5CVhWm2TsRpgOBPYUz-Ec",
                                                    "name": "Bhusawal",
                                                    "address": "Bhusawal, Maharashtra, India",
                                                    "websiteUri": "null",
                                                    "longitude": 75.8010962,
                                                    "latitude": 21.045520399999997,
                                                    "viewPort": {
                                                        "southWestCoordinate": {
                                                            "longitude": 75.7544766,
                                                            "latitude": 21.0167808
                                                        },
                                                        "northWestCoordinate": {
                                                            "longitude": 75.86487950000001,
                                                            "latitude": 21.0630713
                                                        }}}}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Not Created")

    def test_booking_status_mapping_location_save_400_no_google_places(self):
        # Negative test case for booking status mapping with non existent manual booking
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-save/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,

                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Not Created")

    def test_booking_status_mapping_location_save_400_no_name(self):
        # Negative test case for booking status mapping with non existent booking status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-save/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "google_places": {
                                                    "id": "ChIJRz5CVhWm2TsRpgOBPYUz-Ec",
                                                    "name": "",
                                                    "address": "Bhusawal, Maharashtra, India",
                                                    "websiteUri": "null",
                                                    "longitude": 75.8010962,
                                                    "latitude": 21.045520399999997,
                                                    "viewPort": {
                                                        "southWestCoordinate": {
                                                            "longitude": 75.7544766,
                                                            "latitude": 21.0167808
                                                        },
                                                        "northWestCoordinate": {
                                                            "longitude": 75.86487950000001,
                                                            "latitude": 21.0630713
                                                        }}}}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Not Created")

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_status_mapping_location_save_201_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-save/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "google_places": {
                                                    "id": "ChIJRz5CVhWm2TsRpgOBPYUz-Ec",
                                                    "name": "Bhusawal",
                                                    "address": "Bhusawal, Maharashtra, India",
                                                    "websiteUri": "null",
                                                    "longitude": 75.8010962,
                                                    "latitude": 21.045520399999997,
                                                    "viewPort": {
                                                        "southWestCoordinate": {
                                                            "longitude": 75.7544766,
                                                            "latitude": 21.0167808
                                                        },
                                                        "northWestCoordinate": {
                                                            "longitude": 75.86487950000001,
                                                            "latitude": 21.0630713
                                                        }}}}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Created")


class BookingStatusMappingLocationRetreive(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_location_retrieve_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get(
            "/api/booking-statuses-mapping-location-retrieve/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_location_retrieve_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            "/api/booking-statuses-mapping-location-retrieve/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_location_retrieve_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(
            "/api/booking-statuses-mapping-location-retrieve/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_location_retrieve_tests_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/booking-statuses-mapping-location-retrieve/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_status_mapping_location_retrieve_404_wrong_id(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 19345721
        response = self.client.get("/api/booking-statuses-mapping-location-retrieve/{}/".format(id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_status_mapping_location_retrieve_200_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": self.city,
                                                "district": self.district,
                                                "state": self.state,
                                                "country": self.country
                                                }),
                                    content_type='application/json')
        id = response.data['data']['id']
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-location-retrieve/{}/".format(id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Retrieved")


class BookingStatusMappingLocationDestroy(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_location_destroy_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(
            "/api/booking-statuses-mapping-location-destroy/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_location_destroy_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            "/api/booking-statuses-mapping-location-destroy/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_location_destroy_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(
            "/api/booking-statuses-mapping-location-destroy/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_location_destroy_tests_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-location-destroy/{}/".format(self.booking_status_mapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_status_mapping_location_destroy_404_wrong_id(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 19345721
        response = self.client.post("/api/booking-statuses-mapping-location-destroy/{}/".format(id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_status_mapping_location_destroy_200_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": self.city,
                                                "district": self.district,
                                                "state": self.state,
                                                "country": self.country
                                                }),
                                    content_type='application/json')
        id = response.data['data']['id']
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-destroy/{}/".format(id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Deleted")


class BookingStatusMappingLocationUpdate(BookingStatusMappingTests):
    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def booking_status_mapping_location_update_401_no_header(self):
        # Negative test for updating booking status mapping create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(
            "/api/booking-statuses-mapping-location-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "city": self.city,
                        "district": self.district,
                        "state": self.state,
                        "country": self.country
                        }),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:expired header
                 Status code:401
    """

    def booking_status_mapping_location_update_401_expired_header(self):
        # Negative test case for updating booking status mapping create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            "/api/booking-statuses-mapping-location-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "city": self.city,
                        "district": self.district,
                        "state": self.state,
                        "country": self.country
                        }),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                 Test ID:TS01AH00073
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:wrong token
                 Status code:401
    """

    def booking_status_mapping_location_update_401_wrong_token(self):
        # Negative test case for updating booking status mapping with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(
            "/api/booking-statuses-mapping-location-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "city": self.city,
                        "district": self.district,
                        "state": self.state,
                        "country": self.country
                        }),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                   Test ID:TS01AH00074*
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:wrong method
                   Status code:405
      """

    def booking_status_mapping_location_update_tests_405_wrong_method(self):
        # Negative test for updating booking status mapping with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-location-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                        "city": self.city,
                        "district": self.district,
                        "state": self.state,
                        "country": self.country
                        }),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_booking_status_mapping_location_update_400_body_blank(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": self.city,
                                                "district": self.district,
                                                "state": self.state,
                                                "country": self.country
                                                }),
                                    content_type='application/json')
        id = response.data['data']['id']
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/booking-statuses-mapping-location-update/{}/".format(id),
            json.dumps({
                        }),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Not Updated")

    def test_booking_status_mapping_location_update_400_fields_blank(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": self.city,
                                                "district": self.district,
                                                "state": self.state,
                                                "country": self.country
                                                }),
                                    content_type='application/json')
        id = response.data['data']['id']
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/booking-statuses-mapping-location-update/{}/".format(id),
            json.dumps({"booking_status_mapping_id": "",
                        "city": "",
                        "district": "",
                        "state": "",
                        "country": ""
                        }),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Not Updated")

    def test_booking_status_mapping_location_update_400_fields_corrupt(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": self.city,
                                                "district": self.district,
                                                "state": self.state,
                                                "country": self.country
                                                }),
                                    content_type='application/json')
        id = response.data['data']['id']
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/booking-statuses-mapping-location-update/{}/".format(id),
            json.dumps({"booking_status_mapping_id": "jgug",
                        "city": "klfgh",
                        "district": "fkgi",
                        "state": "dkfjgh",
                        "country": "flguu"
                        }),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Not Updated")

    def test_booking_status_mapping_location_update_400_fields_non_existent(self):
        # Negative test case for updating booking status mapping with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/booking-statuses-mapping-location-update/{}/".format(self.booking_status_mapping_id),
            json.dumps({"booking_status_mapping_id": "16",
                        "city": self.city,
                        "district": self.district,
                        "state": self.state,
                        "country": self.country
                        }),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Booking Statuses Mapping Location Doesn't exists")

    """
           Test ID:TS01AH00078
           Created By:Hari
           Created On:05/12/2018
           Scenario:user-category-update/
           Status:success
           Message:updated
           Status code:202
    """

    def test_booking_status_mapping_location_update_200_success(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-create/",
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": self.city,
                                                "district": self.district,
                                                "state": self.state,
                                                "country": self.country
                                                }),
                                    content_type='application/json')
        id = response.data['data']['id']
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-update/{}/".format(id),
                                    json.dumps({"booking_status_mapping_id": self.booking_status_mapping_id,
                                                "city": "Madurai",
                                                "district": "Madurai",
                                                "state": "Tamil Nadu",
                                                "country": "India"
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location Updated")


class BookingStatusMappingLocationListTests(BookingStatusMappingTests):
    """
               Test ID:TS01TD00087
               Created By:Hari
               Created On:13/12/2018
               Scenario:employee-roles-mapping-list/
               Status:failure
               Message:wrong method
               Status code:405
    """

    def test_booking_status_mapping_locationlist_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-mapping-location-list/", content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
               Test ID:TS01TD00088
               Created By:Hari
               Created On:13/12/2018
               Scenario:employee-roles-mapping-list/
               Status:failure
               Message:no header
               Status code:401
    """

    def test_booking_status_mapping_locationlist_401_no_header(self):
        self.client.credentials()
        response = self.client.get("/api/booking-statuses-mapping-location-list/", content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00089
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_booking_status_mapping_locationlist_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-mapping-location-list/", content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00089
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_booking_status_mapping_locationlist_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/booking-statuses-mapping-location-list/", content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00090
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:success
          Message:employee roles mapping list
          Status code:200
    """

    def test_booking_status_mapping_locationlist_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-location-list/", content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location List")

    """
           Test ID:TS01TD00091
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles search by name
           Status code:200
     """

    def test_booking_status_mapping_locationlist_200_search_by_valid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-location-list/?search=3",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location List")

    """
           Test ID:TS01TD00092
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles search by employee status
           Status code:200
    """

    def test_booking_status_mapping_commentlist_200_search_by_invalid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-location-list/?search=1122",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location List")

    """
           Test ID:TS01TD00094
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles mapping list valid id
           Status code:200
    """

    def test_booking_status_mapping_commentlist_200_valid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-location-list/?id=9",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location List")

    """
         Test ID:TS01TD00095
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-mapping-list/
         Status:success
         Message:employee roles mapping list range
         Status code:200
    """

    def test_booking_status_mapping_commentlist_200_invalid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-location-list/?id=1111",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_booking_status_mapping_commentlist_200_valid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-location-list/?booking_status_mapping_id=\"self.booking_status_mapping_id\" ",
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_booking_status_mapping_commentlist_200_invalid_booking_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-location-list/?booking_status_mapping=Confirmedjhg",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_employee_roles_mapping_locationlist_200_valid_booking_status_mapping(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-location-list/?booking_status_mapping__manual_booking_id=1,2",
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_locationlist_200_invalid_booking_status_mapping(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-location-list/?booking_status_mapping__manual_booking_id=1,88",
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_employee_roles_mapping_list_200_valid_booking_status_mapping_booking_status_chain(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-location-list/?booking_status_mapping__booking_status_chain__booking_status__status=1,2,3",
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_list_200_invalid_booking_status_mapping_booking_status_chain(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/booking-statuses-mapping-location-list/?booking_status_mapping__booking_status_chain__booking_status__status=111,222,3",
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Location List")

    def test_employee_roles_mapping_list_200_valid_lattitude\
                    (self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-list/?comment=loaded",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_list_200_invalid_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-mapping-comments-list/?comment=loadedj gf",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Mapping Comments List")

