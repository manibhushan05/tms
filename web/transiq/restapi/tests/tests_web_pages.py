import json

from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from employee.models import Employee


class WebPageSetup(APITestCase):
    """
        Setup dummy data for testing purpose
    """

    def setUp(self):
        self.login_url = reverse('login')
        self.test_user = User.objects.create_user('testUser', 'test@example.com', 'testPassword')
        self.employye = mommy.make(Employee, username=self.test_user)
        self.login_data = self.client.post(self.login_url, {"username": "testUser", "password": "testPassword"}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])


class BookingWebPageTest(WebPageSetup):
    """
    Test Suite ID: TS01
    Test Suite: Web Application
    Module: Booking
    """

    def setUp(self):
        super().setUp()
        self.commission_booking_url = reverse(viewname='basic_commission_booking_page')
        self.booking_history_url = reverse(viewname="full_booking_list_page")
        self.update_contract_booking_url = reverse(viewname="update_contract_booking_page")
        self.pod_list_url = reverse(viewname='pod_list_page')
        self.download_lr_url = reverse(viewname='download_lr_page')
        self.get_placed_order_customer_summary_url = reverse(viewname='get_placed_order_customer_summary_page')
        self.get_billed_customer_summary_url = reverse(viewname='get_billed_customer_summary_page')
        self.get_supplier_summary_url = reverse(viewname='get_supplier_summary_page')
        self.get_vehicle_summary_url = reverse(viewname='get_vehicle_summary_page')

    def test_open_commission_booking_page_with_authenticated_user(self):
        """
        Test ID: TS01BK00001
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open commission booking page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.commission_booking_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_open_commission_booking_page_with_unauthenticated_user(self):
        """
        Test ID: TS01BK00002
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open commission booking page with unauthenticated user
        """
        response = self.client.get(self.commission_booking_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_open_commission_booking_page_with_invalid_token(self):
        """
        Test ID: TS01BK00003
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open commission booking page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.get(self.commission_booking_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_open_commission_booking_page_with_extra_parameters(self):
        """
        Test ID: TS01BK00004
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open commission booking page with extra dummy parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.commission_booking_url, {"dummy_param": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_full_booking_page_list_with_authenticated_user(self):
        """
        Test ID: TS01BK00005
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open full booking page list with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.booking_history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_full_booking_page_list_with_unauthenticated_user(self):
        """
        Test ID: TS01BK00006
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open full booking page list with unauthenticated user
        """
        response = self.client.get(self.booking_history_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_full_booking_page_list_with_invalid_token(self):
        """
        Test ID: TS01BK00007
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open full booking page list with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.booking_history_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_full_booking_page_list_with_extra_parameters(self):
        """
        Test ID: TS01BK00008
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open full booking page list with extra dummy parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.booking_history_url, {"dummy_param": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contract_booking_page_with_authorized_user(self):
        """
        Test ID: TS01BK00009
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open update contract booking url with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.update_contract_booking_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contract_booking_page_with_unauthorized_user(self):
        """
        Test ID: TS01BK00010
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open update contract booking url with unauthenticated user
        """
        response = self.client.get(self.update_contract_booking_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_contract_booking_page_with_invalid_token(self):
        """
        Test ID: TS01BK00011
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open update contract booking url with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.update_contract_booking_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_contract_booking_page_with_extra_parameters(self):
        """
        Test ID: TS01BK00012
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open update contract booking url with extra dummy parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.update_contract_booking_url, {"dummy_param": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pod_list_page_with_authenticated_user(self):
        """
        Test ID: TS01BK00013
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open pod list url (form downloads section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.pod_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pod_list_page_with_unauthenticated_user(self):
        """
        Test ID: TS01BK00014
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open pod list url (form downloads section) with unauthenticated user
        """
        response = self.client.get(self.pod_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pod_list_page_with_invalid_token(self):
        """
        Test ID: TS01BK00015
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open pod list url (form downloads section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.pod_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pod_list_page_with_extra_parameters(self):
        """
        Test ID: TS01BK00016
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open pod list url (form downloads section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.pod_list_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_lr_page_with_authenticated_user(self):
        """
        Test ID: TS01BK00017
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open download lorry url (form downloads section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.download_lr_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_lr_page_with_unauthenticated_user(self):
        """
        Test ID: TS01BK00018
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open download lorry url (form downloads section) with unauthenticated user
        """
        response = self.client.get(self.download_lr_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_download_lr_page_with_invalid_token(self):
        """
        Test ID: TS01BK00019
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open download lorry url (form downloads section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.download_lr_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_download_lr_page_with_extra_parameters(self):
        """
        Test ID: TS01BK00020
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open download lorry url (form downloads section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.download_lr_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_placed_order_customer_summary_page_with_authenticated_user(self):
        """
        Test ID: TS01BK00021
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open placed order customer summary url (form accounting summary section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.get_placed_order_customer_summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_placed_order_customer_summary_page_with_unauthenticated_user(self):
        """
        Test ID: TS01BK00022
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open placed order customer summary url (form accounting summary section) with unauthenticated user
        """
        response = self.client.get(self.get_placed_order_customer_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_placed_order_customer_summary_page_with_invalid_token(self):
        """
        Test ID: TS01BK0023
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open placed order customer summary url (form accounting summary section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.get_placed_order_customer_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_placed_order_customer_summary_page_with_extra_parameters(self):
        """
        Test ID: TS01BK0024
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open placed order customer summary url (form accounting summary section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.get_placed_order_customer_summary_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_billed_customer_summary_page_with_authenticated_user(self):
        """
        Test ID: TS01BK00025
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get billed customer summary page (form accounting summary section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.get_billed_customer_summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_billed_customer_summary_page_with_unauthenticated_user(self):
        """
        Test ID: TS01BK00026
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get billed customer summary page (form accounting summary section) with unauthenticated user
        """
        response = self.client.get(self.get_billed_customer_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_billed_customer_summary_page_with_invalid_token(self):
        """
        Test ID: TS01BK00027
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get billed customer summary page (form accounting summary section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.get_billed_customer_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_billed_customer_summary_page_with_extra_parameters(self):
        """
        Test ID: TS01BK00028
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get billed customer summary page (form accounting summary section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.get_billed_customer_summary_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_supplier_summary_page_with_authenticated_user(self):
        """
        Test ID: TS01BK00029
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get supplier summary page (form accounting summary section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.get_supplier_summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_supplier_summary_page_with_unauthenticated_user(self):
        """
        Test ID: TS01BK00030
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get supplier summary page (form accounting summary section) with authenticated user
        """
        response = self.client.get(self.get_supplier_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_supplier_summary_page_with_invalid_token(self):
        """
        Test ID: TS01BK00031
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get supplier summary page (form accounting summary section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.get_supplier_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_supplier_summary_page_with_extra_parameters(self):
        """
        Test ID: TS01BK00032
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get supplier summary page (form accounting summary section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.get_supplier_summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_vehicle_summary_page_with_authenticated_user(self):
        """
        Test ID: TS01BK00033
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get vehicle summary page (form accounting summary section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.get_vehicle_summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_vehicle_summary_page_with_unauthenticated_user(self):
        """
        Test ID: TS01BK00034
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get vehicle summary page (form accounting summary section) with unauthenticated user
        """
        response = self.client.get(self.get_vehicle_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_vehicle_summary_page_with_invalid_token(self):
        """
        Test ID: TS01BK00035
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get vehicle summary page (form accounting summary section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invaidToken')
        response = self.client.get(self.get_vehicle_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_vehicle_summary_page_with_extra_parameters(self):
        """
        Test ID: TS01BK00036
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open get vehicle summary page (form accounting summary section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.get_vehicle_summary_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PaymentWebPageTest(WebPageSetup):
    """
    Test Suite ID: TS01
    Test Suite: Web Application
    Module: Payment
    """

    def setUp(self):
        super().setUp()
        self.add_received_payments_url = reverse(viewname='add_received_inward_payment')
        self.inward_payment_list_url = reverse(viewname='inward_payment_list_page')
        self.uncredited_cheques_url = reverse(viewname='uncredited_cheque_page')
        self.outward_payment_page_url = reverse(viewname='outward_payment_page')
        self.outward_payment_list_url = reverse(viewname='outward_payment_list')
        self.download_payment_file_url = reverse(viewname='download_payment_page')
        self.get_payment_receipt_list_url = reverse(viewname='get_payment_receipt_page')

    def test_add_received_payments_page_with_authenticated_user(self):
        """
        Test ID: TSO1PY00001
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open add received payments url with authorized user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.add_received_payments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_received_payments_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1PY00002
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open add received payments url with authorized user
        """
        response = self.client.get(self.add_received_payments_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_received_payments_page_with_invalid_token(self):
        """
        Test ID: TSO1PY00003
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open add received payments url with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.add_received_payments_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_received_payments_page_with_extra_parameters(self):
        """
        Test ID: TSO1PY00004
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open add received payments url with extra dummy parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.add_received_payments_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inward_payment_list_page_with_authenticated_user(self):
        """
        Test ID: TSO1PY00005
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open inward payment list url with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.inward_payment_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inward_payment_list_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1PY00006
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open inward payment list url with unauthenticated user
        """
        response = self.client.get(self.inward_payment_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inward_payment_list_page_with_invalid_token(self):
        """
        Test ID: TSO1PY00007
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open inward payment list url with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.inward_payment_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inward_payment_list_page_with_extra_parameters(self):
        """
        Test ID: TSO1PY00008
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open inward payment list url with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.inward_payment_list_url, {"dummy_param": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_uncredited_cheques_page_with_authenticated_user(self):
        """
        Test ID: TSO1PY00009
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open uncredited cheques url with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.uncredited_cheques_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_uncredited_cheques_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1PY00010
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open uncredited cheques url with unauthenticated user
        """
        response = self.client.get(self.uncredited_cheques_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_uncredited_cheques_page_with_invalid_token(self):
        """
        Test ID: TSO1PY00011
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open uncredited cheques url with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.uncredited_cheques_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_uncredited_cheques_page_with_extra_parameters(self):
        """
        Test ID: TSO1PY00012
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open uncredited cheques url with extra dummy parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.uncredited_cheques_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outward_payment_page_with_authenticated_user(self):
        """
        Test ID: TSO1PY00013
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open outward payment page url with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.outward_payment_page_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outward_payment_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1PY00014
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open outward payment page url with unauthenticated user
        """
        response = self.client.get(self.outward_payment_page_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outward_payment_page_with_invalid_token(self):
        """
        Test ID: TSO1PY00015
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open outward payment page url with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.outward_payment_page_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outward_payment_page_with_extra_parameters(self):
        """
        Test ID: TSO1PY00016
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open outward payment page url with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.outward_payment_page_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outward_payment_list_page_with_authenticated_user(self):
        """
        Test ID: TSO1PY00017
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open outward payment list page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.outward_payment_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outward_payment_list_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1PY00018
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open outward payment list page with unauthenticated user
        """
        response = self.client.get(self.outward_payment_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outward_payment_list_page_with_invalid_token(self):
        """
        Test ID: TSO1PY00019
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open outward payment list page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.outward_payment_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outward_payment_list_page_with_extra_parameters(self):
        """
        Test ID: TSO1PY00020
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open outward payment list page with extra dummy parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.outward_payment_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_payment_file_page_with_authenticated_user(self):
        """
        Test ID: TSO1PY00021
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open download payment file url with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.download_payment_file_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_payment_file_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1PY00022
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open download payment file url with unauthenticated user
        """
        response = self.client.get(self.download_payment_file_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_download_payment_file_page_with_invalid_token(self):
        """
        Test ID: TSO1PY00023
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open download payment file url with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.download_payment_file_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_download_payment_file_page_with_extra_parameters(self):
        """
        Test ID: TSO1PY00024
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open download payment file url with extra dummy parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.download_payment_file_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_payment_receipt_list_page_with_authenticated_user(self):
        """
        Test ID: TSO1PY00025
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open payment receipt list url (form download section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.get_payment_receipt_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_payment_receipt_list_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1PY00026
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open payment receipt list url (form download section) with unauthenticated user
        """
        response = self.client.get(self.get_payment_receipt_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_payment_receipt_list_page_with_invalid_token(self):
        """
        Test ID: TSO1PY00027
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open payment receipt list url (form download section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.get_payment_receipt_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_payment_receipt_list_page_with_extra_parameters(self):
        """
        Test ID: TSO1PY00028
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open payment receipt list url (form download section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.get_payment_receipt_list_url, {"dummy_parmas": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class InvoiceWebPageTest(WebPageSetup):
    """
    Test Suite ID: TS01
    Test Suite: Web Application
    Module: Invoice
    """

    def setUp(self):
        super().setUp()
        self.fetch_full_booking_invoice_url = reverse(viewname='fetch_full_booking_invoice_page')
        self.fetch_commission_booking_invoice_url = reverse(viewname='fetch_commission_booking_invoice_page')
        self.invoices_url = reverse(viewname='invoice_list_page')
        self.invoice_summary_url = reverse(viewname='invoice_summary_list_page')

    def test_fetch_full_booking_invoice_page_with_authenticated_user(self):
        """
        Test ID: TSO1IV00001
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open fetch full booking invoice url with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.fetch_full_booking_invoice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fetch_full_booking_invoice_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1IV00002
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open fetch full booking invoice url with unauthenticated user
        """
        response = self.client.get(self.fetch_full_booking_invoice_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fetch_full_booking_invoice_page_with_invalid_token(self):
        """
        Test ID: TSO1IV00003
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open fetch full booking invoice url with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.fetch_full_booking_invoice_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fetch_full_booking_invoice_page_with_extra_parameters(self):
        """
        Test ID: TSO1IV00004
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open fetch full booking invoice url with extra parameter
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.fetch_full_booking_invoice_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fetch_commission_booking_invoice_page_with_authenticated_user(self):
        """
        Test ID: TSO1IV00005
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open fetch commission booking invoice url with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.fetch_commission_booking_invoice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fetch_commission_booking_invoice_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1IV00006
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open fetch commission booking invoice url with unauthenticated user
        """
        response = self.client.get(self.fetch_commission_booking_invoice_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fetch_commission_booking_invoice_page_with_invalid_token(self):
        """
        Test ID: TSO1IV00007
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open fetch commission booking invoice url with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.fetch_commission_booking_invoice_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fetch_commission_booking_invoice_page_with_extra_parameters(self):
        """
        Test ID: TSO1IV00008
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open fetch commission booking invoice url with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.fetch_commission_booking_invoice_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoices_page_with_authenticated_user(self):
        """
        Test ID: TSO1IV00009
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open invoices url (from downloads section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.invoices_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoices_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1IV00010
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open invoices url (from downloads section) with unauthenticated user
        """
        response = self.client.get(self.invoices_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoices_page_with_invalid_token(self):
        """
        Test ID: TSO1IV00011
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open invoices url (from downloads section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.invoices_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoices_page_with_extra_parameters(self):
        """
        Test ID: TSO1IV00012
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open invoices url (from downloads section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.invoices_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoice_summary_page_with_authenticated_user(self):
        """
        Test ID: TSO1IV00013
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open invoices summary url (from downloads section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.invoice_summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoice_summary_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1IV00014
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open invoices summary url (from downloads section) with unauthenticated user
        """
        response = self.client.get(self.invoice_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoice_summary_page_with_invalid_token(self):
        """
        Test ID: TSO1IV00015
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open invoices summary url (from downloads section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.invoice_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoice_summary_page_with_extra_parameters(self):
        """
        Test ID: TSO1IV00016
        Created By: Adarsh Patel
        Created On: 05-Dec-2018
        Scenario: open invoices summary url (from downloads section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.invoice_summary_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreditDebitNoteIssueWebPageTest(WebPageSetup):
    """
    Test Suite ID: TS01
    Test Suite: Web Application
    Module: CreditDebitNoteIssue
    """

    def setUp(self):
        super().setUp()
        self.issue_credit_debit_note_url = reverse(viewname='issue_credit_debit_note_page')
        self.issue_credit_note_customer_url = reverse(viewname='issue_credit_note_customer_page')
        self.issue_credit_note_supplier_url = reverse(viewname='issue_credit_note_supplier_page')
        self.issue_debit_note_customer_url = reverse(viewname='issue_debit_note_customer_page')
        self.issue_debit_note_supplier_url = reverse(viewname='issue_debit_note_supplier_page')
        self.issue_credit_note_customer_direct_advance_url = reverse(
            viewname='issue_credit_note_customer_direct_advance_page')
        self.approve_credit_debit_note_url = reverse(viewname='approve_credit_debit_note_page')

    def test_issue_credit_debit_note_page_with_authenticated_user(self):
        """
        Test ID: TSO1CD00001
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit debit note page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_credit_debit_note_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_credit_debit_note_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1CD00002
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit debit note page with unauthenticated user
        """
        response = self.client.get(self.issue_credit_debit_note_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_credit_debit_note_page_with_invalid_token(self):
        """
        Test ID: TSO1CD00003
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit debit note page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.issue_credit_debit_note_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_credit_debit_note_page_with_extra_parameters(self):
        """
        Test ID: TSO1CD00004
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit debit note page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_credit_debit_note_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_credit_note_customer_page_with_authenticated_user(self):
        """
        Test ID: TSO1CD00005
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit debit note customer page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_credit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_credit_note_customer_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1CD00006
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit debit note customer page with unauthenticated user
        """
        response = self.client.get(self.issue_credit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_credit_note_customer_page_with_invalid_token(self):
        """
        Test ID: TSO1CD00007
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit debit note customer page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.issue_credit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_credit_note_customer_page_with_extra_parameters(self):
        """
        Test ID: TSO1CD00008
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit debit note customer page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_credit_note_customer_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_credit_note_supplier_page_with_authenticated_user(self):
        """
        Test ID: TSO1CD00009
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit note supplier page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_credit_note_supplier_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_credit_note_supplier_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1CD00010
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit note supplier page with unauthenticated user
        """
        response = self.client.get(self.issue_credit_note_supplier_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_credit_note_supplier_page_with_invalid_token(self):
        """
        Test ID: TSO1CD00011
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit note supplier page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.issue_credit_note_supplier_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_credit_note_supplier_page_with_extra_parameters(self):
        """
        Test ID: TSO1CD00012
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit note supplier page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_credit_note_supplier_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_debit_note_customer_page_with_authenticated_user(self):
        """
        Test ID: TSO1CD00013
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue debit note customer page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_debit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_debit_note_customer_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1CD00014
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue debit note customer page with unauthenticated user
        """
        response = self.client.get(self.issue_debit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_debit_note_customer_page_with_invalid_token(self):
        """
        Test ID: TSO1CD00015
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue debit note customer page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.issue_debit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_debit_note_customer_page_with_extra_parameters(self):
        """
        Test ID: TSO1CD00016
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue debit note customer page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_debit_note_customer_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_debit_note_supplier_page_with_authenticated_user(self):
        """
        Test ID: TSO1CD00017
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue debit note supplier page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_debit_note_supplier_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_debit_note_supplier_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1CD00018
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue debit note supplier page with unauthenticated user
        """
        response = self.client.get(self.issue_debit_note_supplier_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_debit_note_supplier_page_with_invalid_token(self):
        """
        Test ID: TSO1CD00019
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue debit note supplier page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.issue_debit_note_supplier_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_debit_note_supplier_page_with_extra_parameters(self):
        """
        Test ID: TSO1CD00020
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue debit note supplier page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_debit_note_supplier_url, {"dummy_parma": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_credit_note_customer_direct_advance_page_with_authenticated_user(self):
        """
        Test ID: TSO1CD00021
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit note customer direct advance page authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_credit_note_customer_direct_advance_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_credit_note_customer_direct_advance_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1CD00022
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit note customer direct advance page unauthenticated user
        """
        response = self.client.get(self.issue_credit_note_customer_direct_advance_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_credit_note_customer_direct_advance_page_with_invalid_token(self):
        """
        Test ID: TSO1CD00023
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit note customer direct advance page invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.issue_credit_note_customer_direct_advance_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_credit_note_customer_direct_advance_page_with_extra_parameters(self):
        """
        Test ID: TSO1CD00024
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open issue credit note customer direct advance page extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.issue_credit_note_customer_direct_advance_url, {"dummy_params": "dummy"},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_credit_debit_note_page_with_authenticated_user(self):
        """
        Test ID: TSO1CD00025
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open approve credit debit note page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_credit_debit_note_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_credit_debit_note_page_with_unauthenticated_user(self):
        """
        Test ID: TSO1CD00026
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open approve credit debit note page with unauthenticated user
        """
        response = self.client.get(self.approve_credit_debit_note_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_credit_debit_note_page_with_invalid_token(self):
        """
        Test ID: TSO1CD00027
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open approve credit debit note page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.approve_credit_debit_note_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_credit_debit_note_page_with_extra_parameters(self):
        """
        Test ID: TSO1CD00028
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open approve credit debit note page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_credit_debit_note_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UploadsWebPageTest(WebPageSetup):
    """
    Test Suite ID: TS01
    Test Suite: Web Application
    Module: Document Upload
    """

    def setUp(self):
        super().setUp()
        self.pod_upload_url = reverse(viewname='pod_upload_page')
        self.cheque_upload_url = reverse(viewname='cheque_upload_page')
        self.invoice_receipt_upload_url = reverse(viewname='invoice_receipt_upload_page')
        self.owner_upload_url = reverse(viewname='owner_upload_page')
        self.vehicle_upload_url = reverse(viewname='vehicle_upload_page')
        self.driver_upload_url = reverse(viewname='driver_upload_page')
        self.my_uploaded_pod_list_url = reverse(viewname='my_uploaded_pod_list_page')

    def test_pod_upload_page_with_authenticated_user(self):
        """
        Test ID: TS0DU00001
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pod upload page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.pod_upload_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pod_upload_page_with_unauthenticated_user(self):
        """
        Test ID: TS01DU00002
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pod upload page with unauthenticated user
        """
        response = self.client.get(self.pod_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pod_upload_page_with_invalid_token(self):
        """
        Test ID: TS01DU00003
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pod upload page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.pod_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pod_upload_page_with_extra_parameters(self):
        """
        Test ID: TS01DU0004
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pod upload page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.pod_upload_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cheque_upload_page_with_authenticated_user(self):
        """
        Test ID: TS0DU00005
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open cheque upload page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.cheque_upload_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cheque_upload_page_with_unauthenticated_user(self):
        """
        Test ID: TS0DU00006
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open cheque upload page with unauthenticated user
        """
        response = self.client.get(self.cheque_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cheque_upload_page_with_invalid_token(self):
        """
        Test ID: TS0DU00007
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open cheque upload page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.cheque_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cheque_upload_page_with_extra_parameters(self):
        """
        Test ID: TS0DU00008
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open cheque upload page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.cheque_upload_url, {"dummmy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoice_receipt_page_with_authenticated_user(self):
        """
        Test ID: TS0DU00009
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open invoice receipt upload page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.invoice_receipt_upload_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoice_receipt_page_with_unauthenticated_user(self):
        """
        Test ID: TS0DU00010
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open invoice receipt upload page with unauthenticated user
        """
        response = self.client.get(self.invoice_receipt_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoice_receipt_page_with_invalid_token(self):
        """
        Test ID: TS0DU00011
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open invoice receipt upload page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.invoice_receipt_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoice_receipt_page_with_extra_parameters(self):
        """
        Test ID: TS0DU00012
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open invoice receipt upload page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.invoice_receipt_upload_url, {"dummy_params": "dummy"}, fomrat='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_upload_page_with_authenticated_user(self):
        """
        Test ID: TS0DU00013
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner upload page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.owner_upload_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_upload_page_with_unauthenticated_user(self):
        """
        Test ID: TS0DU00014
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner upload page with unauthenticated user
        """
        response = self.client.get(self.owner_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_upload_page_with_invalid_token(self):
        """
        Test ID: TS0DU00015
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner upload page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.owner_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_upload_page_with_extra_parameters(self):
        """
        Test ID: TS0DU00016
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner upload page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.owner_upload_url, {"dummy_params": "dummy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_upload_page_with_authenticated_user(self):
        """
        Test ID: TS0DU00017
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open vehicle upload page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.vehicle_upload_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_upload_page_with_unauthenticated_user(self):
        """
        Test ID: TS0DU00018
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open vehicle upload page with unauthenticated user
        """
        response = self.client.get(self.vehicle_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vehicle_upload_page_with_invalid_token(self):
        """
        Test ID: TS0DU00019
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open vehicle upload page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.vehicle_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vehicle_upload_page_with_extra_parameters(self):
        """
        Test ID: TS0DU00020
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open vehicle upload page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.vehicle_upload_url, {"dummy_params": "dummy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_driver_upload_page_with_authenticated_user(self):
        """
        Test ID: TS0DU00021
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver upload page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.driver_upload_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_driver_upload_page_with_unauthenticated_user(self):
        """
        Test ID: TS0DU00022
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver upload page with unauthenticated user
        """
        response = self.client.get(self.driver_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_driver_upload_page_with_invalid_token(self):
        """
        Test ID: TS0DU00023
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver upload page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.driver_upload_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_driver_upload_page_with_extra_parameters(self):
        """
        Test ID: TS0DU00024
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver upload page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.driver_upload_url, {"dummy_params": "dummy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_uploaded_pod_list_page_with_authenticated_user(self):
        """
        Test ID: TS0DU00025
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open my uploaded pod list page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.my_uploaded_pod_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_uploaded_pod_list_page_with_unauthenticated_user(self):
        """
        Test ID: TS0DU00026
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open my uploaded pod list page with unauthenticated user
        """
        response = self.client.get(self.my_uploaded_pod_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_uploaded_pod_list_page_with_invalid_token(self):
        """
        Test ID: TS0DU00027
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open my uploaded pod list page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.my_uploaded_pod_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_uploaded_pod_list_page_with_extra_parameters(self):
        """
        Test ID: TS0DU00028
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open my uploaded pod list page with extra_parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.my_uploaded_pod_list_url, {"dummy_params": "dummy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserAgentWebPageTest(WebPageSetup):
    """
    Test Suite ID: TS01
    Test Suite: Web Application
    Module: User Agents (Registrations, Updates)
    """

    def setUp(self):
        super().setUp()
        self.vehicle_register_url = reverse(viewname='vehicle_register_page')
        self.owner_register_url = reverse(viewname='owner_register_page')
        self.sme_register_url = reverse(viewname='sme_register_page')
        self.supplier_register_url = reverse(viewname='supplier_register_page')
        self.driver_register_url = reverse(viewname='driver_register_page')
        self.team_owner_vehicle_list_url = reverse(viewname='team_owner_vehicle_list_page')
        self.sme_list_url = reverse(viewname='sme_list_page')
        self.supplier_list_url = reverse(viewname='supplier_list_page')
        self.driver_list_url = reverse(viewname='driver_list_page')

    def test_vechicle_register_page_with_authenticated_user(self):
        """
        Test ID: TS01UA00001
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open vehicle register page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.vehicle_register_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_register_page_with_unauthenticated_user(self):
        """
        Test ID: TS01UA00002
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open vehicle register page with unauthenticated user
        """
        response = self.client.get(self.vehicle_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vehicle_register_page_with_invalid_token(self):
        """
        Test ID: TS01UA00003
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open vehicle register page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.vehicle_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vechicle_register_page_with_extra_parameters(self):
        """
        Test ID: TS01UA00004
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open vehicle register page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.vehicle_register_url, {"dummy_params": "dummy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_register_page_with_authenticated_user(self):
        """
        Test ID: TS01UA00005
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner register page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.owner_register_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_register_page_with_unauthenticated_user(self):
        """
        Test ID: TS01UA00006
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner register page with unauthenticated user
        """
        response = self.client.get(self.owner_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_register_page_with_invalid_token(self):
        """
        Test ID: TS01UA00007
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner register page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.owner_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_register_page_with_extra_parameters(self):
        """
        Test ID: TS01UA00008
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner register page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.owner_register_url, {"dummy_params": "dummy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sme_register_page_with_authenticated_user(self):
        """
        Test ID: TS01UA00009
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open sme register page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.sme_register_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sme_register_page_with_unauthenticated_user(self):
        """
        Test ID: TS01UA00010
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open sme register page with unauthenticated user
        """
        response = self.client.get(self.sme_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_register_page_with_invalid_token(self):
        """
        Test ID: TS01UA00011
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open sme register page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.sme_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_register_page_with_extra_paramters(self):
        """
        Test ID: TS01UA00012
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open sme register page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.sme_register_url, {"dummy_params": "dummy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supplier_register_page_with_authenticated_user(self):
        """
        Test ID: TS01UA00013
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open supplier register page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.supplier_register_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supplier_register_page_with_unauthenticated_user(self):
        """
        Test ID: TS01UA00014
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open supplier register page with unauthenticated user
        """
        response = self.client.get(self.supplier_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_supplier_register_page_with_invalid_token(self):
        """
        Test ID: TS01UA00015
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open supplier register page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.supplier_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_supplier_register_page_with_extra_parameters(self):
        """
        Test ID: TS01UA00016
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open supplier register page with extra dummy parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.supplier_register_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_driver_register_page_with_authenticated_user(self):
        """
        Test ID: TS01UA00017
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver register page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.driver_register_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_driver_register_page_with_unauthenticated_user(self):
        """
        Test ID: TS01UA00018
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver register page with unauthenticated user
        """
        response = self.client.get(self.driver_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_driver_register_page_with_invalid_token(self):
        """
        Test ID: TS01UA00019
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver register page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.driver_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_driver_register_page_with_extra_parameters(self):
        """
        Test ID: TS01UA00020
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver register page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.driver_register_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_vehicle_list_page_with_authenticated_user(self):
        """
        Test ID: TS01UA00021
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner vehicle list page (from Updates section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.team_owner_vehicle_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_vehicle_list_page_with_unauthenticated_user(self):
        """
        Test ID: TS01UA00022
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner vehicle list page (from Updates section) with unauthenticated user
        """
        response = self.client.get(self.team_owner_vehicle_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_vehicle_list_page_with_invalid_token(self):
        """
        Test ID: TS01UA00023
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner vehicle list page (from Updates section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.team_owner_vehicle_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_vehicle_list_page_with_extra_parameters(self):
        """
        Test ID: TS01UA00024
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open owner vehicle list page (from Updates section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.team_owner_vehicle_list_url, {"dummy_params": "dummyw"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sme_list_page_with_authenticated_user(self):
        """
        Test ID: TS01UA00025
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open sme list page (from Updates section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.sme_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sme_list_page_with_unauthenticated_user(self):
        """
        Test ID: TS01UA00026
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open sme list page (from Updates section) with unauthenticated user
        """
        response = self.client.get(self.sme_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_list_page_with_invalid_token(self):
        """
        Test ID: TS01UA00027
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open sme list page (from Updates section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.sme_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_list_page_with_extra_parameters(self):
        """
        Test ID: TS01UA00028
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open sme list page (from Updates section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.sme_list_url, {"dummy_params": "dummy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supplier_list_page_with_authenticated_user(self):
        """
        Test ID: TS01UA00029
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open supplier list page (from Updates section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.supplier_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supplier_list_page_with_unauthenticated_user(self):
        """
        Test ID: TS01UA00030
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open supplier list page (from Updates section) with unauthenticated user
        """
        response = self.client.get(self.supplier_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_supplier_list_page_with_invalid_token(self):
        """
        Test ID: TS01UA00031
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open supplier list page (from Updates section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.supplier_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_supplier_list_page_with_extra_parameters(self):
        """
        Test ID: TS01UA00032
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open supplier list page (from Updates section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.supplier_list_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_driver_list_page_with_authenticated_user(self):
        """
        Test ID: TS01UA00033
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver list page (from Updates section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.driver_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_driver_list_page_with_unauthenticated_user(self):
        """
        Test ID: TS01UA00034
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver list page (from Updates section) with unauthenticated user
        """
        response = self.client.get(self.driver_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_driver_list_page_with_invalid_token(self):
        """
        Test ID: TS01UA00035
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver list page (from Updates section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.driver_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_driver_list_page_with_extra_parameters(self):
        """
        Test ID: TS01UA00036
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open driver list page (from Updates section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.driver_list_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BankAccountWebPageTest(WebPageSetup):
    """
    Test Suite ID: TS01
    Test Suite: Web Application
    Module: Bank Account
    """

    def setUp(self):
        super().setUp()
        self.fetch_ifsc_url = reverse(viewname='fetch_ifsc_page')
        self.bank_account_list_url = reverse(viewname='bank_account_list_page')

    def test_fetch_ifc_page_with_authenticated_user(self):
        """
        Test ID: TS01BA00001
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open fetch ifsc page (from Updates section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.fetch_ifsc_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fetch_ifc_page_with_unauthenticated_user(self):
        """
        Test ID: TS01BA00002
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open fetch ifsc page (from Updates section) with unauthenticated user
        """
        response = self.client.get(self.fetch_ifsc_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fetch_ifc_page_with_invalid_token(self):
        """
        Test ID: TS01BA00003
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open fetch ifsc page (from Updates section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.fetch_ifsc_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fetch_ifc_page_with_extra_parameters(self):
        """
        Test ID: TS01BA00004
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open fetch ifsc page (from Updates section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.fetch_ifsc_url, {"dummy_params": "dummy"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bank_account_list_page_with_authenticated_user(self):
        """
        Test ID: TS01BA00005
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open bank account list page (from Updates section) with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.bank_account_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bank_account_list_page_with_unauthenticated_user(self):
        """
        Test ID: TS01BA00006
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open bank account list page (from Updates section) with unauthenticated user
        """
        response = self.client.get(self.bank_account_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bank_account_list_page_with_invalid_token(self):
        """
        Test ID: TS01BA00007
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open bank account list page (from Updates section) with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.bank_account_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bank_account_list_page_with_extra_parameters(self):
        """
        Test ID: TS01BA00008
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open bank account list page (from Updates section) with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.bank_account_list_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TaskDashboardWebPageTest(WebPageSetup):
    """
    Test Suite ID: TS01
    Test Suite: Web Application
    Module: Task Dashboard
    """

    def setUp(self):
        super().setUp()
        self.confirm_new_booking_url = reverse(viewname='confirm_new_booking')
        self.generate_lr_url = reverse(viewname='generate_lr_page')
        self.bookings_pay_advance_url = reverse(viewname='bookings_pay_advance_page')
        self.booking_verify_pod_url = reverse(viewname='td_unverified_pod_list_page')
        self.pay_balance_booking_history_url = reverse(viewname='pay_balance_booking_history_page')
        self.raise_invoice_booking_history_url = reverse(viewname='raise_invoice_booking_history_page')
        self.process_payment_url = reverse(viewname='process_payment')
        self.reconsile_payment_url = reverse(viewname='raise_invoice_booking_history_page')
        self.pending_inward_list_url = reverse(viewname='pending_inward_list')
        self.upload_invoice_sent_receipt_url = reverse(viewname='upload_invoice_sent_receipt_page')
        self.confirm_invoice_sent_receipt_url = reverse(viewname='confirm_invoice_sent_receipt')

    def test_confirm_new_booking_page_with_authenticated_user(self):
        """
        Test ID: TS01TD00001
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open confirm new booking page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.confirm_new_booking_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_confirm_new_booking_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00002
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open confirm new booking page with unauthenticated user
        """
        response = self.client.get(self.confirm_new_booking_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_confirm_new_booking_page_with_invalid_token(self):
        """
        Test ID: TS01TD00003
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open confirm new booking page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.confirm_new_booking_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_confirm_new_booking_page_with_extra_parameters(self):
        """
        Test ID: TS01TD00004
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open confirm new booking page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.confirm_new_booking_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_generate_lr_page_with_authenticated_user(self):
        """
        Test ID: TS01TD00005
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open generate lr page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.generate_lr_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_generate_lr_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00006
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open generate lr page with unauthenticated user
        """
        response = self.client.get(self.generate_lr_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_generate_lr_page_with_invalid_token(self):
        """
        Test ID: TS01TD00007
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open generate lr page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.generate_lr_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_generate_lr_page_with_extra_parameters(self):
        """
        Test ID: TS01TD00008
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open generate lr page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.generate_lr_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bookings_pay_advance_page_with_authenticated_user(self):
        """
        Test ID: TS01TD00009
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open booking pay advance page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.bookings_pay_advance_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bookings_pay_advance_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00010
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open booking pay advance page with unauthenticated user
        """
        response = self.client.get(self.bookings_pay_advance_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bookings_pay_advance_page_with_invalid_token(self):
        """
        Test ID: TS01TD00011
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open booking pay advance page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.bookings_pay_advance_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bookings_pay_advance_page_with_extra_parameters(self):
        """
        Test ID: TS01TD00012
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open booking pay advance page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.bookings_pay_advance_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_booking_verify_pod_page_with_authenticated_user(self):
        """
        Test ID: TS01TD00013
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open booking verify pod page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.booking_verify_pod_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_booking_verify_pod_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00014
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open booking verify pod page with unauthenticated user
        """
        response = self.client.get(self.booking_verify_pod_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_booking_verify_pod_page_with_invalid_token(self):
        """
        Test ID: TS01TD00015
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open booking verify pod page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.booking_verify_pod_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_booking_verify_pod_page_with_extra_parameters(self):
        """
        Test ID: TS01TD00016
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open booking verify pod page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.booking_verify_pod_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pay_balance_booking_history_page_with_authenticated_user(self):
        """
        Test ID: TS01TD00017
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pay balance booking history page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.pay_balance_booking_history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pay_balance_booking_history_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00018
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pay balance booking history page with unauthenticated user
        """
        response = self.client.get(self.pay_balance_booking_history_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pay_balance_booking_history_page_with_invalid_token(self):
        """
        Test ID: TS01TD00019
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pay balance booking history page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.pay_balance_booking_history_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pay_balance_booking_history_page_with_extra_parameters(self):
        """
        Test ID: TS01TD00020
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pay balance booking history page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.pay_balance_booking_history_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_raise_invoice_booking_history_page_with_authenticated_user(self):
        """
        Test ID: TS01TD00021
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open raise invoice booking history page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.raise_invoice_booking_history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_raise_invoice_booking_history_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00022
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open raise invoice booking history page with unauthenticated user
        """
        response = self.client.get(self.raise_invoice_booking_history_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_raise_invoice_booking_history_page_with_invalid_token(self):
        """
        Test ID: TS01TD00023
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open raise invoice booking history page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.raise_invoice_booking_history_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_raise_invoice_booking_history_page_with_extra_parameters(self):
        """
        Test ID: TS01TD00024
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open raise invoice booking history page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.raise_invoice_booking_history_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_process_payment_page_with_authenticated_user(self):
        """
        Test ID: TS01TD00025
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open process payment page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.process_payment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_process_payment_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00026
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open process payment page with unauthenticated user
        """
        response = self.client.get(self.process_payment_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_process_payment_page_with_invalid_token(self):
        """
        Test ID: TS01TD00027
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open process payment page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.process_payment_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_process_payment_page_with_extra_parameters(self):
        """
        Test ID: TS01TD00028
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open process payment page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.process_payment_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reconcile_payment_page_with_authenticated_user(self):
        """
        Test ID: TS01TD00029
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open reconcile payment page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.reconsile_payment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reconcile_payment_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00030
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open reconcile payment page with unauthenticated user
        """
        response = self.client.get(self.reconsile_payment_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reconcile_payment_page_with_invalid_token(self):
        """
        Test ID: TS01TD00031
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open reconcile payment page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.reconsile_payment_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reconcile_payment_page_with_extra_parameters(self):
        """
        Test ID: TS01TD00032
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open reconcile payment page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.reconsile_payment_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pending_inward_list_page_with_authenticated_user(self):
        """
        Test ID: TS01TD00033
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pending inward list page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.pending_inward_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pending_inward_list_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00034
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pending inward list page with unauthenticated user
        """
        response = self.client.get(self.pending_inward_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pending_inward_list_page_with_invalid_token(self):
        """
        Test ID: TS01TD00035
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pending inward list page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.pending_inward_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pending_inward_list_page_with_extra_parameters(self):
        """
        Test ID: TS01TD00036
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open pending inward list page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.pending_inward_list_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_invoice_sent_receipt_page_with_authenticated_user(self):
        """
        Test ID: TS01TD00037
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open upload invoice sent receipt page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.upload_invoice_sent_receipt_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_invoice_sent_receipt_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00038
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open upload invoice sent receipt page with unauthenticated user
        """
        response = self.client.get(self.upload_invoice_sent_receipt_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_invoice_sent_receipt_page_with_invalid_token(self):
        """
        Test ID: TS01TD00039
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open upload invoice sent receipt page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.upload_invoice_sent_receipt_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_invoice_sent_receipt_page_with_extra_parameters(self):
        """
        Test ID: TS01TD00040
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open upload invoice sent receipt page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.upload_invoice_sent_receipt_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_confirm_invoice_sent_receipt_page_with_authenticated_user(self):
        """
        Test ID: TS01TD00041
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open confirm invoice sent receipt page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.confirm_invoice_sent_receipt_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_confirm_invoice_sent_receipt_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00042
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open confirm invoice sent receipt page with unauthenticated user
        """
        response = self.client.get(self.confirm_invoice_sent_receipt_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_confirm_invoice_sent_receipt_page_with_invalid_token(self):
        """
        Test ID: TS01TD00043
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open confirm invoice sent receipt page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.confirm_invoice_sent_receipt_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_confirm_invoice_sent_receipt_page_with_extra_parameters(self):
        """
        Test ID: TS01TD00044
        Created By: Adarsh Patel
        Created On: 06-Dec-2018
        Scenario: open confirm invoice sent receipt page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.confirm_invoice_sent_receipt_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RemainingPageUrlTest(WebPageSetup):
    """
    Test Suite ID: TS01
    Test Suite: Web Application
    Module: Test Coverage
    """

    def setUp(self):
        super().setUp()
        self.basic_full_booking_url = reverse(viewname='basic_full_booking_page')
        self.detailed_full_booking_url = reverse(viewname='detailed_full_booking_page')
        self.detailed_full_booking_page_mb_id_based_url = reverse(viewname='detailed_full_booking_page_mb_id_based',  kwargs={"pk": 5400 } )
        self.pending_inward_payment_adjustment_url = reverse(viewname='pending_inward_payment_adjustment')
        self.create_bank_account_url = reverse(viewname='create_bank_account_page')
        self.track_dashboard_url = reverse(viewname='track_dashboard_page')
        self.employee_profile_url = reverse(viewname='employee_profile_page')
        self.change_password_url = reverse(viewname='change_password_page')
        self.owner_list_url =  reverse(viewname='owner_list_page')
        self.sme_register_url = reverse(viewname='sme_register_page')
        self.partial_booking_list_url = reverse(viewname='partial_booking_list_page')
        self.approve_credit_note_customer_url = reverse(viewname='approve_credit_note_customer_page')
        self.approve_credit_note_supplier_url = reverse(viewname='approve_credit_note_supplier_page')
        self.approve_debit_note_customer_url = reverse(viewname='approve_debit_note_customer_page')
        self.approve_debit_note_supplier_url = reverse(viewname='approve_debit_note_supplier_page')
        self.approve_credit_note_customer_direct_advance_url = reverse(viewname='approve_credit_note_customer_direct_advance_page')
        self.monitoring_web_senior_mgmt_status_url = reverse(viewname='monitoring_web_senior_mgmt_status_page')
        self.monitoring_web_senior_mgmt_task_status_url = reverse(viewname='monitoring_web_senior_mgmt_task_status_page')

    def test_basic_full_booking_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00001
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open basic full booking page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.basic_full_booking_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_basic_full_booking_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00002
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open basic full booking page with unauthenticated user
        """
        response = self.client.get(self.basic_full_booking_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_basic_full_booking_page_with_invalid_token(self):
        """
        Test ID: TS01TC00003
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open basic full booking page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.basic_full_booking_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_basic_full_booking_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00004
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open basic full booking page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.basic_full_booking_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detailed_full_booking_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00005
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open detailed_full_booking_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.detailed_full_booking_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detailed_full_booking_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00006
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open detailed_full_booking_page with unauthenticated user
        """
        response = self.client.get(self.detailed_full_booking_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detailed_full_booking_page_with_invalid_token(self):
        """
        Test ID: TS01TC00007
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open detailed_full_booking_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.detailed_full_booking_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detailed_full_booking_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00008
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open detailed_full_booking_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.detailed_full_booking_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_detailed_full_booking_page_mb_id_based_with_authenticated_user(self):
    #     """
    #     Test ID: TS01TC00009
    #     Created By: Adarsh Patel
    #     Created On: 25-Dec-2018
    #     Scenario: open detailed_full_booking_page_mb_id_based with authenticated user
    #     """
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.get(self.detailed_full_booking_page_mb_id_based_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detailed_full_booking_page_mb_id_based_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00010
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open detailed_full_booking_page_mb_id_based with unauthenticated user
        """
        response = self.client.get(self.detailed_full_booking_page_mb_id_based_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detailed_full_booking_page_mb_id_based_with_invalid_token(self):
        """
        Test ID: TS01TC00011
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open detailed_full_booking_page_mb_id_based with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.detailed_full_booking_page_mb_id_based_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_detailed_full_booking_page_mb_id_based_with_extra_parameters(self):
    #     """
    #     Test ID: TS01TC00012
    #     Created By: Adarsh Patel
    #     Created On: 25-Dec-2018
    #     Scenario: open detailed_full_booking_page_mb_id_based with extra parameters
    #     """
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.get(self.detailed_full_booking_page_mb_id_based_url, {"dummy_params": "dummy"}, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_pending_inward_payment_adjustment_page_with_authenticated_user(self):
    #     """
    #     Test ID: TS01TC00013
    #     Created By: Adarsh Patel
    #     Created On: 25-Dec-2018
    #     Scenario: open pending_inward_payment_adjustment_page with authenticated user
    #     """
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.get(self.pending_inward_payment_adjustment_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pending_inward_payment_adjustment_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00014
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open pending_inward_payment_adjustment_page with unauthenticated user
        """
        response = self.client.get(self.pending_inward_payment_adjustment_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pending_inward_payment_adjustment_page_with_invalid_token(self):
        """
        Test ID: TS01TC00015
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open pending_inward_payment_adjustment_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.pending_inward_payment_adjustment_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_pending_inward_payment_adjustment_page_with_extra_parameters(self):
    #     """
    #     Test ID: TS01TC00016
    #     Created By: Adarsh Patel
    #     Created On: 25-Dec-2018
    #     Scenario: open pending_inward_payment_adjustment_page with extra parameters
    #     """
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.get(self.pending_inward_payment_adjustment_url, {"dummy_params": "dummy"}, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_bank_account_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00017
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open create_bank_account_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_bank_account_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_bank_account_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00018
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open create_bank_account_page with unauthenticated user
        """
        response = self.client.get(self.create_bank_account_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_bank_account_page_with_invalid_token(self):
        """
        Test ID: TS01TC00019
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open create_bank_account_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.create_bank_account_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_bank_account_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00020
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open create_bank_account_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.create_bank_account_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_track_dashboard_page_with_authenticated_user(self):
    #     """
    #     Test ID: TS01TC00021
    #     Created By: Adarsh Patel
    #     Created On: 25-Dec-2018
    #     Scenario: open track_dashboard_page with authenticated user
    #     """
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.get(self.track_dashboard_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_track_dashboard_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00022
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open track_dashboard_page with unauthenticated user
        """
        response = self.client.get(self.track_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_track_dashboard_page_with_invalid_token(self):
        """
        Test ID: TS01TC00023
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open track_dashboard_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.track_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_track_dashboard_page_with_extra_parameters(self):
    #     """
    #     Test ID: TS01TC00024
    #     Created By: Adarsh Patel
    #     Created On: 25-Dec-2018
    #     Scenario: open track_dashboard_page with extra parameters
    #     """
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.get(self.track_dashboard_url, {"dummy_params": "dummy"}, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_employee_profile_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00025
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open employee_profile_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.employee_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_employee_profile_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00026
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open employee_profile_page with unauthenticated user
        """
        response = self.client.get(self.employee_profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_profile_page_with_invalid_token(self):
        """
        Test ID: TS01TC00027
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open employee_profile_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.employee_profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_profile_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00028
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open employee_profile_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.employee_profile_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00029
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open change_password_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.change_password_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00030
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open change_password_page with unauthenticated user
        """
        response = self.client.get(self.change_password_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_page_with_invalid_token(self):
        """
        Test ID: TS01TC00031
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open change_password_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.change_password_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00032
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open change_password_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.change_password_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_list_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00033
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open owner_list_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.owner_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_list_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00034
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open owner_list_page with unauthenticated user
        """
        response = self.client.get(self.owner_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_list_page_with_invalid_token(self):
        """
        Test ID: TS01TC00035
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open owner_list_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.owner_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_list_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00036
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open owner_list_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.owner_list_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sme_register_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00037
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open sme_register_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.sme_register_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sme_register_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00038
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open sme_register_page with unauthenticated user
        """
        response = self.client.get(self.sme_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_register_page_with_invalid_token(self):
        """
        Test ID: TS01TC00039
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open sme_register_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.sme_register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_register_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00040
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open sme_register_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.sme_register_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_booking_list_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00041
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open partial_booking_list_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.partial_booking_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_booking_list_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00042
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open partial_booking_list_page with unauthenticated user
        """
        response = self.client.get(self.partial_booking_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_booking_list_page_with_invalid_token(self):
        """
        Test ID: TS01TC00043
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open partial_booking_list_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.partial_booking_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_booking_list_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00044
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open partial_booking_list_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.partial_booking_list_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_credit_note_customer_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00045
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_customer_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_credit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_credit_note_customer_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00046
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_customer_page with unauthenticated user
        """
        response = self.client.get(self.approve_credit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_credit_note_customer_page_with_invalid_token(self):
        """
        Test ID: TS01TC00047
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_customer_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.approve_credit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_credit_note_customer_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00048
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_customer_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_credit_note_customer_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_credit_note_supplier_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00049
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_supplier_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_credit_note_supplier_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_credit_note_supplier_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00050
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_supplier_page with unauthenticated user
        """
        response = self.client.get(self.approve_credit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_credit_note_supplier_page_with_invalid_token(self):
        """
        Test ID: TS01TC00051
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_supplier_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.approve_credit_note_supplier_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_credit_note_supplier_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00052
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_supplier_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_credit_note_supplier_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_debit_note_customer_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00053
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_debit_note_customer_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_debit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_debit_note_customer_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00054
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_debit_note_customer_page with unauthenticated user
        """
        response = self.client.get(self.approve_debit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_debit_note_customer_page_with_invalid_token(self):
        """
        Test ID: TS01TC00055
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_debit_note_customer_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.approve_debit_note_customer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_debit_note_customer_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00056
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_debit_note_customer_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_debit_note_customer_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_debit_note_supplier_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00057
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_debit_note_supplier_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_credit_note_supplier_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_debit_note_supplier_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00058
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_debit_note_supplier_page with unauthenticated user
        """
        response = self.client.get(self.approve_credit_note_supplier_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_debit_note_supplier_page_with_invalid_token(self):
        """
        Test ID: TS01TC00059
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_debit_note_supplier_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.approve_credit_note_supplier_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_debit_note_supplier_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00060
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_debit_note_supplier_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_credit_note_supplier_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_credit_note_customer_direct_advance_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00061
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_customer_direct_advance_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_credit_note_customer_direct_advance_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_credit_note_customer_direct_advance_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00062
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_customer_direct_advance_page with unauthenticated user
        """
        response = self.client.get(self.approve_credit_note_customer_direct_advance_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_credit_note_customer_direct_advance_page_with_invalid_token(self):
        """
        Test ID: TS01TC00063
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_customer_direct_advance_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.approve_credit_note_customer_direct_advance_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_credit_note_customer_direct_advance_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00064
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open approve_credit_note_customer_direct_advance_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.approve_credit_note_customer_direct_advance_url, {"dummy_params": "dummy"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_monitoring_web_senior_mgmt_status_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00065
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open monitoring_web_senior_mgmt_status_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.monitoring_web_senior_mgmt_status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_monitoring_web_senior_mgmt_status_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00066
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open monitoring_web_senior_mgmt_status_page with unauthenticated user
        """
        response = self.client.get(self.monitoring_web_senior_mgmt_status_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_monitoring_web_senior_mgmt_status_page_with_invalid_token(self):
        """
        Test ID: TS01TC00067
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open monitoring_web_senior_mgmt_status_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.monitoring_web_senior_mgmt_status_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_monitoring_web_senior_mgmt_status_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00068
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open monitoring_web_senior_mgmt_status_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.monitoring_web_senior_mgmt_status_url, {"dummy_params": "dummy"},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_monitoring_web_senior_mgmt_task_status_page_with_authenticated_user(self):
        """
        Test ID: TS01TC00069
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open monitoring_web_senior_mgmt_task_status_page with authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.monitoring_web_senior_mgmt_task_status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_monitoring_web_senior_mgmt_task_status_page_with_unauthenticated_user(self):
        """
        Test ID: TS01TD00070
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open monitoring_web_senior_mgmt_task_status_page with unauthenticated user
        """
        response = self.client.get(self.monitoring_web_senior_mgmt_task_status_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_monitoring_web_senior_mgmt_task_status_page_with_invalid_token(self):
        """
        Test ID: TS01TC00071
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open monitoring_web_senior_mgmt_task_status_page with invalid token
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        response = self.client.get(self.monitoring_web_senior_mgmt_task_status_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_monitoring_web_senior_mgmt_task_status_page_with_extra_parameters(self):
        """
        Test ID: TS01TC00072
        Created By: Adarsh Patel
        Created On: 25-Dec-2018
        Scenario: open monitoring_web_senior_mgmt_task_status_page with extra parameters
        """
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.monitoring_web_senior_mgmt_task_status_url, {"dummy_params": "dummy"},format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)