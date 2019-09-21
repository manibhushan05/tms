import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import Profile


class EmployeeRolesTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.employeeroleslist_url = reverse('employee_roles_list/')
        self.employeerolescreate_url = reverse('employee_roles_create/')

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
        response = self.client.post(self.employeerolescreate_url, json.dumps({"role": "ops_executive"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.employeeroles_id = response.data['data']['id']


class EmployeeRolesCreateTests(EmployeeRolesTests):

    """
         Test ID:TS01TD00016
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-create/
         Status:failure
         Message:wrong method
         Status code:405
    """

    def test_employee_roles_create_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.employeerolescreate_url, {'role': 'office data entry'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01TD00017
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-create/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_employee_roles_create_401_no_header(self):
        self.client.credentials()
        response = self.client.post(self.employeerolescreate_url, {'role': 'office data entry'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01TD00018
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-create/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_employee_roles_create_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.employeerolescreate_url, {'role': 'office data entry'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00018
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-create/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_employee_roles_create_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.employeerolescreate_url, {'role': 'office data entry'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00022
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-create/
         Status:failure
         Message:wrong content type
         Status code:415
    """

    def test_employee_roles_create_415_header_with_wrong_content_type(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolescreate_url, json.dumps({'role': 'office data entry'}),
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
         Test ID:TS01TD00019
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-create/
         Status:failure
         Message:blank body
         Status code:400
    """

    def test_employee_roles_create_400_blank_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolescreate_url, {}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['role'][0], "This field is required.")

    """
         Test ID:TS01TD00020
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-create/
         Status:failure
         Message:blank role
         Status code:400
    """

    def test_employee_roles_create_400_blank_role_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolescreate_url, {'role': ''}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
         Test ID:TS01TD00021
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-create/
         Status:failure
         Message:corrupted role field
         Status code:400
    """

    def test_employee_roles_create_400_corrupt_role_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolescreate_url, {'role': 'hjwgdkwydgwdbwydugdbddgydbyedvvd'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
         Test ID:TS01TD00023
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-create/
         Status:success
         Message:correct role field
         Status code:201
    """

    def test_employee_roles_create_201_correct_role_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolescreate_url, json.dumps({"role": "accounts_receivable"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Role Created")

    """
         Test ID:TS01TD00024
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-create/
         Status:failure
         Message:duplicate role field
         Status code:400
    """

    def test_employee_roles_create_400_duplicate_role_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolescreate_url, json.dumps({"role": "accounts_payable"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolescreate_url, json.dumps({'role': 'accounts_payable'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['role'][0], "This field must be unique.")


class EmployeeRolesRetrieveTests(EmployeeRolesTests):

    """
         Test ID:TS01TD00025
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-retrieve/<Valid ID>/
         Status:failure
         Message:wrong method
         Status code:405
    """

    def test_employee_roles_retrieve_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-retrieve/{}/".format(self.employeeroles_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01TD00026
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-retrieve/<Valid ID>/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_employee_roles_retrieve_401_no_header(self):
        self.client.credentials()
        response = self.client.get("/api/employee-roles-retrieve/{}/".format(self.employeeroles_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01TD00027
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-retrieve/<Valid ID>/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_employee_roles_retrieve_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/employee-roles-retrieve/{}/".format(self.employeeroles_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00027
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-retrieve/<Valid ID>/
         Status:failure
         Message:wrong header
         Status code:401
    """

    def test_employee_roles_retrieve_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/employee-roles-retrieve/{}/".format(self.employeeroles_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00028
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-retrieve/<Valid ID>/
         Status:failure
         Message:wrong id
         Status code:404
    """

    def test_employee_roles_retrieve_404_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.employeeroles_id = 10000
        response = self.client.get("/api/employee-roles-retrieve/{}/".format(self.employeeroles_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
         Test ID:TS01TD00029
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-retrieve/<Valid ID>/
         Status:success
         Message:retreive
         Status code:200
    """

    def test_employee_roles_retrieve_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-retrieve/{}/".format(self.employeeroles_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Role Retrieved")

class EmployeeRolesUpdateTests(EmployeeRolesTests):

    """
         Test ID:TS01TD00030
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-update/<Valid ID>/
         Status:failure
         Message:wrong method
         Status code:405
    """

    def test_employee_roles_update_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-update/{}/".format(self.employeeroles_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01TD00031
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-update/<Valid ID>/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_employee_roles_update_401_no_header(self):
        self.client.credentials()
        response = self.client.post("/api/employee-roles-update/{}/".format(self.employeeroles_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01TD00033
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-update/<Valid ID>/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_employee_roles_update_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/employee-roles-update/{}/".format(self.employeeroles_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00033
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-update/<Valid ID>/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_employee_roles_update_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/employee-roles-update/{}/".format(self.employeeroles_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00032
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-update/<Valid ID>/
         Status:failure
         Message:wrong content type
         Status code:415
    """

    def test_employee_roles_update_415_header_with_wrong_content_type(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-update/{}/".format(self.employeeroles_id),
                                    json.dumps({'role': 'office data entry'}),
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
         Test ID:TS01TD00034
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-update/<Valid ID>/
         Status:failure
         Message:body blank
         Status code:400
    """

    def test_employee_roles_update_400_blank_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-update/{}/".format(self.employeeroles_id), {},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['role'][0], "This field is required.")

    """
         Test ID:TS01TD00035
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-update/<Valid ID>/
         Status:failure
         Message:role blank
         Status code:400
    """

    def test_employee_roles_update_400_blank_role_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-update/{}/".format(self.employeeroles_id), {'role': ''},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
         Test ID:TS01TD00036
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-update/<Valid ID>/
         Status:failure
         Message:role corrupt
         Status code:400
    """

    def test_employee_roles_update_400_corrupt_role_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-update/{}/".format(self.employeeroles_id),
                                    {'role': 'ybeckarwtebrkeurwekubcryy'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
         Test ID:TS01TD00037
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-update/<Valid ID>/
         Status:failure
         Message:wrong id
         Status code:400
    """

    def test_employee_roles_update_400_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        employeeroles_id = 1000
        response = self.client.post("/api/employee-roles-update/{}/".format(employeeroles_id),
                                    json.dumps({'role': 'traffic'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "EmployeeRoles Doesn't exists")

    """
         Test ID:TS01TD00038
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-update/<Valid ID>/
         Status:success
         Message:correct role field
         Status code:202
    """

    def test_employee_roles_update_202_correct_role_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-update/{}/".format(self.employeeroles_id),
                                    json.dumps({"role": "traffic"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Role Updated")


class EmployeeRolesDestroyTests(EmployeeRolesTests):

    """
         Test ID:TS01TD00039
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-destroy/<Valid ID>/
         Status:failure
         Message:wrong method
         Status code:405
    """

    def test_employee_roles_delete_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-destroy/{}/".format(self.employeeroles_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01TD00040
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-destroy/<Valid ID>/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_employee_roles_delete_401_no_header(self):
        self.client.credentials()
        response = self.client.post("/api/employee-roles-destroy/{}/".format(self.employeeroles_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01TD00041
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-destroy/<Valid ID>/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_employee_roles_delete_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/employee-roles-destroy/{}/".format(self.employeeroles_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00041
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-destroy/<Valid ID>/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_employee_roles_delete_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/employee-roles-destroy/{}/".format(self.employeeroles_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00042
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-destroy/<Valid ID>/
         Status:failure
         Message:wrong id
         Status code:404
    """

    def test_employee_roles_delete_404_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.employeeroles_id = 1000
        response = self.client.post("/api/employee-roles-destroy/{}/".format(self.employeeroles_id), {'role': 'traffic'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
         Test ID:TS01TD00043
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-destroy/<Valid ID>/
         Status:success
         Message:employee role deleted
         Status code:200
    """

    def test_employee_roles_delete_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-destroy/{}/".format(self.employeeroles_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Role Deleted")


class EmployeeRolesListTests(EmployeeRolesTests):

    """
         Test ID:TS01TD00044
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-list/
         Status:failure
         Message:wrong method
         Status code:405
    """

    def test_employee_roles_list_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeeroleslist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01TD00045
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-list/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_employee_roles_list_401_no_header(self):
        self.client.credentials()
        response = self.client.get(self.employeeroleslist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01TD00046
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-list/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_employee_roles_list_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.employeeroleslist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00046
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-list/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_employee_roles_list_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.employeeroleslist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01TD00047
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-list/
         Status:success
         Message:employee roles list
         Status code:200
    """

    def test_employee_roles_list_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.employeeroleslist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles List")

    """
         Test ID:TS01TD00048
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-list/
         Status:success
         Message:search traffic roles list
         Status code:200
    """

    def test_employee_roles_list_200_search_traffic(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolescreate_url, json.dumps({"role": "traffic"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-list/?search=traffic/",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles List")

    """
         Test ID:TS01TD00049
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-list/
         Status:success
         Message:search corrupt field
         Status code:200
    """

    def test_employee_roles_list_200_search_corrupt_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-list/?search=chmohgm",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles List")

    """
         Test ID:TS01TD00050
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-list/
         Status:success
         Message:list for id
         Status code:200
    """

    def test_employee_roles_list_200_id_7(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-list/?id=7",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles List")

    """
         Test ID:TS01TD00051
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-list/
         Status:success
         Message:list for invalid id
         Status code:200
    """

    def test_employee_roles_list_200_id_567(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-list/?id=567",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles List")

    """
         Test ID:TS01TD00052
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-list/
         Status:success
         Message:list for range
         Status code:200
    """

    def test_employee_roles_list_200_range(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-list/?id_range_0=4&id_range_1=8",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles List")

    """
          Test ID:TS01TD00053
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-list/
          Status:success
          Message:list for created on
          Status code:200
    """

    def test_employee_roles_list_200_created_on(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-list/?created_on=2018-07-27",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles List")
    """
          Test ID:TS01TD00054
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-list/
          Status:success
          Message:wrong created on
          Status code:200
    """

    def test_employee_roles_list_200_wrong_created_on_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-list/?created_on=2018-07-31",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles List")








