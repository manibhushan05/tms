import json
from datetime import datetime
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import S3Upload
from supplier.models import Driver,Supplier,Vehicle
from fileupload.models import PODFile, VehicleFile, OwnerFile, DriverFile, ChequeFile, InvoiceReceiptFile
from restapi.helper_api import generate_random_string
from sme.models import Sme
from team.models import LrNumber, ManualBooking, Invoice


class FileUploadSetup(APITestCase):
    """
        Setup dummy data for File Upload Setup
    """

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.test_user = User.objects.create_user('testUser', 'test@example.com', 'testPassword')
        self.test_user = User.objects.create_user('admin', 'test@example.com', 'testPassword')
        self.login_data = self.client.post(self.login_url, {"username": "testUser", "password": "testPassword"}).content
        self.login_data = json.loads(self.login_data.decode('utf8'))
        self.token = "Token {}".format(self.login_data["token"])


        self.booking = mommy.make(ManualBooking)
        self.lr_number = mommy.make(LrNumber, _fill_optional=["lr_number"],booking=self.booking,datetime=datetime.now())
        self.s3_upload = mommy.make(S3Upload)
        self.driver = mommy.make(Driver)
        self.customer = mommy.make(Sme)
        self.invoice = mommy.make(Invoice, invoice_number=generate_random_string(N=20), date=datetime.now().date())

        self.pod_file = mommy.make(PODFile)
        self.vehicle = mommy.make(Vehicle)
        self.supplier = mommy.make(Supplier)
        self.vehicle_file = mommy.make(VehicleFile)
        self.owner_file = mommy.make(OwnerFile)
        self.driver_file = mommy.make(DriverFile)
        self.cheque_file = mommy.make(ChequeFile, _fill_optional=['s3_url'])
        self.customer = mommy.make(Sme)
        self.invoice_receipt_file = mommy.make(InvoiceReceiptFile, _fill_optional=['invoice_number'])


