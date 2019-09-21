from datetime import datetime

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters, generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import FileUploadParser, MultiPartParser, JSONParser
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api import s3util
from api.models import S3Upload
from api.utils import get_ext
from fileupload.models import PODFile, VehicleFile, OwnerFile, DriverFile, ChequeFile, InvoiceReceiptFile
from fileupload.views import get_new_serial, update_invoice_booking_status
from restapi.filter.file_upload import PODFileFilter, VehicleFileFilter, OwnerFileFilter, DriverFileFilter, \
    ChequeFileFilter, InvoiceReceiptFileFilter
from restapi.helper_api import generate_random_string, error_response, success_response, check_booking_status, \
    create_new_booking_status, update_booking_status, get_booking_status_mapping_object
from restapi.models import BookingStatusesMapping, BookingStatusChain
from restapi.parser.fileupload import parse_pod_upload_fms
from restapi.search import CustomSearch
from restapi.serializers.api import S3UploadSerializer
from restapi.serializers.file_upload import PODFileSerializer, VehicleFileSerializer, OwnerFileSerializer, \
    DriverFileSerializer, ChequeFileSerializer, InvoiceReceiptFileSerializer
from restapi.serializers.team import ManualBookingSerializer
from restapi.service.documents import create_pod_file
from restapi.utils import get_or_none
from team.models import ManualBooking, LrNumber, RejectedPOD, Invoice


class CustomTokenAuthentication(TokenAuthentication):

    def get_token(self, cookies):
        for cookie in cookies:
            cookie = cookie.strip()
            if cookie.startswith('token='):
                return cookie.split("=")[1]
        return None

    def authenticate(self, request):
        cookies = request.META["HTTP_COOKIE"].split(";")
        token = "Token {}".format(self.get_token(cookies))
        request.META['HTTP_AUTHORIZATION'] = token
        return super().authenticate(request)


class PODFileCreatePageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/booking/pod-list.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class PODFileListView(generics.ListAPIView):
    queryset = PODFile.objects.order_by('-id').exclude(deleted=True)
    serializer_class = PODFileSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = PODFileFilter
    search_fields = (
        'id', 'uploaded_by__username', 'verified_by__username', 'lr_number__lr_number',
        'booking__booking_id', 's3_url', 's3_thumb_url',
        'serial', 'verified', 'is_valid', 'verified_datetime', 'created_by__username', 'created_on')

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


class PODFileViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on PODFile
    """

    def web_upload(self, request):
        lr_number_id = request.data.get('lr_number', None)

        if not lr_number_id:
            return error_response(msg='lr_number id not provided', status=400, data={})
        if str(lr_number_id).startswith('BROKER'):
            booking = get_or_none(ManualBooking, booking_id=lr_number_id)
            lr_obj = None
        else:
            lr_obj = get_or_none(LrNumber, id=lr_number_id)
            booking = None if not isinstance(lr_obj, LrNumber) else lr_obj.booking

        if not (isinstance(lr_obj, LrNumber) or isinstance(booking, ManualBooking)):
            return error_response(msg='LrNumber with id=%s not found' % lr_number_id, status=404, data={})

        if not request.FILES:
            return error_response(msg='no file to upload', status=400, data={})

        upload_file = request.FILES.get('file')
        pod_file = create_pod_file(lr_number=lr_obj, upload_file=upload_file, user=User.objects.last(), booking=booking)
        pod_serializer = PODFileSerializer(pod_file)
        booking_unloaded = check_booking_status(booking, 'unloaded')
        if not booking_unloaded:
            create_new_booking_status(booking, 'unloaded', User.objects.get(username='admin'))
        else:
            update_booking_status(booking, 'unloaded', 'in_progress', User.objects.get(username='admin'))
        booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
        if not booking_pod_uploaded:
            create_new_booking_status(booking, 'pod_uploaded', request.user)
        else:
            update_booking_status(booking, 'pod_uploaded', 'in_progress', request.user)
        return Response(status=status.HTTP_200_OK,
                        data={'files': [pod_serializer.data], 'Content-Disposition': 'inline; filename=files.json'})
        # return upload_json_response(request, data={'files': [serialize(pod_file)]})

    def create(self, request):
        request.data['user'] = request.user.username
        data = request.data
        booking = get_or_none(ManualBooking, booking_id=data['lr_number'])
        if not isinstance(booking, ManualBooking):
            lr_number = get_or_none(LrNumber, lr_number=data.get('lr_number', None))
            booking = lr_number.booking if isinstance(lr_number.booking, ManualBooking) else None
        parsed_data = parse_pod_upload_fms(data)
        for pod in parsed_data:
            s3_upload_serializer = S3UploadSerializer(data=pod.pop('s3_upload_data'))
            if s3_upload_serializer.is_valid():
                s3_upload = s3_upload_serializer.save()
                pod['s3_upload'] = s3_upload.id
            else:
                return error_response(status=status.HTTP_400_BAD_REQUEST, data=s3_upload_serializer.errors,
                                      msg="Something went wrong, Please try later")
            pod_file_serializer = PODFileSerializer(data=pod)
            if pod_file_serializer.is_valid():
                pod_file_serializer.save()
            else:
                return error_response(status=status.HTTP_400_BAD_REQUEST, data=s3_upload_serializer.errors,
                                      msg="Something went wrong, Please try later")
        booking_unloaded = check_booking_status(booking, 'unloaded')
        if not booking_unloaded:
            create_new_booking_status(booking, 'unloaded', User.objects.get(username='admin'))
        else:
            update_booking_status(booking, 'unloaded', 'in_progress', User.objects.get(username='admin'))
        booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
        if not booking_pod_uploaded:
            create_new_booking_status(booking, 'pod_uploaded', request.user)
        else:
            update_booking_status(booking, 'pod_uploaded', 'in_progress', request.user)
        return success_response(data={}, status=status.HTTP_201_CREATED, msg="POD Files created")

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        pod_file = get_or_none(PODFile, id=pk)
        # request.data["created_by"] =
        if not isinstance(pod_file, PODFile):
            return Response({"error": "PODFile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        pod_file_serializer = PODFileSerializer(pod_file, data=request.data)

        if pod_file_serializer.is_valid():
            pod_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "PODFile Updated",
                "data": pod_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "PODFile not Updated",
            "data": pod_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        pod_file = get_or_none(PODFile, id=pk)
        if not isinstance(pod_file, PODFile):
            return Response({"error": "PODFile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        pod_file_serializer = PODFileSerializer(
            instance=pod_file,
            data=request.data,
            partial=True
        )

        if pod_file_serializer.is_valid():
            pod_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "PODFile Updated",
                "data": pod_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "PODFile not Updated",
            "data": pod_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def approve(self, request):
        booking = ManualBooking.objects.get(id=request.data.get('booking_id'))
        if isinstance(booking, ManualBooking):
            data = {'delivered_weight': request.data.get('delivered_weight'),
                    'loaded_weight': request.data.get('loaded_weight'), 'pod_date': datetime.now(),
                    'delivery_datetime': request.data.get('delivery_datetime'), 'pod_status': 'completed'}
            manual_booking_serializer = ManualBookingSerializer(instance=booking, data=data, partial=True)
            if manual_booking_serializer.is_valid():
                manual_booking_serializer.save()
                for pod in PODFile.objects.filter(booking=booking).exclude(verified=True):
                    pod.is_valid = True
                    pod.verified = True
                    pod.verified_by = request.user
                    pod.verified_datetime = datetime.now()
                    pod.save()
                    S3Upload.objects.filter(id=pod.s3_upload_id).update(is_valid=True, verified=True)
                    booking_unloaded = check_booking_status(booking, 'unloaded')
                    if not booking_unloaded:
                        create_new_booking_status(booking, 'unloaded', User.objects.get(username='admin'))
                    else:
                        update_booking_status(booking, 'unloaded', 'in_progress', User.objects.get(username='admin'))
                    booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
                    if not booking_pod_uploaded:
                        create_new_booking_status(booking, 'pod_uploaded', User.objects.get(username='admin'))
                    else:
                        update_booking_status(booking, 'pod_uploaded', 'in_progress', User.objects.get(username='admin'))
                    booking_pod_verified = check_booking_status(booking, 'pod_verified')
                    if not booking_pod_verified:
                        create_new_booking_status(booking, 'pod_verified', request.user)
                    else:
                        update_booking_status(booking, 'pod_verified', 'in_progress', request.user)
                return success_response(status=status.HTTP_200_OK, msg='verified', data={})
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Something went wrong', data={})
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Something went wrong', data={})

    def reject(self, request):
        booking = ManualBooking.objects.get(id=request.data.get('booking_id'))
        if not isinstance(booking, ManualBooking):
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Booking id is not valid', data={})
        booking.pod_status = 'rejected'
        booking.save()
        for lr in booking.lr_numbers.all():
            RejectedPOD.objects.create(booking=booking, lr=lr, remarks=request.data.get('rejection_remark'),
                                       rejected_by=request.user)
        if not booking.lr_numbers.exists():
            RejectedPOD.objects.create(booking=booking, remarks=request.data.get('rejection_remark'),
                                       rejected_by=request.user)
        for pod in PODFile.objects.filter(booking=booking).exclude(verified=True):
            pod.is_valid = False
            pod.verified = True
            pod.verified_by = request.user
            pod.verified_datetime = datetime.now()
            pod.save()
            S3Upload.objects.filter(id=pod.s3_upload_id).update(is_valid=False, verified=True)
            booking_unloaded = check_booking_status(booking, 'unloaded')
            booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
            if booking_unloaded:
                unloaded_obj = get_booking_status_mapping_object(booking, 'unloaded')
                if unloaded_obj.created_by == User.objects.get(username='admin') and \
                        unloaded_obj.changed_by == User.objects.get(username='admin'):
                    update_booking_status(booking, 'unloaded', 'reverted', User.objects.get(username='admin'))
            if booking_pod_uploaded:
                update_booking_status(booking, 'pod_uploaded', 'reverted', request.user)
        return success_response(msg='POD for booking ID {} is rejected'.format(booking.booking_id),
                                status=status.HTTP_200_OK, data={})

    def resubmit(self, request):
        resubmission_remark = request.data.get('resubmission_remark')
        booking_id = request.data.get('booking_id')
        resubmitted_pod = request.data.get('resubmitted_pod')
        if not resubmission_remark:
            return error_response(msg="Remarks is mandatory", status=status.HTTP_400_BAD_REQUEST, data={})
        if not booking_id:
            return error_response(msg="Booking id is required", status=status.HTTP_400_BAD_REQUEST, data={})
        booking = get_or_none(ManualBooking, booking_id=booking_id)
        if not isinstance(booking, ManualBooking):
            return error_response(msg="BAD request", status=status.HTTP_400_BAD_REQUEST, data={})
        if not PODFile.objects.filter(booking=booking).exists():
            return error_response(msg="BAD Request", status=status.HTTP_400_BAD_REQUEST, data={})
        PODFile.objects.filter(id__in=resubmitted_pod).update(verified=False, is_valid=False)
        PODFile.objects.filter(booking=booking).exclude(id__in=resubmitted_pod).update(verified=True, is_valid=False)
        booking.pod_status = 'unverified'
        booking.save()
        booking_unloaded = check_booking_status(booking, 'unloaded')
        if booking_unloaded:
            unloaded_obj = get_booking_status_mapping_object(booking, 'unloaded')
            if unloaded_obj.created_by == User.objects.get(username='admin') and \
                    unloaded_obj.changed_by == User.objects.get(username='admin'):
                update_booking_status(booking, 'unloaded', 'in_progress', User.objects.get(username='admin'))
        booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
        if not booking_pod_uploaded:
            create_new_booking_status(booking, 'pod_uploaded', request.user)
        else:
            update_booking_status(booking, 'pod_uploaded', 'in_progress', request.user)
        return success_response(msg="success", status=status.HTTP_200_OK, data={})

    def retrieve(self, request, pk=None):
        pod_file = get_or_none(PODFile, id=pk)
        if isinstance(pod_file, PODFile):
            pod_file_serializer = PODFileSerializer(pod_file)
            return Response(pod_file_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "PODFile does not exist"}, status=status.HTTP_404_NOT_FOUND)



class VehicleFileListView(generics.ListAPIView):
    queryset = VehicleFile.objects.order_by('-id').exclude(deleted=True)
    serializer_class = VehicleFileSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = VehicleFileFilter
    search_fields = (
        'id', 'uploaded_by__username', 'vehicle__vehicle_type__vehicle_type', 'vehicle__vehicle_number',
        'document_category', 's3_url', 's3_thumb_url',
        'serial', 'verified', 'is_valid', 's3_upload__filename', 'created_by__username', 'created_on')

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


class VehicleFileViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Vehicle File
    """

    def create(self, request, pk=None):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        request.data["uploaded_by"] = self.request.user.username
        vehicle_file_serializer = VehicleFileSerializer(data=request.data)
        if vehicle_file_serializer.is_valid():
            vehicle_file_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Vehicle File Created",
                "data": vehicle_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle File not Created",
            "data": vehicle_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        vehicle_file = get_or_none(VehicleFile, id=pk)
        if not isinstance(vehicle_file, VehicleFile):
            return Response({"error": "Vehicle File does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_file_serializer = VehicleFileSerializer(vehicle_file, data=request.data)

        if vehicle_file_serializer.is_valid():
            vehicle_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle File Updated",
                "data": vehicle_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle File not Updated",
            "data": vehicle_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        vehicle_file = get_or_none(VehicleFile, id=pk)
        if not isinstance(vehicle_file, VehicleFile):
            return Response({"error": "Vehicle File does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_file_serializer = VehicleFileSerializer(
            instance=vehicle_file,
            data=request.data,
            partial=True
        )

        if vehicle_file_serializer.is_valid():
            vehicle_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle File Updated",
                "data": vehicle_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle File not Updated",
            "data": vehicle_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        vehicle_file = get_or_none(VehicleFile, id=pk)
        if isinstance(vehicle_file, VehicleFile):
            vehicle_file_serializer = VehicleFileSerializer(vehicle_file)
            return Response(vehicle_file_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Vehicle File does not exist"}, status=status.HTTP_404_NOT_FOUND)


class OwnerFileListView(generics.ListAPIView):
    queryset = OwnerFile.objects.order_by('-id').exclude(deleted=True)
    serializer_class = OwnerFileSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = OwnerFileFilter
    search_fields = (
        'id', 'uploaded_by__username', 'owner__name__username',
        'document_category', 's3_url', 's3_thumb_url',
        'serial', 'verified', 'is_valid', 's3_upload__filename', 'created_by__username', 'created_on')

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


class OwnerFileViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Owner File
    """

    def create(self, request, pk=None):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        request.data["uploaded_by"] = self.request.user.username
        owner_file_serializer = OwnerFileSerializer(data=request.data)
        if owner_file_serializer.is_valid():
            owner_file_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Owner File Created",
                "data": owner_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Owner File not Created",
            "data": owner_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        owner_file = get_or_none(OwnerFile, id=pk)
        if not isinstance(owner_file, OwnerFile):
            return Response({"error": "Owner File does not exist"}, status=status.HTTP_404_NOT_FOUND)
        owner_file_serializer = OwnerFileSerializer(owner_file, data=request.data)

        if owner_file_serializer.is_valid():
            owner_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Owner File Updated",
                "data": owner_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Owner File not Updated",
            "data": owner_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        owner_file = get_or_none(OwnerFile, id=pk)
        if not isinstance(owner_file, OwnerFile):
            return Response({"error": "Owner File does not exist"}, status=status.HTTP_404_NOT_FOUND)
        owner_file_serializer = OwnerFileSerializer(
            instance=owner_file,
            data=request.data,
            partial=True
        )

        if owner_file_serializer.is_valid():
            owner_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Owner File Updated",
                "data": owner_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Owner File not Updated",
            "data": owner_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        owner_file = get_or_none(OwnerFile, id=pk)
        if isinstance(owner_file, OwnerFile):
            owner_file_serializer = OwnerFileSerializer(owner_file)
            return Response(owner_file_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Owner File does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DriverFileListView(generics.ListAPIView):
    queryset = DriverFile.objects.order_by('-id').exclude(deleted=True)
    serializer_class = DriverFileSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = DriverFileFilter
    search_fields = (
        'id', 'uploaded_by__username', 'driver__name',
        'document_category', 's3_url', 's3_thumb_url',
        'serial', 'verified', 'is_valid', 's3_upload__filename', 'created_by__username', 'created_on')

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


class DriverFileViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on DriverFile
    """

    def create(self, request, pk=None):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        request.data["uploaded_by"] = self.request.user.username
        driver_file_serializer = DriverFileSerializer(data=request.data)
        if driver_file_serializer.is_valid():
            driver_file_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "DriverFile Created",
                "data": driver_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "DriverFile not Created",
            "data": driver_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        driver_file = get_or_none(DriverFile, id=pk)
        if not isinstance(driver_file, DriverFile):
            return Response({"error": "DriverFile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        driver_file_serializer = DriverFileSerializer(driver_file, data=request.data)

        if driver_file_serializer.is_valid():
            driver_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "DriverFile Updated",
                "data": driver_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "DriverFile not Updated",
            "data": driver_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        driver_file = get_or_none(DriverFile, id=pk)
        if not isinstance(driver_file, DriverFile):
            return Response({"error": "DriverFile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        driver_file_serializer = DriverFileSerializer(
            instance=driver_file,
            data=request.data,
            partial=True
        )

        if driver_file_serializer.is_valid():
            driver_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "DriverFile Updated",
                "data": driver_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "DriverFile not Updated",
            "data": driver_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        driver_file = get_or_none(DriverFile, id=pk)
        if isinstance(driver_file, DriverFile):
            driver_file_serializer = DriverFileSerializer(driver_file)
            return Response(driver_file_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "DriverFile does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ChequeFileListView(generics.ListAPIView):
    queryset = ChequeFile.objects.order_by('-id').exclude(deleted=True)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    serializer_class = ChequeFileSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = ChequeFileFilter
    search_fields = (
        'id', 'uploaded_by__username', 'resolved_by__username', 'customer_name',
        'cheque_number', 'cheque_date', 'remarks', 'amount',
        'serial', 'resolved', 'resolved_datetime', 'is_valid', 's3_upload__filename', 'created_by__username',
        'created_on')

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


class ChequeFileViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on ChequeFile
    """

    def create(self, request, pk=None):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        request.data["uploaded_by"] = self.request.user.username
        cheque_file_serializer = ChequeFileSerializer(data=request.data)
        if cheque_file_serializer.is_valid():
            cheque_file_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "ChequeFile Created",
                "data": cheque_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "ChequeFile not Created",
            "data": cheque_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        cheque_file = get_or_none(ChequeFile, id=pk)
        if not isinstance(cheque_file, ChequeFile):
            return Response({"error": "ChequeFile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        cheque_file_serializer = ChequeFileSerializer(cheque_file, data=request.data)

        if cheque_file_serializer.is_valid():
            cheque_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "ChequeFile Updated",
                "data": cheque_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "ChequeFile not Updated",
            "data": cheque_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        cheque_file = get_or_none(ChequeFile, id=pk)
        if not isinstance(cheque_file, ChequeFile):
            return Response({"error": "ChequeFile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        cheque_file_serializer = ChequeFileSerializer(
            instance=cheque_file,
            data=request.data,
            partial=True
        )

        if cheque_file_serializer.is_valid():
            cheque_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "ChequeFile Updated",
                "data": cheque_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "ChequeFile not Updated",
            "data": cheque_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        cheque_file = get_or_none(ChequeFile, id=pk)

        if isinstance(cheque_file, ChequeFile):
            cheque_file_serializer = ChequeFileSerializer(cheque_file)
            # if request.META["CONTENT_TYPE"] == "application/json":
            return Response(cheque_file_serializer.data, status=status.HTTP_200_OK)
            # else:
            #     return HttpResponseRedirect(redirect_to='/page/uncredited-cheques/')

        return Response({"error": "ChequeFile does not exist"}, status=status.HTTP_404_NOT_FOUND)


class InvoiceReceiptFileListView(generics.ListAPIView):
    queryset = InvoiceReceiptFile.objects.order_by('-id').exclude(deleted=True)
    serializer_class = InvoiceReceiptFileSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = InvoiceReceiptFileFilter
    search_fields = (
        'id', 'uploaded_by__username', 'invoice_number', 'invoice_receipt__invoice_number',
        'serial', 'verified', 'is_valid', 's3_upload__filename', 'created_by__username',
        'created_on')

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


class InvoiceReceiptFileViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on InvoiceReceiptFile
    """

    def create(self, request):
        invoice = get_or_none(Invoice, invoice_number=request.data.get('invoice_number', -1))
        if not isinstance(invoice, Invoice):
            return error_response(msg="Bad request", status=status.HTTP_400_BAD_REQUEST, data={})
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        request.data["uploaded_by"] = self.request.user.username
        request.data["invoice_receipt"] = invoice.id
        request.data["serial"] = generate_random_string(N=20)
        
        invoice_receipt_file_serializer = InvoiceReceiptFileSerializer(data=request.data)
        if invoice_receipt_file_serializer.is_valid():
            invoice_receipt_file_serializer.save()
            invoice_sent_mode = request.data.get('invoice_sent_mode', None)
            invoice_confirm_mode = request.data.get('invoice_confirm_mode', None)
            invoice_confirm_by_name = request.data.get('invoice_confirm_by_name', None)
            invoice_confirm_by_phone = request.data.get('invoice_confirm_by_phone', None)
            INVOICE_SENT_MODE_CHOICES = (
                ('CR', 'Courier'),
                ('HD', 'Hand Delivered'),
                ('EM', 'Email Screenshot')
            )
            INVOICE_CONFIRM_MODE_CHOICES = (
                ('PH', 'Phone'),
                ('WA', 'Written Acknowledgement'),
                ('EM', 'Email Screenshot')
            )
            if invoice_sent_mode:
                if invoice_sent_mode not in [x[0] for x in INVOICE_SENT_MODE_CHOICES]:
                    return error_response(msg='Invalid Invoice Sent Mode', status=400, data={})
            if invoice_confirm_mode:
                if invoice_confirm_mode not in [x[0] for x in INVOICE_CONFIRM_MODE_CHOICES]:
                    return error_response(msg='Invalid Invoice Confirm Mode', status=400, data={})
                if invoice_confirm_mode == 'PH' and not invoice_confirm_by_name and not invoice_confirm_by_phone:
                    return error_response(msg='Invoice Confirm Name and Phone required', status=400, data={})
            if not invoice_sent_mode and not invoice_confirm_mode:
                return error_response(msg='Invoice Sent or Confirm Mode Required', status=status.HTTP_400_BAD_REQUEST,
                                      data={})

            if invoice_sent_mode:
                update_invoice_booking_status(invoice.id, 'party_invoice_sent', request.user)
            if invoice_confirm_mode:
                update_invoice_booking_status(invoice.id, 'invoice_confirmed', request.user)
            return success_response(data=invoice_receipt_file_serializer.data, status=status.HTTP_201_CREATED,
                                    msg="InvoiceReceiptFile Created")
        return error_response(msg="InvoiceReceiptFile not Created", data=invoice_receipt_file_serializer.errors,
                              status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        invoice_receipt_file = get_or_none(InvoiceReceiptFile, id=pk)
        if not isinstance(invoice_receipt_file, InvoiceReceiptFile):
            return Response({"error": "InvoiceReceiptFile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        invoice_receipt_file_serializer = InvoiceReceiptFileSerializer(invoice_receipt_file, data=request.data)

        if invoice_receipt_file_serializer.is_valid():
            invoice_receipt_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "InvoiceReceiptFile Updated",
                "data": invoice_receipt_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "InvoiceReceiptFile not Updated",
            "data": invoice_receipt_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        invoice_receipt_file = get_or_none(InvoiceReceiptFile, id=pk)
        if not isinstance(invoice_receipt_file, InvoiceReceiptFile):
            return Response({"error": "InvoiceReceiptFile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        invoice_receipt_file_serializer = InvoiceReceiptFileSerializer(
            instance=invoice_receipt_file,
            data=request.data,
            partial=True
        )

        if invoice_receipt_file_serializer.is_valid():
            invoice_receipt_file_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "InvoiceReceiptFile Updated",
                "data": invoice_receipt_file_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "InvoiceReceiptFile not Updated",
            "data": invoice_receipt_file_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        invoice_receipt_file = get_or_none(InvoiceReceiptFile, id=pk)
        if isinstance(invoice_receipt_file, InvoiceReceiptFile):
            invoice_receipt_file_serializer = InvoiceReceiptFileSerializer(invoice_receipt_file)
            return Response(invoice_receipt_file_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "InvoiceReceiptFile does not exist"}, status=status.HTTP_404_NOT_FOUND)
