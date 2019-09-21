import json

from model_mommy import mommy
from django.contrib.auth.models import User, Group, Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from utils.models import City
from utils.models import State


class AccountTestSetup(APITestCase):
    '''
        Setup dummy data for tesing purpose
    '''

    def setUp(self):
        self.login_url = reverse('login')

        self.test_user = User.objects.create_user('testUser', 'test@example.com', 'testPassword')
        self.login_data = self.client.post(self.login_url, {"username": "testUser", "password": "testPassword"}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        self.city = mommy.make(City)
        self.permissions = Permission.objects.all()
        self.group = Group.objects.create(name="testGroup")

    def serialize_response_content(self, data):
        return json.loads(data.decode("utf8"))


class UserTest(AccountTestSetup):
    """
        Test cases for User
    """

    def setUp(self):
        super().setUp()
        self.user_data = {
            "is_superuser": False,
            "username": "hitech",
            "password": "12345678",
            "first_name": "Hi-tech Concern",
            "last_name": "stud",
            "email": "hitechconcern2@gmail.com",
            "is_staff": False,
            "is_active": True,
            "groups": [self.group.id],
            "user_permissions": self.permissions.values_list("id", flat=True),
        }
        self.minimum_valid_data = {
            "username": "hitech",
            "password": "12345678"
        }
        self.create_url = reverse("authentication_user_create")
        self.update_url = reverse("authentication_user_update", kwargs={"pk": self.test_user.id})
        self.partial_update_url = reverse("authentication_user_partial_update", kwargs={"pk": self.test_user.id})
        self.retrieve_url = reverse("authentication_user_retrieve", kwargs={"pk": self.test_user.id})
        self.soft_destroy = reverse("authentication_user_soft_destroy", kwargs={"pk": self.test_user.id})
        self.destroy = reverse("authentication_user_destroy", kwargs={"pk": self.test_user.id})

    def test_create_user_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_with_full_valid_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.user_data.copy()
        data["email"] = "invalidEmail"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.user_data.copy()
        data["groups"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["groups"] = "invalidGroup"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["groups"] = [self.group.id * 100]
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_function_except_create_without_token(self):

        response = self.client.put(self.update_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.user_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_functions_except_create_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")

        response = self.client.put(self.update_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.user_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Password is immutable field hence this test case checks that full update should not happen
    def test_update_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_user_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"username": "newName"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("authentication_user_retrieve",
                                   kwargs={"pk": self.test_user.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_soft_destroy_existing_user(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.patch(self.soft_destroy, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
    #
    # def test_soft_destroy_non_existing_user(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     bad_retrieve_url = reverse("authentication_user_soft_destroy",
    #                                kwargs={"pk": self.test_user.id * 1000})
    #     response = self.client.patch(bad_retrieve_url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #
    # def test_destroy_existing_user(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.delete(self.destroy, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    # def test_destroy_non_existing_user(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     bad_retrieve_url = reverse("authentication_user_destroy",
    #                                kwargs={"pk": self.test_user.id * 1000})
    #     response = self.client.delete(bad_retrieve_url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#
# class ProfileTest(AccountTestSetup):
#     """
#         Test cases for creating Profile various data
#         1. Create profile with complete valid data
#
#     """
#
#     def setUp(self):
#         super().setUp()
#         self.profile_data = {
#             "name": "Naruto Uzumaki",
#             "contact_person_name": "Kakakshi Hatake",
#             "contact_person_phone": "9807654312",
#             "phone": "9087564312",
#             "alternate_phone": "9078645123",
#             "email": "konoha@hiddenleaf.com",
#             "alternate_email": "maelstorm@hokage.com",
#             "address": "Konohagakure no sato, Village hidden in the leaf",
#             "pin": "234356",
#             "designation": "Fire Shadow",
#             "comment": "The creed of the ninja",
#             "deleted": False,
#             "deleted_on": None,
#             "user": self.test_user.id,
#             "city": self.city.id
#
#         }
#
#     def test_create_profile_with_valid_data(self):
#         self.client.credentials(HTTP_AUTHORIZATION=self.token)
#         self.profile_create_url = reverse('authentication_user_profile_create')
#         response = self.client.post(self.profile_create_url, self.profile_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)