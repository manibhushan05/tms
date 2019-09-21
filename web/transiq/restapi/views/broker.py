from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters, generics
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response

from authentication.models import Profile
from broker.models import Broker, BrokerVehicle, BrokerOwner, BrokerDriver, BrokerAccount, BrokerSummary
from employee.models import Employee
from restapi.filter.broker import BrokerFilter, BrokerVehicleFilter, BrokerOwnerFilter, BrokerDriverFilter, \
    BrokerAccountFilter
from restapi.helper_api import error_response, success_response, generate_username, generate_broker_code, \
    get_employee_roles
from restapi.pagination import CustomeDatatablesPaginator
from restapi.parser.updatawebdata import parse_broker_update_data
from restapi.search import CustomSearch
from restapi.serializers.authentication import ProfileSerializer, UserSerializer
from restapi.serializers.broker import BrokerSerializer, BrokerVehicleSerializer, BrokerOwnerSerializer, \
    BrokerDriverSerializer, BrokerAccountSerializer, BrokerSummarySerializer
from restapi.utils import get_or_none
from utils.models import State


class BrokerListView(generics.ListAPIView):
    serializer_class = BrokerSerializer
    pagination_class = CustomeDatatablesPaginator
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = BrokerFilter
    ordering_fields = ('id',)

    search_fields = (
        'id', 'code', 'name__username', 'name__profile__name', 'name__profile__phone', 'address__line1', 'city__name',
        'aaho_office__branch_name', 'route',
        'aaho_poc__username__username', 'pan', 'broker_vehicle__vehicle__vehicle_number', 'created_on')

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

    def get_queryset(self):
        employee = get_or_none(Employee, username=self.request.user)
        if self.request.GET.get('broker_data_category') == 'web_brokers_records' and isinstance(employee, Employee):
            emp_roles_response = get_employee_roles(self.request.user)
            if emp_roles_response['status'] == 'failure':
                return Broker.objects.none()
            elif ('management' in emp_roles_response['roles'] or 'tech' in emp_roles_response['roles']):
                return Broker.objects.exclude(Q(deleted=True) | Q(name__profile=None))
            else:
                return Broker.objects.filter(aaho_office__in=employee.office_multiple.all())

        return Broker.objects.exclude(deleted=True).exclude(name__profile=None).order_by('-id')


class BrokerSummaryListView(generics.ListAPIView):
    serializer_class = BrokerSummarySerializer
    pagination_class = CustomeDatatablesPaginator
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    # filter_class = OwnerVehicleFilter
    search_fields = (
        'id', 'broker__name__profile__name', 'broker__name__profile__phone', 'broker__aaho_poc__username__profile__name')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Success", "status_code": status.HTTP_200_OK, "msg": "Broker Summary List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)

    def get_queryset(self):
        emp_roles_response = get_employee_roles(self.request.user)
        queryset = BrokerSummary.objects.exclude(deleted=True).exclude(broker__name__profile=None).annotate(
            completed_pod_balance_amount=RawSQL(
                "(accounting_summary->>%s)::numeric", ("completed_pod_balance_amount",))
        ).order_by('-completed_pod_balance_amount')
        if emp_roles_response['status'] == 'success' and ('city_head' in emp_roles_response['roles']):
            employee = get_or_none(Employee, username=self.request.user)
            if isinstance(employee, Employee):
                queryset = queryset.filter(broker__aaho_office__in=employee.office_multiple.all())
        return queryset


class BrokerViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Broker
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def create(self, request):
        if "created_by" not in request.data:
            request.data["created_by"] = self.request.user.username
        if "changed_by" not in request.data:
            request.data["changed_by"] = request.user.username
        try:
            profile_data = {
                "name": request.data["user"],
                "phone": request.data["phone"],
                "email": request.data.get("email", None),
                "city": request.data.get("city", None),
                "alternate_phone": request.data.get("alternate_phone", None),
                "contact_person_name": request.data.get("contact_person_name", None),
                "contact_person_phone": request.data.get("contact_person_phone", None),
                "comment": request.data.get("remarks", None)
            }
        except KeyError:
            return Response({"error": "Key Error"}, status=status.HTTP_400_BAD_REQUEST)
        username = generate_username(profile_data["name"], profile_data["phone"], profile_data["email"])
        password = "X@RWERT21RW!@#"
        user = UserSerializer(data={"username": username, "password": password})
        if user.is_valid():
            user = user.save()
            profile_data["user"] = user.id
            profile = ProfileSerializer(data=profile_data)
            if profile.is_valid():
                profile.save()
                code = generate_broker_code()
                request.data["name"] = user.id
                if "code" not in request.data:
                    request.data["code"] = code
                request.data["supplier_phone"] = profile_data["phone"]
                if isinstance(request.data.get('destination_state', []), list) and 'select_all' in request.data.get(
                        'destination_state', []):
                    request.data['destination_state'] = State.objects.values_list('id', flat=True)
                broker_serializer = BrokerSerializer(data=request.data)
                if broker_serializer.is_valid():
                    broker_serializer.save()
                    response = {
                        "status_code": status.HTTP_201_CREATED,
                        "status": "Success",
                        "msg": "Supplier Created",
                        "data": broker_serializer.data
                    }
                    return Response(data=response, status=status.HTTP_201_CREATED)
                response = {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "status": "Error",
                    "msg": "Supplier not Created",
                    "data": broker_serializer.errors
                }
                return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
            user.delete()
            return Response(profile.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        broker = get_or_none(Broker, id=pk)
        if not isinstance(broker, Broker):
            return Response({"error": "Broker does not exist"}, status=status.HTTP_404_NOT_FOUND)
        dest_states = []
        if "destination_state" in request.data.keys():
            dest_states = request.data.pop('destination_state')
        if dest_states:
            if 'select_all' in dest_states:
                dest_states = State.objects.values_list('id', flat=True)
            request.data["destination_state"] = dest_states
        broker_serializer = BrokerSerializer(instance=broker, data=request.data)
        if broker_serializer.is_valid():
            broker_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Broker Updated",
                "data": broker_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Broker not Updated",
            "data": broker_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):

        broker = get_or_none(Broker, id=pk)
        if not isinstance(broker, Broker):
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Broker Doesnot Exists', data={})

        profile = get_or_none(Profile, user=broker.name)
        request.data["changed_by"] = self.request.user.username
        parsed_data = parse_broker_update_data(request.data, id=pk)
        if isinstance(profile, Profile) and parsed_data['profile_data']:
            profile_serializer = ProfileSerializer(instance=profile, data=parsed_data['profile_data'], partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                return error_response(
                    status=status.HTTP_400_BAD_REQUEST, msg='Invalid owner data', data=profile_serializer.errors)
        else:
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Profile Doesnot Exists', data={})
        broker_serializer = BrokerSerializer(
            instance=broker,
            data=parsed_data,
            partial=True
        )
        if broker_serializer.is_valid():
            broker_serializer.save()
            return success_response(status=status.HTTP_202_ACCEPTED, msg='Broker updated', data=broker_serializer.data)
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Something went wrong',
                              data=broker_serializer.errors)

    def retrieve(self, request, pk=None):
        broker = get_or_none(Broker, id=pk)
        if not isinstance(broker, Broker):
            return Response({"error": "Broker does not exist"}, status=status.HTTP_404_NOT_FOUND)
        broker_serializer = BrokerSerializer(broker)
        return Response(broker_serializer.data, template_name='team/registrations/update-supplier.html',
                        status=status.HTTP_200_OK)


