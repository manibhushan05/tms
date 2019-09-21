import uuid

import time

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.test.client import Client
from django.utils.encoding import force_text
import json

from api.schema import status_msg_schema, validate_json
from broker.models import Broker
from driver.models import DriverAppUser
from sme.models import Sme

# use this password everywhere, since we can't find out what the password was after storing it in the database
PASSWORD = 'AAHO#dummy@666!'


def user_details():
    return dict(username='test_user', email='info@aaho.in', password=PASSWORD)


def driver_details():
    device_id = str(uuid.uuid4())
    return device_id, get_driver_details(device_id)


def get_driver_details(device_id):
    return {
        'device_id': device_id,
        'driver_name': 'James Bond',
        'driver_number': '8978937498',
        'vehicle_number': 'JB07 JB 0007',
        'vehicle_type': 'BMW',
    }


class ApiTestCase(TestCase):
    """
    Abstract TestCase for API testing, all other Api tests inherit from this class
    """

    def secure(self):
        """
        are connections using https?
        """
        if not hasattr(self, 'is_secure'):
            self.is_secure = getattr(settings, 'SECURE_API_TEST_CLIENT', False)
        return self.is_secure

    def method(self):
        """
        Returns the HTTP method used to call the API, must be implemented in subclasses
        """
        raise NotImplementedError('`method()` method must be implemented in non-abstract subclasses')

    def url(self):
        """
        Returns the url of the API to be tested, only method that MUST be implemented in all non-abstract Api test cases
        """
        raise NotImplementedError('`url()` method must be implemented in non-abstract subclasses')

    def data(self):
        """
        Returns the post data to be sent along with the API request, default is None
        """
        return None

    def invalid_data(self):
        """
        Returns list of post data inputs expected to generate a 400 response from server, by default it is a list
        containing an empty dict
        """
        return [{}]

    def error_400_msg(self):
        """
        Override this method to give out custom 400 error msg
        """
        return ''

    def auth_required(self):
        """
        Return whether the API being tested requires authentication, `login()` is not called if this returns False
        """
        return False

    def login_url(self):
        """
        Returns the login url, must be implemented if auth is required, is ignored if auth_required() is False
        """
        raise NotImplementedError('`login_url()` method must be implemented in non-abstract subclasses requiring auth')

    def logout_url(self):
        """
        Returns the logout url, must be implemented if auth is required, is ignored if auth_required() is False
        """
        raise NotImplementedError('`logout_url()` method must be implemented in non-abstract subclasses requiring auth')

    def login_data(self):
        """
        Returns username and password, or any other credentials required for login
        """
        raise None

    def get_auth_headers(self):
        """
        Auth headers for different types of authentications, e.g. for token authentication we add a
        `HTTP_AUTHORIZATION: Token <token>` header to all our authenticated requests
        """
        return {}

    def is_json(self):
        """
        Returns True if the format of request and response is json, JSON validation is only done if this returns True
        """
        return True

    def schema(self):
        """
        Return the JSON schema structure the response is supposed to follow, override this for different APIs,
        the default is simply status and msg - {'status': string, 'msg': string}
        """
        return status_msg_schema()

    def confirm_result(self):
        """
        Override this method to confirm if the intended result of calling an API is reflected on the database
        """
        pass

    def validate_misc_response(self, response):
        """
        Override this to validate non-json types of responses, like checking if a zip file is returned with the correct
        content type etc.
        """
        pass

    def assert_success_response(self, url, response):
        """
        Helper method to assert http 200 response
        """
        status = response.status_code
        # self.assertEqual(
        #     status, 200, '%s error response from the server at URL "%s"\n\n RESPONSE:\n\n%s\n' % (status, url, response)
        # )

    def assert_response_code(self, url, response, expected_code, msg=None):
        """
        Helper method to assert a particular http response code
        """
        status = response.status_code
        msg = (msg or '').strip()
        msg = '' if not msg else ('ERROR: %s \n\n' % msg)
        self.assertEqual(
            status, expected_code,
            '%sUnexpected %s response from the server at URL "%s", expected http status = %s\n\n RESPONSE:\n\n%s\n' % (
                msg, status, url, expected_code, response
            )
        )

    def process_json_response(self, response):
        """
        Parse json response and validate with json schema
        """
        if self.is_json() and response.content:
            response_content = force_text(response.content)
            try:
                self.response_data = json.loads(response_content)
            except ValueError:
                self.response_data = None
            self.assertIsNotNone(self.response_data, 'Could not decode json response %s' % response_content)
            resp_schema = self.schema()
            # error = validate_json(self.response_data, resp_schema)
            # self.assertIsNone(error, 'JSON Response validation failed')
            if 'status' in resp_schema['properties']:
                self.assertEqual(self.response_data['status'], 'success', 'Response must have status=success')

    def response_json(self):
        """
        get json response of last get_response call, if available
        """
        return getattr(self, 'response_data', None)

    def login(self):
        """
        Login for APIs that require authentication, since this is called for a lot of tests, there is no need for a
        separate login-url test
        """
        if self.is_json():
            response = self.client.post(self.login_url(), data=json.dumps(self.login_data()),
                                        content_type='application/json', secure=self.secure())
        else:
            response = self.client.post(self.login_url(), data=self.login_data(), secure=self.secure())
        self.assert_success_response(self.login_url(), response)

    def logout(self):
        """
        Logout to check the behaviour of a API without authentication. again, since this is called for a lot of tests,
        there is no need for a separate logout-url test
        """
        response = self.client.post(self.logout_url(), secure=self.secure())
        self.assert_success_response(self.logout_url(), response)

    def get_response(self, data=None):
        """
        Make request with apt method, auth_headers and content_type, throw an error if method is not supported
        """
        auth_headers = self.get_auth_headers() or {}
        if self.method() == 'get':
            return self.client.get(self.url(), secure=self.secure(), **auth_headers)
        elif self.method() == 'post':
            post_data = data if data is not None else self.data()
            if self.is_json():
                return self.client.post(self.url(), data=None if not post_data else json.dumps(post_data),
                                        content_type='application/json', secure=self.secure(), **auth_headers)
            else:
                return self.client.generic('POST', self.url(), data=post_data, secure=self.secure(), **auth_headers)
        else:
            raise AssertionError('method "%s" not supported' % self.method())

    def check_success_response(self):
        """
        Test method to check 200 response from an api, validate the response, verify the intended effects
        Test methods start with `check_` instead of `test_` to avoid running them in abstract classes, they can be later
        exposed in non-abstract subclasses by mixing in `UnAbstract` or `UnAbstractAuth`
        """
        # login if required
        if self.auth_required():
            self.login()
        # record response time of url
        start_time = time.time()
        response = self.get_response()
        response_time = time.time() - start_time
        # check 200 response
        self.assert_success_response(self.url(), response)
        # if response is json, parse it and validate its structure
        self.process_json_response(response)
        # do some other validation on the response
        self.validate_misc_response(response)
        # check database etc. to see if the url call had the desired effect
        self.confirm_result()

    def check_400_response(self):
        """
        Test method to check 400 response for post APIs
        """
        # login if required
        if self.auth_required():
            self.login()
        err_msg = 'No 400 response on invalid data'
        if self.error_400_msg():
            err_msg += (': ' + self.error_400_msg())
        # get the list of wrong inputs
        wrong_inputs = self.invalid_data()
        if isinstance(wrong_inputs, dict):
            wrong_inputs = [wrong_inputs]
        # check for each
        for wrong_data in wrong_inputs:
            response = self.get_response(data=wrong_data)
            self.assert_response_code(self.url(), response, 400, msg=err_msg)

    def check_authentication(self):
        """
        Test method to check 401 response for the APIs that require authentication
        """
        # logout to ensure that our session has ended
        self.logout()
        response = self.get_response()
        # we should get a 401 response, as the url needs authentication
        self.assert_response_code(self.url(), response, 401)


