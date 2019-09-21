import json

from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import Profile
from restapi.models import TaskDashboardFunctionalities


class TdfTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.tdflist_url = reverse('task_dashboard_functionalities_list/')
        self.tdfcreate_url = reverse('task_dashboard_functionalities_create/')

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
        self.taskdf = mommy.make(TaskDashboardFunctionalities)
        self.functionality = self.taskdf.functionality
        self.tdid = self.taskdf.id


class TDFCreateTests(TdfTests):

    """
         Test ID:TS02RQ00006
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong content type
         Status code:415
    """

    def test_tdf_create_415_header_with_wrong_content_type(self):
        # Negative test case of req quotes create with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.tdfcreate_url, json.dumps({"functionality": "Delivered"}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
         Test ID:TS02RQ00007
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:invalid method header
         Status code:401
    """

    def test_tdf_create_401_no_header(self):
        # Negative test case of req quotes create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(self.tdfcreate_url, {"functionality": "Delivered"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS02RQ00008
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:expired header
         Status code:401
    """
    def test_tdf_create_401_expired_header(self):
        # Negative test case of req quotes create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.tdfcreate_url, {"functionality": "Delivered"}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS02RQ00008
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_tdf_create_401_wrong_token(self):
        # Negative test case of req quotes create with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.tdfcreate_url, json.dumps({"functionality": "Delivered"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS02RQ00009
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong vehicle number
         Status code:400
    """
    def test_tdf_create_400_emptybody(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and wrong vehicle_no
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.tdfcreate_url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['functionality'][0], "This field is required.")

    """
         Test ID:TS02RQ00010
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong requirement
         Status code:400
    """

    def test_tdf_create_400_tdf_empty(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and wrong requirement_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.tdfcreate_url, json.dumps({"functionality":""}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['functionality'][0], "\"\" is not a valid choice.")

    """
         Test ID:TS02RQ00011
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong supplier
         Status code:400
    """

    def test_tdf_create_400_corrupt_fields(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and wrong broker_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.tdfcreate_url, json.dumps({"functionality": "Delivegfygred"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['functionality'][0], "\"Delivegfygred\" is not a valid choice.")

    """
         Test ID:TS02RQ00012
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:rate not integer
         Status code:400
    """

    def test_tdf_create_uniquefield(self):
        # Negative test case of tdf create with HTTP Header Authorization token and functionality not unique
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.tdfcreate_url, json.dumps({"functionality": "Delivered"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
         Test ID:TS02RQ00014
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:success
         Message:requirement quote created
         Status code:201
    """

    def test_tdf_create_201(self):
        # Positive test case of req quotes create with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.tdfcreate_url,
                                    json.dumps({"functionality": "delivered"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Task Dashboard Functionalities Created")


class TdfRetrieveTests(TdfTests):

    """
         Test ID:TS02RQ00015
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-detail/<id>
         Status:failure
         Message:no header
         Status code:401
    """

    def test_tdf_retreive_401_no_header(self):
        # Negative test case for getting req quotes detail with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/task-dashboard-functionalities-retrieve/{}/".format(self.tdid), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS02RQ00016
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-detail/<id>
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_tdf_retrieve_401_expired_header(self):
        # Negative test case for getting req quotes detail with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/task-dashboard-functionalities-retrieve/{}/".format(self.tdid), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00016
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-detail/<id>
       Status:failure
       Message:wrong token
       Status code:401
    """

    def test_tdf_retrieve_401_wrong_token(self):
        # Negative test case for getting req quotes detail with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/task-dashboard-functionalities-retrieve/{}/".format(self.tdid), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00017
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-detail/<id>
       Status:failure
       Message:wrong method
       Status code:405
    """

    def test_tdf_retrieve_405_wrong_method(self):
        # Negative test for getting req quotes detail with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/task-dashboard-functionalities-retrieve/{}/".format(self.tdid), format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
       Test ID:TS02RQ00019
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-detail/<id>
       Status:failure
       Message:wrong id
       Status code:404
    """

    def test_tdf_detail_404_wrong_id(self):
        # Negative test for getting req quotes detail with wrong id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 10303
        response = self.client.get("/api/task-dashboard-functionalities-retrieve/{}/".format(id), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")


    """
       Test ID:TS02RQ00020
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-detail/<id>
       Status:success
       Message:req quotes detail display
       Status code:200
    """
    def test_tdf_retrieve_200(self):
        # Positive for getting req quotes detail
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/task-dashboard-functionalities-retrieve/{}/".format(self.tdid), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Task Dashboard Functionalities Retrieved")


class TdfUpdateTests(TdfTests):

    """
       Test ID:TS02RQ00022
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-detail/<id>
       Status:failure
       Message:no header
       Status code:401
    """

    def test_tdf_update_401_no_header(self):
        # Negative test for updating req quotes with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/task-dashboard-functionalities-update/{}/".format(self.tdid), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
       Test ID:TS02RQ00023
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:expired header
       Status code:401
    """

    def test_tdf_update_401_expired_header(self):
        # Negative test case for updating req quotes with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/task-dashboard-functionalities-update/{}/".format(self.tdid), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00023
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:success
       Message:wrong token
       Status code:401
    """
    def test_req_quotes_update_401_wrong_token(self):
        # Negative test case for updating req quotes with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/task-dashboard-functionalities-update/{}/".format(self.tdid), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00021
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:success
       Message:wrong method
       Status code:405
    """

    def test_tdf_update_405_wrong_method(self):
        # Negative test for updating req quotes with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/task-dashboard-functionalities-update/{}/".format(self.tdid), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
       Test ID:TS02RQ00024
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:wrong content type
       Status code:415
    """

    def test_tdf_update_415_header_with_wrong_content_type(self):
        # Negative test case for updating req quotes with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/task-dashboard-functionalities-update/{}/".format(self.tdid),json.dumps({"functionality": "Delivered"}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
       Test ID:TS02RQ00025
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:req quotes detail display
       Status code:400
    """

    def test_tdf_update_400_wrong_id(self):
        # Negative test for updating req quotes with wrong id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        id = 100
        response = self.client.post("/api/task-dashboard-functionalities-update/{}/".format(id), json.dumps({"functionality": "Delivered"}),content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "TaskDashboardFunctionalities Doesn't exists")

    """
       Test ID:TS02RQ00026
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:wrong vehicle number
       Status code:400
    """
    def test_tdf_update_400_bodyblank(self):
        # Negative test case for updating req quotes with HTTP Header Authorization token and body blank
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/task-dashboard-functionalities-update/{}/".format(self.tdid),
                                    json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['functionality'][0], "This field is required.")

    """
       Test ID:TS02RQ00027
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:wrong requirement id
       Status code:400
    """
    def test_tdf_update_400_empty_field(self):
        # Negative test case for updating req quotes with HTTP Header Authorization token and wrong requirement_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/task-dashboard-functionalities-update/{}/".format(self.tdid),
                                    json.dumps({"functionality": ""}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['functionality'][0], "\"\" is not a valid choice.")

    """
       Test ID:TS02RQ00028
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:wrong supplier id
       Status code:400
    """

    def test_tdf_update_400_corrupt_body(self):
        # Negative test case for updating req quotes with HTTP Header Authorization token and wrong broker_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/task-dashboard-functionalities-update/{}/".format(self.tdid),
                                    json.dumps({"functionality": "ghfhgmh"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['functionality'][0], "\"ghfhgmh\" is not a valid choice.")


    """
       Test ID:TS02RQ00031
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:success
       Message:req quotes updated
       Status code:202
    """
    def test_tdf_update_202(self):
        # Positive test case for updating req quotes with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/task-dashboard-functionalities-update/{}/".format(self.tdid),
                                    json.dumps({"functionality": "delivered"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Task Dashboard Functionalities Updated")

class TdfDestroyTests(TdfTests):

    """
       Test ID:TS02RQ00032
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-destroy/<REQ QT ID>/
       Status:failure
       Message:wrong method
       Status code:405
    """

    def test_tdf_destroy_405_wrong_method(self):
        # Negative test for destroying req quotes with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/task-dashboard-functionalities-destroy/{}/".format(self.tdid))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
       Test ID:TS02RQ00033
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-destroy/<REQ QT ID>/
       Status:failure
       Message:no header
       Status code:401
    """

    def test_tdf_destroy_401_no_header(self):
        # Negative test case for destroying req quotes with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/task-dashboard-functionalities-destroy/{}/".format(self.tdid))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
       Test ID:TS02RQ00034
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-destroy/<REQ QT ID>/
       Status:failure
       Message:expired header
       Status code:401
    """

    def test_tdf_destroy_401_expired_header(self):
        # Negative test case for destroying req quotes with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/task-dashboard-functionalities-destroy/{}/".format(self.tdid))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00034
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-destroy/<REQ QT ID>/
       Status:failure
       Message:wrong token
       Status code:401
    """

    def test_tdf_destroy_401_wrong_token(self):
        # Negative test case for destroying req quotes with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/task-dashboard-functionalities-destroy/{}/".format(self.tdid))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00035
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-destroy/<REQ QT ID>/
       Status:success
       Message:req quotes destroyed
       Status code:200
    """

    def test_tdf_destroy_404_wrong_id(self):
        # Wrong credentials for id
        id = 2373224
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/task-dashboard-functionalities-destroy/{}/".format(id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    def test_tdf_destroy_200(self):
        # Positive for destroying req quotes
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/task-dashboard-functionalities-destroy/{}/".format(self.tdid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Task Dashboard Functionalities Deleted")


class TdfListTests(TdfTests):

    """
        Test ID:TS02RQ00110
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
        Status:failure
        Message:test req all
        Status code:401
    """

    def test_tdf_list_401_no_header(self):
        # Negative test case for getting filtered req list with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/task-dashboard-functionalities-list/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
            Test ID:TS02RQ00114
            Created By:Hari
            Created On:11/12/2018
            Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
            Status:failure
            Message:test req all
            Status code:401
    """

    def test_tdf_list_401_expired_header(self):
        # Negative test case for getting filtered req list with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/task-dashboard-functionalities-list/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
        Test ID:TS02RQ00114
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
        Status:failure
        Message:test req all
        Status code:401
    """

    def test_tdf_list_401_wrong_token(self):
        # Negative test case for getting filtered req list with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/task-dashboard-functionalities-list/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
        Test ID:TS02RQ00109
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
        Status:success
        Message:test req all
        Status code:200
    """

    def test_tdf_list_405_wrong_method(self):
        # Negative test for getting filtered req list with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/task-dashboard-functionalities-list/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
        Test ID:TS02RQ00119
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
        Status:success
        Message:req list filter
        Status code:200
    """

    def test_tdf_list_filter_200(self):
        # Positive test case for getting filtered req list with correct req_status and aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/task-dashboard-functionalities-list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Task Dashboard Functionality List")

    """
       Test ID:TS02RQ00120
       Created By:Hari
       Created On:11/12/2018
       Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
       Status:failure
       Message:req list filter
       Status code:200
    """

    def test_tdf_list_valid_search_200(self):
        # Positive test case for getting filtered req list with correct req_status and aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/task-dashboard-functionalities-list/?search=delivered")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Task Dashboard Functionality List")

    def test_tdf_list_invalid_search_200(self):
        # Positive test case for getting filtered req list with correct req_status and aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/task-dashboard-functionalities-list/?search=valirtd")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Task Dashboard Functionality List")

    def test_tdf_list_valid_idsearch_200(self):
        # Positive test case for getting filtered req list with correct req_status and aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/task-dashboard-functionalities-list/?id=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Task Dashboard Functionality List")

    def test_tdf_list_invalid_idsearch_200(self):
        # Positive test case for getting filtered req list with correct req_status and aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/task-dashboard-functionalities-list/?id=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Task Dashboard Functionality List")

    def test_tdf_list_valid_functionality_200(self):
        # Positive test case for getting filtered req list with correct req_status and aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/task-dashboard-functionalities-list/?functionality=monitor")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Task Dashboard Functionality List")

    def test_tdf_list_invalid_functionality_200(self):
        # Positive test case for getting filtered req list with correct req_status and aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/task-dashboard-functionalities-list/?functionality=dsshgf")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Task Dashboard Functionality List")
