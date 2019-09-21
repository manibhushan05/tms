from datetime import datetime, timedelta

from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics, filters
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api import s3util
from api.models import S3Upload
from api.utils import format_date
from api.utils import get_or_none
from broker.models import BrokerVehicle, Broker
from driver.models import Driver, DriverAppUser, GPSLogNew, OTP, GPSDevice, GPSDeviceLog, TracknovateGPSDevice, \
    TracknovateGPSDeviceLog, WaytrackerGPSDevice, WaytrackerGPSDeviceLog, TempoGoGPSDevice, TempoGoGPSDeviceLog, \
    SecuGPSDevice, SecuGPSDeviceLog, MahindraGPSDevice, MahindraGPSDeviceLog, BharatGPSTrackerLog, GPSDeviceProvider
from fileupload.models import DriverFile
from fileupload.views import get_new_serial
from fms.views import validate_url
from owner.models import Vehicle as OwnerVehicle
from owner.vehicle_util import compare_format
from restapi.filter.driver import DriverFilter, GPSDeviceFilter, GPSDeviceProviderFilter
from restapi.helper_api import error_response, success_response, is_fms_user
from restapi.search import CustomSearch
from restapi.serializers.driver import DriverSerializer, DriverAppUserSerializer, GPSLogNewSerializer, OTPSerializer, \
    GPSDeviceSerializer, GPSDeviceLogSerializer, TracknovateGPSDeviceSerializer, TracknovateGPSDeviceLogSerializer, \
    WaytrackerGPSDeviceSerializer, WaytrackerGPSDeviceLogSerializer, TempoGoGPSDeviceSerializer, \
    TempoGoGPSDeviceLogSerializer, SecuGPSDeviceSerializer, SecuGPSDeviceLogSerializer, MahindraGPSDeviceSerializer, \
    MahindraGPSDeviceLogSerializer, FMSDriverSerializer, GPSDeviceProviderSerializer
from restapi.service.driver import parse_driver_docs
from restapi.utils import get_or_none
from supplier.models import Supplier, Vehicle
from utils.managements import get_deleted_objects


