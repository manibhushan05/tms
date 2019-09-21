import json

from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import Profile
from employee.models import Employee
from restapi.models import EmployeeRoles
from utils.models import AahoOffice


class EmployeeRolesMappingTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.employeerolesmappinglist_url = reverse('employee_roles_mapping_list/')
        self.employeerolesmappingcreate_url = reverse('employee_roles_mapping_create/')

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

        self.aaho_office = mommy.make(AahoOffice)
        self.employee = mommy.make(Employee, office=self.aaho_office)
        self.employee_id = self.employee.id
        self.employee_roles = mommy.make(EmployeeRoles)
        self.employeeroles_id = self.employee_roles.id

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": self.employee_id,
                                                "employee_role_id": self.employeeroles_id,
                                                "employee_status": "active"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.employeerolesmapping_id = response.data['data']['id']


class EmployeeRolesMappingCreateTests(EmployeeRolesMappingTests):
    def setUp(self):
        super().setUp()

        self.aaho_office = mommy.make(AahoOffice)
        self.employee = mommy.make(Employee, office=self.aaho_office)
        self.employee_id = self.employee.id
        self.employee_roles = mommy.make(EmployeeRoles, role="traffic")
        self.employeeroles_id = self.employee_roles.id

    """
          Test ID:TS01TD00055
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:wrong method
          Status code:405
    """

    def test_employee_roles_mapping_create_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.employeerolesmappingcreate_url,
                                   {"employee_id": self.employee_id,
                                    "employee_role_id": self.employeeroles_id,
                                    "employee_status": "active"}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00056
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_employee_roles_mapping_create_401_no_header(self):
        self.client.credentials()
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": self.employee_id,
                                     "employee_role_id": self.employeeroles_id,
                                     "employee_status": "active"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00057
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_employee_roles_mapping_create_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": self.employee_id,
                                     "employee_role_id": self.employeeroles_id,
                                     "employee_status": "active"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00057
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:wrong token
          Status code:401
    """

    def test_employee_roles_mapping_create_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": self.employee_id,
                                     "employee_role_id": self.employeeroles_id,
                                     "employee_status": "active"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00059
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:wrong content type
          Status code:415
    """

    def test_employee_roles_mapping_create_415_header_with_wrong_content_type(self):
        # Negative test case of req quotes create with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": self.employee_id,
                                                "employee_role_id": self.employeeroles_id,
                                                "employee_status": "active"}),
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
          Test ID:TS01TD00058
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:blank body
          Status code:400
    """

    def test_employee_roles_mapping_create_400_blank_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesmappingcreate_url, {}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['employee_id'][0], "This field is required.")
        self.assertEqual(response.data['employee_role_id'][0], "This field is required.")
        self.assertEqual(response.data['employee_status'][0], "This field is required.")

    """
          Test ID:TS01TD00060
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:blank fields
          Status code:400
    """

    def test_employee_roles_mapping_create_400_blank_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": "",
                                     "employee_role_id": "",
                                     "employee_status": ""}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['employee_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_role_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_status'][0], "\"\" is not a valid choice.")

    """
          Test ID:TS01TD00061
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:currupt fields
          Status code:400
    """

    def test_employee_roles_mapping_create_400_corrupt_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": "ksln",
                                     "employee_role_id": "shdks",
                                     "employee_status": "shjdsdh"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['employee_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_role_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_status'][0], "\"shjdsdh\" is not a valid choice.")

    """
          Test ID:TS01TD00062
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:incorrect employee id
          Status code:400
    """

    def test_employee_roles_mapping_create_400_incorrect_employee_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": "6179797947",
                                                "employee_role_id": self.employeeroles_id,
                                                "employee_status": "active"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
          Test ID:TS01TD00063
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:incorrect employee role
          Status code:400
    """

    def test_employee_roles_mapping_create_400_incorrect_employee_role_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": self.employee_id,
                                                "employee_role_id": "73837",
                                                "employee_status": "active"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
          Test ID:TS01TD00065
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:success
          Message:correct feilds
          Status code:201
    """

    def test_employee_roles_mapping_create_201_correct_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": self.employee_id,
                                                "employee_role_id": self.employeeroles_id,
                                                "employee_status": "active"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Role Mapping Created")

    """
          Test ID:TS01TD00064
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:duplicate fields
          Status code:401
    """

    def test_employee_roles_mapping_create_400_duplicate_role_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": self.employee_id,
                                                "employee_role_id": self.employeeroles_id,
                                                "employee_status": "active"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": self.employee_id,
                                                "employee_role_id": self.employeeroles_id,
                                                "employee_status": "active"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class EmployeeRolesMappingRetrieveTests(EmployeeRolesMappingTests):

    """
          Test ID:TS01TD00066
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-retrieve/<Valid ID>/
          Status:failure
          Message:wrong method
          Status code:405
    """

    def test_employee_roles_mapping_retrieve_405_wrong_method(self):
        # Negative test for getting req quotes detail with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-mapping-retrieve/{}/".format(self.employeerolesmapping_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00067
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-retrieve/<Valid ID>/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_employee_roles_mapping_retrieve_401_no_header(self):
        # Negative test case of req quotes create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/employee-roles-mapping-retrieve/{}/".format(self.employeerolesmapping_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00068
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-retrieve/<Valid ID>/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_employee_roles_mapping_retrieve_401_expired_header(self):
        # Negative test case of req quotes create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/employee-roles-mapping-retrieve/{}/".format(self.employeerolesmapping_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
           Test ID:TS01TD00068
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-retrieve/<Valid ID>/
           Status:failure
           Message:wrong token
           Status code:401
    """

    def test_employee_roles_mappig_retrieve_401_wrong_token(self):
        # Negative test case of req quotes create with wrong HTTP Header Authorization token
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/employee-roles-mapping-retrieve/{}/".format(self.employeerolesmapping_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
           Test ID:TS01TD00069
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-retrieve/<Valid ID>/
           Status:failure
           Message:wrong id
           Status code:404
    """

    def test_employee_roles_mapping_retrieve_404_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        employeerolesmapping_id = 10000
        response = self.client.get("/api/employee-roles-mapping-retrieve/{}/".format(employeerolesmapping_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
           Test ID:TS01TD00070
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-retrieve/<Valid ID>/
           Status:sucess
           Message:retreive roles
           Status code:200
    """

    def test_employee_roles_mapping_retrieve_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-mapping-retrieve/{}/".format(self.employeerolesmapping_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Role Mapping Retrieved")


