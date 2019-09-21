import json

from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import Profile
from employee.models import Employee
from sme.models import SmeTaskEmail, Sme, RateType, CustomerContract, ContractRoute, ContactDetails, Location, \
    ConsignorConsignee, PreferredVehicle, SmeEnquiry
from utils.models import State, City, Address, AahoOffice, Bank, TaxationID, IDDetails, VehicleCategory
from datetime import datetime


class SmeSetup(APITestCase):
    """
        Setup dummy data for tesing purpose
    """

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.test_user = User.objects.create_user('testUser', 'test@example.com', 'testPassword')
        self.profile = mommy.make(Profile, user=self.test_user, name='Mani', phone='8978937498')
        self.login_data = self.client.post(self.login_url, {"username": "testUser", "password": "testPassword"}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])
        self.state = mommy.make(State)
        self.city = mommy.make(City)
        self.address = mommy.make(Address)
        self.aaho_office = mommy.make(AahoOffice, branch_name='Raipur')
        self.aaho_poc = mommy.make(Employee)
        self.account_details = mommy.make(Bank)
        self.taxation_details = mommy.make(TaxationID)
        self.id_details = mommy.make(IDDetails)
        self.vehicle_category = mommy.make(VehicleCategory)

        self.sme_task_email = mommy.make(SmeTaskEmail)
        self.employee = mommy.make(Employee, username=self.test_user)
        self.sme = mommy.make(Sme, name=self.test_user, aaho_poc=self.employee, aaho_office=self.aaho_office,
                              city=self.city)
        self.rate_type = mommy.make(RateType)
        self.customer_contract = mommy.make(CustomerContract)
        self.contract_route = mommy.make(ContractRoute)
        self.contact_details = mommy.make(ContactDetails)
        self.location = mommy.make(Location)
        self.consignor_consignee = mommy.make(ConsignorConsignee)
        self.preferred_vehicle = mommy.make(PreferredVehicle)
        self.sme_enquiry = mommy.make(SmeEnquiry)