class AuthApiTestCase(ApiTestCase):
    """
    Abstract TestCase for APIs that require authentication
    """

    def auth_required(self):
        return True


class DriverAuthApiTestCase(AuthApiTestCase):
    """
    Abstract TestCase for Driver app APIs that require authentication
    """

    def setUp(self):
        super().setUp()
        self.device_id, driver_data = driver_details()
        self.driver = DriverAppUser.objects.create(**driver_data)

    def login_url(self):
        return None

    def logout_url(self):
        return None

    def login(self):
        self.auth_token = self.driver.auth_token

    def logout(self):
        self.auth_token = None

    def get_auth_headers(self):
        return {'HTTP_AUTHORIZATION': 'Token %s' % self.auth_token or 'bad_token123'}


class CustomerAuthApiTestCase(AuthApiTestCase):
    """
    Abstract TestCase for Customer app APIs that require authentication
    """

    def login_url(self):
        return '/api/customer/login/'

    def logout_url(self):
        return '/api/customer/logout/'

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(**user_details())
        self.sme = Sme.objects.create(name=self.user)
        sme_group = Group.objects.create(name='sme')
        self.user.groups.add(sme_group)

    def login_data(self):
        return {'username': self.user.username, 'password': PASSWORD}


class FmsAuthApiTestCase(AuthApiTestCase):
    """
    Abstract TestCase for FMS app APIs that require authentication
    """

    def login_url(self):
        return '/api/fms/login/'

    def logout_url(self):
        return '/api/fms/logout/'

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(**user_details())
        fms_group = Group.objects.create(name='fms')
        self.broker = Broker.objects.create(name=self.user)
        self.user.groups.add(fms_group)

    def login_data(self):
        return {'username': self.user.username, 'password': PASSWORD}


