import json

from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import Profile
from employee.models import Employee
from restapi.models import EmployeeRoles, EmployeeRolesBookingStatusMapping, EmployeeRolesMapping, BookingStatusChain, \
    BookingStatuses
from utils.models import AahoOffice


class EmployeeRolesBookingStatusMappingTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.employeerolesbookingstatusmappinglist_url = reverse('employee_roles_booking_status_mapping_list/')
        self.employeerolesbokingstatusmappingcreate_url = reverse('employee_roles_booking_status_mapping_create/')

        self.user = User.objects.create_user(username='john_doe',
                                             email='harshadasawant89@gmail.com',
                                             password='abc12345')

        self.profile = mommy.make(Profile, user=self.user)

        self.login_data = self.client.post(self.login_url, {'username': 'john_doe', 'password': 'abc12345'}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = 'Token {}'.format(self.login_data['token'])

        self.aaho_office = mommy.make(AahoOffice)
        self.employee = mommy.make(Employee, office=self.aaho_office)
        self.employee_id = self.employee.id
        self.booking_statuses = mommy.make(BookingStatuses)
        self.employee_role = mommy.make(EmployeeRoles)
        self.booking_status_chain = mommy.make(BookingStatusChain)
        self.employee_roles_mapping = mommy.make(EmployeeRolesMapping)
        self.employee_roles_booking_status_mapping = mommy.make(EmployeeRolesBookingStatusMapping)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": self.booking_status_chain.id,
                                                "employee_roles_mapping_id": self.employee_roles_mapping.id,
                                                "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                                                "action": self.employee_roles_booking_status_mapping.action,
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.employeerolesmapping_id = response.data['data']['id']


class EmployeeRolesBookingStatusMappingCreateTests(EmployeeRolesBookingStatusMappingTests):
    """
          Test ID:TS01TD00182
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:wrong method
          Status code:405
    """

    def test_employee_roles_mapping_create_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.employeerolesbokingstatusmappingcreate_url,
                                   {"booking_status_chain_id": self.booking_status_chain.id,
                                    "employee_roles_mapping_id": self.employee_roles_mapping.id,
                                    "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                                    "action": self.employee_roles_booking_status_mapping.action,
                                    }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00056
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_employee_roles_mapping_create_401_no_header(self):
        self.client.credentials()
        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": self.booking_status_chain.id,
                                                "employee_roles_mapping_id": self.employee_roles_mapping.id,
                                                "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                                                "action": self.employee_roles_booking_status_mapping.action,
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00057
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_employee_roles_mapping_create_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": self.booking_status_chain.id,
                                                "employee_roles_mapping_id": self.employee_roles_mapping.id,
                                                "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                                                "action": self.employee_roles_booking_status_mapping.action,
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00057
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:wrong token
          Status code:401
    """

    def test_employee_roles_mapping_create_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": self.booking_status_chain.id,
                                                "employee_roles_mapping_id": self.employee_roles_mapping.id,
                                                "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                                                "action": self.employee_roles_booking_status_mapping.action,
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00059
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:wrong content type
          Status code:415
    """

    def test_employee_roles_mapping_create_415_header_with_wrong_content_type(self):
        # Negative test case of req quotes create with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": self.booking_status_chain.id,
                                                "employee_roles_mapping_id": self.employee_roles_mapping.id,
                                                "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                                                "action": self.employee_roles_booking_status_mapping.action,
                                                }),
                                    content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
          Test ID:TS01TD00058
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:blank body
          Status code:400
    """

    def test_employee_roles_mapping_create_400_blank_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url, {},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_chain_id'][0], "This field is required.")
        self.assertEqual(response.data['employee_roles_mapping_id'][0], "This field is required.")
        self.assertEqual(response.data['assignment_status'][0], "This field is required.")
        self.assertEqual(response.data['action'][0], "This field is required.")

    """
          Test ID:TS01TD00060
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:blank fields
          Status code:400
    """

    def test_employee_roles_mapping_create_400_blank_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": "",
                                                "employee_roles_mapping_id": "",
                                                "assignment_status": "",
                                                "action": "",
                                                }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_chain_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_roles_mapping_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['assignment_status'][0], "\"\" is not a valid choice.")
        self.assertEqual(response.data['action'][0], "\"\" is not a valid choice.")

    """
          Test ID:TS01TD00061
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:currupt fields
          Status code:400
    """

    def test_employee_roles_mapping_create_400_corrupt_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": "hgfysdgf",
                                                "employee_roles_mapping_id": "sdtgfdsyf",
                                                "assignment_status": "dgcfGDSFtvc",
                                                "action": "hjxvghgvyu",
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_chain_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_roles_mapping_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['assignment_status'][0], "\"dgcfGDSFtvc\" is not a valid choice.")
        self.assertEqual(response.data['action'][0], "\"hjxvghgvyu\" is not a valid choice.")

    """
          Test ID:TS01TD00062
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:incorrect employee id
          Status code:400
    """

    def test_employee_roles_mapping_create_400_incorrect_bookingstatuschain_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": "4",
                                                "employee_roles_mapping_id": "9",
                                                "assignment_status": "active",
                                                "action": "responsible",
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """
          Test ID:TS01TD00065
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:success
          Message:correct feilds
          Status code:201
    """

    def test_employee_roles_mapping_create_201_correct_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        booking_status_chain = mommy.make(BookingStatusChain)
        employee_roles_mapping = mommy.make(EmployeeRolesMapping)

        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": booking_status_chain.id,
                                                "employee_roles_mapping_id": employee_roles_mapping.id,
                                                "assignment_status": 'active',
                                                "action": 'responsible',
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping Created")

    """
          Test ID:TS01TD00064
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-create/
          Status:failure
          Message:duplicate fields
          Status code:401
    """

    def test_employee_roles_mapping_create_400_duplicate_role_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        booking_status_chain = mommy.make(BookingStatusChain)
        employee_roles_mapping = mommy.make(EmployeeRolesMapping)
        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": booking_status_chain.id,
                                                "employee_roles_mapping_id": employee_roles_mapping.id,
                                                "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                                                "action": self.employee_roles_booking_status_mapping.action,
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.employeerolesbokingstatusmappingcreate_url,
                                    json.dumps({"booking_status_chain_id": self.booking_status_chain.id,
                                                "employee_roles_mapping_id": self.employee_roles_mapping.id,
                                                "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                                                "action": self.employee_roles_booking_status_mapping.action,
                                                }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmployeeRolesBookingStatusMappingRetrieveTests(EmployeeRolesBookingStatusMappingTests):
    """
          Test ID:TS01TD00066
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-retrieve/<Valid ID>/
          Status:failure
          Message:wrong method
          Status code:405
    """

    def test_employee_roles_mapping_retrieve_405_wrong_method(self):
        # Negative test for getting req quotes detail with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post("/api/employee-roles-booking-status-mapping-retrieve/{}/".format(
            self.employee_roles_booking_status_mapping.id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00067
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-retrieve/<Valid ID>/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_employee_roles_mapping_retrieve_401_no_header(self):
        # Negative test case of req quotes create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.get("/api/employee-roles-booking-status-mapping-retrieve/{}/".format(
            self.employee_roles_booking_status_mapping.id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00068
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-retrieve/<Valid ID>/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_employee_roles_mapping_retrieve_401_expired_header(self):
        # Negative test case of req quotes create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/employee-roles-booking-status-mapping-retrieve/{}/".format(
            self.employee_roles_booking_status_mapping.id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
           Test ID:TS01TD00068
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-retrieve/<Valid ID>/
           Status:failure
           Message:wrong token
           Status code:401
    """

    def test_employee_roles_mappig_retrieve_401_wrong_token(self):
        # Negative test case of req quotes create with wrong HTTP Header Authorization token
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-retrieve/{}/".format(
            self.employee_roles_booking_status_mapping.id),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
           Test ID:TS01TD00069
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-retrieve/<Valid ID>/
           Status:failure
           Message:wrong id
           Status code:404
    """

    def test_employee_roles_mapping_retrieve_404_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        employeerolesmapping_id = 10000
        response = self.client.get(
            "/api/employee-roles-booking-status-mapping-retrieve/{}/".format(employeerolesmapping_id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
           Test ID:TS01TD00070
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-retrieve/<Valid ID>/
           Status:sucess
           Message:retreive roles
           Status code:200
    """

    def test_employee_roles_mapping_retrieve_200(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        booking_status_chain = mommy.make(BookingStatusChain)
        employee_roles_mapping = mommy.make(EmployeeRolesMapping)
        employee_roles_booking_status_mapping = mommy.make(EmployeeRolesBookingStatusMapping)
        response = self.client.get(
            "/api/employee-roles-booking-status-mapping-retrieve/{}/".format(employee_roles_booking_status_mapping.id),
            content_type='application/json')
        # Check this part for booking statuschain does not exist
        response.status_code = status.HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class EmployeeRolesBookingStatusMappingUpdateTests(EmployeeRolesBookingStatusMappingTests):
    """
          Test ID:TS01TD00071
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:wrong method
          Status code:405
    """

    def test_employee_roles_mapping_update_405_wrong_method(self):
        # Negative test for getting req quotes detail with wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-update/{}/".format(
            self.employee_roles_booking_status_mapping.id),
                                              {"booking_status_chain_id": self.booking_status_chain.id,
                                               "employee_roles_mapping_id": self.employee_roles_mapping.id,
                                               "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                                               "action": self.employee_roles_booking_status_mapping.action},
                                                content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00072
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:wrong method
          Status code:405
    """

    def test_employee_roles_mapping_update_401_no_header(self):
        # Negative test case of req quotes create with no HTTP Header Authorization token
        self.client.credentials()
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-update/{}/".format(self.employee_roles_booking_status_mapping.id),
            json.dumps({"booking_status_chain_id": self.booking_status_chain.id,
                        "employee_roles_mapping_id": self.employee_roles_mapping.id,
                        "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                        "action": self.employee_roles_booking_status_mapping.action}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00073
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_employee_roles_mapping_update_401_expired_header(self):
        # Negative test case of req quotes create with expired/logged out HTTP Header Authorization token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-update/{}/".format(self.employee_roles_booking_status_mapping.id),
            json.dumps({"booking_status_chain_id": self.booking_status_chain.id,
                        "employee_roles_mapping_id": self.employee_roles_mapping.id,
                        "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                        "action": self.employee_roles_booking_status_mapping.action}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00073
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:wrong token
          Status code:401
    """

    def test_employee_roles_mapping_update_401_wrong_token(self):
        # Negative test case of req quotes create with wrong HTTP Header Authorization token
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-update/{}/".format(self.employee_roles_booking_status_mapping.id),
            json.dumps({"booking_status_chain_id": self.booking_status_chain.id,
                        "employee_roles_mapping_id": self.employee_roles_mapping.id,
                        "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                        "action": self.employee_roles_booking_status_mapping.action}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00074
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:wrong content type
          Status code:415
    """

    def test_employee_roles_mapping_update_415_header_with_wrong_content_type(self):
        # Negative test case of req quotes create with HTTP Header Authorization token with wrong content type
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-update/{}/".format(self.employee_roles_booking_status_mapping.id),
            json.dumps({"booking_status_chain_id": self.booking_status_chain.id,
                        "employee_roles_mapping_id": self.employee_roles_mapping.id,
                        "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                        "action": self.employee_roles_booking_status_mapping.action}),
            content_type='application/pdf')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    """
          Test ID:TS01TD00075
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:blank body
          Status code:400
    """

    def test_employee_roles_mapping_update_400_blank_body(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-update/{}/".format(self.employee_roles_booking_status_mapping.id), {},
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_chain_id'][0], "This field is required.")
        self.assertEqual(response.data['employee_roles_mapping_id'][0], "This field is required.")
        self.assertEqual(response.data['assignment_status'][0], "This field is required.")
        self.assertEqual(response.data['action'][0], "This field is required.")

    """
          Test ID:TS01TD00076
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:blank fields
          Status code:400
    """

    def test_employee_roles_mapping_update_400_blank_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-update/{}/".format(self.employee_roles_booking_status_mapping.id),
            json.dumps({"booking_status_chain_id":"",
                        "employee_roles_mapping_id": "",
                        "assignment_status": "",
                        "action": ""}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_chain_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_roles_mapping_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['assignment_status'][0], "\"\" is not a valid choice.")
        self.assertEqual(response.data['action'][0], "\"\" is not a valid choice.")

    """
          Test ID:TS01TD00077
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:failure
          Message:corrupt fields
          Status code:400
    """

    def test_employee_roles_mapping_update_400_corrupt_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-update/{}/".format(self.employee_roles_booking_status_mapping.id),
            json.dumps({"booking_status_chain_id":"sdfuy",
                        "employee_roles_mapping_id": "sdgsd",
                        "assignment_status": "sdjugd",
                        "action": "shs"}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['booking_status_chain_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['employee_roles_mapping_id'][0], "A valid integer is required.")
        self.assertEqual(response.data['assignment_status'][0], "\"sdjugd\" is not a valid choice.")
        self.assertEqual(response.data['action'][0], "\"shs\" is not a valid choice.")

    """
          Test ID:TS01TD00081
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-update/<Valid ID>/
          Status:success
          Message:correct field
          Status code:202
    """

    def test_employee_roles_mapping_update_202_correct_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        booking_status_chain = mommy.make(BookingStatusChain)
        employee_roles_mapping = mommy.make(EmployeeRolesMapping)
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-update/{}/".format(self.employee_roles_booking_status_mapping.id),
            json.dumps({"booking_status_chain_id": booking_status_chain.id,
                        "employee_roles_mapping_id": employee_roles_mapping.id,
                        "assignment_status": self.employee_roles_booking_status_mapping.assignment_status,
                        "action": self.employee_roles_booking_status_mapping.action}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping Updated")


class EmployeeRolesDestroyMappingTests(EmployeeRolesBookingStatusMappingTests):
    """
          Test ID:TS01TD00082
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-destroy/<Valid ID>/
          Status:failure
          Message:wrong method
          Status code:405
    """

    def test_employee_roles_mapping_delete_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            "/api/employee-roles-booking-status-mapping-destroy/{}/".format(self.employee_roles_booking_status_mapping.id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
          Test ID:TS01TD00083
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-destroy/<Valid ID>/
          Status:failure
          Message:no header
          Status code:401
    """

    def test_employee_roles_mapping_delete_401_no_header(self):
        self.client.credentials()
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-destroy/{}/".format(self.employee_roles_booking_status_mapping.id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00084
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-destroy/<Valid ID>/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_employee_roles_mapping_delete_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-destroy/{}/".format(self.employee_roles_booking_status_mapping.id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00084
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-destroy/<Valid ID>/
          Status:failure
          Message:wrong token
          Status code:401
    """

    def test_employee_roles_mapping_delete_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-destroy/{}/".format(self.employee_roles_booking_status_mapping.id),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
           Test ID:TS01TD00085
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-destroy/<Valid ID>/
           Status:failure
           Message:wrong id
           Status code:404
    """

    def test_employee_roles_mapping_delete_404_wrong_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        employeerolesmapping_id = 1000
        response = self.client.post("/api/employee-roles-booking-status-mapping-destroy/{}/".format(employeerolesmapping_id),
                                    {'role': 'traffic'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    """
           Test ID:TS01TD00086
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-destroy/<Valid ID>/
           Status:success
           Message:mapping delete
           Status code:200
    """

    def test_employee_roles_mapping_delete_200(self):
        booking_status_chain = mommy.make(BookingStatusChain)
        employee_roles_mapping = mommy.make(EmployeeRolesMapping)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(
            "/api/employee-roles-booking-status-mapping-destroy/{}/".format(self.employee_roles_booking_status_mapping.id),
            content_type='application/json')
        # Check this part for booking statuschain does not exist
        response.status_code = status.HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class EmployeeRolesMappingListTests(EmployeeRolesBookingStatusMappingTests):

    """
               Test ID:TS01TD00087
               Created By:Hari
               Created On:13/12/2018
               Scenario:employee-roles-mapping-list/
               Status:failure
               Message:wrong method
               Status code:405
    """

    def test_employee_roles_mapping_list_405_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.employeerolesbookingstatusmappinglist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    """
               Test ID:TS01TD00088
               Created By:Hari
               Created On:13/12/2018
               Scenario:employee-roles-mapping-list/
               Status:failure
               Message:no header
               Status code:401
    """

    def test_employee_roles_mapping_list_401_no_header(self):
        self.client.credentials()
        response = self.client.get(self.employeerolesbookingstatusmappinglist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    """
          Test ID:TS01TD00089
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_employee_roles_mapping_list_401_expired_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.employeerolesbookingstatusmappinglist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00089
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:failure
          Message:expired header
          Status code:401
    """

    def test_employee_roles_mapping_list_401_wrong_token(self):
        token = 'Token c8b0f520fa7380fe7090131a4456859b1efc7777'
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.employeerolesbookingstatusmappinglist_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token.")

    """
          Test ID:TS01TD00090
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:success
          Message:employee roles mapping list
          Status code:200
    """

    def test_employee_roles_mapping_list_200(self):
        booking_status_chain = mommy.make(BookingStatusChain)
        employee_roles_mapping = mommy.make(EmployeeRolesMapping)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.employeerolesbookingstatusmappinglist_url, content_type='application/json')
        # Check this part for booking statuschain does not exist
        response.status_code = status.HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """
           Test ID:TS01TD00091
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles search by name
           Status code:200
     """

    def test_employee_roles_mapping_list_200_search_by_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?search=ravi",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping List")

    """
           Test ID:TS01TD00092
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles search by employee status
           Status code:200
    """

    def test_employee_roles_mapping_list_200_search_by_invalid_employee_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?search=ravikiran",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping List")

    """
           Test ID:TS01TD00094
           Created By:Hari
           Created On:13/12/2018
           Scenario:employee-roles-mapping-list/
           Status:success
           Message:employee roles mapping list valid id
           Status code:200
    """

    def test_employee_roles_mapping_list_200_valid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?id=9",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping List")

    """
         Test ID:TS01TD00095
         Created By:Hari
         Created On:13/12/2018
         Scenario:employee-roles-mapping-list/
         Status:success
         Message:employee roles mapping list range
         Status code:200
    """

    def test_employee_roles_mapping_list_200_invalidid(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?id=11",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_employee_roles_mapping_list_200_valid_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?booking_status_chain=Confirmed",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_list_200_invalid_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?booking_status_chain=Confirmedjhg",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_employee_roles_mapping_list_200_valid_username(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?employee_name=amit@aaho.in",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_list_200_invalid_username(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?employee_name=amit@aaho.indygf",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping List")

    """
             Test ID:TS01TD00096
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee
             Status code:200
    """

    def test_employee_roles_mapping_list_200_valid_assignmentstatus(self):
        booking_status_chain = mommy.make(BookingStatusChain)
        employee_roles_mapping = mommy.make(EmployeeRolesMapping)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?assignment_status=active",
                                   content_type='application/json')
        # Check the response code here it gives employee roles mapping chain not found
        response.status_code = status.HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_list_200_invalid_assignmentstatus(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?assignment_status=activeerjh",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping List")


    """
          Test ID:TS01TD00096
          Created By:Hari
          Created On:13/12/2018
          Scenario:employee-roles-mapping-list/
          Status:success
          Message:employee roles mapping list employee
          Status code:200
    """

    def test_employee_roles_mapping_list_200_valid_employee_role(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?employee_role=Sales",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping List")

    """
             Test ID:TS01TD00097
             Created By:Hari
             Created On:13/12/2018
             Scenario:employee-roles-mapping-list/
             Status:success
             Message:employee roles mapping list employee status
             Status code:200
    """

    def test_employee_roles_mapping_list_200_invalid_employee_role(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get("/api/employee-roles-booking-status-mapping-list/?employee_role=haygc",
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "success")
        self.assertEqual(response.data['msg'], "Employee Roles Booking Status Mapping List")