class DriverListView(generics.ListAPIView):
    serializer_class = DriverSerializer

    queryset = Driver.objects.all().exclude(deleted=True).order_by('-id')
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = DriverFilter
    ordering_fields = ('id',)
    search_fields = (
        'id', 'name', 'address__line1', 'phone', 'alt_phone', 'driving_licence_number',
        'driving_licence_location',
        'driving_licence_validity', 'taxation_id__service_tax_number', 'account_details__account_number',
        'account_details__bank', 'account_details__ifsc', 'route',
        'priority_level', 'created_by__username', 'created_on')

    def get_serializer_class(self):
        if is_fms_user(user=self.request.user):
            return FMSDriverSerializer
        return DriverSerializer

    def get_queryset(self):
        if is_fms_user(user=self.request.user):
            broker = Broker.objects.get(name=self.request.user)
            bv_id = broker.broker_vehicle.exclude(deleted=True).values_list('vehicle_id', flat=True)
            drivers_id = OwnerVehicle.objects.filter(id__in=bv_id).exclude(driver=None).exclude(
                deleted=True).values_list(
                'driver__id')
            return Driver.objects.filter(id__in=drivers_id)
        return Driver.objects.exclude(deleted=True)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "Broker List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class DriverPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/register-driver.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class DriverViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Driver
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        driver_serializer = DriverSerializer(data=request.data)
        if driver_serializer.is_valid():
            driver_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Driver Created",
                "data": driver_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Driver not Created",
            "data": driver_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def create_bank_account(self, request, pk=None):
        return success_response(status=status.HTTP_201_CREATED, msg="", data={})

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        driver = get_or_none(Driver, id=pk)
        if not isinstance(driver, Driver):
            return Response({"error": "Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)
        driver_serializer = DriverSerializer(instance=driver, data=request.data)
        if driver_serializer.is_valid():
            driver_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Driver Updated",
                "data": driver_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Driver not Updated",
            "data": driver_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def fms_partial_update(self, request, pk=None):
        data = request.data
        parsed_driver_docs = parse_driver_docs(data=request.data)
        driver = get_or_none(Driver, id=pk)
        if isinstance(driver, Driver):
            driver_serializer = DriverSerializer(instance=driver, data=parsed_driver_docs, partial=True)
            if driver_serializer.is_valid():
                driver = driver_serializer.save()
            else:
                return error_response(msg='Something went wrong, Please try later or drop mail at info@aaho.in',
                                      data=driver_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        doc_key = 'pan_doc'
        if doc_key in data and data[doc_key].get('url'):
            if not DriverFile.objects.filter(
                    Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                        s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                            data[doc_key].get('thumb_url')) else None)).exists():
                if S3Upload.objects.filter(uuid=data[doc_key].get('uuid', None)).exists():
                    s3_upload = S3Upload.objects.filter(uuid=data[doc_key].get('uuid', None)).last()
                else:
                    s3_upload = s3util.get_or_create_s3_upload(
                        bucket=data[doc_key].get('bucketName', None),
                        folder=data[doc_key].get('folderName', None),
                        filename=data[doc_key].get('fileName', None),
                        verified=False,
                        is_valid=False,
                        uuid=data[doc_key].get('uuid', None),
                    )
                DriverFile.objects.create(
                    uploaded_by=request.user,
                    driver=driver,
                    document_category='PAN',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(DriverFile, driver=driver),
                    s3_upload=s3_upload,
                )

        doc_key = 'dl_doc'
        if doc_key in data and data[doc_key].get('url'):
            if not DriverFile.objects.filter(
                    Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                        s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                            data[doc_key].get('thumb_url')) else None)).exists():
                if S3Upload.objects.filter(uuid=data[doc_key].get('uuid', None)).exists():
                    s3_upload = S3Upload.objects.filter(uuid=data[doc_key].get('uuid', None)).last()
                else:
                    s3_upload = s3util.get_or_create_s3_upload(
                        bucket=data[doc_key].get('bucketName', None),
                        folder=data[doc_key].get('folderName', None),
                        filename=data[doc_key].get('fileName', None),
                        verified=False,
                        is_valid=False,
                        uuid=data[doc_key].get('uuid', None),
                    )
                DriverFile.objects.create(
                    uploaded_by=request.user,
                    driver=driver,
                    document_category='DL',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(DriverFile, driver=driver),
                    s3_upload=s3_upload,
                )

        driver_serializer = FMSDriverSerializer(driver)
        return success_response(msg='driver details %s' % ('edited' if pk else 'saved'),
                                data=driver_serializer.data, status=status.HTTP_202_ACCEPTED)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        driver = get_or_none(Driver, id=pk)
        if not isinstance(driver, Driver):
            return Response({"error": "Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)
        driver_serializer = DriverSerializer(instance=driver, data=request.data, partial=True)
        if driver_serializer.is_valid():
            driver_serializer.save()
            return success_response(data=driver_serializer.data, msg='Driver updated', status=status.HTTP_202_ACCEPTED)
        return error_response(
            data=driver_serializer.errors, msg='Something went wrong', status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        driver = get_or_none(Driver, id=pk)
        if not isinstance(driver, Driver):
            return Response({"error": "Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)
        driver_serializer = DriverSerializer(driver)
        if is_fms_user(user=request.user):
            driver_serializer = FMSDriverSerializer(driver)
        return Response(driver_serializer.data, template_name='team/registrations/driver-update.html',
                        status=status.HTTP_200_OK)

    def change_deleted(self, objs):
        for obj in objs:
            if isinstance(obj, list):
                self.change_deleted(obj)
            else:
                if "deleted" in dir(obj):
                    if not obj.deleted:
                        obj.deleted = True
                        obj.deleted_on = datetime.now()
                        obj.save()
                else:

                    for field in obj._meta.get_fields():
                        if field.is_relation:
                            related_object = field.related_model.objects.get(id=field.value_from_object(obj))
                            if not related_object.deleted:
                                related_object.deleted = True
                                related_object.deleted_on = datetime.now()
                                related_object.save()

    def soft_destroy(self, request, pk=None):
        driver = get_or_none(Driver, id=pk)
        if not isinstance(driver, Driver):
            return Response({"error": "Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)

        to_delete, model_count, protected = get_deleted_objects(driver)
        self.change_deleted(to_delete)
        driver_serializer = DriverSerializer(driver)
        return Response(driver_serializer.data, status=status.HTTP_200_OK)


class DriverAppUserViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Driver App User
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        driver_app_user_serializer = DriverAppUserSerializer(data=request.data)
        if driver_app_user_serializer.is_valid():
            driver_app_user_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Driver App User Created",
                "data": driver_app_user_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Driver App User not Created",
            "data": driver_app_user_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        driver_app_user = get_or_none(DriverAppUser, id=pk)
        if not isinstance(driver_app_user, DriverAppUser):
            return Response({"error": "Driver App User MahindraGPSDevice does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        driver_app_user_serializer = DriverAppUserSerializer(driver_app_user, data=request.data)

        if driver_app_user_serializer.is_valid():
            driver_app_user_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Driver App User Updated",
                "data": driver_app_user_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Driver App User not Updated",
            "data": driver_app_user_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        driver_app_user = get_or_none(DriverAppUser, id=pk)
        if not isinstance(driver_app_user, DriverAppUser):
            return Response({"error": "Driver App User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        driver_app_user_serializer = DriverAppUserSerializer(
            instance=driver_app_user,
            data=request.data,
            partial=True
        )

        if driver_app_user_serializer.is_valid():
            driver_app_user_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Driver App User Updated",
                "data": driver_app_user_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Driver App User not Updated",
            "data": driver_app_user_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        driver_app_user = get_or_none(DriverAppUser, id=pk)
        if isinstance(driver_app_user, DriverAppUser):
            driver_app_user_serializer = DriverAppUserSerializer(driver_app_user)
            return Response(driver_app_user_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Driver App User does not exist"}, status=status.HTTP_404_NOT_FOUND)


class GPSLogNewViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Driver App User
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        gps_log_new_serializer = GPSLogNewSerializer(data=request.data)
        if gps_log_new_serializer.is_valid():
            gps_log_new_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "GPS Log New Created",
                "data": gps_log_new_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "GPS Log New not Created",
            "data": gps_log_new_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        gps_log_new = get_or_none(GPSLogNew, id=pk)
        if not isinstance(gps_log_new, GPSLogNew):
            return Response({"error": "GPS Log New does not exist"}, status=status.HTTP_404_NOT_FOUND)
        gps_log_new_serializer = GPSLogNewSerializer(gps_log_new, data=request.data)

        if gps_log_new_serializer.is_valid():
            gps_log_new_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "GPS Log New Updated",
                "data": gps_log_new_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "GPS Log New not Updated",
            "data": gps_log_new_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        gps_log_new = get_or_none(GPSLogNew, id=pk)
        if not isinstance(gps_log_new, GPSLogNew):
            return Response({"error": "GPS Log New does not exist"}, status=status.HTTP_404_NOT_FOUND)
        gps_log_new_serializer = GPSLogNewSerializer(
            instance=gps_log_new,
            data=request.data,
            partial=True
        )

        if gps_log_new_serializer.is_valid():
            gps_log_new_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "GPS Log New Updated",
                "data": gps_log_new_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "GPS Log New not Updated",
            "data": gps_log_new_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        gps_log_new = get_or_none(GPSLogNew, id=pk)
        if isinstance(gps_log_new, GPSLogNew):
            gps_log_new_serializer = GPSLogNewSerializer(gps_log_new)
            return Response(gps_log_new_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "GPS Log New does not exist"}, status=status.HTTP_404_NOT_FOUND)


class OTPViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Driver App User
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        otp_serializer = OTPSerializer(data=request.data)
        if otp_serializer.is_valid():
            otp_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "OTP Created",
                "data": otp_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "OTP not Created",
            "data": otp_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        otp = get_or_none(OTP, id=pk)
        if not isinstance(otp, OTP):
            return Response({"error": "OTP does not exist"}, status=status.HTTP_404_NOT_FOUND)
        otp_serializer = OTPSerializer(otp, data=request.data)

        if otp_serializer.is_valid():
            otp_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "OTP Updated",
                "data": otp_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "OTP not Updated",
            "data": otp_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        otp = get_or_none(OTP, id=pk)
        if not isinstance(otp, OTP):
            return Response({"error": "OTP does not exist"}, status=status.HTTP_404_NOT_FOUND)
        otp_serializer = OTPSerializer(
            instance=otp,
            data=request.data,
            partial=True
        )

        if otp_serializer.is_valid():
            otp_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "OTP Updated",
                "data": otp_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "OTP not Updated",
            "data": otp_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        otp = get_or_none(OTP, id=pk)
        if isinstance(otp, OTP):
            otp_serializer = OTPSerializer(otp)
            return Response(otp_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "OTP does not exist"}, status=status.HTTP_404_NOT_FOUND)


class GPSDeviceProviderListView(generics.ListAPIView):
    serializer_class = GPSDeviceProviderSerializer
    search_fields = ('id', 'name')
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('-id',)
    filter_class = GPSDeviceProviderFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "GPS Devices Provider List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)

    def get_queryset(self):
        return GPSDeviceProvider.objects.all()


class GPSDeviceListView(generics.ListAPIView):
    serializer_class = GPSDeviceSerializer
    search_fields = ('id', 'device_id', 'imei', 'address', 'vehicle__vehicle_number', 'driver_name', 'driver_number')
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('-id',)
    filter_class = GPSDeviceFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "GPS Devices List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)

    def get_queryset(self):
        return GPSDevice.objects.exclude(deleted=True).order_by('-location_time')


class GPSDeviceViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of GPS Device
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        gps_device_serializer = GPSDeviceSerializer(data=request.data)
        if gps_device_serializer.is_valid():
            gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "GPS Device Created",
                "data": gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "GPS Device not Created",
            "data": gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        gps_device = get_or_none(GPSDevice, id=pk)
        if not isinstance(gps_device, GPSDevice):
            return Response({"error": "GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        gps_device_serializer = GPSDeviceSerializer(gps_device, data=request.data)

        if gps_device_serializer.is_valid():
            gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "GPS Device Updated",
                "data": gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "GPS Device not Updated",
            "data": gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        gps_device = get_or_none(GPSDevice, id=pk)
        if not isinstance(gps_device, GPSDevice):
            return Response({"error": "GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        gps_device_serializer = GPSDeviceSerializer(
            instance=gps_device,
            data=request.data,
            partial=True
        )

        if gps_device_serializer.is_valid():
            gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "GPS Device Updated",
                "data": gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "GPS Device not Updated",
            "data": gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        gps_device = get_or_none(GPSDevice, id=pk)
        if isinstance(gps_device, GPSDevice):
            gps_device_serializer = GPSDeviceSerializer(gps_device)
            return Response(gps_device_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)


class GPSDeviceLogViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of GPS device Log
    """

    def create(self, request):
        gps_device_log_serializer = GPSDeviceLogSerializer(data=request.data)
        if gps_device_log_serializer.is_valid():
            gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "GPS Device Log Created",
                "data": gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "GPS Device Log not Created",
            "data": gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):

        gps_device_log = get_or_none(GPSDeviceLog, id=pk)
        if not isinstance(gps_device_log, GPSDeviceLog):
            return Response({"error": "GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        gps_device_log_serializer = GPSDeviceLogSerializer(gps_device_log, data=request.data)

        if gps_device_log_serializer.is_valid():
            gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "GPS Device Log Updated",
                "data": gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "GPS Device Log not Updated",
            "data": gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        gps_device_log = get_or_none(GPSDeviceLog, id=pk)
        if not isinstance(gps_device_log, GPSDeviceLog):
            return Response({"error": "GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        gps_device_log_serializer = GPSDeviceLogSerializer(
            instance=gps_device_log,
            data=request.data,
            partial=True
        )

        if gps_device_log_serializer.is_valid():
            gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "GPS Device Log Updated",
                "data": gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "GPS Device Log not Updated",
            "data": gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        gps_device_log = get_or_none(GPSDeviceLog, id=pk)
        if isinstance(gps_device_log, GPSDeviceLog):
            gps_device_log_serializer = GPSDeviceLogSerializer(gps_device_log)
            return Response(gps_device_log_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)


class TracknovateGPSDeviceViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Tracknovate GPS Device
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        tracknovate_gps_device_serializer = TracknovateGPSDeviceSerializer(data=request.data)
        if tracknovate_gps_device_serializer.is_valid():
            tracknovate_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Tracknovate GPS Device Created",
                "data": tracknovate_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tracknovate GPS Device not Created",
            "data": tracknovate_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        tracknovate_gps_device = get_or_none(TracknovateGPSDevice, id=pk)
        if not isinstance(tracknovate_gps_device, TracknovateGPSDevice):
            return Response({"error": "Tracknovate GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        tracknovate_gps_device_serializer = TracknovateGPSDeviceSerializer(tracknovate_gps_device, data=request.data)

        if tracknovate_gps_device_serializer.is_valid():
            tracknovate_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Tracknovate GPS Device Updated",
                "data": tracknovate_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tracknovate GPS Device not Updated",
            "data": tracknovate_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        tracknovate_gps_device = get_or_none(TracknovateGPSDevice, id=pk)
        if not isinstance(tracknovate_gps_device, TracknovateGPSDevice):
            return Response({"error": "Tracknovate GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        tracknovate_gps_device_serializer = TracknovateGPSDeviceSerializer(
            instance=tracknovate_gps_device,
            data=request.data,
            partial=True
        )

        if tracknovate_gps_device_serializer.is_valid():
            tracknovate_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Tracknovate GPS Device Updated",
                "data": tracknovate_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tracknovate GPS Device not Updated",
            "data": tracknovate_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        tracknovate_gps_device = get_or_none(TracknovateGPSDevice, id=pk)
        if isinstance(tracknovate_gps_device, TracknovateGPSDevice):
            tracknovate_gps_device_serializer = TracknovateGPSDeviceSerializer(tracknovate_gps_device)
            return Response(tracknovate_gps_device_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Tracknovate GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)


class TracknovateGPSDeviceLogViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Tracknovate GPS Device Log
    """

    def create(self, request):
        tracknovate_gps_device_log_serializer = TracknovateGPSDeviceLogSerializer(data=request.data)
        if tracknovate_gps_device_log_serializer.is_valid():
            tracknovate_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Tracknovate GPS Device Log Created",
                "data": tracknovate_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tracknovate GPS Device Log not Created",
            "data": tracknovate_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):

        tracknovate_gps_device_log = get_or_none(TracknovateGPSDeviceLog, id=pk)
        if not isinstance(tracknovate_gps_device_log, TracknovateGPSDeviceLog):
            return Response({"error": "Tracknovate GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        tracknovate_gps_device_log_serializer = TracknovateGPSDeviceLogSerializer(tracknovate_gps_device_log,
                                                                                  data=request.data)

        if tracknovate_gps_device_log_serializer.is_valid():
            tracknovate_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Tracknovate GPS Device Log Updated",
                "data": tracknovate_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tracknovate GPS Device Log not Updated",
            "data": tracknovate_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        tracknovate_gps_device_log = get_or_none(TracknovateGPSDeviceLog, id=pk)
        if not isinstance(tracknovate_gps_device_log, TracknovateGPSDeviceLog):
            return Response({"error": "Tracknovate GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        tracknovate_gps_device_log_serializer = TracknovateGPSDeviceLogSerializer(
            instance=tracknovate_gps_device_log,
            data=request.data,
            partial=True
        )

        if tracknovate_gps_device_log_serializer.is_valid():
            tracknovate_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Tracknovate GPS Device Log Updated",
                "data": tracknovate_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tracknovate GPS Device Log not Updated",
            "data": tracknovate_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        tracknovate_gps_device_log = get_or_none(TracknovateGPSDeviceLog, id=pk)
        if isinstance(tracknovate_gps_device_log, TracknovateGPSDeviceLog):
            tracknovate_gps_device_log_serializer = TracknovateGPSDeviceLogSerializer(tracknovate_gps_device_log)
            return Response(tracknovate_gps_device_log_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Tracknovate GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)


class WaytrackerGPSDeviceViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Waytracker GPS Device
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        waytracker_gps_device_serializer = WaytrackerGPSDeviceSerializer(data=request.data)
        if waytracker_gps_device_serializer.is_valid():
            waytracker_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Waytracker GPS Device Created",
                "data": waytracker_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Waytracker GPS Device not Created",
            "data": waytracker_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        waytracker_gps_device = get_or_none(WaytrackerGPSDevice, id=pk)
        if not isinstance(waytracker_gps_device, WaytrackerGPSDevice):
            return Response({"error": "Waytracker GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        waytracker_gps_device_serializer = WaytrackerGPSDeviceSerializer(waytracker_gps_device, data=request.data)

        if waytracker_gps_device_serializer.is_valid():
            waytracker_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Waytracker GPS Device Updated",
                "data": waytracker_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Waytracker GPS Device not Updated",
            "data": waytracker_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        waytracker_gps_device = get_or_none(WaytrackerGPSDevice, id=pk)
        if not isinstance(waytracker_gps_device, WaytrackerGPSDevice):
            return Response({"error": "Waytracker GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        waytracker_gps_device_serializer = WaytrackerGPSDeviceSerializer(
            instance=waytracker_gps_device,
            data=request.data,
            partial=True
        )

        if waytracker_gps_device_serializer.is_valid():
            waytracker_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Waytracker GPS Device Updated",
                "data": waytracker_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Waytracker GPS Device not Updated",
            "data": waytracker_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        waytracker_gps_device = get_or_none(WaytrackerGPSDevice, id=pk)
        if isinstance(waytracker_gps_device, WaytrackerGPSDevice):
            waytracker_gps_device_serializer = WaytrackerGPSDeviceSerializer(waytracker_gps_device)
            return Response(waytracker_gps_device_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Waytracker GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)


class WaytrackerGPSDeviceLogViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Waytracker GPS Device Log
    """

    def create(self, request):
        waytracker_gps_device_serializer = WaytrackerGPSDeviceLogSerializer(data=request.data)
        if waytracker_gps_device_serializer.is_valid():
            waytracker_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Waytracker GPS Device Log Created",
                "data": waytracker_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Waytracker GPS Device Log not Updated",
            "data": waytracker_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):

        waytracker_gps_device = get_or_none(WaytrackerGPSDeviceLog, id=pk)
        if not isinstance(waytracker_gps_device, WaytrackerGPSDeviceLog):
            return Response({"error": "Waytracker GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        waytracker_gps_device_serializer = WaytrackerGPSDeviceLogSerializer(waytracker_gps_device, data=request.data)

        if waytracker_gps_device_serializer.is_valid():
            waytracker_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Waytracker GPS Device Log Updated",
                "data": waytracker_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Waytracker GPS Device Log not Updated",
            "data": waytracker_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        waytracker_gps_device = get_or_none(WaytrackerGPSDeviceLog, id=pk)
        if not isinstance(waytracker_gps_device, WaytrackerGPSDeviceLog):
            return Response({"error": "Waytracker GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        waytracker_gps_device_serializer = WaytrackerGPSDeviceLogSerializer(
            instance=waytracker_gps_device,
            data=request.data,
            partial=True
        )

        if waytracker_gps_device_serializer.is_valid():
            waytracker_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Waytracker GPS Device Log Updated",
                "data": waytracker_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Waytracker GPS Device Log not Updated",
            "data": waytracker_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        waytracker_gps_device = get_or_none(WaytrackerGPSDeviceLog, id=pk)
        if isinstance(waytracker_gps_device, WaytrackerGPSDeviceLog):
            waytracker_gps_device_serializer = WaytrackerGPSDeviceLogSerializer(waytracker_gps_device)
            return Response(waytracker_gps_device_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Waytracker GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)


class TempoGoGPSDeviceViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Tempo Go GPS Device
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        tempo_go_gps_device_serializer = TempoGoGPSDeviceSerializer(data=request.data)
        if tempo_go_gps_device_serializer.is_valid():
            tempo_go_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Tempo Go GPS Device Created",
                "data": tempo_go_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tempo Go GPS Device not Created",
            "data": tempo_go_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        tempo_go_gps_device = get_or_none(TempoGoGPSDevice, id=pk)
        if not isinstance(tempo_go_gps_device, TempoGoGPSDevice):
            return Response({"error": "Tempo Go GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        tempo_go_gps_device_serializer = TempoGoGPSDeviceSerializer(tempo_go_gps_device, data=request.data)

        if tempo_go_gps_device_serializer.is_valid():
            tempo_go_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Tempo Go GPS Device Updated",
                "data": tempo_go_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tempo Go GPS Device not Updated",
            "data": tempo_go_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        tempo_go_gps_device = get_or_none(TempoGoGPSDevice, id=pk)
        if not isinstance(tempo_go_gps_device, TempoGoGPSDevice):
            return Response({"error": "Tempo Go GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        tempo_go_gps_device_serializer = TempoGoGPSDeviceSerializer(
            instance=tempo_go_gps_device,
            data=request.data,
            partial=True
        )

        if tempo_go_gps_device_serializer.is_valid():
            tempo_go_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Tempo Go GPS Device Updated",
                "data": tempo_go_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tempo Go GPS Device not Updated",
            "data": tempo_go_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        tempo_go_gps_device = get_or_none(TempoGoGPSDevice, id=pk)
        if isinstance(tempo_go_gps_device, TempoGoGPSDevice):
            tempo_go_gps_device_serializer = TempoGoGPSDeviceSerializer(tempo_go_gps_device)
            return Response(tempo_go_gps_device_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Tempo Go GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)


class TempoGoGPSDeviceLogViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Tempo Go GPS Device Log
    """

    def create(self, request):
        tempo_go_gps_device_log_serializer = TempoGoGPSDeviceLogSerializer(data=request.data)
        if tempo_go_gps_device_log_serializer.is_valid():
            tempo_go_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Tempo Go GPS Device Log Created",
                "data": tempo_go_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tempo Go GPS Device Log not Created",
            "data": tempo_go_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):

        tempo_go_gps_device_log = get_or_none(TempoGoGPSDeviceLog, id=pk)
        if not isinstance(tempo_go_gps_device_log, TempoGoGPSDeviceLog):
            return Response({"error": "Tempo Go GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        tempo_go_gps_device_log_serializer = TempoGoGPSDeviceLogSerializer(tempo_go_gps_device_log, data=request.data)

        if tempo_go_gps_device_log_serializer.is_valid():
            tempo_go_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Tempo Go GPS Device Log Updated",
                "data": tempo_go_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tempo Go GPS Device Log not Updated",
            "data": tempo_go_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        tempo_go_gps_device_log = get_or_none(TempoGoGPSDeviceLog, id=pk)
        if not isinstance(tempo_go_gps_device_log, TempoGoGPSDeviceLog):
            return Response({"error": "Tempo Go GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        tempo_go_gps_device_log_serializer = TempoGoGPSDeviceLogSerializer(
            instance=tempo_go_gps_device_log,
            data=request.data,
            partial=True
        )

        if tempo_go_gps_device_log_serializer.is_valid():
            tempo_go_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Tempo Go GPS Device Log Updated",
                "data": tempo_go_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Tempo Go GPS Device Log not Updated",
            "data": tempo_go_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        tempo_go_gps_device_log = get_or_none(TempoGoGPSDeviceLog, id=pk)
        if isinstance(tempo_go_gps_device_log, TempoGoGPSDeviceLog):
            tempo_go_gps_device_log_serializer = TempoGoGPSDeviceLogSerializer(tempo_go_gps_device_log)
            return Response(tempo_go_gps_device_log_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Tempo Go GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)


class SecuGPSDeviceViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Secu GPS Device
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        secu_gps_device_serializer = SecuGPSDeviceSerializer(data=request.data)
        if secu_gps_device_serializer.is_valid():
            secu_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Secu GPS Device Created",
                "data": secu_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Secu GPS Device not Created",
            "data": secu_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        secu_gps_device = get_or_none(SecuGPSDevice, id=pk)
        if not isinstance(secu_gps_device, SecuGPSDevice):
            return Response({"error": "Secu GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        secu_gps_device_serializer = SecuGPSDeviceSerializer(secu_gps_device, data=request.data)

        if secu_gps_device_serializer.is_valid():
            secu_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Secu GPS Device Updated",
                "data": secu_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Secu GPS Device not Updated",
            "data": secu_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        secu_gps_device = get_or_none(SecuGPSDevice, id=pk)
        if not isinstance(secu_gps_device, SecuGPSDevice):
            return Response({"error": "Secu GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        secu_gps_device_serializer = SecuGPSDeviceSerializer(
            instance=secu_gps_device,
            data=request.data,
            partial=True
        )

        if secu_gps_device_serializer.is_valid():
            secu_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Secu GPS Device Updated",
                "data": secu_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Secu GPS Device not Updated",
            "data": secu_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        secu_gps_device = get_or_none(SecuGPSDevice, id=pk)
        if isinstance(secu_gps_device, SecuGPSDevice):
            secu_gps_device_serializer = SecuGPSDeviceSerializer(secu_gps_device)
            return Response(secu_gps_device_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Secu GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)


class SecuGPSDeviceLogViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Secu GPS Device Log
    """

    def create(self, request):
        secu_gps_device_log_serializer = SecuGPSDeviceLogSerializer(data=request.data)
        if secu_gps_device_log_serializer.is_valid():
            secu_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Secu GPS Device Log Created",
                "data": secu_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Secu GPS Device Log not Created",
            "data": secu_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):

        secu_gps_device_log = get_or_none(SecuGPSDeviceLog, id=pk)
        if not isinstance(secu_gps_device_log, SecuGPSDeviceLog):
            return Response({"error": "Secu GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        secu_gps_device_log_serializer = SecuGPSDeviceLogSerializer(secu_gps_device_log, data=request.data)

        if secu_gps_device_log_serializer.is_valid():
            secu_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Secu GPS Device Log Updated",
                "data": secu_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Secu GPS Device Log not Updated",
            "data": secu_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        secu_gps_device_log = get_or_none(SecuGPSDeviceLog, id=pk)
        if not isinstance(secu_gps_device_log, SecuGPSDeviceLog):
            return Response({"error": "Secu GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        secu_gps_device_log_serializer = SecuGPSDeviceLogSerializer(
            instance=secu_gps_device_log,
            data=request.data,
            partial=True
        )

        if secu_gps_device_log_serializer.is_valid():
            secu_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Secu GPS Device Log Updated",
                "data": secu_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Secu GPS Device Log not Updated",
            "data": secu_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        secu_gps_device_log = get_or_none(SecuGPSDeviceLog, id=pk)
        if isinstance(secu_gps_device_log, SecuGPSDeviceLog):
            secu_gps_device_log_serializer = SecuGPSDeviceLogSerializer(secu_gps_device_log)
            return Response(secu_gps_device_log_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Secu GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)


class MahindraGPSDeviceViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Mahindra GPS Device
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        mahindra_gps_device_serializer = MahindraGPSDeviceSerializer(data=request.data)
        if mahindra_gps_device_serializer.is_valid():
            mahindra_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Mahindra GPS Device Created",
                "data": mahindra_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Mahindra GPS Device not Created",
            "data": mahindra_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        mahindra_gps_device = get_or_none(MahindraGPSDevice, id=pk)
        if not isinstance(mahindra_gps_device, MahindraGPSDevice):
            return Response({"error": "Mahindra GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        mahindra_gps_device_serializer = MahindraGPSDeviceSerializer(mahindra_gps_device, data=request.data)

        if mahindra_gps_device_serializer.is_valid():
            mahindra_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Mahindra GPS Device Updated",
                "data": mahindra_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Mahindra GPS Device not Updated",
            "data": mahindra_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        mahindra_gps_device = get_or_none(MahindraGPSDevice, id=pk)
        if not isinstance(mahindra_gps_device, MahindraGPSDevice):
            return Response({"error": "Mahindra GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)
        mahindra_gps_device_serializer = MahindraGPSDeviceSerializer(
            instance=mahindra_gps_device,
            data=request.data,
            partial=True
        )

        if mahindra_gps_device_serializer.is_valid():
            mahindra_gps_device_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Mahindra GPS Device Updated",
                "data": mahindra_gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Mahindra GPS Device not Updated",
            "data": mahindra_gps_device_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        mahindra_gps_device = get_or_none(MahindraGPSDevice, id=pk)
        if isinstance(mahindra_gps_device, MahindraGPSDevice):
            mahindra_gps_device_serializer = MahindraGPSDeviceSerializer(mahindra_gps_device)
            return Response(mahindra_gps_device_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Mahindra GPS Device does not exist"}, status=status.HTTP_404_NOT_FOUND)


class MahindraGPSDeviceLogViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on MahindraGPSDevice
    """

    def create(self, request):
        mahindra_gps_device_log_serializer = MahindraGPSDeviceLogSerializer(data=request.data)
        if mahindra_gps_device_log_serializer.is_valid():
            mahindra_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Mahindra GPS Device Log Created",
                "data": mahindra_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Mahindra GPS Device Log not Created",
            "data": mahindra_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):

        mahindra_gps_device_log = get_or_none(MahindraGPSDeviceLog, id=pk)
        if not isinstance(mahindra_gps_device_log, MahindraGPSDeviceLog):
            return Response({"error": "Mahindra GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        mahindra_gps_device_log_serializer = MahindraGPSDeviceLogSerializer(mahindra_gps_device_log, data=request.data)

        if mahindra_gps_device_log_serializer.is_valid():
            mahindra_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Mahindra GPS Device Log Updated",
                "data": mahindra_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Mahindra GPS Device Log not Updated",
            "data": mahindra_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        mahindra_gps_device_log = get_or_none(MahindraGPSDeviceLog, id=pk)
        if not isinstance(mahindra_gps_device_log, MahindraGPSDeviceLog):
            return Response({"error": "Mahindra GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)
        mahindra_gps_device_log_serializer = MahindraGPSDeviceLogSerializer(
            instance=mahindra_gps_device_log,
            data=request.data,
            partial=True
        )

        if mahindra_gps_device_log_serializer.is_valid():
            mahindra_gps_device_log_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Mahindra GPS Device Log Updated",
                "data": mahindra_gps_device_log_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Mahindra GPS Device Log not Updated",
            "data": mahindra_gps_device_log_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        mahindra_gps_device_log = get_or_none(MahindraGPSDeviceLog, id=pk)
        if isinstance(mahindra_gps_device_log, MahindraGPSDeviceLog):
            mahindra_gps_device_log_serializer = MahindraGPSDeviceLogSerializer(mahindra_gps_device_log)
            return Response(mahindra_gps_device_log_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Mahindra GPS Device Log does not exist"}, status=status.HTTP_404_NOT_FOUND)


class VehicleGPSDataListView(generics.ListAPIView):
    queryset = None
    log_class = None
    vehicle = None

    def get_queryset(self):
        self.queryset = eval(self.log_class).objects.filter(
            vehicle_number=compare_format(self.vehicle.vehicle_number)).filter(
            datetime__gte=datetime.now() - timedelta(hours=48)).order_by('-datetime')
        return self.queryset

    def get(self, request, *args, **kwargs):
        return_response = {"status": "failure", "msg": "Vehicle Does not exist"}
        logs_classes = ['TempoGoGPSDeviceLog', 'WaytrackerGPSDeviceLog', 'SecuGPSDeviceLog',
                        'MahindraGPSDeviceLog', 'BharatGPSTrackerLog', 'TracknovateGPSDeviceLog']
        data = []
        vehicle_id = self.request.query_params.get('vehicle_id', None)
        for key, value in self.request.GET.items():
            if key not in ['vehicle_id']:
                return_response = {"status": "failure", "msg": "Only vehicle id is required"}
                return Response(return_response, status=status.HTTP_400_BAD_REQUEST)

        if vehicle_id is not None:
            if not vehicle_id.isnumeric():
                return_response = {"status": "failure", "msg": "Vehicle id should be a number"}
                return Response(return_response, status=status.HTTP_400_BAD_REQUEST)

            self.vehicle = get_or_none(Vehicle, id=vehicle_id)
            if not isinstance(self.vehicle, Vehicle):
                return Response(return_response, status=status.HTTP_400_BAD_REQUEST)
        else:
            return_response = {"status": "failure", "msg": "vehicle_id is required field", "data": {}}
            return Response(return_response, status=status.HTTP_400_BAD_REQUEST)
        for logs_class in logs_classes:
            self.log_class = logs_class
            queryset = self.filter_queryset(self.get_queryset())
            if not queryset:
                continue
            data.append({
                'latitude': str(queryset[0].latitude),
                'longitude': str(queryset[0].longitude),
                'timestamp': format_date(queryset[0].datetime)
            })
            last_time = (queryset[0].datetime - timedelta(minutes=15)).time()
            for gps in queryset:
                if last_time > gps.datetime.time():
                    last_time = (gps.datetime - timedelta(minutes=15)).time()
                    data.append({
                        'latitude': str(gps.latitude),
                        'longitude': str(gps.longitude),
                        'timestamp': format_date(gps.datetime)
                    })
            if len(data) > 0:
                break

        current_location = {
            'from_address': '',
            'to_address': '',
            'from_gps': data[0] if data else {},
            'to_gps': data[0] if data else {},
            'total_distance': 0,
            'distance_covered': 0,
            'distance_remaining': 0,
        }
        return Response({'status': 'success', 'msg': 'GPS Log', 'data': {'gps_data': data,
                                                                         'current_location': current_location,
                                                                         'max_gps_log_days': 7}},
                        status=status.HTTP_200_OK)


class SupplierVehiclesGPSDataListView(generics.ListAPIView):
    broker = None
    queryset = None
    device_class = None
    vehicles = None

    def get_queryset(self):
        self.queryset = eval(self.device_class).objects.filter(vehicle_number__in=self.vehicles). \
            exclude(is_active=False).exclude(latitude=None)
        return self.queryset

    def get(self, request, *args, **kwargs):
        return_response = {"status": "failure", "msg": "Vehicles Do not exist", "data": {}}
        # devices_classes = ['TempoGoGPSDevice', 'WaytrackerGPSDevice', 'SecuGPSDevice', 'MahindraGPSDevice', 'GPSDevice']
        devices_classes = ['GPSDevice']
        for key, value in self.request.GET.items():
            if key not in ['']:
                return_response = {"status": "failure", "msg": "No field is required"}
                return Response(return_response, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.supplier = Supplier.objects.get(user=request.user)
        except Supplier.DoesNotExist:
            return_response['msg'] = 'Supplier does not exist'
            return Response(return_response, status=status.HTTP_400_BAD_REQUEST)
        vehicle_ids = self.supplier.suppliervehicle_set.values_list('vehicle_id', flat=True)
        if not vehicle_ids or len(vehicle_ids) == 0:
            return Response(return_response, status=status.HTTP_400_BAD_REQUEST)
        self.vehicles = Vehicle.objects.filter(id__in=vehicle_ids).values_list('vehicle_number', flat=True)
        data = []
        for devices_class in devices_classes:
            self.device_class = devices_class
            queryset = self.filter_queryset(self.get_queryset())

            for gps_device in queryset:
                vehicle = get_or_none(Vehicle, vehicle_number=compare_format(gps_device.vehicle_number))
                data.append({
                    'bearing': 0.0, 'vehicle_id': vehicle.id if isinstance(vehicle, Vehicle) else '',
                    'vehicle_status': u'unloaded',
                    'vehicle_number': gps_device.vehicle_number,
                    'driver': gps_device.driver_json(), 'location': gps_device.location(), 'path': []
                })

        return Response({'status': 'success', 'msg': 'tracking data', 'data': data})
