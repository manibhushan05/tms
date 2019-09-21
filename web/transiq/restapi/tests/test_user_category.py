import json

from model_mommy import mommy
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User

from authentication.models import Profile
from restapi.models import UserCategory


class UserCategoryTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.usercategory_list_url = reverse('usercategory_list')
        self.usercategory_create_url = reverse('usercategory_create')

        self.user = User.objects.create_user(username='text1234',
                                             email='harsh@gmail.com',
                                             password='text1234')
        self.profile = mommy.make(Profile, user=self.user)

        self.login_data = self.client.post(self.login_url, {'username': 'text1234', 'password': 'text1234'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = 'Token {}'.format(self.login_data['token'])

        user_category = mommy.make(UserCategory)
        self.category_id = user_category.id


class UserCategoryListTests(UserCategoryTests):

    """
         Test ID:TS01AH00047
         Created By:Hari
         Created On:05/12/2018
         Scenario:list user details/
         Status:failur
         Message:no header
         Status code:401
    """

    def test_user_category_list_401_no_header(self):
        # Negative test case for getting user category list with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get(self.usercategory_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01AH00048
         Created By:Hari
         Created On:05/12/2018
         Scenario:list user details/
         Status:failure
         Message:expired header
         Status code:401
    """
    def test_user_category_list_401_expired_header(self):
        # Negative test case for getting user category list with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.usercategory_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid token.')

    """
         Test ID:TS01AH00048
         Created By:Hari
         Created On:05/12/2018
         Scenario:list user details/
         Status:failure
         Message:expired header
         Status code:401
    """
    def test_user_category_list_401_wrong_token(self):
        # Negative test case for getting user category list with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.usercategory_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid token.')


    """
         Test ID:TS01AH00049
         Created By:Hari
         Created On:05/12/2018
         Scenario:list user details/
         Status:failure
         Message:wrong method
         Status code:401
    """

    def test_user_category_list_405_wrong_method(self):
        # Negative test for getting user category list with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.usercategory_list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
         Test ID:TS01AH00046
         Created By:Hari
         Created On:05/12/2018
         Scenario:list user details/
         Status:success
         Message:wrong category
         Status code:200
    """

    def test_user_category_list_200(self):
        # Positive for getting user category list
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.usercategory_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], "User Category List")
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

    """
          Test ID:TS01AH00050
          Created By:Hari
          Created On:05/12/2018
          Scenario:list user details/
          Status:success
          Message:User Category List
          Status code:200
    """

    def test_user_category_list_200_search_on_valid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.usercategory_create_url, json.dumps({'category': 'Customer'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        usercategory_id = response.data['data']['id']

        response = self.client.get("/api/usercategory-list/?search={}".format(usercategory_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data'][0]['id']
        self.assertEqual(data, usercategory_id)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], "User Category List")

    """
        Test ID:TS01AH00051
        Created By:Hari
        Created On:05/12/2018
        Scenario:list user details/
        Status:success
        Message:invalid id search
        Status code:200
    """
    def test_user_category_list_200_search_on_invalid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/usercategory-list/?search=1000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data, [])
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], "User Category List")

    """
        Test ID:TS01AH00052
        Created By:Hari
        Created On:05/12/2018
        Scenario:list user details/
        Status:success
        Message:search on customer provided it exists
        Status code:200
    """

    def test_user_category_list_200_search_on_valid_category(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.usercategory_create_url, json.dumps({'category': 'Customer'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get("/api/usercategory-list/?search=customer")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data'][0]['category']
        self.assertEqual(data, 'Customer')
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], "User Category List")

    """
        Test ID:TS01AH00053
        Created By:Hari
        Created On:05/12/2018
        Scenario:list user details/
        Status:success
        Message:search on invalid category
        Status code:200
    """

    def test_user_category_list_200_search_on_invalid_category(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/usercategory-list/?search=shaslajhdl")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data, [])
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], "User Category List")

    """
        Test ID:TS01AH00054
        Created By:Hari
        Created On:05/12/2018
        Scenario:list user details/
        Status:success
        Message:search on valid id
        Status code:200
    """

    def test_user_category_list_200_valid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.usercategory_create_url, json.dumps({'category': 'Customer'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        usercategory_id = response.data['data']['id']

        response = self.client.get("/api/usercategory-list/?id={}".format(usercategory_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data'][0]['id']
        self.assertEqual(data, usercategory_id)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], "User Category List")

    """
        Test ID:TS01AH00055
        Created By:Hari
        Created On:05/12/2018
        Scenario:list user details/
        Status:success
        Message:search on invalid id
        Status code:200
    """

    def test_user_category_list_200_invalid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/usercategory-list/?id=1000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data, [])
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], "User Category List")

    """
        Test ID:TS01AH00056
        Created By:Hari
        Created On:05/12/2018
        Scenario:list user details/
        Status:success
        Message:search on valid category
        Status code:200
    """

    def test_user_category_list_200_valid_category(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.usercategory_create_url, json.dumps({'category': 'Customer'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get("/api/usercategory-list/?category=customer")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data'][0]['category']
        self.assertEqual(data, 'Customer')
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], "User Category List")

    """
        Test ID:TS01AH00057
        Created By:Hari
        Created On:05/12/2018
        Scenario:list user details/
        Status:success
        Message:search on invalid category
        Status code:200
    """

    def test_user_category_list_200_invalid_category(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/usercategory-list/?category=shaslajhdl")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data, [])
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], "User Category List")


