from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics, filters
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response

from api import s3util
from api.models import S3Upload
from api.utils import to_int, int_or_none
from authentication.models import Profile
from fileupload.models import DriverFile, VehicleFile, OwnerFile
from fms.views import validate_url
from owner.vehicle_util import compare_format
from restapi.filter.supplier import DriverFilter
from restapi.filter.supplier import VehicleFilter, SupplierFilter, ContactPersonFilter, DriverPhoneFilter, \
    VehicleBodyCategoryFilter, VehicleStatusFilter, VehicleInsurerFilter, VehicleInsuranceFilter, VehiclePUCFilter, \
    VehicleFitnessFilter, VehiclePermitFilter, ServiceFilter, DriverVehicleFilter, SupplierVehicleFilter
from restapi.filter.utils import VehicleCategoryFilter
from restapi.helper_api import success_response, error_response
from restapi.pagination import CustomeDatatablesPaginator
from restapi.parser.supplier import parse_supplier_registration_data, parse_driver_registration_data, \
    parse_vehicle_registration_data, parse_driver_update_form, parse_vehicle_update_data, parse_supplier_update_data, \
    generate_username
from restapi.search import CustomSearch
from restapi.serializers.authentication import UserSerializer, ProfileSerializer
from restapi.serializers.supplier import ServiceSerializer, SupplierSerializer, VehicleCategorySerializer, \
    VehicleBodyCategorySerializer, VehicleSerializer, ContactPersonSerializer, DriverPhoneSerializer, \
    DriverVehicleSerializer, VehicleStatusSerializer, VehicleInsurerSerializer, VehicleInsuranceSerializer, \
    VehiclePUCSerializer, VehicleFitnessSerializer, VehiclePermitSerializer, SupplierVehicleSerializer, \
    FMSVehicleSerializer, DriverSerializer, SupplierAccountingSummarySerializer, VehicleAccountingSummarySerializer
from restapi.service.documents import get_new_serial
from restapi.service.driver import parse_supplier_driver_docs
from restapi.service.fms import parse_vehicle_docs
from restapi.utils import get_or_none
from supplier.models import Service, Supplier, Vehicle, ContactPerson, DriverPhone, DriverVehicle, \
    VehicleStatus, VehicleInsurer, VehicleInsurance, VehiclePUC, VehicleFitness, VehiclePermit, SupplierVehicle, Driver, \
    SupplierAccountingSummary, VehicleAccountingSummary
from utils.models import VehicleCategory, VehicleBodyCategory, State