class SmeTaskEmailTest(SmeSetup):
    """
        Test cases for Sme Task Email
    """

    def setUp(self):
        super().setUp()
        self.sme_task_email_data = {

            "deleted": False,
            "deleted_on": None,
            "name": "test"
        }
        self.minimum_valid_data = {

        }
        self.create_url = reverse("sme_sme_task_email_create")
        self.update_url = reverse("sme_sme_task_email_update", kwargs={"pk": self.sme_task_email.id})
        self.partial_update_url = reverse("sme_sme_task_email_partial_update", kwargs={"pk": self.sme_task_email.id})
        self.retrieve_url = reverse("sme_sme_task_email_retrieve", kwargs={"pk": self.sme_task_email.id})
        self.filter_url = reverse("sme_sme_task_email_list")

    def test_create_sme_task_email_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Adding name to minimum data
    def test_create_sme_task_email_with_valid_name(self):
        data = self.minimum_valid_data.copy()
        data["name"] = "Mr.X"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Adding deleted to minimum data
    def test_create_sme_task_email_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] =  True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Adding deleted on to minimum data
    def test_create_sme_task_email_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_task_email_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_task_email_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.sme_task_email_data.copy()

        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.minimum_valid_data.copy()
        data["name"] = "a"*201
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.minimum_valid_data.copy()
        data["deleted_on"] = "invalid_format"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.sme_task_email_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.sme_task_email_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_sme_task_email_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_sme_task_email_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.sme_task_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_sme_task_email_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"name": "test"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_sme_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_sme_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("sme_sme_task_email_retrieve",
                                   kwargs={"pk": self.sme_task_email.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_sme_task_email_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.sme_task_email.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sme_task_email_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.sme_task_email.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sme_task_email_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_task_email_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_task_email_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_task_email_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class SmeTest(SmeSetup):
    """
        Test cases for Sme 
    """

    def setUp(self):
        super().setUp()
        self.sme_data = {
            "company_code": "DEM",
            "latest_lr_serial_number": 0,
            "lr_format_type": "D",
            "customer_address": "test",
            "credit_period": None,
            "pin": None,
            "gstin": None,
            "is_gst_applicable": "no",
            "status": "active",

            "deleted": False,
            "deleted_on": None,
            "name": self.test_user.username,
            "aaho_office": self.aaho_office.id,
            "aaho_poc": self.aaho_poc.id,
            "city": self.city.id,
            "id_proof": self.id_details.id,
            "account_details": self.account_details.id,
            "taxation_details": self.taxation_details.id,
            "email_tasks": [self.sme_task_email.id],
            "phone": "2323232323"
        }
        self.minimum_valid_data = {
            "company_code": "DEM",
            "name": self.test_user.username,
            "aaho_office": self.aaho_office.id,
            "aaho_poc": self.aaho_poc.id,
            "city": self.city.id,
            "phone": "2323232323"

        }
        self.create_url = reverse("sme_sme_create")
        self.update_url = reverse("sme_sme_update", kwargs={"pk": self.sme.id})
        self.partial_update_url = reverse("sme_sme_partial_update", kwargs={"pk": self.sme.id})
        self.retrieve_url = reverse("sme_sme_retrieve", kwargs={"pk": self.sme.id})
        self.filter_url = reverse("sme_sme_list")
        self.summary_url = reverse('sme_summary_sme_list')

    def test_create_sme_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_valid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = "valid_name"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = "v" * 199
        data['company_code'] = 'DEA'
        data["phone"] = '8911137471'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["name"] = None
        data['company_code'] = 'DEB'
        data["phone"] = '8911137472'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_invalid_name(self):
        data = self.minimum_valid_data.copy()

        data["name"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["name"] = "v" * 201
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_phone(self):
        data = self.minimum_valid_data.copy()

        data["phone"] = 9939717009
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = "8978937400"
        data["company_code"] = "DEA"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = u"8978937401"
        data["company_code"] = "DEB"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["phone"] = " 9939717001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "9939717002 "
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_invalid_phone(self):
        data = self.minimum_valid_data.copy()

        data["phone"] = "993971700p"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "99397170088"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "939717008"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["phone"] = "transiq tec"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_gstin(self):
        data = self.minimum_valid_data.copy()

        data["is_gst_applicable"] = "yes"
        data["gstin"] = "12abcde1234a1Zh"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gstin"] = "12ABCDE1234A1z2"
        data['company_code'] = 'DEA'
        data['phone'] = '9939717009'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_gst_applicable"] = "yes"
        data["gstin"] = " 12abcde1234a1zh"
        data['company_code'] = 'DEB'
        data['phone'] = '9939717001'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gstin"] = "12abcde1234a1zh "
        data['company_code'] = 'DEC'
        data['phone'] = '9939717002'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gstin"] = None
        data['company_code'] = 'DED'
        data['phone'] = '9939717004'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_invalid_gstin(self):
        data = self.minimum_valid_data.copy()

        data["gstin"] = "abcde1234a1zh"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = "12abcde1234a1z"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = "12abcde1234a1ah"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = "a2abcde1234a1z2"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = "1babcde1234a1zh"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = "12ab3de1234a1zh"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = "12abcdef234a1z2"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = "12ABCDEFG34A1ZA"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = "12ABCDEFG34A1ZA"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = "12abcde123aa1zh"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = "transiq tec"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_company_code(self):
        data = self.minimum_valid_data.copy()

        data["company_code"] = "abD"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_invalid_company_code(self):
        data = self.minimum_valid_data.copy()

        data["company_code"] = "ab"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["company_code"] = "abcd"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["company_code"] = "1a2"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["company_code"] = "@#$"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["company_code"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["company_code"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_credit_period(self):
        data = self.minimum_valid_data.copy()
        data["credit_period"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["credit_period"] = 50
        data["company_code"] = "DEA"
        data["phone"] = "9939717001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["credit_period"] = 180
        data["company_code"] = "DEB"
        data["phone"] = "9939717002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_invalid_credit_period(self):
        data = self.minimum_valid_data.copy()
        data["credit_period"] = -20
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_period"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_period"] = "invalid_credit_period"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_period"] = 181
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_contact_person_name(self):
        data = self.minimum_valid_data.copy()

        data["contact_person_name"] = "some_name"
        data["company_code"] = "DEA"
        data["phone"] = "9939717001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_person_name"] = "a" * 69
        data["company_code"] = "DEB"
        data["phone"] = "9939717004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_person_name"] = "a" * 70
        data["company_code"] = "DEC"
        data["phone"] = "9939717003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_person_name"] = None
        data["company_code"] = "DED"
        data["phone"] = "9939717002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_invalid_contact_person_name(self):
        data = self.minimum_valid_data.copy()

        data["contact_person_name"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_name"] = "a" * 71
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_name"] = "         "
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_contact_person_phone(self):
        data = self.minimum_valid_data.copy()

        data["contact_person_phone"] = 9939717009
        data["company_code"] = "DEA"
        data["phone"] = "9939717001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_person_phone"] = "8978937498"
        data["company_code"] = "DEB"
        data["phone"] = "9939717002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_person_phone"] = u"8978937498"
        data["company_code"] = "DEC"
        data["phone"] = "9939717003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["contact_person_phone"] = " 9939717001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = "9939717002 "
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_invalid_contact_person_phone(self):
        data = self.minimum_valid_data.copy()

        data["contact_person_phone"] = "993971700p"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = "99397170088"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = "939717008"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["contact_person_phone"] = "transiq tec"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_aaho_poc(self):
        data = self.minimum_valid_data.copy()

        data["aaho_poc"] = self.aaho_poc.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_invalid_aaho_poc(self):
        data = self.minimum_valid_data.copy()

        data["aaho_poc"] = -10  # negative id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = 0  # zero id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = 12345675890  # out of range value id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = 123.456  # floating value id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = "aaho"  # string  id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = None  # None value as id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = ""  # empty string as id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = "@3&!#1!"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = [self.aaho_poc.id, self.aaho_poc.id + 1, self.aaho_poc.id + 2]
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_aaho_office(self):
        data = self.minimum_valid_data.copy()

        data["aaho_office"] = self.aaho_office.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_invalid_aaho_office(self):
        data = self.minimum_valid_data.copy()

        data["aaho_office"] = -10  # negative id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = 0  # zero id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = 12345675890  # out of range value id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = 123.456  # floating value id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = "aaho"  # string  id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = None  # None value as id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = ""  # empty string as id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = "@3&!#1!"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_office"] = [self.aaho_office.id, self.aaho_office.id + 1, self.aaho_office.id + 2]
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_company_address(self):
        data = self.minimum_valid_data.copy()

        data["company_address"] = "some_valid_address"
        data["phone"] = '2323232302'
        data["company_code"] = 'DEB'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["company_address"] = "a" * 300
        data["phone"] = '2323232303'
        data["company_code"] = 'DEC'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_invalid_company_address(self):
        data = self.minimum_valid_data.copy()

        data["company_address"] = "     "
        data["phone"] = '2323232301'
        data["company_code"] = 'DEA'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["company_address"] = ""
        data["phone"] = '2323232302'
        data["company_code"] = 'DEB'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["company_address"] = "a" * 301
        data["phone"] = '2323232303'
        data["company_code"] = 'DEC'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_alternate_phone(self):
        data = self.minimum_valid_data.copy()

        data["alternate_phone"] = 9939717009
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["alternate_phone"] = "8978937498"
        data["phone"] = '2323232301'
        data["company_code"] = 'DEB'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["alternate_phone"] = u"8978937498"
        data["phone"] = '2323232303'
        data["company_code"] = 'DEC'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["alternate_phone"] = None
        data["phone"] = '2323232304'
        data["company_code"] = 'DED'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_invalid_alternate_phone(self):
        data = self.minimum_valid_data.copy()

        data["alternate_phone"] = "993971700p"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["alternate_phone"] = "99397170088"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["alternate_phone"] = "939717008"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["alternate_phone"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["alternate_phone"] = "transiq tec"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_email(self):
        data = self.minimum_valid_data.copy()

        data["email"] = "email@domain.com"  # valid email
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = "firstname.lastname@domain.com"  # Email contains dot in the address field
        data["phone"] = '1212000000'
        data["company_code"] = 'zzz'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = "email@subdomain.domain.com"  # Email contains dot with subdomain
        data["phone"] = '1212000001'
        data["company_code"] = 'zxv'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = "firstname+lastname@domain.com"  # Plus sign is considered valid character
        data["phone"] = '1212000002'
        data["company_code"] = 'zxb'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = "email@123.123.123.123"  # Domain is valid IP address
        data["phone"] = '1212000003'
        data["company_code"] = 'zxs'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #
        # data["email"] = "email@[123.123.123.123]"  #Square bracket around IP address is considered valid
        # data["phone"] = '1212000004'
        # data["company_code"] = 'zxt'
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = "1234567890@domain.com"  # Digits in address are valid
        data["phone"] = '1212000005'
        data["company_code"] = 'zxm'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = "email@domain-one.com"  # Dash in domain name is valid
        data["phone"] = '1212000006'
        data["company_code"] = 'zxl'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = "_______@domain.com"  # Underscore in the address field is valid
        data["phone"] = '1212000007'
        data["company_code"] = 'zxk'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = "email@domain.name"  # .name is valid Top Level Domain name
        data["phone"] = '1212000008'
        data["company_code"] = 'zxj'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data[
            "email"] = "email@domain.co.jp"  # Dot in Top Level Domain name also considered valid (use co.jp as example here)
        data["phone"] = '1212000009'
        data["company_code"] = 'zxh'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = "firstname-lastname@domain.com"  # Dash in address field is valid
        data["phone"] = '1212000010'
        data["company_code"] = 'zxg'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = "email@domain.web"  # .web is not a valid top level domain (drf is supporting this format)
        data["phone"] = '1312000013'
        data["company_code"] = 'qxs'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["email"] = "email@111.222.333.44444"  # Invalid IP format (drf supporting this format)
        data["phone"] = '1312000014'
        data["company_code"] = 'qxa'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_invalid_email(self):
        data = self.minimum_valid_data.copy()

        data["email"] = "plainaddress"  # Missing @ sign and domai
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "#@%^%#$@#$@#.com"  # Garbage
        data["phone"] = '1312000000'
        data["company_code"] = 'qzz'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "@domain.com"  # Missing username
        data["phone"] = '1312000001'
        data["company_code"] = 'qxv'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "Joe Smith <email@domain.com>"  # Encoded html within email is invalid
        data["phone"] = '1312000002'
        data["company_code"] = 'qxb'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "email.domain.com"  # Missing @
        data["phone"] = '1312000003'
        data["company_code"] = 'qxs'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "email@domain@domain.com"  # Two @ sign
        data["phone"] = '1312000005'
        data["company_code"] = 'qxm'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = ".email@domain.com"  # Leading dot in address is not allowed
        data["phone"] = '1312000006'
        data["company_code"] = 'qxl'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "email.@domain.com"  # Trailing dot in address is not allowed
        data["phone"] = '1312000007'
        data["company_code"] = 'qxk'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "email..email@domain.com"  # Multiple dots
        data["phone"] = '1312000008'
        data["company_code"] = 'qxj'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "あいうえお@domain.com"  # Unicode char as address
        data["phone"] = '1312000009'
        data["company_code"] = 'qxh'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "email@domain.com (Joe Smith)"  # Text followed email is not allowed
        data["phone"] = '1312000010'
        data["company_code"] = 'qxg'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "email@domain"  # Missing top level domain (.com/.net/.org/etc)
        data["phone"] = '1312000011'
        data["company_code"] = 'qxd'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "email@-domain.com"  # Leading dash in front of domain is invalid
        data["phone"] = '1312000012'
        data["company_code"] = 'qxh'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["email"] = "email@domain..com"  # Multiple dot in the domain portion is invalid
        data["phone"] = '1312000015'
        data["company_code"] = 'qxq'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_valid_city(self):
        data = self.minimum_valid_data.copy()
        data["city"] = self.city.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_invalid_city(self):
        data = self.minimum_valid_data.copy()

        data["city"] = -10  # negative id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = 0  # zero id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = 12345675890  # out of range value id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = 123.456  # floating value id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = "aaho"  # string  id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = None  # None value as id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = ""  # empty string as id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = "@3&!#1!"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = [self.city.id, self.city.id + 1, self.city.id + 2]
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_with_lr_format_type(self):
        data = self.minimum_valid_data.copy()
        data["lr_format_type"] = "D"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_with_duplicate_company_code(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.sme_data.copy()
        data["company_code"] = self.sme.company_code
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sme_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.sme_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.sme_data.copy()
        data["aaho_poc"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["aaho_poc"] = self.aaho_poc.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.sme_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.sme_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_sme_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_sme_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.sme_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_sme_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"name": self.test_user.username}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_sme_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_sme_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("sme_sme_retrieve",
                                   kwargs={"pk": self.sme.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_sme_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = "{}?{}".format(self.filter_url, "id={}".format(self.sme.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sme_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.sme.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sme_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sme_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_sme_summary_list_page(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.summary_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RateTypeTest(SmeSetup):
    """
        Test cases for Rate Type
    """

    def setUp(self):
        super().setUp()
        self.rate_type_data = {
            "name": "test",
            "deleted": False,
            "deleted_on": None,
        }
        self.minimum_valid_data = {

        }
        self.create_url = reverse("sme_rate_type_create")
        self.update_url = reverse("sme_rate_type_update", kwargs={"pk": self.rate_type.id})
        self.partial_update_url = reverse("sme_rate_type_partial_update", kwargs={"pk": self.rate_type.id})
        self.retrieve_url = reverse("sme_rate_type_retrieve", kwargs={"pk": self.rate_type.id})
        self.filter_url = reverse("sme_rate_type_list")

    def test_create_rate_type_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding name field to minimum data
    def test_create_rate_type_with_valid_name(self):
        data = self.minimum_valid_data.copy()
        data["name"] = "Mr.X"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted field to minimum data
    def test_create_rate_type_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted on field to minimum data
    def test_create_rate_type_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_rate_type_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.rate_type_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_rate_type_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.rate_type_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.rate_type_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.rate_type_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_rate_type_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_rate_type_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.rate_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_rate_type_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"name": self.test_user.username}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_rate_type_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_rate_type_task_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("sme_rate_type_retrieve",
                                   kwargs={"pk": self.rate_type.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_rate_type_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = "{}?{}".format(self.filter_url, "id={}".format(self.rate_type.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rate_type_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.rate_type.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rate_type_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rate_type_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rate_type_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rate_type_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CustomerContractTest(SmeSetup):
    """
        Test cases for Customer Contract
    """

    def setUp(self):
        super().setUp()
        self.customer_contract_data = {
            "start_date": "2016-12-06",
            "end_date": None,
            "billing_frequency": "d",
            "deleted": False,
            "deleted_on": None,
            "customer": self.sme.id
        }
        self.minimum_valid_data = {

        }
        self.create_url = reverse("sme_customer_contract_create")
        self.update_url = reverse("sme_customer_contract_update", kwargs={"pk": self.customer_contract.id})
        self.partial_update_url = reverse("sme_customer_contract_partial_update",
                                          kwargs={"pk": self.customer_contract.id})
        self.retrieve_url = reverse("sme_customer_contract_retrieve", kwargs={"pk": self.customer_contract.id})
        self.filter_url = reverse("sme_customer_contract_list")

    def test_create_customer_contract_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding start date to minimum data
    def test_create_customer_contract_with_valid_start_date(self):
        data = self.minimum_valid_data.copy()
        data["start_date"] = "2018-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding end date to minimum data
    def test_create_customer_contract_with_valid_end_date(self):
        data = self.minimum_valid_data.copy()
        data["end_date"] = "2018-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted to minimum data
    def test_create_customer_contract_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted on to minimum data
    def test_create_customer_contract_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_customer_contract_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding billing_frequency to minimum valid data
    def test_create_sme_with_billing_frequency(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.customer_contract_data.copy()
        data["billing_frequency"] = "d"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding customer to minimum valid data
    def test_create_sme_with_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.customer_contract_data.copy()
        data["customer"] = self.sme.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_customer_contract_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.customer_contract_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.customer_contract_data.copy()
        data["customer"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = self.sme.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.customer_contract_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.customer_contract_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_customer_contract_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_customer_contract_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.customer_contract_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_customer_contract_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"customer": self.sme.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_customer_contract(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_customer_contract(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("sme_customer_contract_retrieve",
                                   kwargs={"pk": self.customer_contract.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_customer_contract_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.customer_contract.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_contract_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.customer_contract.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_contract_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_contract_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_contract_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_contract_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ContractRouteTest(SmeSetup):
    """
        Test cases for Contract Route
    """

    def setUp(self):
        super().setUp()
        self.contract_route_data = {
            "rate": 0,
            "deleted": False,
            "deleted_on": None,
            "contract": self.customer_contract.id,
            "source": self.city.id,
            "destination": self.city.id,
            "rate_type": self.rate_type.id
        }
        self.minimum_valid_data = {

        }
        self.create_url = reverse("sme_contract_route_create")
        self.update_url = reverse("sme_contract_route_update", kwargs={"pk": self.contract_route.id})
        self.partial_update_url = reverse("sme_contract_route_partial_update", kwargs={"pk": self.contract_route.id})
        self.retrieve_url = reverse("sme_contract_route_retrieve", kwargs={"pk": self.contract_route.id})
        self.filter_url = reverse("sme_contract_route_list")

    def test_create_contract_route_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding rate to minimum data
    def test_create_contract_route_with_valid_rate(self):
        data = self.minimum_valid_data.copy()
        data["rate"] = 12000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted to minimum data
    def test_create_contract_route_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted on to minimum data
    def test_create_contract_route_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding source to minimum data
    def test_create_contract_route_with_valid_source(self):
        data = self.minimum_valid_data.copy()
        data["source"] = self.city.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding rate type to minimum data
    def test_create_contract_route_with_valid_rate_type(self):
        data = self.minimum_valid_data.copy()
        data["rate_type"] = self.rate_type.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_contract_route_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding destination to minimum valid data
    def test_create_sme_with_destination(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.contract_route_data.copy()
        data["destination"] = self.city.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_contract_route_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.contract_route_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.contract_route_data.copy()
        data["rate"] = -23
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.contract_route_data.copy()
        data["destination"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["destination"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["destination"] = self.city.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.contract_route_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.contract_route_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_contract_route_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_contract_route_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.contract_route_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_contract_route_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"source": self.city.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_contract_route(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_contract_route(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("sme_contract_route_retrieve",
                                   kwargs={"pk": self.contract_route.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_contract_route_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.contract_route.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contract_route_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.contract_route.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contract_route_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_contract_route_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_contract_route_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_contract_route_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ContactDetailsTest(SmeSetup):
    """
        Test cases for Contact Details
    """

    def setUp(self):
        super().setUp()
        self.contact_details_data = {
            "deleted": False,
            "deleted_on": None,
            "type": "primary",
            "name": "A Kapoor",
            "phone": "8989937498",
            "alternate_phone": "8989937498",
            "email": "akapoor@sme.in",
            "alternate_email": "akapoor@sme.in",
            "designation": "Manager",
            "status": "active",
            "sme": self.sme.id
        }
        self.minimum_valid_data = {
            "sme": self.sme.id
        }
        self.create_url = reverse("sme_contact_details_create")
        self.update_url = reverse("sme_contact_details_update", kwargs={"pk": self.contact_details.id})
        self.partial_update_url = reverse("sme_contact_details_partial_update", kwargs={"pk": self.contact_details.id})
        self.retrieve_url = reverse("sme_contact_details_retrieve", kwargs={"pk": self.contact_details.id})
        self.filter_url = reverse("sme_contact_details_list")

    def test_create_contact_details_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_contact_details_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding choice field to minimum valid data
    def test_create_sme_with_choice(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.contact_details_data.copy()
        data["type"] = "primary"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding email field to minimum valid data
    def test_create_sme_with_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.contact_details_data.copy()
        data["email"] = "akapoor@sme.in"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_contact_details_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.contact_details_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.contact_details_data.copy()
        data["type"] = "invalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.contact_details_data.copy()
        data["email"] = "invalidEmail"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.contact_details_data.copy()
        data["sme"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["sme"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["sme"] = self.sme.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.contact_details_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.contact_details_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_contact_details_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_contact_details_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.contact_details_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_contact_details_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"sme": self.sme.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_contact_details(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_contact_details(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("sme_contact_details_retrieve",
                                   kwargs={"pk": self.contact_details.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_contact_details_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.contact_details.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contact_details_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.contact_details.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contact_details_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_contact_details_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_contact_details_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_contact_details_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class LocationTest(SmeSetup):
    """
        Test cases for Location
    """

    def setUp(self):
        super().setUp()
        self.location_data = {
            "deleted": False,
            "deleted_on": None,
            "type": "loading",
            "address": "Powai",
            "material": "steel",
            "latitude": "23.12",
            "longitude": "12.21",
            "status": "active",
            "sme": self.sme.id,
            "contact": self.contact_details.id,
            "city": self.city.id
        }
        self.minimum_valid_data = {}
        self.create_url = reverse("sme_location_create")
        self.update_url = reverse("sme_location_update", kwargs={"pk": self.location.id})
        self.partial_update_url = reverse("sme_location_partial_update", kwargs={"pk": self.location.id})
        self.retrieve_url = reverse("sme_location_retrieve", kwargs={"pk": self.location.id})
        self.filter_url = reverse("sme_location_list")

    def test_create_location_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_location_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding type field to minimum valid data
    def test_create_sme_with_choice(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.location_data.copy()
        data["type"] = "loading"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding sme field to minimum valid data
    def test_create_sme_with_sme(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.location_data.copy()
        data["sme"] = self.sme.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_location_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.location_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.location_data.copy()
        data["type"] = "invalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.location_data.copy()
        data["sme"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["sme"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["sme"] = self.sme.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.location_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.location_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_location_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_location_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_location_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"sme": self.sme.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_location(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_location(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("sme_location_retrieve",
                                   kwargs={"pk": self.location.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_location_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.location.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_location_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.location.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_location_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_location_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_location_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_location_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ConsignorConsigneeTest(SmeSetup):
    """
        Test cases for Consignor Consignee
    """

    def setUp(self):
        super().setUp()
        self.consignor_consignee_data = {
            "deleted": False,
            "deleted_on": None,
            "type": "consignor",
            "name": "Canpac Trends Pvt. Ltd.",
            "address": "Plot no. 338, Chiyada Village,    B/h Kerala GIDC, Bavla",
            "pin": "382220",
            "phone": "1232123212",
            "tax_id": "test",
            "status": "active",
            "sme": self.sme.id,
            "city": self.city.id
        }
        self.minimum_valid_data = {
            "type": "consignor"
        }
        self.create_url = reverse("sme_consignor_consignee_create")
        self.update_url = reverse("sme_consignor_consignee_update", kwargs={"pk": self.consignor_consignee.id})
        self.partial_update_url = reverse("sme_consignor_consignee_partial_update",
                                          kwargs={"pk": self.consignor_consignee.id})
        self.retrieve_url = reverse("sme_consignor_consignee_retrieve", kwargs={"pk": self.consignor_consignee.id})
        self.filter_url = reverse("sme_consignor_consignee_list")

    def test_create_consignor_consignee_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_consignor_consignee_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding name field to minimum valid data
    def test_create_sme_with_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.consignor_consignee_data.copy()
        data["name"] = "Canpac Trends Pvt. Ltd"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding sme field to minimum valid data
    def test_create_sme_with_sme(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.consignor_consignee_data.copy()
        data["sme"] = self.sme.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_consignor_consignee_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.consignor_consignee_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.consignor_consignee_data.copy()
        data["type"] = "invalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.consignor_consignee_data.copy()
        data["sme"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["sme"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["sme"] = self.sme.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.consignor_consignee_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.consignor_consignee_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_consignor_consignee_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_consignor_consignee_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_consignor_consignee_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"sme": self.sme.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_consignor_consignee(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_consignor_consignee(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("sme_consignor_consignee_retrieve",
                                   kwargs={"pk": self.consignor_consignee.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_consignor_consignee_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.consignor_consignee.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_consignor_consignee_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.consignor_consignee.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_consignor_consignee_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_consignor_consignee_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_consignor_consignee_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_consignor_consignee_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class PreferredVehicleTest(SmeSetup):
    """
        Test cases for Preferred Vehicle
    """

    def setUp(self):
        super().setUp()
        self.preferred_vehicle_data = {
            "deleted": False,
            "deleted_on": None,
            "category": self.vehicle_category.id,
            "sme": self.sme.id,
        }
        self.minimum_valid_data = {
            "category": self.vehicle_category.id,
            "sme": self.sme.id,
        }
        self.create_url = reverse("sme_preferred_vehicle_create")
        self.update_url = reverse("sme_preferred_vehicle_update", kwargs={"pk": self.preferred_vehicle.id})
        self.partial_update_url = reverse("sme_preferred_vehicle_partial_update",
                                          kwargs={"pk": self.preferred_vehicle.id})
        self.retrieve_url = reverse("sme_preferred_vehicle_retrieve", kwargs={"pk": self.preferred_vehicle.id})
        self.filter_url = reverse("sme_preferred_vehicle_list")

    def test_create_preferred_vehicle_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted to minimum data
    def test_create_preferred_vehicle_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding deleted on to minimum data
    def test_create_preferred_vehicle_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_preferred_vehicle_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_preferred_vehicle_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.preferred_vehicle_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.preferred_vehicle_data.copy()
        data["sme"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["sme"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["sme"] = self.sme.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.preferred_vehicle_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.preferred_vehicle_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_preferred_vehicle_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_preferred_vehicle_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.preferred_vehicle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_preferred_vehicle_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"sme": self.sme.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_preferred_vehicle(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_preferred_vehicle(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("sme_preferred_vehicle_retrieve",
                                   kwargs={"pk": self.preferred_vehicle.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter
    def test_preferred_vehicle_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.preferred_vehicle.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_preferred_vehicle_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.preferred_vehicle.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_preferred_vehicle_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_preferred_vehicle_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_preferred_vehicle_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_preferred_vehicle_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class SmeEnquiryTest(SmeSetup):
    """
        Test cases for Sme Enquiry
    """

    def setUp(self):
        super().setUp()
        self.sme_enquiry_data = {
            "subject": "test",
            "message": "test",
            "status": "active",
            "deleted": False,
            "deleted_on": None,
            "sme": self.sme.id,
        }
        self.minimum_valid_data = {}
        self.create_url = reverse("sme_sme_enquiry_create")
        self.update_url = reverse("sme_sme_enquiry_update", kwargs={"pk": self.sme_enquiry.id})
        self.partial_update_url = reverse("sme_sme_enquiry_partial_update",
                                          kwargs={"pk": self.sme_enquiry.id})
        self.retrieve_url = reverse("sme_sme_enquiry_retrieve", kwargs={"pk": self.sme_enquiry.id})

    def test_create_sme_enquiry_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding status field to minimum valid data
    def test_create_sme_with_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.sme_enquiry_data.copy()
        data["status"] = "active"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding sme field to minimum valid data
    def test_create_sme_with_sme(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.sme_enquiry_data.copy()
        data["sme"] = self.sme.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_enquiry_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sme_enquiry_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.sme_enquiry_data.copy()
        data["deleted"] = "2016-12-06"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.sme_enquiry_data.copy()
        data["status"] = "invalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["sme"] = "asdsad"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["sme"] = self.sme.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.sme_enquiry_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.sme_enquiry_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_sme_enquiry_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_sme_enquiry_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.sme_enquiry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_sme_enquiry_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"sme": self.sme.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_sme_enquiry(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_sme_enquiry(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("sme_sme_enquiry_retrieve",
                                   kwargs={"pk": self.sme_enquiry.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