class EmployeeRolesMappingUpdateTests(EmployeeRolesMappingTests):

    """
          Test ID:TS01TD00071
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:wrong method
          Status code:405
    """

    def test_employee_roles_mapping_update_405_wrong_method(self):
        # Negative test for getting req quotes detail with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-mapping-update/{}/".format(self.employeerolesmapping_id),
                                   {"employee_id": self.employee_id,
                                    "employee_role_id": self.employeeroles_id,
                                    "employee_status": "active"}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00072
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:wrong method
          Status code:405
    """

    def test_employee_roles_mapping_update_401_no_header(self):
        # Negative test case of req quotes create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/employee-roles-mapping-update/{}/".format(self.employeerolesmapping_id),
                                    json.dumps({"employee_id": self.employee_id,
                                     "employee_role_id": self.employeeroles_id,
                                     "employee_status": "active"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00073
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_employee_roles_mapping_update_401_expired_header(self):
        # Negative test case of req quotes create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/employee-roles-mapping-update/{}/".format(self.employeerolesmapping_id),
                                    json.dumps({"employee_id": self.employee_id,
                                     "employee_role_id": self.employeeroles_id,
                                     "employee_status": "active"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00073
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:wrong token
          Status code:401
    """

    def test_employee_roles_mapping_update_401_wrong_token(self):
        # Negative test case of req quotes create with wrong HTTP Header Authorization token
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/employee-roles-mapping-update/{}/".format(self.employeerolesmapping_id),
                                    json.dumps({"employee_id": self.employee_id,
                                     "employee_role_id": self.employeeroles_id,
                                     "employee_status": "active"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00074
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:wrong content type
          Status code:415
    """

    def test_employee_roles_mapping_update_415_header_with_wrong_content_type(self):
        # Negative test case of req quotes create with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-mapping-update/{}/".format(self.employeerolesmapping_id),
                                    json.dumps({"employee_id": self.employee_id,
                                                "employee_role_id": self.employeeroles_id,
                                                "employee_status": "active"}),
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
          Test ID:TS01TD00075
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:blank body
          Status code:400
    """

    def test_employee_roles_mapping_update_400_blank_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-mapping-update/{}/".format(self.employeerolesmapping_id), {}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['employee_id'][0], "This field is required.")
        self.assertEqual(response.data['employee_role_id'][0], "This field is required.")
        self.assertEqual(response.data['employee_status'][0], "This field is required.")

    """
          Test ID:TS01TD00076
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:blank fields
          Status code:400
    """

    def test_employee_roles_mapping_update_400_blank_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-mapping-update/{}/".format(self.employeerolesmapping_id),
                                    json.dumps({"employee_id": "",
                                     "employee_role_id": "",
                                     "employee_status": ""}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['employee_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_role_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_status'][0], "\"\" is not a valid choice.")

    """
          Test ID:TS01TD00077
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:corrupt fields
          Status code:400
    """

    def test_employee_roles_mapping_update_400_corrupt_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-mapping-update/{}/".format(self.employeerolesmapping_id),
                                    json.dumps({"employee_id": "ksln",
                                     "employee_role_id": "shdks",
                                     "employee_status": "shjdsdh"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['employee_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_role_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_status'][0], "\"shjdsdh\" is not a valid choice.")

    """
          Test ID:TS01TD00078
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:incorrect employee id field
          Status code:400
    """

    def test_employee_roles_mapping_update_400_incorrect_employee_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-mapping-update/{}/".format(self.employeerolesmapping_id),
                                    json.dumps({"employee_id": "6179797947",
                                                "employee_role_id": self.employeeroles_id,
                                                "employee_status": "active"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
          Test ID:TS01TD00079
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:incorrect employee role id field
          Status code:400
    """

    def test_employee_roles_mapping_update_400_incorrect_employee_role_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-mapping-update/{}/".format(self.employeerolesmapping_id),
                                    json.dumps({"employee_id": self.employee_id,
                                                "employee_role_id": "73837",
                                                "employee_status": "active"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
          Test ID:TS01TD00080
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:wrong id field
          Status code:400
    """

    def test_employee_roles_mapping_update_400_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        employeerolesmapping_id = 10000
        response = self.client.post("/api/employee-roles-mapping-update/{}/".format(employeerolesmapping_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "EmployeeRolesMapping Doesn't exists")

    """
          Test ID:TS01TD00081
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:success
          Message:correct field
          Status code:202
    """

    def test_employee_roles_mapping_update_202_correct_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-mapping-update/{}/".format(self.employeerolesmapping_id),
                                    json.dumps({"employee_id": self.employee_id,
                                                "employee_role_id": self.employeeroles_id,
                                                "employee_status": "active"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Role Mapping Updated")


class EmployeeRolesDestroyMappingTests(EmployeeRolesMappingTests):

    """
          Test ID:TS01TD00082
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-destroy/<Valid ID>/
          Status:failure
          Message:wrong method
          Status code:405
    """

    def test_employee_roles_mapping_delete_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-mapping-destroy/{}/".format(self.employeerolesmapping_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00083
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-destroy/<Valid ID>/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_employee_roles_mapping_delete_401_no_header(self):
        self.client.credentials()
        response = self.client.post("/api/employee-roles-mapping-destroy/{}/".format(self.employeerolesmapping_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00084
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-destroy/<Valid ID>/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_employee_roles_mapping_delete_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/employee-roles-mapping-destroy/{}/".format(self.employeerolesmapping_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00084
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-destroy/<Valid ID>/
          Status:failure
          Message:wrong token
          Status code:401
    """

    def test_employee_roles_mapping_delete_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/employee-roles-mapping-destroy/{}/".format(self.employeerolesmapping_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
           Test ID:TS01TD00085
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-destroy/<Valid ID>/
           Status:failure
           Message:wrong id
           Status code:404
    """

    def test_employee_roles_mapping_delete_404_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        employeerolesmapping_id = 1000
        response = self.client.post("/api/employee-roles-mapping-destroy/{}/".format(employeerolesmapping_id), {'role': 'traffic'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
           Test ID:TS01TD00086
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-destroy/<Valid ID>/
           Status:success
           Message:mapping delete
           Status code:200
    """

    def test_employee_roles_mapping_delete_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-mapping-destroy/{}/".format(self.employeerolesmapping_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Role Mapping Deleted")


class EmployeeRolesMappingListTests(EmployeeRolesMappingTests):

    """
               Test ID:TS01TD00087
               Created By:Hari
               Created On:13/12/2018
               Scenario:employee-roles-mapping-list/
               Status:failure
               Message:wrong method
               Status code:405
    """

    def test_employee_roles_mapping_list_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesmappinglist_url, content_type='application/json')
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

    def test_employee_roles_mapping_list_401_no_header(self):
        self.client.credentials()
        response = self.client.get(self.employeerolesmappinglist_url, content_type='application/json')
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

    def test_employee_roles_mapping_list_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.employeerolesmappinglist_url, content_type='application/json')
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

    def test_employee_roles_mapping_list_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.employeerolesmappinglist_url, content_type='application/json')
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

    def test_employee_roles_mapping_list_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.employeerolesmappinglist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Mapping List")

    """
           Test ID:TS01TD00091
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles search by name
           Status code:200
     """

    def test_employee_roles_mapping_list_200_search_by_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-mapping-list/?search=ravi",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Mapping List")

    """
           Test ID:TS01TD00092
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles search by employee status
           Status code:200
    """

    def test_employee_roles_mapping_list_200_search_by_employee_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-mapping-list/?search=active",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Mapping List")

    """
           Test ID:TS01TD00093
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles search by employee role traffic
           Status code:200
    """

    def test_employee_roles_mapping_list_200_search_by_employee_role_traffic(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-mapping-list/?search=traffic",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Mapping List")

    """
           Test ID:TS01TD00094
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles mapping list valid id
           Status code:200
    """

    def test_employee_roles_mapping_list_200_valid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-mapping-list/?id=9",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Mapping List")

    """
         Test ID:TS01TD00095
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-mapping-list/
         Status:success
         Message:employee roles mapping list range
         Status code:200
    """

    def test_employee_roles_mapping_list_200_range(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-mapping-list/?id_range_0=9&id_range_1=10",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Mapping List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_employee_roles_mapping_list_200_employee(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-mapping-list/??employee=harsh",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Mapping List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_list_200_employee_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-mapping-list/??employee_status=active",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Mapping List")

    """
             Test ID:TS01TD00098
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee role
             Status code:200
    """

    def test_employee_roles_mapping_list_200_employee_role(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-mapping-list/??employee_role=traffic",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Mapping List")