class UserCategoryCreateTests(UserCategoryTests):

    """
        Test ID:TS01AH00059
        Created By:Hari
        Created On:05/12/2018
        Scenario:create user details/
        Status:failure
        Message:no header
        Status code:401
    """

    def test_user_category_create_401_no_header(self):
        # Negative test case of user category create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(self.usercategory_create_url, {'category': 'Customer'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    """
         Test ID:TS01AH00060
         Created By:Hari
         Created On:05/12/2018
         Scenario:create user details/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_user_category_create_401_expired_header(self):
        # Negative test case of user category create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.usercategory_create_url, {'category': 'Customer'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid token.')

    """
        Test ID:TS01AH00060
        Created By:Hari
        Created On:05/12/2018
        Scenario:create user details/
        Status:failure
        Message:wrong token
        Status code:401
    """

    def test_user_category_create_401_wrong_token(self):
        # Negative test case of user category create with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.usercategory_create_url, {'category': 'Customer'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid token.')

    """
        Test ID:TS01AH00061
        Created By:Hari
        Created On:05/12/2018
        Scenario:create user details/
        Status:failure
        Message:wrong method
        Status code:405
    """

    def test_user_category_create_405_wrong_method(self):
        # Negative test for getting user category create with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.usercategory_create_url, {'category': 'Customer'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
            Test ID:TS01AH00064
            Created By:Hari
            Created On:05/12/2018
            Scenario:create user details/
            Status:failure
            Message:more than 15 characters
            Status code:405
        """

    def test_user_category_create_400_category_more_than_15_chars(self):
        # Negative test case of user category create with HTTP Header Authorization token and category than 15 chars
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.usercategory_create_url, json.dumps({'category': 'hjhjhjhjhjhjhhjhjhjhjhjhhhjjh'}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'Error')
        self.assertEqual(response.data['msg'], "User not Created")
        self.assertEqual(response.data['data']['category'][0], "Ensure this field has no more than 15 characters.")

    """
         Test ID:TS01AH00060
         Created By:Hari
         Created On:05/12/2018
         Scenario:create user details/
         Status:success
         Message:User created
         Status code:201
    """

    def test_user_category_create_201(self):
        # Positive test case of user category create with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.usercategory_create_url, json.dumps({'category': 'Customer'}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'Success')
        self.assertEqual(response.data['msg'], "User Created")

    """
         Test ID:TS01AH00062
         Created By:Hari
         Created On:05/12/2018
         Scenario:create user details/
         Status:success
         Message:User created
         Status code:201
    """

    def test_user_category_create_400_no_body(self):
        # Positive test case of user category create with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.usercategory_create_url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'Error')
        self.assertEqual(response.data['msg'], "User not Created")
        self.assertEqual(response.data['data']['category'][0], "This field is required.")

    """
         Test ID:TS01AH00063
         Created By:Hari
         Created On:05/12/2018
         Scenario:create user details/
         Status:success
         Message:User created
         Status code:201
    """

    def test_user_category_create_400_empty_category(self):
        # Positive test case of user category create with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.usercategory_create_url, json.dumps({'category': ''}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'Error')
        self.assertEqual(response.data['msg'], "User not Created")
        self.assertEqual(response.data['data']['category'][0], "This field may not be blank.")

class UserCategoryDetailTests(UserCategoryTests):

    """
         Test ID:TS01AH00080
         Created By:Hari
         Created On:05/12/2018
         Scenario:user-category-details/
         Status:failure
         Message:no header
         Status code:401
    """

    def test_user_category_detail_401_no_header(self):
        # Negative test case for getting user category detail with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/usercategory-detail/{}/".format(self.category_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS01AH00081
         Created By:Hari
         Created On:05/12/2018
         Scenario:user-category-details/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_user_category_detail_401_expired_header(self):
        # Negative test case for getting user category detail with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/usercategory-detail/{}/".format(self.category_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
             Test ID:TS01AH00081
             Created By:Hari
             Created On:05/12/2018
             Scenario:user-category-details/
             Status:failure
             Message:wrong header
             Status code:401
    """

    def test_user_category_detail_401_wrong_token(self):
        # Negative test case for getting user category detail with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/usercategory-detail/{}/".format(self.category_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
             Test ID:TS01AH00081*
             Created By:Hari
             Created On:05/12/2018
             Scenario:user-category-details/
             Status:failure
             Message:wrong method
             Status code:405
    """

    def test_user_category_detail_405_wrong_method(self):
        # Negative test for getting user category detail with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/usercategory-detail/{}/".format(self.category_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
             Test ID:TS01AH00082
             Created By:Hari
             Created On:05/12/2018
             Scenario:user-category-details/
             Status:failure
             Message:wrong id
             Status code:404
    """

    def test_user_category_detail_404_wrong_id(self):
        # Negative test for getting user category detail with wrong id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.category_id = 100
        response = self.client.get("/api/usercategory-detail/{}/".format(self.category_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
                 Test ID:TS01AH00083
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-details/
                 Status:success
                 Message:details verified
                 Status code:404
    """
    def test_user_category_detail_200(self):
        # Positive for getting user category detail
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/usercategory-detail/{}/".format(self.category_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserCategoryUpdateTests(UserCategoryTests):

    """
                 Test ID:TS01AH00072
                 Created By:Hari
                 Created On:05/12/2018
                 Scenario:user-category-update/
                 Status:failure
                 Message:no header
                 Status code:401
    """

    def test_user_category_update_401_no_header(self):
        # Negative test for updating user category with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.put("/api/usercategory-update/{}/".format(self.category_id),
                                   {'category': 'Customer'}, content_type='application/json')
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

    def test_user_category_update_401_expired_header(self):
        # Negative test case for updating user category with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put("/api/usercategory-update/{}/".format(self.category_id),
                                   {'category': 'Customer'}, content_type='application/json')
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

    def test_user_category_update_401_wrong_token(self):
        # Negative test case for updating user category with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4adhfh137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/usercategory-update/{}/".format(self.category_id),
                                    {'category': 'Customer'}, content_type='application/json')
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

    def test_user_category_update_405_wrong_method(self):
        # Negative test for updating user category with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/usercategory-update/{}/".format(self.category_id),
                                   {'category': 'Customer'}, content_type='application/json')
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

    def test_user_category_update_400_wrong_id(self):
        # Negative test for updating user category with wrong id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.category_id = 100
        response = self.client.put("/api/usercategory-update/{}/".format(self.category_id),
                                   {'category': 'Customer'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Failure")
        self.assertEqual(response.data['msg'], "User Doesn't exists")

    """
                   Test ID:TS01AH00076
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:category empty
                   Status code:400
    """

    def test_user_category_update_400_category_empty(self):
        # Negative test case for updating user category with HTTP Header Authorization token and rate not integer
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put("/api/usercategory-update/{}/".format(self.category_id),
                                   json.dumps({'category': ''}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['category'][0], "This field may not be blank.")
        self.assertEqual(response.data['status'], "Error")
        self.assertEqual(response.data['msg'], "User not Updated")

    """
                   Test ID:TS01AH00077
                   Created By:Hari
                   Created On:05/12/2018
                   Scenario:user-category-update/
                   Status:failure
                   Message:category more than 15 characters
                   Status code:401
    """

    def test_user_category_update_400_category_more_than_15_chars(self):
        # Negative test case for updating user category with HTTP Header Authorization token and category more than 15 chars
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put("/api/usercategory-update/{}/".format(self.category_id),
                                   {'category': 'Customer,Supplier,Driver'},
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

    def test_user_category_update_202(self):
        # Positive test case for updating user category with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put("/api/usercategory-update/{}/".format(self.category_id),
                                    json.dumps({'category': 'Customer'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)


class UserCategoryDestroyTests(UserCategoryTests):

    def test_user_category_destroy_405_wrong_method(self):
        # Negative test for destroying user category with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/usercategory-destroy/{}/".format(self.category_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
            Test ID:TS01AH00080
            Created By:Hari
            Created On:05/12/2018
            Scenario:user-category-destroy/
            Status:failure
            Message:no header
            Status code:401
    """

    def test_user_category_destroy_401_no_header(self):
        # Negative test case for destroying user category with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.delete("/api/usercategory-destroy/{}/".format(self.category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
                Test ID:TS01AH00081
                Created By:Hari
                Created On:05/12/2018
                Scenario:user-category-destroy/
                Status:failure
                Message:expired header
                Status code:401
    """

    def test_user_category_destroy_401_expired_header(self):
        # Negative test case for destroying user category with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete("/api/usercategory-destroy/{}/".format(self.category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
                Test ID:TS01AH00081
                Created By:Hari
                Created On:05/12/2018
                Scenario:user-category-destroy/
                Status:failure
                Message:expired header
                Status code:401
    """

    def test_user_category_destroy_401_wrong_token(self):
        # Negative test case for destroying user category with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.delete("/api/usercategory-destroy/{}/".format(self.category_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'],"Invalid token.")

    """
                           Test ID:TS01AH00079
                           Created By:Hari
                           Created On:05/12/2018
                           Scenario:user-category-destroy/
                           Status:success
                           Message:destroyed
                           Status code:200
    """

    def test_user_category_destroy_200(self):
        # Positive for destroying user category
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete("/api/usercategory-destroy/{}/".format(self.category_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
