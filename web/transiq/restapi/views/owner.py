from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api import s3util
from api.models import S3Upload
from api.utils import int_or_none
from authentication.models import Profile
from broker.models import Broker
from driver.models import Driver
from fileupload.models import VehicleFile, OwnerFile, DriverFile
from fileupload.views import get_new_serial
from fms.views import validate_url
from owner.models import Vehicle, Owner, Route, FuelCard, FuelCardTransaction, VehicleSummary
from owner.vehicle_util import compare_format
from restapi.filter.owner import OwnerFilter, OwnerVehicleFilter, FuelCardFilter
from restapi.helper_api import generate_username, error_response, success_response, is_fms_user, is_sme_user
from restapi.pagination import CustomeDatatablesPaginator
from restapi.parser.updatawebdata import parse_update_owner_data
from restapi.search import CustomSearch
from restapi.serializers.authentication import UserSerializer, ProfileSerializer
from restapi.serializers.driver import DriverSerializer
from restapi.serializers.owner import VehicleSerializer, OwnerSerializer, RouteSerializer, FuelCardSerializer, \
    FuelCardTransactionSerializer, Select2FuelCardSerializer, FMSVehicleSerializer, VehicleSummarySerializer
from restapi.service.fms import parse_vehicle_docs
from restapi.utils import get_or_none
from sme.models import Sme


class RouteViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Route
    """

    def create(self, request, pk=None):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        route_serializer = RouteSerializer(data=request.data)
        if route_serializer.is_valid():
            route_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Route Created",
                "data": route_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Route not Created",
            "data": route_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        route = get_or_none(Route, id=pk)
        if not isinstance(route, Route):
            return Response({"error": "Route does not exist"}, status=status.HTTP_404_NOT_FOUND)
        route_serializer = RouteSerializer(instance=route, data=request.data)
        if route_serializer.is_valid():
            route_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Route Updated",
                "data": route_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Route not Updated",
            "data": route_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        route = get_or_none(Route, id=pk)
        if not isinstance(route, Route):
            return Response({"error": "Route does not exist"}, status=status.HTTP_404_NOT_FOUND)
        route_serializer = RouteSerializer(
            instance=route,
            data=request.data,
            partial=True
        )
        if route_serializer.is_valid():
            route_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Route Updated",
                "data": route_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Route not Updated",
            "data": route_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        route = get_or_none(Route, id=pk)
        if not isinstance(route, Route):
            return Response({"error": "Route does not exist"}, status=status.HTTP_404_NOT_FOUND)
        route_serializer = RouteSerializer(route)
        return Response(route_serializer.data, status=status.HTTP_200_OK)


class OwnerListView(generics.ListAPIView):
    queryset = Owner.objects.exclude(name__profile=None).exclude(deleted=True).order_by('-id')
    serializer_class = OwnerSerializer
    pagination_class = CustomeDatatablesPaginator
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = OwnerFilter
    search_fields = (
        'id', 'name__username', 'name__profile__phone', 'name__profile__name', 'owner_address', 'city__name',
        'vehicle_owner__vehicle_number', 'route__destination__name', 'pan', 'created_by__username', 'created_on',
        'owner_files__serial', 'owner_files__verified'
    )

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


class OwnerCreatePageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/register_owner.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class OwnerViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Owner Vehicle
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def create(self, request):
        if "created_by" not in request.data:
            request.data["created_by"] = self.request.user.username
        if "changed_by" not in request.data:
            request.data["changed_by"] = self.request.user.username
        try:

            profile_data = {
                "name": request.data["name"],
                "phone": request.data["phone"],
                "email": request.data.get("email",None),
                "contact_person_name": request.data.get("contact_person_name", None),
                "contact_person_phone": request.data.get("contact_person_phone", None),
                "comment": request.data.get("remarks", None)
            }
        except KeyError:
            return Response({"error": "Key Error"}, status=status.HTTP_400_BAD_REQUEST)

        username = generate_username(profile_data["name"], profile_data["phone"])
        password = "X@RWERT21RW!@#"

        user_serializer = UserSerializer(data={"username": username, "password": password})
        if user_serializer.is_valid():
            user = user_serializer.save()
            profile_data["user"] = user.id
            profile_serializer = ProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save()
                request.data["name"] = user.id
                request.data["owner_phone"] = profile_data["phone"]
                owner_serializer = OwnerSerializer(data=request.data)
                if owner_serializer.is_valid():
                    owner = owner_serializer.save()
                    Vehicle.objects.filter(id__in=request.data.get("vehicles_detail", [])).update(owner=owner)
                    response = {
                        "status_code": status.HTTP_201_CREATED,
                        "status": "Success",
                        "msg": "Owner Created",
                        "data": owner_serializer.data
                    }
                    return Response(data=response, status=status.HTTP_201_CREATED)
                user.delete()
                response = {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "status": "Error",
                    "msg": "Owner not Created",
                    "data": owner_serializer.errors
                }
                return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
            user.delete()
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        owner = get_or_none(Owner, id=pk)
        if not isinstance(owner, Owner):
            return Response({"error": "Owner does not exist"}, status=status.HTTP_404_NOT_FOUND)

        owner_serializer = OwnerSerializer(instance=owner, data=request.data)
        if owner_serializer.is_valid():
            owner_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Owner Updated",
                "data": owner_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Owner not Updated",
            "data": owner_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        owner = get_or_none(Owner, id=pk)
        if not isinstance(owner, Owner):
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Owner Doesnot Exists', data={})

        profile = get_or_none(Profile, user=owner.name)
        parsed_data = parse_update_owner_data(request.data, id=pk)
        parsed_data["changed_by"] = self.request.user.username
        if isinstance(profile, Profile) and parsed_data['profile_data']:
            profile_serializer = ProfileSerializer(instance=profile, data=parsed_data['profile_data'], partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                return error_response(
                    status=status.HTTP_400_BAD_REQUEST, msg='Invalid owner data', data=profile_serializer.errors)
        else:
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Profile Doesnot Exists', data={})
        vehicles_id = parsed_data.pop('vehicles_detail')
        Vehicle.objects.filter(id__in=vehicles_id).update(owner=owner)
        Vehicle.objects.exclude(id__in=vehicles_id).filter(owner=owner).update(owner=None)
        owner_serializer = OwnerSerializer(
            instance=owner,
            data=parsed_data,
            partial=True
        )
        if owner_serializer.is_valid():
            owner_serializer.save()
            return success_response(status=status.HTTP_202_ACCEPTED, msg='Owner updated', data=owner_serializer.data)
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Something went wrong',
                              data=owner_serializer.errors)

    def retrieve(self, request, pk=None):
        owner = get_or_none(Owner, id=pk)
        if not isinstance(owner, Owner):
            return Response({"error": "Owner does not exist"}, status=status.HTTP_404_NOT_FOUND)
        owner_serializer = OwnerSerializer(owner)
        return Response(owner_serializer.data, template_name='team/registrations/owner-update.html',
                        status=status.HTTP_200_OK)


class OwnerVehicleListView(generics.ListAPIView):
    queryset = Vehicle.objects.exclude(deleted=True).order_by('-id')
    serializer_class = FMSVehicleSerializer
    pagination_class = CustomeDatatablesPaginator
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = OwnerVehicleFilter
    search_fields = (
        'id', 'owner__name__username', 'driver__name', 'rc_number', 'permit', 'permit_type',
        'vehicle_type__vehicle_type', 'vehicle_capacity', 'body_type', 'vehicle_number', 'vehicle_model', 'created_on')

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

    def get_serializer_class(self):
        if is_fms_user(user=self.request.user):
            return FMSVehicleSerializer

        return VehicleSerializer

    def get_queryset(self):
        if is_fms_user(user=self.request.user):
            broker = Broker.objects.get(name=self.request.user)
            bv_id = broker.broker_vehicle.exclude(deleted=True).values_list('vehicle_id', flat=True)
            return Vehicle.objects.filter(id__in=bv_id).exclude(deleted=True)
        elif is_sme_user(user=self.request.user):
            from team.models import ManualBooking
            sme = get_or_none(Sme, name=self.request.user)
            if isinstance(sme, Sme):
                vehicles_id = ManualBooking.objects.filter(company=sme).exclude(booking_status='cancelled').values_list(
                    'vehicle_id', flat=True)
                return Vehicle.objects.filter(id__in=list(set(list(vehicles_id))))
            return Vehicle.objects.none()
        return Vehicle.objects.exclude(deleted=True)


class OwnerVehicleSummaryListView(generics.ListAPIView):
    serializer_class = VehicleSummarySerializer
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
        queryset = VehicleSummary.objects.exclude(deleted=True).annotate(
            completed_pod_balance_amount=RawSQL(
                "(accounting_summary->>%s)::numeric", ("completed_pod_balance_amount",))
        ).order_by('-completed_pod_balance_amount')
        return queryset


class OwnerVehicleViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Owner Vehicle
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def create(self, request, pk=None):
        request.data['vehicle_number'] = compare_format(request.data['vehicle_number'])
        if "created_by" not in request.data:
            request.data["created_by"] = self.request.user.username
        if "changed_by" not in request.data:
            request.data["changed_by"] = self.request.user.username
        if request.data.get('gps_enabled', None) == 'yes':
            request.data['gps_enabled'] = True
        else:
            request.data['gps_enabled'] = False
        if request.data.get('registration_year', None) and 'registration_year' in request.data:
            request.data['registration_year'] = '01-Jan-{}'.format(request.data['registration_year'].strip())
        vehicle_serializer = VehicleSerializer(data=request.data)
        if vehicle_serializer.is_valid():
            vehicle_serializer.save()
            return success_response(status=status.HTTP_201_CREATED, msg="Vehicle Created", data=vehicle_serializer.data)
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Vehicle not Created",
                              data=vehicle_serializer.errors)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

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
                return error_response(msg='Vehicle with id=%s does not exist' % vehicle_id,
                                      status=status.HTTP_404_NOT_FOUND, data=None)
        if request.data.get('gps_enabled', None) == 'yes':
            request.data['gps_enabled'] = True
        else:
            request.data['gps_enabled'] = False

        data = request.data
        parsed_data = parse_vehicle_docs(request.data)
        request.data["changed_by"] = self.request.user.username
        vehicle = get_or_none(Vehicle, id=pk)

        vehicle_serializers = VehicleSerializer(
            instance=vehicle,
            data=parsed_data,
            partial=True
        )
        if vehicle_serializers.is_valid():
            vehicle_serializers.save()

        owner = vehicle.owner if isinstance(vehicle.owner, Owner) else None
        driver = vehicle.driver if isinstance(vehicle.driver, Driver) else None
        if isinstance(owner, Owner) and parsed_data.get('owner_data', None):
            owner_serializer = OwnerSerializer(
                instance=owner,
                data=parsed_data.get('owner_data', None),
                partial=True
            )
            if owner_serializer.is_valid():
                owner_serializer.save()
            else:
                pass
        if isinstance(driver, Driver) and parsed_data.get('driver_data', None):
            driver_serializer = DriverSerializer(
                instance=driver,
                data=parsed_data.get('driver_data', None),
                partial=True
            )
            if driver_serializer.is_valid():
                driver_serializer.save()

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
                    owner=owner,
                    document_category='PAN',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(OwnerFile, owner=owner),
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
                    owner=owner,
                    document_category='DEC',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(OwnerFile, owner=owner),
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
                    driver=driver,
                    document_category='DL',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(DriverFile, driver=driver),
                    s3_upload=s3_upload,
                )
        vehicle = get_or_none(Vehicle, id=pk)
        vehicle_serializer = FMSVehicleSerializer(instance=vehicle)
        return success_response(
            msg='vehicle details %s' % ('edited' if vehicle_id else 'saved'),
            data=vehicle_serializer.data, status=status.HTTP_202_ACCEPTED
        )

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        if request.data.get('registration_year', None) and 'registration_year' in request.data:
            request.data['registration_year'] = '01-Jan-{}'.format(request.data['registration_year'].strip())
        vehicle = get_or_none(Vehicle, id=pk)
        data = request.data
        if not isinstance(vehicle, Vehicle):
            return Response({"error": "Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if 'owner' not in data:
            data['owner'] = None
        vehicle_serializers = VehicleSerializer(
            instance=vehicle,
            data=data,
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

        vehicle_serializers = VehicleSerializer(vehicle)
        if is_fms_user(request.user):
            vehicle_serializers = FMSVehicleSerializer(vehicle)
        return Response(template_name='team/registrations/update-vehicle.html', data=vehicle_serializers.data,
                        status=status.HTTP_200_OK)


class FuelCardListView(generics.ListAPIView):
    filter_class = FuelCardFilter
    queryset = FuelCard.objects.exclude(deleted=True).exclude(card_number=None).order_by('-id')
    serializer_class = Select2FuelCardSerializer
    pagination_class = CustomeDatatablesPaginator
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    # filter_class = OwnerVehicleFilter
    search_fields = (
        'id', 'customer_id', 'card_number', 'issue_date', 'expiry_date', 'created_by__username',
        'created_on')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Success", "status_code": status.HTTP_200_OK, "msg": "Fuel Card Summary List"}
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)
        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class FuelCardViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Fuel Card
    """

    def create(self, request, pk=None):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        fuel_card_serializer = FuelCardSerializer(data=request.data)
        if fuel_card_serializer.is_valid():
            fuel_card_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Fuel Card Created",
                "data": fuel_card_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Fuel Card not Created",
            "data": fuel_card_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        fuel_card = get_or_none(FuelCard, id=pk)
        if not isinstance(fuel_card, FuelCard):
            return Response({"error": "Fuel Card does not exist"}, status=status.HTTP_404_NOT_FOUND)
        fuel_card_serializers = FuelCardSerializer(instance=fuel_card, data=request.data)
        if fuel_card_serializers.is_valid():
            fuel_card_serializers.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Fuel Card Updated",
                "data": fuel_card_serializers.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Fuel Card not Updated",
            "data": fuel_card_serializers.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        fuel_card = get_or_none(FuelCard, id=pk)
        if not isinstance(fuel_card, FuelCard):
            return Response({"error": "Fuel Card does not exist"}, status=status.HTTP_404_NOT_FOUND)
        fuel_card_serializers = FuelCardSerializer(
            instance=fuel_card,
            data=request.data,
            partial=True
        )
        if fuel_card_serializers.is_valid():
            fuel_card_serializers.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Fuel Card Updated",
                "data": fuel_card_serializers.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Fuel Card not Updated",
            "data": fuel_card_serializers.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        fuel_card = get_or_none(FuelCard, id=pk)
        if not isinstance(fuel_card, FuelCard):
            return Response({"error": "Fuel Card does not exist"}, status=status.HTTP_404_NOT_FOUND)
        fuel_card_serializers = FuelCardSerializer(fuel_card)
        return Response(fuel_card_serializers.data, status=status.HTTP_200_OK)


class FuelCardTransactionViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of Owner FuelCardTransaction
    """

    def create(self, request, pk=None):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        fuel_card_transaction_serializer = FuelCardTransactionSerializer(data=request.data)
        if fuel_card_transaction_serializer.is_valid():
            fuel_card_transaction_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Fuel Card Transaction Created",
                "data": fuel_card_transaction_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Fuel Card Transaction not Created",
            "data": fuel_card_transaction_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        fuel_card_transaction = get_or_none(FuelCardTransaction, id=pk)
        if not isinstance(fuel_card_transaction, FuelCardTransaction):
            return Response({"error": "Fuel Card Transaction does not exist"}, status=status.HTTP_404_NOT_FOUND)
        fuel_card_transaction_serializers = FuelCardTransactionSerializer(instance=fuel_card_transaction,
                                                                          data=request.data)
        if fuel_card_transaction_serializers.is_valid():
            fuel_card_transaction_serializers.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Fuel Card Transaction Updated",
                "data": fuel_card_transaction_serializers.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Fuel Card Transaction not Updated",
            "data": fuel_card_transaction_serializers.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        fuel_card_transaction = get_or_none(FuelCardTransaction, id=pk)
        if not isinstance(fuel_card_transaction, FuelCardTransaction):
            return Response({"error": "Fuel Card Transaction does not exist"}, status=status.HTTP_404_NOT_FOUND)
        fuel_card_transaction_serializers = FuelCardTransactionSerializer(
            instance=fuel_card_transaction,
            data=request.data,
            partial=True
        )
        if fuel_card_transaction_serializers.is_valid():
            fuel_card_transaction_serializers.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Fuel Card Transaction Updated",
                "data": fuel_card_transaction_serializers.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Fuel Card Transaction not Updated",
            "data": fuel_card_transaction_serializers.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        fuel_card_transaction = get_or_none(FuelCardTransaction, id=pk)
        if not isinstance(fuel_card_transaction, FuelCardTransaction):
            return Response({"error": "Fuel Card Transaction does not exist"}, status=status.HTTP_404_NOT_FOUND)
        fuel_card_transaction_serializers = FuelCardTransactionSerializer(fuel_card_transaction)
        return Response(fuel_card_transaction_serializers.data, status=status.HTTP_200_OK)
