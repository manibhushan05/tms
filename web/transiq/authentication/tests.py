from django.contrib.auth.models import User
from django.test import TestCase, Client


class WebLoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='mani@aaho.in', password='aaho@1234')
        self.client = Client(enforce_csrf_checks=False)

    def test_web_login_views(self):
        response = self.client.post('/authentication/web-login/', {'username': 'mani@aaho.in', 'password': 'aaho@1234'})
        # self.assertEqual(response.status_code, 200)
