from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class HelperAPISetup(APITestCase):
    """
        Setup dummy data for tesing purpose
    """

    def setUp(self):
        self.test_user1 = User.objects.create_user(username='testUser', email='test1@example.com', password='testPassword')
        self.test_user2 = User.objects.create_user(username='1212121212', email='test2@example.com', password='testPassword')
        self.test_user3 = User.objects.create_user(username='testUser', email='test3@example.com', password='testPassword')


# class GenerateUserNameTest(HelperAPISetup):
#
#     def 