class BrokerVehicleListView(generics.ListAPIView):
    queryset = BrokerVehicle.objects.order_by('-id').exclude(deleted=True)
    serializer_class = BrokerVehicleSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = BrokerVehicleFilter
    search_fields = ('id',
                     'broker__name__username', 'vehicle__vehicle_number', 'vehicle__body_type',
                     'broker__name__profile__name',
                     'broker__name__profile__phone', 'account_details__account_number', 'account_details__bank',
                     'account_details__ifsc')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "Broker Vehicle List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class BrokerVehicleViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Broker Vehicle
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        broker_vehicle_serializer = BrokerVehicleSerializer(data=request.data)
        if broker_vehicle_serializer.is_valid():
            broker_vehicle_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Broker Vehicle Created",
                "data": broker_vehicle_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Broker Vehicle not Created",
            "data": broker_vehicle_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        broker_vehicle = get_or_none(BrokerVehicle, id=pk)
        if not isinstance(broker_vehicle, BrokerVehicle):
            return Response({"error": "Broker Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        broker_vehicle_serializers = BrokerVehicleSerializer(instance=broker_vehicle, data=request.data)
        if broker_vehicle_serializers.is_valid():
            broker_vehicle_serializers.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Broker Vehicle Updated",
                "data": broker_vehicle_serializers.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Broker Vehicle not Updated",
            "data": broker_vehicle_serializers.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        broker_vehicle = get_or_none(BrokerVehicle, id=pk)
        if not isinstance(broker_vehicle, BrokerVehicle):
            return Response({"error": "Broker Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        broker_vehicle_serializers = BrokerVehicleSerializer(
            instance=broker_vehicle,
            data=request.data,
            partial=True
        )
        if broker_vehicle_serializers.is_valid():
            broker_vehicle_serializers.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Broker Vehicle Updated",
                "data": broker_vehicle_serializers.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Broker Vehicle not Updated",
            "data": broker_vehicle_serializers.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        broker_vehicle = get_or_none(BrokerVehicle, id=pk)
        if not isinstance(broker_vehicle, BrokerVehicle):
            return Response({"error": "Broker Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        broker_vehicle_serializers = BrokerVehicleSerializer(broker_vehicle)
        return Response(broker_vehicle_serializers.data, status=status.HTTP_200_OK)


class BrokerOwnerListView(generics.ListAPIView):
    queryset = BrokerOwner.objects.order_by('-id').exclude(deleted=True)
    serializer_class = BrokerOwnerSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = BrokerOwnerFilter
    search_fields = ('id', 'broker__name__username', 'owner__name__username')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "Broker Owner List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(serializer.data)


class BrokerOwnerViewSet(viewsets.ViewSet):
    """
            API for CRUP operation on Broker Owner
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        broker_owner_serializer = BrokerOwnerSerializer(data=request.data)
        if broker_owner_serializer.is_valid():
            broker_owner_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Broker Owner Created",
                "data": broker_owner_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Broker Owner not Created",
            "data": broker_owner_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        broker_owner = get_or_none(BrokerOwner, id=pk)
        if not isinstance(broker_owner, BrokerOwner):
            return Response({"error": "Broker Owner does not exist"}, status=status.HTTP_404_NOT_FOUND)
        broker_owner_serializer = BrokerOwnerSerializer(broker_owner, data=request.data)

        if broker_owner_serializer.is_valid():
            broker_owner_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Broker Owner Updated",
                "data": broker_owner_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Broker Owner not Updated",
            "data": broker_owner_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        broker_owner = get_or_none(BrokerOwner, id=pk)
        if not isinstance(broker_owner, BrokerOwner):
            return Response({"error": "Broker Owner does not exist"}, status=status.HTTP_404_NOT_FOUND)
        broker_owner_serializer = BrokerOwnerSerializer(
            instance=broker_owner,
            data=request.data,
            partial=True
        )

        if broker_owner_serializer.is_valid():
            broker_owner_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Broker Owner Updated",
                "data": broker_owner_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Broker Owner not Updated",
            "data": broker_owner_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        broker_owner = get_or_none(BrokerOwner, id=pk)
        if isinstance(broker_owner, BrokerOwner):
            broker_owner_serializer = BrokerOwnerSerializer(broker_owner)
            return Response(broker_owner_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Broker Owner does not exist"}, status=status.HTTP_404_NOT_FOUND)


class BrokerDriverListView(generics.ListAPIView):
    queryset = BrokerDriver.objects.order_by('-id').exclude(deleted=True)
    serializer_class = BrokerDriverSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = BrokerDriverFilter
    search_fields = (
        'id', 'driver__name', 'driver__phone', 'broker__name__profile__name', 'broker__name__profile__phone')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "Broker Driver List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(serializer.data)


class BrokerDriverViewSet(viewsets.ViewSet):
    """
            API for CRUP operation on Broker Driver
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        broker_driver_serializer = BrokerDriverSerializer(data=request.data)
        if broker_driver_serializer.is_valid():
            broker_driver_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Broker Driver Created",
                "data": broker_driver_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Broker Driver not Created",
            "data": broker_driver_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        broker_driver = get_or_none(BrokerDriver, id=pk)
        if not isinstance(broker_driver, BrokerDriver):
            return Response({"error": "Broker Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)
        broker_driver_serializer = BrokerDriverSerializer(broker_driver, data=request.data)

        if broker_driver_serializer.is_valid():
            broker_driver_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Broker Driver Updated",
                "data": broker_driver_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Broker Driver not Updated",
            "data": broker_driver_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        broker_driver = get_or_none(BrokerDriver, id=pk)
        if not isinstance(broker_driver, BrokerDriver):
            return Response({"error": "Broker Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)
        broker_driver_serializer = BrokerDriverSerializer(
            instance=broker_driver,
            data=request.data,
            partial=True
        )

        if broker_driver_serializer.is_valid():
            broker_driver_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Broker Driver Updated",
                "data": broker_driver_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Broker Driver not Updated",
            "data": broker_driver_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        broker_driver = get_or_none(BrokerDriver, id=pk)
        if isinstance(broker_driver, BrokerDriver):
            broker_driver_serializer = BrokerDriverSerializer(broker_driver)
            return Response(broker_driver_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Broker Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)


class BrokerAccountListView(generics.ListAPIView):
    queryset = BrokerAccount.objects.order_by('-id').exclude(deleted=True)
    serializer_class = BrokerAccountSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = BrokerAccountFilter
    search_fields = ('id', 'broker__name__username', 'broker__name__profile__name', 'broker__name__profile__phone')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Broker Vehicle List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(serializer.data)


class BrokerAccountViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Broker Account
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        broker_account_serializer = BrokerAccountSerializer(data=request.data)
        if broker_account_serializer.is_valid():
            broker_account_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "BrokerAccount Created",
                "data": broker_account_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "BrokerAccount not Created",
            "data": broker_account_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        broker_account = get_or_none(BrokerAccount, id=pk)
        if not isinstance(broker_account, BrokerAccount):
            return Response({"error": "BrokerAccount does not exist"}, status=status.HTTP_404_NOT_FOUND)
        broker_account_serializer = BrokerAccountSerializer(broker_account, data=request.data)

        if broker_account_serializer.is_valid():
            broker_account_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "BrokerAccount Updated",
                "data": broker_account_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "BrokerAccount not Updated",
            "data": broker_account_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        broker_account = get_or_none(BrokerAccount, id=pk)
        if not isinstance(broker_account, BrokerAccount):
            return Response({"error": "BrokerAccount does not exist"}, status=status.HTTP_404_NOT_FOUND)
        broker_account_serializer = BrokerAccountSerializer(
            instance=broker_account,
            data=request.data,
            partial=True
        )

        if broker_account_serializer.is_valid():
            broker_account_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "BrokerAccount Updated",
                "data": broker_account_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "BrokerAccount not Updated",
            "data": broker_account_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        broker_account = get_or_none(BrokerAccount, id=pk)
        if isinstance(broker_account, BrokerAccount):
            broker_account_serializer = BrokerAccountSerializer(broker_account)
            return Response(broker_account_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "BrokerAccount does not exist"}, status=status.HTTP_404_NOT_FOUND)

# class DocumentViewSet(viewsets.ViewSet):
#     """
#         API for CRUP operation on Document
#     """
#
#     def create(self, request):
#         document_serializer = DocumentSerializer(data=request.data)
#         if document_serializer.is_valid():
#             document_serializer.save()
#             return Response(document_serializer.data, status=status.HTTP_201_CREATED)
#         return Response(document_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def update(self, request, pk=None):
#
#         document = get_or_none(Document, id=pk)
#         if not isinstance(document, Document):
#             return Response({"error": "Document does not exist"}, status=status.HTTP_404_NOT_FOUND)
#         document_serializer = DocumentSerializer(document, data=request.data)
#
#         if document_serializer.is_valid():
#             document_serializer.save()
#             return Response(document_serializer.data, status=status.HTTP_202_ACCEPTED)
#         return Response(document_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def partial_update(self, request, pk=None):
#         document = get_or_none(Document, id=pk)
#         if not isinstance(document, Document):
#             return Response({"error": "Document does not exist"}, status=status.HTTP_404_NOT_FOUND)
#         document_serializer = DocumentSerializer(
#             instance=document,
#             data=request.data,
#             partial=True
#         )
#
#         if document_serializer.is_valid():
#             document_serializer.save()
#             return Response(document_serializer.data, status=status.HTTP_202_ACCEPTED)
#         return Response(document_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def retrieve(self, request, pk=None):
#         document = get_or_none(Document, id=pk)
#         if isinstance(document, Document):
#             document_serializer = DocumentSerializer(document)
#             return Response(document_serializer.data, status=status.HTTP_200_OK)
#         return Response({"error": "Document does not exist"}, status=status.HTTP_404_NOT_FOUND)