class PODFileTest(FileUploadSetup):
    """
        Test cases for POD File
    """

    def setUp(self):
        super().setUp()
        self.pod_file_data = {
            "s3_thumb_url": None,
            "verified_datetime": None,
            "deleted": False,
            "deleted_on": None,
            "verified_by": None,
            "lr_number": self.lr_number.id,
            "s3_upload": self.s3_upload.id,
            "serial": generate_random_string(20),
            "verified": False,
            "is_valid": False,
            "booking": self.booking.id,
            "s3_url": """
                                    https://aahodouments.s3.amazonaws.com/uploads/pod/hvlung7g745q7zrctqqaqa/pod-ah1907006-ibw694ez.jpg
                                """
        }
        self.minimum_valid_data = {
            "lr_number": self.lr_number.id,
            "s3_upload": self.s3_upload.id,
            "serial": generate_random_string(20),
            "verified": False,
            "is_valid": False,
            "booking": self.booking.id,
            "s3_url": """
                            https://aahodouments.s3.amazonaws.com/uploads/pod/hvlung7g745q7zrctqqaqa/pod-ah1907006-ibw694ez.jpg
                        """
        }
        self.create_url = reverse("file_upload_pod_file_create")
        self.update_url = reverse("file_upload_pod_file_update", kwargs={"pk": self.pod_file.id})
        self.partial_update_url = reverse("file_upload_pod_file_partial_update", kwargs={"pk": self.pod_file.id})
        self.retrieve_url = reverse("file_upload_pod_file_retrieve", kwargs={"pk": self.pod_file.id})
        self.filter_url = reverse("file_upload_pod_file_list")



    def test_upload_pod_file_with_full_valid_data(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "lr_number": self.lr_number.id,
                "file": image}
        response = self.client.post("/upload/pod-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_pod_file_with_invalid_token(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"] + "invalid" ,
                "lr_number": self.lr_number.id,
                "file": image}
        response = self.client.post("/upload/pod-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  #302 error (cant redirect to login page)

    def test_upload_pod_file_with_invalid_lr_number(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "lr_number": -12,
                "file": image}
        response = self.client.post("/upload/pod-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) #lr_number not found

        data = {"Authorization": self.login_data["token"],
                "lr_number": 0,
                "file": image}
        response = self.client.post("/upload/pod-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  #lr_number not found

        data = {"Authorization": self.login_data["token"],
                "lr_number": "invalid",
                "file": image}
        response = self.client.post("/upload/pod-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) #lr_number not found

        data = {"Authorization": self.login_data["token"],
                "lr_number": 1.23,
                "file": image}
        response = self.client.post("/upload/pod-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) #lr_number not found

    #
    # def test_create_pod_file_with_minimum_valid_data(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_create_pod_file_upload_with_valid_serail_number(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["serial"] = generate_random_string(1)
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["serial"] = generate_random_string(19)
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["serial"] = generate_random_string(20)
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_pod_file_upload_with_invalid_serail_number(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["serial"] = generate_random_string(21)
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["serial"] = None
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["serial"] = ""
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_pod_file_upload_with_valid_s3_url(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["s3_url"] = self.pod_file_data["s3_url"]
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_create_pod_file_upload_with_invalid_s3_url(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["s3_url"] = "https://invalid_s3_url"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["s3_url"] = None
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["s3_url"] = ""
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_pod_file_with_valid_verified_datetime(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["verified_datetime"] = datetime.now()
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["verified_datetime"] = str(datetime.now())
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["verified_datetime"] = None
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_create_pod_file_with_invalid_verified_datetime(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["verified_datetime"] = "invalid_format"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["verified_datetime"] = "2018-12-09:23:12:2020"
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_create_pod_file_with_valid_lr_number(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["lr_number"] = self.lr_number.id
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     data["lr_number"] = None
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_pod_file_with_invalid_lr_number(self):
    #     data = self.minimum_valid_data.copy()
    #
    #     data["lr_number"] = -12
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["lr_number"] = 0
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #


    # def test_create_pod_file_with_full_valid_data(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.post(self.create_url, self.pod_file_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_pod_file_invalid_data(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     data = self.pod_file_data.copy()
    #     data["verified"] = "WrongBooleanValue"
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data = self.pod_file_data.copy()
    #     data["deleted_on"] = "2016-10-27"
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data = self.pod_file_data.copy()
    #     data["s3_upload"] = -1
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["s3_upload"] = "invalidId"
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     data["s3_upload"] = self.s3_upload.id * 100
    #     response = self.client.post(self.create_url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_4_function_without_token(self):
        response = self.client.post(self.create_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.pod_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.pod_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.pod_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.pod_file_data.copy()
        data["created_by"] = self.test_user.id
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_update_pod_file_with_minimum_valid_date(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.put(self.update_url, self.minimum_valid_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
    # 
    # def test_update_pod_file_with_full_valid_data(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=self.token)
    #     response = self.client.put(self.update_url, self.pod_file_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_pod_file_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"serial": "RQT"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"booking": self.booking.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_pod_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_pod_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("file_upload_pod_file_retrieve",
                                   kwargs={"pk": self.pod_file.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_pod_file_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.pod_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pod_file_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.pod_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pod_file_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pod_file_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pod_file_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pod_file_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class VehicleFileTest(FileUploadSetup):
    """
        Test cases for Vehicle File
    """

    def setUp(self):
        super().setUp()
        self.vehicle_file_data = {
            "document_category": "REG",
            "s3_thumb_url": None,
            "deleted": False,
            "deleted_on": None,
            "s3_upload": self.s3_upload.id,
            "serial": "MFQPY51J",
            "verified": False,
            "is_valid": False,
            "booking": self.booking.id,
            "supplier_vehicle": self.vehicle.id,
            "s3_url": """
                       https://aahodouments.s3.amazonaws.com/uploads/pod/hvlung7g745q7zrctqqaqa/pod-ah1907006-ibw694ez.jpg
                      """
        }
        self.minimum_valid_data = {
            "document_category": "REG",
            "supplier_vehicle": self.vehicle.id,
            "s3_upload": self.s3_upload.id,
            "serial": "MFQPY51J",
            "verified": False,
            "is_valid": False,
            "s3_url": """
                            https://aahodouments.s3.amazonaws.com/uploads/pod/hvlung7g745q7zrctqqaqa/pod-ah1907006-ibw694ez.jpg
                        """
        }
        self.create_url = reverse("file_upload_vehicle_file_create")
        self.update_url = reverse("file_upload_vehicle_file_update", kwargs={"pk": self.vehicle_file.id})
        self.partial_update_url = reverse("file_upload_vehicle_file_partial_update",
                                          kwargs={"pk": self.vehicle_file.id})
        self.retrieve_url = reverse("file_upload_vehicle_file_retrieve", kwargs={"pk": self.vehicle_file.id})
        self.filter_url = reverse("file_upload_vehicle_file_list")


    def test_upload_vehicle_file_with_full_valid_data(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "document_category": "REG",
                "vehicle_number": self.vehicle.id,
                "file": image
                }
        response = self.client.post("/upload/vehicle-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_vehicle_file_with_invalid_token(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"] + "invalid",
                "document_category": "REG",
                "vehicle_number": self.vehicle.id,
                "file": image
                }
        response = self.client.post("/upload/vehicle-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  #302 error (cant redirect to login page)

    def test_upload_vehicle_file_with_invalid_vehicle(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")
        data = {"Authorization": self.login_data["token"],
                "document_category": "REG",
                "vehicle_number": -12,
                "file": image
                }
        response = self.client.post("/upload/vehicle-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # vehicle not found

        data = {"Authorization": self.login_data["token"],
                "document_category": "REG",
                "file": image
                }
        response = self.client.post("/upload/vehicle-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  #vehicle not provided

    def test_upload_vehicle_file_without_document_category(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")
        data = {"Authorization": self.login_data["token"],
                "vehicle_number": self.vehicle.id,
                "file": image
                }
        response = self.client.post("/upload/vehicle-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # document category not provided

    def test_upload_vehicle_file_without_any_file(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")
        data = {"Authorization": self.login_data["token"],
                "vehicle_number": self.vehicle.id,
                "document_category": "REG"
                }
        response = self.client.post("/upload/vehicle-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # file not provided


    def test_create_vehicle_file_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted to minimum data
    def test_create_vehicle_file_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted on to minimum data
    def test_create_vehicle_file_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding vehicle to minimum data
    def test_create_vehicle_file_with_valid_vehicle(self):
        data = self.minimum_valid_data.copy()
        data["supplier_vehicle"] = self.vehicle.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding driver to minimum data
    def test_create_vehicle_file_with_valid_driver(self):
        data = self.minimum_valid_data.copy()
        data["driver"] = self.driver.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_file_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_vehicle_file_with_duplicate_s3_url(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_file_data.copy()
        data["s3_url"] = self.vehicle_file.s3_url
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vehicle_file_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_file_data.copy()
        data["verified"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.vehicle_file_data.copy()
        data["document_category"] = "invalidCategory"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.vehicle_file_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.vehicle_file_data.copy()
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
        response = self.client.post(self.create_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.vehicle_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.vehicle_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.vehicle_file_data.copy()
        data["created_by"] = self.test_user.id
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_vehicle_file_with_minimum_valid_data(self):
        data = self.minimum_valid_data.copy()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_vehicle_file_with_full_valid_data(self):
        data = self.vehicle_file_data.copy()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_vehicle_file_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"serial": "RQT"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"supplier_vehicle": self.vehicle.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_vehicle_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_vehicle_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("file_upload_vehicle_file_retrieve",
                                   kwargs={"pk": self.vehicle_file.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_vehicle_file_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.vehicle_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_file_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.vehicle_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_file_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vehicle_file_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vehicle_file_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vehicle_file_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class OwnerFileTest(FileUploadSetup):
    """
        Test cases for Vehicle File
    """

    def setUp(self):
        super().setUp()
        self.owner_file_data = {
            "document_category": "PAN",
            "s3_thumb_url": None,
            "deleted": False,
            "deleted_on": None,
            "s3_upload": self.s3_upload.id,
            "serial": "MFQPY51J",
            "verified": False,
            "is_valid": False,
            "supplier": self.supplier.id,
            "s3_url": """
                       https://aahodouments.s3.amazonaws.com/uploads/pod/hvlung7g745q7zrctqqaqa/pod-ah1907006-ibw694ez.jpg
                      """
        }
        self.minimum_valid_data = {
            "document_category": "PAN",
            "supplier": self.supplier.id,
            "s3_upload": self.s3_upload.id,
            "serial": "MFQPY51J",
            "is_valid": False,
            "s3_url": """
                            https://aahodouments.s3.amazonaws.com/uploads/pod/hvlung7g745q7zrctqqaqa/pod-ah1907006-ibw694ez.jpg
                        """
        }
        self.create_url = reverse("file_upload_owner_file_create")
        self.update_url = reverse("file_upload_owner_file_update", kwargs={"pk": self.owner_file.id})
        self.partial_update_url = reverse("file_upload_owner_file_partial_update",
                                          kwargs={"pk": self.owner_file.id})
        self.retrieve_url = reverse("file_upload_owner_file_retrieve", kwargs={"pk": self.owner_file.id})
        self.filter_url = reverse("file_upload_owner_file_list")



    def test_upload_owner_file_with_full_valid_data(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "supplier": self.supplier.id,
                "document_category": "PAN",
                "file": image
                }
        response = self.client.post("/upload/supplier-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_owner_file_with_invalid_token(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"] + "invalid",
                "supplier": self.supplier.id,
                "document_category": "PAN",
                "file": image
                }
        response = self.client.post("/upload/supplier-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # 302 error (cant redirect to login page)

    def test_upload_owner_file_with_invalid_owner(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "supplier": -12,
                "document_category": "PAN",
                "file": image
                }
        response = self.client.post("/upload/supplier-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # owner not found

        data = {"Authorization": self.login_data["token"],
                "document_category": "PAN",
                "file": image
                }
        response = self.client.post("/upload/supplier-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # owner not provided

    def test_upload_owner_file_without_document_category(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "supplier": self.supplier.id,
                "file": image
                }
        response = self.client.post("/upload/supplier-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # document category not provided

    def test_upload_owner_file_without_any_file(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "supplier": self.supplier.id,
                "document_category": "PAN"
                }
        response = self.client.post("/upload/supplier-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # file not provided



    def test_create_owner_file_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Adding deleted field to minimum data
    def test_create_owner_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = False
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Adding deleted on field to minimum data
    def test_create_owner_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Adding verified field to minimum data
    def test_create_owner_with_valid_verified(self):
        data = self.minimum_valid_data.copy()
        data["verified"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_file_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_owner_file_with_duplicate_s3_url(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.owner_file_data.copy()
        data["s3_url"] = self.owner_file.s3_url
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_owner_file_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.owner_file_data.copy()
        data["verified"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.owner_file_data.copy()
        data["document_category"] = "invalidCategory"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.owner_file_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.owner_file_data.copy()
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
        response = self.client.post(self.create_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.owner_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.owner_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.owner_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.owner_file_data.copy()
        data["created_by"] = self.test_user.id
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_owner_file_with_minimum_valid_date(self):
        data = self.minimum_valid_data.copy()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_owner_file_with_full_valid_data(self):
        data = self.owner_file_data.copy()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_owner_file_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"serial": "RQT"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"supplier": self.supplier.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_owner_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_owner_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("file_upload_owner_file_retrieve",
                                   kwargs={"pk": self.owner_file.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_owner_file_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.owner_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_file_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.owner_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_file_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_file_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_file_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_file_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class DriverFileTest(FileUploadSetup):
    """
        Test cases for Driver File
    """

    def setUp(self):
        super().setUp()
        self.driver_file_data = {
            "document_category": "PAN",
            "s3_thumb_url": None,
            "deleted": False,
            "deleted_on": None,
            "s3_upload": self.s3_upload.id,
            "serial": "W7QDDG61",
            "verified": False,
            "is_valid": False,
            "supplier_driver": self.driver.id,
            "s3_url": """
                       https://aahodouments.s3.amazonaws.com/uploads/pod/hvlung7g745q7zrctqqaqa/pod-ah1907006-ibw694ez.jpg
                      """
        }
        self.minimum_valid_data = {
            "supplier_driver": self.driver.id,
            "s3_upload": self.s3_upload.id,
            "serial": "MFQPY51J",
            "is_valid": False,
            "verified": False,
            "s3_url": """
                            https://aahodouments.s3.amazonaws.com/uploads/pod/hvlung7g745q7zrctqqaqa/pod-ah1907006-ibw694ez.jpg
                        """
        }
        self.create_url = reverse("file_upload_driver_file_create")
        self.update_url = reverse("file_upload_driver_file_update", kwargs={"pk": self.driver_file.id})
        self.partial_update_url = reverse("file_upload_driver_file_partial_update",
                                          kwargs={"pk": self.driver_file.id})
        self.retrieve_url = reverse("file_upload_driver_file_retrieve", kwargs={"pk": self.driver_file.id})
        self.filter_url = reverse("file_upload_driver_file_list")

    def test_upload_driver_file_with_full_valid_data(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "driver": self.driver.id,
                "document_category": "PAN",
                "file": image
                }
        response = self.client.post("/upload/driver-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_driver_file_with_invalid_token(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"] + "invalid",
                "driver": self.driver.id,
                "document_category": "PAN",
                "file": image
                }
        response = self.client.post("/upload/driver-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # 302 error (cant redirect to login page)

    def test_upload_driver_file_with_invalid_driver(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "driver": -12,
                "document_category": "PAN",
                "file": image
                }
        response = self.client.post("/upload/driver-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # driver not found

        data = {"Authorization": self.login_data["token"],
                "document_category": "PAN",
                "file": image
                }
        response = self.client.post("/upload/driver-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # driver not provided

    def test_upload_driver_file_without_document_category(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "driver": self.driver.id,
                "file": image
                }
        response = self.client.post("/upload/driver-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # document category not provided


    def test_create_driver_file_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted field to minimum data
    def test_create_driver_file_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted on field to minimum data
    def test_create_driver_file_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding document_category field to minimum data
    def test_create_driver_file_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["document_category"] = 'DL'
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_file_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver_file_with_duplicate_s3_url(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.driver_file_data.copy()
        data["s3_url"] = self.driver_file.s3_url
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_file_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.driver_file_data.copy()
        data["verified"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.driver_file_data.copy()
        data["document_category"] = "invalidCategory"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.driver_file_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.driver_file_data.copy()
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
        response = self.client.post(self.create_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.driver_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.driver_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.driver_file_data.copy()
        data["created_by"] = self.test_user.id
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_driver_file_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_driver_file_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, self.driver_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_driver_file_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"serial": "RQT"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"supplier_driver": self.driver.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_driver_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_driver_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("file_upload_driver_file_retrieve",
                                   kwargs={"pk": self.driver_file.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_driver_file_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.driver_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Filter test cases
    def test_driver_file_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.driver_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_driver_file_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_driver_file_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_driver_file_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_driver_file_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ChequeFileTest(FileUploadSetup):
    """
        Test cases for Cheque File
    """

    def setUp(self):
        super().setUp()
        self.cheque_file_data = {

            "resolved_datetime": "2018-02-07T08:17:17.244223",
            "customer_name": "Centenary polytex pv. ltd.",
            "amount": 4300,
            "cheque_number": "073695",
            "cheque_date": "2018-02-02",
            "remarks": "MTF171128012/13",
            "resolved": True,
            "resolved_by": self.test_user.username,
            "customer": self.customer.id,
            "deleted": False,
            "deleted_on": None,
            "serial": "W7QDDG61",
            "is_valid": False,
            "s3_url": """
                       https://aahodouments.s3.amazonaws.com
                      """,
            "s3_upload": self.s3_upload.id

        }
        self.minimum_valid_data = {
            "s3_upload": self.s3_upload.id,
            "serial": "MFQPY51J",
            "is_valid": False,
            "customer_name": "Naruto",
            "cheque_number": "231223",
            "cheque_date": "2016-10-27"
        }
        self.create_url = reverse("file_upload_cheque_file_create")
        self.update_url = reverse("file_upload_cheque_file_update", kwargs={"pk": self.cheque_file.id})
        self.partial_update_url = reverse("file_upload_cheque_file_partial_update",
                                          kwargs={"pk": self.cheque_file.id})
        self.retrieve_url = reverse("file_upload_cheque_file_retrieve", kwargs={"pk": self.cheque_file.id})
        self.filter_url = reverse("file_upload_cheque_file_list")


    def test_upload_cheque_file_with_full_valid_data(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "customer_name": "aaho_customer",
                "amount": 10000,
                "cheque_date": "09-Dec-2018",
                "cheque_number": "231223",
                "file": image}
        response = self.client.post("/upload/cheque-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_cheque_file_with_invalid_token(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"] + "invalid",
                "customer_name": "aaho_customer",
                "amount": 10000,
                "cheque_date": "09-Dec-2018",
                "cheque_number": "231223",
                "file": image}
        response = self.client.post("/upload/cheque-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # 302 error (cant redirect to login page)

    def test_upload_cheque_file_with_invalid_cheque_number(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "customer_name": "aaho_customer",
                "amount": 10000,
                "cheque_date": "09-Dec-2018",
                "cheque_number": "2312230", #invalid cheque_number
                "file": image}
        response = self.client.post("/upload/cheque-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  #400 (invalid cheque number)

    def test_upload_cheque_file_with_invalid_amount(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "customer_name": "aaho_customer",
                "amount": "invalid123",
                "cheque_date": "29-Dec-2018",
                "cheque_number": "231223",
                "file": image}
        response = self.client.post("/upload/cheque-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # 400 (invalid amount)

    def test_upload_cheque_file_without_any_file(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "customer_name": "aaho_customer",
                "amount": 10000,
                "cheque_date": "29-Dec-2018",
                "cheque_number": "231223"
                }
        response = self.client.post("/upload/cheque-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # 400 (no file uploaded)


    def test_create_cheque_file_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding amount field to minimum data
    def test_create_cheque_file_with_valid_amount(self):
        data  = self.minimum_valid_data.copy()
        data["amount"] = 4300
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding remarks field to minimum data
    def test_create_cheque_file_with_valid_remarks(self):
        data = self.minimum_valid_data.copy()
        data["remarks"] = "any valid remark."
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding customer field to minimum data
    def test_create_cheque_file_with_valid_customer(self):
        data = self.minimum_valid_data.copy()
        data["customer"] = self.customer.id
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # adding deleted on field to minimum data
    def test_create_cheque_file_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_cheque_file_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_cheque_file_with_duplicate_s3_url(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.cheque_file_data.copy()
        data["s3_url"] = self.cheque_file.s3_url
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_cheque_file_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.cheque_file_data.copy()
        data["is_valid"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.cheque_file_data.copy()
        data["cheque_number"] = "12345"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["cheque_number"] = "1234567"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.cheque_file_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.cheque_file_data.copy()
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
        response = self.client.post(self.create_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.cheque_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.cheque_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.cheque_file_data.copy()
        data["created_by"] = self.test_user.id
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_cheque_file_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_cheque_file_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, self.cheque_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_cheque_file_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"serial": "RQT"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"s3_upload": self.s3_upload.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_cheque_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_cheque_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("file_upload_cheque_file_retrieve",
                                   kwargs={"pk": self.cheque_file.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_cheque_file_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.cheque_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cheque_file_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.cheque_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cheque_file_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cheque_file_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cheque_file_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cheque_file_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class InvoiceReceiptFileTest(FileUploadSetup):
    """
        Test cases for Invoice Receipt File
    """

    def setUp(self):
        super().setUp()
        self.invoice_receipt_file_data = {
            "invoice_number": self.invoice.invoice_number,
            "verified": False,
            "deleted": False,
            "deleted_on": None,
            "serial": "W7QDDG61",
            "is_valid": False,
            "s3_upload": self.s3_upload.id,
            "invoice_receipt": self.invoice.id,
            "invoice_sent_mode": "CR",
            "invoice_confirm_mode": "EM"
        }
        self.minimum_valid_data = {
            "s3_upload": self.s3_upload.id,
            "serial": "MFQPY51J",
            "is_valid": False,
            "verified": False,
            "invoice_number": self.invoice.invoice_number,
            "invoice_sent_mode": "CR",
            "invoice_confirm_mode": "EM"
        }
        self.create_url = reverse("file_upload_invoice_receipt_file_create")
        self.update_url = reverse("file_upload_invoice_receipt_file_update",
                                  kwargs={"pk": self.invoice_receipt_file.id})
        self.partial_update_url = reverse("file_upload_invoice_receipt_file_partial_update",
                                          kwargs={"pk": self.invoice_receipt_file.id})
        self.retrieve_url = reverse("file_upload_invoice_receipt_file_retrieve",
                                    kwargs={"pk": self.invoice_receipt_file.id})
        self.filter_url = reverse("file_upload_invoice_receipt_file_list")


    def test_upload_invoice_receipt_file_with_full_valid_data(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "invoice_number": self.invoice.invoice_number,
                "invoice_sent_mode": "CR",
                "file": image}
        response = self.client.post("/upload/invoice-receipt-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_invoice_receipt_file_with_invalid_token(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"] + "invalid",
                "invoice_number": self.invoice.invoice_number,
                "invoice_sent_mode": "CR",
                "file": image}
        response = self.client.post("/upload/invoice-receipt-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # 302 error (cant redirect to login page)

    def test_upload_invoice_receipt_file_with_invalid_invoice_number(self):
        image = SimpleUploadedFile("/static/aaho/images/images/index/Image4.jpg", b"file_content",
                                   content_type="image/jpeg")

        data = {"Authorization": self.login_data["token"],
                "invoice_number": -12,
                "invoice_sent_mode": "CR",
                "file": image}
        response = self.client.post("/upload/invoice-receipt-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # invoice number does not exist

        data = {"Authorization": self.login_data["token"],
                "invoice_number": 0,
                "invoice_sent_mode": "CR",
                "file": image}
        response = self.client.post("/upload/invoice-receipt-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # invoice number does not exist

        data = {"Authorization": self.login_data["token"],
                "invoice_number": 1.23,
                "invoice_sent_mode": "CR",
                "file": image}
        response = self.client.post("/upload/invoice-receipt-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # invoice number does not exist

        data = {"Authorization": self.login_data["token"],
                "invoice_number": "invalid",
                "invoice_sent_mode": "CR",
                "file": image}
        response = self.client.post("/upload/invoice-receipt-docs-create/", data, format='multipart', HTTP_ACCEPT='MIMEJSON')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # invoice number does not exist


    def test_create_invoice_receipt_file_with_minimum_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted field to minimum data
    def test_create_invoice_receipt_file_with_valid_deleted(self):
        data = self.minimum_valid_data.copy()
        data["deleted"] = True
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #adding deleted on field to minimum data
    def test_create_invoice_receipt_file_with_valid_deleted_on(self):
        data = self.minimum_valid_data.copy()
        data["deleted_on"] = datetime.now()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_receipt_file_with_full_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.create_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invoice_receipt_file_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.invoice_receipt_file_data.copy()
        data["is_valid"] = "WrongBooleanValue"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.invoice_receipt_file_data.copy()
        data["deleted_on"] = "2016-10-27"
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.invoice_receipt_file_data.copy()
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
        response = self.client.post(self.create_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.invoice_receipt_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_4_functions_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token + "invalidToken")
        response = self.client.post(self.create_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(self.update_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.partial_update_url, self.invoice_receipt_file_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.create_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.create_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.create_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.update_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.update_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.update_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.partial_update_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.partial_update_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.get(self.partial_update_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_function_with_invalid_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(self.retrieve_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(self.retrieve_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(self.retrieve_url, self.invoice_receipt_file_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test to change field such as created by which are immutable
    def test_try_to_change_immutable_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = self.invoice_receipt_file_data.copy()
        data["created_by"] = self.test_user.id
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invoice_receipt_file_with_minimum_valid_date(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, self.minimum_valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_invoice_receipt_file_with_full_valid_data(self):
        data = self.minimum_valid_data.copy()
        data["invoice_number"] = "IN1234243"
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_partial_update_invoice_receipt_file_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {"serial": "RQT"}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        data = {"s3_upload": self.s3_upload.id}
        response = self.client.patch(self.partial_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_existing_invoice_receipt_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_invoice_receipt_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        bad_retrieve_url = reverse("file_upload_invoice_receipt_file_retrieve",
                                   kwargs={"pk": self.invoice_receipt_file.id * 1000})
        response = self.client.get(bad_retrieve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filter test cases
    def test_invoice_receipt_file_filter_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = "{}?{}".format(self.filter_url, "id={}".format(self.invoice_receipt_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoice_receipt_file_search_working(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        url = "{}?{}".format(self.filter_url, "search={}".format(self.invoice_receipt_file.id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoice_receipt_no_header(self):
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoice_receipt_wrong_token(self):
        token = "806fa0efd3ce26fe080f65da4ad5a137e1d056ff"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoice_receipt_expired_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoice_receipt_wrong_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(self.filter_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