class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.order_by('-id').exclude(deleted=True)
    serializer_class = ServiceSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = ServiceFilter
    search_fields = ('id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Service List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class ServiceViewSet(viewsets.ViewSet):
    def list(self, request):
        page_size = to_int(request.GET.get('page_size'))
        search_key = request.GET.get('search')
        services = Service.objects.exclude(deleted=True)
        serializer = ServiceSerializer(services[:page_size], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        service_serializer = ServiceSerializer(data=request.data)
        if service_serializer.is_valid():
            service_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Service Created",
                "data": service_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Service not Created",
            "data": service_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        service = get_or_none(Service, id=pk)
        if not isinstance(service, Service):
            return Response({"error": "Service does not exist"}, status=status.HTTP_404_NOT_FOUND)
        service_serializer = ServiceSerializer(service, data=request.data)

        if service_serializer.is_valid():
            service_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Service Updated",
                "data": service_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Service not Updated",
            "data": service_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        service = get_or_none(Service, id=pk)
        if not isinstance(service, Service):
            return Response({"error": "Service does not exist"}, status=status.HTTP_404_NOT_FOUND)
        service_serializer = ServiceSerializer(
            instance=service,
            data=request.data,
            partial=True
        )

        if service_serializer.is_valid():
            service_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Service Updated",
                "data": service_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Service not Updated",
            "data": service_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        service = get_or_none(Service, id=pk)
        if isinstance(service, Service):
            service_serializer = ServiceSerializer(service)
            return Response(service_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Service does not exist"}, status=status.HTTP_404_NOT_FOUND)


class SupplierListView(generics.ListAPIView):
    queryset = Supplier.objects.order_by('-id').exclude(deleted=True)
    serializer_class = SupplierSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = SupplierFilter
    search_fields = ('id', 'user__profile__name', 'user__profile__phone')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Broker List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)
        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)

    def get_queryset(self):
        if self.request.GET.get('owner', None):
            return Supplier.objects.filter(suppliervehicle__ownership='O').exclude(deleted=True).order_by('-id')
        return Supplier.objects.exclude(deleted=True).order_by('-id')


class SupplierAccountingSummaryListView(generics.ListAPIView):
    serializer_class = SupplierAccountingSummarySerializer
    pagination_class = CustomeDatatablesPaginator
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    # filter_class = OwnerVehicleFilter
    search_fields = (
        'id', 'supplier__user__profile__name', 'supplier__user__profile__phone',
        'supplier__aaho_poc__username__profile__name')

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
        queryset = SupplierAccountingSummary.objects.exclude(deleted=True).exclude(
            supplier__user__profile=None).annotate(
            completed_pod_balance_amount=RawSQL(
                "(accounting_summary->>%s)::numeric", ("completed_pod_balance_amount",))
        ).order_by('-completed_pod_balance_amount')

        return queryset


class SupplierViewSet(viewsets.ViewSet):
    """
            API for CRUP operation on OutWard Payment
        """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    parser_classes = (MultiPartParser, JSONParser)

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        if isinstance(request.data.get('serving_states', []), list) and 'select_all' in request.data.get(
                'serving_states', []):
            request.data['serving_states'] = State.objects.values_list('id', flat=True)
        data = parse_supplier_registration_data(request.data)
        user_serializer = UserSerializer(data=data['user'])
        is_valid_data = True
        error_message = []
        error_data = []
        supplier_serializer = ''
        user_data = []
        if user_serializer.is_valid():
            user = user_serializer.save()
            user_data.append(user.id)
            profile_data = data['profile']
            profile_data['user'] = user.id
            profile_serializer = ProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save()
                supplier_data = data['supplier']
                supplier_data['user'] = user.username
                supplier_serializer = SupplierSerializer(data=supplier_data)
                if supplier_serializer.is_valid():
                    supplier = supplier_serializer.save()
                    for vehicle in request.data.get('owned_trucks', []):
                        supplier_vehicle_serializer = SupplierVehicleSerializer(data={
                            'supplier': supplier.id,
                            'vehicle': vehicle,
                            'created_by': self.request.user.username,
                            'changed_by': self.request.user.username,
                            'ownership': 'O',
                            'active': True
                        })
                        if supplier_vehicle_serializer.is_valid():
                            supplier_vehicle_serializer.save()
                        else:
                            is_valid_data = True
                            error_message.append('Invalid Supplier Vehicle data')
                            error_data.append(supplier_vehicle_serializer.errors)
                    for contact_person in data.get('contact_person'):
                        contact_person_user_data = contact_person['user']
                        contact_person_user_serializer = UserSerializer(data=contact_person_user_data)
                        if contact_person_user_serializer.is_valid():
                            contact_person_user = contact_person_user_serializer.save()
                            user_data.append(contact_person_user.id)
                            contact_person_profile_data = contact_person['profile']
                            contact_person_profile_data['user'] = contact_person_user.id
                            contact_person_profile_serializer = ProfileSerializer(data=contact_person_profile_data)
                            if contact_person_profile_serializer.is_valid():
                                contact_person_profile_serializer.save()
                                contact_person_data = {
                                    'user': contact_person_user.username,
                                    'supplier': supplier.id,
                                    'changed_by': self.request.user.username,
                                    'created_by': self.request.user.username
                                }
                                contact_person_serializer = ContactPersonSerializer(data=contact_person_data)
                                if contact_person_serializer.is_valid():
                                    contact_person_serializer.save()
                                else:
                                    is_valid_data = False
                                    error_message.append('Invalid Contact Person  data')
                                    error_data.append(contact_person_serializer.errors)
                            else:
                                is_valid_data = False
                                error_message.append('Invalid Contact Person Profile data')
                                error_data.append(contact_person_profile_serializer.errors)
                        else:
                            is_valid_data = False
                            error_message.append('Invalid Contact Person User data')
                            error_data.append(contact_person_user_serializer.errors)
                else:
                    is_valid_data = False
                    error_message.append('Invalid Supplier data')
                    error_data.append(supplier_serializer.errors)
            else:
                is_valid_data = False
                error_message.append('Invalid Profile data')
                error_data.append(profile_serializer.errors)
        else:
            is_valid_data = False
            error_message.append('Invalid User data')
            error_data.append(user_serializer.errors)
        if is_valid_data:
            return success_response(status=status.HTTP_201_CREATED, msg="Supplier is created",
                                    data=supplier_serializer.data)
        User.objects.filter(id__in=user_data).delete()
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg=', '.join(error_message), data=error_data)

    def supplier_data_validation(self, request):
        if 'supplier_name' in request.data and request.data.get('supplier_name') and Supplier.objects.filter(
                user__profile__name__iexact=self.request.data.get('supplier_name')).exists():
            return error_response(status=status.HTTP_409_CONFLICT, msg='Supplier with same name already exists',
                                  data={})
        if 'phone' in request.data and request.data.get('phone') and Supplier.objects.filter(
                user__profile__phone=self.request.data.get('phone')).exists():
            return error_response(status=status.HTTP_409_CONFLICT, msg='Phone number already exists', data={})
        if 'pan' in request.data and request.data.get('pan') and Supplier.objects.filter(
                pan__iexact=self.request.data.get('pan')).exists():
            return error_response(status=status.HTTP_409_CONFLICT, msg='PAN already exists', data={})
        if 'email' in request.data and request.data.get('email') and Supplier.objects.filter(
                user__profile__email=self.request.data.get('email')).exists():
            return error_response(status=status.HTTP_409_CONFLICT, msg='Email ID already exists', data={})
        if 'vehicle' in request.data and request.data.get('vehicle') and SupplierVehicle.objects.filter(
                vehicle__in=self.request.data.get('vehicle', []), ownership='O', active=True).exists():
            return error_response(status=status.HTTP_409_CONFLICT, msg='Vehicle number already exists', data={})
        return success_response(status=status.HTTP_200_OK, msg="Accepted", data={})

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        supplier = get_or_none(Supplier, id=pk)
        if not isinstance(supplier, Supplier):
            return Response({"error": "Supplier does not exist"}, status=status.HTTP_404_NOT_FOUND)
        supplier_serializer = SupplierSerializer(supplier, data=request.data)

        if supplier_serializer.is_valid():
            supplier_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Supplier Updated",
                "data": supplier_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Supplier not Updated",
            "data": supplier_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username

        supplier = get_or_none(Supplier, id=pk)
        if not isinstance(supplier, Supplier):
            return Response({"error": "Supplier does not exist"}, status=status.HTTP_404_NOT_FOUND)
        data = parse_supplier_update_data(request.data)
        profile_data = data.get('profile', {})
        if supplier.user and profile_data:
            profile = get_or_none(Profile, user=supplier.user)
            if isinstance(profile, Profile):
                profile_serializer = ProfileSerializer(instance=profile, data=profile_data, partial=True)
                if profile_serializer.is_valid():
                    profile_serializer.save()
                else:
                    return error_response(msg="Invalid Supplier data", data=profile_serializer.errors,
                                          status=status.HTTP_400_BAD_REQUEST)
        supplier_serializer = SupplierSerializer(
            instance=supplier,
            data=data.get('supplier', {}),
            partial=True
        )
        for vehicle in request.data.get('owned_trucks', []):
            if not SupplierVehicle.objects.filter(vehicle_id=vehicle).exists():
                supplier_vehicle_serializer = SupplierVehicleSerializer(
                    data={'supplier': pk, 'ownership': 'O', 'vehicle': vehicle, 'changed_by': request.user.username})
                if supplier_vehicle_serializer.is_valid():
                    supplier_vehicle_serializer.save()
                else:
                    return error_response(status=status.HTTP_400_BAD_REQUEST, data=supplier_vehicle_serializer.errors,
                                          msg='vehicle is associated with other owner')
        for row in data.get('contact_person', []):
            if not ContactPerson.objects.filter(user__profile__phone=row['phone']).exists():
                user_serializer = UserSerializer(data={
                    "username": generate_username(),
                    "password": 'Yt@U7866TR.12'
                })
                if user_serializer.is_valid():
                    user = user_serializer.save()
                    row['user'] = user.id
                    row['changed_by'] = request.user.username
                    profile_serializer = ProfileSerializer(data=row)
                    if profile_serializer.is_valid():
                        profile_serializer.save()
                    else:
                        return error_response(status=status.HTTP_400_BAD_REQUEST, data=profile_serializer.errors,
                                              msg="wrong profile data")
                    contact_person_data = {
                        'created_by': request.user.username,
                        'changed_by': request.user.username,
                        'supplier': pk,
                        'user': user.username
                    }
                    contact_person_serializer = ContactPersonSerializer(data=contact_person_data)
                    if contact_person_serializer.is_valid():
                        contact_person_serializer.save()
                    else:
                        return error_response(status=status.HTTP_400_BAD_REQUEST, data=contact_person_serializer.errors,
                                              msg="wrong contact person")
                else:
                    return error_response(status=status.HTTP_400_BAD_REQUEST, data=user_serializer.errors,
                                          msg="wrong user data")

        if supplier_serializer.is_valid():
            supplier_serializer.save()
            return success_response(status=status.HTTP_200_OK, data=supplier_serializer.data, msg="supplier updated")
        return error_response(data=supplier_serializer.errors, msg="invalid data", status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        supplier = get_or_none(Supplier, id=pk)

        if isinstance(supplier, Supplier):
            supplier_serializer = SupplierSerializer(supplier)
            return Response(supplier_serializer.data, status=status.HTTP_200_OK,
                            template_name='supplier/update/supplier.html')
        return Response({"error": "Supplier does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ContactPersonListView(generics.ListAPIView):
    queryset = ContactPerson.objects.order_by('-id').exclude(deleted=True)
    serializer_class = ContactPersonSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = ContactPersonFilter
    search_fields = (
        'id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Contact Person List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class ContactPersonViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        contact_person_serializer = ContactPersonSerializer(data=request.data)
        if contact_person_serializer.is_valid():
            contact_person_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Contact Person Created",
                "data": contact_person_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Contact Person not Created",
            "data": contact_person_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        contact_person = get_or_none(ContactPerson, id=pk)
        if not isinstance(contact_person, ContactPerson):
            return Response({"error": "Contact Person does not exist"}, status=status.HTTP_404_NOT_FOUND)
        contact_person_serializer = ContactPersonSerializer(contact_person, data=request.data)

        if contact_person_serializer.is_valid():
            contact_person_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Contact Person Updated",
                "data": contact_person_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Contact Person not Updated",
            "data": contact_person_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        contact_person = get_or_none(ContactPerson, id=pk)
        if not isinstance(contact_person, ContactPerson):
            return Response({"error": "Contact Person does not exist"}, status=status.HTTP_404_NOT_FOUND)
        contact_person_serializer = ContactPersonSerializer(
            instance=contact_person,
            data=request.data,
            partial=True
        )

        if contact_person_serializer.is_valid():
            contact_person_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Contact Person Updated",
                "data": contact_person_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Contact Person not Updated",
            "data": contact_person_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        contact_person = get_or_none(ContactPerson, id=pk)
        if isinstance(contact_person, ContactPerson):
            contact_person_serializer = ContactPersonSerializer(contact_person)
            return Response(contact_person_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Contact Person does not exist"}, status=status.HTTP_404_NOT_FOUND)


class SupplierDriverListView(generics.ListAPIView):
    queryset = Driver.objects.exclude(deleted=True).order_by('-id')
    serializer_class = DriverSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = DriverFilter
    search_fields = (
        'id', 'user__profile__name', 'driving_licence_number', 'user__profile__phone')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Supplier Driver List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)

    def get_queryset(self):
        APP_CATEGORY = self.request.META.get('HTTP_APP_CATEGORY')
        if APP_CATEGORY == 'fms':
            vehicles = SupplierVehicle.objects.filter(supplier__user=self.request.user).values_list(
                'vehicle_id', flat=True)
            drivers = DriverVehicle.objects.filter(vehicle_id__in=vehicles).distinct().values_list(
                'driver_id', flat=True)
            return Driver.objects.filter(id__in=drivers).exclude(deleted=True).order_by('-id')
        return Driver.objects.exclude(deleted=True).order_by('-id')


class SupplierDriverViewSet(viewsets.ViewSet):
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def list(self, request):
        pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        data = parse_driver_registration_data(request.data)
        user_data = data.get('user')
        user_serializer = UserSerializer(data=user_data)
        error_response_data = []
        error_message = []
        success_response_data = {}

        user_id = None
        if user_serializer.is_valid():
            user = user_serializer.save()
            user_id = user.id
            profile_data = data.get('profile')
            profile_data['user'] = user_id if isinstance(user, User) else None
            profile_serializer = ProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                error_message.append('Invalid Data')
                error_response_data.append(profile_serializer.errors)
            driver_data = data.get('driver')
            driver_data['user'] = user.username if isinstance(user, User) else None
            driver_serializer = DriverSerializer(data=driver_data)
            if driver_serializer.is_valid():
                driver = driver_serializer.save()
                for driver_phone in data.get('driver_phone'):
                    driver_phone_data = driver_phone
                    driver_phone_data['driver'] = driver.id
                    driver_phone_serializer = DriverPhoneSerializer(data=driver_phone_data)
                    if driver_phone_serializer.is_valid():
                        driver_phone_serializer.save()
                    else:
                        error_message.append('Invalid Phone Number')
                        error_response_data.append(driver_phone_serializer.errors)
                success_response_data = driver_serializer.data
            else:
                error_message.append('Invalid Driver Data')
                error_response_data.append(driver_serializer.errors)
        else:
            error_message.append('Invalid Driver User Data')
            error_response_data.append(user_serializer.errors)
        if error_response_data:
            if user_id:
                User.objects.filter(id=user_id).delete()
            return error_response(status=status.HTTP_400_BAD_REQUEST, data=error_response_data,
                                  msg='\n'.join(error_message))
        else:
            return success_response(status=status.HTTP_201_CREATED, data=success_response_data, msg='Driver Created')

    def driver_data_validation(self, request):
        if 'phone' in request.data and request.data.get('phone') and (DriverPhone.objects.filter(
                phone=self.request.data.get('phone')).exists()) or (Driver.objects.filter(user__profile__phone=self.request.data.get('phone')).exists()):
            return error_response(status=status.HTTP_409_CONFLICT, msg='Phone number already exists', data={})
        return success_response(status=status.HTTP_200_OK, msg="Accepted", data={})

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        driver = get_or_none(Driver, id=pk)
        if not isinstance(driver, Driver):
            return Response({"error": "Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)
        driver_serializer = DriverSerializer(driver, data=request.data)

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
        parsed_driver_docs = parse_supplier_driver_docs(data=request.data)
        driver = get_or_none(Driver, id=pk)
        if driver.user and Profile.objects.filter(user=driver.user).exists():
            profile_data = parsed_driver_docs.pop('user_data')
            profile_instance = Profile.objects.get(user=driver.user)
            profile_serializer = ProfileSerializer(instance=profile_instance, data=profile_data, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
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
                    supplier_driver=driver,
                    document_category='PAN',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(DriverFile, supplier_driver=driver),
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
                    supplier_driver=driver,
                    document_category='DL',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(DriverFile, supplier_driver=driver),
                    s3_upload=s3_upload,
                )
        driver = get_or_none(Driver, id=pk)
        driver_serializer = DriverSerializer(driver)
        return success_response(msg='driver details %s' % ('edited' if pk else 'saved'),
                                data=driver_serializer.data, status=status.HTTP_202_ACCEPTED)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        driver = get_or_none(Driver, id=pk)
        if not isinstance(driver, Driver):
            return Response({"error": "Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)
        data = parse_driver_update_form(data=request.data)
        profile = get_or_none(Profile, user=driver.user)
        if isinstance(profile, Profile) and data.get('profile', None):
            profile_serializer = ProfileSerializer(instance=profile,
                                                   data=data.get('profile', None), partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
        driver_serializer = DriverSerializer(
            instance=driver,
            data=data.get('driver_data'),
            partial=True
        )

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

    def retrieve(self, request, pk=None):
        driver = get_or_none(Driver, id=pk)
        if isinstance(driver, Driver):
            driver_serializer = DriverSerializer(driver)
            return Response(driver_serializer.data, template_name='supplier/update/driver.html',
                            status=status.HTTP_200_OK)
        return Response({"error": "Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)


class SupplierDriverPhoneListView(generics.ListAPIView):
    queryset = DriverPhone.objects.order_by('-id').exclude(deleted=True)
    serializer_class = DriverPhoneSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = DriverPhoneFilter
    search_fields = ('id',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Supplier Driver Phone List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class SupplierDriverPhoneViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        driver_phone_serializer = DriverPhoneSerializer(data=request.data)
        if driver_phone_serializer.is_valid():
            driver_phone_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Driver Phone Created",
                "data": driver_phone_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Driver Phone not Created",
            "data": driver_phone_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        driver_phone = get_or_none(DriverPhone, id=pk)
        if not isinstance(driver_phone, DriverPhone):
            return Response({"error": "Driver Phone does not exist"}, status=status.HTTP_404_NOT_FOUND)
        driver_phone_serializer = DriverPhoneSerializer(driver_phone, data=request.data)

        if driver_phone_serializer.is_valid():
            driver_phone_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Driver Phone Updated",
                "data": driver_phone_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Driver Phone not Updated",
            "data": driver_phone_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        driver_phone = get_or_none(DriverPhone, id=pk)
        if not isinstance(driver_phone, DriverPhone):
            return Response({"error": "Driver Phone does not exist"}, status=status.HTTP_404_NOT_FOUND)
        driver_phone_serializer = DriverPhoneSerializer(
            instance=driver_phone,
            data=request.data,
            partial=True
        )

        if driver_phone_serializer.is_valid():
            driver_phone_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Driver Phone Updated",
                "data": driver_phone_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Driver Phone not Updated",
            "data": driver_phone_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        driver_phone = get_or_none(DriverPhone, id=pk)
        if isinstance(driver_phone, DriverPhone):
            driver_phone_serializer = DriverPhoneSerializer(driver_phone)
            return Response(driver_phone_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Driver Phone does not exist"}, status=status.HTTP_404_NOT_FOUND)


class VehicleBodyCategoryListView(generics.ListAPIView):
    queryset = VehicleBodyCategory.objects.order_by('-id').exclude(deleted=True)
    serializer_class = VehicleBodyCategorySerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = VehicleBodyCategoryFilter
    search_fields = (
        'id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Vehicle Body Category List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class VehicleBodyCategoryViewSet(viewsets.ViewSet):
    """
        API for creation, updation and retrieval of Vehicle Body Category
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        vehicle_body_category_serializer = VehicleBodyCategorySerializer(data=request.data)
        if vehicle_body_category_serializer.is_valid():
            vehicle_body_category_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Vehicle Body Category Created",
                "data": vehicle_body_category_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Body Category not Created",
            "data": vehicle_body_category_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_body_category = get_or_none(VehicleBodyCategory, id=pk)
        if not isinstance(vehicle_body_category, VehicleBodyCategory):
            return Response({"error": "Vehicle Body Category does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_body_category_serializer = VehicleBodyCategorySerializer(vehicle_body_category, data=request.data)

        if vehicle_body_category_serializer.is_valid():
            vehicle_body_category_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Body Category Updated",
                "data": vehicle_body_category_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Body Category not Updated",
            "data": vehicle_body_category_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_body_category = get_or_none(VehicleBodyCategory, id=pk)
        if not isinstance(vehicle_body_category, VehicleBodyCategory):
            return Response({"error": "Vehicle Body Category does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_body_category_serializer = VehicleBodyCategorySerializer(
            instance=vehicle_body_category,
            data=request.data,
            partial=True
        )

        if vehicle_body_category_serializer.is_valid():
            vehicle_body_category_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Body Category Updated",
                "data": vehicle_body_category_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Body Category not Updated",
            "data": vehicle_body_category_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        vehicle_body_category = get_or_none(VehicleBodyCategory, id=pk)
        if isinstance(vehicle_body_category, VehicleBodyCategory):
            return Response(VehicleBodyCategorySerializer(vehicle_body_category).data, status=status.HTTP_200_OK)
        return Response({"error": "Vehicle body category does not exist"}, status=status.HTTP_404_NOT_FOUND)


class VehicleCategoryListView(generics.ListAPIView):
    serializer_class = VehicleCategorySerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    queryset = VehicleCategory.objects.exclude(deleted=True).order_by("-id")
    filter_class = VehicleCategoryFilter
    ordering_fields = ('id',)
    search_fields = (
        'id', 'vehicle_type', 'capacity', 'truck_body_type', 'truck_body__name', 'description')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Vehicle Category List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class VehicleCategoryViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Vehicle Category
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        vehicle_category_serializer = VehicleCategorySerializer(data=request.data)
        if vehicle_category_serializer.is_valid():
            vehicle_category_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Vehicle Category Created",
                "data": vehicle_category_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Category not Created",
            "data": vehicle_category_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_category = get_or_none(VehicleCategory, id=pk)
        if not isinstance(vehicle_category, VehicleCategory):
            return Response({"error": "Vehicle Category does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_category_serializer = VehicleCategorySerializer(instance=vehicle_category,
                                                                data=request.data)
        if vehicle_category_serializer.is_valid():
            vehicle_category_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Category Updated",
                "data": vehicle_category_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Category not Updated",
            "data": vehicle_category_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_category = get_or_none(VehicleCategory, id=pk)
        if not isinstance(vehicle_category, VehicleCategory):
            return Response({"error": "Vehicle Category does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_category_serializer = VehicleCategorySerializer(
            instance=vehicle_category,
            data=request.data,
            partial=True
        )
        if vehicle_category_serializer.is_valid():
            vehicle_category_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Category Updated",
                "data": vehicle_category_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Category not Updated",
            "data": vehicle_category_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        vehicle_category = get_or_none(VehicleCategory, id=pk)
        if not isinstance(vehicle_category, VehicleCategory):
            return Response({"error": "Vehicle body category does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_category_serializer = VehicleCategorySerializer(vehicle_category)
        return Response(vehicle_category_serializer.data, status=status.HTTP_200_OK)


class VehicleListView(generics.ListAPIView):
    queryset = Vehicle.objects.exclude(deleted=True).order_by('-id')
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = VehicleFilter
    search_fields = (
        'id', 'vehicle_number', 'vehicle_type__vehicle_type', 'vehicle_capacity',
        'chassis_number', 'engine_number', 'registration_year',
        'registration_validity', 'gps_enabled', 'created_by__username')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Vehicle List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)

    def get_queryset(self):
        APP_CATEGORY = self.request.META.get('HTTP_APP_CATEGORY')
        if APP_CATEGORY == 'fms':
            supplier_vehicles = SupplierVehicle.objects.filter(supplier__user=self.request.user).exclude(
                Q(deleted=True) | Q(active=False)).values_list('vehicle_id', flat=True)
            return Vehicle.objects.filter(id__in=supplier_vehicles).exclude(deleted=True).order_by('-id')
        return Vehicle.objects.exclude(deleted=True).order_by('-id')

    def get_serializer_class(self):
        APP_CATEGORY = self.request.META.get('HTTP_APP_CATEGORY')
        if APP_CATEGORY == 'fms':
            return FMSVehicleSerializer
        return VehicleSerializer


class VehicleAccountingSummaryListView(generics.ListAPIView):
    serializer_class = VehicleAccountingSummarySerializer
    pagination_class = CustomeDatatablesPaginator
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    # filter_class = OwnerVehicleFilter
    search_fields = ('id', 'vehicle__vehicle_number')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Success", "status_code": status.HTTP_200_OK, "msg": "Vehicles List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)

    def get_queryset(self):
        queryset = VehicleAccountingSummary.objects.exclude(deleted=True).annotate(
            completed_pod_balance_amount=RawSQL(
                "(accounting_summary->>%s)::numeric", ("completed_pod_balance_amount",))
        ).order_by('-completed_pod_balance_amount')
        return queryset


class VehicleViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Vehicle
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        vehicle_number = compare_format(request.data.get('vehicle_number', None))
        if Vehicle.objects.filter(vehicle_number=vehicle_number).exists():
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg='{} already exists'.format(vehicle_number),
                                  data={})
        data = parse_vehicle_registration_data(data=request.data)
        vehicle_data = data.pop('vehicle')
        vehicle_serializer = VehicleSerializer(data=vehicle_data)
        error_response_data = []
        error_message = []
        success_response_data = {}

        if vehicle_serializer.is_valid():
            vehicle = vehicle_serializer.save()
            success_response_data = vehicle_serializer.data
            insurance_data = data.pop('insurance')
            insurance_data['vehicle'] = vehicle.id
            insurance_serializer = VehicleInsuranceSerializer(data=insurance_data)
            if insurance_serializer.is_valid():
                insurance_serializer.save()
            else:
                error_message.append('Invalid insurance data')
                error_response_data.append(insurance_serializer.errors)

            puc_data = data.pop('puc')
            puc_data['vehicle'] = vehicle.id
            puc_serializer = VehiclePUCSerializer(data=puc_data)
            if puc_serializer.is_valid():
                puc_serializer.save()
            else:
                error_message.append('Invalid PUC data')
                error_response_data.append(puc_serializer.errors)

            permit_data = data.pop('permit')
            permit_data['vehicle'] = vehicle.id
            permit_serializer = VehiclePermitSerializer(data=permit_data)
            if permit_serializer.is_valid():
                permit_serializer.save()
            else:
                error_message.append('Invalid permit data')
                error_response_data.append(permit_serializer.errors)
            fitness_data = data.pop('fitness')
            fitness_data['vehicle'] = vehicle.id
            fitness_serializer = VehicleFitnessSerializer(data=fitness_data)
            if fitness_serializer.is_valid():
                fitness_serializer.save()
            else:
                error_message.append('Invalid fitness data')
                error_response_data.append(fitness_serializer.errors)
            supplier_vehicle_data = data.pop('vehicle_supplier')
            supplier_vehicle_data['vehicle'] = vehicle.id
            supplier_vehicle_serializer = SupplierVehicleSerializer(data=supplier_vehicle_data)
            if supplier_vehicle_serializer.is_valid():
                supplier_vehicle_serializer.save()
            else:
                error_message.append('Invalid supplier_vehicle data')
                error_response_data.append(supplier_vehicle_serializer.errors)
        else:
            error_response_data.append(vehicle_serializer.errors)
            error_message.append('invalid vehicle data')
        if success_response_data:
            return success_response(status=status.HTTP_201_CREATED, msg="vehicle created", data=success_response_data)
        else:
            return error_response(status=status.HTTP_400_BAD_REQUEST, data=error_response_data,
                                  msg='\n'.join(error_message))

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle = get_or_none(Vehicle, id=pk)
        if not isinstance(vehicle, Vehicle):
            return Response({"error": "Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_serializers = VehicleSerializer(instance=vehicle, data=request.data)
        if vehicle_serializers.is_valid():
            vehicle_serializers.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Updated",
                "data": vehicle_serializers.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle not Updated",
            "data": vehicle_serializers.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def fms_update(self, request, pk):
        vehicle_id = pk

        if vehicle_id and vehicle_id.isnumeric():
            vehicle = get_or_none(Vehicle, id=int_or_none(vehicle_id))
            if not isinstance(vehicle, Vehicle):
                return error_response(msg='Vehicle with id={} does not exist'.format(vehicle_id),
                                      status=status.HTTP_404_NOT_FOUND, data=None)
        if request.data.get('gps_enabled', None) == 'yes':
            request.data['gps_enabled'] = True
        else:
            request.data['gps_enabled'] = False
        data = request.data
        data['vehicle_id'] = pk
        parsed_data = parse_vehicle_docs(data)

        request.data["changed_by"] = self.request.user.username
        vehicle = get_or_none(Vehicle, id=pk)

        vehicle_serializers = VehicleSerializer(
            instance=vehicle,
            data=parsed_data,
            partial=True
        )
        if vehicle_serializers.is_valid():
            vehicle_serializers.save()

        supplier = get_or_none(Supplier, user=request.user)
        supplier_driver = vehicle.driver

        doc_key = 'rc_doc'
        if doc_key in data and data[doc_key].get('url'):

            if not VehicleFile.objects.filter(
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
                VehicleFile.objects.create(
                    uploaded_by=request.user,
                    vehicle=vehicle,
                    document_category='REG',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(VehicleFile, vehicle=vehicle),
                    s3_upload=s3_upload
                )

        doc_key = 'permit_doc'
        if doc_key in data and data[doc_key].get('url'):

            if not VehicleFile.objects.filter(
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
                VehicleFile.objects.create(
                    uploaded_by=request.user,
                    vehicle=vehicle,
                    document_category='PERM',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(VehicleFile, vehicle=vehicle),
                    s3_upload=s3_upload
                )

        doc_key = 'insurance_doc'
        if doc_key in data and data[doc_key].get('url'):

            if not VehicleFile.objects.filter(
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
                VehicleFile.objects.create(
                    uploaded_by=request.user,
                    vehicle=vehicle,
                    document_category='INS',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(VehicleFile, vehicle=vehicle),
                    s3_upload=s3_upload
                )

        doc_key = 'fitness_doc'
        if doc_key in data and data[doc_key].get('url'):

            if not VehicleFile.objects.filter(
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
                VehicleFile.objects.create(
                    uploaded_by=request.user,
                    vehicle=vehicle,
                    document_category='FIT',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(VehicleFile, vehicle=vehicle),
                    s3_upload=s3_upload
                )

        doc_key = 'puc_doc'
        if doc_key in data and data[doc_key].get('url'):

            if not VehicleFile.objects.filter(
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
                VehicleFile.objects.create(
                    uploaded_by=request.user,
                    vehicle=vehicle,
                    document_category='PUC',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(VehicleFile, vehicle=vehicle),
                    s3_upload=s3_upload,
                )

        doc_key = 'owner_pan_doc'
        if doc_key in data and vehicle.owner and data[doc_key].get('url'):
            if not OwnerFile.objects.filter(
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
                OwnerFile.objects.create(
                    uploaded_by=request.user,
                    supplier=supplier,
                    document_category='PAN',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(OwnerFile, supplier=supplier),
                    s3_upload=s3_upload
                )

        doc_key = 'owner_dec_doc'
        if doc_key in data and vehicle.owner and data[doc_key].get('url'):

            if not OwnerFile.objects.filter(
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
                OwnerFile.objects.create(
                    uploaded_by=request.user,
                    supplier=supplier,
                    document_category='DEC',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(OwnerFile, supplier=supplier),
                    s3_upload=s3_upload,
                )

        doc_key = 'driver_dl_doc'
        if doc_key in data and vehicle.driver and data[doc_key].get('url'):
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
                    supplier_driver=supplier_driver,
                    document_category='DL',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(DriverFile, supplier_driver=supplier_driver),
                    s3_upload=s3_upload,
                )
        vehicle = get_or_none(Vehicle, id=pk)
        vehicle_serializer = FMSVehicleSerializer(instance=vehicle)
        return success_response(
            msg='vehicle details %s' % ('edited' if vehicle_id else 'saved'),
            data=vehicle_serializer.data, status=status.HTTP_202_ACCEPTED
        )

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle = get_or_none(Vehicle, id=pk)
        if not isinstance(vehicle, Vehicle):
            return Response({"error": "Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        data = parse_vehicle_update_data(request.data)
        vehicle_serializers = VehicleSerializer(
            instance=vehicle,
            data=data.get('vehicle', {}),
            partial=True
        )
        if vehicle_serializers.is_valid():
            vehicle_serializers.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Updated",
                "data": vehicle_serializers.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle not Updated",
            "data": vehicle_serializers.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        vehicle = get_or_none(Vehicle, id=pk)
        if not isinstance(vehicle, Vehicle):
            return Response({"error": "Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_serializers = FMSVehicleSerializer(vehicle)
        data = vehicle_serializers.data
        APP_CATEGORY = self.request.META.get('HTTP_APP_CATEGORY')
        if APP_CATEGORY == 'fms':
            vehicle_serializers = FMSVehicleSerializer(vehicle)
            data = vehicle_serializers.data
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=data, status=status.HTTP_200_OK, template_name='supplier/update/vehicle.html')


class DriverVehicleListView(generics.ListAPIView):
    queryset = DriverVehicle.objects.order_by('-id').exclude(deleted=True)
    serializer_class = DriverVehicleSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = DriverVehicleFilter
    search_fields = (
        'id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Driver Vehicle List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)
        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class DriverVehicleViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        driver_vehicle_serializer = DriverVehicleSerializer(data=request.data)
        if driver_vehicle_serializer.is_valid():
            driver_vehicle_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Driver Vehicle Created",
                "data": driver_vehicle_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Driver Vehicle not Created",
            "data": driver_vehicle_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        driver_vehicle = get_or_none(DriverVehicle, id=pk)
        if not isinstance(driver_vehicle, DriverVehicle):
            return Response({"error": "Driver Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        driver_vehicle_serializer = DriverVehicleSerializer(driver_vehicle, data=request.data)

        if driver_vehicle_serializer.is_valid():
            driver_vehicle_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Driver Vehicle Updated",
                "data": driver_vehicle_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Driver Vehicle not Updated",
            "data": driver_vehicle_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        driver_vehicle = get_or_none(DriverVehicle, id=pk)
        if not isinstance(driver_vehicle, DriverVehicle):
            return Response({"error": "Driver Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        driver_vehicle_serializer = DriverVehicleSerializer(
            instance=driver_vehicle,
            data=request.data,
            partial=True
        )

        if driver_vehicle_serializer.is_valid():
            driver_vehicle_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Driver Vehicle Updated",
                "data": driver_vehicle_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Driver Vehicle not Updated",
            "data": driver_vehicle_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        driver_vehicle = get_or_none(DriverVehicle, id=pk)
        if isinstance(driver_vehicle, DriverVehicle):
            driver_vehicle_serializer = DriverVehicleSerializer(driver_vehicle)
            return Response(driver_vehicle_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Driver Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)


class VehicleStatusListView(generics.ListAPIView):
    queryset = VehicleStatus.objects.order_by('-id').exclude(deleted=True)
    serializer_class = VehicleStatusSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = VehicleStatusFilter
    search_fields = (
        'id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Vehicle Status List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class VehicleStatusViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        vehicle_status_serializer = VehicleStatusSerializer(data=request.data)
        if vehicle_status_serializer.is_valid():
            vehicle_status_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Vehicle Status Created",
                "data": vehicle_status_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Status not Created",
            "data": vehicle_status_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_status = get_or_none(VehicleStatus, id=pk)
        if not isinstance(vehicle_status, VehicleStatus):
            return Response({"error": "Vehicle Status does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_status_serializer = VehicleStatusSerializer(instance=vehicle_status, data=request.data)
        if vehicle_status_serializer.is_valid():
            vehicle_status_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Status Updated",
                "data": vehicle_status_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Status not Updated",
            "data": vehicle_status_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_status = get_or_none(VehicleStatus, id=pk)
        if not isinstance(vehicle_status, VehicleStatus):
            return Response({"error": "Vehicle Status does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_status_serializer = VehicleStatusSerializer(
            instance=vehicle_status,
            data=request.data,
            partial=True
        )
        if vehicle_status_serializer.is_valid():
            vehicle_status_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Status Updated",
                "data": vehicle_status_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Status not Updated",
            "data": vehicle_status_serializer
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        vehicle_status = get_or_none(VehicleStatus, id=pk)
        if not isinstance(vehicle_status, VehicleStatus):
            return Response({"error": "Vehicle Status does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_status_serializer = VehicleStatusSerializer(vehicle_status)
        return Response(vehicle_status_serializer.data, status=status.HTTP_200_OK)


class VehicleInsurerListView(generics.ListAPIView):
    queryset = VehicleInsurer.objects.order_by('-id').exclude(deleted=True)
    serializer_class = VehicleInsurerSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = VehicleInsurerFilter
    search_fields = (
        'id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Vehicle Insurer List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class VehicleInsurerViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        vehicle_inusrer_serializer = VehicleInsurerSerializer(data=request.data)
        if vehicle_inusrer_serializer.is_valid():
            vehicle_inusrer_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Vehicle Insurer Created",
                "data": vehicle_inusrer_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Insurer not Created",
            "data": vehicle_inusrer_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_inusrer = get_or_none(VehicleInsurer, id=pk)

        if not isinstance(vehicle_inusrer, VehicleInsurer):
            return Response({"error": "Vehicle Insurer does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_inusrer_serializer = VehicleInsurerSerializer(instance=vehicle_inusrer, data=request.data)
        if vehicle_inusrer_serializer.is_valid():
            vehicle_inusrer_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Insurer Updated",
                "data": vehicle_inusrer_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Insurer not Updated",
            "data": vehicle_inusrer_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_inusrer = get_or_none(VehicleInsurer, id=pk)
        if not isinstance(vehicle_inusrer, VehicleInsurer):
            return Response({"error": "Vehicle Insurer does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_inusrer_serializer = VehicleInsurerSerializer(
            instance=vehicle_inusrer,
            data=request.data,
            partial=True
        )
        if vehicle_inusrer_serializer.is_valid():
            vehicle_inusrer_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Insurer Updated",
                "data": vehicle_inusrer_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Insurer not Updated",
            "data": vehicle_inusrer_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        vehicle_inusrer = get_or_none(VehicleInsurer, id=pk)
        if not isinstance(vehicle_inusrer, VehicleInsurer):
            return Response({"error": "Vehicle Insurer does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_inusrer_serializer = VehicleInsurerSerializer(vehicle_inusrer)
        return Response(vehicle_inusrer_serializer.data, status=status.HTTP_200_OK)


class VehicleInsuranceListView(generics.ListAPIView):
    queryset = VehicleInsurance.objects.order_by('-id').exclude(deleted=True)
    serializer_class = VehicleInsuranceSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = VehicleInsuranceFilter
    search_fields = (
        'id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Vehicle Insurance List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class VehicleInsuranceViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        vehicle_inusrance_serializer = VehicleInsuranceSerializer(data=request.data)
        if vehicle_inusrance_serializer.is_valid():
            vehicle_inusrance_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Vehicle Insurance Created",
                "data": vehicle_inusrance_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Insurance not Created",
            "data": vehicle_inusrance_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_inusrance = get_or_none(VehicleInsurance, id=pk)

        if not isinstance(vehicle_inusrance, VehicleInsurance):
            return Response({"error": "Vehicle Insurance does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_inusrance_serializer = VehicleInsuranceSerializer(instance=vehicle_inusrance, data=request.data)
        if vehicle_inusrance_serializer.is_valid():
            vehicle_inusrance_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Insurance Updated",
                "data": vehicle_inusrance_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Insurance not Updated",
            "data": vehicle_inusrance_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_inusrance = get_or_none(VehicleInsurance, id=pk)
        if not isinstance(vehicle_inusrance, VehicleInsurance):
            return Response({"error": "Vehicle Insurance does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_inusrance_serializer = VehicleInsuranceSerializer(
            instance=vehicle_inusrance,
            data=request.data,
            partial=True
        )
        if vehicle_inusrance_serializer.is_valid():
            vehicle_inusrance_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Insurance Updated",
                "data": vehicle_inusrance_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Insurance not Updated",
            "data": vehicle_inusrance_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        vehicle_inusrance = get_or_none(VehicleInsurance, id=pk)
        if not isinstance(vehicle_inusrance, VehicleInsurance):
            return Response({"error": "Vehicle Insurance does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_inusrance_serializer = VehicleInsuranceSerializer(vehicle_inusrance)
        return Response(vehicle_inusrance_serializer.data, status=status.HTTP_200_OK)


class VehiclePUCListView(generics.ListAPIView):
    queryset = VehiclePUC.objects.order_by('-id').exclude(deleted=True)
    serializer_class = VehiclePUCSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = VehiclePUCFilter
    search_fields = (
        'id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Vehicle PUC List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class VehiclePUCViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        vehicle_puc_serializer = VehiclePUCSerializer(data=request.data)
        if vehicle_puc_serializer.is_valid():
            vehicle_puc_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Vehicle PUC Created",
                "data": vehicle_puc_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle PUC not Created",
            "data": vehicle_puc_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_puc = get_or_none(VehiclePUC, id=pk)

        if not isinstance(vehicle_puc, VehiclePUC):
            return Response({"error": "Vehicle PUC does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_puc_serializer = VehiclePUCSerializer(instance=vehicle_puc, data=request.data)
        if vehicle_puc_serializer.is_valid():
            vehicle_puc_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle PUC Updated",
                "data": vehicle_puc_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle PUC not Updated",
            "data": vehicle_puc_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_puc = get_or_none(VehiclePUC, id=pk)
        if not isinstance(vehicle_puc, VehiclePUC):
            return Response({"error": "Vehicle PUC does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_puc_serializer = VehiclePUCSerializer(
            instance=vehicle_puc,
            data=request.data,
            partial=True
        )
        if vehicle_puc_serializer.is_valid():
            vehicle_puc_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle PUC Updated",
                "data": vehicle_puc_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle PUC not Updated",
            "data": vehicle_puc_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        vehicle_puc = get_or_none(VehiclePUC, id=pk)
        if not isinstance(vehicle_puc, VehiclePUC):
            return Response({"error": "Vehicle PUC does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_puc_serializer = VehiclePUCSerializer(vehicle_puc)
        return Response(vehicle_puc_serializer.data, status=status.HTTP_200_OK)


class VehicleFitnessListView(generics.ListAPIView):
    queryset = VehicleFitness.objects.order_by('-id').exclude(deleted=True)
    serializer_class = VehicleFitnessSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = VehicleFitnessFilter
    search_fields = (
        'id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Vehicle Fitness List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class VehicleFitnessViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        vehicle_fitness_serializer = VehicleFitnessSerializer(data=request.data)
        if vehicle_fitness_serializer.is_valid():
            vehicle_fitness_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Vehicle Fitness Created",
                "data": vehicle_fitness_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Fitness not Created",
            "data": vehicle_fitness_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_fitness = get_or_none(VehicleFitness, id=pk)

        if not isinstance(vehicle_fitness, VehicleFitness):
            return Response({"error": "Vehicle Fitness does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_fitness_serializer = VehicleFitnessSerializer(instance=vehicle_fitness, data=request.data)
        if vehicle_fitness_serializer.is_valid():
            vehicle_fitness_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Fitness Updated",
                "data": vehicle_fitness_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Fitness not Updated",
            "data": vehicle_fitness_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_fitness = get_or_none(VehicleFitness, id=pk)
        if not isinstance(vehicle_fitness, VehicleFitness):
            return Response({"error": "Vehicle Fitness does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_fitness_serializer = VehicleFitnessSerializer(
            instance=vehicle_fitness,
            data=request.data,
            partial=True
        )
        if vehicle_fitness_serializer.is_valid():
            vehicle_fitness_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Fitness Updated",
                "data": vehicle_fitness_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Fitness not Updated",
            "data": vehicle_fitness_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        vehicle_fitness = get_or_none(VehicleFitness, id=pk)
        if not isinstance(vehicle_fitness, VehicleFitness):
            return Response({"error": "Vehicle Fitness does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_fitness_serializer = VehicleFitnessSerializer(vehicle_fitness)
        return Response(vehicle_fitness_serializer.data, status=status.HTTP_200_OK)


class VehiclePermitListView(generics.ListAPIView):
    queryset = VehiclePermit.objects.order_by('-id').exclude(deleted=True)
    serializer_class = VehiclePermitSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = VehiclePermitFilter
    search_fields = (
        'id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Vehicle Permit List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class VehiclePermitViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        vehicle_permit_serializer = VehiclePermitSerializer(data=request.data)
        if vehicle_permit_serializer.is_valid():
            vehicle_permit_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Vehicle Permit Created",
                "data": vehicle_permit_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Permit not Created",
            "data": vehicle_permit_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_permit = get_or_none(VehiclePermit, id=pk)

        if not isinstance(vehicle_permit, VehiclePermit):
            return Response({"error": "Vehicle Permit does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_permit_serializer = VehiclePermitSerializer(instance=vehicle_permit, data=request.data)
        if vehicle_permit_serializer.is_valid():
            vehicle_permit_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Permit Updated",
                "data": vehicle_permit_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Permit not Updated",
            "data": vehicle_permit_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        vehicle_permit = get_or_none(VehiclePermit, id=pk)
        if not isinstance(vehicle_permit, VehiclePermit):
            return Response({"error": "Vehicle Permit does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_permit_serializer = VehiclePermitSerializer(
            instance=vehicle_permit,
            data=request.data,
            partial=True
        )
        if vehicle_permit_serializer.is_valid():
            vehicle_permit_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Vehicle Permit Updated",
                "data": vehicle_permit_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Vehicle Permit not Updated",
            "data": vehicle_permit_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        vehicle_permit = get_or_none(VehiclePermit, id=pk)
        if not isinstance(vehicle_permit, VehiclePermit):
            return Response({"error": "Vehicle Permit does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vehicle_permit_serializer = VehiclePermitSerializer(vehicle_permit)
        return Response(vehicle_permit_serializer.data, status=status.HTTP_200_OK)


class SupplierVehicleListView(generics.ListAPIView):
    queryset = SupplierVehicle.objects.order_by('-id').exclude(deleted=True)
    serializer_class = SupplierVehicleSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = SupplierVehicleFilter
    search_fields = (
        'id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Supplier Vehicle List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class SupplierVehicleViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = request.user.username
        supplier_vehicle_serializer = SupplierVehicleSerializer(data=request.data)
        if supplier_vehicle_serializer.is_valid():
            supplier_vehicle_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Supplier Vehicle Created",
                "data": supplier_vehicle_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Supplier Vehicle not Created",
            "data": supplier_vehicle_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        supplier_vehicle = get_or_none(SupplierVehicle, id=pk)

        if not isinstance(supplier_vehicle, SupplierVehicle):
            return Response({"error": "Supplier Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        supplier_vehicle_serializer = SupplierVehicleSerializer(instance=supplier_vehicle, data=request.data)
        if supplier_vehicle_serializer.is_valid():
            supplier_vehicle_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Supplier Vehicle Updated",
                "data": supplier_vehicle_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Supplier Vehicle not Updated",
            "data": supplier_vehicle_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = request.user.username
        supplier_vehicle = get_or_none(SupplierVehicle, id=pk)
        if not isinstance(supplier_vehicle, SupplierVehicle):
            return Response({"error": "Suplier Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        supplier_vehicle_serializer = SupplierVehicleSerializer(
            instance=supplier_vehicle,
            data=request.data,
            partial=True
        )
        if supplier_vehicle_serializer.is_valid():
            supplier_vehicle_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Supplier Vehicle Updated",
                "data": supplier_vehicle_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Supplier Vehicle not Updated",
            "data": supplier_vehicle_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        supplier_vehicle = get_or_none(SupplierVehicle, id=pk)
        if not isinstance(supplier_vehicle, SupplierVehicle):
            return Response({"error": "Supplier Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        supplier_vehicle_serializer = SupplierVehicleSerializer(supplier_vehicle)
        return Response(supplier_vehicle_serializer.data, status=status.HTTP_200_OK)
