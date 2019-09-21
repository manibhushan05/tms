import json

from model_mommy import mommy
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User, Group

from broker.models import Broker
from employee.models import Employee
from restapi.models import UserCategory, EmployeeRoles, EmployeeRolesMapping, TaskDashboardFunctionalities, \
    EmployeeRolesFunctionalityMapping
from sme.models import Sme
from supplier.models import Supplier


class UserInitialDataTests(APITestCase):

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harsh@gmail.com',
                                             password='text1234')

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'text1234'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        self.customer_user = User.objects.create_user(username='david',
                                                      email='david12@gmail.com',
                                                      password='pqrs1234'
                                                      )

        self.sme = Sme.objects.create(name=self.customer_user)
        sme_group = Group.objects.create(name='sme')
        self.customer_user.groups.add(sme_group)

        user_category = mommy.make(UserCategory, category='Customer')

        self.customer_category_id = user_category.id

        self.login_data = self.client.post(self.login_url, {'username': 'david', 'password': 'pqrs1234'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.customer_token = "Token {}".format(self.login_data["token"])

        self.supplier_user = User.objects.create_user(username='james',
                                                      email='harshadasawant89@gmail.com',
                                                      password='pwd12345'
                                                      )

        self.supplier = Supplier.objects.create(user=self.supplier_user)

        user_supplier_category = mommy.make(UserCategory, category='Supplier')
        self.supplier_category_id = user_supplier_category.id

        self.login_data = self.client.post(self.login_url, {'username': 'james', 'password': 'pwd12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.supplier_token = "Token {}".format(self.login_data["token"])

        self.broker_user = User.objects.create_user(username='sam',
                                                    email='harshadasawant89@gmail.com',
                                                    password='abc12345'
                                                    )

        self.broker = Broker.objects.create(name=self.broker_user)

        user_broker_category = mommy.make(UserCategory, category='Broker')
        self.broker_category_id = user_broker_category.id

        self.login_data = self.client.post(self.login_url, {'username': 'sam', 'password': 'abc12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.broker_token = "Token {}".format(self.login_data["token"])

    """
         Test ID:TS01AH00088
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial data/
         Status:success
         Message:wrong method
         Status code:405
    """

    def test_user_initial_data_405_wrong_method(self):
        # Negative test for getting user initial data with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01AH00089
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_user_initial_data_401_no_header(self):
        # Negative test for getting user initial data with no HTTP Header Authorization token
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01AH00090
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:blank token
         Status code:401
    """

    def test_user_initial_data_401_blank_token(self):
        # Negative test case for getting user initial data with blank HTTP Header Authorization token
        self.token = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01AH00091               
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:wromg token
         Status code:401
    """

    def test_user_initial_data_401_wrong_token(self):
        # Negative test case for getting user initial data with wrong HTTP Header Authorization token

        token = "Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01AH00091
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:expired token
         Status code:401
    """

    def test_user_initial_data_401_expired_token(self):
        # Negative test case for getting user initial data with expired HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01AH00094
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:blank category id
         Status code:400
    """

    def test_user_initial_data_400_blank_category_id(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token but blank category_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.customer_category_id = ""
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['msg'], "category_id field can not be blank")
        self.assertEqual(response.data['status'], "failure")

    """
         Test ID:TS01AH00093
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:user category does not exist
         Status code:401
    """

    def test_user_initial_data_400_wrong_category_id(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token but wrong category id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.customer_category_id = 100
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "User Category Does Not Exist")

    """
         Test ID:TS01AH00096
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:user category cannot be blank
         Status code:400
    """

    def test_user_initial_data_400_non_customer_token(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token of non-customer
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "User Customer does not exist")

    """
         Test ID:TS01AH00095
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:User Category should be a number
         Status code:400
    """

    def test_user_initial_data_400_non_supplier_token(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token of non-supplier
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.supplier_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "User Supplier does not exist")

    """
         Test ID:TS01AH00097
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:User Category should be a a valid one
         Status code:400
    """

    def test_user_initial_data_400_non_broker_token(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token of non-broker
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.broker_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "User Broker does not exist")

    """
         Test ID:TS01AH00098
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:success
         Message:User Category valid 
         Status code:200
    """

    def test_user_initial_data_200_customer_token(self):
        # Positive test case for getting customer token and category_id
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")

    """
         Test ID:TS01AH000100
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:User Category valid
         Status code:200
    """

    def test_user_initial_data_200_supplier_token(self):
        # Positive test case for getting supplier token and category_id
        self.client.credentials(HTTP_AUTHORIZATION=self.supplier_token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.supplier_category_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")

    """
         Test ID:TS01AH00099
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:User Category valid 
         Status code:200
    """

    def test_user_initial_data_200_broker_token(self):
        # Positive test case for getting broker token and category_id
        self.client.credentials(HTTP_AUTHORIZATION=self.broker_token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.broker_category_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")

# class for user-initial-td details
class UserInitialTDFunctionalitiesDataTests(APITestCase):

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harsh@gmail.com',
                                             password='text1234')

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'text1234'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        # Employee
        self.employee_user = User.objects.create_user(username='james',
                                                      email='harshadasawant89@gmail.com',
                                                      password='pwd12345'
                                                      )

        self.employee = Employee.objects.create(username=self.employee_user)

        user_employee_category = mommy.make(UserCategory, category='Employee')
        self.employee_category_name = user_employee_category.category

        self.login_data = self.client.post(self.login_url, {'username': 'james', 'password': 'pwd12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.employee_token = "Token {}".format(self.login_data["token"])

    """
             Test ID:TS01AH00102
             Created By:Hari
             Created On:07/12/2018
             Scenario:get user initial td data/
             Status:failure
             Message:invalid method header
             Status code:405
    """

    def test_user_tb_initial_data_405_wrong_method(self):
        # Negative test for getting user initial data with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
             Test ID:TS01AH00103
             Created By:Hari
             Created On:07/12/2018
             Scenario:get user initial td data/
             Status:failure
             Message:no auth credentials provided
             Status code:401
    """

    def test_user_tb_initial_data_401_no_header(self):
        # Negative test for getting user initial data with no HTTP Header Authorization token
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
             Test ID:TS01AH00104
             Created By:Hari
             Created On:07/12/2018
             Scenario:get user initial td data/
             Status:failure
             Message:blank token
             Status code:401
        """

    def test_user_tb_initial_data_401_blank_token(self):
        # Negative test case for getting user initial data with blank HTTP Header Authorization token
        self.token = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01AH00105
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial td data/
         Status:failure
         Message:wromg token
         Status code:401
    """

    def test_user_tb_initial_data_401_wrong_token(self):
        # Negative test case for getting user initial data with wrong HTTP Header Authorization token

        token = "Token 806fa0efd3ce2khn080f65da4ad5hg3je1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01AH00105
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial td data/
         Status:failure
         Message:expired token
         Status code:401
    """

    def test_user_tb_initial_data_401_expired_token(self):
        # Negative test case for getting user initial data with expired HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
             Test ID:TS01AH00106
             Created By:Hari
             Created On:06/12/2018
             Scenario:get user initial td data/
             Status:failure
             Message:expired token
             Status code:401
    """

    def test_user_tb_initial_data_401_non_employee_category(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token of non-broker
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "User category is not found")

    """
             Test ID:TS01AH00107
             Created By:Hari
             Created On:07/12/2018
             Scenario:get user initial td data/
             Status:failure
             Message:blank category
             Status code:400
        """

    def test_user_tb_initial_data_400_blank_category_name(self):
        # Negative test case for getting user initial td data with HTTP Header Authorization token but blank category
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.employee_category_name = ""
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['msg'], "category field can not be blank")
        self.assertEqual(response.data['status'], "failure")

    """
             Test ID:TS01AH00108
             Created By:Hari
             Created On:07/12/2018
             Scenario:get user td initial data/
             Status:failure
             Message:User Category valid 
             Status code:200
    """

    def test_user_tb_initial_data_200_employee_category_sucess(self):
        # Positive test case for getting employee category
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # self.employee_category_name="employee"
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['msg'], "Employee TD Functionalities retrieved")
        self.assertEqual(response.data['status'], "success")

class UserInitialDataTests(APITestCase):

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harsh@gmail.com',
                                             password='text1234')

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'text1234'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        self.customer_user = User.objects.create_user(username='david',
                                                      email='david12@gmail.com',
                                                      password='pqrs1234'
                                                      )

        self.sme = Sme.objects.create(name=self.customer_user)
        sme_group = Group.objects.create(name='sme')
        self.customer_user.groups.add(sme_group)

        user_category = mommy.make(UserCategory, category='Customer')

        self.customer_category_id = user_category.id

        self.login_data = self.client.post(self.login_url, {'username': 'david', 'password': 'pqrs1234'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.customer_token = "Token {}".format(self.login_data["token"])

        self.supplier_user = User.objects.create_user(username='james',
                                                      email='harshadasawant89@gmail.com',
                                                      password='pwd12345'
                                                      )

        self.supplier = Supplier.objects.create(user=self.supplier_user)

        user_supplier_category = mommy.make(UserCategory, category='Supplier')
        self.supplier_category_id = user_supplier_category.id

        self.login_data = self.client.post(self.login_url, {'username': 'james', 'password': 'pwd12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.supplier_token = "Token {}".format(self.login_data["token"])

        self.broker_user = User.objects.create_user(username='sam',
                                                    email='harshadasawant89@gmail.com',
                                                    password='abc12345'
                                                    )

        self.broker = Broker.objects.create(name=self.broker_user)

        user_broker_category = mommy.make(UserCategory, category='Broker')
        self.broker_category_id = user_broker_category.id

        self.login_data = self.client.post(self.login_url, {'username': 'sam', 'password': 'abc12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.broker_token = "Token {}".format(self.login_data["token"])

    """
         Test ID:TS01AH00088
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial data/
         Status:success
         Message:wrong method
         Status code:405
    """

    def test_user_initial_data_405_wrong_method(self):
        # Negative test for getting user initial data with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01AH00089
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_user_initial_data_401_no_header(self):
        # Negative test for getting user initial data with no HTTP Header Authorization token
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01AH00090
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:blank token
         Status code:401
    """

    def test_user_initial_data_401_blank_token(self):
        # Negative test case for getting user initial data with blank HTTP Header Authorization token
        self.token = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01AH00091
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_user_initial_data_401_wrong_token(self):
        # Negative test case for getting user initial data with wrong HTTP Header Authorization token

        token = "Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01AH00091
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:expired token
         Status code:401
    """

    def test_user_initial_data_401_expired_token(self):
        # Negative test case for getting user initial data with expired HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01AH00094
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:blank category id
         Status code:400
    """

    def test_user_initial_data_400_blank_category_id(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token but blank category_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.customer_category_id = ""
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['msg'], "category_id field can not be blank")
        self.assertEqual(response.data['status'], "failure")

    """
         Test ID:TS01AH00093
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:user category does not exist
         Status code:401
    """

    def test_user_initial_data_400_wrong_category_id(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token but wrong category id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.customer_category_id = 100
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "User Category Does Not Exist")

    """
         Test ID:TS01AH00096
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:user category cannot be blank
         Status code:400
    """

    def test_user_initial_data_400_non_customer_token(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token of non-customer
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "User Customer does not exist")

    """
         Test ID:TS01AH00095
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:User Category should be a number
         Status code:400
    """

    def test_user_initial_data_400_non_supplier_token(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token of non-supplier
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.supplier_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "User Supplier does not exist")

    """
         Test ID:TS01AH00097
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:User Category should be a a valid one
         Status code:400
    """

    def test_user_initial_data_400_non_broker_token(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token of non-broker
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.broker_category_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")

    """
         Test ID:TS01AH00098
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:success
         Message:User Category valid 
         Status code:200
    """

    def test_user_initial_data_200_customer_token(self):
        # Positive test case for getting customer token and category_id
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.customer_category_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """
         Test ID:TS01AH000100
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:User Category valid
         Status code:200
    """

    def test_user_initial_data_200_supplier_token(self):
        # Positive test case for getting supplier token and category_id
        self.client.credentials(HTTP_AUTHORIZATION=self.supplier_token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.supplier_category_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """
         Test ID:TS01AH00099
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial data/
         Status:failure
         Message:User Category valid 
         Status code:200
    """

    def test_user_initial_data_200_broker_token(self):
        # Positive test case for getting broker token and category_id
        self.client.credentials(HTTP_AUTHORIZATION=self.broker_token)
        response = self.client.get("/api/get-user-initial-data/?category_id={}".format(self.broker_category_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

# class for user-initial-td details
class UserInitialTDFunctionalitiesDataTests(APITestCase):

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harsh@gmail.com',
                                             password='text1234')

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'text1234'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        # Employee
        self.employee_user = User.objects.create_user(username='james',
                                                      email='harshadasawant89@gmail.com',
                                                      password='pwd12345'
                                                      )

        self.employee = Employee.objects.create(username=self.employee_user)
        employee_obj= self.employee
        user_employee_category = mommy.make(UserCategory, category='employee')
        self.employee_category_name = user_employee_category.category

        user_employee_roletype = mommy.make(EmployeeRoles, role='ops_executive')
        self.employee_role = user_employee_roletype.role

        user_employee_rolesmapping = mommy.make(EmployeeRolesMapping, employee_status='active',employee_role=user_employee_roletype, employee=employee_obj)
        self.employee_role = user_employee_rolesmapping.employee_status

        user_employee_tdfunc = mommy.make(TaskDashboardFunctionalities, functionality='new_inquiry')
        self.employee_role = user_employee_tdfunc.functionality

        user_employee_erfm = mommy.make(EmployeeRolesFunctionalityMapping, caption='employee_ready',td_functionality=user_employee_tdfunc,employee_role=user_employee_roletype)
        self.employee_role = user_employee_erfm.caption



        self.login_data = self.client.post(self.login_url, {'username': 'james', 'password': 'pwd12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.employee_token = "Token {}".format(self.login_data["token"])

    """
             Test ID:TS01AH00102
             Created By:Hari
             Created On:07/12/2018
             Scenario:get user initial td data/
             Status:failure
             Message:invalid method header
             Status code:405
    """

    def test_user_tb_initial_data_405_wrong_method(self):
        # Negative test for getting user initial data with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
             Test ID:TS01AH00103
             Created By:Hari
             Created On:07/12/2018
             Scenario:get user initial td data/
             Status:failure
             Message:no auth credentials provided
             Status code:401
    """

    def test_user_tb_initial_data_401_no_header(self):
        # Negative test for getting user initial data with no HTTP Header Authorization token
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
             Test ID:TS01AH00104
             Created By:Hari
             Created On:07/12/2018
             Scenario:get user initial td data/
             Status:failure
             Message:blank token
             Status code:401
        """

    def test_user_tb_initial_data_401_blank_token(self):
        # Negative test case for getting user initial data with blank HTTP Header Authorization token
        self.token = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01AH00105
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial td data/
         Status:failure
         Message:wromg token
         Status code:401
    """

    def test_user_tb_initial_data_401_wrong_token(self):
        # Negative test case for getting user initial data with wrong HTTP Header Authorization token

        token = "Token 806fa0efd3ce2khn080f65da4ad5hg3je1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01AH00105
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial td data/
         Status:failure
         Message:expired token
         Status code:401
    """

    def test_user_tb_initial_data_401_expired_token(self):
        # Negative test case for getting user initial data with expired HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS01AH00106
         Created By:Hari
         Created On:06/12/2018
         Scenario:get user initial td data/
         Status:failure
         Message:expired token
         Status code:401
    """

    def test_user_tb_initial_data_401_non_employee_category(self):
        # Negative test case for getting user initial data with HTTP Header Authorization token of non-broker
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Employee Roles not found")

    """
         Test ID:TS01AH00107
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user initial td data/
         Status:failure
         Message:blank category
         Status code:400
    """

    def test_user_tb_initial_data_400_blank_category_name(self):
        # Negative test case for getting user initial td data with HTTP Header Authorization token but blank category
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.employee_category_name = ""
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['msg'], "category field can not be blank")
        self.assertEqual(response.data['status'], "failure")

    """
         Test ID:TS01AH00108
         Created By:Hari
         Created On:07/12/2018
         Scenario:get user td initial data/
         Status:failure
         Message:User Category valid 
         Status code:200
    """

    def test_user_tb_initial_data_200_employee_category_sucess(self):
        # Positive test case for getting employee category
        self.client.credentials(HTTP_AUTHORIZATION=self.employee_token)
        response = self.client.get("/api/get-user-initial-td-functionalities-data/?category={}".format(self.employee_category_name))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['msg'], "Employee TD Functionalities retrieved")
        self.assertEqual(response.data['status'], "success")
