import json

from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import Profile
from employee.models import Employee
from restapi.models import TaskDashboardFunctionalities, EmployeeRoles, EmployeeRolesFunctionalityMapping
from utils.models import AahoOffice


class ErfmTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.erfmlist_url = reverse('employee_roles_functionalities_mapping_list/')
        self.erfmcreate_url = reverse('employee_roles_functionalities_mapping_create/')

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
        self.aaho_office = mommy.make(AahoOffice)
        self.employee = mommy.make(Employee, office=self.aaho_office)
        self.employee_id = self.employee.id
        self.employee_roles = mommy.make(EmployeeRoles)
        self.employeeroles_id = self.employee_roles.id
        self.taskdf = mommy.make(TaskDashboardFunctionalities)
        self.functionality = self.taskdf.functionality
        self.tdid = self.taskdf.id
        self.erfm = mommy.make(EmployeeRolesFunctionalityMapping, td_functionality=self.taskdf,
                               employee_role=self.employee_roles, caption="Bharat")
        self.erfm_id = self.erfm.id
        self.caption = self.erfm.caption


class ErfmCreateTests(ErfmTests):
    """
         Test ID:TS02RQ00006
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong content type
         Status code:415
    """

    def test_erfm_create_415_header_with_wrong_content_type(self):
        # Negative test case of req quotes create with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.erfmcreate_url, json.dumps({"td_functionality_id": self.tdid,
                                                                     "employee_role_id": self.employeeroles_id,
                                                                     "caption": self.caption
                                                                     }), content_type='application/pdf')
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

    def test_erfm_create_401_no_header(self):
        # Negative test case of req quotes create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(self.erfmcreate_url, {"td_functionality_id": self.tdid,
                                                          "employee_role_id": self.employeeroles_id,
                                                          "caption": self.caption
                                                          })
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

    def test_erfm_create_401_expired_header(self):
        # Negative test case of req quotes create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.erfmcreate_url, json.dumps({"td_functionality_id": self.tdid,
                                                                     "employee_role_id": self.employeeroles_id,
                                                                     "caption": self.caption
                                                                     }), content_type='application/json')
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

    def test_erfm_create_401_wrong_token(self):
        # Negative test case of req quotes create with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.erfmcreate_url, json.dumps({"td_functionality_id": self.tdid,
                                                                     "employee_role_id": self.employeeroles_id,
                                                                     "caption": self.caption
                                                                     }), content_type='application/json')
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

    def test_erfm_create_400_emptybody(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and wrong vehicle_no
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.erfmcreate_url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['td_functionality_id'][0], "This field is required.")
        self.assertEqual(response.data['employee_role_id'][0], "This field is required.")
        self.assertEqual(response.data['caption'][0], "This field is required.")

    """
         Test ID:TS02RQ00010
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong requirement
         Status code:400
    """

    def test_erfm_create_400_fields_empty(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and wrong requirement_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.erfmcreate_url, json.dumps({"td_functionality_id": "",
                                                                     "employee_role_id": "",
                                                                     "caption": ""
                                                                     }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['td_functionality_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_role_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['caption'][0], "This field may not be blank.")

    """
         Test ID:TS02RQ00011
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong supplier
         Status code:400
    """

    def test_erfm_create_400_corrupt_fields(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and wrong broker_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.erfmcreate_url, json.dumps({"td_functionality_id": "jhg",
                                                                     "employee_role_id": "dsfy",
                                                                     "caption": "jhgfq"
                                                                     }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['td_functionality_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_role_id'][0], "A valid integer is required.")

    def test_erfm_create_400_non_existent_tdid(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and wrong broker_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.erfmcreate_url, json.dumps({"td_functionality_id": 324223,
                                                                     "employee_role_id": self.employee_roles,
                                                                     "caption": self.caption
                                                                     }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_erfm_create_400_non_existent_employeeid(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and wrong broker_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.erfmcreate_url, json.dumps({"td_functionality_id": self.tdid,
                                                                     "employee_role_id": 7643645,
                                                                     "caption": "jhgfq"
                                                                     }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
         Test ID:TS02RQ00012
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:rate not integer
         Status code:400
    """

    def test_erfm_create_uniquefield(self):
        # Negative test case of tdf create with HTTP Header Authorization token and functionality not unique
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.erfmcreate_url, json.dumps({"td_functionality_id": self.tdid,
                                                                     "employee_role_id": self.employeeroles_id,
                                                                     "caption": "Inward Entry"
                                                                     }), content_type='application/json')
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

    def test_erfm_create_201(self):
        # Positive test case of req quotes create with HTTP Header Authorization token
        self.taskdf = mommy.make(TaskDashboardFunctionalities)
        self.functionality = self.taskdf.functionality
        self.tdid = self.taskdf.id
        self.erfm = mommy.make(EmployeeRolesFunctionalityMapping, td_functionality=self.taskdf,
                               employee_role=self.employee_roles, caption="Bharat")
        self.erfm_id = self.erfm.id
        self.caption = self.erfm.caption
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.erfmcreate_url,
                                    json.dumps({"td_functionality_id": self.tdid,
                                                "employee_role_id": self.employeeroles_id,
                                                "caption": self.caption
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Functionalities Mapping Created")
