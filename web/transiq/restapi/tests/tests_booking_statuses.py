import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import Profile


class BookingStatusesTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.bookingstatuseslist_url = reverse('booking_statuses_list/')
        self.bookingstatusescreate_url = reverse('booking_statuses_create/')

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

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusescreate_url,
                                    json.dumps({"status": "unloaded", "time_limit": "50"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.bookingstatuses_id = response.data['data']['id']


class BookingStatusesCreateTests(BookingStatusesTests):

    """
         Test ID:TS01TD00099
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-create/
         Status:failure
         Message:wrong method
         Status code:405
    """

    def test_booking_statuses_create_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.bookingstatusescreate_url, {"status": "unloaded", "time_limit": "50"},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01TD00100
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-create/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_booking_statuses_create_401_no_header(self):
        self.client.credentials()
        response = self.client.post(self.bookingstatusescreate_url, {"status": "unloaded", "time_limit": "50"},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01TD00101
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-create/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_booking_statuses_create_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.bookingstatusescreate_url, {"status": "unloaded", "time_limit": "50"},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00101
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-create/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_booking_statuses_create_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.bookingstatusescreate_url, {"status": "unloaded", "time_limit": "50"},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00102
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-create/
         Status:failure
         Message:wrong content
         Status code:415
    """

    def test_booking_statuses_create_415_header_with_wrong_content_type(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusescreate_url, json.dumps({"status": "unloaded", "time_limit": "50"}),
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
         Test ID:TS01TD00103
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-create/
         Status:failure
         Message:blank body
         Status code:400
    """

    def test_booking_statuses_create_400_blank_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusescreate_url, {}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'][0], "This field is required.")
        self.assertEqual(response.data['time_limit'][0], "This field is required.")

    """
        Test ID:TS01TD00104
        Created By:Hari
        Created On:13/12/2018
        Scenario:booking-statuses-create/
        Status:failure
        Message:blank fields
        Status code:400
    """

    def test_booking_statuses_create_400_blank_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusescreate_url, json.dumps({"status": "", "time_limit": ""}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'][0], "\"\" is not a valid choice.")
        self.assertEqual(response.data['time_limit'][0], "A valid integer is required.")

    """
        Test ID:TS01TD00105
        Created By:Hari
        Created On:13/12/2018
        Scenario:booking-statuses-create/
        Status:failure
        Message:corrupt fields
        Status code:400
    """

    def test_booking_statuses_create_400_corrupt_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusescreate_url, json.dumps({"status": "ghfggm", "time_limit": "fdhhgfv"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'][0], "\"ghfggm\" is not a valid choice.")
        self.assertEqual(response.data['time_limit'][0], "A valid integer is required.")

    """
        Test ID:TS01TD00107
        Created By:Hari
        Created On:13/12/2018
        Scenario:booking-statuses-create/
        Status:success
        Message:correct fields
        Status code:201
    """

    def test_booking_statuses_create_201_correct_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusescreate_url, json.dumps({"status": "loaded", "time_limit": "40"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Created")

    """
        Test ID:TS01TD00106
        Created By:Hari
        Created On:13/12/2018
        Scenario:booking-statuses-create/
        Status:failure
        Message:correct fields
        Status code:400
    """

    def test_booking_statuses_create_400_duplicate_status_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusescreate_url, json.dumps({"status": "confirmed", "time_limit": "50"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatusescreate_url, {"status": "confirmed", "time_limit": "50"},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookingStatusesRetrieveTests(BookingStatusesTests):

    """
         Test ID:TS01TD00108
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-retrieve/<Valid ID>/
         Status:failure
         Message:wrong method
         Status code:405
    """

    def test_booking_statuses_retrieve_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-retrieve/{}/".format(self.bookingstatuses_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01TD00109
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-retrieve/<Valid ID>/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_booking_statuses_retrieve_401_no_header(self):
        self.client.credentials()
        response = self.client.get("/api/booking-statuses-retrieve/{}/".format(self.bookingstatuses_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01TD00110
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-retrieve/<Valid ID>/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_booking_statuses_retrieve_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/booking-statuses-retrieve/{}/".format(self.bookingstatuses_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00110
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-retrieve/<Valid ID>/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_booking_statuses_retrieve_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/booking-statuses-retrieve/{}/".format(self.bookingstatuses_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00111
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-retrieve/<Valid ID>/
         Status:failure
         Message:wrong id
         Status code:404
    """

    def test_booking_statuses_retrieve_404_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bookingstatuses_id = 10000
        response = self.client.get("/api/booking-statuses-retrieve/{}/".format(bookingstatuses_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
         Test ID:TS01TD00112
         Created By:Hari
         Created On:13/12/2018
         Scenario:booking-statuses-retrieve/<Valid ID>/
         Status:success
         Message:retrieve success
         Status code:200
    """

    def test_booking_statuses_retrieve_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-retrieve/{}/".format(self.bookingstatuses_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")

class BookingStatusesUpdateTests(BookingStatusesTests):

    """
          Test ID:TS01TD00113
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-update/<Valid ID>/
          Status:failure
          Message:wrong method
          Status code:405
     """

    def test_booking_statuses_update_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-update/{}/".format(self.bookingstatuses_id),
                                   {"status": "unloaded", "time_limit": "50"},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00114
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-update/<Valid ID>/
          Status:failure
          Message:wrong method
          Status code:401
     """

    def test_booking_statuses_update_401_no_header(self):
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-update/{}/".format(self.bookingstatuses_id),
                                    json.dumps({"status": "unloaded", "time_limit": "50"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00115
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-update/<Valid ID>/
          Status:failure
          Message:expired header
          Status code:401
     """

    def test_booking_statuses_update_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-update/{}/".format(self.bookingstatuses_id),
                                    json.dumps({"status": "unloaded", "time_limit": "50"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00115
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-update/<Valid ID>/
          Status:failure
          Message:wrong token
          Status code:401
     """

    def test_booking_statuses_update_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-update/{}/".format(self.bookingstatuses_id),
                                    json.dumps({"status": "unloaded", "time_limit": "50"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00116
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-update/<Valid ID>/
          Status:failure
          Message:wrong content type
          Status code:415
     """

    def test_booking_statuses_update_415_header_with_wrong_content_type(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-update/{}/".format(self.bookingstatuses_id),
                                    json.dumps({"status": "unloaded", "time_limit": "50"}),
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
          Test ID:TS01TD00117
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-update/<Valid ID>/
          Status:failure
          Message:blank body
          Status code:400
     """

    def test_booking_statuses_update_400_blank_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-update/{}/".format(self.bookingstatuses_id), {},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'][0], "This field is required.")
        self.assertEqual(response.data['time_limit'][0], "This field is required.")

    """
          Test ID:TS01TD00118
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-update/<Valid ID>/
          Status:failure
          Message:blank fields
          Status code:400
     """

    def test_booking_statuses_update_400_blank_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-update/{}/".format(self.bookingstatuses_id),
                                    json.dumps({"status": "", "time_limit": ""}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'][0], "\"\" is not a valid choice.")
        self.assertEqual(response.data['time_limit'][0], "A valid integer is required.")

    """
          Test ID:TS01TD00119
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-update/<Valid ID>/
          Status:failure
          Message:corrupt fields
          Status code:400
     """

    def test_booking_statuses_update_400_corrupt_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-update/{}/".format(self.bookingstatuses_id),
                                    json.dumps({"status": "ghfggm", "time_limit": "fdhhgfv"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'][0], "\"ghfggm\" is not a valid choice.")
        self.assertEqual(response.data['time_limit'][0], "A valid integer is required.")

    """
          Test ID:TS01TD00120
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-update/<Valid ID>/
          Status:failure
          Message:wrong id
          Status code:400
     """

    def test_employee_roles_update_400_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bookingstatuses_id = 1000
        response = self.client.post("/api/booking-statuses-update/{}/".format(bookingstatuses_id),
                                    json.dumps({'role': 'traffic'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "BookingStatuses Doesn't exists")

    """
          Test ID:TS01TD00121
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-update/<Valid ID>/
          Status:failure
          Message:correct fields
          Status code:201
     """

    def test_booking_statuses_update_202_correct_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-update/{}/".format(self.bookingstatuses_id),
                                    json.dumps({"status": "confirmed", "time_limit": "50"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Updated")


class BookingStatusesDestroyTests(BookingStatusesTests):

    """
          Test ID:TS01TD00122
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-destroy/<Valid ID>/
          Status:failure
          Message:wrong method
          Status code:405
     """

    def test_booking_statuses_delete_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-destroy/{}/".format(self.bookingstatuses_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00123
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-destroy/<Valid ID>/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_booking_statuses_delete_401_no_header(self):
        self.client.credentials()
        response = self.client.post("/api/booking-statuses-destroy/{}/".format(self.bookingstatuses_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00124
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-destroy/<Valid ID>/
          Status:failure
          Message:expired header
          Status code:401
     """

    def test_booking_statuses_delete_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/booking-statuses-destroy/{}/".format(self.bookingstatuses_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00124
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-destroy/<Valid ID>/
          Status:failure
          Message:wrong token
          Status code:401
     """

    def test_booking_statuses_delete_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/booking-statuses-destroy/{}/".format(self.bookingstatuses_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00125
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-destroy/<Valid ID>/
          Status:failure
          Message:wrong id
          Status code:404
     """

    def test_booking_statuses_delete_404_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bookingstatuses_id = 1000
        response = self.client.post("/api/booking-statuses-destroy/{}/".format(bookingstatuses_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
          Test ID:TS01TD00126
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-destroy/<Valid ID>/
          Status:fsuccess
          Message:deletesuccess
          Status code:200
     """

    def test_booking_statuses_delete_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/booking-statuses-destroy/{}/".format(self.bookingstatuses_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses Deleted")


class BookingStatusesListTests(BookingStatusesTests):

    """
          Test ID:TS01TD00127
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:failure
          Message:wrong method
          Status code:405
     """

    def test_booking_statuses_list_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.bookingstatuseslist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00128
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:failure
          Message:no header
          Status code:401
     """

    def test_booking_statuses_list_401_no_header(self):
        self.client.credentials()
        response = self.client.get(self.bookingstatuseslist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00129
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:failure
          Message:expired header
          Status code:401
     """

    def test_booking_statuses_list_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.bookingstatuseslist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00129
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:failure
          Message:wrong token
          Status code:401
     """

    def test_booking_statuses_list_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.bookingstatuseslist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00130
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:success
          Message:booking statuses list
          Status code:200
    """

    def test_booking_statuses_list_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.bookingstatuseslist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses List")

    """
          Test ID:TS01TD00131
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:success
          Message:booking statuses search by valid number
          Status code:200
    """

    def test_booking_statuses_list_200_search_by_valid_no(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-list/?search=3/",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses List")

    """
          Test ID:TS01TD00132
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:success
          Message:booking statuses search by invalid no.
          Status code:200
    """

    def test_booking_statuses_list_200_search_by_invalid_no(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-list/?search=8/",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses List")

    """
          Test ID:TS01TD00133
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:success
          Message:booking statuses search by booking status loaded
          Status code:200
    """

    def test_booking_statuses_list_200_search_by_booking_status_loaded(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-list/?search=loaded",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses List")

    """
          Test ID:TS01TD00134
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:success
          Message:booking statuses search by valid id
          Status code:200
    """

    def test_booking_statuses_list_200_valid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-list/?id=2",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses List")

    """
          Test ID:TS01TD00135
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:success
          Message:booking statuses range
          Status code:200
    """

    def test_booking_statuses_list_200_range(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-list/?id_range_0=1&id_range_1=3",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses List")

    """
          Test ID:TS01TD00136
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:success
          Message:booking statuses loaded
          Status code:200
    """

    def test_booking_statuses_list_200_status_loaded(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-list/?status=loaded",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses List")

    """
          Test ID:TS01TD00137
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:success
          Message:booking statuses corrupt status
          Status code:200
    """

    def test_booking_statuses_list_200_corrupt_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-list/?status=sgjsgd",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses List")

    """
          Test ID:TS01TD00138
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:success
          Message:booking statuses list time limit
          Status code:200
    """

    def test_booking_statuses_list_200_time_limit(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-list/?time_limit=34",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses List")

    """
          Test ID:TS01TD00139
          Created By:Hari
          Created On:13/12/2018
          Scenario:booking-statuses-list/
          Status:success
          Message:booking statuses list invalid time limit
          Status code:200
    """

    def test_booking_statuses_list_200_invalid_time_limit(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/booking-statuses-list/?time_limit=3",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Booking Statuses List")