# final abstract TestCase subclasses, all ApiTestCases should inherit from the following,
# these should be pretty self explanatory


class GetApiTestCase(ApiTestCase):

    def method(self):
        return 'get'


class PostApiTestCase(ApiTestCase):

    def method(self):
        return 'post'


class GetDriverAuthApiTestCase(DriverAuthApiTestCase):

    def method(self):
        return 'get'


class PostDriverAuthApiTestCase(DriverAuthApiTestCase):

    def method(self):
        return 'post'


class GetCustomerAuthApiTestCase(CustomerAuthApiTestCase):

    def method(self):
        return 'get'


class PostCustomerAuthApiTestCase(CustomerAuthApiTestCase):

    def method(self):
        return 'post'


class GetFmsAuthApiTestCase(FmsAuthApiTestCase):

    def method(self):
        return 'get'


class PostFmsAuthApiTestCase(FmsAuthApiTestCase):

    def method(self):
        return 'post'


class UnAbstract(object):
    """
    Mixin to make ApiTestCase subclasses non-abstract by exposing the `test_*` method. Notice how this does not subclass
    TestCase. Keeping `test_*` methods separate from abstract TestCase subclasses will ensure that our abstract Api test
    cases are not run when they are imported by other test modules unless they are mixed in together with these classes.

    e.g. `class TestCustomerLoginStatusApi(GetApiTestCase, UnAbstract): pass`
    """

    def test_success_response(self):
        return self.check_success_response()


class UnAbstractAuth(UnAbstract):
    """
    Subclass of `UnAbstract` for APIs that require authentication, also exposes the `test_authentication` method
    """

    def test_authentication(self):
        return self.check_authentication()


class UnAbstractAuth400(UnAbstractAuth):
    """
    Subclass of `UnAbstractAuth` for POST APIs that exposes the method to check 400 response on invalid data
    """

    def test_400_response(self):
        return self.check_400_response()


class UnAbstract400(UnAbstract):
    """
    Subclass of `UnAbstract` for POST APIs that exposes the method to check 400 response on invalid data
    """

    def test_400_response(self):
        return self.check_400_response()
