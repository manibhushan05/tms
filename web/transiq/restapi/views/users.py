import json

from django.contrib.auth.models import User
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, generics, filters
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import Profile
from broker.models import Broker
from employee.models import Employee
from restapi.filter.users import UserCategoryFilter, UserFilters
from restapi.helper_api import get_broker_user_data
from restapi.helper_api import get_supplier_user_data, get_employee_user_data
from restapi.models import UserCategory, EmployeeRolesMapping, EmployeeRolesFunctionalityMapping
from restapi.search import CustomSearch
from restapi.serializers.authentication import UserSerializer
from restapi.serializers.task_dashboard import EmployeeRolesFunctionalityMappingSerializer
from restapi.serializers.users import UserCategorySerializer
from sme.models import Sme, ContactDetails
from supplier.models import Supplier
from utils.models import Bank
import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('username')
    search_fields = ['id', 'username', 'profile__name', 'profile__phone']
    filter_class = UserFilters

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "User List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)

    def get_queryset(self):
        # active_account = self.request.GET.get('active_account', None)
        # if 'active_account' == active_account:
        #     return User.objects.filter(is_active=True)
        return User.objects.order_by('-id')


class UserCategoryListView(generics.ListAPIView):
    queryset = UserCategory.objects.order_by('-id').exclude(deleted=True)
    serializer_class = UserCategorySerializer
    # pagination_class = StandardResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = UserCategoryFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'category')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "User Category List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(serializer.data)


class UserCategoryViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving user category.

    """

    def create(self, request):
        user_category_serializer = UserCategorySerializer(data=request.data)
        if user_category_serializer.is_valid():
            user_category_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "User Created",
                "data": user_category_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "User not Created",
            "data": user_category_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = UserCategory.objects.all().exclude(deleted=True)
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserCategorySerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        try:
            user = UserCategory.objects.get(id=pk)
        except UserCategory.DoesNotExist:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "Failure",
                "msg": "User Doesn't exists",
                "data": {}
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        user_category_serializer = UserCategorySerializer(instance=user, data=request.data)
        if user_category_serializer.is_valid():
            user = user_category_serializer.save()
            if user:
                response = {
                    "status_code": status.HTTP_202_ACCEPTED,
                    "status": "Success",
                    "msg": "User Updated",
                    "data": user_category_serializer.data
                }
                return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "User not Updated",
            "data": user_category_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = UserCategory.objects.all()
        user_category = get_object_or_404(queryset, pk=pk)
        serializer = UserCategorySerializer(user_category)
        user_category.deleted = True
        user_category.deleted_on = timezone.now()
        user_category.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserInitialData(APIView):
    """
    A simple APIView for getting User's initial data.

    """

    def get(self, request, *args, **kwargs):
        data = {}
        failure_msg = {'status': 'failure', 'msg': 'category_id field is required'}
        category_id = request.GET.get('category_id')
        if not category_id:
            failure_msg['msg'] = 'category_id field can not be blank'
            return Response(failure_msg, status=status.HTTP_400_BAD_REQUEST)
        if not category_id.isnumeric():
            failure_msg['msg'] = 'User Category should be a number'
            return Response(failure_msg, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_category = UserCategory.objects.get(id=category_id)
        except UserCategory.DoesNotExist:
            failure_msg['msg'] = 'User Category Does Not Exist'
            return Response(failure_msg, status=status.HTTP_400_BAD_REQUEST)

        if user_category.category.lower() == 'customer'.lower():
            response = self.get_customer_data(request)
            if response['status'] == 'failure':
                failure_msg = {'status': 'failure', 'msg': response['msg']}
                return Response(failure_msg, status=status.HTTP_400_BAD_REQUEST)
            data.update(response['data'])
            return Response(data, status=status.HTTP_200_OK)
        elif user_category.category.lower() == 'supplier'.lower():
            response = self.get_supplier_data(request)
            if response['status'] == 'failure':
                failure_msg = {'status': 'failure', 'msg': response['msg']}
                return Response(failure_msg, status=status.HTTP_400_BAD_REQUEST)
            data.update(response['data'])
            return Response(data, status=status.HTTP_200_OK)
        elif user_category.category.lower() == 'broker'.lower():
            response = self.get_broker_data(request)
            if response['status'] == 'failure':
                failure_msg = {'status': 'failure', 'msg': response['msg']}
                return Response(failure_msg, status=status.HTTP_400_BAD_REQUEST)
            data.update(response['data'])
            return Response(data, status=status.HTTP_200_OK)
        elif user_category.category.lower() == 'employee'.lower():
            response = self.get_employee_data(request)
            if response['status'] == 'failure':
                failure_msg = {'status': 'failure', 'msg': response['msg']}
                return Response(failure_msg, status=status.HTTP_400_BAD_REQUEST)
            data.update(response['data'])
            return Response(data, status=status.HTTP_200_OK)
        failure_msg = {'status': 'failure', 'msg': 'User Category Is Not Supported'}
        return Response(failure_msg, status=status.HTTP_200_OK)

    def get_customer_data(self, request):
        # Customer data
        customer_id = ''
        aaho_office_id = ''
        try:
            sme = Sme.objects.get(name=request.user)
            contact = ContactDetails.objects.filter(status='active', sme=sme).order_by('type')[0]
            customer_id = sme.id
            aaho_office = sme.aaho_office
            if not aaho_office:
                aaho_office_id = sme.aaho_poc.office.id
            else:
                aaho_office_id = sme.aaho_office.id
        except Sme.DoesNotExist:
            return {'status': 'failure', 'msg': 'User Customer does not exist', 'data': {}}
        except IndexError:
            contact = ContactDetails.objects.create(sme=sme, name=request.user.first_name)

        from customer.views import get_user_data
        data = {
            'user': get_user_data(request.user, contact, sme),
            'customer_id': customer_id,
            'aaho_office_id': aaho_office_id
        }
        return {'status': 'success', 'data': data}

    def get_supplier_data(self, request):
        # supplier data
        try:
            supplier = Supplier.objects.get(user=request.user)
        except Supplier.DoesNotExist:
            return {'status': 'failure', 'msg': 'User Supplier does not exist', 'data': {}}
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user, name=request.user.first_name, email=request.user.email)
        accounts = Bank.objects.filter(user=request.user)
        accounts_data = []
        for ac in accounts:
            ac_data = ac.to_json()
            accounts_data.append(ac_data)
        data = {
            'user': get_supplier_user_data(request.user, profile, supplier),
            'accounts_data': accounts_data,
            'aaho_office': supplier.aaho_office.to_json() if supplier.aaho_office else {},
        }
        return {'status': 'success', 'data': data}

    def get_broker_data(self, request):
        # broker data
        user = request.user
        try:
            broker = Broker.objects.get(name=user)
        except Broker.DoesNotExist:
            return {'status': 'failure', 'msg': 'User Broker does not exist', 'data': {}}
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user, name=user.first_name, email=user.email)
        accounts = Bank.objects.filter(user=user)
        accounts_data = []
        for ac in accounts:
            ac_data = ac.to_json()
            accounts_data.append(ac_data)
        data = {
            'user': get_broker_user_data(user, profile, broker=broker),
            'accounts_data': accounts_data,
            'aaho_office': broker.aaho_office.to_json() if broker.aaho_office else {},
        }
        return {'status': 'success', 'data': data}

    def get_employee_data(self, request):
        # Employee Data
        try:
            employee = Employee.objects.get(username=request.user)
        except Employee.DoesNotExist:
            return {'status': 'failure', 'msg': 'Employee does not exist', 'data': {}}
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user, name=request.user.first_name, email=request.user.email)
        data = {
            'user': get_employee_user_data(request.user, profile, employee),
        }
        return {'status': 'success', 'data': data}


class UserInitialTDFunctionalitiesData(viewsets.ViewSet):
    # @method_decorator(cache_page(60))
    def retrieve_td_func_data(self, request, pk=None):
        failure_msg = {'status': 'failure', 'msg': 'Initial TD Data could not be retrieved', 'data': {},
                       'status_code': status.HTTP_400_BAD_REQUEST}
        category = request.GET.get('category')
        if not category:
            failure_msg['msg'] = 'category field can not be blank'
            return Response(failure_msg, status=status.HTTP_400_BAD_REQUEST)
        if category != 'employee':
            failure_msg['msg'] = 'User category is not found'
            return Response(failure_msg, status=status.HTTP_400_BAD_REQUEST)
        employee_roles_ids = EmployeeRolesMapping.objects.filter(employee__username=request.user).exclude(deleted=True). \
            values_list('employee_role_id', flat=True)
        if not employee_roles_ids:
            failure_msg['msg'] = 'Employee Roles not found'
            return Response(failure_msg, status=status.HTTP_400_BAD_REQUEST)
        erfms = EmployeeRolesFunctionalityMapping.objects.filter(employee_role_id__in=employee_roles_ids).exclude(
            deleted=True)
        if not erfms:
            failure_msg['msg'] = 'Employee Functionalities not found'
            return Response(failure_msg, status=status.HTTP_400_BAD_REQUEST)
        context = {'request': request}
        # data = sorted(data, key=lambda k: k.get('current_functionality_count', 0), reverse=True)
        serializer = EmployeeRolesFunctionalityMappingSerializer(erfms, context=context, many=True)
        u_data = []
        for d in serializer.data:
            if d['td_functionality_id'] not in [td['td_functionality_id'] for td in u_data]:
                u_data.append(d)
        success_msg = {'status': 'success', 'msg': 'Employee TD Functionalities retrieved', 'data': u_data,
                       'status_code': status.HTTP_200_OK}
        return Response(success_msg, status=status.HTTP_200_OK)
