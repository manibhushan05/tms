from django.db import IntegrityError
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics, filters
from rest_framework.response import Response

from api.utils import get_or_none
from notification.models import MobileDevice
from restapi.filter.notification import MobileDeviceFilters
from restapi.search import CustomSearch
from restapi.serializers.notifications import MobileDeviceSerializer


class MobileDeviceListView(generics.ListAPIView):
    serializer_class = MobileDeviceSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    queryset = MobileDevice.objects.exclude(deleted=True).order_by("-id")
    filter_class = MobileDeviceFilters
    ordering_fields = ('id')
    search_fields = (
        'id', 'token')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successfull", "status_code": status.HTTP_200_OK,
                "msg": "Mobile Device List for Notification"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class MobileDeviceViewSet(viewsets.ViewSet):
    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["user"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        app = request.data.get('app', None)
        device_id = request.data.get('device_id', None)
        token = request.data.get('token', None)
        if not token:
            response = {"status_code": status.HTTP_400_BAD_REQUEST, "status": "failure",
                        "msg": "Mobile Device not Created", "data": {"Token is required field"}}
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        mobile_device = MobileDevice.objects.filter(device_id=device_id, app=app).exclude(deleted=True)
        if mobile_device:
            try:
                mobile_device[0].token = token
                mobile_device[0].changed_by = request.user
                mobile_device[0].user = request.user
                mobile_device[0].save()
                response = {
                    "status_code": status.HTTP_200_OK,
                    "status": "success",
                    "msg": "Token Updated",
                    "data": MobileDeviceSerializer(mobile_device[0]).data
                }
            except IntegrityError:
                mobile_device = MobileDevice.objects.filter(token=token).exclude(deleted=True)
                if mobile_device:
                    mobile_device[0].changed_by = request.user
                    mobile_device[0].app = app
                    mobile_device[0].device_id = device_id
                    mobile_device[0].user = request.user
                    mobile_device[0].save()
                    response = {
                        "status_code": status.HTTP_200_OK,
                        "status": "success",
                        "msg": "Token Updated",
                        "data": MobileDeviceSerializer(mobile_device[0]).data
                    }
                    print('IntegrityError handled')
                else:
                    response = {
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "status": "failure",
                        "msg": "Mobile Device not Updated",
                        "data": {"IntegrityError"}
                    }
                    print('IntegrityError not handled')
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            mobile_device = MobileDevice.objects.filter(token=token).exclude(deleted=True)
            if mobile_device:
                mobile_device[0].changed_by = request.user
                mobile_device[0].app = app
                mobile_device[0].device_id = device_id
                mobile_device[0].user = request.user
                mobile_device[0].save()
                response = {"status_code": status.HTTP_200_OK, "status": "success",
                            "msg": "Token Updated", "data": MobileDeviceSerializer(mobile_device[0]).data}
                return Response(data=response, status=status.HTTP_200_OK)
            else:
                mobile_device_serializer = MobileDeviceSerializer(data=request.data)
                if mobile_device_serializer.is_valid():
                    mobile_device_serializer.save()
                    response = {"status_code": status.HTTP_201_CREATED, "status": "success",
                                "msg": "Token created successful", "data": mobile_device_serializer.data}
                    return Response(data=response, status=status.HTTP_201_CREATED)
                response = {"status_code": status.HTTP_400_BAD_REQUEST, "status": "failure",
                            "msg": "Mobile Device not Created", "data": str(mobile_device_serializer.errors['token'][0])}
                return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        pass

    def partial_update(self, request, pk=None):
        pass

    def retrieve(self, request, pk=None):
        pass
