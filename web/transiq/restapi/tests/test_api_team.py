import json
import string
import random

from django.contrib.auth.models import User, Group
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import S3Upload
from supplier.models import Driver
from broker.models import Broker
from employee.models import Employee
from owner.models import Vehicle, FuelCard, Owner
from restapi.helper_api import generate_random_string, random_with_N_digits
from restapi.models import BookingStatuses, BookingStatusChain, TaskDashboardFunctionalities
from sme.models import Sme
from supplier.models import Supplier
from team.models import CreditDebitNoteReason, Invoice, ManualBooking, CreditNoteCustomer, DebitNoteCustomer, \
    CreditNoteSupplier, DebitNoteSupplier, CreditNoteCustomerDirectAdvance, DebitNoteSupplierDirectAdvance, \
    InvoiceSummary, LrNumber, OutWardPayment, InWardPayment, RejectedPOD, BookingConsignorConsignee, BookingInsurance, \
    OutWardPaymentBill, ToPayInvoice, PendingInwardPaymentEntry
from utils.models import City, AahoOffice, VehicleCategory, Bank
from datetime import datetime


class TeamSetup(APITestCase):
    """
        Setup dummy data for testing purpose
    """

    create_url = ''
    update_url = ''
    partial_update_url = ''
    retrieve_url = ''

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.group = Group.objects.create(name="emp_group1")
        self.test_user = User.objects.create_user('testUser', 'test@example.com', 'testPassword')
        self.test_user3 = User.objects.create_user(username='admin', email='test@example.com', password='testPassword')
        self.test_user2 = User.objects.create_user('testUser2', 'test2@example.com', 'test2Password')
        self.test_user.groups.add(self.group)
        self.login_data = self.client.post(self.login_url, {"username": "testUser", "password": "testPassword"}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])

        self.employee = mommy.make(Employee, username=self.test_user)
        self.customer = mommy.make(Sme, company_code="XXX")
        self.s3_upload = mommy.make(S3Upload)
        self.source_office = mommy.make(AahoOffice)
        self.destination_office = mommy.make(AahoOffice)
        self.company = mommy.make(Sme, company_code=generate_random_string(N=3))
        self.customer_to_be_billed_to = mommy.make(Sme)
        self.supplier = mommy.make(Supplier, code=generate_random_string(N=4),
                                   user__profile__name=generate_random_string(N=30),
                                   user__profile__phone=random_with_N_digits(n=10))
        self.driver = mommy.make(Driver, user=self.test_user)
        self.owner = mommy.make(Owner)
        self.consignor_city_fk = mommy.make(City, name=generate_random_string(N=12))
        self.consignee_city_fk = mommy.make(City, name=generate_random_string(N=12))
        self.from_city_fk = mommy.make(City, name=generate_random_string(N=12))
        self.to_city_fk = mommy.make(City, name=generate_random_string(N=12))
        self.vehicle = mommy.make(Vehicle, vehicle_number=generate_random_string(N=12))
        self.vehicle_category = mommy.make(VehicleCategory, vehicle_type=generate_random_string(N=20))
        self.city = mommy.make(City, name=generate_random_string(N=20))
        self.bank_account = mommy.make(Bank)
        self.fuel_card = mommy.make(FuelCard)
        self.customer_fk = mommy.make(Sme)

        self.invoice_summary = mommy.make(InvoiceSummary)
        self.booking = mommy.make(ManualBooking, lorry_number=generate_random_string(N=12))
        self.lr_number = mommy.make(LrNumber, _fill_optional=["lr_number"])
        self.rejected_pod = mommy.make(RejectedPOD)
        self.booking_consignor_consignee = mommy.make(BookingConsignorConsignee)
        self.booking_insurance = mommy.make(BookingInsurance)
        self.outward_pmt = mommy.make(OutWardPayment)
        self.inward_payment = mommy.make(InWardPayment)
        self.outward_payment = mommy.make(OutWardPayment)
        self.outward_payment_bill = mommy.make(OutWardPaymentBill)
        self.invoice = mommy.make(Invoice, date='2017-01-05')
        self.broker=mommy.make(Broker)
        self.to_pay_invoice = mommy.make(ToPayInvoice, _fill_optional=['invoice_number'])
        self.pending_inward_payment_entry = mommy.make(PendingInwardPaymentEntry)

        self.reason = mommy.make(CreditDebitNoteReason)
        self.bookings = [
            mommy.make(ManualBooking, source_office=self.source_office, destination_office=self.destination_office).id]
        self.credit_note_customer = mommy.make(CreditNoteCustomer)
        self.debit_note_customer = mommy.make(DebitNoteCustomer)
        self.credit_note_supplier = mommy.make(CreditNoteSupplier)
        self.debit_note_supplier = mommy.make(DebitNoteSupplier)
        self.credit_note_customer_direct_advance = mommy.make(CreditNoteCustomerDirectAdvance)
        self.debit_note_supplier_direct_advance = mommy.make(DebitNoteSupplierDirectAdvance)
        self.booking_statuses = mommy.make(BookingStatuses, status='confirmed')
        self.booking_status_chain = mommy.make(BookingStatusChain, booking_status=self.booking_statuses)
        self.task_dashboard_functionality = mommy.make(TaskDashboardFunctionalities, functionality='pending_lr')


