from django.conf import settings
from rest_framework import generics, viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import get_object_or_404
from django.utils import timezone
from datetime import datetime
from api.models import google_reverse_geocode
from api.utils import get_or_none
from employee.models import Employee
from restapi.filter.task_dashboard import EmployeeRolesFilter, EmployeeRolesMappingFilter, BookingStatusesFilter, \
    BookingStatusChainFilter, EmployeeRolesBookingStatusMappingFilter, BookingStatusesMappingFilter, \
    TaskDashboardFunctionalitiesFilter, EmployeeRolesFunctionalityMappingFilter, BookingStatusesMappingCommentsFilter, \
    BookingStatusesMappingLocationFilter, SmePendingPaymentsCommentsFilter
from restapi.helper_api import get_bookings_monitoring_status, get_bookings_monitoring_tac, get_bookings_monitoring_iwp, \
    get_bookings_monitoring_tao, get_bookings_monitoring_owp, get_employee_roles, get_employee_display_roles, \
    get_tasks_monitoring_row
from restapi.models import EmployeeRoles, EmployeeRolesMapping, BookingStatuses, BookingStatusChain, \
    EmployeeRolesBookingStatusMapping, BookingStatusesMapping, TaskDashboardFunctionalities, \
    EmployeeRolesFunctionalityMapping, BookingStatusesMappingComments, BookingStatusesMappingLocation, \
    SmePaymentFollowupComments
from rest_framework.response import Response

from restapi.serializers.task_dashboard import EmployeeRolesSerializer, EmployeeRolesMappingSerializer, \
    BookingStatusesSerializer, BookingStatusChainSerializer, EmployeeRolesBookingStatusMappingSerializer, \
    BookingStatusesMappingSerializer, TaskDashboardFunctionalitiesSerializer, \
    EmployeeRolesFunctionalityMappingSerializer, BookingStatusesMappingCommentsSerializer, \
    BookingStatusesMappingLocationSerializer, SmePendingPaymentsCommentsSerializer
from restapi.signals import send_notification_to_invoice_confirmed_escalated_personnel
from team.helper.helper import to_int
from team.models import ManualBooking, Invoice
from utils.models import AahoOffice


