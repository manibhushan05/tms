import datetime
import json

from model_mommy import mommy
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User, Group

from authentication.models import Profile
from employee.models import Employee
from restapi.models import EmployeeRoles
from sme.models import Sme
from utils.models import State, City, AahoOffice, VehicleCategory


class RequirementTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.reqcreate_url = reverse('requirement_create')
        self.reqlistall_url = reverse('requirements_list')
        self.reqlistfilter_url = reverse('requirement_list_filter')
        self.reqlistuser_url = reverse('requirement_list_user')
        self.employeerolesmappingcreate_url = reverse('employee_roles_mapping_create/')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harshadasawant89@gmail.com',
                                             password='abc12345')
        self.profile = mommy.make(Profile, user=self.user)

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'abc12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = 'Token {}'.format(self.login_data['token'])

        self.client_user = User.objects.create_user(username='david',
                                                    email='harshadasawant89@gmail.com',
                                                    password='pqr12345'
                                                    )
        self.profile = mommy.make(Profile, user=self.client_user)
        self.sme = mommy.make(Sme, name=self.client_user)
        self.sme_group = mommy.make(Group, name='sme')
        self.client_user.groups.add(self.sme_group)
        self.client_id = self.sme.id

        self.login_data = self.client.post(self.login_url, {'username': 'david', 'password': 'pqr12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.customer_token = 'Token {}'.format(self.login_data['token'])

        self.sales_user = User.objects.create_user(username='james',
                                                   email='harshadasawant89@gmail.com',
                                                   password='pwd12345'
                                                   )

        self.sales = mommy.make(Sme, name=self.sales_user)
        self.sales_group = mommy.make(Group, name='sales')
        self.sales_user.groups.add(self.sales_group)

        self.login_data = self.client.post(self.login_url, {'username': 'james', 'password': 'pwd12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.sales_token = "Token {}".format(self.login_data["token"])

        self.state = mommy.make(State, name='maharashtra')
        self.from_city = mommy.make(City)
        self.from_city_id = self.from_city.id
        self.to_city = mommy.make(City, state=self.state)
        self.to_city_id = self.to_city.id
        self.aaho_office = mommy.make(AahoOffice)
        self.aaho_office_id = self.aaho_office.id
        self.vehicle_type = mommy.make(VehicleCategory)
        self.type_of_vehicle_id = self.vehicle_type.id

        self.from_date = (datetime.date.today()).isoformat()
        self.to_date = (datetime.date.today() + datetime.timedelta(days=3)).isoformat()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "to_shipment_date": self.to_date,
                                                                    "from_city_id": self.from_city_id,
                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "tonnage": 44,
                                                                    "material": "Jackets",
                                                                    "req_status": "open",
                                                                    "type_of_vehicle_id": self.type_of_vehicle_id,
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.req_id = response.data['data']['id']

        self.req_status = (
            ('open', 'Open'),
            ('cancelled', 'Cancelled'),
            ('fulfilled', 'Fulfilled'),
            ('unverified', 'Unverified'),
            ('lapsed', 'Lapsed'),
        )

        self.employee = mommy.make(Employee, office=self.aaho_office, username=self.user)
        self.employee_id = self.employee.id
        self.employee_roles = mommy.make(EmployeeRoles, role='tech')
        self.employeeroles_id = self.employee_roles.id

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesmappingcreate_url,
                                    json.dumps({"employee_id": self.employee_id,
                                                "employee_role_id": self.employeeroles_id,
                                                "employee_status": "active"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.employeerolesmapping_id = response.data['data']['id']


class ReqCreateTests(RequirementTests):

    """
          Test ID:TS02RQ00037
          Created By:Hari
          Created On:11/12/2018
          Scenario:requirement-create/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_req_create_401_no_header(self):
        # Negative test case for creating req with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(self.reqcreate_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
      Test ID:TS02RQ00036
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-create/
      Status:failure
      Message:wrong method
      Status code:405
    """

    def test_req_create_405_wrong_method(self):
        # Negative test for creating req with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.reqcreate_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
      Test ID:TS02RQ00038
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-create/
      Status:failure
      Message:wrong content type
      Status code:415
    """

    def test_req_create_415_header_with_wrong_content_type(self):
        # Negative test case for creating req with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id":   self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "from_city_id": self.from_city_id,
                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "no_of_vehicles": self.type_of_vehicle_id,
                                                                    "material": "Jackets",
                                                                    "req_status": "open",
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}),
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
      Test ID:TS02RQ00039
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-create/
      Status:failure
      Message:blank data
      Status code:400
    """

    def test_req_create_400_blank_data(self):
        # Negative test case for creating req with HTTP Header Authorization token with blank data
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, {}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['client_id'][0], "This field is required.")
        self.assertEqual(response.data['data']['from_shipment_date'][0], "This field is required.")
        self.assertEqual(response.data['data']['from_city_id'][0], "This field is required.")
        self.assertEqual(response.data['data']['to_city_id'][0], "This field is required.")
        self.assertEqual(response.data['data']['req_status'][0], "This field is required.")
        self.assertEqual(response.data['data']['material'][0], "This field is required.")
        self.assertEqual(response.data['data']['aaho_office_id'][0], "This field is required.")

    """
         Test ID:TS02RQ00040
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:blank client id
         Status code:400
    """
    def test_req_create_400_wrong_client_id(self):
        # Negative test case for creating req with HTTP Header Authorization token with wrong client id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": 455233,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect client ")


    """
         Test ID:TS02RQ00041
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:client id cannot be a string
         Status code:400
    """

    def test_req_create_400_client_id_as_string(self):
        # Negative test case for creating req with HTTP Header Authorization token with client id as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": "hihkhhd",
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['client_id'][0], "A valid integer is required.")

    """
         Test ID:TS02RQ00042
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:blank from shipment data
         Status code:400
    """

    def test_req_create_400_blank_from_shipment_date(self):
        # Negative test case for creating req with HTTP Header Authorization token with blank from shipment date
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": "",
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['from_shipment_date'][0], "This field may not be blank.")

    """
         Test ID:TS02RQ00043
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:shipment date with wrong format
         Status code:400
    """

    def test_req_create_400_from_shipment_date_with_wrong_date_format(self):
        # Negative test case for creating req with HTTP Header Authorization token and from_shipment_date with wrong date format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": "19-06-2018",
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect date format, should be YYYY-MM-DD")

    """
         Test ID:TS02RQ00044
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:wrong from city
         Status code:400
    """

    def test_req_create_400_wrong_from_city_id(self):
        # Negative test case for creating req with HTTP Header Authorization token with wrong from_city_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": 379577495,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect from city ")

    """
         Test ID:TS02RQ00045
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:city id cannot be a string
         Status code:400
    """

    def test_req_create_400_from_city_id_as_string(self):
        # Negative test case for creating req with HTTP Header Authorization token with from_city as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": "hgdgxuu",
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['from_city_id'][0], "A valid integer is required.")

    """
         Test ID:TS02RQ00046
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:wrong to city id
         Status code:400
    """

    def test_req_create_400_wrong_to_city_id(self):
        # Negative test case for creating req with HTTP Header Authorization token with wrong to_city_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": 807875765,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect to city ")

    """
         Test ID:TS02RQ00047
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:to city id cannot be a string
         Status code:400
    """

    def test_req_create_400_to_city_id_as_string(self):
        # Negative test case for creating req with HTTP Header Authorization token with to_city_id as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": "hjfhjkhd",
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['to_city_id'][0], "A valid integer is required.")

    """
         Test ID:TS02RQ00048
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:wrong aaho id
         Status code:400
    """

    def test_req_create_400_wrong_aaho_id(self):
        # Negative test case for creating req with HTTP Header Authorization token with wrong aaho_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": 781,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect Aaho Office")

    """
         Test ID:TS02RQ00049
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:aaho id cannot be a string
         Status code:400
    """

    def test_req_create_400_aaho_id_as_string(self):
        # Negative test case for creating req with HTTP Header Authorization token with aaho_id as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": "gfkjhdkh",
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['aaho_office_id'][0], "A valid integer is required.")

    """
         Test ID:TS02RQ00050
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:number of vehicles not more than 9999
         Status code:400
    """

    def test_req_create_400_no_of_vehicles_not_more_than_9999(self):
        # Negative test case for creating req with HTTP Header Authorization token and no_of_vehicles not more than 9999
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": 76789798789,
                                                         "tonnage": 44,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry not Created")

    """
         Test ID:TS02RQ00051
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:no. of vehicles can't be a string
         Status code:400
    """

    def test_req_create_400_no_of_vehicles_as_string(self):
        # Negative test case for creating req with HTTP Header Authorization token and no_of_vehicles as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": "gugfhduyrfl",
                                                         "tonnage": 44,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['no_of_vehicles'][0], "A valid integer is required.")

    """
         Test ID:TS02RQ00052
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:material out of range
         Status code:400
    """

    def test_req_create_400_material_out_of_range(self):
        # Negative test case for creating req with HTTP Header Authorization token and material out of range
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "jsffad,udodlkdkldjjoedklsmdljghfghjhgfghfjtftgftehjftghdchf",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['material'][0], "Ensure this field has no more than 35 characters.")

    """
         Test ID:TS02RQ00053
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:wrong req status
         Status code:400
    """

    def test_req_create_400_wrong_req_status(self):
        # Negative test case for creating req with HTTP Header Authorization token and wrong req_status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "jsdgjmg",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry status is wrong")

    """
         Test ID:TS02RQ00054
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:wrong lapsed req status
         Status code:400
    """

    def test_req_create_400_wrong_lapsed_req_status(self):
        # Negative test case for creating req with HTTP Header Authorization token and wrong lapsed req_status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "no_of_vehicles": self.type_of_vehicle_id,
                                                         "material": "Jackets",
                                                         "req_status": "lapsed",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'],"Inquiry status should be open/unverified")

    """
         Test ID:TS02RQ00055
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:no tonnage and number of vehicles
         Status code:400
    """

    def test_req_create_400_no_tonnage_and_no_of_vehicles(self):
        # Negative test case for creating req with HTTP Header Authorization token with no tonnage and no_of_vehicles
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Enter Either Tonnage or No of Vehicles")

    """
         Test ID:TS02RQ00056
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:tonnage out of range
         Status code:400
    """

    def test_req_create_400_tonnage_out_of_range(self):
        # Negative test case for creating req with HTTP Header Authorization token and tonnage out of range
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "tonnage": 3764330234664644,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry not Created")

    """
         Test ID:TS02RQ00057
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:tonnage cant be a string
         Status code:400
    """

    def test_req_create_400_tonnage_as_string(self):
        # Negative test case for creating req with HTTP Header Authorization token and tonnage as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "tonnage": "kuyghgmb",
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['tonnage'][0], "A valid number is required.")

    """
         Test ID:TS02RQ00058
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:rate out of range
         Status code:400
    """

    def test_req_create_400_rate_out_of_range(self):
        # Negative test case for creating req with HTTP Header Authorization token and rate out of range
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "tonnage": 44,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 76754464673455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry not Created")

    """
         Test ID:TS02RQ00059
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:rate cant be a string
         Status code:400
    """

    def test_req_create_400_rate_as_string(self):
        # Negative test case for creating req with HTTP Header Authorization token and rate as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "tonnage": 44,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": "rjfjtfykg",
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['rate'][0], "A valid integer is required.")

    """
         Test ID:TS02RQ00060
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:blank shipment date
         Status code:400
    """

    def test_req_create_400_blank_to_shipment_date(self):
        # Negative test case for creating req with HTTP Header Authorization token with blank to_shipment_date
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "to_shipment_date": "",
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "tonnage": 44,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['to_shipment_date'][0], "This field may not be blank.")

    """
         Test ID:TS02RQ00061
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:to shipment date with wrong date format
         Status code:400
    """

    def test_req_create_400_to_shipment_date_with_wrong_date_format(self):
        # Negative test case for creating req with HTTP Header Authorization token and tp_shipment_date with wrong date format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "to_shipment_date": "20-06-2018",
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "tonnage": 44,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect date format, should be YYYY-MM-DD")

    """
         Test ID:TS02RQ00062
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:wrong type of vehicle id
         Status code:400
    """
    def test_req_create_400_wrong_type_of_vehicle_id(self):
        # Negative test case for creating req with HTTP Header Authorization token and wrong vehilce_type_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "to_shipment_date": self.to_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "tonnage": 44,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "type_of_vehicle_id": 5474875,
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry not Created")

    """
         Test ID:TS02RQ00063
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:vehicle id cant be a string
         Status code:400
    """

    def test_req_create_400_type_of_vehicle_id_as_string(self):
        # Negative test case for creating req with HTTP Header Authorization token and type_of_vehicle_id as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "to_shipment_date": self.to_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "tonnage": 44,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "type_of_vehicle_id": "fkfcktdktfm",
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['type_of_vehicle_id'][0], "A valid integer is required.")

    """
         Test ID:TS02RQ00065
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:to date should be greater than from date
         Status code:400
    """

    def test_req_create_400_to_date_should_be_greater_than_from_date(self):
        # Negative test case for creating req with HTTP Header Authorization token and to_date should be greater than from_date
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "to_shipment_date": "2018-06-19",
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "tonnage": 44,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "type_of_vehicle_id": 5,
                                                         "rate": 3455,
                                                         "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "To Date should be greater than From Date")

    """
         Test ID:TS02RQ00066
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:failure
         Message:remark out of range
         Status code:400
    """

    def test_req_create_400_remark_out_of_range(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                         "from_shipment_date": self.from_date,
                                                         "to_shipment_date": self.to_date,
                                                         "from_city_id": self.from_city_id,
                                                         "to_city_id": self.to_city_id,
                                                         "aaho_office_id": self.aaho_office_id,
                                                         "tonnage": 44,
                                                         "material": "Jackets",
                                                         "req_status": "open",
                                                         "type_of_vehicle_id": self.type_of_vehicle_id,
                                                         "rate": 3455,
                                                         "remark": "qwertyuiopasdfghjklzxcvbnmm"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry not Created")
        self.assertEqual(response.data['data']['remark'][0], "Ensure this field has no more than 25 characters.")

    """
         Test ID:TS02RQ00064
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-create/
         Status:success
         Message:req created
         Status code:400
    """

    def test_req_create_201(self):
        # Positive test case for creating req with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "to_shipment_date": self.to_date,
                                                                    "from_city_id": self.from_city_id,
                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "tonnage": 44,
                                                                    "material": "Jackets",
                                                                    "req_status": "open",
                                                                    "type_of_vehicle_id": self.type_of_vehicle_id,
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Inquiry Created")


class ReqUpdateTests(RequirementTests):

    """
         Test ID:TS02RQ00069
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-update/<Req ID>/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_req_update_401_no_header(self):
        # Negative test case for updating req with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS02RQ00070
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-update/<Req ID>/  
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_req_update_401_expired_header(self):
        # Negative test case for updating req with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS02RQ00070
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-update/<Req ID>/  
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_req_update_401_wrong_token(self):
        # Negative test case for updating req with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS02RQ00067
         Created By:Hari
         Created On:11/12/2018
         Scenario:requirement-update/<Req ID>/  
         Status:failure
         Message:wrong method
         Status code:401
    """
    def test_req_update_405_wrong_method(self):
        # Negative test for updating req with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/requirement-update/{}/".format(self.req_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
        Test ID:TS02RQ00071
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:wrong content type
        Status code:415
    """
    def test_req_update_415_header_with_wrong_content_type(self):
        # Negative test case for updating req with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),
                                    json.dumps({"client_id":   self.client_id,
                                                "from_shipment_date": self.from_date,
                                                "from_city_id": self.from_city_id,
                                                "to_city_id": self.to_city_id,
                                                "aaho_office_id": self.aaho_office_id,
                                                "no_of_vehicles": self.type_of_vehicle_id,
                                                "material": "Jackets",
                                                "req_status": "open",
                                                "rate": 3455,
                                                "remark": "Requirement details"}),
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
        Test ID:TS02RQ00072
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:wrong req id
        Status code:400
    """

    def test_req_update_400_wrong_req_id(self):
        # Negative test for updating req with wrong req_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.req_id = 1000
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry Doesn't exists")

    """
        Test ID:TS02RQ00073
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:blank data
        Status code:400
    """
    def test_req_update_400_blank_data(self):
        # Negative test case for updating req with HTTP Header Authorization token with blank data
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id), {}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['client_id'][0], "This field is required.")
        self.assertEqual(response.data['data']['from_shipment_date'][0], "This field is required.")
        self.assertEqual(response.data['data']['from_city_id'][0], "This field is required.")
        self.assertEqual(response.data['data']['to_city_id'][0], "This field is required.")
        self.assertEqual(response.data['data']['aaho_office_id'][0], "This field is required.")
        self.assertEqual(response.data['data']['material'][0], "This field is required.")
        self.assertEqual(response.data['data']['req_status'][0], "This field is required.")

    """
        Test ID:TS02RQ00074
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:wrong client id
        Status code:400
    """
    def test_req_update_400_wrong_client_id(self):
        # Negative test case for updating req with HTTP Header Authorization token with wrong client id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": 455233,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect client ")

    """
        Test ID:TS02RQ00075
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:client id cant be a string
        Status code:400
    """
    def test_req_update_400_client_id_as_string(self):
        # Negative test case for updating req with HTTP Header Authorization token with client id as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": "hihkhhd",
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['client_id'][0], "A valid integer is required.")

    """
        Test ID:TS02RQ00076
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:shipment date blank
        Status code:400
    """
    def test_req_update_400_blank_from_shipment_date(self):
        # Negative test case for updating req with HTTP Header Authorization token with blank from shipment date
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": "",
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['from_shipment_date'][0], "This field may not be blank.")

    """
        Test ID:TS02RQ00077
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:shipment date with wrong date format
        Status code:400
    """
    def test_req_update_400_from_shipment_date_with_wrong_date_format(self):
        # Negative test case for updating req with HTTP Header Authorization token and from_shipment_date with wrong date format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": "19-06-2018",
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect date format, should be YYYY-MM-DD")

    """
        Test ID:TS02RQ00078
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:wrong city id
        Status code:400
    """
    def test_req_update_400_wrong_from_city_id(self):
        # Negative test case for updating req with HTTP Header Authorization token with wrong from_city_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": 379577495,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect from city ")

    """
        Test ID:TS02RQ00079
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:city id cant be a string
        Status code:400
    """
    def test_req_update_400_from_city_id_as_string(self):
        # Negative test case for updating req with HTTP Header Authorization token with wrong from_city_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": "hgdgxuu",
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['from_city_id'][0], "A valid integer is required.")


    """
        Test ID:TS02RQ00080
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:no header
        Status code:400
    """
    def test_req_update_400_wrong_to_city_id(self):
        # Negative test case for updating req with HTTP Header Authorization token with wrong to_city_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": 807875765897,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect to city ")

    """
        Test ID:TS02RQ00081
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:to city can't be a string
        Status code:400
    """
    def test_req_update_400_to_city_id_as_string(self):
        # Negative test case for updating req with HTTP Header Authorization token with to_city_id as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": "hjfhjkhd",
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['to_city_id'][0], "A valid integer is required.")

    """
        Test ID:TS02RQ00082
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:wrong aaho id
        Status code:401
    """

    def test_req_update_400_wrong_aaho_id(self):
        # Negative test case for updating req with HTTP Header Authorization token with wrong aaho_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": 781,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect Aaho Office")

    """
        Test ID:TS02RQ00083
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:aaho id cant be a string
        Status code:401
    """
    def test_req_update_400_aaho_id_as_string(self):
        # Negative test case for updating req with HTTP Header Authorization token with aaho_id as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": "gfkjhdkh",
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['aaho_office_id'][0], "A valid integer is required.")

    """
        Test ID:TS02RQ00084
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:number of vehicles cannot be more than 9999
        Status code:401
    """

    def test_req_update_400_no_of_vehicles_not_more_than_9999(self):
        # Negative test case for updating req with HTTP Header Authorization token and no_of_vehicles not more than 9999
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": 76789798789,
                                     "tonnage": 44,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry not Updated")

    """
        Test ID:TS02RQ00085
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:no of vehicles cant be a string
        Status code:400
    """

    def test_req_update_400_no_of_vehicles_as_string(self):
        # Negative test case for updating req with HTTP Header Authorization token and no_of_vehicles as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": "gugfhduyrfl",
                                     "tonnage": 44,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['no_of_vehicles'][0], "A valid integer is required.")

    """
        Test ID:TS02RQ00086
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:material out of range
        Status code:400
    """

    def test_req_update_400_material_out_of_range(self):
        # Negative test case for updating req with HTTP Header Authorization token and material out of range
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "jsffad,udodlkdkldjjoedklsmdhmhjkljljkjk,huikyujyhhjgf",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['material'][0], "Ensure this field has no more than 35 characters.")

    """
        Test ID:TS02RQ00087
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:wrong req status
        Status code:401
    """

    def test_req_update_400_wrong_req_status(self):
        # Negative test case for updating req with HTTP Header Authorization token and wrong req_status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "jsdgjmg",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry status is wrong")

    """
        Test ID:TS02RQ00088
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:wrong lapsed req status
        Status code:401
    """

    def test_req_update_400_wrong_lapsed_req_status(self):
        # Negative test case for updating req with HTTP Header Authorization token and wrong lapsed req_status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "no_of_vehicles": self.type_of_vehicle_id,
                                     "material": "Jackets",
                                     "req_status": "lapsed",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'],"Inquiry status should be open/unverified")

    """
        Test ID:TS02RQ00089
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:no header
        Status code:400
    """

    def test_req_update_400_no_tonnage_and_no_of_vehicles(self):
        # Negative test case for updating req with HTTP Header Authorization token with no tonnage and no_of_vehicles
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Enter Either Tonnage or No of Vehicles")

    """
        Test ID:TS02RQ00090
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:tonnage out of range
        Status code:400
    """

    def test_req_update_400_tonnage_out_of_range(self):
        # Negative test case for updating req with HTTP Header Authorization token and tonnage out of range
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "tonnage": 3764330234664644,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry not Updated")

    """
        Test ID:TS02RQ00091
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:tonnage cant be a string
        Status code:400
    """

    def test_req_update_400_tonnage_as_string(self):
        # Negative test case for updating req with HTTP Header Authorization token and tonnage as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "tonnage": "kuyghgmb",
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['tonnage'][0], "A valid number is required.")

    """
        Test ID:TS02RQ00092
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:rate out of range
        Status code:400
    """

    def test_req_update_400_rate_out_of_range(self):
        # Negative test case for updating req with HTTP Header Authorization token and rate out of range
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "tonnage": 44,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 76754464673455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry not Updated")

    """
        Test ID:TS02RQ00093
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:rate cant be a string
        Status code:400
    """

    def test_req_update_400_rate_as_string(self):
        # Negative test case for updating req with HTTP Header Authorization token and rate as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "tonnage": 44,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": "rjfjtfykg",
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['rate'][0], "A valid integer is required.")

    """
        Test ID:TS02RQ00094
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:blank to shipment details
        Status code:400
    """

    def test_req_update_400_blank_to_shipment_date(self):
        # Negative test case for updating req with HTTP Header Authorization token with blank to_shipment_date
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "to_shipment_date": "",
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "tonnage": 44,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['to_shipment_date'][0], "This field may not be blank.")

    """
        Test ID:TS02RQ00095
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:to shipment date with wrong format
        Status code:400
    """

    def test_req_update_400_to_shipment_date_with_wrong_date_format(self):
        # Negative test case for updating req with HTTP Header Authorization token and tp_shipment_date with wrong date format
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "to_shipment_date": "20-06-2018",
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "tonnage": 44,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Incorrect date format, should be YYYY-MM-DD")

    """
        Test ID:TS02RQ00096
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:wrong type of vehicle id
        Status code:400
    """

    def test_req_update_400_wrong_type_of_vehicle_id(self):
        # Negative test case for updating req with HTTP Header Authorization token and wrong vehilce_type_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "to_shipment_date": self.to_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "tonnage": 44,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "type_of_vehicle_id": 5474875,
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry not Updated")

    """
        Test ID:TS02RQ00097
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:vehicle type cannot be a string
        Status code:401
    """

    def test_req_update_400_type_of_vehicle_id_as_string(self):
        # Negative test case for updating req with HTTP Header Authorization token and type_of_vehicle_id as string
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "to_shipment_date": self.to_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "tonnage": 44,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "type_of_vehicle_id": "fkfcktdktfm",
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['type_of_vehicle_id'][0], "A valid integer is required.")

    """
        Test ID:TS02RQ00098
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:to date should be greater than from date
        Status code:400
    """

    def test_req_update_400_to_date_should_be_greater_than_from_date(self):
        # Negative test case for updating req with HTTP Header Authorization token and to_date should be greater than from_date
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "to_shipment_date": "2018-06-19",
                                    "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "tonnage": 44,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "type_of_vehicle_id": 5,
                                     "rate": 3455,
                                     "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "To Date should be greater than From Date")

    """
        Test ID:TS02RQ00099
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-update/<Req ID>/  
        Status:failure
        Message:remark out of range
        Status code:401
    """

    def test_req_create_400_remark_out_of_range(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),json.dumps(
                                    {"client_id": self.client_id,
                                     "from_shipment_date": self.from_date,
                                     "to_shipment_date": self.to_date,
                                     "from_city_id": self.from_city_id,
                                     "to_city_id": self.to_city_id,
                                     "aaho_office_id": self.aaho_office_id,
                                     "tonnage": 44,
                                     "material": "Jackets",
                                     "req_status": "open",
                                     "type_of_vehicle_id": self.type_of_vehicle_id,
                                     "rate": 3455,
                                     "remark": "qwertyuiopasdfghjklzxcvbnmm"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry not Updated")
        self.assertEqual(response.data['data']['remark'][0], "Ensure this field has no more than 25 characters.")

    """
            Test ID:TS02RQ00068
            Created By:Hari
            Created On:11/12/2018
            Scenario:requirement-update/<Req ID>/  
            Status:success
            Message:req updated
            Status code:202
    """

    def test_req_update_202(self):
        # Positive test case for updating req with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),
                                    json.dumps({"client_id": self.client_id,
                                                "from_shipment_date": self.from_date,
                                                "to_shipment_date": self.to_date,
                                                "from_city_id": self.from_city_id,
                                                "to_city_id": self.to_city_id,
                                                "aaho_office_id": self.aaho_office_id,
                                                "tonnage": 44,
                                                "material": "Jackets",
                                                "req_status": "open",
                                                "type_of_vehicle_id": self.type_of_vehicle_id,
                                                "rate": 3455,
                                                "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Inquiry Updated")


class ReqDetailTests(RequirementTests):

    """
            Test ID:TS02RQ00102
            Created By:Hari
            Created On:11/12/2018
            Scenario:requirement-detail/<Req ID>/
            Status:failure
            Message:no header
            Status code:401
    """

    def test_req_detail_401_no_header(self):
        # Negative test case for getting req detail with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/requirement-detail/{}/".format(self.req_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
            Test ID:TS02RQ00103
            Created By:Hari
            Created On:11/12/2018
            Scenario:requirement-detail/<Req ID>/
            Status:failure
            Message:expired header
            Status code:401
    """

    def test_req_detail_401_expired_header(self):
        # Negative test case for getting req detail with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/requirement-detail/{}/".format(self.req_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
        Test ID:TS02RQ00103
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-detail/<Req ID>/
        Status:failure
        Message:wrong token
        Status code:401
    """

    def test_req_detail_401_wrong_token(self):
        # Negative test case for getting req detail with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/requirement-detail/{}/".format(self.req_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
        Test ID:TS02RQ00101
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-detail/<Req ID>/
        Status:failure
        Message:wrong method
        Status code:405
    """
    def test_req_detail_405_wrong_method(self):
        # Negative test for getting req quotes with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-detail/{}/".format(self.req_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
        Test ID:TS02RQ00104
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-detail/<Req ID>/
        Status:failure
        Message:wrong token
        Status code:401
    """

    def test_req_detail_404_wrong_req_id(self):
        # Negative test for getting req detail with wrong req_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.req_id = 1000
        response = self.client.get("/api/requirement-detail/{}/".format(self.req_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
        Test ID:TS02RQ00105
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-detail/<Req ID>/
        Status:success
        Message:details displayed
        Status code:200
    """

    def test_req_detail_200(self):
        # Positive for getting req detail
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/requirement-detail/{}/".format(self.req_id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "inquiry data")

class ReqListAllTests(RequirementTests):

    """
        Test ID:TS02RQ00107
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-all/
        Status:failure
        Message:no header
        Status code:401
    """

    def test_req_list_all_401_no_header(self):
        # Negative test case for getting all req list with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get(self.reqlistall_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
        Test ID:TS02RQ00108
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-all/
        Status:failure
        Message:expired header
        Status code:401
    """

    def test_req_list_all_401_expired_header(self):
        # Negative test case for getting all req list with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.reqlistall_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
        Test ID:TS02RQ00108
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-all/
        Status:failure
        Message:wrong token
        Status code:401
    """

    def test_req_list_all_401_wrong_token(self):
        # Negative test case for getting all req list with wrong HTTP Header Authorization token
        self.token = 'Token abc'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.reqlistall_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
        Test ID:TS02RQ00106
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-all/
        Status:failure
        Message:wrong method
        Status code:405
    """

    def test_req_list_all_405_wrong_method(self):
        # Negative test for getting all req list with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqlistall_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
        Test ID:TS02RQ00109
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-all/
        Status:success
        Message:test req all
        Status code:200
    """

    def test_req_list_all_200(self):
        # Positive for getting all req list
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.reqlistall_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.req = response.data['data']
        self.total_count = response.data['count']
        self.next = response.data['next']
        self.each_count = len(self.req) * (self.total_count // 25) + self.total_count % 25
        self.assertEqual(self.total_count, self.each_count)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "inquiry data")


class ReqListFilterTests(RequirementTests):

    """
        Test ID:TS02RQ00110
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
        Status:failure
        Message:test req all
        Status code:401
    """

    def test_req_list_filter_401_no_header(self):
        # Negative test case for getting filtered req list with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/requirement-list-filter/?requirement_status={}&aaho_office_id={}".format(self.req_status, self.aaho_office_id))
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

    def test_req_list_filter_401_expired_header(self):
        # Negative test case for getting filtered req list with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/requirement-list-filter/?requirement_status={}&aaho_office_id={}".format(self.req_status, self.aaho_office_id))
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

    def test_req_list_filter_401_wrong_token(self):
        # Negative test case for getting filtered req list with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/requirement-list-filter/?requirement_status={}&aaho_office_id={}".format(self.req_status, self.aaho_office_id))
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

    def test_req_list_filter_405_wrong_method(self):
        # Negative test for getting filtered req list with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-list-filter/?requirement_status={}&aaho_office_id={}".format(self.req_status, self.aaho_office_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
        Test ID:TS02RQ00116
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
        Status:failure
        Message:wrong req status
        Status code:400
    """

    def test_req_list_filter_400_wrong_req_status(self):
        # Negative test for getting filtered req list with wrong req_status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.req_status = "jgfdrfty"
        response = self.client.get("/api/requirement-list-filter/?requirement_status={}&aaho_office_id={}".format(self.req_status, self.aaho_office_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry status is wrong")

    """
        Test ID:TS02RQ00117
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
        Status:failure
        Message:wrong req aaho office id
        Status code:400
    """

    def test_req_list_filter_400_wrong_req_aaho_office_id(self):
        # Negative test for getting filtered req list with wrong aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.aaho_office_id = 1000
        response = self.client.get("/api/requirement-list-filter/?requirement_status={}&aaho_office_id={}".format(self.req_status, self.aaho_office_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry status is wrong")

    """
        Test ID:TS02RQ00118
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
        Status:failure
        Message:wrong req aaho office id
        Status code:200
    """

    def test_req_list_filter_400_wrong_req_status_and_aaho_ofice_id(self):
        # Negative test for getting filtered req list with wrong req_status and aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.req_status = "hdgdks"
        self.aaho_office_id = 1000
        response = self.client.get("/api/requirement-list-filter/?requirement_status={}&aaho_office_id={}".format(self.req_status, self.aaho_office_id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Inquiry status is wrong")

    """
        Test ID:TS02RQ00118
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
        Status:failure
        Message:wrong req aaho office id
        Status code:200
    """

    def test_req_list_filter_400_no_req_status(self):
        # Negative test for getting filtered req list with no req_status
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/requirement-list-filter/?requirement_status={}&aaho_office_id={}".format(self.req_status, self.aaho_office_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")

    """
            Test ID:TS02RQ00119
            Created By:Hari
            Created On:11/12/2018
            Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
            Status:failure
            Message:wrong req aaho office id
            Status code:200
    """

    def test_req_list_filter_400_no_aaho_office_id(self):
        # Negative test for getting filtered req list with no aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/requirement-list-filter/?requirement_status={}&aaho_office_id={}".format(self.req_status, self.aaho_office_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")

    """
        Test ID:TS02RQ00119
        Created By:Hari
        Created On:11/12/2018
        Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
        Status:success
        Message:req list filter
        Status code:200
    """

    def test_req_list_filter_200(self):
        # Positive test case for getting filtered req list with correct req_status and aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.reqlistfilter_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.req = response.data['data']
        self.total_count = response.data['count']
        self.next = response.data['next']
        self.each_count = len(self.req) * (self.total_count // 25) + self.total_count % 25
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "inquiry data")
        self.assertEqual(self.total_count, self.each_count)

    """
       Test ID:TS02RQ00120
       Created By:Hari
       Created On:11/12/2018
       Scenario:requirement-list-filter/?requirement_status=<REQ STATUS>&aaho_office_id=<AAHO OFFICE ID>
       Status:failure
       Message:req list filter
       Status code:200
    """

    def test_req_list_filter_200_correct_req_status_and_aaho_office_id(self):
        # Positive test case for getting filtered req list with correct req_status and aaho_office_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.reqlistfilter_url, kwargs={"requirement_status": self.req_status, "aaho_office_id":self.aaho_office_id })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.req = response.data['data']
        self.total_count = response.data['count']
        self.next = response.data['next']
        self.each_count = len(self.req)*(self.total_count//25)+self.total_count % 25
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "inquiry data")
        self.assertEqual(self.total_count, self.each_count)


class ReqListUserTests(RequirementTests):

    """
          Test ID:TS02RQ00124
          Created By:Hari
          Created On:11/12/2018
          Scenario:requirement-list-user/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_req_list_user_401_no_header(self):
        # Negative test case for getting user req list no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get(self.reqlistuser_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
      Test ID:TS02RQ00125
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:failure
      Message:no header
      Status code:401
    """

    def test_req_list_user_401_expired_header(self):
        # Negative test case for getting user req list with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.reqlistuser_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
      Test ID:TS02RQ00125
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:failure
      Message:wrong token
      Status code:401
    """

    def test_req_list_user_401_wrong_token(self):
        # Negative test case for getting user req list with wrong HTTP Header Authorization token
        token = '806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.reqlistuser_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
      Test ID:TS02RQ00123
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:failure
      Message:wrong method
      Status code:405
    """

    def test_req_list_user_405_wrong_method(self):
        # Negative test for getting user req list with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.post(self.reqlistuser_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
      Test ID:TS02RQ00126
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:failure
      Message:token of sales or customer
      Status code:200
    """

    def test_req_list_user_200_token_of_sales_or_customer(self):
        # Positive test case for getting user req list with token of sales or customer
        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "to_shipment_date": self.to_date,
                                                                    "from_city_id": self.from_city_id,
                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "tonnage": 44,
                                                                    "material": "Jackets",
                                                                    "req_status": "open",
                                                                    "type_of_vehicle_id": self.type_of_vehicle_id,
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.get(self.reqlistuser_url)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "inquiry data")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.req = response.data['data']
        self.total_count = response.data['count']
        self.next = response.data['next']
        self.each_count = len(self.req)

        while self.next is not None:
            response = self.client.get(self.next)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.req = response.data['data']
            self.each_count += len(self.req)
            self.next = response.data['next']

        self.assertEqual(self.total_count, self.each_count)

        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "to_shipment_date": self.to_date,
                                                                    "from_city_id": self.from_city_id,
                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "tonnage": 44,
                                                                    "material": "Jackets",
                                                                    "req_status": "open",
                                                                    "type_of_vehicle_id": self.type_of_vehicle_id,
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.get(self.reqlistuser_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.req = response.data['data']
        self.total_count = response.data['count']
        self.next = response.data['next']
        self.each_count = len(self.req)

        while self.next is not None:
            response = self.client.get(self.next)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.req = response.data['data']
            self.each_count += len(self.req)
            self.next = response.data['next']

        self.assertEqual(self.total_count, self.each_count)

    """
      Test ID:TS02RQ00127
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:failure
      Message:token of neither sales or customer
      Status code:400
    """

    def test_req_list_user_400_token_of_neither_sales_nor_customer(self):
        # Negative test case for getting user req list with token of neither sales nor customer
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.reqlistuser_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Does Not support this user")

    """
      Test ID:TS02RQ00128
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:success
      Message:token of customer of created req
      Status code:200
    """

    def test_req_list_user_200_token_of_customer_of_created_req(self):
        # Positive test case for getting user req list with req created by sales and token of customer of created req
        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "to_shipment_date": self.to_date,
                                                                    "from_city_id": self.from_city_id,
                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "tonnage": 44,
                                                                    "material": "Jackets",
                                                                    "req_status": "open",
                                                                    "type_of_vehicle_id": self.type_of_vehicle_id,
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.get(self.reqlistuser_url)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "inquiry data")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """
      Test ID:TS02RQ00129
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:failure
      Message:token of customer of created req
      Status code:200
    """

    def test_req_list_user_200_token_of_sales_of_created_req(self):
        # Positive test case for getting user req list with created by sales and token of sales of created req
        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "to_shipment_date": self.to_date,
                                                                    "from_city_id": self.from_city_id,
                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "tonnage": 44,
                                                                    "material": "Jackets",
                                                                    "req_status": "open",
                                                                    "type_of_vehicle_id": self.type_of_vehicle_id,
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Inquiry Created")
        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.get(self.reqlistuser_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """
      Test ID:TS02RQ00130
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:success
      Message:req created by customer token
      Status code:200
    """

    def test_req_list_user_200_req_created_by_customer_token_of_customer_of_created_req(self):
        # Positive test case for getting user req list with created by customer and token of customer of created req
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "to_shipment_date": self.to_date,
                                                                    "from_city_id": self.from_city_id,
                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "tonnage": 44,
                                                                    "material": "Jackets",
                                                                    "req_status": "open",
                                                                    "type_of_vehicle_id": self.type_of_vehicle_id,
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Inquiry Created")
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.get(self.reqlistuser_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """
      Test ID:TS02RQ00131
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:success
      Message:req created by customer token of sales
      Status code:200
    """

    def test_req_list_user_200_req_created_by_customer_token_of_sales_of_created_req(self):
        # Positive test case for getting user req list with created by customer and token of customer of created req
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "to_shipment_date": self.to_date,
                                                                    "from_city_id": self.from_city_id,
                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "tonnage": 44,
                                                                    "material": "Jackets",
                                                                    "req_status": "open",
                                                                    "type_of_vehicle_id": self.type_of_vehicle_id,
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Inquiry Created")
        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.get(self.reqlistuser_url)
        self.data = response.data['data']
        self.assertEqual(len(self.data), 0)

    """
      Test ID:TS02RQ00132
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:success
      Message:req list user
      Status code:200
    """

    def test_req_list_user_200_create_update_get(self):
        # Positive test case for getting user req list with created by customer, verified by sales and token of sales of created req
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "to_shipment_date": self.to_date,
                                                                    "from_city_id": self.from_city_id,





                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "tonnage": 44,
                                                                    "material": "Jackets",
                                                                    "req_status": "unverified",
                                                                    "type_of_vehicle_id": self.type_of_vehicle_id,
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.req_id = response.data['data']['id']
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Inquiry Created")
        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),
                                    json.dumps({"client_id": self.client_id,
                                                "from_shipment_date": self.from_date,
                                                "to_shipment_date": self.to_date,
                                                "from_city_id": self.from_city_id,
                                                "to_city_id": self.to_city_id,
                                                "aaho_office_id": self.aaho_office_id,
                                                "tonnage": 44,
                                                "material": "Jackets",
                                                "req_status": "open",
                                                "type_of_vehicle_id": self.type_of_vehicle_id,
                                                "rate": 3455,
                                                "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.get(self.reqlistuser_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """
      Test ID:TS02RQ00133
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:success
      Message:create not update get
      Status code:200
    """

    def test_req_list_user_200_create_not_update_get(self):
        # Positive test case for getting user req list with created by customer, verified by sales and token of sales of created req
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "to_shipment_date": self.to_date,
                                                                    "from_city_id": self.from_city_id,
                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "tonnage": 44,
                                                                    "material": "Jackets",
                                                                    "req_status": "unverified",
                                                                    "type_of_vehicle_id": self.type_of_vehicle_id,
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.req_id = response.data['data']['id']
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Inquiry Created")
        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),
                                    json.dumps({"client_id": self.client_id,
                                                "from_shipment_date": self.from_date,
                                                "to_shipment_date": self.to_date,
                                                "from_city_id": self.from_city_id,
                                                "to_city_id": self.to_city_id,
                                                "aaho_office_id": self.aaho_office_id,
                                                "tonnage": 35,
                                                "material": "Jackets",
                                                "req_status": "unverified",
                                                "type_of_vehicle_id": self.type_of_vehicle_id,
                                                "rate": 3455,
                                                "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.get(self.reqlistuser_url)
        self.data = response.data['data']
        self.assertEqual(len(self.data), 0)

    """
      Test ID:TS02RQ00134
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-list-user/
      Status:success
      Message:create update retreive
      Status code:200
    """

    def test_req_list_user_200_create_update_retrieve(self):
        # Positive test case for getting user req list with created by sales,update by customer and token of sales of created req
        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.post(self.reqcreate_url, json.dumps({"client_id": self.client_id,
                                                                    "from_shipment_date": self.from_date,
                                                                    "to_shipment_date": self.to_date,
                                                                    "from_city_id": self.from_city_id,
                                                                    "to_city_id": self.to_city_id,
                                                                    "aaho_office_id": self.aaho_office_id,
                                                                    "tonnage": 44,
                                                                    "material": "Jackets",
                                                                    "req_status": "open",
                                                                    "type_of_vehicle_id": self.type_of_vehicle_id,
                                                                    "rate": 3455,
                                                                    "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.req_id = response.data['data']['id']
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Inquiry Created")
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.post("/api/requirement-update/{}/".format(self.req_id),
                                    json.dumps({"client_id": self.client_id,
                                                "from_shipment_date": self.from_date,
                                                "to_shipment_date": self.to_date,
                                                "from_city_id": self.from_city_id,
                                                "to_city_id": self.to_city_id,
                                                "aaho_office_id": self.aaho_office_id,
                                                "tonnage": 50,
                                                "material": "Jackets",
                                                "req_status": "unverified",
                                                "type_of_vehicle_id": self.type_of_vehicle_id,
                                                "rate": 5757,
                                                "remark": "Requirement details"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self.client.credentials(HTTP_AUTHORIZATION=self.sales_token)
        response = self.client.get(self.reqlistuser_url)
        self.data = response.data['data']
        self.assertEqual(len(self.data), 0)


class ReqDestroyTests(RequirementTests):

    """
          Test ID:TS02RQ00136
          Created By:Hari
          Created On:11/12/2018
          Scenario:requirement-destroy/<REQ ID>/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_req_destroy_401_no_header(self):
        # Negative test case for  destroying req with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/requirement-destroy/{}/".format(self.req_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS02RQ00137
          Created By:Hari
          Created On:11/12/2018
          Scenario:requirement-destroy/<REQ ID>/
          Status:failure
          Message:expired token
          Status code:401
    """

    def test_req_destroy_401_expired_header(self):
        # Negative test case for destroying req with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        response = self.client.post("/api/requirement-destroy/{}/".format(self.req_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS02RQ00137
          Created By:Hari
          Created On:11/12/2018
          Scenario:requirement-destroy/<REQ ID>/
          Status:failure
          Message:wrong token
          Status code:401
    """

    def test_req_destroy_401_wrong_token(self):
        # Negative test case for destroying req with wrong HTTP Header Authorization token
        self.token = 'Token abc'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-destroy/{}/".format(self.req_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
      Test ID:TS02RQ00135
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-destroy/<REQ ID>/
      Status:failure
      Message:wrong method
      Status code:405
    """

    def test_req_destroy_405_wrong_method(self):
        # Negative test for destroying req with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/requirement-destroy/{}/".format(self.req_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
      Test ID:TS02RQ00138
      Created By:Hari
      Created On:11/12/2018
      Scenario:requirement-destroy/<REQ ID>/
      Status:success
      Message:destroyed
      Status code:200
    """

    def test_req_destroy_200(self):
        # Positive for destroying req
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/requirement-destroy/{}/".format(self.req_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Inquiry deleted")

class ReqUserListTests(RequirementTests):

    """
          Test ID:TS02RQ00140
          Created By:Hari
          Created On:11/12/2018
          Scenario:user-list/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_user_list_401_no_header(self):
        # Negative test case for  destroying req with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/user-list/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS02RQ00141
          Created By:Hari
          Created On:11/12/2018
          Scenario:user-list/
          Status:failure
          Message:expired token
          Status code:401
    """

    def test_user_list_401_expired_header(self):
        # Negative test case for destroying req with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        response = self.client.get("/api/user-list/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS02RQ00141
          Created By:Hari
          Created On:11/12/2018
          Scenario:user-list/
          Status:failure
          Message:wrong token
          Status code:401
    """

    def test_user_list_401_wrong_token(self):
        # Negative test case for destroying req with wrong HTTP Header Authorization token
        self.token = 'Token abc'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/user-list/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
      Test ID:TS02RQ00139
      Created By:Hari
      Created On:11/12/2018
      Scenario:user-list/
      Status:failure
      Message:wrong method
      Status code:405
    """

    def test_user_list_405_wrong_method(self):
        # Negative test for destroying req with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/user-list/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
      Test ID:TS02RQ00142
      Created By:Hari
      Created On:11/12/2018
      Scenario:user-list/
      Status:success
      Message:list the details
      Status code:405
    """

    def test_user_list_200(self):
        # Positive for destroying req
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/user-list/".format(self.req_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "User List")

class ReqCancelTests(RequirementTests):

    """
          Test ID:TS02RQ00145
          Created By:Hari
          Created On:11/12/2018
          Scenario:get-requirement-cancel-reasons/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_req_cancel_401_no_header(self):
        # Negative test case for  destroying req with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/get-requirement-cancel-reasons/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS02RQ00146
          Created By:Hari
          Created On:11/12/2018
          Scenario:get-requirement-cancel-reasons/
          Status:failure
          Message:expired token
          Status code:401
    """

    def test_req_cancel_401_expired_header(self):
        # Negative test case for destroying req with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        response = self.client.get("/api/get-requirement-cancel-reasons/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS02RQ00146
          Created By:Hari
          Created On:11/12/2018
          Scenario:get-requirement-cancel-reasons/
          Status:failure
          Message:wrong token
          Status code:401
    """

    def test_req_cancel_401_wrong_token(self):
        # Negative test case for destroying req with wrong HTTP Header Authorization token
        self.token = 'Token abc'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-requirement-cancel-reasons/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
      Test ID:TS02RQ00144
      Created By:Hari
      Created On:11/12/2018
      Scenario:get-requirement-cancel-reasons/
      Status:failure
      Message:wrong method
      Status code:405
    """

    def test_req_cancel_405_wrong_method(self):
        # Negative test for destroying req with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/get-requirement-cancel-reasons/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
      Test ID:TS02RQ00147
      Created By:Hari
      Created On:11/12/2018
      Scenario:get-requirement-cancel-reasons/
      Status:success
      Message:list the details
      Status code:405
    """

    def test_req_cancel_200(self):
        # Positive for destroying req
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-requirement-cancel-reasons/".format(self.req_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Inquiry Cancellation reasons")



























































