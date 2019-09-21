import json

from model_mommy import mommy
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from authentication.models import Profile


class MobileAppVersionTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.mobileappversionlist_url = reverse('mobile_app_version_list')
        self.mobileappversioncreate_url = reverse('mobile_app_version_create')
        self.mobileappversioncheck_url = reverse('mobile_app_version_check')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harshadasawant89@gmail.com',
                                             password='abc12345')
        self.profile = mommy.make(Profile, user=self.user)

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'abc12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = 'Token {}'.format(self.login_data['token'])

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, json.dumps({"app_platform": "android",
                                                                                 "app_name": "AC",
                                                                                 "app_version": "2.0",
                                                                                 "comment": "Second release",
                                                                                 "upgrade_type": "recommend"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.mobileappversion_id = response.data['data']['id']


class MobileAppVersionListTests(MobileAppVersionTests):

    """
       Test ID:TS02RQ00149
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-list/
       Status:failure
       Message:no header
       Status code:401
    """

    def test_mobile_app_version_list_401_no_header(self):
        # Negative test case for getting mobile app version list with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get(self.mobileappversionlist_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
      Test ID:TS02RQ00150
      Created By:Hari
      Created On:12/12/2018
      Scenario:mobile-app-version-list/
      Status:failure
      Message:expired header
      Status code:401
    """

    def test_mobile_app_version_list_401_expired_header(self):
        # Negative test case for getting mobile app version list with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.mobileappversionlist_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
      Test ID:TS02RQ00150
      Created By:Hari
      Created On:12/12/2018
      Scenario:mobile-app-version-list/
      Status:failure
      Message:wrong token
      Status code:401
    """

    def test_mobile_app_version_list_401_wrong_token(self):
        # Negative test case for getting mobile app version list with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.mobileappversionlist_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
      Test ID:TS02RQ00148
      Created By:Hari
      Created On:12/12/2018
      Scenario:mobile-app-version-list/
      Status:failure
      Message:wrong method
      Status code:405
    """

    def test_mobile_app_version_list_405_wrong_method(self):
        # Negative test for getting mobile app version list with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversionlist_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
      Test ID:TS02RQ00151
      Created By:Hari
      Created On:12/12/2018
      Scenario:mobile-app-version-list/
      Status:failure
      Message:mobile app version list display
      Status code:405
    """

    def test_mobile_app_version_list_200(self):
        # Positive for getting mobile app version list
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.mobileappversionlist_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "Successful")
        self.assertEqual(response.data['msg'], "Mobile App version List")

    """
       Test ID:TS02RQ00152
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-list/
       Status:success
       Message:pagination
       Status code:200
    """

    def test_mobile_app_version_list_200_checking_count(self):
        # Positive for getting mobile app version list with checking count
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.mobileappversionlist_url)
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