class EmployeeRolesListView(generics.ListAPIView):
    queryset = EmployeeRoles.objects.order_by('-id').exclude(deleted=True)
    serializer_class = EmployeeRolesSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = EmployeeRolesFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'role')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Employee Roles List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class EmployeeRolesViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for creating, updating, deleting and retrieving Employee Roles.

    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        employee_roles_serializer = EmployeeRolesSerializer(data=request.data)
        if employee_roles_serializer.is_valid():
            employee_roles_serializer.save()
            response = {'status': 'success', 'msg': 'Employee Role Created', 'data':
                {'id': employee_roles_serializer.data['id']}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(employee_roles_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = EmployeeRoles.objects.all().exclude(deleted=True)
        emp_role = get_object_or_404(queryset, pk=pk)
        serializer = EmployeeRolesSerializer(emp_role)
        response = {'status': 'success', 'msg': 'Employee Role Retrieved', 'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        try:
            emp_role = EmployeeRoles.objects.get(id=pk)
        except EmployeeRoles.DoesNotExist:
            return Response({"status": "EmployeeRoles Doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        emp_role_serializer = EmployeeRolesSerializer(instance=emp_role, data=request.data)
        if emp_role_serializer.is_valid():
            emp_roles = emp_role_serializer.save()
            if emp_roles:
                response = {'status': 'success', 'msg': 'Employee Role Updated', 'data':
                    {'id': emp_role_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(emp_role_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = EmployeeRoles.objects.all()
        emp_role = get_object_or_404(queryset, pk=pk)
        serializer = EmployeeRolesSerializer(emp_role)
        emp_role.deleted = True
        emp_role.deleted_on = timezone.now()
        emp_role.save()
        response = {'status': 'success', 'msg': 'Employee Role Deleted', 'data':
            {'id': serializer.data['id']}}
        return Response(response, status=status.HTTP_200_OK)


class EmployeeRolesMappingListView(generics.ListAPIView):
    queryset = EmployeeRolesMapping.objects.order_by('-id').exclude(deleted=True).filter(employee_status='active')
    serializer_class = EmployeeRolesMappingSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = EmployeeRolesMappingFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'employee__username__username', 'employee_role__role', 'employee_status', 'employee__id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Employee Roles Mapping List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class EmployeeRolesMappingViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for creating, updating, deleting and retrieving Employee Roles Mapping.

    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        employee_roles_mapping_serializer = EmployeeRolesMappingSerializer(data=request.data)
        if employee_roles_mapping_serializer.is_valid():
            employee_roles_mapping_serializer.save()
            response = {'status': 'success', 'msg': 'Employee Role Mapping Created', 'data':
                {'id': employee_roles_mapping_serializer.data['id']}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(employee_roles_mapping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = EmployeeRolesMapping.objects.all().exclude(deleted=True)
        emp_role_mapping = get_object_or_404(queryset, pk=pk)
        serializer = EmployeeRolesMappingSerializer(emp_role_mapping)
        response = {'status': 'success', 'msg': 'Employee Role Mapping Retrieved', 'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def employee_role_list(self, request):
        roles = EmployeeRolesMapping.objects.filter(employee__username=request.user).exclude(
            employee_status='inactive').values_list('employee_role__role', flat=True)
        if roles:
            return Response(data=list(set(roles)),status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        try:
            emp_role_mapping = EmployeeRolesMapping.objects.get(id=pk)
        except EmployeeRolesMapping.DoesNotExist:
            return Response({"status": "EmployeeRolesMapping Doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        emp_role_mapping_serializer = EmployeeRolesMappingSerializer(instance=emp_role_mapping, data=request.data)
        if emp_role_mapping_serializer.is_valid():
            emp_roles_mapping = emp_role_mapping_serializer.save()
            if emp_roles_mapping:
                response = {'status': 'success', 'msg': 'Employee Role Mapping Updated', 'data':
                    {'id': emp_role_mapping_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(emp_role_mapping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = EmployeeRolesMapping.objects.all()
        emp_role_mapping = get_object_or_404(queryset, pk=pk)
        serializer = EmployeeRolesMappingSerializer(emp_role_mapping)
        emp_role_mapping.deleted = True
        emp_role_mapping.deleted_on = timezone.now()
        emp_role_mapping.save()
        response = {'status': 'success', 'msg': 'Employee Role Mapping Deleted', 'data':
            {'id': serializer.data['id']}}
        return Response(response, status=status.HTTP_200_OK)


class BookingStatusesListView(generics.ListAPIView):
    queryset = BookingStatuses.objects.order_by('-id').exclude(deleted=True)
    serializer_class = BookingStatusesSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = BookingStatusesFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'status', 'time_limit')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Booking Statuses List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class BookingStatusesViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for creating, updating, deleting and retrieving Booking Statuses.

    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        booking_statuses_serializer = BookingStatusesSerializer(data=request.data)
        if booking_statuses_serializer.is_valid():
            booking_statuses_serializer.save()
            response = {'status': 'success', 'msg': 'Booking Statuses Created', 'data':
                {'id': booking_statuses_serializer.data['id']}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(booking_statuses_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = BookingStatuses.objects.all().exclude(deleted=True)
        booking_status = get_object_or_404(queryset, pk=pk)
        serializer = BookingStatusesSerializer(booking_status)
        response = {'status': 'success', 'msg': 'Booking Status Retrieved', 'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        try:
            booking_statuses = BookingStatuses.objects.get(id=pk)
        except BookingStatuses.DoesNotExist:
            return Response({"status": "BookingStatuses Doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        booking_statuses_serializer = BookingStatusesSerializer(instance=booking_statuses, data=request.data)
        if booking_statuses_serializer.is_valid():
            booking_status = booking_statuses_serializer.save()
            if booking_status:
                response = {'status': 'success', 'msg': 'Booking Statuses Updated', 'data':
                    {'id': booking_statuses_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(booking_statuses_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = BookingStatuses.objects.all()
        booking_status = get_object_or_404(queryset, pk=pk)
        serializer = BookingStatusesSerializer(booking_status)
        booking_status.deleted = True
        booking_status.deleted_on = timezone.now()
        booking_status.save()
        response = {'status': 'success', 'msg': 'Booking Statuses Deleted', 'data':
            {'id': serializer.data['id']}}
        return Response(response, status=status.HTTP_200_OK)


class BookingStatusChainListView(generics.ListAPIView):
    queryset = BookingStatusChain.objects.order_by('-id').exclude(deleted=True)
    serializer_class = BookingStatusChainSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = BookingStatusChainFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'booking_status__status', 'level', 'primary_preceded_booking_status__status',
                     'primary_succeeded_booking_status__status', 'secondary_preceded_booking_status__status',
                     'secondary_succeeded_booking_status__status')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Booking Status Chain List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class BookingStatusChainViewSet(viewsets.ViewSet):
    """
        A simple ViewSet for creating, updating, deleting and retrieving Booking Status Chain.

        """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        booking_status_chain_serializer = BookingStatusChainSerializer(data=request.data)
        if booking_status_chain_serializer.is_valid():
            booking_status_chain_serializer.save()
            response = {'status': 'success', 'msg': 'Booking Status Chain Created', 'data':
                {'id': booking_status_chain_serializer.data['id']}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(booking_status_chain_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = BookingStatusChain.objects.all().exclude(deleted=True)
        booking_status_chain = get_object_or_404(queryset, pk=pk)
        serializer = BookingStatusChainSerializer(booking_status_chain)
        response = {'status': 'success', 'msg': 'Booking Status Chain Retrieved', 'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        try:
            booking_status_chain = BookingStatusChain.objects.get(id=pk)
        except BookingStatusChain.DoesNotExist:
            return Response({"status": "BookingStatusChain Doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        booking_status_chain_serializer = BookingStatusChainSerializer(instance=booking_status_chain, data=request.data)
        if booking_status_chain_serializer.is_valid():
            booking_status_c = booking_status_chain_serializer.save()
            if booking_status_c:
                response = {'status': 'success', 'msg': 'Booking Status Chain Updated', 'data':
                    {'id': booking_status_chain_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(booking_status_chain_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = BookingStatusChain.objects.all()
        booking_status_chain = get_object_or_404(queryset, pk=pk)
        serializer = BookingStatusChainSerializer(booking_status_chain)
        booking_status_chain.deleted = True
        booking_status_chain.deleted_on = timezone.now()
        booking_status_chain.save()
        response = {'status': 'success', 'msg': 'Booking Status Chain Deleted', 'data':
            {'id': serializer.data['id']}}
        return Response(response, status=status.HTTP_200_OK)


class EmployeeRolesBookingStatusMappingListView(generics.ListAPIView):
    queryset = EmployeeRolesBookingStatusMapping.objects.order_by('-id').exclude(deleted=True)
    serializer_class = EmployeeRolesBookingStatusMappingSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = EmployeeRolesBookingStatusMappingFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'employee_roles_mapping__employee__username__username',
                     'employee_roles_mapping__employee_role__role', 'booking_status_chain__booking_status__status',
                     'assignment_status')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK,
                "msg": "Employee Roles Booking Status Mapping List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class EmployeeRolesBookingStatusMappingViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for creating, updating, deleting and retrieving Employee Roles Booking Status.
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        employee_roles_booking_status_mapping_serializer = EmployeeRolesBookingStatusMappingSerializer(
            data=request.data)
        if employee_roles_booking_status_mapping_serializer.is_valid():
            employee_roles_booking_status_mapping_serializer.save()
            response = {'status': 'success', 'msg': 'Employee Roles Booking Status Mapping Created', 'data':
                {'id': employee_roles_booking_status_mapping_serializer.data['id']}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(employee_roles_booking_status_mapping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = EmployeeRolesBookingStatusMapping.objects.all().exclude(deleted=True)
        employee_roles_booking_status_mapping = get_object_or_404(queryset, pk=pk)
        serializer = EmployeeRolesBookingStatusMappingSerializer(employee_roles_booking_status_mapping)
        response = {'status': 'success', 'msg': 'Employee Roles Booking Status Mapping Retrieved',
                    'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        try:
            employee_roles_booking_status_mapping = EmployeeRolesBookingStatusMapping.objects.get(id=pk)
        except EmployeeRolesBookingStatusMapping.DoesNotExist:
            return Response({"status": "EmployeeRolesBookingStatusMapping Doesn't exists"},
                            status=status.HTTP_400_BAD_REQUEST)
        employee_roles_booking_status_mapping_serializer = EmployeeRolesBookingStatusMappingSerializer(
            instance=employee_roles_booking_status_mapping, data=request.data)
        if employee_roles_booking_status_mapping_serializer.is_valid():
            emp_role_booking_status_m = employee_roles_booking_status_mapping_serializer.save()
            if emp_role_booking_status_m:
                response = {'status': 'success', 'msg': 'Employee Roles Booking Status Mapping Updated', 'data':
                    {'id': employee_roles_booking_status_mapping_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(employee_roles_booking_status_mapping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = EmployeeRolesBookingStatusMapping.objects.all()
        employee_role_booking_status_mapping = get_object_or_404(queryset, pk=pk)
        serializer = EmployeeRolesBookingStatusMappingSerializer(employee_role_booking_status_mapping)
        employee_role_booking_status_mapping.deleted = True
        employee_role_booking_status_mapping.deleted_on = timezone.now()
        employee_role_booking_status_mapping.save()
        response = {'status': 'success', 'msg': 'Employee Roles Booking Status Mapping Deleted', 'data':
            {'id': serializer.data['id']}}
        return Response(response, status=status.HTTP_200_OK)


class BookingStatusesMappingListView(generics.ListAPIView):
    queryset = BookingStatusesMapping.objects.order_by('-id').exclude(deleted=True)
    serializer_class = BookingStatusesMappingSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = BookingStatusesMappingFilter
    ordering_fields = ('id',)
    search_fields = (
    'id', 'manual_booking__booking_id', 'booking_status_chain__booking_status__status', 'booking_stage')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Booking Statuses Mapping List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class BookingStatusesMappingViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for creating, updating, deleting and retrieving Booking Statuses Mapping.
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        booking_statuses_mapping_serializer = BookingStatusesMappingSerializer(data=request.data)
        if booking_statuses_mapping_serializer.is_valid():
            booking_statuses_mapping_serializer.save()
            response = {'status': 'success', 'msg': 'Booking Statuses Mapping Created', 'data':
                {'id': booking_statuses_mapping_serializer.data['id']}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Not Created',
                        'data': booking_statuses_mapping_serializer.errors, 'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def create_key_based(self, request):
        request.data["created_by"] = self.request.user.username
        if 'booking_status' not in request.data:
            response = {'status': 'failure', 'msg': 'booking_status is required field', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        booking_status_key = request.data['booking_status']
        try:
            booking_status = BookingStatuses.objects.get(status=booking_status_key)
        except BookingStatuses.DoesNotExist:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Not Created', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        try:
            booking_status_chain = BookingStatusChain.objects.get(booking_status=booking_status)
        except BookingStatusChain.DoesNotExist:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Not Created', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        request.data["booking_status_chain_id"] = booking_status_chain.id
        booking_statuses_mapping_serializer = BookingStatusesMappingSerializer(data=request.data)
        if booking_statuses_mapping_serializer.is_valid():
            booking_statuses_mapping_serializer.save()
            response = {'status': 'success', 'msg': 'Booking Statuses Mapping Created', 'data':
                {'id': booking_statuses_mapping_serializer.data['id']}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Not Created',
                        'data': booking_statuses_mapping_serializer.errors,
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def create_key_based_bulk(self, request):
        request.data["created_by"] = self.request.user.username
        if 'booking_status' not in request.data:
            response = {'status': 'failure', 'msg': 'booking_status is required field', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if 'manual_booking_id' not in request.data:
            response = {'status': 'failure', 'msg': 'manual_booking_id is required field', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        booking_status_key = request.data['booking_status']
        try:
            booking_status = BookingStatuses.objects.get(status=booking_status_key)
        except BookingStatuses.DoesNotExist:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Not Created', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        try:
            booking_status_chain = BookingStatusChain.objects.get(booking_status=booking_status)
        except BookingStatusChain.DoesNotExist:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Not Created', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        request.data["booking_status_chain_id"] = booking_status_chain.id
        manual_booking_id = request.data['manual_booking_id'].split(',')
        request.data.pop('manual_booking_id')
        bsm_ids = []
        errors = []
        for mbid in manual_booking_id:
            request.data['manual_booking_id'] = mbid
            booking_statuses_mapping_serializer = BookingStatusesMappingSerializer(data=request.data)
            if booking_statuses_mapping_serializer.is_valid():
                booking_statuses_mapping_serializer.save()
                bsm_ids.append(booking_statuses_mapping_serializer.data['id'])
            else:
                errors.append(booking_statuses_mapping_serializer.errors)
            request.data.pop('manual_booking_id')
        if bsm_ids:
            response = {'status': 'success', 'msg': 'Booking Statuses Mapping Created',
                        'data': {'id': bsm_ids}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Not Created',
                        'data': errors, 'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = BookingStatusesMapping.objects.all().exclude(deleted=True)
        booking_statuses_mapping = get_object_or_404(queryset, pk=pk)
        serializer = BookingStatusesMappingSerializer(booking_statuses_mapping)
        response = {'status': 'success', 'msg': 'Booking Statuses Mapping Retrieved', 'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        try:
            booking_statuses_mapping = BookingStatusesMapping.objects.get(id=pk)
        except BookingStatusesMapping.DoesNotExist:
            return Response({"status": "BookingStatusesMapping Doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        booking_statuses_mapping_serializer = BookingStatusesMappingSerializer(
            instance=booking_statuses_mapping, data=request.data)
        if 'due_date' in request.data:
            request.data['due_date'] = datetime.strptime(request.data['due_date'], '%Y-%m-%d')
        if booking_statuses_mapping_serializer.is_valid():
            booking_statuses_m = booking_statuses_mapping_serializer.save()
            if booking_statuses_m:
                response = {'status': 'success', 'msg': 'Booking Statuses Mapping Updated', 'data':
                    {'id': booking_statuses_mapping_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(booking_statuses_mapping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_key_based_bulk(self, request):
        request.data["changed_by"] = request.user.username
        if 'booking_status' not in request.data:
            response = {'status': 'failure', 'msg': 'booking_status is required field', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if 'manual_booking_id' not in request.data:
            response = {'status': 'failure', 'msg': 'manual_booking_id is required field', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        booking_status_key = request.data['booking_status']
        try:
            booking_status = BookingStatuses.objects.get(status=booking_status_key)
        except BookingStatuses.DoesNotExist:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Not Created', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        try:
            booking_status_chain = BookingStatusChain.objects.get(booking_status=booking_status)
        except BookingStatusChain.DoesNotExist:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Not Created', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        request.data["booking_status_chain_id"] = booking_status_chain.id
        manual_booking_id = request.data['manual_booking_id'].split(',')
        request.data.pop('manual_booking_id')
        bsm_ids = []
        errors = []
        for mbid in manual_booking_id:
            request.data['manual_booking_id'] = mbid
            booking = get_or_none(ManualBooking, id=mbid)
            if not booking:
                bsm_ids = []
                break
            bsm = get_or_none(BookingStatusesMapping, manual_booking=booking, booking_status_chain=booking_status_chain)
            if not bsm:
                bsm_ids = []
                break
            booking_statuses_mapping_serializer = BookingStatusesMappingSerializer(instance=bsm, data=request.data)
            if booking_statuses_mapping_serializer.is_valid():
                booking_statuses_mapping_serializer.save()
                bsm_ids.append(booking_statuses_mapping_serializer.data['id'])
            else:
                errors.append(booking_statuses_mapping_serializer.errors)
            request.data.pop('manual_booking_id')
        if bsm_ids:
            response = {'status': 'success', 'msg': 'Booking Statuses Mapping Updated',
                        'data': {'id': bsm_ids}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Not Created',
                        'data': errors, 'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def update_invoice_based(self, request):
        request.data["changed_by"] = request.user.username
        if 'booking_status' not in request.data:
            response = {'status': 'failure', 'msg': 'booking_status is required field', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if 'invoice_number' not in request.data:
            response = {'status': 'failure', 'msg': 'invocie_number is required field', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        booking_status_key = request.data['booking_status']
        try:
            booking_status_chain = BookingStatusChain.objects.get(booking_status__status=booking_status_key)
        except BookingStatusChain.DoesNotExist:
            response = {'status': 'failure', 'msg': 'Booking Statuses Chain Does Not Exist', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        request.data["booking_status_chain_id"] = booking_status_chain.id
        invoice_number = request.data['invoice_number']
        request.data.pop('invoice_number')
        bsm_ids = []
        errors = []
        invoice = get_or_none(Invoice, invoice_number=invoice_number)
        if not invoice:
            response = {'status': 'failure', 'msg': 'Invoice Does Not Exist', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not settings.TESTING:
            send_notification_to_invoice_confirmed_escalated_personnel(invoice.customer_fk,
                                                                   invoice.customer_fk.aaho_office.id, invoice_number)

        for booking in invoice.bookings.all():
            request.data['manual_booking_id'] = booking.id
            bsm = get_or_none(BookingStatusesMapping, manual_booking=booking, booking_status_chain=booking_status_chain)
            if not bsm:
                bsm_ids = []
                break
            booking_statuses_mapping_serializer = BookingStatusesMappingSerializer(instance=bsm, data=request.data)
            if booking_statuses_mapping_serializer.is_valid():
                booking_statuses_mapping_serializer.save()
                bsm_ids.append(booking_statuses_mapping_serializer.data['id'])
            else:
                errors.append(booking_statuses_mapping_serializer.errors)
            request.data.pop('manual_booking_id')
        if bsm_ids:
            response = {'status': 'success', 'msg': 'Booking Statuses Mapping Updated',
                        'data': {'id': bsm_ids}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Not Created',
                        'data': errors, 'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = BookingStatusesMapping.objects.all()
        booking_statuses_mapping = get_object_or_404(queryset, pk=pk)
        serializer = BookingStatusesMappingSerializer(booking_statuses_mapping)
        booking_statuses_mapping.deleted = True
        booking_statuses_mapping.deleted_on = timezone.now()
        booking_statuses_mapping.save()
        response = {'status': 'success', 'msg': 'Booking Statuses Mapping Deleted', 'data':
            {'id': serializer.data['id']}}
        return Response(response, status=status.HTTP_200_OK)


class TaskDashboardFunctionalitiesListView(generics.ListAPIView):
    queryset = TaskDashboardFunctionalities.objects.order_by('-id').exclude(deleted=True)
    serializer_class = TaskDashboardFunctionalitiesSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = TaskDashboardFunctionalitiesFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'functionality')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Task Dashboard Functionality List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class TaskDashboardFunctionalitiesViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for creating, updating, deleting and retrieving Task Dashboard Functionality.

    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        task_dashboard_functionalities_serializer = TaskDashboardFunctionalitiesSerializer(data=request.data)
        if task_dashboard_functionalities_serializer.is_valid():
            task_dashboard_functionalities_serializer.save()
            response = {'status': 'success', 'msg': 'Task Dashboard Functionalities Created', 'data':
                {'id': task_dashboard_functionalities_serializer.data['id']}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(task_dashboard_functionalities_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = TaskDashboardFunctionalities.objects.all().exclude(deleted=True)
        td_func = get_object_or_404(queryset, pk=pk)
        serializer = TaskDashboardFunctionalitiesSerializer(td_func)
        response = {'status': 'success', 'msg': 'Task Dashboard Functionalities Retrieved', 'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        try:
            td_func = TaskDashboardFunctionalities.objects.get(id=pk)
        except TaskDashboardFunctionalities.DoesNotExist:
            return Response({"status": "TaskDashboardFunctionalities Doesn't exists"},
                            status=status.HTTP_400_BAD_REQUEST)
        td_func_serializer = TaskDashboardFunctionalitiesSerializer(instance=td_func, data=request.data)
        if td_func_serializer.is_valid():
            td_func = td_func_serializer.save()
            if td_func:
                response = {'status': 'success', 'msg': 'Task Dashboard Functionalities Updated', 'data':
                    {'id': td_func_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(td_func_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = TaskDashboardFunctionalities.objects.all()
        td_func = get_object_or_404(queryset, pk=pk)
        serializer = TaskDashboardFunctionalitiesSerializer(td_func)
        td_func.deleted = True
        td_func.deleted_on = timezone.now()
        td_func.save()
        response = {'status': 'success', 'msg': 'Task Dashboard Functionalities Deleted', 'data':
            {'id': serializer.data['id']}}
        return Response(response, status=status.HTTP_200_OK)


class EmployeeRolesFunctionalityMappingListView(generics.ListAPIView):
    queryset = EmployeeRolesFunctionalityMapping.objects.order_by('-id').exclude(deleted=True)
    serializer_class = EmployeeRolesFunctionalityMappingSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = EmployeeRolesFunctionalityMappingFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'td_functionality__functionality', 'employee_role__role', 'employee_role__id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK,
                "msg": "Employee Roles Functionality Mapping List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            data["data"] = sorted(data["data"], key=lambda k: k.get('current_functionality_count', 0), reverse=True)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        data["data"] = sorted(data["data"], key=lambda k: k.get('current_functionality_count', 0), reverse=True)
        return Response(data)


class EmployeeRolesFunctionalityMappingViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for creating, updating, deleting and retrieving Employee Roles Functionality Mapping.

    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        employee_roles_functionalities_serializer = EmployeeRolesFunctionalityMappingSerializer(data=request.data)
        if employee_roles_functionalities_serializer.is_valid():
            employee_roles_functionalities_serializer.save()
            response = {'status': 'success', 'msg': 'Employee Roles Functionalities Mapping Created', 'data':
                {'id': employee_roles_functionalities_serializer.data['id']}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(employee_roles_functionalities_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = EmployeeRolesFunctionalityMapping.objects.all().exclude(deleted=True)
        er_func = get_object_or_404(queryset, pk=pk)
        serializer = EmployeeRolesFunctionalityMappingSerializer(er_func)
        response = {'status': 'success', 'msg': 'Employee Roles Functionalities Mapping Retrieved',
                    'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        try:
            td_func = EmployeeRolesFunctionalityMapping.objects.get(id=pk)
        except EmployeeRolesFunctionalityMapping.DoesNotExist:
            return Response({"status": "EmployeeRolesFunctionalityMapping Doesn't exists"},
                            status=status.HTTP_400_BAD_REQUEST)
        er_func_serializer = EmployeeRolesFunctionalityMappingSerializer(instance=td_func, data=request.data)
        if er_func_serializer.is_valid():
            er_func = er_func_serializer.save()
            if er_func:
                response = {'status': 'success', 'msg': 'Employee Roles Functionalities Mapping Updated', 'data':
                    {'id': er_func_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(er_func_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = EmployeeRolesFunctionalityMapping.objects.all()
        er_func = get_object_or_404(queryset, pk=pk)
        serializer = EmployeeRolesFunctionalityMappingSerializer(er_func)
        er_func.deleted = True
        er_func.deleted_on = timezone.now()
        er_func.save()
        response = {'status': 'success', 'msg': 'Employee Roles Functionalities Mapping Deleted', 'data':
            {'id': serializer.data['id']}}
        return Response(response, status=status.HTTP_200_OK)


class BookingStatusesMappingCommentsListView(generics.ListAPIView):
    queryset = BookingStatusesMappingComments.objects.order_by('-id').exclude(deleted=True)
    serializer_class = BookingStatusesMappingCommentsSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = BookingStatusesMappingCommentsFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'booking_status_mapping__id', 'booking_status_mapping__manual_booking__id',
                     'booking_status_mapping__booking_status_chain__booking_status__status', 'comment')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK,
                "msg": "Booking Statuses Mapping Comments List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class BookingStatusesMappingCommentsViewSet(viewsets.ViewSet):
    """
        A simple ViewSet for creating, updating, deleting and retrieving Booking Status Mapping Comments.

        """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        booking_statuses_mapping_comments_serializer = BookingStatusesMappingCommentsSerializer(data=request.data)
        if booking_statuses_mapping_comments_serializer.is_valid():
            booking_statuses_mapping_comments_serializer.save()
            response = {'status': 'success', 'msg': 'Booking Statuses Mapping Comments Created', 'data':
                {'id': booking_statuses_mapping_comments_serializer.data['id']}, 'status_code': status.HTTP_201_CREATED}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Comments Not Created',
                        'data': booking_statuses_mapping_comments_serializer.errors,
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def create_bulk(self, request):
        request.data["created_by"] = self.request.user.username
        if 'booking_status_mapping_id' not in request.data:
            response = {'status': 'failure', 'msg': 'booking_status_mapping_id is required field', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if 'comment' not in request.data:
            response = {'status': 'failure', 'msg': 'comment is required field', 'data': {},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        booking_status_mapping_id = str(request.data['booking_status_mapping_id']).split(',')
        request.data.pop('booking_status_mapping_id')
        bsmc_ids = []
        errors = []
        for bsm_id in booking_status_mapping_id:
            request.data['booking_status_mapping_id'] = bsm_id
            booking_statuses_mapping_comments_serializer = BookingStatusesMappingCommentsSerializer(data=request.data)
            if booking_statuses_mapping_comments_serializer.is_valid():
                booking_statuses_mapping_comments_serializer.save()
                bsmc_ids.append(booking_statuses_mapping_comments_serializer.data['id'])
            else:
                errors.append(booking_statuses_mapping_comments_serializer.errors)
        if bsmc_ids:
            response = {'status': 'success', 'msg': 'Booking Statuses Mapping Comments Created', 'data':
                {'id': bsmc_ids}, 'status_code': status.HTTP_201_CREATED}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Comments Not Created',
                        'data': errors, 'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = BookingStatusesMappingComments.objects.all().exclude(deleted=True)
        er_func = get_object_or_404(queryset, pk=pk)
        if er_func:
            serializer = BookingStatusesMappingCommentsSerializer(er_func)
            response = {'status': 'success', 'msg': 'Booking Statuses Mapping Comments Retrieved',
                        'data': serializer.data, 'status_code': status.HTTP_200_OK}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Comments Not Found',
                        'data': {}, 'status_code': status.HTTP_404_NOT_FOUND}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        try:
            bs_mapping = BookingStatusesMappingComments.objects.get(id=pk)
        except BookingStatusesMappingComments.DoesNotExist:
            return Response({"status": "Booking Statuses Mapping Comments Doesn't exists"},
                            status=status.HTTP_400_BAD_REQUEST)
        bs_mapping_serializer = BookingStatusesMappingCommentsSerializer(instance=bs_mapping, data=request.data)
        if bs_mapping_serializer.is_valid():
            bs_map = bs_mapping_serializer.save()
            if bs_map:
                response = {'status': 'success', 'msg': 'Booking Statuses Mapping Comments Updated', 'data':
                    {'id': bs_mapping_serializer.data['id']}, 'status_code': status.HTTP_202_ACCEPTED}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Comments Not Updated',
                    'data': bs_mapping_serializer.errors, 'status_code': status.HTTP_400_BAD_REQUEST}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = BookingStatusesMappingComments.objects.all()
        er_func = get_object_or_404(queryset, pk=pk)
        serializer = BookingStatusesMappingCommentsSerializer(er_func)
        er_func.deleted = True
        er_func.deleted_on = timezone.now()
        er_func.save()
        response = {'status': 'success', 'msg': 'Booking Statuses Mapping Comments Deleted', 'data':
            {'id': serializer.data['id']}, 'status_code': status.HTTP_200_OK}
        return Response(response, status=status.HTTP_200_OK)


class BookingStatusesMappingLocationListView(generics.ListAPIView):
    queryset = BookingStatusesMappingLocation.objects.order_by('-id').exclude(deleted=True)
    serializer_class = BookingStatusesMappingLocationSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = BookingStatusesMappingLocationFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'booking_status_mapping__id', 'booking_status_mapping__manual_booking__id',
                     'booking_status_mapping__booking_status_chain__booking_status__status', 'latitude', 'longitude')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK,
                "msg": "Booking Statuses Mapping Location List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class BookingStatusesMappingLocationViewSet(viewsets.ViewSet):
    """
        A simple ViewSet for creating, updating, deleting and retrieving Booking Status Mapping Location.

        """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        booking_statuses_mapping_location_serializer = BookingStatusesMappingLocationSerializer(data=request.data)
        if booking_statuses_mapping_location_serializer.is_valid():
            booking_statuses_mapping_location_serializer.save()
            response = {'status': 'success', 'msg': 'Booking Statuses Mapping Location Created', 'data':
                {'id': booking_statuses_mapping_location_serializer.data['id']}, 'status_code': status.HTTP_201_CREATED}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Location Not Created',
                        'data': booking_statuses_mapping_location_serializer.errors,
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def save_location(self, request):
        request.data["created_by"] = self.request.user.username
        if 'google_places' not in request.data:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Location Not Created',
                        'data': {'google_places key required field'}, 'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if 'name' not in request.data['google_places'].keys() or 'latitude' not in request.data['google_places'].keys() \
                or 'longitude' not in request.data['google_places'].keys():
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Location Not Created',
                        'data': {'name, latitude, longitude key in google_places required field'},
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        city = request.data['google_places']['name']
        reverse_geocode = google_reverse_geocode(request.data['google_places']['latitude'],
                                                 request.data['google_places']['longitude'])
        request.data["city"] = city
        request.data["district"] = reverse_geocode['district'] if reverse_geocode['district'] else city
        request.data["state"] = reverse_geocode['state'] if reverse_geocode['state'] else city
        request.data["latitude"] = reverse_geocode['latitude']
        request.data["longitude"] = reverse_geocode['longitude']
        request.data["country"] = 'India'
        booking_statuses_mapping_location_serializer = BookingStatusesMappingLocationSerializer(data=request.data)
        if booking_statuses_mapping_location_serializer.is_valid():
            booking_statuses_mapping_location_serializer.save()
            response = {'status': 'success', 'msg': 'Booking Statuses Mapping Location Created', 'data':
                {'id': booking_statuses_mapping_location_serializer.data['id']}, 'status_code': status.HTTP_201_CREATED}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Location Not Created',
                        'data': booking_statuses_mapping_location_serializer.errors,
                        'status_code': status.HTTP_400_BAD_REQUEST}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = BookingStatusesMappingLocation.objects.all().exclude(deleted=True)
        er_func = get_object_or_404(queryset, pk=pk)
        if er_func:
            serializer = BookingStatusesMappingLocationSerializer(er_func)
            response = {'status': 'success', 'msg': 'Booking Statuses Mapping Location Retrieved',
                        'data': serializer.data}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Location Not Found',
                        'data': {}, 'status_code': status.HTTP_404_NOT_FOUND}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        try:
            bs_mapping = BookingStatusesMappingLocation.objects.get(id=pk)
        except BookingStatusesMappingLocation.DoesNotExist:
            return Response({"status": "Booking Statuses Mapping Location Doesn't exists"},
                            status=status.HTTP_400_BAD_REQUEST)
        bs_mapping_serializer = BookingStatusesMappingLocationSerializer(instance=bs_mapping, data=request.data)
        if bs_mapping_serializer.is_valid():
            bs_map = bs_mapping_serializer.save()
            if bs_map:
                response = {'status': 'success', 'msg': 'Booking Statuses Mapping Location Updated', 'data':
                    {'id': bs_mapping_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        response = {'status': 'failure', 'msg': 'Booking Statuses Mapping Location Not Updated',
                    'data': bs_mapping_serializer.errors, 'status_code': status.HTTP_400_BAD_REQUEST}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = BookingStatusesMappingLocation.objects.all()
        er_func = get_object_or_404(queryset, pk=pk)
        serializer = BookingStatusesMappingLocationSerializer(er_func)
        er_func.deleted = True
        er_func.deleted_on = timezone.now()
        er_func.save()
        response = {'status': 'success', 'msg': 'Booking Statuses Mapping Location Deleted', 'data':
            {'id': serializer.data['id']}, 'status_code': status.HTTP_200_OK}
        return Response(response, status=status.HTTP_200_OK)


class BookingStatusesMonitoringViewSet(viewsets.ViewSet):

    def retrieve_booking_status(self, request, pk=None):
        response = {'status': 'failure', 'msg': 'Booking Statuses Monitoring Not Found',
                    'data': {}, 'status_code': status.HTTP_404_NOT_FOUND}
        emp_roles_response = get_employee_roles(self.request.user)
        if emp_roles_response['status'] == 'success' and ('management' not in emp_roles_response['roles']
                                                          and 'tech' not in emp_roles_response['roles']):
            response['status_code'] = status.HTTP_400_BAD_REQUEST
            response['msg'] = 'User Not allowed to access'
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        filter_params = {'from_date': request.GET.get('from_date', None),
                         'to_date': request.GET.get('to_date', None),
                         'source_office_id': request.GET.get('source_office_id', None),
                         'destination_office_id': request.GET.get('destination_office_id', None),
                         'customer_id': request.GET.get('customer_id', None),
                         'supplier_id': request.GET.get('supplier_id', None),
                         'user': None}
        data = []
        bookings_status_nos = {'header': '#Bookings', 'pre_loading': 0, 'in_transit': 0, 'pod_due': 0,
                               'invoice_pending': 0, 'credit_period': 0, 'payment_due': 0, 'payment_overdue': 0,
                               'payment_received': 0}
        tac = {'header': 'TAC', 'pre_loading': 0, 'in_transit': 0, 'pod_due': 0,
               'invoice_pending': 0, 'credit_period': 0, 'payment_due': 0, 'payment_overdue': 0,
               'payment_received': 0}
        iwp = {'header': 'IWP', 'pre_loading': 0, 'in_transit': 0, 'pod_due': 0,
               'invoice_pending': 0, 'credit_period': 0, 'payment_due': 0, 'payment_overdue': 0,
               'payment_received': 0}
        tao = {'header': 'TAO', 'pre_loading': 0, 'in_transit': 0, 'pod_due': 0,
               'invoice_pending': 0, 'credit_period': 0, 'payment_due': 0, 'payment_overdue': 0,
               'payment_received': 0}
        owp = {'header': 'OWP', 'pre_loading': 0, 'in_transit': 0, 'pod_due': 0,
               'invoice_pending': 0, 'credit_period': 0, 'payment_due': 0, 'payment_overdue': 0,
               'payment_received': 0}

        response = {'status': 'success', 'msg': 'Booking Statuses Monitoring Found',
                    'data': {}, 'status_code': status.HTTP_200_OK}

        data.append(get_bookings_monitoring_status(bookings_status_nos, filter_params))
        data.append(get_bookings_monitoring_tac(tac, filter_params))
        data.append(get_bookings_monitoring_iwp(iwp, filter_params))
        data.append(get_bookings_monitoring_tao(tao, filter_params))
        data.append(get_bookings_monitoring_owp(owp, filter_params))
        response['data'] = data
        return Response(response['data'], status=status.HTTP_200_OK)

    def retrieve_task_status(self, request, pk=None):
        response = {'status': 'failure', 'msg': 'Task Statuses Monitoring Not Found',
                    'data': {}, 'status_code': status.HTTP_404_NOT_FOUND}
        emp_roles_response = get_employee_display_roles(self.request.user)
        if emp_roles_response['status'] == 'success' and ('Management' not in emp_roles_response['roles']
                                                          and 'Technology' not in emp_roles_response['roles']):
            response['status_code'] = status.HTTP_400_BAD_REQUEST
            response['msg'] = 'User Not allowed to access'
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        response = {'status': 'success', 'msg': 'Task Statuses Monitoring Found',
                    'data': {}, 'status_code': status.HTTP_200_OK}
        filter_params = {'from_date': request.GET.get('from_date', None),
                         'to_date': request.GET.get('to_date', None),
                         'role_id': request.GET.get('role_id', None)}
        data = []

        for office in AahoOffice.objects.all():
            if filter_params['role_id']:
                office_roles = set(
                    EmployeeRolesMapping.objects.filter(employee__office=office, employee_role_id=filter_params['role_id']).
                        values_list('employee_role__id', flat=True))
            else:
                office_roles = set(EmployeeRolesMapping.objects.filter(employee__office=office).values_list('employee_role__id', flat=True))
            # office_employees = set(EmployeeRolesMapping.objects.filter(employee__office=office, employee_role__id__in=office_roles).
            #                        values_list('employee__username__profile__name', flat=True))
            for office_role in office_roles:
                emp_role = get_or_none(EmployeeRoles, id=office_role)
                office_employees = set(
                    EmployeeRolesMapping.objects.filter(employee__office=office, employee_role=emp_role).
                    values_list('employee__username__profile__name', flat=True))
                row = {'employee_name': emp_role.get_role()['role'], 'employee_roles': office_employees,
                       'employee_office': office.branch_name}
                data.append(get_tasks_monitoring_row(self.request.user, emp_role.id, office, row, filter_params))

        # for emp in Employee.objects.filter(status='active'):
        #     emp_roles_response = ','.join(get_employee_display_roles(emp.username)['roles'])
        #     row = {'employee_name': emp.emp_name(), 'employee_roles': emp_roles_response,
        #            'employee_office': emp.office.branch_name,
        #            'task_completed_this_week': 0, 'task_completed_this_month': 0, 'pending_tasks': 0,
        #            'overdue_task_less_2_days': 0, 'overdue_task_2_to_7_days': 0, 'overdue_task_7_to_30_days': 0}
        #     data.append(row)
        response['data'] = data
        return Response(response['data'], status=status.HTTP_200_OK)

    def retrieve_ch_booking_status(self, request, pk=None):
        response = {'status': 'failure', 'msg': 'Booking Statuses Monitoring Not Found',
                    'data': {}, 'status_code': status.HTTP_404_NOT_FOUND}
        emp_roles_response = get_employee_roles(self.request.user)
        employee = get_or_none(Employee, username=self.request.user)
        if emp_roles_response['status'] == 'success' and 'city_head' not in emp_roles_response['roles']:
            response['status_code'] = status.HTTP_400_BAD_REQUEST
            response['msg'] = 'User Not allowed to access'
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        filter_params = {'from_date': request.GET.get('from_date', None),
                         'to_date': request.GET.get('to_date', None),
                         'source_office_id': request.GET.get('source_office_id', None),
                         'destination_office_id': request.GET.get('destination_office_id', None),
                         'customer_id': request.GET.get('customer_id', None),
                         'supplier_id': request.GET.get('supplier_id', None),
                         'user': self.request.user}
        data = []
        bookings_status_nos = {'header': '#Bookings', 'pre_loading': 0, 'in_transit': 0, 'pod_due': 0,
                               'invoice_pending': 0, 'credit_period': 0, 'payment_due': 0, 'payment_overdue': 0,
                               'payment_received': 0}
        tac = {'header': 'TAC', 'pre_loading': 0, 'in_transit': 0, 'pod_due': 0,
               'invoice_pending': 0, 'credit_period': 0, 'payment_due': 0, 'payment_overdue': 0,
               'payment_received': 0}
        iwp = {'header': 'IWP', 'pre_loading': 0, 'in_transit': 0, 'pod_due': 0,
               'invoice_pending': 0, 'credit_period': 0, 'payment_due': 0, 'payment_overdue': 0,
               'payment_received': 0}
        tao = {'header': 'TAO', 'pre_loading': 0, 'in_transit': 0, 'pod_due': 0,
               'invoice_pending': 0, 'credit_period': 0, 'payment_due': 0, 'payment_overdue': 0,
               'payment_received': 0}
        owp = {'header': 'OWP', 'pre_loading': 0, 'in_transit': 0, 'pod_due': 0,
               'invoice_pending': 0, 'credit_period': 0, 'payment_due': 0, 'payment_overdue': 0,
               'payment_received': 0}

        response = {'status': 'success', 'msg': 'Booking Statuses Monitoring Found',
                    'data': {}, 'status_code': status.HTTP_200_OK}

        data.append(get_bookings_monitoring_status(bookings_status_nos, filter_params))
        data.append(get_bookings_monitoring_tac(tac, filter_params))
        data.append(get_bookings_monitoring_iwp(iwp, filter_params))
        data.append(get_bookings_monitoring_tao(tao, filter_params))
        data.append(get_bookings_monitoring_owp(owp, filter_params))
        response['data'] = data
        return Response(response['data'], status=status.HTTP_200_OK)

    # def retrieve_ch_task_status(self, request, pk=None):
    #     response = {'status': 'failure', 'msg': 'Task Statuses Monitoring Not Found',
    #                 'data': {}, 'status_code': status.HTTP_404_NOT_FOUND}
    #     emp_roles_response = get_employee_display_roles(self.request.user)
    #     if emp_roles_response['status'] == 'success' and 'City Head' not in emp_roles_response['roles']:
    #         response['status_code'] = status.HTTP_400_BAD_REQUEST
    #         response['msg'] = 'User Not allowed to access'
    #         return Response(response, status=status.HTTP_400_BAD_REQUEST)
    #
    #     response = {'status': 'success', 'msg': 'Task Statuses Monitoring Found',
    #                 'data': {}, 'status_code': status.HTTP_200_OK}
    #     employee = get_or_none(Employee, username=self.request.user)
    #     data = []
    #     for emp in Employee.objects.filter(status='active', office=employee.office):
    #         emp_roles_response = ','.join(get_employee_display_roles(emp.username)['roles'])
    #         row = {'employee_name': emp.emp_name(), 'employee_roles': emp_roles_response,
    #                'employee_office': emp.office.branch_name,
    #                'task_completed_this_week': 0, 'task_completed_this_month': 0, 'pending_tasks': 0,
    #                'overdue_task_less_2_days': 0, 'overdue_task_2_to_7_days': 0, 'overdue_task_7_to_30_days': 0}
    #         data.append(row)
    #     response['data'] = data
    #     return Response(response['data'], status=status.HTTP_200_OK)


class SmePendingPaymentsCommentsListView(generics.ListAPIView):
    queryset = SmePaymentFollowupComments.objects.order_by('-id').exclude(deleted=True)
    serializer_class = SmePendingPaymentsCommentsSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = SmePendingPaymentsCommentsFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'sme__id', 'sme__name__profile__name', 'sme__company_code', 'comment', 'due_date')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Sme Pending Payments Comments List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class SmePendingPaymentsCommentsViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for creating, updating, deleting and retrieving Sme Pending Payments Comments.

    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        sme_pending_payments_comments_serializer = SmePendingPaymentsCommentsSerializer(data=request.data)
        if sme_pending_payments_comments_serializer.is_valid():
            sme_pending_payments_comments_serializer.save()
            response = {'status': 'success', 'msg': 'Sme Pending Payments Comments Created', 'data':
                {'id': sme_pending_payments_comments_serializer.data['id']}}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(sme_pending_payments_comments_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = SmePaymentFollowupComments.objects.all().exclude(deleted=True)
        sme_pending_payments_comments = get_object_or_404(queryset, pk=pk)
        serializer = SmePendingPaymentsCommentsSerializer(sme_pending_payments_comments)
        response = {'status': 'success', 'msg': 'Sme Pending Payments Comments Retrieved', 'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def retrieve_sme(self, request, sme_id=None):
        queryset = SmePaymentFollowupComments.objects.filter(sme_id=sme_id).exclude(deleted=True).order_by('id')
        # sme_pending_payments_comments = get_object_or_404(queryset, pk=pk)
        serializer = SmePendingPaymentsCommentsSerializer(queryset, many=True)
        response = {'status': 'success', 'msg': 'Sme Pending Payments Comments Retrieved', 'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        try:
            sme_pending_payments_comments = SmePaymentFollowupComments.objects.get(id=pk)
        except SmePaymentFollowupComments.DoesNotExist:
            return Response({"status": "Sme Pending Payments Comments Doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        sme_pending_payments_comments_serializer = SmePendingPaymentsCommentsSerializer(instance=sme_pending_payments_comments, data=request.data)
        if sme_pending_payments_comments_serializer.is_valid():
            sme_pending_payments_comments = sme_pending_payments_comments_serializer.save()
            if sme_pending_payments_comments:
                response = {'status': 'success', 'msg': 'Sme Pending Payments Comments Updated', 'data':
                    {'id': sme_pending_payments_comments_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(sme_pending_payments_comments_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_sme(self, request, sme_id=None):
        request.data["changed_by"] = request.user.username
        request.data['sme_id'] = sme_id
        sme_pending_payments_comments = SmePaymentFollowupComments.objects.filter(sme_id=sme_id).exclude(deleted=True).last()
        if not sme_pending_payments_comments:
            request.data["created_by"] = self.request.user.username
            if 'comment' not in request.data:
                request.data['comment'] = 'New Due Date Updated'
            sme_pending_payments_comments_serializer = SmePendingPaymentsCommentsSerializer(data=request.data)
            if sme_pending_payments_comments_serializer.is_valid():
                sme_pending_payments_comments_serializer.save()
                response = {'status': 'success', 'msg': 'Sme Pending Payments Comments Created', 'data':
                    {'id': sme_pending_payments_comments_serializer.data['id']}}
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                return Response(sme_pending_payments_comments_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # return Response({"status": "Sme Pending Payments Comments Doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        if 'comment' not in request.data:
            request.data['comment'] = sme_pending_payments_comments.comment
        sme_pending_payments_comments_serializer = SmePendingPaymentsCommentsSerializer(instance=sme_pending_payments_comments, data=request.data)
        if sme_pending_payments_comments_serializer.is_valid():
            sme_pending_payments_comments = sme_pending_payments_comments_serializer.save()
            if sme_pending_payments_comments:
                response = {'status': 'success', 'msg': 'Sme Pending Payments Comments Updated', 'data':
                    {'id': sme_pending_payments_comments_serializer.data['id']}}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(sme_pending_payments_comments_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        queryset = SmePaymentFollowupComments.objects.all()
        sme_pending_payments_comments = get_object_or_404(queryset, pk=pk)
        serializer = SmePendingPaymentsCommentsSerializer(sme_pending_payments_comments)
        sme_pending_payments_comments.deleted = True
        sme_pending_payments_comments.deleted_on = timezone.now()
        sme_pending_payments_comments.save()
        response = {'status': 'success', 'msg': 'Sme Pending Payments Comments Deleted', 'data':
            {'id': serializer.data['id']}}
        return Response(response, status=status.HTTP_200_OK)