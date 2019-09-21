import json

from model_mommy import mommy
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from authentication.models import Profile
from driver.models import OTP


class UserAuthenticationTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.authtoken_url = reverse('get_auth_token')
        self.groupslist_url = reverse('groups_list')
        self.changepwd_url = reverse('change_password')
        self.resetpwd_url = reverse('reset_password')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harshadasawant89@gmail.com',
                                             password='abc12345',
                                             first_name='John',
                                             last_name='Doe')
        self.user = User.objects.create_user(username='text1234',
                                             email='harsh@gmail.com',
                                             password='text1234',
                                             first_name='Ganesh',
                                             last_name='Narayanan')
        self.profile = mommy.make(Profile, user=self.user)
        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'abc12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

    """
        Test Suite ID:TS01
        Test Suite:Web Application
        Module:Authentication 
    """
class UserLoginTests(UserAuthenticationTests):
    def setUp(self):
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='john_doe', email='harshadasawant89@gmail.com', password='pwd12345', first_name='John',
            last_name='Doe'
        )

        self.user = User.objects.create_user(
            username='text1234', email='harsha@gmail.com', password='text1234', first_name='Ganesh',
            last_name='Narayanan'
        )

        self.profile = mommy.make(Profile, user=self.user)

    """
         Test ID:TS01AH00001
         Created By:Hari
         Created On:05/12/2018
         Scenario:login/
         Status:success 
         Message:Login Successful
         Status code:200
    """

    def test_user_login(self):
        # Positive test for user login with correct username and password
        response = self.client.post(self.login_url, {'username': 'text1234', 'password': 'text1234'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['token'])
        self.assertEqual(response.data['data']['username'], 'text1234')
        self.assertEqual(response.data['msg'],'Login Successful')
        self.assertEqual(response.data['status'], 'success')

        """
             Test ID:TS01AH00002
             Created By:Hari
             Created On:05/12/2018
             Scenario:login/
             Status:failure 
             Message:Login Unsuccessful
             Status code:400
        """

    def test_user_login_400_blank_username(self):
        # Negative test for user login with blank username
        response = self.client.post(self.login_url, {'username': '', 'password': 'text1234'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'],'failure')
        self.assertEqual(response.data['msg'], 'Login Unsuccessful')
        self.assertEqual(response.data['data']['username'][0], 'This field may not be blank.')

        """
             Test ID:TS01AH00003
             Created By:Hari
             Created On:05/12/2018
             Scenario:login/
             Status:failure 
             Message:Login Unsuccessful
             Status code:400
        """

    def test_user_login_400_blank_password(self):
        # Negative test for user login with blank password
        response = self.client.post(self.login_url, {'username': 'text1234', 'password': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'Login Unsuccessful')
        self.assertEqual(response.data['data']['password'][0], 'This field may not be blank.')

        """
             Test ID:TS01AH00004
             Created By:Hari
             Created On:05/12/2018
             Scenario:login/
             Status:failure 
             Message:Login Unsuccessful
             Status code:400
        """

    def test_user_login_400_no_username_password(self):
        # Negative test for user login with no username and password
        response = self.client.post(self.login_url, {'username': '', 'password': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'Login Unsuccessful')
        self.assertEqual(response.data['data']['username'][0],'This field may not be blank.')
        self.assertEqual(response.data['data']['password'][0], 'This field may not be blank.')

        """
             Test ID:TS01AH00005
             Created By:Hari
             Created On:05/12/2018
             Scenario:login/
             Status:failure 
             Message:Login Unsuccessful
             Status code:400
         """

    def test_user_login_400_no_data(self):
        # Negative test for user login with no data
        response = self.client.post(self.login_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'Login Unsuccessful')
        self.assertEqual(response.data['data']['username'][0], 'This field is required.')
        self.assertEqual(response.data['data']['password'][0], 'This field is required.')

    """
         Test ID:TS01AH00006
         Created By:Hari
         Created On:05/12/2018
         Scenario:login/
         Status:failure 
         Message:Login Unsuccessful
         Status code:400
    """

    def test_user_login_400_wrong_pwd(self):
        # Negative test for user login with wrong password
        response = self.client.post(self.login_url, {'username': 'text1234', 'password': 'pqrstuv'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'Login Unsuccessful')
        self.assertEqual(response.data['data']['non_field_errors'][0], 'Unable to log in with provided credentials.')

    """
         Test ID:TS01AH00007
         Created By:Hari
         Created On:05/12/2018
         Scenario:login/
         Status:failure 
         Message:Login Unsuccessful
         Status code:400
    """

    def test_user_login_400_wrong_username(self):
        # Negative test for user login with wrong username
        response = self.client.post(self.login_url, {'username': 'abc123', 'password': 'pwd12345'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'Login Unsuccessful')
        self.assertEqual(response.data['data']['non_field_errors'][0], 'Unable to log in with provided credentials.')


class UserLogoutTests(UserAuthenticationTests):
    """
         Test ID:TS01AH00008
         Created By:Hari
         Created On:05/12/2018
         Scenario:logout/
         Status:success
         Message:success
         Status code:200
    """

    def test_user_logout(self):
        # Positive test case for user logout with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    """
         Test ID:TS01AH00009
         Created By:Hari
         Created On:05/12/2018
         Scenario:logout/
         Status:failure
         Status code:401
    """

    def test_user_logout_401_no_header(self):
        # Negative test case for user logout with no HTTP Header Authorization token
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    """
                                                    Test ID:TS01AH00010
                                                    Created By:Hari
                                                    Created On:05/12/2018
                                                    Scenario:logout/
                                                    Status:failure
                                                    Status code:401
                                                    """

    def test_user_logout_401_expired_header(self):
        # Negative test case for user logout with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid token.')

    """
        Test ID:TS01AH00011
        Created By:Hari
        Created On:05/12/2018
        Scenario:logout/
        Status:failure
        Status code:401
    """

    def test_user_logout_401_wrong_token(self):
        # Negative test case for user logout with wrong HTTP Header Authorization token
        token = '806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')


class AuthTokenTests(UserAuthenticationTests):

    """
        Test ID:TS01AH00012
        Created By:Hari
        Created On:05/12/2018
        Scenario:get-auth-token/
        Status:success
        Status code:200
    """

    def test_auth_token(self):
        # Positive test for getting authorization token with correct username and password
        response = self.client.post(self.authtoken_url, {'username': 'text1234', 'password': 'text1234'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['token'])

    """
        Test ID:TS01AH00013
        Created By:Hari
        Created On:05/12/2018
        Scenario:get-auth-token/
        Status:failure
        Message:username cannot be blank
        Status code:400
    """

    def test_auth_token_400_blank_username(self):
        # Negative test for getting authorization token with blank username
        response = self.client.post(self.authtoken_url, {'username': '', 'password': 'text1234'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'][0], 'This field may not be blank.')

    """
        Test ID:TS01AH00014
        Created By:Hari
        Created On:05/12/2018
        Scenario:get-auth-token/
        Status:failure
        Message:password cannot be blank
        Status code:400
    """

    def test_auth_token_400_blank_pwd(self):
        # Negative test for getting authorization token with blank password
        response = self.client.post(self.authtoken_url, {'username': 'text1234', 'password': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field may not be blank.')

    """
         Test ID:TS01AH00015
         Created By:Hari
         Created On:05/12/2018
         Scenario:get-auth-token/
         Status:failure
         Message:username aand password cannot be blank
         Status code:400
    """

    def test_auth_token_400_blank_username_pwd(self):
        # Negative test for getting authorization token with blank username and password
        response = self.client.post(self.authtoken_url, {'username': '', 'password': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field may not be blank.')
        self.assertEqual(response.data['username'][0], 'This field may not be blank.')

    """
         Test ID:TS01AH00016
         Created By:Hari
         Created On:05/12/2018
         Scenario:get-auth-token/
         Status:failure
         Message:username aand password cannot be blank
         Status code:400
     """

    def test_auth_token_400_no_data(self):
        # Negative test for getting authorization token with no data
        response = self.client.post(self.authtoken_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field is required.')
        self.assertEqual(response.data['username'][0], 'This field is required.')

    """
        Test ID:TS01AH00017
        Created By:Hari
        Created On:05/12/2018
        Scenario:get-auth-token/
        Status:failure
        Message:incorrect password
        Status code:400
    """


    def test_auth_token_400_wrong_pwd(self):
        # Negative test for getting authorization token with wrong password
        response = self.client.post(self.authtoken_url, {'username': 'text1234', 'password': 'abcdef'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Unable to log in with provided credentials.')

    """
        Test ID:TS01AH00018
        Created By:Hari
        Created On:05/12/2018
        Scenario:get-auth-token/
        Status:failure
        Message:incorrect username
        Status code:400
    """

    def test_auth_token_400_wrong_username(self):
        # Negative test for getting authorization token with wrong username
        response = self.client.post(self.authtoken_url, {'username': 'abc1234', 'password': 'text1234'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Unable to log in with provided credentials.')

class GroupsListTests(UserAuthenticationTests):

    """
         Test ID:TS01AH00019
         Created By:Hari
         Created On:05/12/2018
         Scenario:group-list/
         Status:success
         Message:success
         Status code:200
    """

    def test_groups_list(self):
        # Positive test for getting groups list with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.groupslist_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """
         Test ID:TS01AH00020
         Created By:Hari
         Created On:05/12/2018
         Scenario:group-list/
         Status:failure
         Message:no http access token
         Status code:401
    """

    def test_groups_list_401_on_header(self):
        # Negative test for getting groups list with no HTTP Header Authorization token
        response = self.client.get(self.groupslist_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

        """
             Test ID:TS01AH00021
             Created By:Hari
             Created On:05/12/2018
             Scenario:group-list/
             Status:failure
             Message:expired token
             Status code:401
        """

    def test_groups_list_401_expired_header(self):
        # Negative test for getting groups list with expired/logged out  HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.groupslist_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid token.')

        """
            Test ID:TS01AH00022
            Created By:Hari
            Created On:05/12/2018
            Scenario:group-list/
            Status:failure
            Message:wrong token
            Status code:401
        """

    def test_groups_list_401_wrong_token(self):
        # Negative test case for getting groups list with wrong HTTP Header Authorization token
        token = '806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.groupslist_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

class ChangePasswordTests(UserAuthenticationTests):
    """
        Test ID:TS01AH00023
        Created By:Hari
        Created On:05/12/2018
        Scenario:change-password/
        Status:failure
        Message:no header
        Status code:401
    """

    def test_change_password_401_no_header(self):
        # Negative test for getting changing password with no HTTP Header Authorization token
        response = self.client.put(self.changepwd_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    """
        Test ID:TS01AH00024
        Created By:Hari
        Created On:05/12/2018
        Scenario:change-password/
        Status:failure
        Message:expired header
        Status code:401
    """

    def test_change_password_401_expired_header(self):
        # Negative test for getting groups list with expired/logged out  HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.changepwd_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid token.')

    """
        Test ID:TS01AH00025
        Created By:Hari
        Created On:05/12/2018
        Scenario:change-password/
        Status:failure
        Message:wrong token
        Status code:400
    """

    def test_change_password_401_wrong_token(self):
        # Negative test case for changing password with wrong HTTP Header Authentication token
        token = '806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.changepwd_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    """
         Test ID:TS01AH00026
         Created By:Hari
         Created On:05/12/2018
         Scenario:change-password/
         Status:failure
         Message:oldpassword is not valid
         Status code:400
    """

    def test_change_password_400_wrong_old_pwd(self):
        # Negative test case for changing password with HTTP Header Authentication token and wrong old password
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.changepwd_url, {'old_password': 'text1234', 'new_password': 'newpassword'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['old_password'][0], 'Wrong password.')
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'Old password is not valid')

    """
         Test ID:TS01AH00027
         Created By:Hari
         Created On:05/12/2018
         Scenario:change-password/
         Status:failure
         Message:no new password
         Status code:400
    """


    def test_change_password_400_no_new_pwd(self):
        # Negative test case for changing password with HTTP Header Authentication token and no new password
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.changepwd_url, {'old_password': 'text1234', 'new_password': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['new_password'][0], 'This field may not be blank.')
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'Something went wrong, Plz try later')

        """
             Test ID:TS01AH00028
             Created By:Hari
             Created On:05/12/2018
             Scenario:change-password/
             Status:failure
             Message:bad request
             Status code:400
        """

    def test_change_password_400_short_pwd(self):
        # Negative test case for changing password with HTTP Header Authorization token and new password too short
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.changepwd_url, {'old_password': 'text1234', 'new_password': 'adb'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['new_password'][0], 'Ensure this field has at least 8 characters.')
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'Something went wrong, Plz try later')

        """
             Test ID:TS01AH00029
             Created By:Hari
             Created On:05/12/2018
             Scenario:change-password/
             Status:success
             Message:password updated
             Status code:200
        """

    def test_change_password(self):
        # Positive test case for changing password with HTTP Header Authorization token and correct new password
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.changepwd_url, {'old_password': 'abc12345', 'new_password': 'str12345'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], 'Password updated')

class ForgotPasswordTests(UserAuthenticationTests):
    def setUp(self):
        self.forgotpwd_url = reverse('forgot_pwd')
        self.user = User.objects.create_user(username='text1234',
                                             email='harsh@gmail.com',
                                             password='text1234',
                                             first_name='Ganesh',
                                             last_name='Narayanan'
                                             )
        self.profile = mommy.make(Profile, user=self.user, phone='9619135574')

    """
         Test ID:TS01AH00030
         Created By:Hari
         Created On:05/12/2018
         Scenario:forgot-password/
         Status:success
         Message:otp sent
         Status code:200
    """

    def tests_forgot_password(self):
        # Positive test for forgot password
        response = self.client.post(self.forgotpwd_url, {'username': 'text1234'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], "OTP Sent to ['9619135574']")

    """
       Test ID:TS01AH00031
       Created By:Hari
       Created On:05/12/2018
       Scenario:forgot-password/
       Status:failure
       Message:otp sending failed
       Status code:400
    """

    def test_forgot_password_400_no_data(self):
        # Negative test for forgot password with no data
        response = self.client.post(self.forgotpwd_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['username'][0],
                         'This field is required.')
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'OTP Sending failed')

    """
        Test ID:TS01AH00032
        Created By:Hari
        Created On:05/12/2018
        Scenario:forgot-password/
        Status:failure
        Message:otp sent
        Status code:400
    """

    def test_forgot_password_400_blank_username(self):
        # Negative test for forgot password with blank username
        response = self.client.post(self.forgotpwd_url, {'username': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data']['username'][0],
                         'This field may not be blank.')
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'OTP Sending failed')


class VerifyOtpTests(UserAuthenticationTests):
    def setUp(self):
        self.verifyotp_url = reverse('verify_otp')
        self.user = User.objects.create_user(username='text1234',
                                             email='harsh@gmail.com',
                                             password='text1234',
                                             first_name='Ganesh',
                                             last_name='Narayanan')
        self.profile = mommy.make(Profile, user=self.user, phone='9619255142')

        url = reverse('forgot_pwd')
        data = {
            'username': 'text1234'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.otp = OTP.objects.get(phone='9619255142')

    """
         Test ID:TS01AH00033
         Created By:Hari
         Created On:05/12/2018
         Scenario:verify-otp/
         Status:success
         Message:otp sent
         Status code:200
    """

    def test_verify_otp(self):
        # Positive test for verifying otp
        response = self.client.post(self.verifyotp_url, {'username': 'text1234', 'otp': self.otp.otp}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], 'OTP Verified')

    """
          Test ID:TS01AH00034
          Created By:Hari
          Created On:06/12/2018
          Scenario:verify-otp/
          Status:failure
          Message:no data
          Status code:400
    """

    def test_verify_otp_400_no_data(self):
        # Negative test for verifying otp with no data
        response = self.client.post(self.verifyotp_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg']['username'][0], 'This field is required.')
        self.assertEqual(response.data['msg']['otp'][0], 'This field is required.')

    """
          Test ID:TS01AH00035
          Created By:Hari
          Created On:06/12/2018
          Scenario:verify-otp/
          Status:failure
          Message:no username
          Status code:400
    """

    def test_verify_otp_400_no_username(self):
        # Negative test for verifying with no username
        response = self.client.post(self.verifyotp_url, {'otp': self.otp.otp}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg']['username'][0], 'This field is required.')

    """
         Test ID:TS01AH00036
         Created By:Hari
         Created On:06/12/2018
         Scenario:verify-otp/
         Status:failure
         Message:no otp
         Status code:400
    """


    def test_verify_otp_400_no_otp(self):
        # Negative test case for verifying otp with no otp entered
        response = self.client.post(self.verifyotp_url, {'username': 'john_doe'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg']['otp'][0], 'This field is required.')

    """
         Test ID:TS01AH00037
         Created By:Hari
         Created On:06/12/2018
         Scenario:verify-otp/
         Status:failure
         Message:wrong username
         Status code:400
    """

    def test_verify_otp_400_wrong_username(self):
        # Negative test case for verifying otp with wrong username
        response = self.client.post(self.verifyotp_url, {'username': 'abc123', 'otp': self.otp.otp}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'User Does Not Exist')

    """
         Test ID:TS01AH00038
         Created By:Hari
         Created On:06/12/2018
         Scenario:verify-otp/
         Status:failure
         Message:wrong username
         Status code:400
    """

    def test_verify_otp_400_wrong_otp(self):
        # Negative test case for verifying otp with wrong otp
        response = self.client.post(self.verifyotp_url, {'username': 'text1234', 'otp': '654783'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'Invalid OTP')

    """
         Test ID:TS01AH00083
         Created By:Hari
         Created On:06/12/2018
         Scenario:verify-otp/
         Status:failure
         Message:otp more than 6 characters
         Status code:400
    """

    def test_verify_otp_400_exceed_otp(self):
        # Negative test case for verifying otp with wrong otp
        response = self.client.post(self.verifyotp_url, {'username': 'text1234', 'otp': '65478312'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg']['otp'][0], 'Ensure this field has no more than 6 characters.')

class ResetPasswordTests(UserAuthenticationTests):

    """
          Test ID:TS01AH00039
          Created By:Hari
          Created On:06/12/2018
          Scenario:reset-password/
          Status:success
          Message:password reset
          Status code:200
    """

    def test_reset_password_204(self):
        # Positive test case for resetting password with HTTP Header Authorization token and correct new password
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.resetpwd_url, {'username': 'john_doe', 'password': 'pwd12345'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['msg'], 'Password is reset')

    """
       Test ID:TS01AH00040
       Created By:Hari
       Created On:06/12/2018
       Scenario:reset-password/
       Status:failure
       Message:no auth details provided
       Status code:401
    """

    def test_reset_password_401_no_header(self):
        # Negative test case for resetting password with no HTTP Header Authorization token
        response = self.client.put(self.resetpwd_url, {'username': 'john_doe', 'password': 'pwd12345'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    """
          Test ID:TS01AH00041
          Created By:Hari
          Created On:06/12/2018
          Scenario:reset-password/
          Status:failure
          Message:no username password provided
          Status code:400
    """

    def test_reset_password_400_no_data(self):
        # Negative test for resetting password with HTTP Header Authorization token but no data
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.resetpwd_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg']['username'][0], 'This field is required.')
        self.assertEqual(response.data['msg']['password'][0], 'This field is required.')

    """
        Test ID:TS01AH00042
        Created By:Hari
        Created On:06/12/2018
        Scenario:reset-password/
        Status:failure
        Message:no password provided
        Status code:400
    """

    def test_reset_password_400_no_pwd(self):
        # Negative test case for resetting password with HTTP Header Authorization token but no password
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.resetpwd_url, {'username': 'john_doe'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg']['password'][0], 'This field is required.')

    """
         Test ID:TS01AH00043
         Created By:Hari
         Created On:06/12/2018
         Scenario:reset-password/
         Status:failure
         Message:no username provided
         Status code:400
    """

    def test_reset_password_400_no_username(self):
        # Negative test case for resetting password with HTTP Header Authorization token but no username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.resetpwd_url, {'password': 'pwd12345'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg']['username'][0], 'This field is required.')

        """
            Test ID:TS01AH00044
            Created By:Hari
            Created On:06/12/2018
            Scenario:reset-password/
            Status:failure
            Message:no password provided
            Status code:400
        """

    def test_reset_password_400_wrong_username(self):
        # Negative test case for resetting password with HTTP Header Authorization token and wrong username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.resetpwd_url, {'username': 'abc123', 'password': 'pwd12345'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg'], 'Wrong username.')

    """
       Test ID:TS01AH00045
       Created By:Hari
       Created On:06/12/2018
       Scenario:reset-password/
       Status:failure
       Message:no password provided
       Status code:400
   """

    def test_reset_password_400_short_pwd(self):
        # Negative test case for resetting password with HTTP Header Authorization token and password wrong
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.resetpwd_url, {'username': 'john_doe', 'password': 'adbf'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failure')
        self.assertEqual(response.data['msg']['password'][0], 'Ensure this field has at least 8 characters.')