class MobileAppVersionCreateTests(MobileAppVersionTests):

    """
       Test ID:TS02RQ00154
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:no header
       Status code:401
    """

    def test_mobile_app_version_create_401_no_header(self):
        # Negative test case for creating mobile app version with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(self.mobileappversioncreate_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
       Test ID:TS02RQ00155
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:expired header
       Status code:401
    """

    def test_mobile_app_version_create_401_expired_header(self):
        # Negative test case for creating mobile app version with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.mobileappversioncreate_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00155
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:wrong token
       Status code:401
    """

    def test_mobile_app_version_create_401_wrong_token(self):
        # Negative test case for creating mobile app version with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.mobileappversioncreate_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00153
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:wrong method
       Status code:405
    """

    def test_mobile_app_version_create_405_wrong_method(self):
        # Negative test for creating mobile app version with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.mobileappversioncreate_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
       Test ID:TS02RQ00156
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:wrong content type
       Status code:415
    """

    def test_mobile_app_version_create_415_with_wrong_content_type(self):
        # Negative test case for creating mobile app version with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, {"app_platform": "android",
                                                                      "app_name": "AC",
                                                                      "app_version": "2.0",
                                                                      "comment": "Second release",
                                                                      "upgrade_type": "recommend"},
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
       Test ID:TS02RQ00159
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:no data
       Status code:400
    """

    def test_mobile_app_version_create_400_no_data(self):
        # Negative test case for creating mobile app version with HTTP Header Authorization token with no data
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, {}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['app_platform'][0], "This field is required.")
        self.assertEqual(response.data['app_name'][0], "This field is required.")
        self.assertEqual(response.data['app_version'][0], "This field is required.")

    """
       Test ID:TS02RQ00160
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:mobile app version create
       Status code:400
    """

    def test_mobile_app_version_create_400_with_blank_fields(self):
        # Negative test case for creating mobile app version with HTTP Header Authorization token with blank fields
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, json.dumps({"app_platform": "",
                                                                      "app_name": "",
                                                                      "app_version": "",
                                                                      "comment": "",
                                                                      "upgrade_type": ""}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00157
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:wrong app platform
       Status code:400
    """

    def test_mobile_app_version_create_400_with_wrong_app_platform(self):
        # Negative test case for creating mobile app version with HTTP Header Authorization token with wrong app_platform
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, json.dumps({"app_platform": "blueberry",
                                                                      "app_name": "AC",
                                                                      "app_version": "2.0",
                                                                      "comment": "Second release",
                                                                      "upgrade_type": "recommend"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00158
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:wrong app name
       Status code:400
    """

    def test_mobile_app_version_create_400_with_wrong_app_name(self):
        # Negative test case for creating mobile app version with HTTP Header Authorization token with wrong app_name
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, json.dumps({"app_platform": "android",
                                                                      "app_name": "khkijijl",
                                                                      "app_version": "2.0",
                                                                      "comment": "Second release",
                                                                      "upgrade_type": "recommend"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00161
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:wrong app version
       Status code:400
    """

    def test_mobile_app_version_create_400_with_wrong_app_version(self):
        # Negative test case for creating mobile app version with HTTP Header Authorization token with wrong app_version
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, json.dumps({"app_platform": "android",
                                                                      "app_name": "AC",
                                                                      "app_version": "jhksjah",
                                                                      "comment": "Second release",
                                                                      "upgrade_type": "recommend"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00162
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:invalid comment
       Status code:400
    """

    def test_mobile_app_version_create_400_with_invalid_comment(self):
        # Negative test case for creating mobile app version with HTTP Header Authorization token with invalid name
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, json.dumps({"app_platform": "android",
                                                                      "app_name": "AC",
                                                                      "app_version": "2.0",
                                                                      "comment": ",jgdsludjhcdjokdoskekpd;kclsjdhedhjkhkdhhkuehnnnnnnnnjjjjjjjjjsjuuhdsluhehdhhuhehdehuheuheudhdujxhjhdjhe",
                                                                      "upgrade_type": "recommend"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['comment'][0], "Ensure this field has no more than 100 characters.")

    """
       Test ID:TS02RQ00163
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:failure
       Message:invalid comment
       Status code:400
    """

    def test_mobile_app_version_create_400_with_wrong_upgrade_type(self):
        # Negative test case for creating mobile app version with HTTP Header Authorization token with wrong upgrade type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, json.dumps({"app_platform": "android",
                                                                      "app_name": "AC",
                                                                      "app_version": "2.0",
                                                                      "comment": "Second release",
                                                                      "upgrade_type": "hswgydlwsdug"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00164
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-create/
       Status:success
       Message:mobile app version create
       Status code:201
    """

    def test_mobile_app_version_create_201(self):
        # Negative test case for creating mobile app version with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, {"app_platform": "android",
                                                                                 "app_name": "AC",
                                                                                 "app_version": "2.0",
                                                                                 "comment": "Second release",
                                                                                 "upgrade_type": "recommend"},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "App Version Created")

class MobileAppVersionDetailTests(MobileAppVersionTests):

    """
       Test ID:TS02RQ00166
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-detail/<ID>/
       Status:failure
       Message:no header
       Status code:401
    """

    def test_mobile_app_version_detail_401_no_header(self):
        # Negative test case for getting mobile app version detail with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/mobile-app-version-detail/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
       Test ID:TS02RQ00167
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-detail/<ID>/
       Status:failure
       Message:expired header
       Status code:401
    """

    def test_mobile_app_version_detail_401_expired_header(self):
        # Negative test case for getting mobile app version deatil with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/mobile-app-version-detail/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00167
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-detail/<ID>/
       Status:success
       Message:wrong token
       Status code:401
    """

    def test_mobile_app_version_detail_401_wrong_token(self):
        # Negative test case for getting mobile app version detail with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/mobile-app-version-detail/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00165
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-detail/<ID>/
       Status:failure
       Message:wrong method
       Status code:405
    """

    def test_mobile_app_version_detail_405_wrong_method(self):
        # Negative test for getting mobile app version detail with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-detail/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
       Test ID:TS02RQ00168
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-detail/<ID>/
       Status:failure
       Message:id invalid id
       Status code:405
    """

    def test_mobile_app_version_detail_404_wrong_token(self):
        # Negative test case for getting mobile app version detail with wrong HTTP Header Authorization token
        mobileappversion_id = 542375428935876859
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/mobile-app-version-detail/{}/".format(mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
       Test ID:TS02RQ00169
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-detail/<ID>/
       Status:success
       Message:App version retreived
       Status code:405
    """

    def test_mobile_app_version_detail_200(self):
        # Positive for getting mobile app version detail
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/mobile-app-version-detail/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "App Version Retrieved")


class MobileAppVersionUpdateTests(MobileAppVersionTests):
    """
       Test ID:TS02RQ00171
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:no header
       Status code:401
    """

    def test_mobile_app_version_update_401_no_header(self):
        # Negative test case for updating mobile app version with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
       Test ID:TS02RQ00172
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:expired header
       Status code:401
    """
    def test_mobile_app_version_update_401_expired_header(self):
        # Negative test case for updating mobile app version with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00172
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:wrong token
       Status code:401
    """

    def test_mobile_app_version_update_401_wrong_token(self):
        # Negative test case for updating mobile app version with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00170
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:wrong method
       Status code:405
    """

    def test_mobile_app_version_update_405_wrong_method(self):
        # Negative test for updating mobile app version with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
       Test ID:TS02RQ00173
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-detail/<ID>/
       Status:failure
       Message:id invalid
       Status code:405
    """

    def test_mobile_app_version_update_415_with_wrong_content_type(self):
        # Negative test case for updating mobile app version with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id),
                                    {"app_platform": "android",
                                     "app_name": "AC",
                                     "app_version": "2.0",
                                     "comment": "Second release",
                                     "upgrade_type": "recommend"},
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
       Test ID:TS02RQ00177
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:no data
       Status code:400
    """

    def test_mobile_app_version_update_400_no_data(self):
        # Negative test case for updating mobile app version with HTTP Header Authorization token with no data
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id), {}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['app_platform'][0], "This field is required.")
        self.assertEqual(response.data['app_name'][0], "This field is required.")
        self.assertEqual(response.data['app_version'][0], "This field is required.")

    """
       Test ID:TS02RQ00174
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:id invalid
       Status code:404
    """

    def test_mobile_app_version_detail_404_wrong_token(self):
        # Negative test case for getting mobile app version detail with wrong HTTP Header Authorization token
        mobileappversion_id = 542375428935876859
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/mobile-app-version-detail/{}/".format(mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
       Test ID:TS02RQ00178
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:blank fields
       Status code:400
    """

    def test_mobile_app_version_update_400_with_blank_fields(self):
        # Negative test case for updating mobile app version with HTTP Header Authorization token with blank fields
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id),
                                    json.dumps({"app_platform": "",
                                     "app_name": "",
                                     "app_version": "",
                                     "comment": "",
                                     "upgrade_type": ""}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00175
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:wrong app platform
       Status code:400
    """

    def test_mobile_app_version_update_400_with_wrong_app_platform(self):
        # Negative test case for updating mobile app version with HTTP Header Authorization token with wrong app_platform
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id),
                                    json.dumps({"app_platform": "blueberry",
                                    "app_name": "AC",
                                    "app_version": "2.0",
                                    "comment": "Second release",
                                    "upgrade_type": "recommend"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00176
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:wrong app name
       Status code:400
    """

    def test_mobile_app_version_update_400_with_wrong_app_name(self):
        # Negative test case for updating mobile app version with HTTP Header Authorization token with wrong app_name
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id),
                                    json.dumps({"app_platform": "android",
                                    "app_name": "khkijijl",
                                    "app_version": "2.0",
                                    "comment": "Second release",
                                    "upgrade_type": "recommend"}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00179
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:wrong app version
       Status code:400
    """

    def test_mobile_app_version_update_400_with_wrong_app_version(self):
        # Negative test case for updating mobile app version with HTTP Header Authorization token with wrong app_version
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id),
                                    json.dumps({"app_platform": "android",
                                     "app_name": "AC",
                                     "app_version": "jhksjah",
                                     "comment": "Second release",
                                     "upgrade_type": "recommend"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00180
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:comment invalid
       Status code:400
    """

    def test_mobile_app_version_update_400_with_invalid_comment(self):
        # Negative test case for updating mobile app version with HTTP Header Authorization token with invalid name
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id),
                                    json.dumps({"app_platform": "android",
                                    "app_name": "AC",
                                    "app_version": "2.0",
                                    "comment": ",jgdsludjhcdjokdoskekpd;kclsjdhedhjkhkdhhkuehnnnnnnnnjjjjjjjjjsjuuhdsluhehdhhuhehdehuheuheudhdujxhjhdjhe",
                                    "upgrade_type": "recommend"}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['comment'][0], "Ensure this field has no more than 100 characters.")

    """
       Test ID:TS02RQ00181
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-update/<ID>/
       Status:failure
       Message:upgrade type invalid
       Status code:400
    """

    def test_mobile_app_version_update_400_with_wrong_upgrade_type(self):
        # Negative test case for updating mobile app version with HTTP Header Authorization token with wrong update type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id),
                                    json.dumps({"app_platform": "android",
                                    "app_name": "AC",
                                    "app_version": "2.0",
                                    "comment": "Second release",
                                    "upgrade_type": "hswgydlwsdug"}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00182
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-detail/<ID>/
       Status:success
       Message:updated
       Status code:202
    """

    def test_mobile_app_version_update_202(self):
        # Negative test case for updating mobile app version with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-update/{}/".format(self.mobileappversion_id),
                                    json.dumps({"app_platform": "ios",
                                                "app_name": "AS",
                                                "app_version": "2.0",
                                                "comment": "Second release",
                                                "upgrade_type": "recommend"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "App Version Updated")



class MobileAppVersionDestroyTests(MobileAppVersionTests):

    """
       Test ID:TS02RQ00184
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-destroy/<ID>/
       Status:failure
       Message:no header
       Status code:401
    """

    def test_mobile_app_version_destroy_401_no_header(self):
        # Negative test case for destroying mobile app version with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/mobile-app-version-destroy/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
       Test ID:TS02RQ00185
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-destroy/<ID>/
       Status:failure
       Message:expired header
       Status code:401
    """

    def test_mobile_app_version_destroy_401_expired_header(self):
        # Negative test case for destroying mobile app version with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/mobile-app-version-destroy/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00185
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-destroy/<ID>/
       Status:failure
       Message:wrong token
       Status code:401
    """

    def test_mobile_app_version_destroy_401_wrong_token(self):
        # Negative test case for destroying mobile app version with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/mobile-app-version-destroy/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00183
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-destroy/<ID>/
       Status:failure
       Message:wrong token
       Status code:401
    """

    def test_mobile_app_version_destroy_405_wrong_method(self):
        # Negative test for destroying mobile app version with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/mobile-app-version-destroy/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
           Test ID:TS02RQ00186
           Created By:Hari
           Created On:12/12/2018
           Scenario:mobile-app-version-destroy/<ID>/
           Status:failure
           Message:id wrong
           Status code:404
        """

    def test_mobile_app_version_destroy_404_wrong_token(self):
        # Negative test case for getting mobile app version detail with wrong HTTP Header Authorization token
        mobileappversion_id = 542375428935876859
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-destroy/{}/".format(mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
       Test ID:TS02RQ00187
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-destroy/<ID>/
       Status:success
       Message:wrong token
       Status code:200
    """

    def test_mobile_app_version_destroy_200(self):
        # Positive for destroying mobile app version
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/mobile-app-version-destroy/{}/".format(self.mobileappversion_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "App Version Deleted")



class MobileAppVersionCheckTests(MobileAppVersionTests):

    """
       Test ID:TS02RQ00190
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-check/
       Status:failure
       Message:no header
       Status code:401
    """

    def test_mobile_app_version_check_401_no_header(self):
        # Negative test case for checking mobile app version with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(self.mobileappversioncheck_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
       Test ID:TS02RQ00191
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-check/
       Status:failure
       Message:expired header
       Status code:401
    """

    def test_mobile_app_version_check_401_expired_header(self):
        # Negative test case for checking mobile app version with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.mobileappversioncheck_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00191
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-check/
       Status:failure
       Message:expired header
       Status code:401
    """

    def test_mobile_app_version_check_401_wrong_token(self):
        # Negative test case for checking mobile app version with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.mobileappversioncheck_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00189
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-check/
       Status:failure
       Message:wrong method
       Status code:405
    """

    def test_mobile_app_version_check_405_wrong_method(self):
        # Negative test for checking mobile app version with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.mobileappversioncheck_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
       Test ID:TS02RQ00194
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-check/
       Status:failure
       Message:no data in body
       Status code:400
    """

    def test_mobile_app_version_check_400_no_data(self):
        # Negative test case for checking mobile app version with HTTP Header Authorization token with no data
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncheck_url, {}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['app_platform'][0], "This field is required.")
        self.assertEqual(response.data['app_name'][0], "This field is required.")
        self.assertEqual(response.data['app_version'][0], "This field is required.")

    """
       Test ID:TS02RQ00195
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-check/
       Status:failure
       Message:body with blank fields
       Status code:400
    """

    def test_mobile_app_version_check_400_with_blank_fields(self):
        # Negative test case for checking mobile app version with HTTP Header Authorization token with blank fields
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncheck_url, json.dumps({"app_platform": "",
                                                                     "app_name": "",
                                                                     "app_version": ""}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00192
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-check/
       Status:failure
       Message:wrong app platform
       Status code:400
    """

    def test_mobile_app_version_check_400_with_wrong_app_platform(self):
        # Negative test case for checking mobile app version with HTTP Header Authorization token with wrong app_platform
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncheck_url, json.dumps({"app_platform": "blueberry",
                                                                     "app_name": "AC",
                                                                     "app_version": "2.0"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00193
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-check/
       Status:failure
       Message:wrong app name
       Status code:400
    """

    def test_mobile_app_version_check_400_with_wrong_app_name(self):
        # Negative test case for checking mobile app version with HTTP Header Authorization token with wrong app_name
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncheck_url, json.dumps({"app_platform": "android",
                                                                     "app_name": "khkijijl",
                                                                     "app_version": "2.0"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00196
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-check/
       Status:failure
       Message:wrong app name
       Status code:400
    """

    def test_mobile_app_version_check_200_force(self):
        # Positive test case for checking mobile app version with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, { "app_platform": "android",
                                                                       "app_name": "AC",
                                                                       "app_version": "2.0",
                                                                       "comment": "Second release",
                                                                       "upgrade_type": "force"},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncheck_url, json.dumps({"app_platform": "android",
                                                                                "app_name": "AC",
                                                                                "app_version": "1.0"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "App version data")

    """
       Test ID:TS02RQ00197
       Created By:Hari
       Created On:12/12/2018
       Scenario:mobile-app-version-check/
       Status:failure
       Message:wrong app name
       Status code:400
    """

    def test_mobile_app_version_check_200_recommend(self):
        # Positive test case for checking mobile app version with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncreate_url, json.dumps({"app_platform": "android",
                                                                                 "app_name": "AC",
                                                                                 "app_version": "2.0",
                                                                                 "comment": "Second release",
                                                                                 "upgrade_type": "recommend"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.mobileappversioncheck_url, json.dumps({"app_platform": "android",
                                                                                "app_name": "AC",
                                                                                "app_version": "2.0"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "App version data")




