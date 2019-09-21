import json

from model_mommy import mommy
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User, Group

from authentication.models import Profile
from broker.models import Broker
from fms.models import Requirement
from sme.models import Sme
from supplier.models import Supplier
from utils.models import City, State, AahoOffice


class ReqQuotesTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.reqquoteslist_url = reverse('req_quotes_list')
        self.reqquotescreate_url = reverse('req_quotes_create')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harshadasawant89@gmail.com',
                                             password='abc12345')
        self.profile = mommy.make(Profile, user=self.user)

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'abc12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = 'Token {}'.format(self.login_data['token'])

        self.client_user = User.objects.create_user(username='david',
                                                    email='harshadasawant89@gmail.com',
                                                    password='pqr12345'
                                                    )
        self.profile = mommy.make(Profile, user=self.client_user)
        self.sme = mommy.make(Sme, name=self.client_user)
        self.sme_group = mommy.make(Group, name='sme')

        self.broker_user = User.objects.create_user(username='james',
                                                    email='harshadasawant89@gmail.com',
                                                    password='jam12345'
                                                    )
        self.profile = mommy.make(Profile, user=self.broker_user)
        self.broker = mommy.make(Broker, name=self.broker_user)
        self.supplier_user = User.objects.create_user(username='james2',
                                                    email='harshadasawaent89@gmail.com',
                                                    password='jam12345'
                                                    )
        self.supplier = mommy.make(Supplier, user=self.supplier_user)
        self.supplier_profile = mommy.make(Profile, user=self.supplier.user)
        self.broker_id = self.broker.id
        self.state = mommy.make(State)
        self.city = mommy.make(City)
        self.aaho_office = mommy.make(AahoOffice)
        self.requirement = mommy.make(Requirement, client=self.sme,  aaho_office=self.aaho_office)
        self.requirement_id = self.requirement.id

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqquotescreate_url,
                                    json.dumps({"vehicle_no": "sd458909",'supplier_id':self.supplier.id, "requirement_id": self.requirement_id,
                                                "broker_id": self.broker_id, "rate": 87987}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.reqquote_id = response.data['data']['id']


class ReqQuotesListTests(ReqQuotesTests):

    """
         Test ID:TS02RQ00002
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-list/
         Status:failure
         Message:invalid method header
         Status code:401
    """

    def test_req_quotes_list_401_no_header(self):
        # Negative test case for getting req quotes list with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get(self.reqquoteslist_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS02RQ00003
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-list/
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_req_quotes_list_401_expired_header(self):
        # Negative test case for for getting req quotes list with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        response = self.client.get(self.reqquoteslist_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS02RQ00003
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-list/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_req_quotes_list_401_wrong_token(self):
        # Negative test case for getting req quotes list with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.reqquoteslist_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
             Test ID:TS02RQ00001
             Created By:Hari
             Created On:11/12/2018
             Scenario:req-quotes-list/
             Status:failure
             Message:wrong method
             Status code:405
     """

    def test_req_quotes_list_405_wrong_method(self):
        # Negative test for getting req quotes list with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqquoteslist_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
             Test ID:TS02RQ00004
             Created By:Hari
             Created On:11/12/2018
             Scenario:req-quotes-list/
             Status:failure
             Message:wrong content type
             Status code:415
    """

    def test_req_quotes_list_415_header_with_wrong_content_type(self):
        # Negative test case for getting req quotes list with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.reqquoteslist_url, content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
         Test ID:TS02RQ00005
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-list/
         Status:success
         Message:Requirement Quote List
         Status code:200
    """

    def test_req_quotes_list_200(self):
        # Positive test case for getting req quotes list
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.reqquoteslist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ReqQuotesCreateTests(ReqQuotesTests):

    """
         Test ID:TS02RQ00006
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong content type
         Status code:415
    """

    def test_req_quotes_create_415_header_with_wrong_content_type(self):
        # Negative test case of req quotes create with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqquotescreate_url, json.dumps({'vehicle_no': 'sd458909',
                                                                          'requirement_id': self.requirement_id,
                                                                          'broker_id': self.broker_id,
                                                                          'rate': 4400}), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
         Test ID:TS02RQ00007
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:invalid method header
         Status code:401
    """

    def test_req_quotes_create_401_no_header(self):
        # Negative test case of req quotes create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(self.reqquotescreate_url, {'vehicle_no': 'sd458909',
                                                               'requirement_id': self.requirement_id,
                                                               'broker_id': self.broker_id,
                                                               'rate': 4400})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS02RQ00008
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:expired header
         Status code:401
    """
    def test_req_quotes_create_401_expired_header(self):
        # Negative test case of req quotes create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.reqquotescreate_url, {'vehicle_no': 'sd458909',
                                                               'requirement_id': self.requirement_id,
                                                               'broker_id': self.broker_id,
                                                               'rate': 4400},content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS02RQ00008
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong token
         Status code:401
    """

    def test_req_quotes_create_401_wrong_token(self):
        # Negative test case of req quotes create with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.reqquotescreate_url, {'vehicle_no': 'sd458909',
                                                               'requirement_id': self.requirement_id,
                                                               'broker_id': self.broker_id,
                                                               'rate': 4400},content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
         Test ID:TS02RQ00009
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong vehicle number
         Status code:400
    """
    def test_req_quotes_create_400_wrong_vehicle_no(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and wrong vehicle_no
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqquotescreate_url, json.dumps({'vehicle_no': 58909,
                                                               'requirement_id': self.requirement_id,
                                                               'broker_id': self.broker_id,
                                                               'rate': 4400}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Pattern Does Not Match")

    """
         Test ID:TS02RQ00010
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong requirement
         Status code:400
    """

    def test_req_quotes_create_400_wrong_requirement_id(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and wrong requirement_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqquotescreate_url, json.dumps({'vehicle_no': 'sd458909',
                                                               'requirement_id': 322,
                                                               'broker_id': self.broker_id,
                                                               'rate': 4400}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
         Test ID:TS02RQ00011
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:wrong supplier
         Status code:400
    """

    def test_req_quotes_create_400_wrong_supplier_id(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and wrong broker_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqquotescreate_url, json.dumps({'vehicle_no': 'sd458909',
                                                               'requirement_id': self.requirement_id,
                                                               'broker_id': 'gf8',
                                                               'rate': 4400}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Error")
        self.assertEqual(response.data['msg'], "Inquiry Quote not Created")

    """
         Test ID:TS02RQ00012
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:rate not integer
         Status code:400
    """

    def test_req_quotes_create_400_rate_not_integer(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and rate not integer
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqquotescreate_url, json.dumps({'vehicle_no': 'sd458909',
                                                               'requirement_id': self.requirement_id,
                                                               'broker_id': self.broker_id,
                                                               'rate': '4500dfgdfgdfg'}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Error")
        self.assertEqual(response.data['msg'], "Inquiry Quote not Created")

    """
         Test ID:TS02RQ00013
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:failure
         Message:rate not more than 99999
         Status code:400
    """

    def test_req_quotes_create_400_rate_not_more_than_99999(self):
        # Negative test case of req quotes create with HTTP Header Authorization token and rate not more than 99999
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqquotescreate_url, json.dumps({'vehicle_no': 'sd458909',
                                                               'requirement_id': self.requirement_id,
                                                               'broker_id': self.broker_id,
                                                               'rate': 87987080980}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Error")
        self.assertEqual(response.data['msg'], "Inquiry Quote not Created")

    """
         Test ID:TS02RQ00014
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-create/
         Status:success
         Message:requirement quote created
         Status code:201
    """

    def test_req_quotes_create_201(self):
        # Positive test case of req quotes create with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.reqquotescreate_url,
                                    json.dumps({"vehicle_no": "sd458909", "requirement_id": self.requirement_id,
                                                "broker_id": self.broker_id,"supplier_id": self.supplier.id, "rate": 87987}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "Success")
        self.assertEqual(response.data['msg'], "Inquiry Quote Created")
        self.assertTrue(response.data['data']['id'])

class ReqQuotesDetailTests(ReqQuotesTests):

    """
         Test ID:TS02RQ00015
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-detail/<id>
         Status:failure
         Message:no header
         Status code:401
    """

    def test_req_quotes_detail_401_no_header(self):
        # Negative test case for getting req quotes detail with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/req-quotes-detail/{}/".format(self.reqquote_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
         Test ID:TS02RQ00016
         Created By:Hari
         Created On:11/12/2018
         Scenario:req-quotes-detail/<id>
         Status:failure
         Message:expired header
         Status code:401
    """

    def test_req_quotes_detail_401_expired_header(self):
        # Negative test case for getting req quotes detail with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/req-quotes-detail/{}/".format(self.reqquote_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00016
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-detail/<id>
       Status:failure
       Message:wrong token
       Status code:401
    """

    def test_req_quotes_detail_401_wrong_token(self):
        # Negative test case for getting req quotes detail with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/req-quotes-detail/{}/".format(self.reqquote_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00017
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-detail/<id>
       Status:failure
       Message:wrong method
       Status code:405
    """

    def test_req_quotes_detail_405_wrong_method(self):
        # Negative test for getting req quotes detail with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/req-quotes-detail/{}/".format(self.reqquote_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
       Test ID:TS02RQ00019
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-detail/<id>
       Status:failure
       Message:wrong id
       Status code:404
    """

    def test_req_quotes_detail_404_wrong_id(self):
        # Negative test for getting req quotes detail with wrong id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.reqquote_id = 100
        response = self.client.get("/api/req-quotes-detail/{}/".format(self.reqquote_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
       Test ID:TS02RQ00018
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-detail/<id>
       Status:failure
       Message:wrong content type in header
       Status code:415
    """

    def test_req_quotes_detail_415_header_with_wrong_content_type(self):
        # Negative test case for getting req quotes list with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/req-quotes-detail/{}/".format(self.reqquote_id), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
       Test ID:TS02RQ00020
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-detail/<id>
       Status:success
       Message:req quotes detail display
       Status code:200
    """
    def test_req_quotes_detail_200(self):
        # Positive for getting req quotes detail
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/req-quotes-detail/{}/".format(self.reqquote_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class ReqQuotesUpdateTests(ReqQuotesTests):

    """
       Test ID:TS02RQ00022
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-detail/<id>
       Status:failure
       Message:no header
       Status code:401
    """

    def test_req_quotes_update_401_no_header(self):
        # Negative test for updating req quotes with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post("/api/req-quotes-update/{}/".format(self.reqquote_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
       Test ID:TS02RQ00023
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:expired header
       Status code:401
    """

    def test_req_quotes_update_401_expired_header(self):
        # Negative test case for updating req quotes with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post("/api/req-quotes-update/{}/".format(self.reqquote_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00023
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:success
       Message:wrong token
       Status code:401
    """
    def test_req_quotes_update_401_wrong_token(self):
        # Negative test case for updating req quotes with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post("/api/req-quotes-update/{}/".format(self.reqquote_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00021
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:success
       Message:wrong method
       Status code:405
    """

    def test_req_quotes_update_405_wrong_method(self):
        # Negative test for updating req quotes with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/req-quotes-update/{}/".format(self.reqquote_id), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
       Test ID:TS02RQ00024
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:wrong content type
       Status code:415
    """

    def test_req_quotes_update_415_header_with_wrong_content_type(self):
        # Negative test case for updating req quotes with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/req-quotes-update/{}/".format(self.reqquote_id), content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
       Test ID:TS02RQ00025
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:req quotes detail display
       Status code:400
    """

    def test_req_quotes_update_400_wrong_id(self):
        # Negative test for updating req quotes with wrong id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.reqquote_id = 100
        response = self.client.post("/api/req-quotes-update/{}/".format(self.reqquote_id),json.dumps({'vehicle_no': 'sd458909', 'requirement_id': self.requirement_id,
                                     'broker_id': self.broker_id, 'rate': 4400}),content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Inquiry Quote Doesn't exists")

    """
       Test ID:TS02RQ00026
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:wrong vehicle number
       Status code:400
    """
    def test_req_quotes_update_400_wrong_vehicle_no(self):
        # Negative test case for updating req quotes with HTTP Header Authorization token and wrong vehicle_no
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/req-quotes-update/{}/".format(self.reqquote_id),
                                    json.dumps({'vehicle_no': 58909, 'requirement_id': self.requirement_id,
                                     'broker_id': self.broker_id, 'rate': 4400}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "failure")
        self.assertEqual(response.data['msg'], "Pattern Does Not Match")

    """
       Test ID:TS02RQ00027
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:wrong requirement id
       Status code:400
    """
    def test_req_quotes_update_400_wrong_requirement_id(self):
        # Negative test case for updating req quotes with HTTP Header Authorization token and wrong requirement_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/req-quotes-update/{}/".format(self.reqquote_id),
                                    json.dumps({'vehicle_no': 'sd458909', 'requirement_id': 322, 'broker_id': self.broker_id,
                                     'rate': 4400}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
       Test ID:TS02RQ00028
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:wrong supplier id
       Status code:400
    """

    def test_req_quotes_update_400_wrong_supplier_id(self):
        # Negative test case for updating req quotes with HTTP Header Authorization token and wrong broker_id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/req-quotes-update/{}/".format(self.reqquote_id),
                                    json.dumps({'vehicle_no': 'sd458909', 'requirement_id': self.requirement_id,
                                     'broker_id': 'gf8', 'rate': 4400}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Error")
        self.assertEqual(response.data['msg'], "Inquiry Quote not Updated")

    """
       Test ID:TS02RQ00029
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:rate not an integer
       Status code:200
    """
    def test_req_quotes_update_400_rate_not_integer(self):
        # Negative test case for updating req quotes with HTTP Header Authorization token and rate not integer
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/req-quotes-update/{}/".format(self.reqquote_id),
                                    json.dumps({'vehicle_no': 'sd458909', 'requirement_id': self.requirement_id,
                                    'broker_id': self.broker_id, 'rate': '4500dfgdfgdfg'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Error")
        self.assertEqual(response.data['msg'], "Inquiry Quote not Updated")

    """
       Test ID:TS02RQ00030
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:failure
       Message:rate not more than 99999
       Status code:400
    """
    def test_req_quotes_update_400_rate_not_more_than_99999(self):
        # Negative test case for updating req quotes with HTTP Header Authorization token and rate not more than 99999
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/req-quotes-update/{}/".format(self.reqquote_id),
                                    json.dumps({'vehicle_no': 'sd458909', 'requirement_id': self.requirement_id,
                                     'broker_id': self.broker_id, 'rate': 87987080980}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "Error")
        self.assertEqual(response.data['msg'], "Inquiry Quote not Updated")

    """
       Test ID:TS02RQ00031
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-update/<ID>
       Status:success
       Message:req quotes updated
       Status code:202
    """
    def test_req_quotes_update_202(self):
        # Positive test case for updating req quotes with HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/req-quotes-update/{}/".format(self.reqquote_id),
                                    json.dumps({"vehicle_no": "sd458909", "requirement_id": self.requirement_id,
                                                "broker_id": self.broker_id,"supplier_id": self.supplier.id,  "rate": 9675}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "Success")
        self.assertEqual(response.data['msg'], "Inquiry Quote Updated")

class ReqQuoteDestroyTests(ReqQuotesTests):

    """
       Test ID:TS02RQ00032
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-destroy/<REQ QT ID>/
       Status:failure
       Message:wrong method
       Status code:405
    """

    def test_req_quotes_destroy_405_wrong_method(self):
        # Negative test for destroying req quotes with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/req-quotes-destroy/{}/".format(self.reqquote_id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
       Test ID:TS02RQ00033
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-destroy/<REQ QT ID>/
       Status:failure
       Message:no header
       Status code:401
    """

    def test_req_quotes_destroy_401_no_header(self):
        # Negative test case for destroying req quotes with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/req-quotes-destroy/{}/".format(self.reqquote_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
       Test ID:TS02RQ00034
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-destroy/<REQ QT ID>/
       Status:failure
       Message:expired header
       Status code:401
    """

    def test_req_quotes_destroy_401_expired_header(self):
        # Negative test case for destroying req quotes with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/req-quotes-destroy/{}/".format(self.reqquote_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00034
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-destroy/<REQ QT ID>/
       Status:failure
       Message:wrong token
       Status code:401
    """

    def test_req_quotes_destroy_401_wrong_token(self):
        # Negative test case for destroying req quotes with wrong HTTP Header Authorization token
        token = 'Token 806fa0efd3ce26fe080f65da4ad5a137e1d056ff'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/req-quotes-destroy/{}/".format(self.reqquote_id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
       Test ID:TS02RQ00035
       Created By:Hari
       Created On:11/12/2018
       Scenario:req-quotes-destroy/<REQ QT ID>/
       Status:success
       Message:req quotes destroyed
       Status code:200
    """

    def test_req_quotes_destroy_200(self):
        # Positive for destroying req quotes
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/req-quotes-destroy/{}/".format(self.reqquote_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