class InvoiceSummaryTest(TeamSetup):
    """
        Test cases for Invoice Summary
    """

    def setUp(self):
        super().setUp()
        self.invoice_summary_data = {
            "ref_number": "ASD43324HF",
            "datetime": "2016-08-28T05:15:19.089051",
            "deleted": False,
            "deleted_on": None,
            "s3_upload": self.s3_upload.id
        }
        self.minimum_valid_data = {
            "ref_number": "ASD43324HF",
            "s3_upload": self.s3_upload.id
        }
        self.create_url = reverse("team_invoice_summary_create")
        self.update_url = reverse("team_invoice_summary_update", kwargs={"pk": self.invoice_summary.id})
        self.partial_update_url = reverse("team_invoice_summary_partial_update", kwargs={"pk": self.invoice_summary.id})
        self.retrieve_url = reverse("team_invoice_summary_retrieve", kwargs={"pk": self.invoice_summary.id})

    def test_create_invoice_summary_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_summary_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding datetime to minimum data
    def test_create_invoice_summary_with_valid_datetime(self):
        data = self.minimum_valid_data.copy()
        data["datetime"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding deleted to minimum data
    def test_create_invoice_summary_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding deleted on to minimum data
    def test_create_invoice_summary_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_summary_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_summary_with_duplicate_s3_url(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.invoice_summary_data.copy()
        data["ref_number"] = self.invoice_summary.ref_number
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_summary_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.invoice_summary_data.copy()
        data["deleted"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.invoice_summary_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.invoice_summary_data.copy()
        data["s3_upload"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["s3_upload"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["s3_upload"] = self.s3_upload.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.invoice_summary_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.invoice_summary_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.invoice_summary_data.copy()
        data["created_by"] = self.test_user.username
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invoice_summary_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_invoice_summary_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.invoice_summary_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_invoice_summary_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = {"s3_upload": self.s3_upload.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_invoice_summary(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_invoice_summary(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_invoice_summary_retrieve",
                                   kwargs={"pk": self.invoice_summary.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ManualBookingTest(TeamSetup):
    """
        Test cases for Manual Booking
    """

    def setUp(self):
        super().setUp()
        self.manual_booking_data = {
            "vehicle_number": "CG04 LU 6781",
            "vehicle_category_id": self.vehicle_category.id,
            "truck_driver_id": self.driver.id,
            "supplier_id": self.supplier.id,
            "supplier_rate": "234",
            "truck_owner_id": self.supplier.id,
            "gst_liability": "consignor",
            "customer_placed_order": self.company.id,
            "customer_to_be_billed": self.customer_to_be_billed_to.id,
            "billing_type": "T.B.B.",
            "source_office": self.source_office.id,
            "destination_office": self.destination_office.id,
            "from_city_fk": self.from_city_fk.id,
            "to_city_fk": self.to_city_fk.id,
            "shipment_datetime": "04-Sep-2018 01:04 AM",
            "charged_weight": "123",
            "party_rate": "322",
            "refundable_amount": "332",
            "supplier_charged_weight": "234",
            "loaded_weight": "433",
            "number_of_lr": "1",
            "total_amount_to_party": "39606",
            "total_amount_to_owner": "54756"
        }
        self.update_manual_booking_data = {
            "booking_id": "AH1907194",
            "company_code": "LRC",
            "consignor_name": "test",
            "consignor_address": None,
            "consignor_city": None,
            "consignor_pin": None,
            "consignor_phone": None,
            "consignor_cst_tin": None,
            "consignor_gstin": None,
            "consignee_name": None,
            "consignee_address": None,
            "consignee_city": None,
            "consignee_pin": None,
            "consignee_phone": None,
            "consignee_cst_tin": None,
            "consignee_gstin": None,
            "billing_type": "T.B.B.",
            "gst_liability": "consignor",
            "liability_of_service_tax": None,
            "shipment_date": "2018-06-19",
            "delivery_datetime": "2018-06-19T17:22:11.540124",
            "from_city": "Turbhe",
            "to_city": "Varanasi",
            "lorry_number": "mh12hd5795",
            "type_of_vehicle": "12 Tyre Taurus, 21/22 tons",
            "road_permit_number": None,
            "party_invoice_number": None,
            "party_invoice_date": None,
            "party_invoice_amount": "0",
            "number_of_package": None,
            "material": None,
            "loaded_weight": "10.000",
            "delivered_weight": "1.000",
            "charged_weight": "1.000",
            "supplier_charged_weight": "1.000",
            "party_rate": 62000,
            "supplier_rate": 55000,
            "is_insured": False,
            "insurance_provider": None,
            "insurance_policy_number": None,
            "insured_amount": "0.00",
            "insurance_date": None,
            "insurance_risk": None,
            "driver_name": "Vijay Kumar Tiwari",
            "driver_phone": "07869120066",
            "driver_dl_number": "MT17R20160189115",
            "driver_dl_validity": None,
            "truck_broker_owner_name": "Swastik Roadlines",
            "truck_broker_owner_phone": "9322599070",
            "truck_owner_name": "Swastik Roadlines",
            "truck_owner_phone": "9322599070",
            "loading_points": None,
            "unloading_points": None,
            "total_in_ward_amount": "0.00",
            "total_out_ward_amount": "0.00",
            "total_amount_to_company": 62000,
            "advance_amount_from_company": 0,
            "refund_amount": 0,
            "total_amount_to_owner": 54900,
            "loading_charge": 0,
            "unloading_charge": 0,
            "detention_charge": 0,
            "additional_charges_for_company": 0,
            "remarks_about_additional_charges": None,
            "additional_charges_for_owner": 0,
            "note_for_additional_owner_charges": None,
            "commission": 0,
            "lr_cost": 0,
            "deduction_for_advance": 100,
            "deduction_for_balance": 0,
            "other_deduction": 0,
            "remarks_about_deduction": None,
            "deductions_for_company": 0,
            "to_be_billed_to": None,
            "invoice_number": None,
            "billing_address": None,
            "billing_contact_number": None,
            "billing_invoice_date": None,
            "invoice_remarks_for_additional_charges": None,
            "invoice_remarks_for_deduction_discount": None,
            "tds_deducted_amount": 0,
            "pod_date": None,
            "pod_status": "pending",
            "outward_payment_status": "no_payment_made",
            "inward_payment_status": "no_payment",
            "invoice_status": "no_invoice",
            "comments": None,
            "remarks_advance_from_company": None,
            "tds_certificate_status": "n",
            "booking_status": "confirmed",
            "is_advance": None,
            "is_print_payment_mode_instruction": False,
            "deleted": False,
            "deleted_on": None,
            "source_office": self.source_office.id,
            "destination_office": self.destination_office.id,
            "company": self.company.id,
            "customer_to_be_billed_to": self.customer_to_be_billed_to.id,
            "owner_supplier": self.supplier.id,
            "driver": self.driver.id,
            "consignor_city_fk": self.consignor_city_fk.id,
            "consignee_city_fk": None,
            "from_city_fk": self.from_city_fk.id,
            "to_city_fk": self.to_city_fk.id,
            "vehicle": self.vehicle.id,
            "vehicle_category": self.vehicle_category.id,
            "invoice_summary": self.invoice_summary.id,
        }

        self.minimum_valid_data = {
            "vehicle_number": "CG04 LU 6781",
            "vehicle_category_id": self.vehicle_category.id,
            "truck_driver_id": self.driver.id,
            "owner_supplier_id": self.supplier.id,
            "supplier_rate": "234",
            "truck_owner_id": self.supplier.id,
            "gst_liability": "consignor",
            "customer_placed_order": self.company.id,
            "customer_to_be_billed": self.customer_to_be_billed_to.id,
            "billing_type": "T.B.B.",
            "source_office": self.source_office.id,
            "destination_office": self.destination_office.id,
            "from_city": self.from_city_fk.id,
            "to_city": self.to_city_fk.id,
            "shipment_datetime": "04-Sep-2018 01:04 AM",
            "charged_weight": "123",
            "party_rate": "322",
            "refundable_amount": "332",
            "supplier_charged_weight": "234",
            "loaded_weight": "433",
            "number_of_lr": "1",
            "total_amount_to_party": "39606",
            "total_amount_to_owner": "54756",
            "driver_phone": "9234534510",
            "driver_name": "9234534510",
        }

        self.create_url = reverse("team_manual_booking_create")
        self.update_url = reverse("team_manual_booking_update", kwargs={"pk": self.booking.id})
        self.partial_update_url = reverse("team_manual_booking_partial_update", kwargs={"pk": self.booking.id})
        self.retrieve_url = reverse("team_manual_booking_retrieve", kwargs={"pk": self.booking.id})
        self.logout_url = reverse('logout')
        self.filter_url = reverse("team_manual_booking_list")

    def test_create_manual_booking_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data.pop('from_city', None)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_company_code(self):
        data = self.minimum_valid_data.copy()

        data["company_code"] = "a1c"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["company_code"] = "@#&"
        data["booking_id"] = "120000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_company_code(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["company_code"] = "a1cd"  # length > 3
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["company_code"] = "@#"  # length < 3
    #     data["booking_id"] = "120000"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["company_code"] = ""
    #     data["booking_id"] = "120001"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["company_code"] = None
    #     data["booking_id"] = "120002"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignor_name(self):
        data = self.minimum_valid_data.copy()

        data["consignor_name"] = "valid_name"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_name"] = generate_random_string(99)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_name"] = generate_random_string(100)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_name"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignor_name(self):
        data = self.minimum_valid_data.copy()

        data["consignor_name"] = generate_random_string(101)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_name"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignor_address(self):
        data = self.minimum_valid_data.copy()

        data["consignor_address"] = "valid_address"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_address"] = generate_random_string(254)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_address"] = generate_random_string(255)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_name"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignor_address(self):
        data = self.minimum_valid_data.copy()

        data["consignor_address"] = generate_random_string(256)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_address"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_manual_booking_with_valid_consignor_city(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["consignor_city"] = "valid_city"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["consignor_city"] = generate_random_string(34)
    #     data["booking_id"] = "12300"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["consignor_city"] = generate_random_string(35)
    #     data["booking_id"] = "12301"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["consignor_city"] = None
    #     data["booking_id"] = "12302"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_consignor_city(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["consignor_city"] = generate_random_string(36)
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["consignor_city"] = ""
    #     data["booking_id"] = "12300"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignor_pin(self):
        data = self.minimum_valid_data.copy()

        data["consignor_pin"] = "224122"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_pin"] = generate_random_string(5)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_pin"] = generate_random_string(6)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_pin"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignor_pin(self):
        data = self.minimum_valid_data.copy()

        data["consignor_pin"] = generate_random_string(7)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_pin"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignor_phone(self):
        data = self.minimum_valid_data.copy()

        data["consignor_phone"] = "123458910"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_phone"] = random_with_N_digits(19)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_phone"] = random_with_N_digits(20)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_phone"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignor_phone(self):
        data = self.minimum_valid_data.copy()

        data["consignor_phone"] = random_with_N_digits(21)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_phone"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignor_gstin(self):
        data = self.minimum_valid_data.copy()

        data["consignor_gstin"] = "12abcde1234a1Zh"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_gstin"] = "12ABCDE1234A1z2"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignor_gstin"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignor_gstin(self):
        data = self.minimum_valid_data.copy()

        data["consignor_gstin"] = generate_random_string(16)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_gstin"] = generate_random_string(14)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_cst_tin"] = ""
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignee_name(self):
        data = self.minimum_valid_data.copy()

        data["consignee_name"] = "valid_name"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_name"] = generate_random_string(99)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_name"] = generate_random_string(100)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_name"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignee_name(self):
        data = self.minimum_valid_data.copy()

        data["consignee_name"] = generate_random_string(101)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_name"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignee_address(self):
        data = self.minimum_valid_data.copy()

        data["consignee_address"] = "valid_address"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_address"] = generate_random_string(399)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_address"] = generate_random_string(400)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_address"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignee_address(self):
        data = self.minimum_valid_data.copy()

        data["consignee_address"] = generate_random_string(401)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_address"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_manual_booking_with_valid_consignee_city(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["consignee_city"] = "valid_city"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["consignee_city"] = generate_random_string(34)
    #     data["booking_id"] = "12300"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["consignee_city"] = generate_random_string(35)
    #     data["booking_id"] = "12301"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["consignee_city"] = None
    #     data["booking_id"] = "12302"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_consignee_pin(self):
        data = self.minimum_valid_data.copy()

        data["consignee_pin"] = "620015"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_pin"] = generate_random_string(5)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_pin"] = generate_random_string(6)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_pin"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignee_pin(self):
        data = self.minimum_valid_data.copy()

        data["consignee_pin"] = generate_random_string(7)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_city"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignee_phone(self):
        data = self.minimum_valid_data.copy()

        data["consignee_phone"] = "123458910"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_phone"] = random_with_N_digits(19)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_phone"] = random_with_N_digits(20)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_phone"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignee_phone(self):
        data = self.minimum_valid_data.copy()

        data["consignee_phone"] = random_with_N_digits(21)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_phone"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignee_cst_tin(self):
        data = self.minimum_valid_data.copy()

        data["consignee_cst_tin"] = "valid_tin"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_cst_tin"] = generate_random_string(49)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_cst_tin"] = generate_random_string(50)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_cst_tin"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignee_cst_tin(self):
        data = self.minimum_valid_data.copy()

        data["consignee_cst_tin"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_cst_tin"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignee_gstin(self):
        data = self.minimum_valid_data.copy()

        data["consignee_gstin"] = "12abcde1234a1Zh"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_gstin"] = "12ABCDE1234A1z2"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["consignee_gstin"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignee_gstin(self):
        data = self.minimum_valid_data.copy()

        data["consignee_gstin"] = generate_random_string(16)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_gstin"] = generate_random_string(14)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_cst_tin"] = ""
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_billing_type(self):
        data = self.minimum_valid_data.copy()

        data["billing_type"] = "T.B.B."
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["billing_type"] = "To Pay"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["billing_type"] = "Paid"
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["billing_type"] = "contract"
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_billing_type(self):
        data = self.minimum_valid_data.copy()

        data["billing_type"] = "invalid_choice"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["billing_type"] = ""
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["billing_type"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["billing_type"] = "ConTract"
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_gst_liability(self):
        data = self.minimum_valid_data.copy()

        data["gst_liability"] = "consignor"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gst_liability"] = "consignee"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gst_liability"] = "carrier"
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gst_liability"] = "exempted"
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_gst_liability(self):
        data = self.minimum_valid_data.copy()

        data["gst_liability"] = "invalid_choice"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gst_liability"] = ""
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # data["gst_liability"] = None
        # data["booking_id"] = "12302"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gst_liability"] = "ExEmpTed"
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_liability_of_service_tax(self):
        data = self.minimum_valid_data.copy()

        data["liability_of_service_tax"] = "valid123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["liability_of_service_tax"] = generate_random_string(39)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["liability_of_service_tax"] = generate_random_string(40)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["liability_of_service_tax"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_liability_of_service_tax(self):
        data = self.minimum_valid_data.copy()

        data["liability_of_service_tax"] = generate_random_string(41)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["liability_of_service_tax"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_shipment_date(self):
        data = self.minimum_valid_data.copy()

        data["shipment_date"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["shipment_date"] = "2018-12-09"
        data["booking_id"] = "12345"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_shipment_date(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["shipment_date"] = "invalid_format"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["shipment_date"] = "18-12-09"
    #     data["booking_id"] = "12345"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["shipment_date"] = "09/12/2018"
    #     data["booking_id"] = "12346"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["shipment_date"] = "12-09-18"
    #     data["booking_id"] = "12347"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_from_city(self):
        data = self.minimum_valid_data.copy()

        data["from_city"] = self.from_city_fk.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_from_city(self):
        data = self.minimum_valid_data.copy()

        data["from_city"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["from_city"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["from_city"] = None
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_to_city(self):
        data = self.minimum_valid_data.copy()

        data["to_city"] = self.to_city_fk.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_to_city(self):
        data = self.minimum_valid_data.copy()

        data["to_city"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["to_city"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["to_city"] = None
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_lorry_number(self):
        data = self.minimum_valid_data.copy()

        data["lorry_number"] = "UP12ABP2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["lorry_number"] = generate_random_string(7)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["lorry_number"] = generate_random_string(10)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["lorry_number"] = generate_random_string(15)
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_lorry_number(self):
        data = self.minimum_valid_data.copy()

        data["lorry_number"] = generate_random_string(6)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["lorry_number"] = generate_random_string(16)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["lorry_number"] = ""
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["lorry_number"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_type_of_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["type_of_vehicle"] = "semi_open"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["type_of_vehicle"] = generate_random_string(69)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["type_of_vehicle"] = generate_random_string(70)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["type_of_vehicle"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_road_permit_number(self):
        data = self.minimum_valid_data.copy()

        data["road_permit_number"] = "semi_open"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["road_permit_number"] = generate_random_string(254)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["road_permit_number"] = generate_random_string(255)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["road_permit_number"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_road_permit_number(self):
        data = self.minimum_valid_data.copy()

        data["road_permit_number"] = generate_random_string(256)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["road_permit_number"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_party_invoice_number(self):
        data = self.minimum_valid_data.copy()

        data["party_invoice_number"] = "INV1234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["party_invoice_number"] = generate_random_string(254)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["party_invoice_number"] = generate_random_string(255)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["party_invoice_number"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_party_invoice_number(self):
        data = self.minimum_valid_data.copy()

        data["party_invoice_number"] = generate_random_string(256)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["party_invoice_number"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_party_invoice_date(self):
        data = self.minimum_valid_data.copy()

        data["party_invoice_date"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["party_invoice_date"] = "2018-12-09"
        data["booking_id"] = "12345"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_party_invoice_date(self):
        data = self.minimum_valid_data.copy()

        data["party_invoice_date"] = "invalid_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["party_invoice_date"] = "18-12-09"
        data["booking_id"] = "12345"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["party_invoice_date"] = "09/12/2018"
        data["booking_id"] = "12346"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["party_invoice_date"] = "12-09-18"
        data["booking_id"] = "12347"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_party_invoice_amount(self):
        data = self.minimum_valid_data.copy()

        data["party_invoice_amount"] = "234523456"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["party_invoice_amount"] = random_with_N_digits(99)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["party_invoice_amount"] = random_with_N_digits(100)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["party_invoice_amount"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_number_of_package(self):
        data = self.minimum_valid_data.copy()

        data["number_of_package"] = "1000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["number_of_package"] = random_with_N_digits(29)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["number_of_package"] = random_with_N_digits(30)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["number_of_package"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_number_of_package(self):
        data = self.minimum_valid_data.copy()

        data["number_of_package"] = random_with_N_digits(31)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["number_of_package"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_material(self):
        data = self.minimum_valid_data.copy()

        data["material"] = "valid_material"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["material"] = generate_random_string(499)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["material"] = generate_random_string(500)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["material"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_material(self):
        data = self.minimum_valid_data.copy()

        data["material"] = generate_random_string(501)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["material"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_loaded_weight(self):
        data = self.minimum_valid_data.copy()

        data["loaded_weight"] = "0.000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["loaded_weight"] = "123456789.123"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["loaded_weight"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["loaded_weight"] = ""
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_loaded_weight(self):
        data = self.minimum_valid_data.copy()

        data["loaded_weight"] = "12.3456"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["loaded_weight"] = "12345678910.123"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_charged_weight(self):
        data = self.minimum_valid_data.copy()

        data["charged_weight"] = "0.000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["charged_weight"] = "10000.123"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["charged_weight"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_charged_weight(self):
        data = self.minimum_valid_data.copy()

        data["charged_weight"] = "12.3456"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["charged_weight"] = "12345678910.123"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_supplier_charged_weight(self):
        data = self.minimum_valid_data.copy()

        data["supplier_charged_weight"] = "0.000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["supplier_charged_weight"] = "10000.123"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["supplier_charged_weight"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_supplier_charged_weight(self):
        data = self.minimum_valid_data.copy()

        data["supplier_charged_weight"] = "12.3456"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_charged_weight"] = "1234567891.123"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_party_rate(self):
        data = self.minimum_valid_data.copy()

        data["party_rate"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["party_rate"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["party_rate"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # data["party_rate"] = None
        # data["booking_id"] = "123402"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_party_rate(self):
        data = self.minimum_valid_data.copy()

        data["party_rate"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["party_rate"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["party_rate"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_supplier_rate(self):
        data = self.minimum_valid_data.copy()

        data["supplier_rate"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["supplier_rate"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["supplier_rate"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # data["supplier_rate"] = None
        # data["booking_id"] = "123402"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_supplier_rate(self):
        data = self.minimum_valid_data.copy()

        data["supplier_rate"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_rate"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_rate"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_is_insured(self):
        data = self.minimum_valid_data.copy()

        data["is_insured"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_insured"] = False
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_insured"] = 0
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_insured"] = 1
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_insurance_provider(self):
        data = self.minimum_valid_data.copy()

        data["insurance_provider"] = "AXIS123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_provider"] = generate_random_string(199)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_provider"] = generate_random_string(200)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_provider"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_insurance_provider(self):
        data = self.minimum_valid_data.copy()

        data["insurance_provider"] = generate_random_string(201)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurance_provider"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_insurance_policy_number(self):
        data = self.minimum_valid_data.copy()

        data["insurance_policy_number"] = "AXIS123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_policy_number"] = generate_random_string(199)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_policy_number"] = generate_random_string(200)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_policy_number"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_insurance_policy_number(self):
        data = self.minimum_valid_data.copy()

        data["insurance_policy_number"] = generate_random_string(201)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurance_policy_number"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_insured_amount(self):
        data = self.minimum_valid_data.copy()

        data["insured_amount"] = "0.00"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insured_amount"] = "123.45"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insured_amount"] = None
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_insured_amount(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["insured_amount"] = 123.456
    #     data["booking_id"] = "12300"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["insured_amount"] = "invalid12"
    #     data["booking_id"] = "12301"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["insured_amount"] = ""
    #     data["booking_id"] = "12302"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_insurance_date(self):
        data = self.minimum_valid_data.copy()

        data["insurance_date"] = "12-Dec-2018"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_date"] = "2018-12-09"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_date"] = None
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_insurance_date(self):
        data = self.minimum_valid_data.copy()

        data["insurance_date"] = "12/12/2018"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurance_date"] = "invalid_date_format"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurance_date"] = "18/12/09"
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurance_date"] = "12/09/18"
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_insurance_risk(self):
        data = self.minimum_valid_data.copy()

        data["insurance_risk"] = "AXIS"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_risk"] = generate_random_string(199)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_risk"] = generate_random_string(200)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["insurance_risk"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_insurance_risk(self):
        data = self.minimum_valid_data.copy()

        data["insurance_risk"] = generate_random_string(201)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["insurance_risk"] = ""
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_driver_name(self):
        data = self.minimum_valid_data.copy()

        data["driver_name"] = "Mahmood_Abbs"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = generate_random_string(254)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_name"] = generate_random_string(255)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_driver_phone(self):
        data = self.minimum_valid_data.copy()

        data["driver_phone"] = "1400201101101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_phone"] = generate_random_string(19)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_phone"] = generate_random_string(20)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_driver_dl_number(self):
        data = self.minimum_valid_data.copy()

        data["driver_dl_number"] = "DL123456"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_dl_number"] = generate_random_string(254)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_dl_number"] = generate_random_string(255)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_dl_number"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_driver_dl_validity(self):
        data = self.minimum_valid_data.copy()

        data["driver_dl_validity"] = "12-Dec-2020"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_dl_validity"] = "2024-12-09"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["driver_dl_validity"] = None
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_truck_broker_owner_name(self):
        data = self.minimum_valid_data.copy()

        data["truck_broker_owner_name"] = "Mrs.X"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_broker_owner_name"] = generate_random_string(99)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_broker_owner_name"] = generate_random_string(100)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_broker_owner_name"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_broker_owner_name"] = ""
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_truck_broker_owner_phone(self):
        data = self.minimum_valid_data.copy()

        data["truck_broker_owner_phone"] = "1234567843456"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_broker_owner_phone"] = generate_random_string(24)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_broker_owner_phone"] = generate_random_string(25)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_broker_owner_phone"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_broker_owner_phone"] = ""
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_truck_owner_name(self):
        data = self.minimum_valid_data.copy()

        data["truck_owner_name"] = "Mrs.X"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_owner_name"] = generate_random_string(99)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_owner_name"] = generate_random_string(100)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_owner_name"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_owner_name"] = ""
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_truck_owner_phone(self):
        data = self.minimum_valid_data.copy()

        data["truck_owner_phone"] = "1234567843"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_owner_phone"] = generate_random_string(24)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_owner_phone"] = generate_random_string(25)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_owner_phone"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["truck_owner_phone"] = ""
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_loading_points(self):
        data = self.minimum_valid_data.copy()

        data["loading_points"] = "1233"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["loading_points"] = generate_random_string(254)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["loading_points"] = generate_random_string(255)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["loading_points"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_loading_points(self):
        data = self.minimum_valid_data.copy()

        data["loading_points"] = generate_random_string(256)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["loading_points"] = ""
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_unloading_points(self):
        data = self.minimum_valid_data.copy()

        data["unloading_points"] = "1233"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["unloading_points"] = generate_random_string(254)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["unloading_points"] = generate_random_string(255)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["unloading_points"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_unloading_points(self):
        data = self.minimum_valid_data.copy()

        data["unloading_points"] = generate_random_string(256)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["unloading_points"] = ""
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_total_in_ward_amount(self):
        data = self.minimum_valid_data.copy()

        data["total_in_ward_amount"] = "0.00"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_in_ward_amount"] = "123.45"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_in_ward_amount"] = None
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_total_in_ward_amount(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["total_in_ward_amount"] = 123.456
    #     data["booking_id"] = "12300"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["total_in_ward_amount"] = "invalid12"
    #     data["booking_id"] = "12301"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["total_in_ward_amount"] = ""
    #     data["booking_id"] = "12302"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_total_out_ward_amount(self):
        data = self.minimum_valid_data.copy()

        data["total_out_ward_amount"] = "0.00"
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_out_ward_amount"] = "123.45"
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_out_ward_amount"] = None
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_total_out_ward_amount(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["total_out_ward_amount"] = 123.456
    #     data["booking_id"] = "12300"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["total_out_ward_amount"] = "invalid12"
    #     data["booking_id"] = "12301"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["total_out_ward_amount"] = ""
    #     data["booking_id"] = "12302"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_total_amount_to_company(self):
        data = self.minimum_valid_data.copy()

        data["total_amount_to_company"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_amount_to_company"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_amount_to_company"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_amount_to_company"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_total_amount_to_company(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["total_amount_to_company"] = -123
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["total_amount_to_company"] = 2147483648
    #     data["booking_id"] = "123400"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["total_amount_to_company"] = "invalid123"
    #     data["booking_id"] = "123401"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_advance_amount_from_company(self):
        data = self.minimum_valid_data.copy()

        data["advance_amount_from_company"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["advance_amount_from_company"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["advance_amount_from_company"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["advance_amount_from_company"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_advance_amount_from_company(self):
        data = self.minimum_valid_data.copy()

        data["advance_from_company"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["advance_from_company"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_refund_amount(self):
        data = self.minimum_valid_data.copy()

        data["refund_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["refund_amount"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["refund_amount"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["refund_amount"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_refund_amount(self):
        data = self.minimum_valid_data.copy()

        data["refundable_amount"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["refundable_amount"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_total_amount_to_owner(self):
        data = self.minimum_valid_data.copy()

        data["total_amount_to_owner"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_amount_to_owner"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_amount_to_owner"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_amount_to_owner"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_total_amount_to_owner(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["total_amount_to_owner"] = -123
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["total_amount_to_owner"] = 2147483648
    #     data["booking_id"] = "123400"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["total_amount_to_owner"] = "invalid123"
    #     data["booking_id"] = "123401"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_loading_charge(self):
        data = self.minimum_valid_data.copy()

        data["loading_charge"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["loading_charge"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["loading_charge"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["loading_charge"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_loading_charge(self):
        data = self.minimum_valid_data.copy()

        data["loading_charge"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["loading_charge"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["loading_charge"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_unloading_charge(self):
        data = self.minimum_valid_data.copy()

        data["unloading_charge"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["unloading_charge"] = 100000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["unloading_charge"] = 100000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["unloading_charge"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_unloading_charge(self):
        data = self.minimum_valid_data.copy()

        data["unloading_charge"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["unloading_charge"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["unloading_charge"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_detention_charge(self):
        data = self.minimum_valid_data.copy()

        data["detention_charge"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["detention_charge"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["detention_charge"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["detention_charge"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_detention_charge(self):
        data = self.minimum_valid_data.copy()

        data["detention_charge"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["detention_charge"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["detention_charge"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_additional_charges_for_company(self):
        data = self.minimum_valid_data.copy()

        data["additional_charges_for_company"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["additional_charges_for_company"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["additional_charges_for_company"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["additional_charges_for_company"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_additional_charges_for_company(self):
        data = self.minimum_valid_data.copy()

        data["additional_charges_for_company"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["additional_charges_for_company"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["additional_charges_for_company"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_remarks_about_additional_charges(self):
        data = self.minimum_valid_data.copy()

        data["remarks_about_additional_charges"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["remarks_about_additional_charges"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["remarks_about_additional_charges"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["remarks_about_additional_charges"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_additional_charges_for_owner(self):
        data = self.minimum_valid_data.copy()

        data["additional_charges_for_owner"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["additional_charges_for_owner"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["additional_charges_for_owner"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["additional_charges_for_owner"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_additional_charges_for_owner(self):
        data = self.minimum_valid_data.copy()

        data["additional_charges_for_owner"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["additional_charges_for_owner"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["additional_charges_for_owner"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_commission(self):
        data = self.minimum_valid_data.copy()

        data["commission"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["commission"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["commission"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["commission"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_commission(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["commission"] = -123
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["commission"] = 2147483648
    #     data["booking_id"] = "123400"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["commission"] = "invalid123"
    #     data["booking_id"] = "123401"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_lr_cost(self):
        data = self.minimum_valid_data.copy()

        data["lr_cost"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["lr_cost"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["lr_cost"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["lr_cost"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_deduction_for_advance(self):
        data = self.minimum_valid_data.copy()

        data["deduction_for_advance"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deduction_for_advance"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deduction_for_advance"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deduction_for_advance"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_deduction_for_balance(self):
        data = self.minimum_valid_data.copy()

        data["deduction_for_balance"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deduction_for_balance"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deduction_for_balance"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deduction_for_balance"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_deduction_for_balance(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["deduction_for_balance"] = -123
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["deduction_for_balance"] = 2147483648
    #     data["booking_id"] = "123400"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["deduction_for_balance"] = "invalid123"
    #     data["booking_id"] = "123401"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_other_deduction(self):
        data = self.minimum_valid_data.copy()

        data["other_deduction"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["other_deduction"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["other_deduction"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["other_deduction"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_other_deduction(self):
        data = self.minimum_valid_data.copy()

        data["other_deduction"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["other_deduction"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["other_deduction"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_deductions_for_company(self):
        data = self.minimum_valid_data.copy()

        data["deductions_for_company"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deductions_for_company"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deductions_for_company"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_deductions_for_company(self):
        data = self.minimum_valid_data.copy()

        data["deductions_for_company"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deductions_for_company"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deductions_for_company"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_uto_be_billed_to(self):
        data = self.minimum_valid_data.copy()

        data["to_be_billed_to"] = "valid_details"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["to_be_billed_to"] = generate_random_string(199)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["to_be_billed_to"] = generate_random_string(200)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["to_be_billed_to"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_to_be_billed_to(self):
        data = self.minimum_valid_data.copy()

        data["to_be_billed_to"] = generate_random_string(201)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["to_be_billed_to"] = ""
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_invoice_number(self):
        data = self.minimum_valid_data.copy()

        data["invoice_number"] = "INV123456"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_number"] = generate_random_string(49)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_number"] = generate_random_string(50)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_number"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_invoice_number(self):
        data = self.minimum_valid_data.copy()

        data["invoice_number"] = generate_random_string(51)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice_number"] = ""
        data["booking_id"] = "12303"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_billing_address(self):
        data = self.minimum_valid_data.copy()

        data["billing_address"] = "INV123456"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["billing_address"] = generate_random_string(299)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["billing_address"] = generate_random_string(300)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["billing_address"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_billing_address(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["billing_address"] = generate_random_string(301)
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["billing_address"] = ""
    #     data["booking_id"] = "12303"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_billing_contact_number(self):
        data = self.minimum_valid_data.copy()

        data["billing_contact_number"] = "1213456"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["billing_contact_number"] = generate_random_string(49)
        data["booking_id"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["billing_contact_number"] = generate_random_string(50)
        data["booking_id"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["billing_contact_number"] = None
        data["booking_id"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_billing_contact_number(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["billing_contact_number"] = generate_random_string(51)
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["billing_contact_number"] = ""
    #     data["booking_id"] = "12303"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_tds_deducted_amount(self):
        data = self.minimum_valid_data.copy()

        data["tds_deducted_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["tds_deducted_amount"] = 1000000
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["tds_deducted_amount"] = 1000000
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # data["tds_deducted_amount"] = None
        # data["booking_id"] = "123402"
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_tds_deducted_amount(self):
        data = self.minimum_valid_data.copy()

        data["tds_deducted_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["tds_deducted_amount"] = 2147483648
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["tds_deducted_amount"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_billing_invoice_date(self):
        data = self.minimum_valid_data.copy()

        data["billing_invoice_date"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["billing_invoice_date"] = "2018-12-09"
        data["booking_id"] = "1234556"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_billing_invoice_date(self):
        data = self.minimum_valid_data.copy()

        data["billing_invoice_date"] = "12/Dec/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["billing_invoice_date"] = "18-12-09"
        data["booking_id"] = "1234556"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["billing_invoice_date"] = "12-18-09"
        data["booking_id"] = "1234557"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["billing_invoice_date"] = "09-12-18"
        data["booking_id"] = "1234558"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_pod_date(self):
        data = self.minimum_valid_data.copy()

        data["pod_date"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pod_date"] = "2018-12-09"
        data["booking_id"] = "1234556"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_pod_date(self):
        data = self.minimum_valid_data.copy()

        data["pod_date"] = "12/Dec/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pod_date"] = "18-12-09"
        data["booking_id"] = "1234556"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pod_date"] = "12-18-09"
        data["booking_id"] = "1234557"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pod_date"] = "09-12-18"
        data["booking_id"] = "1234558"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_pod_status(self):
        data = self.minimum_valid_data.copy()

        data["pod_status"] = "pending"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pod_status"] = "unverified"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pod_status"] = "rejected"
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pod_status"] = "completed"
        data["booking_id"] = "123403"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pod_status"] = None
        data["booking_id"] = "123404"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_pod_status(self):
        data = self.minimum_valid_data.copy()

        data["pod_status"] = "PenDing"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pod_status"] = "invalid"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_outward_payment_status(self):
        data = self.minimum_valid_data.copy()

        data["outward_payment_status"] = "no_payment_made"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["outward_payment_status"] = "partial"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["outward_payment_status"] = "complete"
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["outward_payment_status"] = "excess"
        data["booking_id"] = "123403"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["outward_payment_status"] = None
        data["booking_id"] = "123404"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_outward_payment_status(self):
        data = self.minimum_valid_data.copy()

        data["outward_payment_status"] = "ExCess"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["outward_payment_status"] = "invalid"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_inward_payment_status(self):
        data = self.minimum_valid_data.copy()

        data["inward_payment_status"] = "no_payment"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["inward_payment_status"] = "partial_received"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["inward_payment_status"] = "full_received"
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["inward_payment_status"] = "excess"
        data["booking_id"] = "123403"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["inward_payment_status"] = None
        data["booking_id"] = "123404"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_inward_payment_status(self):
        data = self.minimum_valid_data.copy()

        data["inward_payment_status"] = "ExCess"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["inward_payment_status"] = "invalid"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_invoice_status(self):
        data = self.minimum_valid_data.copy()

        data["invoice_status"] = "no_invoice"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_status"] = "invoice_raised"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_status"] = "invoice_sent"
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_status"] = "invoice_confirmed"
        data["booking_id"] = "123403"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_status"] = None
        data["booking_id"] = "123404"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_invoice_status(self):
        data = self.minimum_valid_data.copy()

        data["invoice_status"] = "Invoice_Confirmed"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice_status"] = "invalid"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_tds_certificate_status(self):
        data = self.minimum_valid_data.copy()

        data["tds_certificate_status"] = "y"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["tds_certificate_status"] = "n"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["tds_certificate_status"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_tds_certificate_status(self):
        data = self.minimum_valid_data.copy()

        data["tds_certificate_status"] = "Yes"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["tds_certificate_status"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_is_advance(self):
        data = self.minimum_valid_data.copy()

        data["is_advance"] = "no"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_advance"] = "yes"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_advance"] = None
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_is_advance(self):
        data = self.minimum_valid_data.copy()

        data["is_print_payment_mode_instruction"] = "YeS"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["is_print_payment_mode_instruction"] = "invalid123"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_booking_status(self):
        data = self.minimum_valid_data.copy()

        data["booking_status"] = "confirmed"
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["booking_status"] = "delivered"
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["booking_status"] = "closed"
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["booking_status"] = "cancelled"
        data["booking_id"] = "123403"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["booking_status"] = None
        data["booking_id"] = "123404"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_manual_booking_with_invalid_booking_status(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["booking_status"] = "Confijrmed"
    #     data["booking_id"] = "123400"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["booking_status"] = "invalid"
    #     data["booking_id"] = "123401"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_manual_booking_with_valid_is_print_payment_mode_instruction(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["is_print_payment_mode_instruction"] = True
    #     data["booking_id"] = "123400"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["is_print_payment_mode_instruction"] = False
    #     data["booking_id"] = "123401"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["is_print_payment_mode_instruction"] = 0
    #     data["booking_id"] = "123402"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["is_print_payment_mode_instruction"] = 1
    #     data["booking_id"] = "123403"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["booking_id"] = "123402"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["booking_id"] = "123403"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_created_on(self):
        data = self.minimum_valid_data.copy()

        data["created_on"] = datetime.now()
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["created_on"] = str(datetime.now())
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        data["booking_id"] = "123400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        data["booking_id"] = "123401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_source_office(self):
        data = self.minimum_valid_data.copy()

        data["source_office"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["source_office"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["source_office"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["source_office"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["source_office"] = "invalid"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["source_office"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["source_office"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_destination_office(self):
        data = self.minimum_valid_data.copy()

        data["destination_office"] = self.destination_office.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_destination_office(self):
        data = self.minimum_valid_data.copy()

        data["destination_office"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["destination_office"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["source_office"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["destination_office"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["destination_office"] = "invalid123"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["destination_office"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["destination_office"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_company(self):
        data = self.minimum_valid_data.copy()

        data["customer_placed_order"] = self.company.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_company(self):
        data = self.minimum_valid_data.copy()

        data["customer_placed_order"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_placed_order"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_placed_order"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_placed_order"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_placed_order"] = "invalid123"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_placed_order"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_placed_order"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_customer_to_be_billed_to(self):
        data = self.minimum_valid_data.copy()

        data["customer_to_be_billed_to"] = self.customer_to_be_billed_to.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_customer_to_be_billed_to(self):
        data = self.minimum_valid_data.copy()

        data["customer_to_be_billed"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_to_be_billed"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_to_be_billed"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_to_be_billed"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_to_be_billed"] = "invalid123"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_to_be_billed"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_to_be_billed"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_supplier(self):
        data = self.minimum_valid_data.copy()

        data["supplier"] = self.supplier.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_supplier(self):
        data = self.minimum_valid_data.copy()

        data["supplier_id"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_id"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_id"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_id"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_id"] = "invalid123"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_id"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["supplier_id"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_owner(self):
        data = self.minimum_valid_data.copy()

        data["owner"] = self.owner.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_driver(self):
        data = self.minimum_valid_data.copy()

        data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_driver(self):
        data = self.minimum_valid_data.copy()

        data["truck_driver_id"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_driver_id"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_driver_id"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_driver_id"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_driver_id"] = "invalid123"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_driver_id"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["truck_driver_id"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignor_city_fk(self):
        data = self.minimum_valid_data.copy()

        data["consignor_city"] = self.consignor_city_fk.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignor_city_fk(self):
        data = self.minimum_valid_data.copy()

        data["consignor_city"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_city"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_city"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_city"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_city"] = "invalid123"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_city"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignor_city"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_consignee_city_fk(self):
        data = self.minimum_valid_data.copy()

        data["consignee_city_fk"] = self.consignee_city_fk.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_consignee_city_fk(self):
        data = self.minimum_valid_data.copy()

        data["consignee_city"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_city"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_city"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_city"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_city"] = "invalid123"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_city"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["consignee_city"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_invalid_from_city_fk(self):
        data = self.minimum_valid_data.copy()

        data["from_city"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["from_city"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["from_city"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["from_city"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["from_city"] = "invalid123"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["from_city"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["from_city"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_to_city_fk(self):
        data = self.minimum_valid_data.copy()

        data["to_city_fk"] = self.to_city_fk.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_to_city_fk(self):
        data = self.minimum_valid_data.copy()

        data["to_city"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["to_city"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["to_city"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["to_city"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["to_city"] = "invalid123"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["to_city"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["to_city"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_vehicle(self):
        data = self.minimum_valid_data.copy()

        data["vehicle"] = self.vehicle.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_valid_vehicle_category(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_category"] = self.vehicle_category.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_vehicle_category(self):
        data = self.minimum_valid_data.copy()

        data["vehicle_category_id"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_category_id"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_category_id"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_category_id"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_category_id"] = "invalid123"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_category_id"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["vehicle_category_id"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_valid_invoice_summary(self):
        data = self.minimum_valid_data.copy()

        data["invoice_summary"] = self.invoice_summary.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_invoice_summary(self):
        data = self.minimum_valid_data.copy()

        data["invoice_summary"] = -123
        data["booking_id"] = "10100"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice_summary"] = 0
        data["booking_id"] = "10101"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice_summary"] = 12.2345
        data["booking_id"] = "10102"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice_summary"] = 1234523
        data["booking_id"] = "10103"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice_summary"] = "invalid123"
        data["booking_id"] = "10104"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice_summary"] = datetime.now()
        data["booking_id"] = "10105"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice_summary"] = str(datetime.now())
        data["booking_id"] = "10106"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_manual_booking_with_invalid_lorry_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.manual_booking_data.copy()
        data["vehicle_number"] = "mh12asdd5795"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["lorry_number"] = "mh122sdd5795"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["lorry_number"] = "12sdd5795"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_booking_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()

        data["destination_office"] = self.destination_office.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.manual_booking_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.manual_booking_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.update_manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.update_manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.update_manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.update_manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.update_manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.update_manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.manual_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.manual_booking_data.copy()
        data["created_by"] = self.test_user.username
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_manual_booking_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"vehicle_category": self.vehicle_category.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_manual_booking(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_manual_booking(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_manual_booking_retrieve",
                                   kwargs={"pk": self.booking.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_manual_booking_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.booking.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.booking.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manual_booking_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manual_booking_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manual_booking_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ManualBookingListTest(APITestCase):

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.test_user = User.objects.create_user('testUser', 'test@example.com', 'testPassword')
        self.login_data = self.client.post(self.login_url, {"username": "testUser", "password": "testPassword"}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.list_url = reverse('team_manual_booking_list')
        self.partialbooking_url = reverse('partial_booking_list_page')
        self.fullbooking_url = reverse('full_booking_list_page')
        self.aaho_office = mommy.make(AahoOffice, branch_name='RAIPUR')
        self.broker = mommy.make(Broker, name=self.test_user, aaho_office=self.aaho_office)
        self.broker_name = self.broker.name
        self.token = "Token {}".format(self.login_data["token"])
        self.vehicle_category = mommy.make(VehicleCategory, vehicle_type="luxury")
        self.vehtype = self.vehicle_category.vehicle_type
        self.vehicle = mommy.make(Vehicle, vehicle_type=self.vehicle_category)
        self.vehicleid = self.vehicle.id

    def test_manual_booking_list_expired_token(self):
        # Negative Test Case for expired token
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manual_booking_list_wrong_method(self):
        # Negative Test Case for wrong method
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.list_url, format=json)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_manual_booking_list_wrong_token(self):
        # Negative Test Case for wrong HTTP Authorisation token
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manual_booking_list_no_header(self):
        # Negative Test Case for no header
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_manual_booking_list_get_fmsuser_bookings(self):
        # Get the booking list for a given fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get(self.list_url, format=json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_list_get_vehicle_wise_boking(self):
        # Get the vehicle wise booking for a fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get("/api/team-manual-booking-list/?vehicle_type=luxury/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_list_get_partial_booking(self):
        # Get the vehicle wise booking for a fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get(self.partialbooking_url, format=json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_list_get_full_booking(self):
        # Get the vehicle wise booking for a fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get(self.fullbooking_url, format=json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_list_get_loaded_booking(self):
        # Get the vehicle wise booking for a fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get("/api/team-manual-booking-list/?booking_data_category=loaded_bookings/", format=json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_list_get_advnotpaid_booking(self):
        # Get the vehicle wise booking for a fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get("/api/team-manual-booking-list/?booking_data_category=advance_not_paid/",
                                   format=json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_list_get_paybalance_booking(self):
        # Get the vehicle wise booking for a fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get("/api/team-manual-booking-list/?booking_data_category=pay_balance/", format=json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_list_get_intransit_booking(self):
        # Get the vehicle wise booking for a fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get("/api/team-manual-booking-list/?booking_data_category=in_transit/", format=json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_list_get_delivered_booking(self):
        # Get the vehicle wise booking for a fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get("/api/team-manual-booking-list/?booking_data_category=delivered/", format=json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_list_get_confirminvoice_booking(self):
        # Get the vehicle wise booking for a fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get("/api/team-manual-booking-list/?booking_data_category=invoice_confirmation/",
                                   format=json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_list_get_raiseinvoice_booking(self):
        # Get the vehicle wise booking for a fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get("/api/team-manual-booking-list/?booking_data_category=raise_invoice/", format=json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_booking_list_get_incompletelr_booking(self):
        # Get the vehicle wise booking for a fms user
        self.client.credentials(HTTP_AUTHORIZATION=self.token, HTTP_APP_CATEGORY="fms")
        response = self.client.get("/api/team-manual-booking-list/?booking_data_category=incomplete_lr/", format=json)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LrNumberTest(TeamSetup):
    """
        Test cases for Lr Number
    """

    def setUp(self):
        super().setUp()
        self.lr_number_data = {
            "lr_number": "HTR171208005",
            "datetime": "2017-12-08T13:12:00",
            "pod_status": "pending",
            "deleted": False,
            "deleted_on": None,
            "booking": self.booking.id,
            "source_office": self.source_office.id
        }
        self.minimum_valid_data = {
            "lr_number": "HTR171208005",
            "datetime": "2017-12-08T13:12:00"
        }
        self.create_url = reverse("team_lr_number_create")
        self.update_url = reverse("team_lr_number_update", kwargs={"pk": self.lr_number.id})
        self.partial_update_url = reverse("team_lr_number_partial_update", kwargs={"pk": self.lr_number.id})
        self.retrieve_url = reverse("team_lr_number_retrieve", kwargs={"pk": self.lr_number.id})

    def test_create_lr_number_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_lr_number_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding pod_status field in minimum data
    def test_create_lr_number_with_valid_pod_status(self):
        data = self.minimum_valid_data.copy()
        data["pod_status"] = "pending"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding booking field in minimum data
    def test_create_lr_number_with_valid_booking(self):
        data = self.minimum_valid_data.copy()
        data["booking"] = self.booking.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding deleted field in minimum data
    def test_create_lr_number_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding deleted on field in minimum data
    def test_create_lr_number_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lr_number_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lr_number_with_duplicate_lr_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.lr_number_data.copy()
        data["lr_number"] = self.lr_number.lr_number
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_lr_number_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.lr_number_data.copy()
        data["deleted"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.lr_number_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.lr_number_data.copy()
        data["source_office"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["source_office"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["source_office"] = self.source_office.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.lr_number_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.lr_number_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.lr_number_data.copy()
        data["created_by"] = self.test_user.username
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_lr_number_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_lr_number_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.lr_number_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_lr_number_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = {"booking": self.booking.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_lr_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_lr_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_lr_number_retrieve",
                                   kwargs={"pk": self.lr_number.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RejectedPODTest(TeamSetup):
    """
        Test cases for Rejected POD
    """

    def setUp(self):
        super().setUp()
        self.rejected_pod_data = {
            "remarks": "There is no sign of stamp on this pod?",
            "deleted": False,
            "deleted_on": None,
            "booking": self.booking.id,
            "lr": self.lr_number.id

        }
        self.minimum_valid_data = {
            "lr": self.lr_number.id,
            "remarks": "There is no sign of stamp on this pod?",
            "booking": self.booking.id
        }
        self.create_url = reverse("team_rejected_pod_create")
        # self.update_url = reverse("team_rejected_pod_update", kwargs={"pk": self.rejected_pod.id})
        # self.partial_update_url = reverse("team_rejected_pod_partial_update", kwargs={"pk": self.rejected_pod.id})
        self.retrieve_url = reverse("team_rejected_pod_retrieve", kwargs={"pk": self.rejected_pod.id})

    def test_create_rejected_pod_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejected_pod_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_rejected_pod_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.rejected_pod_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_rejected_pod_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.rejected_pod_data.copy()
        data["deleted"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.rejected_pod_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.rejected_pod_data.copy()
        data["booking"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking"] = self.booking.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.rejected_pod_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # response = self.client.put(self.update_url, self.rejected_pod_data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        #
        # response = self.client.patch(self.partial_update_url, self.rejected_pod_data,
        #                              format='json')
        # self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.rejected_pod_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # response = self.client.put(self.update_url, self.rejected_pod_data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        #
        # response = self.client.patch(self.partial_update_url, self.rejected_pod_data,
        #                              format='json')
        # self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.rejected_pod_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.rejected_pod_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.rejected_pod_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # def test_update_function_with_invalid_request(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.update_url, self.rejected_pod_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #
    #     response = self.client.patch(self.update_url, self.rejected_pod_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #
    #     response = self.client.get(self.update_url, self.rejected_pod_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #
    # def test_partial_update_function_with_invalid_request(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.put(self.partial_update_url, self.rejected_pod_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #
    #     response = self.client.post(self.partial_update_url, self.rejected_pod_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #
    #     response = self.client.get(self.partial_update_url, self.rejected_pod_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.rejected_pod_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.rejected_pod_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.rejected_pod_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    # def test_try_to_change_immutable_fields(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     data = self.rejected_pod_data.copy()
    #     data["created_by"] = self.test_user.username
    #     response = self.client.patch(self.partial_update_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_update_rejected_pod_with_minimum_valid_date(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
    #
    # def test_update_rejected_pod_with_full_valid_data(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.put(self.update_url, self.rejected_pod_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
    #
    # def test_partial_update_rejected_pod_with_valid_data(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #
    #     data = {"booking": self.booking.id}
    #     response = self.client.patch(self.partial_update_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_rejected_pod(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_rejected_pod(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_rejected_pod_retrieve",
                                   kwargs={"pk": self.rejected_pod.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookingConsignorConsigneeTest(TeamSetup):
    """
        Test cases for Booking Consignor Consignee
    """

    def setUp(self):
        super().setUp()
        self.booking_consignor_consignee_data = {
            "category": "hokage",
            "name": "the second wind",
            "address": "village hidden in the rain",
            "pin": None,
            "phone": None,
            "cst_tin": None,
            "gstin": None,
            "deleted": False,
            "deleted_on": None,
            "booking": self.booking.id,
            "lr": self.lr_number.id,
            "city": self.city.id
        }
        self.minimum_valid_data = {}
        self.create_url = reverse("team_booking_consignor_consignee_create")
        self.update_url = reverse("team_booking_consignor_consignee_update",
                                  kwargs={"pk": self.booking_consignor_consignee.id})
        self.partial_update_url = reverse("team_booking_consignor_consignee_partial_update",
                                          kwargs={"pk": self.booking_consignor_consignee.id})
        self.retrieve_url = reverse("team_booking_consignor_consignee_retrieve",
                                    kwargs={"pk": self.booking_consignor_consignee.id})

    def test_create_booking_consignor_consignee_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_booking_consignor_consignee_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding lr field to minimum valid data

    def test_create_booking_consignor_consignee_with_lr(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.booking_consignor_consignee_data.copy()
        data["booking_consignor_consignee"] = self.booking_consignor_consignee.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_booking_consignor_consignee_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.booking_consignor_consignee_data.copy()
        data["deleted"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.booking_consignor_consignee_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.booking_consignor_consignee_data.copy()
        data["booking"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking"] = self.booking.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.booking_consignor_consignee_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.booking_consignor_consignee_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.booking_consignor_consignee_data.copy()
        data["created_by"] = self.test_user.username
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_booking_consignor_consignee_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_booking_consignor_consignee_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.booking_consignor_consignee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_booking_consignor_consignee_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = {"booking": self.booking.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_booking_consignor_consignee(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_booking_consignor_consignee(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_booking_consignor_consignee_retrieve",
                                   kwargs={"pk": self.booking_consignor_consignee.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookingInsuranceTest(TeamSetup):
    """
        Test cases for Booking Insurance
    """

    def setUp(self):
        super().setUp()
        self.booking_insurance_data = {
            "is_insured": False,
            "insurance_provider": None,
            "insurance_policy_number": "23423",
            "insured_amount": "0.00",
            "insurance_date": "2012-03-23",
            "insurance_risk": None,
            "deleted": False,
            "deleted_on": None
        }
        self.minimum_valid_data = {

        }
        self.create_url = reverse("team_booking_insurance_create")
        self.update_url = reverse("team_booking_insurance_update",
                                  kwargs={"pk": self.booking_insurance.id})
        self.partial_update_url = reverse("team_booking_insurance_partial_update",
                                          kwargs={"pk": self.booking_insurance.id})
        self.retrieve_url = reverse("team_booking_insurance_retrieve",
                                    kwargs={"pk": self.booking_insurance.id})

    def test_create_booking_insurance_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_booking_insurance_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding insured_amount field to minimum valid data
    def test_create_booking_insurance_with_insured_amount(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.booking_insurance_data.copy()
        data["insured_amount"] = "231"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding insurance_policy_number field to minimum valid data
    def test_create_booking_insurance_with_insured_insurance_policy_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.booking_insurance_data.copy()
        data["insurance_policy_number"] = 12345
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding deleted field to minimum valid data
    def test_create_booking_insurance_with_deleted(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.booking_insurance_data.copy()
        data["deleted"] = True
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_booking_insurance_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.booking_insurance_data.copy()
        data["deleted"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.booking_insurance_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.booking_insurance_data.copy()
        data["insurance_policy_number"] = "a" * 201
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.booking_insurance_data.copy()
        data["insured_amount"] = "123.23344"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.booking_insurance_data.copy()
        data["insurance_date"] = "26/12/2018"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.booking_insurance_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.booking_insurance_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.booking_insurance_data.copy()
        data["created_by"] = self.test_user.username
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_booking_insurance_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_booking_insurance_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.booking_insurance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_booking_insurance_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = {"deleted": True}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_booking_insurance(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_booking_insurance(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_booking_insurance_retrieve",
                                   kwargs={"pk": self.booking_insurance.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class InWardPaymentTest(TeamSetup):
    """
        Test cases for InWard Payment
    """

    def setUp(self):
        super().setUp()
        self.inward_payment_data = {
            "received_from": "Kirti Roadlines",
            "tds": "0.00",
            "actual_amount": "39000.00",
            "expected_amount": "39000.00",
            "payment_mode": "cash",
            "trn": None,
            "remarks": "100 deducted for Tapal.",
            "payment_date": "2016-08-24",
            "invoice_number": "B1002",
            "deleted": False,
            "deleted_on": None,
            "booking_id": self.bookings
        }
        self.minimum_valid_data = {
            "actual_amount": "39000.00",
            "tds": "0.00",
            "booking_id": self.bookings,
            "payment_mode": "cash",
            "received_from": "Kirti Roadlines",
            "invoice_number": "B1002",
            "payment_date": "2016-08-24"
        }
        self.create_url = reverse("team_inward_payment_create")
        self.update_url = reverse("team_inward_payment_update",
                                  kwargs={"pk": self.inward_payment.id})
        self.partial_update_url = reverse("team_inward_payment_partial_update",
                                          kwargs={"pk": self.inward_payment.id})
        self.retrieve_url = reverse("team_inward_payment_retrieve",
                                    kwargs={"pk": self.inward_payment.id})
        self.filter_url = reverse("team_inward_payment_list")
        self.invoice_url = reverse('team_invoice_summary_list')

    def test_create_inward_payment_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inward_payment_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_inward_payment_with_other_data_format(self):
        pass

    def test_create_inward_payment_with_valid_received_from(self):
        data = self.minimum_valid_data.copy()

        data["received_from"] = "some_valid_info"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["received_from"] = "s" * 299
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["received_from"] = "s" * 300
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_inward_payment_with_invalid_received_from(self):
        data = self.minimum_valid_data.copy()

        data["received_from"] = "s" * 301
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["received_from"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["received_from"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inward_payment_with_valid_tds(self):
        data = self.minimum_valid_data.copy()

        data["tds"] = 0.00
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["tds"] = 123.34
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["tds"] = -300.34
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_inward_payment_with_invalid_tds(self):
        data = self.minimum_valid_data.copy()

        data["tds"] = "invalid_tds"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["tds"] = 123.345
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["tds"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["tds"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inward_payment_with_valid_actual_amount(self):
        data = self.minimum_valid_data.copy()

        data["actual_amount"] = 0.00
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["actual_amount"] = 123.34
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["actual_amount"] = -300.34
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_inward_payment_with_invalid_actual_amount(self):
        data = self.minimum_valid_data.copy()

        data["actual_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["actual_amount"] = 123.345
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["actual_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["actual_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inward_payment_with_valid_expected_amount(self):
        data = self.minimum_valid_data.copy()

        data["expected_amount"] = 0.00
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["expected_amount"] = 123.34
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["expected_amount"] = -300.34
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["expected_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_inward_payment_with_invalid_expected_amount(self):
        data = self.minimum_valid_data.copy()

        data["expected_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expected_amount"] = 123.345
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expected_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inward_payment_with_valid_payment_mode(self):
        data = self.minimum_valid_data.copy()

        data["payment_mode"] = "cash"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "cheque"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "neft"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "imps"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "rtgs"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "happay"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "cash_deposit"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "hdfc_internal_account"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_inward_payment_with_invalid_payment_mode(self):
        data = self.minimum_valid_data.copy()

        data["payment_mode"] = "invalid_mode"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["payment_mode"] = "ChEque"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["payment_mode"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inward_payment_with_valid_trn(self):
        data = self.minimum_valid_data.copy()

        data["trn"] = "valid_trn"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["trn"] = "v" * 199
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["trn"] = "v" * 200
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["trn"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_inward_payment_with_invalid_trn(self):
        data = self.minimum_valid_data.copy()

        data["trn"] = "v" * 201
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["trn"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inward_payment_with_valid_remarks(self):
        data = self.minimum_valid_data.copy()

        data["remarks"] = "some_valid_remark."
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["remarks"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["remarks"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_inward_payment_with_valid_payment_date(self):
        data = self.minimum_valid_data.copy()

        data["payment_date"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_date"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_date"] = "2018-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_inward_payment_with_invalid_payment_date(self):
        data = self.minimum_valid_data.copy()

        data["payment_date"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["payment_date"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["payment_date"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inward_payment_with_valid_invoice_number(self):
        data = self.minimum_valid_data.copy()

        data["invoice_number"] = "valid_number12334"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_number"] = "v" * 299
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_number"] = "v" * 300
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_number"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_inward_payment_with_invalid_invoice_number(self):
        data = self.minimum_valid_data.copy()

        data["invoice_number"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice_number"] = "v" * 301
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inward_payment_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_inward_payment_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -12
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inward_payment_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_inward_payment_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09/12/18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "12-09-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inward_payment_with_valid_booking_id(self):
        data = self.minimum_valid_data.copy()

        data["booking_id"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_inward_payment_with_invalid_booking_id(self):
        data = self.minimum_valid_data.copy()

        data["booking_id"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking_id"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking_id"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking_id"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking_id"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inward_payment_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_inward_payment_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.inward_payment_data.copy()
        data["deleted"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.inward_payment_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.inward_payment_data.copy()
        data["payment_mode"] = "invalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.inward_payment_data.copy()
        data["booking_id"] = [-1]
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking_id"] = ["invalidId"]
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking_id"] = [self.booking.id * 100]
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.inward_payment_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.inward_payment_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.inward_payment_data.copy()
        data["created_by"] = self.test_user.username
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_inward_payment_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_inward_payment_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.inward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_inward_payment_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = {"booking_id": self.bookings}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_inward_payment(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_inward_payment(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_inward_payment_retrieve",
                                   kwargs={"pk": self.inward_payment.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_inward_payment_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.inward_payment.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inward_payment_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.inward_payment.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inward_payment_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inward_payment_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inward_payment_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inward_payment_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_invoice_summary_url(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.invoice_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OutWardPaymentTest(TeamSetup):
    """
        Test cases for OutWard Payment
    """

    def setUp(self):
        super().setUp()
        self.outward_payment_data = {
            "paid_to": "Cuttack Golden Trailer Service",
            "lorry_number": "CG07 CA 7448",
            "actual_amount": "0.00",
            "expected_amount": "0.00",
            'outward_payment_mode': 'cash',
            'payment_mode': 'cash',
            "remarks": "Enet transfer",
            "payment_date": "2016-08-12",
            "invoice_number": "Advance",
            "status": "paid",
            "is_sms_supplier": False,
            "is_refund_amount": False,
            "deleted": False,
            "deleted_on": None,
            "bank_account": self.bank_account.id,
            "fuel_card": self.fuel_card.id,
            "booking_id": self.bookings
        }
        self.minimum_valid_data = {
            "paid_to": "Cuttack Golden Trailer Service",
            'outward_payment_mode': 'cash',
            'payment_mode': 'cash',
            'booking_id': self.bookings,
            'actual_amount': '1.5',
            'payment_date': datetime.now().date()
        }
        self.create_url = reverse("team_outward_payment_create")
        self.update_url = reverse("team_outward_payment_update",
                                  kwargs={"pk": self.outward_payment.id})
        self.partial_update_url = reverse("team_outward_payment_partial_update",
                                          kwargs={"pk": self.outward_payment.id})
        self.retrieve_url = reverse("team_outward_payment_retrieve",
                                    kwargs={"pk": self.outward_payment.id})
        self.filter_url = reverse("team_outward_payment_list")
        self.bill_url = reverse('team_outward_payment_bill_list')
        self.lr_list_url = reverse('team_lr_number_list')

    def test_create_outward_payment_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_other_data_format(self):
        pass

    def test_create_outward_payment_with_valid_paid_to(self):
        data = self.minimum_valid_data.copy()

        data["paid_to"] = "some valid details123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["paid_to"] = "s" * 299
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["paid_to"] = "s" * 300
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_invalid_paid_to(self):
        data = self.minimum_valid_data.copy()

        data["paid_to"] = "s" * 301
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["paid_to"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["paid_to"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_utr(self):
        data = self.minimum_valid_data.copy()

        data["utr"] = "tryu" * 4
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["utr"] = "v" * 29
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["utr"] = "v" * 30
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["utr"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_invalid_utr(self):
        data = self.minimum_valid_data.copy()

        data["utr"] = 'try' * 5
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["utr"] = "v" * 31
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["utr"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_actual_amount(self):
        data = self.minimum_valid_data.copy()

        data["actual_amount"] = "0.00"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["actual_amount"] = "123333.23"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_invalid_actual_amount(self):
        data = self.minimum_valid_data.copy()

        data["actual_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["actual_amount"] = "1233.123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["actual_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["actual_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_tds(self):
        data = self.minimum_valid_data.copy()

        data["tds"] = "0.00"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["tds"] = "123333.23"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["tds"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_invalid_tds(self):
        data = self.minimum_valid_data.copy()

        data["tds"] = "invalid_tds"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["tds"] = "123333.234"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["tds"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_expected_amount(self):
        data = self.minimum_valid_data.copy()

        data["expected_amount"] = "0.00"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["expected_amount"] = "123333.23"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["expected_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_invalid_expected_amount(self):
        data = self.minimum_valid_data.copy()

        data["expected_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expected_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["expected_amount"] = "1233.123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_payment_mode(self):
        data = self.minimum_valid_data.copy()

        data["payment_mode"] = "cash"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "cheque"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "neft"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "imps"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "rtgs"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "happay"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "fuel_card"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "hdfc_internal_account"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_mode"] = "adjustment"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_outward_payment_with_invalid_payment_mode(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["payment_mode"] = "invlaid_mode"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["payment_mode"] = "ChEque"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["payment_mode"] = ""
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["payment_mode"] = None
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_remarks(self):
        data = self.minimum_valid_data.copy()

        data["remarks"] = "some_valid_remarks"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["remarks"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_invalid_remarks(self):
        data = self.minimum_valid_data.copy()

        data["remarks"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_payment_date(self):
        data = self.minimum_valid_data.copy()

        data["payment_date"] = "2018-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_date"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # data["payment_date"] = datetime.now()
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #
        # data["payment_date"] = str(datetime.now())
        # self.client.credentials(HTTP_AUTHORIZATION=self.token)
        # response = self.client.post(self.create_url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_invalid_payment_date(self):
        data = self.minimum_valid_data.copy()

        data["payment_date"] = "12/Dec/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["payment_date"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["payment_date"] = "09/12/18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["payment_date"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_status(self):
        data = self.minimum_valid_data.copy()

        data["status"] = "paid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = "unpaid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = "reconciled"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["status"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_outward_payment_with_invalid_status(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["status"] = "invalid_status"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["status"] = "UnPaid"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["status"] = datetime.now()
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["status"] = str(datetime.now())
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_is_sms_supplier(self):
        data = self.minimum_valid_data.copy()

        data["is_sms_supplier"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_sms_supplier"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_sms_supplier"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_sms_supplier"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_outward_payment_with_invalid_is_sms_supplier(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["is_sms_supplier"] = "invalid"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["is_sms_supplier"] = None
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_is_refund_amount(self):
        data = self.minimum_valid_data.copy()

        data["is_refund_amount"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_refund_amount"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_refund_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["is_refund_amount"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_outward_payment_with_invalid_is_refund_amount(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["is_refund_amount"] = "invalid"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["is_refund_amount"] = None
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = "2018-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_invalid_deleted_on(self):
        data = self.minimum_valid_data.copy()

        data["deleted_on"] = "12/Dec/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18/12/09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "invalid_date_format"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_bank_account(self):
        data = self.minimum_valid_data.copy()

        data["bank_account"] = self.bank_account.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["bank_account"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_invalid_bank_account(self):
        data = self.minimum_valid_data.copy()

        data["bank_account"] = "invalid_account_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bank_account"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bank_account"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bank_account"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bank_account"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_fuel_card(self):
        data = self.minimum_valid_data.copy()

        data["fuel_card"] = self.fuel_card.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["fuel_card"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_invalid_fuel_card(self):
        data = self.minimum_valid_data.copy()

        data["fuel_card"] = "invalid_account_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fuel_card"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fuel_card"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fuel_card"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["fuel_card"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_with_valid_booking_id(self):
        data = self.minimum_valid_data.copy()

        data["booking_id"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_outward_payment_with_invalid_booking_id(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["booking_id"] = ["invalid_account_id"]
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["booking_id"] = -123
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["booking_id"] = 0
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["booking_id"] = datetime.now()
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["booking_id"] = str(datetime.now())
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Adding field booking_id to minimum valid data
    def test_create_outward_payment_with_booking_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["booking_id"] = self.bookings
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.outward_payment_data.copy()
        data["paid_to"] = None
        data["actual_amount"] = None
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.outward_payment_data.copy()
        data["actual_amount"] = None
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.outward_payment_data.copy()
        data["paid_to"] = None
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.outward_payment_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.outward_payment_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.outward_payment_data.copy()
        data["created_by"] = self.test_user.username
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_outward_payment_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_outward_payment_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.outward_payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_outward_payment_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = {"booking_id": self.bookings}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_outward_payment(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_outward_payment(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_outward_payment_retrieve",
                                   kwargs={"pk": self.outward_payment.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_outward_payment_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.outward_payment.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outward_payment_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.outward_payment.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outward_payment_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outward_payment_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outward_payment_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outward_payment_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_outward_payment_bill_url(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.bill_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lr_list_url(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.lr_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OutWardPaymentBillTest(TeamSetup):
    """
        Test cases for OutWard Payment Bill
    """

    def setUp(self):
        super().setUp()
        self.outward_payment_bill_data = {
            "bill_number": "10086",
            "bill_date": "2017-04-02",
            "amount": 32600,
            "vehicle_number": "CG07 BA 5297",
            "lr_number": "SBV170323004",
            "from_city": "VISAKHAPATNAM",
            "to_city": "KORBA",
            "loading_date": "2017-03-23",
            "weight": "26.000",
            "paid_to": None,
            "pan_number": None,
            "deleted": False,
            "deleted_on": None,
            "outward_pmt": [self.outward_pmt.id],
            "booking": self.booking.id
        }
        self.minimum_valid_data = {
            "outward_pmt": [self.outward_pmt.id],
            "bill_number": "10086",
            "bill_date": "2017-04-02",
            "amount": 32600
        }
        self.create_url = reverse("team_outward_payment_bill_create")
        self.update_url = reverse("team_outward_payment_bill_update",
                                  kwargs={"pk": self.outward_payment_bill.id})
        self.partial_update_url = reverse("team_outward_payment_bill_partial_update",
                                          kwargs={"pk": self.outward_payment_bill.id})
        self.retrieve_url = reverse("team_outward_payment_bill_retrieve",
                                    kwargs={"pk": self.outward_payment_bill.id})
        self.filter_url = reverse("team_outward_payment_bill_list")

    def test_create_outward_payment_bill_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_bill_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding amount field to minimum data
    def test_create_outward_payment_bill_with_valid_amount(self):
        data = self.minimum_valid_data.copy()
        data["amount"] = 12000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding vehicle number field to minimum data
    def test_create_outward_payment_bill_with_valid_vehicle_number(self):
        data = self.minimum_valid_data.copy()
        data["vehicle_number"] = "AP21EK2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding deleted field to minimum data
    def test_create_outward_payment_bill_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding deleted on field to minimum data
    def test_create_outward_payment_bill_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_bill_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_outward_payment_bill_with_duplicate_bill_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["bill_number"] = self.outward_payment_bill.bill_number
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_outward_payment_bill_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.outward_payment_bill_data.copy()
        data["deleted"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.outward_payment_bill_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.outward_payment_bill_data.copy()
        data["amount"] = "invalidAmount"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.outward_payment_bill_data.copy()
        data["booking"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["booking"] = self.booking.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.outward_payment_bill_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.outward_payment_bill_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.outward_payment_bill_data.copy()
        data["created_by"] = self.test_user.username
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_outward_payment_bill_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_outward_payment_bill_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.outward_payment_bill_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_outward_payment_bill_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = {"booking": self.booking.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_outward_payment_bill(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_outward_payment_bill(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_outward_payment_bill_retrieve",
                                   kwargs={"pk": self.outward_payment_bill.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_outward_payment_bill_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.outward_payment_bill.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outward_payment_bill_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.outward_payment_bill.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outward_payment_bil_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outward_payment_bill_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outward_payment_bill_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outward_payment_bill_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class InvoiceTest(TeamSetup):
    """
        Test cases for Invoice
    """

    def setUp(self):
        super().setUp()
        self.invoice_data = {
            "invoice_number": "TB-CPC1072",
            "date": "2017-01-05",
            "company_name": "Canpac Trends Pvt. Ltd.",
            "payment_received": True,
            "address": "Plot no. 338, Chiyada Village, B/h Kerala GIDC, Bavla",
            "pin": None,
            "gstin": None,
            "total_amount": 99000,
            "advance_payment": 0,
            "remarks": "[]",
            "service_tax_paid_by": "consignor",
            "service_tax_aaho": 12,
            "deleted": False,
            "deleted_on": None,
            "summary_required": False,
            "customer_fk": self.customer_fk.id,
            "city": self.city.id,
            "s3_upload": self.s3_upload.id,
            "bookings": self.bookings
        }
        self.minimum_valid_data = {
            "city": self.city.id,
            "invoice_number": "TB-CPC1072",
            "company_name": "Canpac Trends Pvt. Ltd.",
            "address": "Plot no. 338, Chiyada Village, B/h Kerala GIDC, Bavla",
            "customer_fk": self.customer_fk.id,
            "date": "2017-01-05",
            "total_amount": 99000,
            "service_tax_paid_by": "consignor",
            "gstin": None,
            "s3_upload": self.s3_upload.id,
            "pin": None,
            "service_tax_aaho": 21

        }
        self.create_url = reverse("team_invoice_create")
        self.update_url = reverse("team_invoice_update",
                                  kwargs={"pk": self.invoice.id})
        self.partial_update_url = reverse("team_invoice_partial_update",
                                          kwargs={"pk": self.invoice.id})
        self.retrieve_url = reverse("team_invoice_retrieve",
                                    kwargs={"pk": self.invoice.id})
        self.filter_url = reverse("team_invoice_list")

    def test_create_invoice_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_other_data_format(self):
        pass

    def test_create_invoice_with_valid_invoice_number(self):
        data = self.minimum_valid_data.copy()

        data["invoice_number"] = "INvoice-123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_number"] = "a" * 29
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice_number"] = "b" * 30
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_invoice_number(self):
        data = self.minimum_valid_data.copy()

        data["invoice_number"] = "a" * 31
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice_number"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice_number"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_date(self):
        data = self.minimum_valid_data.copy()

        data["date"] = "12-Dec-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["date"] = "2018-12-09"
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_date(self):
        data = self.minimum_valid_data.copy()

        data["date"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["date"] = "18-12-09"
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["date"] = "12-09-18"
        data["invoice_number"] = "12001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["date"] = "09/12/2018"
        data["invoice_number"] = "12002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["date"] = ""
        data["invoice_number"] = "12003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["date"] = None
        data["invoice_number"] = "12004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_company_name(self):
        data = self.minimum_valid_data.copy()

        data["company_name"] = "some valid company"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["company_name"] = "s" * 254
        data["invoice_number"] = "13000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["company_name"] = "s" * 255
        data["invoice_number"] = "13001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_company_name(self):
        data = self.minimum_valid_data.copy()

        data["company_name"] = "a" * 256
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["company_name"] = ""
        data["invoice_number"] = "14000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["company_name"] = None
        data["invoice_number"] = "13001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_payment_received(self):
        data = self.minimum_valid_data.copy()

        data["payment_received"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_received"] = True
        data["invoice_number"] = "122000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_received"] = 0
        data["invoice_number"] = "122001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["payment_received"] = 1
        data["invoice_number"] = "122002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_payment_received(self):
        data = self.minimum_valid_data.copy()

        data["payment_received"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["payment_received"] = -1
        data["invoice_number"] = "122000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["payment_received"] = ""
        data["invoice_number"] = "122001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["payment_received"] = None
        data["invoice_number"] = "122002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = "some_valid_address:Delta123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = "s" * 499
        data["invoice_number"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = "s" * 500
        data["invoice_number"] = "12301"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["address"] = None
        data["invoice_number"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_address(self):
        data = self.minimum_valid_data.copy()

        data["address"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["address"] = "s" * 501
        data["invoice_number"] = "13300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_pin(self):
        data = self.minimum_valid_data.copy()

        data["pin"] = "pin123"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pin"] = "12345"
        data["invoice_number"] = "12300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["pin"] = None
        data["invoice_number"] = "12302"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_pin(self):
        data = self.minimum_valid_data.copy()

        data["pin"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["pin"] = "invalid123"
        data["invoice_number"] = "13300"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_gstin(self):
        data = self.minimum_valid_data.copy()

        data["gstin"] = "12abcde1234a1Zh"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gstin"] = "12ABCDE1234A1z2"
        data["invoice_number"] = "3400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["gstin"] = None
        data["invoice_number"] = "3401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_gstin(self):
        data = self.minimum_valid_data.copy()

        data["gstin"] = "12abcde1234a1Zh1"  # length > 15
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = "12ABCDE1234A1z"  # lenght < 15
        data["invoice_number"] = "3400"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["gstin"] = ""
        data["invoice_number"] = "3401"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_total_amount(self):
        data = self.minimum_valid_data.copy()

        data["total_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_amount"] = 1000000
        data["invoice_number"] = "100000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["total_amount"] = 1000000
        data["invoice_number"] = "100001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_total_amount(self):
        data = self.minimum_valid_data.copy()

        data["total_amount"] = -1234
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["total_amount"] = 2147483648
        data["invoice_number"] = "100000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["total_amount"] = "ivalid"
        data["invoice_number"] = "100001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["total_amount"] = ""
        data["invoice_number"] = "100002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["total_amount"] = None
        data["invoice_number"] = "100002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_advance_payment(self):
        data = self.minimum_valid_data.copy()

        data["advance_payment"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["advance_payment"] = 1000000
        data["invoice_number"] = "100000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["advance_payment"] = 1000000
        data["invoice_number"] = "100001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_advance_payment(self):
        data = self.minimum_valid_data.copy()

        data["advance_payment"] = -1234
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["advance_payment"] = 2147483648
        data["invoice_number"] = "100000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["advance_payment"] = "nvalid"
        data["invoice_number"] = "100001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["advance_payment"] = ""
        data["invoice_number"] = "100002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["advance_payment"] = None
        data["invoice_number"] = "100002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_remarks(self):
        data = self.minimum_valid_data.copy()

        data["remarks"] = "some_valid_remarks"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["remarks"] = "s" * 499
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["remarks"] = "s" * 500
        data["invoice_number"] = "12001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["remarks"] = None
        data["invoice_number"] = "12002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_remarks(self):
        data = self.minimum_valid_data.copy()

        data["remarks"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["remarks"] = "s" * 501
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_service_tax_paid_by(self):
        data = self.minimum_valid_data.copy()

        data["service_tax_paid_by"] = "some_valid_data"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["service_tax_paid_by"] = "s" * 254
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["service_tax_paid_by"] = "s" * 255
        data["invoice_number"] = "12001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["service_tax_paid_by"] = None
        data["invoice_number"] = "12002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_service_tax_paid_by(self):
        data = self.minimum_valid_data.copy()

        data["service_tax_paid_by"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["service_tax_paid_by"] = "s" * 256
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_service_tax_aaho(self):
        data = self.minimum_valid_data.copy()

        data["service_tax_aaho"] = 0.00
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["service_tax_aaho"] = 12.34
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_service_tax_aaho(self):
        data = self.minimum_valid_data.copy()

        data["service_tax_aaho"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["service_tax_aaho"] = 123.345
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["service_tax_aaho"] = None
        data["invoice_number"] = "12002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["service_tax_aaho"] = "invalid"
        data["invoice_number"] = "12003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = False
        data["invoice_number"] = "123000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 0
        data["invoice_number"] = "123001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted"] = 1
        data["invoice_number"] = "123002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_deleted(self):
        data = self.minimum_valid_data.copy()

        data["deleted"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = ""
        data["invoice_number"] = "123000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = None
        data["invoice_number"] = "123001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted"] = -1
        data["invoice_number"] = "123002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_summary_required(self):
        data = self.minimum_valid_data.copy()

        data["summary_required"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["summary_required"] = False
        data["invoice_number"] = "123000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["summary_required"] = 0
        data["invoice_number"] = "123001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["summary_required"] = 1
        data["invoice_number"] = "123002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_summary_required(self):
        data = self.minimum_valid_data.copy()

        data["summary_required"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["summary_required"] = ""
        data["invoice_number"] = "123000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["summary_required"] = None
        data["invoice_number"] = "123001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["summary_required"] = -1
        data["invoice_number"] = "123002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_customer_fk(self):
        data = self.minimum_valid_data.copy()

        data["customer_fk"] = self.customer_fk.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_customer_fk(self):
        data = self.minimum_valid_data.copy()

        data["customer_fk"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_fk"] = "invalid"
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_fk"] = -123
        data["invoice_number"] = "12001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_fk"] = 0
        data["invoice_number"] = "12002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_fk"] = 12.34
        data["invoice_number"] = "12003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_fk"] = datetime.now()
        data["invoice_number"] = "12004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_fk"] = str(datetime.now())
        data["invoice_number"] = "12005"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_fk"] = ""
        data["invoice_number"] = "12006"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_fk"] = None
        data["invoice_number"] = "12007"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_city(self):
        data = self.minimum_valid_data.copy()

        data["city"] = self.city.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["city"] = None
        data["invoice_number"] = "12007"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["city"] = ""
        data["invoice_number"] = "12008"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_city(self):
        data = self.minimum_valid_data.copy()

        data["city"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = 2345678
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = -123
        data["invoice_number"] = "12001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = 0
        data["invoice_number"] = "12002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = 12.34
        data["invoice_number"] = "12003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = datetime.now()
        data["invoice_number"] = "12004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["city"] = str(datetime.now())
        data["invoice_number"] = "12005"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_s3_upload(self):
        data = self.minimum_valid_data.copy()

        data["s3_upload"] = self.s3_upload.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["s3_upload"] = None
        data["invoice_number"] = "12007"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["s3_upload"] = ""
        data["invoice_number"] = "12008"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_s3_upload(self):
        data = self.minimum_valid_data.copy()

        data["s3_upload"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["s3_upload"] = 12345678
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["s3_upload"] = -123
        data["invoice_number"] = "12001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["s3_upload"] = 0
        data["invoice_number"] = "12002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["s3_upload"] = 12.34
        data["invoice_number"] = "12003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["s3_upload"] = datetime.now()
        data["invoice_number"] = "12004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["s3_upload"] = str(datetime.now())
        data["invoice_number"] = "12005"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_valid_bookings(self):
        data = self.minimum_valid_data.copy()

        data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_invalid_bookings(self):
        data = self.minimum_valid_data.copy()

        data["bookings"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 12345678
        data["invoice_number"] = "12000"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -123
        data["invoice_number"] = "12001"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 0
        data["invoice_number"] = "12002"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 12.34
        data["invoice_number"] = "12003"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = datetime.now()
        data["invoice_number"] = "12004"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = str(datetime.now())
        data["invoice_number"] = "12005"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = None
        data["invoice_number"] = "12007"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = ""
        data["invoice_number"] = "12008"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_with_duplicate_invoice_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["invoice_number"] = self.invoice.invoice_number
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.invoice_data.copy()
        data["deleted"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.invoice_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.invoice_data.copy()
        data["total_amount"] = "invalidAmount"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.invoice_data.copy()
        data["s3_upload"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["s3_upload"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["s3_upload"] = self.s3_upload.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.invoice_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.invoice_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.invoice_data.copy()
        data["created_by"] = self.test_user.username
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invoice_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_invoice_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_invoice_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = {"bookings": self.bookings}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_invoice(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_invoice(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_invoice_retrieve",
                                   kwargs={"pk": self.invoice.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_invoice_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.invoice.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoice_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.invoice.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoice_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoice_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoice_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoice_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ToPayInvoiceTest(TeamSetup):
    """
        Test cases for To Pay Invoice
    """

    def setUp(self):
        super().setUp()
        self.to_pay_invoice_data = {
            "invoice_gen_office": None,
            "invoice_number": "TP-MTX1079",
            "date": "2017-01-13",
            "company_name": "MORTEX INDIA",
            "payment_received": True,
            "company_address": "1A,EAST INDIA HOUSE,20 BRITISH INDIAN STREET",
            "pin": None,
            "gstin": None,
            "source": "RAIPUR",
            "destination": "VISHAKHAPATNAM",
            "vehicle_number": "AP35 W 0621",
            "lr_number": "MTX170107006\nMTX170107005",
            "quantity": "21.000",
            "rate": "1550",
            "total_payable_freight": "32550",
            "amount_payable_to_transiq": "31070",
            "balance_payable_to_lorry_driver": "1480",
            "advance_payment": 0,
            "remarks": "[]",
            "service_tax_paid_by": "consignee",
            "service_tax_aaho": None,
            "deleted": False,
            "deleted_on": None,
            "customer_fk": self.customer_fk.id,
            "city": self.city.id,
            "bookings": self.bookings
        }
        self.minimum_valid_data = {
            "bookings": self.bookings
        }
        self.create_url = reverse("team_to_pay_invoice_create")
        self.update_url = reverse("team_to_pay_invoice_update",
                                  kwargs={"pk": self.to_pay_invoice.id})
        self.partial_update_url = reverse("team_to_pay_invoice_partial_update",
                                          kwargs={"pk": self.to_pay_invoice.id})
        self.retrieve_url = reverse("team_to_pay_invoice_retrieve",
                                    kwargs={"pk": self.to_pay_invoice.id})

    def test_create_to_pay_invoice_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_to_pay_invoice_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding field invoice number to minimum valid data
    def test_create_to_pay_invoice_with_invoice_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["invoice_number"] = "TP-MTX1079"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding field company name to minimum valid data
    def test_create_to_pay_invoice_with_company_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["company_name"] = "some valid company"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding field city to minimum valid data
    def test_create_to_pay_invoice_with_city(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["city"] = self.city.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding field  remarks to minimum valid data
    def test_create_to_pay_invoice_with_remarks(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["remarks"] = "some valid remarks"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_to_pay_invoice_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_to_pay_invoice_with_duplicate_invoice_number(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.minimum_valid_data.copy()
        data["invoice_number"] = self.to_pay_invoice.invoice_number
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_to_pay_invoice_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.to_pay_invoice_data.copy()
        data["deleted"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.to_pay_invoice_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.to_pay_invoice_data.copy()
        data["advance_payment"] = "invalidAmount"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.to_pay_invoice_data.copy()
        data["customer_fk"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_fk"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer_fk"] = self.customer_fk.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.to_pay_invoice_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.to_pay_invoice_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.to_pay_invoice_data.copy()
        data["created_by"] = self.test_user.username
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_to_pay_invoice_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_to_pay_invoice_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.to_pay_invoice_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_to_pay_invoice_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        data = {"bookings": self.bookings}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_to_pay_invoice(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_to_pay_invoice(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_to_pay_invoice_retrieve",
                                   kwargs={"pk": self.to_pay_invoice.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PendingInwardPaymentEntryTest(TeamSetup):
    """
        Test cases for Pending Inward Payment Entry
    """

    def setUp(self):
        super().setUp()
        self.pending_inward_payment_entry_data = {
            "customer_name": "VVR180116014, YJR180125006, VVR180117013",
            "payment_mode": "cheque",
            "amount": "89950.00",
            "tds": "0.00",
            "payment_date": "2018-02-15",
            "adjusted_flag": True,
            "credited_flag": True,
            "uploaded_datetime": "2018-02-15T14:12:53",
            "adjusted_datetime": "2018-02-15T14:42:18.083133",
            "deleted": False,
            "deleted_on": None,
            "trn": "0000000000003009",
            "additional_remark": "CHQ DEP - MICR 8 CLEARING - VISAKHAPATNA",
            "inward_payment": [self.inward_payment.id],
            "customer": self.customer.id,
            "bookings": self.bookings
        }
        self.minimum_valid_data = {
            "amount": "89950.00",
            "payment_mode": "neft",
            "payment_date": "2018-06-18",
            "trn": ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(10)),
            "customer": None

        }
        self.create_url = reverse("team_pending_inward_payment_entry_create")
        self.update_url = reverse("team_pending_inward_payment_entry_update",
                                  kwargs={"pk": self.pending_inward_payment_entry.id})
        self.partial_update_url = reverse("team_pending_inward_payment_entry_partial_update",
                                          kwargs={"pk": self.pending_inward_payment_entry.id})
        self.retrieve_url = reverse("team_pending_inward_payment_entry_retrieve",
                                    kwargs={"pk": self.pending_inward_payment_entry.id})

    def test_create_pending_inward_payment_entry_with_less_than_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pending_inward_payment_entry_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding field customer to minimum valid data
    def test_create_pending_inward_payment_entry_with_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        data = self.minimum_valid_data.copy()
        data["customer"] = self.customer.id
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding field inward payment to minimum valid data
    def test_create_pending_inward_payment_entry_with_inward_payment(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        data = self.minimum_valid_data.copy()
        data["inward_payment"] = [self.inward_payment.id]
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding field deleted to minimum valid data
    def test_create_pending_inward_payment_entry_with_deleted(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        data = self.minimum_valid_data.copy()
        data["deleted"] = False
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Adding field deleted on to minimum valid data
    def test_create_pending_inward_payment_entry_with_deleted_on(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_pending_inward_payment_entry_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        response = self.client.post(self.create_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_pending_inward_payment_entry_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        data = self.pending_inward_payment_entry_data.copy()
        data["deleted"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.pending_inward_payment_entry_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.pending_inward_payment_entry_data.copy()
        data["payment_mode"] = "invalidType"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.pending_inward_payment_entry_data.copy()
        data["amount"] = "invalidAmount"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.pending_inward_payment_entry_data.copy()
        data["customer"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = self.customer.id * 100
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        self.client.credentials(CONTENT_TYPE='application/json')
        response = self.client.post(self.create_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.pending_inward_payment_entry_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken", CONTENT_TYPE='application/json')
        response = self.client.post(self.create_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.pending_inward_payment_entry_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        response = self.client.put(self.create_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        response = self.client.post(self.update_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        response = self.client.put(self.partial_update_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        response = self.client.put(self.retrieve_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.pending_inward_payment_entry_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')
        data = self.pending_inward_payment_entry_data.copy()
        data["uploaded_by"] = self.test_user.username
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_update_pending_inward_payment_entry_with_minimum_valid_date(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
    #
    # def test_update_pending_inward_payment_entry_with_full_valid_data(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.put(self.update_url, self.pending_inward_payment_entry_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_pending_inward_payment_entry_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token, CONTENT_TYPE='application/json')

        data = {"bookings": self.bookings}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_pending_inward_payment_entry(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_pending_inward_payment_entry(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_pending_inward_payment_entry_retrieve",
                                   kwargs={"pk": self.pending_inward_payment_entry.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreditDebitNoteReasonTest(TeamSetup):
    """
        Test cases for Credit Debit Note Reason
    """

    def setUp(self):
        super().setUp()
        self.credit_debit_note_reason_data = {
            "name": "testReason",
            "deleted": False,
            "deleted_on": "2012-09-09T02:23:32"
        }
        self.create_url = reverse("team_credit_debit_note_reason_create")
        self.update_url = reverse("team_credit_debit_note_reason_update", kwargs={"pk": self.reason.id})
        self.partial_update_url = reverse("team_credit_debit_note_reason_partial_update", kwargs={"pk": self.reason.id})
        self.retrieve_url = reverse("team_credit_debit_note_reason_retrieve", kwargs={"pk": self.reason.id})
        self.filter_url = reverse("team_credit_debit_note_reason_list")

    def test_create_reason_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        response = self.client.post(self.create_url, self.credit_debit_note_reason_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_all_4_functions_without_token(self):
        response = self.client.post(self.create_url, self.credit_debit_note_reason_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.credit_debit_note_reason_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.credit_debit_note_reason_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "makingInvalid")
        response = self.client.post(self.create_url, self.credit_debit_note_reason_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.credit_debit_note_reason_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.credit_debit_note_reason_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_reason_with_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.credit_debit_note_reason_data["deleted_on"] = "2012-09-09"
        response = self.client.patch(self.partial_update_url, self.credit_debit_note_reason_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_reason_with_valid_data(self):
        self.credit_debit_note_reason_data["deleted_on"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.credit_debit_note_reason_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_reason_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, {"name": "New Name"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = self.client.patch(self.partial_update_url, {"deleted": True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_reason(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_reason(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_credit_debit_note_reason_retrieve", kwargs={"pk": self.reason.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_reason_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.reason.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reason_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.reason.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reason_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reason_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reason_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reason_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CreditNoteCustomerTest(TeamSetup):
    """
        Test cases for Credit Note Customer Test
    """

    def setUp(self):
        super().setUp()
        self.credit_note_customer_minimum_data = {
            "reason": self.reason.id,
            "customer": self.customer.id,
            "credit_amount": 123456,
            "remarks": "some_valid_remark.",
        }
        self.create_url = reverse("team_credit_note_customer_create")
        self.update_url = reverse("team_credit_note_customer_update", kwargs={"pk": self.credit_note_customer.id})
        self.partial_update_url = reverse("team_credit_note_customer_partial_update",
                                          kwargs={"pk": self.credit_note_customer.id})
        self.retrieve_url = reverse("team_credit_note_customer_retrieve", kwargs={"pk": self.credit_note_customer.id})
        self.filter_url = reverse("team_credit_note_customer_list")

    def test_create_credit_note_customer_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.credit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_data_format(self):
        pass

    def test_create_credit_note_customer_with_valid_credit_amount(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["credit_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["credit_amount"] = 123456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["credit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["credit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_credit_amount(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["credit_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_valid_adjusted_amount(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["adjusted_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_adjusted_amount(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["adjusted_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_valid_approved_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["approved_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["approved_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["approved_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_approved_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["approved_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_valid_rejected_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["rejected_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rejected_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rejected_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_rejected_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["rejected_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_valid_deleted_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["deleted_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_deleted_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_valid_reason(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["reason"] = self.reason.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_reason(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["reason"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_valid_status(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["status"] = "pending"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_status(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["status"] = "approved"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "rejected"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "partial"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "adjusted"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_valid_bookings(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_bookings(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["bookings"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_valid_invoice(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["invoice"] = self.invoice.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_invoice(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["invoice"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_valid_approved_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["approved_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_approved_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["approved_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_valid_adjusted_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["adjusted_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_adjusted_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["adjusted_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_valid_rejected_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["rejected_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_rejected_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["rejected_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.credit_note_customer_minimum_data["adjusted_amount"] = 12121
        self.credit_note_customer_minimum_data["credit_amount"] = 12121
        self.credit_note_customer_minimum_data["invoice"] = self.invoice.id
        self.credit_note_customer_minimum_data["approved_on"] = "2012-09-09T02:23:32"
        self.credit_note_customer_minimum_data["approved_by"] = self.test_user.username
        self.credit_note_customer_minimum_data["remarks"] = "Good"
        self.credit_note_customer_minimum_data["deleted"] = False
        self.credit_note_customer_minimum_data["deleted_on"] = None
        self.credit_note_customer_minimum_data["status"] = "pending"
        self.credit_note_customer_minimum_data["bookings"] = self.bookings
        response = self.client.post(self.create_url, self.credit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.credit_note_customer_minimum_data["adjusted_amount"] = 1

        response = self.client.post(self.create_url, self.credit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.credit_note_customer_minimum_data["adjusted_amount"] = 2147483646
        self.credit_note_customer_minimum_data["credit_note_number"] = 12
        response = self.client.post(self.create_url, self.credit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_with_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.credit_note_customer_minimum_data.copy()
        data["adjusted_amount"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483650
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.credit_note_customer_minimum_data.copy()
        data["approved_on"] = "2012-09-09"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.credit_note_customer_minimum_data.copy()
        data["status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.credit_note_customer_minimum_data.copy()
        data["approved_by"] = "InvalidUserName"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = self.customer.id * 10000
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # updating credit note customer
    def test_update_credit_note_customer_with_unauthenticated_user(self):
        data = self.credit_note_customer_minimum_data.copy()
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_credit_note_customer_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        data = self.credit_note_customer_minimum_data.copy()
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_credit_note_customer_with_invalid_method(self):
        data = self.credit_note_customer_minimum_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_credit_note_customer_with_invalid_data_format(self):
        pass

    def test_update_credit_note_customer_with_valid_credit_amount(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["credit_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["credit_amount"] = 123456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["credit_amount"] = 2147483646
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["credit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_credit_amount(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["credit_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_with_valid_adjusted_amount(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["adjusted_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_adjusted_amount(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["adjusted_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_with_valid_approved_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["approved_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["approved_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["approved_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_approved_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["approved_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_with_valid_rejected_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["rejected_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["rejected_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["rejected_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_rejected_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["rejected_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_with_valid_deleted_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["deleted_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_deleted_on(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_with_valid_reason(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["reason"] = self.reason.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_reason(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["reason"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_with_valid_bookings(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_bookings(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["bookings"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_with_valid_invoice(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["invoice"] = self.invoice.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["invoice"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["invoice"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_invoice(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["invoice"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_with_valid_approved_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["approved_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_approved_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["approved_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_with_valid_adjusted_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["adjusted_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_adjusted_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["adjusted_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_with_valid_rejected_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["rejected_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_rejected_by(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["rejected_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_with_valid_status(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["status"] = "approved"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "partial"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "rejected"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "adjusted"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_invalid_status(self):
        data = self.credit_note_customer_minimum_data.copy()

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_functions_without_token(self):
        response = self.client.post(self.create_url, self.credit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.credit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.credit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.credit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.credit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.credit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_credit_note_customer_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.credit_note_customer_minimum_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_with_full_valid_data(self):
        self.credit_note_customer_minimum_data["adjusted_amount"] = 12121
        self.credit_note_customer_minimum_data["credit_amount"] = 12121
        self.credit_note_customer_minimum_data["invoice"] = self.invoice.id
        self.credit_note_customer_minimum_data["approved_on"] = "2012-09-09T02:23:32"
        self.credit_note_customer_minimum_data["approved_by"] = self.test_user.username
        self.credit_note_customer_minimum_data["remarks"] = "Good"
        self.credit_note_customer_minimum_data["deleted"] = False
        self.credit_note_customer_minimum_data["deleted_on"] = None
        self.credit_note_customer_minimum_data["status"] = "pending"
        self.credit_note_customer_minimum_data["bookings"] = self.bookings

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.credit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_credit_note_customer_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        adjusted_amount = {"adjusted_amount": 1231}
        response = self.client.patch(self.partial_update_url, adjusted_amount, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_on = {"issued_on": "2012-09-09T02:23:32"}
        response = self.client.patch(self.partial_update_url, issued_on, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        status_data = {"status": "pending"}
        response = self.client.patch(self.partial_update_url, status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_by = {"issued_by": self.test_user.username}
        response = self.client.patch(self.partial_update_url, issued_by, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        customer = {"customer": self.customer.id}
        response = self.client.patch(self.partial_update_url, customer, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_credit_note_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_credit_note_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_credit_note_customer_retrieve",
                                   kwargs={"pk": self.credit_note_customer.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_credit_note_customer_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.credit_note_customer.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_credit_note_customer_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.credit_note_customer.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_credit_note_customer_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_credit_note_customer_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_credit_note_customer_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_credit_note_customer_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class DebitNoteCustomerTest(TeamSetup):
    """
        Test cases for Debit Note Customer
    """

    def setUp(self):
        super().setUp()
        self.debit_note_customer_data = {
            "debit_note_number": "12",
            "customer": self.customer.id,
            "reason": self.reason.id,
            "debit_amount": 12000,
            "remarks": "some_valid_remarks."
        }
        self.debit_note_customer_minimum_data = {
            "customer": self.customer.id,
            "reason": self.reason.id,
            "debit_amount": 12000,
            "remarks": "some_valid_remarks."
        }
        self.create_url = reverse("team_debit_note_customer_create")
        self.update_url = reverse("team_debit_note_customer_update", kwargs={"pk": self.debit_note_customer.id})
        self.partial_update_url = reverse("team_debit_note_customer_partial_update",
                                          kwargs={"pk": self.debit_note_customer.id})
        self.retrieve_url = reverse("team_debit_note_customer_retrieve", kwargs={"pk": self.debit_note_customer.id})
        self.filter_url = reverse("team_debit_note_customer_list")

    def test_create_debit_note_customer_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.debit_note_customer_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_data_format(self):
        pass

    def test_create_debit_note_customer_with_valid_debit_amount(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["debit_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["debit_amount"] = 123456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["debit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["debit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_debit_amount(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["debit_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_valid_adjusted_amount(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["adjusted_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_adjusted_amount(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["adjusted_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_valid_approved_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["approved_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["approved_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["approved_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_approved_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["approved_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_valid_rejected_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["rejected_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rejected_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rejected_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_rejected_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["rejected_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_valid_deleted_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["deleted_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_deleted_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_valid_reason(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["reason"] = self.reason.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_reason(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["reason"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_valid_status(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["status"] = "pending"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_status(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["status"] = "approved"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "rejected"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "partial"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "adjusted"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_valid_bookings(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_bookings(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["bookings"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_valid_invoice(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["invoice"] = self.invoice.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_invoice(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["invoice"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_valid_approved_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["approved_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_approved_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["approved_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_valid_adjusted_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["adjusted_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_adjusted_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["adjusted_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_valid_rejected_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["rejected_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_rejected_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["rejected_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # update debit note customer

    def test_update_debit_note_customer_with_unauthenticated_user(self):
        data = self.debit_note_customer_minimum_data.copy()
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_debit_note_customer_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        data = self.debit_note_customer_minimum_data.copy()
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_debit_note_customer_with_invalid_method(self):
        data = self.debit_note_customer_minimum_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_debit_note_customer_with_invalid_data_format(self):
        pass

    def test_update_debit_note_customer_with_valid_debit_amount(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["debit_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["debit_amount"] = 123456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["debit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["debit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_debit_amount(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["debit_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_customer_with_valid_adjusted_amount(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["adjusted_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_adjusted_amount(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["adjusted_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_customer_with_valid_approved_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["approved_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["approved_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["approved_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_approved_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["approved_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_customer_with_valid_rejected_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["rejected_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["rejected_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["rejected_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_rejected_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["rejected_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_customer_with_valid_deleted_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["deleted_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_deleted_on(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_customer_with_valid_reason(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["reason"] = self.reason.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_reason(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["reason"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_customer_with_valid_bookings(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_bookings(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["bookings"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_customer_with_valid_invoice(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["invoice"] = self.invoice.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["invoice"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["invoice"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_invoice(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["invoice"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_customer_with_valid_approved_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["approved_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_approved_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["approved_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_customer_with_valid_adjusted_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["adjusted_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_adjusted_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["adjusted_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_customer_with_valid_rejected_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["rejected_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_rejected_by(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["rejected_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_customer_with_valid_status(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["status"] = "approved"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "partial"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "rejected"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "adjusted"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_invalid_status(self):
        data = self.debit_note_customer_minimum_data.copy()

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_customer_with_adjustment_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_customer_data["adjusted_amount"] = "23423"
        response = self.client.post(self.create_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invoice_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_customer_data["invoice"] = self.invoice.id
        response = self.client.post(self.create_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_both_adjustment_invoice_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_customer_data["adjusted_amount"] = "23123"
        self.debit_note_customer_data["invoice"] = self.invoice.id
        response = self.client.post(self.create_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_customer_data["adjusted_amount"] = 12121
        self.debit_note_customer_data["debit_amount"] = 12121
        self.debit_note_customer_data["invoice"] = self.invoice.id
        self.debit_note_customer_data["approved_on"] = "2012-09-09T02:23:32"
        self.debit_note_customer_data["approved_by"] = self.test_user.username
        self.debit_note_customer_data["remarks"] = "Good"
        self.debit_note_customer_data["deleted"] = False
        self.debit_note_customer_data["deleted_on"] = None
        self.debit_note_customer_data["bookings"] = self.bookings
        self.debit_note_customer_data["status"] = "pending"

        response = self.client.post(self.create_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.debit_note_customer_data["adjusted_amount"] = 1
        self.debit_note_customer_data["debit_note_number"] = 1231

        response = self.client.post(self.create_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.debit_note_customer_data["adjusted_amount"] = 1000000
        self.debit_note_customer_data["debit_note_number"] = 12
        response = self.client.post(self.create_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_customer_with_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.debit_note_customer_data.copy()
        data["adjusted_amount"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483650
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.debit_note_customer_data.copy()
        data["approved_on"] = "2012-09-09"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.debit_note_customer_data.copy()
        data["status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.debit_note_customer_data.copy()
        data["approved_by"] = "InvalidUserName"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = self.customer.id * 10000
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_functions_without_token(self):
        response = self.client.post(self.create_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_debit_note_customer_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.debit_note_customer_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_customer_with_full_valid_data(self):
        self.debit_note_customer_data["adjusted_amount"] = 12121
        self.debit_note_customer_data["debit_amount"] = 12121
        self.debit_note_customer_data["invoice"] = self.invoice.id
        self.debit_note_customer_data["approved_by"] = self.test_user.username
        self.debit_note_customer_data["approved_on"] = None
        self.debit_note_customer_data["remarks"] = "Good"
        self.debit_note_customer_data["deleted"] = False
        self.debit_note_customer_data["deleted_on"] = None
        self.debit_note_customer_data["customer"] = self.customer.id
        self.debit_note_customer_data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.debit_note_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_debit_note_customer_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        adjusted_amount = {"adjusted_amount": 1231}
        response = self.client.patch(self.partial_update_url, adjusted_amount, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_on = {"issued_on": "2012-09-09T02:23:32"}
        response = self.client.patch(self.partial_update_url, issued_on, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        status_data = {"status": "pending"}
        response = self.client.patch(self.partial_update_url, status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_by = {"issued_by": self.test_user.username}
        response = self.client.patch(self.partial_update_url, issued_by, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        customer = {"customer": self.customer.id}
        response = self.client.patch(self.partial_update_url, customer, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_debit_note_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_debit_note_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_debit_note_customer_retrieve",
                                   kwargs={"pk": self.debit_note_customer.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_debit_note_customer_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.debit_note_customer.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_debit_note_customer_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.debit_note_customer.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_debit_note_customer_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_debit_note_customer_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_debit_note_customer_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_debit_note_customer_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CreditNoteSupplierTest(TeamSetup):
    """
        Test cases for Credit Note Supplier
    """

    def setUp(self):
        super().setUp()
        self.credit_note_supplier_data = {
            "credit_note_number": "1232",
            "reason": self.reason.id,
            "broker": self.broker.id,
            "credit_amount": 12000,
            "remarks": "some_valid_remarks",
            "accounting_supplier": self.supplier.id,
        }
        self.credit_note_supplier_minimum_data = {
            "broker": self.broker.id,
            "reason": self.reason.id,
            "credit_amount": 12000,
            "remarks": "some_valid_remarks",
            "accounting_supplier": self.supplier.id,
        }

        self.create_url = reverse("team_credit_note_supplier_create")
        self.update_url = reverse("team_credit_note_supplier_update", kwargs={"pk": self.credit_note_supplier.id})
        self.partial_update_url = reverse("team_credit_note_supplier_partial_update",
                                          kwargs={"pk": self.credit_note_supplier.id})
        self.retrieve_url = reverse("team_credit_note_supplier_retrieve", kwargs={"pk": self.credit_note_supplier.id})
        self.filter_url = reverse("team_credit_note_supplier_list")

    def test_create_credit_note_supplier_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.credit_note_supplier_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_data_format(self):
        pass

    def test_create_credit_note_supplier_with_valid_credit_amount(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["credit_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["credit_amount"] = 123456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["credit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["credit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_credit_amount(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["credit_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_valid_adjusted_amount(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["adjusted_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_adjusted_amount(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["adjusted_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_valid_approved_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["approved_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["approved_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["approved_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_approved_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["approved_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_valid_rejected_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["rejected_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rejected_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rejected_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_rejected_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["rejected_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_valid_deleted_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["deleted_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_deleted_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_valid_reason(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["reason"] = self.reason.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_reason(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["reason"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_valid_status(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["status"] = "pending"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_status(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["status"] = "approved"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "rejected"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "partial"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "adjusted"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_valid_bookings(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_bookings(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["bookings"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_valid_invoice(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["invoice"] = self.invoice.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_invoice(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["invoice"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_valid_approved_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["approved_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_approved_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["approved_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_valid_adjusted_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["adjusted_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_adjusted_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["adjusted_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_valid_rejected_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["rejected_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_rejected_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["rejected_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # updating credit note supplier

    def test_update_credit_note_supplier_with_unauthenticated_user(self):
        data = self.credit_note_supplier_minimum_data.copy()
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_credit_note_supplier_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        data = self.credit_note_supplier_minimum_data.copy()
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_credit_note_supplier_with_invalid_method(self):
        data = self.credit_note_supplier_minimum_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_credit_note_supplier_with_invalid_data_format(self):
        pass

    def test_update_credit_note_supplier_with_valid_credit_amount(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["credit_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["credit_amount"] = 123456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["credit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["credit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_credit_amount(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["credit_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_supplier_with_valid_adjusted_amount(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["adjusted_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_adjusted_amount(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["adjusted_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_supplier_with_valid_approved_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["approved_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["approved_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["approved_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_approved_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["approved_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_supplier_with_valid_rejected_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["rejected_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["rejected_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["rejected_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_rejected_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["rejected_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_supplier_with_valid_deleted_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["deleted_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_deleted_on(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_supplier_with_valid_reason(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["reason"] = self.reason.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_reason(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["reason"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_supplier_with_valid_bookings(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_bookings(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["bookings"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_supplier_with_valid_invoice(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["invoice"] = self.invoice.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["invoice"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["invoice"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_invoice(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["invoice"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_supplier_with_valid_approved_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["approved_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_approved_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["approved_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_supplier_with_valid_adjusted_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["adjusted_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_adjusted_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["adjusted_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_supplier_with_valid_rejected_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["rejected_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_rejected_by(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["rejected_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_supplier_with_valid_status(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["status"] = "approved"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "partial"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "rejected"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "adjusted"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_invalid_status(self):
        data = self.credit_note_supplier_minimum_data.copy()

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_supplier_with_adjustment_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.credit_note_supplier_data["adjusted_amount"] = "23423"
        response = self.client.post(self.create_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invoice_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.credit_note_supplier_data["invoice"] = self.invoice.id
        response = self.client.post(self.create_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_both_adjustment_invoice_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.credit_note_supplier_data["adjusted_amount"] = "23123"
        self.credit_note_supplier_data["invoice"] = self.invoice.id
        response = self.client.post(self.create_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.credit_note_supplier_data["adjusted_amount"] = 12121
        self.credit_note_supplier_data["credit_amount"] = 12121
        self.credit_note_supplier_data["invoice"] = self.invoice.id
        self.credit_note_supplier_data["approved_by"] = self.test_user.username
        self.credit_note_supplier_data["approved_on"] = "2012-09-09T02:23:32"
        self.credit_note_supplier_data["remarks"] = "Good"
        self.credit_note_supplier_data["deleted"] = False
        self.credit_note_supplier_data["deleted_on"] = None
        self.credit_note_supplier_data["broker"] = self.broker.id
        self.credit_note_supplier_data["bookings"] = self.bookings

        response = self.client.post(self.create_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.credit_note_supplier_data["adjusted_amount"] = 1

        response = self.client.post(self.create_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.credit_note_supplier_data["adjusted_amount"] = 1000000
        response = self.client.post(self.create_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_supplier_with_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.credit_note_supplier_data.copy()
        data["adjusted_amount"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483650
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.credit_note_supplier_data.copy()
        data["approved_on"] = "2012-09-09"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.credit_note_supplier_data.copy()
        data["status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.credit_note_supplier_data.copy()
        data["approved_by"] = "InvalidUserName"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["broker"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["broker"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["broker"] = self.customer.id * 10000
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_credit_note_supplier_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.credit_note_supplier_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_supplier_with_full_valid_data(self):
        self.credit_note_supplier_data["adjusted_amount"] = 12121
        self.credit_note_supplier_data["invoice"] = self.invoice.id
        self.credit_note_supplier_data["approved_on"] = "2012-09-09T02:23:32"
        self.credit_note_supplier_data["approved_by"] = self.test_user.username
        self.credit_note_supplier_data["remarks"] = "Good"
        self.credit_note_supplier_data["deleted"] = False
        self.credit_note_supplier_data["broker"] = self.broker.id
        self.credit_note_supplier_data["bookings"] = self.bookings

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.credit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_credit_note_supplier_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        adjusted_amount = {"adjusted_amount": 1231}
        response = self.client.patch(self.partial_update_url, adjusted_amount, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_on = {"approved_on": "2012-09-09T02:23:32"}
        response = self.client.patch(self.partial_update_url, issued_on, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        status_data = {"status": "pending"}
        response = self.client.patch(self.partial_update_url, status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_by = {"approved_by": self.test_user.username}
        response = self.client.patch(self.partial_update_url, issued_by, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        supplier = {"broker": self.broker.id}
        response = self.client.patch(self.partial_update_url, supplier, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_credit_note_supplier(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_credit_note_supplier(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_debit_note_customer_retrieve",
                                   kwargs={"pk": self.credit_note_supplier.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_credit_note_supplier_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.credit_note_supplier.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_credit_note_supplier_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.credit_note_supplier.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_credit_note_supplier_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_credit_note_supplier_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_credit_note_supplier_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_credit_note_supplier_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class DebitNoteSupplierTest(TeamSetup):
    """
        Test cases for Credit Note Supplier
    """

    def setUp(self):
        super().setUp()
        self.debit_note_supplier_data = {
            "reason": self.reason.id,
            "broker": self.broker.id,
            "debit_amount": 12000,
            "remarks": "some_valid_remark.",
            "accounting_supplier": self.supplier.id,
        }
        self.debit_note_supplier_minimum_data = {
            "broker": self.broker.id,
            "reason": self.reason.id,
            "debit_amount": 12000,
            "remarks": "some_valid_remark.",
            "accounting_supplier": self.supplier.id,
        }
        self.create_url = reverse("team_debit_note_supplier_create")
        self.update_url = reverse("team_debit_note_supplier_update", kwargs={"pk": self.debit_note_supplier.id})
        self.partial_update_url = reverse("team_debit_note_supplier_partial_update",
                                          kwargs={"pk": self.debit_note_supplier.id})
        self.retrieve_url = reverse("team_debit_note_supplier_retrieve", kwargs={"pk": self.debit_note_supplier.id})
        self.filter_url = reverse("team_debit_note_supplier_list")

    def test_create_debit_note_supplier_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.debit_note_supplier_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_data_format(self):
        pass

    def test_create_debit_note_supplier_with_valid_debit_amount(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["debit_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["debit_amount"] = 123456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["debit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["debit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_debit_amount(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["debit_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_valid_adjusted_amount(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["adjusted_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_adjusted_amount(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["adjusted_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_valid_approved_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["approved_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["approved_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["approved_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_approved_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["approved_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_valid_rejected_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["rejected_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rejected_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rejected_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_rejected_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["rejected_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_valid_deleted_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["deleted_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_deleted_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_valid_reason(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["reason"] = self.reason.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_reason(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["reason"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_valid_status(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["status"] = "pending"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_status(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["status"] = "approved"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "rejected"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "partial"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "adjusted"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_valid_bookings(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_bookings(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["bookings"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_valid_invoice(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["invoice"] = self.invoice.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_invoice(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["invoice"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_valid_approved_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["approved_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_approved_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["approved_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_valid_adjusted_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["adjusted_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_adjusted_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["adjusted_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_valid_rejected_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["rejected_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_rejected_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["rejected_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debit_note_supplier_with_adjustment_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_supplier_data["adjusted_amount"] = "23423"
        response = self.client.post(self.create_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invoice_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_supplier_data["invoice"] = self.invoice.id
        response = self.client.post(self.create_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_both_adjustment_invoice_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_supplier_data["adjusted_amount"] = "23123"
        self.debit_note_supplier_data["invoice"] = self.invoice.id
        response = self.client.post(self.create_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_supplier_data["adjusted_amount"] = 12121
        self.debit_note_supplier_data["debit_amount"] = 12121
        self.debit_note_supplier_data["invoice"] = self.invoice.id
        self.debit_note_supplier_data["approved_by"] = self.test_user.username
        self.debit_note_supplier_data["approved_on"] = "2012-09-09T02:23:32"
        self.debit_note_supplier_data["remarks"] = "Good"
        self.debit_note_supplier_data["deleted"] = False
        self.debit_note_supplier_data["deleted_on"] = None
        self.debit_note_supplier_data["bookings"] = self.bookings
        self.debit_note_supplier_data["status"] = "pending"

        response = self.client.post(self.create_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.debit_note_supplier_data["adjusted_amount"] = 1
        response = self.client.post(self.create_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.debit_note_supplier_data["adjusted_amount"] = 1000000
        response = self.client.post(self.create_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_with_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.debit_note_supplier_data.copy()
        data["adjusted_amount"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483650
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.debit_note_supplier_data.copy()
        data["approved_on"] = "2012-09-09"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.debit_note_supplier_data.copy()
        data["status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.debit_note_supplier_data.copy()
        data["approved_by"] = "InvalidUserName"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["broker"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["broker"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["broker"] = self.customer.id * 10000
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # updating debit note supplier

    def test_update_debit_note_supplier_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.debit_note_supplier_minimum_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_unauthenticated_user(self):
        data = self.debit_note_supplier_minimum_data.copy()
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_debit_note_supplier_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        data = self.debit_note_supplier_minimum_data.copy()
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_debit_note_supplier_with_invalid_method(self):
        data = self.debit_note_supplier_minimum_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_debit_note_supplier_with_invalid_data_format(self):
        pass

    def test_update_debit_note_supplier_with_valid_credit_amount(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["debit_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["debit_amount"] = 123456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["debit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["debit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_credit_amount(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["debit_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["debit_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_valid_adjusted_amount(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["adjusted_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_adjusted_amount(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["adjusted_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_valid_approved_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["approved_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["approved_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["approved_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_approved_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["approved_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_valid_rejected_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["rejected_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["rejected_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["rejected_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_rejected_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["rejected_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_valid_deleted_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["deleted_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_deleted_on(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_valid_reason(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["reason"] = self.reason.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_reason(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["reason"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_valid_bookings(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_bookings(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["bookings"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_valid_invoice(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["invoice"] = self.invoice.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["invoice"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["invoice"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_invoice(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["invoice"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_valid_approved_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["approved_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_approved_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["approved_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_valid_adjusted_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["adjusted_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_adjusted_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["adjusted_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_valid_rejected_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["rejected_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_rejected_by(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["rejected_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_valid_status(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["status"] = "approved"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "partial"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "rejected"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "adjusted"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_with_invalid_status(self):
        data = self.debit_note_supplier_minimum_data.copy()

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_debit_note_supplier_with_full_valid_data(self):
        self.debit_note_supplier_data["adjusted_amount"] = 12121
        self.debit_note_supplier_data["debit_amount"] = 12121
        self.debit_note_supplier_data["invoice"] = self.invoice.id
        self.debit_note_supplier_data["approved_by"] = self.test_user.username
        self.debit_note_supplier_data["approved_on"] = "2012-09-09T02:23:32"
        self.debit_note_supplier_data["remarks"] = "Good"
        self.debit_note_supplier_data["deleted"] = False
        self.debit_note_supplier_data["deleted_on"] = None
        self.debit_note_supplier_data["bookings"] = self.bookings
        self.debit_note_supplier_data["status"] = "pending"

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.debit_note_supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_debit_note_supplier_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        adjusted_amount = {"adjusted_amount": 1231}
        response = self.client.patch(self.partial_update_url, adjusted_amount, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_on = {"approved_on": "2012-09-09T02:23:32"}
        response = self.client.patch(self.partial_update_url, issued_on, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        status_data = {"status": "pending"}
        response = self.client.patch(self.partial_update_url, status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_by = {"approved_by": self.test_user.username}
        response = self.client.patch(self.partial_update_url, issued_by, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        supplier = {"broker": self.broker.id}
        response = self.client.patch(self.partial_update_url, supplier, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_debit_note_supplier(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_debit_note_supplier(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_debit_note_supplier_retrieve",
                                   kwargs={"pk": self.debit_note_supplier.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_debit_note_supplier_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.debit_note_supplier.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_debit_note_supplier_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.debit_note_supplier.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_debit_note_supplier_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_debit_note_supplier_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_debit_note_supplier_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_debit_note_supplier_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CreditNoteCustomerDirectAdvanceTest(TeamSetup):
    """
        Test cases for Credit Note Customer Direct Advance Test
    """

    def setUp(self):
        super().setUp()
        self.credit_note_customer_direct_advance_data = {
            "reason": self.reason.id,
            "customer": self.customer.id
        }
        self.credit_note_customer_direct_advance_minimum_data = {
            "customer": self.customer.id,
            "broker": self.broker.id,
            "credit_amount": 12000,
            "reason": self.reason.id,
            "remarks": "some_valid_remark.",
            "bookings": self.bookings,
            "supplier": self.supplier.id,
        }

        self.create_url = reverse("team_credit_note_customer_direct_advance_create")
        self.update_url = reverse("team_credit_note_customer_direct_advance_update",
                                  kwargs={"pk": self.credit_note_customer_direct_advance.id})
        self.partial_update_url = reverse("team_credit_note_customer_direct_advance_partial_update",
                                          kwargs={"pk": self.credit_note_customer_direct_advance.id})
        self.retrieve_url = reverse("team_credit_note_customer_direct_advance_retrieve",
                                    kwargs={"pk": self.credit_note_customer_direct_advance.id})
        self.filter_url = reverse("team_credit_note_customer_direct_advance_list")

    def test_create_credit_note_customer_direct_advance_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.credit_note_customer_direct_advance_minimum_data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_data_format(self):
        pass

    def test_create_credit_note_customer_direct_advance_with_valid_credit_amount(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["credit_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["credit_amount"] = 123456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["credit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["credit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_credit_amount(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["credit_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_valid_adjusted_amount(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["adjusted_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_adjusted_amount(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["adjusted_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_valid_approved_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["approved_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["approved_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["approved_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_approved_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["approved_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_valid_rejected_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["rejected_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rejected_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["rejected_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_rejected_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["rejected_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_valid_deleted_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["deleted_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_deleted_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_valid_reason(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["reason"] = self.reason.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_reason(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["reason"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_valid_status(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["status"] = "pending"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_status(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["status"] = "approved"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "rejected"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "partial"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "adjusted"  # must be pending only during creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_valid_bookings(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_bookings(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["bookings"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_valid_invoice(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["invoice"] = self.invoice.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data["invoice"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_invoice(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["invoice"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_valid_approved_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["approved_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_approved_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["approved_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_valid_adjusted_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["adjusted_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_adjusted_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["adjusted_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_valid_rejected_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["rejected_by"] = self.test_user.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_rejected_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["rejected_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credit_note_customer_direct_advance_with_adjustment_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.credit_note_customer_direct_advance_data["adjusted_amount"] = "23423"
        response = self.client.post(self.create_url, self.credit_note_customer_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invoice_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.credit_note_customer_direct_advance_data["invoice"] = self.invoice.id
        response = self.client.post(self.create_url, self.credit_note_customer_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_both_adjustment_invoice_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.credit_note_customer_direct_advance_data["adjusted_amount"] = "23123"
        self.credit_note_customer_direct_advance_data["invoice"] = self.invoice.id
        response = self.client.post(self.create_url, self.credit_note_customer_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.credit_note_customer_direct_advance_data["adjusted_amount"] = 12121
        self.credit_note_customer_direct_advance_data["credit_amount"] = 12121
        self.credit_note_customer_direct_advance_data["invoice"] = self.invoice.id
        self.credit_note_customer_direct_advance_data["approved_by"] = self.test_user.username
        self.credit_note_customer_direct_advance_data["approved_on"] = "2012-09-09T02:23:32"
        self.credit_note_customer_direct_advance_data["remarks"] = "Good"
        self.credit_note_customer_direct_advance_data["deleted"] = False
        self.credit_note_customer_direct_advance_data["deleted_on"] = None
        self.credit_note_customer_direct_advance_data["status"] = "pending"
        self.credit_note_customer_direct_advance_data["broker"] = self.broker.id
        self.credit_note_customer_direct_advance_data["bookings"] = self.bookings

        response = self.client.post(self.create_url, self.credit_note_customer_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.credit_note_customer_direct_advance_data["adjusted_amount"] = 1
        response = self.client.post(self.create_url, self.credit_note_customer_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.credit_note_customer_direct_advance_data["adjusted_amount"] = 1000000
        response = self.client.post(self.create_url, self.credit_note_customer_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_credit_note_customer_direct_advance_with_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.credit_note_customer_direct_advance_data.copy()
        data["adjusted_amount"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483650
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.credit_note_customer_direct_advance_data.copy()
        data["approved_on"] = "2012-09-09"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.credit_note_customer_direct_advance_data.copy()
        data["status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.credit_note_customer_direct_advance_data.copy()
        data["approved_by"] = "InvalidUserName"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = self.customer.id * 10000
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.credit_note_customer_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.credit_note_customer_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.credit_note_customer_direct_advance_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.credit_note_customer_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.credit_note_customer_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.credit_note_customer_direct_advance_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # update credit note customer direct advance

    def test_update_credit_note_customer_direct_advance_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.credit_note_customer_direct_advance_minimum_data,
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_unauthenticated_user(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_credit_note_customer_direct_advance_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + 'invalidToken')
        data = self.credit_note_customer_direct_advance_minimum_data.copy()
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_credit_note_customer_direct_advance_with_invalid_method(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_credit_note_customer_direct_advance_with_invalid_data_format(self):
        pass

    def test_update_credit_note_customer_direct_advance_with_valid_credit_amount(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["credit_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["credit_amount"] = 123456
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["credit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["credit_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_credit_amount(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["credit_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["credit_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_valid_adjusted_amount(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["adjusted_amount"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["adjusted_amount"] = 1000000
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_adjusted_amount(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["adjusted_amount"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = "invalid_amount"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483648
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_valid_approved_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["approved_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["approved_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["approved_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_approved_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["approved_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_valid_rejected_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["rejected_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["rejected_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["rejected_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_rejected_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["rejected_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_valid_deleted_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["deleted_on"] = datetime(2018, 7, 14, 12, 30)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["deleted_on"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_deleted_on(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["deleted_on"] = "09/12/2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "invalid_date"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-12-18"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "18-12-09"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["deleted_on"] = "09-December-2018"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_valid_reason(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["reason"] = self.reason.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_reason(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["reason"] = "invalid_id"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["reason"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_valid_bookings(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["bookings"] = self.bookings
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_bookings(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["bookings"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = ""
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["bookings"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_valid_invoice(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["invoice"] = self.invoice.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["invoice"] = None
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_invoice(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["invoice"] = "invalid"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -123
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = 0
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = -3.14
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["invoice"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_valid_approved_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["approved_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_approved_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["approved_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["approved_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_valid_adjusted_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["adjusted_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_adjusted_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["adjusted_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_valid_rejected_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["rejected_by"] = self.test_user2.username
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_rejected_by(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["rejected_by"] = "invalid_user"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["rejected_by"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_valid_status(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["status"] = "approved"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "partial"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "rejected"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data["status"] = "adjusted"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_credit_note_customer_direct_advance_with_invalid_status(self):
        data = self.credit_note_customer_direct_advance_minimum_data.copy()

        data["status"] = "invalid_status"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["status"] = str(datetime.now())
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_credit_note_customer_direct_advance_with_full_valid_data(self):
        self.credit_note_customer_direct_advance_data["adjusted_amount"] = 12121
        self.credit_note_customer_direct_advance_data["credit_amount"] = 12121
        self.credit_note_customer_direct_advance_data["invoice"] = self.invoice.id
        self.credit_note_customer_direct_advance_data["approved_by"] = self.test_user.username
        self.credit_note_customer_direct_advance_data["approved_on"] = "2012-09-09T02:23:32"
        self.credit_note_customer_direct_advance_data["remarks"] = "Good"
        self.credit_note_customer_direct_advance_data["deleted"] = False
        self.credit_note_customer_direct_advance_data["deleted_on"] = None
        self.credit_note_customer_direct_advance_data["status"] = "pending"
        self.credit_note_customer_direct_advance_data["broker"] = self.broker.id
        self.credit_note_customer_direct_advance_data["bookings"] = self.bookings

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.credit_note_customer_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_credit_note_customer_direct_advance_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        adjusted_amount = {"adjusted_amount": 1231}
        response = self.client.patch(self.partial_update_url, adjusted_amount, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_on = {"approved_on": "2012-09-09T02:23:32"}
        response = self.client.patch(self.partial_update_url, issued_on, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        status_data = {"status": "pending"}
        response = self.client.patch(self.partial_update_url, status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_by = {"approved_by": self.test_user.username}
        response = self.client.patch(self.partial_update_url, issued_by, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        customer_direct_advance = {"customer": self.customer.id}
        response = self.client.patch(self.partial_update_url, customer_direct_advance, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_credit_note_customer_direct_advance(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_credit_note_customer_direct_advance(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_debit_note_customer_retrieve",
                                   kwargs={"pk": self.credit_note_customer_direct_advance.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_credit_note_customer_direct_advance_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.credit_note_customer_direct_advance.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_credit_note_customer_direct_advance_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.credit_note_customer_direct_advance.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_credit_note_customer_direct_advance_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_credit_note_customer_direct_advance_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_credit_note_customer_direct_advance_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_credit_note_customer_direct_advance_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class DebitNoteSupplierDirectAdvanceTest(TeamSetup):
    """
        Test cases for Debit Note Supplier Direct Advance
    """

    def setUp(self):
        super().setUp()
        self.debit_note_supplier_direct_advance_data = {

            "reason": self.reason.id,
            "broker": self.broker.id,
            'accounting_supplier':self.supplier.id
        }
        self.create_url = reverse("team_debit_note_supplier_direct_advance_create")
        self.update_url = reverse("team_debit_note_supplier_direct_advance_update",
                                  kwargs={"pk": self.debit_note_supplier_direct_advance.id})
        self.partial_update_url = reverse("team_debit_note_supplier_direct_advance_partial_update",
                                          kwargs={"pk": self.debit_note_supplier_direct_advance.id})
        self.retrieve_url = reverse("team_debit_note_supplier_direct_advance_retrieve",
                                    kwargs={"pk": self.debit_note_supplier_direct_advance.id})
        self.filter_url = reverse("team_debit_note_supplier_direct_advance_list")

    def test_create_debit_note_supplier_direct_advance_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_direct_advance_with_adjustment_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_supplier_direct_advance_data["adjusted_amount"] = "23423"
        response = self.client.post(self.create_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_direct_advance_with_invoice_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_supplier_direct_advance_data["invoice"] = self.invoice.id
        response = self.client.post(self.create_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_direct_advance_with_both_adjustment_invoice_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_supplier_direct_advance_data["adjusted_amount"] = "23123"
        self.debit_note_supplier_direct_advance_data["invoice"] = self.invoice.id
        response = self.client.post(self.create_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_direct_advance_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.debit_note_supplier_direct_advance_data["adjusted_amount"] = 12121
        self.debit_note_supplier_direct_advance_data["debit_amount"] = 12121
        self.debit_note_supplier_direct_advance_data["invoice"] = self.invoice.id
        self.debit_note_supplier_direct_advance_data["approved_by"] = self.test_user.username
        self.debit_note_supplier_direct_advance_data["approved_on"] = "2012-09-09T02:23:32"
        self.debit_note_supplier_direct_advance_data["remarks"] = "Good"
        self.debit_note_supplier_direct_advance_data["deleted"] = False
        self.debit_note_supplier_direct_advance_data["deleted_on"] = None
        self.debit_note_supplier_direct_advance_data["status"] = "pending"
        self.debit_note_supplier_direct_advance_data["customer"] = self.customer.id
        self.debit_note_supplier_direct_advance_data["bookings"] = self.bookings

        response = self.client.post(self.create_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.debit_note_supplier_direct_advance_data["adjusted_amount"] = 1

        response = self.client.post(self.create_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.debit_note_supplier_direct_advance_data["adjusted_amount"] = 1000000
        response = self.client.post(self.create_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_debit_note_supplier_direct_advance_with_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.debit_note_supplier_direct_advance_data.copy()
        data["adjusted_amount"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["adjusted_amount"] = 2147483650
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.debit_note_supplier_direct_advance_data.copy()
        data["approved_on"] = "2012-09-09"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.debit_note_supplier_direct_advance_data.copy()
        data["status"] = "InvalidChoice"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.debit_note_supplier_direct_advance_data.copy()
        data["approved_by"] = "InvalidUserName"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = -1
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = "invalidId"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["customer"] = self.customer.id * 10000
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.debit_note_supplier_direct_advance_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.debit_note_supplier_direct_advance_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_debit_note_supplier_direct_advance_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_debit_note_supplier_direct_advance_with_full_valid_data(self):
        self.debit_note_supplier_direct_advance_data["adjusted_amount"] = 12121
        self.debit_note_supplier_direct_advance_data["debit_amount"] = 12121
        self.debit_note_supplier_direct_advance_data["invoice"] = self.invoice.id
        self.debit_note_supplier_direct_advance_data["approved_by"] = self.test_user.username
        self.debit_note_supplier_direct_advance_data["approved_on"] = "2012-09-09T02:23:32"
        self.debit_note_supplier_direct_advance_data["remarks"] = "Good"
        self.debit_note_supplier_direct_advance_data["deleted"] = False
        self.debit_note_supplier_direct_advance_data["deleted_on"] = None
        self.debit_note_supplier_direct_advance_data["status"] = "pending"
        self.debit_note_supplier_direct_advance_data["customer"] = self.customer.id
        self.debit_note_supplier_direct_advance_data["bookings"] = self.bookings

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.update_url, self.debit_note_supplier_direct_advance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_debit_note_supplier_direct_advance_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

        adjusted_amount = {"adjusted_amount": 1231}
        response = self.client.patch(self.partial_update_url, adjusted_amount, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_on = {"approved_on": "2012-09-09T02:23:32"}
        response = self.client.patch(self.partial_update_url, issued_on, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        status_data = {"status": "pending"}
        response = self.client.patch(self.partial_update_url, status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        issued_by = {"approved_by": self.test_user.username}
        response = self.client.patch(self.partial_update_url, issued_by, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        supplier_direct_advance = {"broker": self.broker.id}
        response = self.client.patch(self.partial_update_url, supplier_direct_advance, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_debit_note_supplier_direct_advance(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_debit_note_supplier_direct_advance(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("team_debit_note_supplier_direct_advance_retrieve",
                                   kwargs={"pk": self.debit_note_supplier_direct_advance.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_debit_note_supplier_direct_advance_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.debit_note_supplier_direct_advance.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_debit_note_supplier_direct_advance_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.debit_note_supplier_direct_advance.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_debit_note_supplier_direct_advance_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_debit_note_supplier_direct_advance_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_debit_note_supplier_direct_advance_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_debit_note_supplier_direct_advance_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
