from rest_framework import generics, viewsets, status
from rest_framework.generics import get_object_or_404
from django.utils import timezone

from broker.models import BrokerVehicle, Broker
from fms.doc import downloadable_documents_data
from fms.email import send_documents_email
from fms.models import MobileAppVersions
from fms.views import get_expiry_key
from owner.models import Vehicle
from restapi.serializers.app_version import MobileAppVersionSerializer
from rest_framework.response import Response


class MobileAppVersionListView(generics.ListAPIView):
    queryset = MobileAppVersions.objects.order_by('-id').exclude(deleted=True)
    serializer_class = MobileAppVersionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Mobile App version List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(serializer.data)


class MobileAppVersionViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving App version.

    """

    def create(self, request):
        app_version_serializer = MobileAppVersionSerializer(data=request.data)
        if app_version_serializer.is_valid():
            app_version_serializer.save()
            response = {'status': 'success', 'msg': 'App Version Created', 'data':
                {'id': app_version_serializer.data['id']}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(app_version_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = MobileAppVersions.objects.all().exclude(deleted=True)
        app_ver = get_object_or_404(queryset, pk=pk)
        serializer = MobileAppVersionSerializer(app_ver)
        response = {'status': 'success', 'msg': 'App Version Retrieved', 'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        try:
            app_ver = MobileAppVersions.objects.get(id=pk)
        except MobileAppVersions.DoesNotExist:
            return Response({"status": "MobileAppVersions Doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        app_ver_serializer = MobileAppVersionSerializer(instance=app_ver, data=request.data)
        if app_ver_serializer.is_valid():
            app_vers = app_ver_serializer.save()
            if app_vers:
                response = {'status': 'success', 'msg': 'App Version Updated', 'data':
                    {'id': app_ver_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(app_ver_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = MobileAppVersions.objects.all()
        mobile_ver = get_object_or_404(queryset, pk=pk)
        serializer = MobileAppVersionSerializer(mobile_ver)
        mobile_ver.deleted = True
        mobile_ver.deleted_on = timezone.now()
        mobile_ver.save()
        response = {'status': 'success', 'msg': 'App Version Deleted', 'data':
            {'id': serializer.data['id']}}
        return Response(response, status=status.HTTP_200_OK)

    def check(self, request):
        mobile_app_ver_serializer = MobileAppVersionSerializer(data=request.data)
        if mobile_app_ver_serializer.is_valid():
            response = mobile_app_ver_serializer.check_update_need(mobile_app_ver_serializer.validated_data)
            if response['status'] == 'failure':
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(mobile_app_ver_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendEmailViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for sending emails

    """
    def vehicle_documents_email(self, request):
        vehicle_id = request.data.get('id', None)
        emails = request.data.get('emails', None) or []
        excluded = request.data.get('excluded', None) or []

        response = {'status': 'failure', 'msg': 'Vehicle Document Email not sent',
                    'data': {}, 'status_code': status.HTTP_400_BAD_REQUEST}

        if vehicle_id is None or not emails:
            response['data'] = 'Vehicle or Email not received'
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            response['data'] = 'Vehicle Does not exist'
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        vehicle_documents = downloadable_documents_data(vehicle, excluded)

        try:
            broker = Broker.objects.get(name=request.user)
        except Broker.DoesNotExist:
            broker = None

        try:
            broker_vehicle = BrokerVehicle.objects.get(broker=broker, vehicle=vehicle)
            account = broker_vehicle.account_details
        except BrokerVehicle.DoesNotExist:
            account = None

        if not vehicle_documents and (not account or "ac" in excluded):
            response['data'] = 'Vehicle has no associated documents'
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        send_documents_email(vehicle, account, vehicle_documents, emails, excluded, get_expiry_key())
        response['data'] = 'Email Sent'
        response['status'] = 'success'
        response['msg'] = 'Vehicle Document Email sent'
        response['status_code'] = status.HTTP_200_OK
        return Response(response, status=status.HTTP_200_OK)
