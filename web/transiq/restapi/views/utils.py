from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters, generics
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response

from api.utils import get_ext
from restapi.filter.utils import BankFilter, CityFilter, AahoOfficeFilter
from restapi.helper_api import success_response, error_response
from restapi.search import CustomSearch
from restapi.serializers.authentication import BankSerializer
from restapi.serializers.utils import StateSerializer, CitySerializer, AddressSerializer, IDDetailsSerializer, \
    BankNameSerializer, IfscDetailSerializer, AahoOfficeSerializer, TaxationIDSerializer
from restapi.utils import get_or_none
from team import tasks
from transiq.settings.choices import outward_payment_mode_choices, inward_payment_mode_choices, \
    booking_outward_payment_status_choices, booking_inward_payment_status_choices, booking_invoice_status_choices, \
    booking_pod_status_choices, booking_billing_type_choices, outward_payment_status_choices, \
    outward_payment_refund_category_choices
from utils.models import State, City, Address, IDDetails, BankName, IfscDetail, Bank, AahoOffice, TaxationID


class StateListView(generics.ListAPIView):
    serializer_class = StateSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    queryset = State.objects.exclude(deleted=True).order_by("-id")
    # filter_class = Sate
    ordering_fields = ('id',)
    search_fields = (
        'id', 'name', 'code')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "State List"}

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)
        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class StateViewSet(viewsets.ViewSet):

    # def list(self, request):
    #     pass

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        state_serializer = StateSerializer(data=request.data)
        if state_serializer.is_valid():
            state_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "State Created",
                "data": state_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "State not Created",
            "data": state_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        state = get_or_none(State, id=pk)
        if not isinstance(state, State):
            return Response({"error": "State does not exist"}, status=status.HTTP_404_NOT_FOUND)
        state_serializer = StateSerializer(state, data=request.data)

        if state_serializer.is_valid():
            state_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "State Updated",
                "data": state_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "State not Updated",
            "data": state_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        state = get_or_none(State, id=pk)
        if not isinstance(state, State):
            return Response({"error": "State does not exist"}, status=status.HTTP_404_NOT_FOUND)
        state_serializer = StateSerializer(
            instance=state,
            data=request.data,
            partial=True
        )

        if state_serializer.is_valid():
            state_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "State Updated",
                "data": state_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "State not Updated",
            "data": state_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        state = get_or_none(State, id=pk)
        if isinstance(state, State):
            state_serializer = StateSerializer(state)
            return Response(state_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "State does not exist"}, status=status.HTTP_404_NOT_FOUND)


class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    queryset = City.objects.exclude(deleted=True).order_by("-id")
    filter_class = CityFilter
    ordering_fields = ('id',)
    search_fields = (
        'id', 'name', 'code', 'state__name')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "City List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class CityViewSet(viewsets.ViewSet):

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        city_serializer = CitySerializer(data=request.data)
        if city_serializer.is_valid():
            city_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "City Created",
                "data": city_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "City not Created",
            "data": city_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        city = get_or_none(City, id=pk)
        if not isinstance(city, City):
            return Response({"error": "City does not exist"}, status=status.HTTP_404_NOT_FOUND)
        city_serializer = CitySerializer(city, data=request.data)

        if city_serializer.is_valid():
            city_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "City Updated",
                "data": city_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "City not Updated",
            "data": city_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        city = get_or_none(City, id=pk)
        if not isinstance(city, City):
            return Response({"error": "City does not exist"}, status=status.HTTP_404_NOT_FOUND)
        city_serializer = CitySerializer(
            instance=city,
            data=request.data,
            partial=True
        )

        if city_serializer.is_valid():
            city_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "City Updated",
                "data": city_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "City not Updated",
            "data": city_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        city = get_or_none(City, id=pk)
        if isinstance(city, City):
            city_serializer = CitySerializer(city)
            return Response(city_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "City does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # def soft_destroy_all_related_objects(self, to_delete):
    #     for obj in to_delete:
    #         if not isinstance(obj, list):
    #             obj.deleted = True
    #
    #             #obj.save()
    #             #return
    #         else:
    #             self.soft_destroy_all_related_objects(obj)
    #
    # def soft_destroy(self, request, pk=None):
    #     city = get_or_none(City, id=pk)
    #     if not isinstance(city, City):
    #         return Response({"error": "City does not exist"}, status=status.HTTP_404_NOT_FOUND)
    #
    #     to_delete, protected, model_count = get_deleted_objects([city])
    #     self.soft_destroy_all_related_objects(to_delete)
    #     city_serializer = CitySerializer(city)
    #     return Response(city_serializer.data, status=status.HTTP_200_OK)


class AddressViewSet(viewsets.ViewSet):

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        address_serializer = AddressSerializer(data=request.data)
        if address_serializer.is_valid():
            address_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Address Created",
                "data": address_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Address not Created",
            "data": address_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        address = get_or_none(Address, id=pk)
        if not isinstance(address, Address):
            return Response({"error": "Address does not exist"}, status=status.HTTP_404_NOT_FOUND)
        address_serializer = AddressSerializer(address, data=request.data)

        if address_serializer.is_valid():
            address_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Address Updated",
                "data": address_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Address not Updated",
            "data": address_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        address = get_or_none(Address, id=pk)
        if not isinstance(address, Address):
            return Response({"error": "Address does not exist"}, status=status.HTTP_404_NOT_FOUND)
        address_serializer = AddressSerializer(
            instance=address,
            data=request.data,
            partial=True
        )

        if address_serializer.is_valid():
            address_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Address Updated",
                "data": address_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Address not Updated",
            "data": address_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        address = get_or_none(Address, id=pk)
        if isinstance(address, Address):
            address_serializer = AddressSerializer(address)
            return Response(address_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Address does not exist"}, status=status.HTTP_404_NOT_FOUND)


class IDDetailsViewSet(viewsets.ViewSet):

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        idd_details_serializer = IDDetailsSerializer(data=request.data)
        if idd_details_serializer.is_valid():
            idd_details_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "ID Details Created",
                "data": idd_details_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "ID Details not Created",
            "data": idd_details_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        idd_details = get_or_none(IDDetails, id=pk)
        if not isinstance(idd_details, IDDetails):
            return Response({"error": "ID Details does not exist"}, status=status.HTTP_404_NOT_FOUND)
        idd_details_serializer = IDDetailsSerializer(idd_details, data=request.data)

        if idd_details_serializer.is_valid():
            idd_details_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "ID Details Updated",
                "data": idd_details_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "ID Details not Updated",
            "data": idd_details_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        idd_details = get_or_none(IDDetails, id=pk)
        if not isinstance(idd_details, IDDetails):
            return Response({"error": "ID Details does not exist"}, status=status.HTTP_404_NOT_FOUND)
        idd_details_serializer = IDDetailsSerializer(
            instance=idd_details,
            data=request.data,
            partial=True
        )

        if idd_details_serializer.is_valid():
            idd_details_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "ID Details Updated",
                "data": idd_details_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "ID Details not Updated",
            "data": idd_details_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        idd_details = get_or_none(IDDetails, id=pk)
        if isinstance(idd_details, IDDetails):
            idd_details_serializer = IDDetailsSerializer(idd_details)
            return Response(idd_details_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "ID Details does not exist"}, status=status.HTTP_404_NOT_FOUND)


class BankNameViewSet(viewsets.ViewSet):

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        bank_name_serializer = BankNameSerializer(data=request.data)
        if bank_name_serializer.is_valid():
            bank_name_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Bank Name Created",
                "data": bank_name_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Bank Name not Created",
            "data": bank_name_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        bank_name = get_or_none(BankName, id=pk)
        if not isinstance(bank_name, BankName):
            return Response({"error": "Bank Name does not exist"}, status=status.HTTP_404_NOT_FOUND)
        bank_name_serializer = BankNameSerializer(bank_name, data=request.data)

        if bank_name_serializer.is_valid():
            bank_name_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Bank Name Updated",
                "data": bank_name_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Bank Name not Updated",
            "data": bank_name_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        bank_name = get_or_none(BankName, id=pk)
        if not isinstance(bank_name, BankName):
            return Response({"error": "Bank Name does not exist"}, status=status.HTTP_404_NOT_FOUND)
        bank_name_serializer = BankNameSerializer(
            instance=bank_name,
            data=request.data,
            partial=True
        )

        if bank_name_serializer.is_valid():
            bank_name_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Bank Name Updated",
                "data": bank_name_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Bank Name not Updated",
            "data": bank_name_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        bank_name = get_or_none(BankName, id=pk)
        if isinstance(bank_name, BankName):
            bank_name_serializer = BankNameSerializer(bank_name)
            return Response(bank_name_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Bank Name does not exist"}, status=status.HTTP_404_NOT_FOUND)


class IfscDetailViewSet(viewsets.ViewSet):

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        ifsc_detail_serializer = IfscDetailSerializer(data=request.data)
        if ifsc_detail_serializer.is_valid():
            ifsc_detail_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Ifsc Detail Created",
                "data": ifsc_detail_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Ifsc Detail not Created",
            "data": ifsc_detail_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        ifsc_detail = get_or_none(IfscDetail, id=pk)
        if not isinstance(ifsc_detail, IfscDetail):
            return Response({"error": "Ifsc Detail does not exist"}, status=status.HTTP_404_NOT_FOUND)
        ifsc_detail_serializer = IfscDetailSerializer(ifsc_detail, data=request.data)

        if ifsc_detail_serializer.is_valid():
            ifsc_detail_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Ifsc Detail Updated",
                "data": ifsc_detail_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Ifsc Detail not Updated",
            "data": ifsc_detail_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        ifsc_detail = get_or_none(IfscDetail, id=pk)
        if not isinstance(ifsc_detail, IfscDetail):
            return Response({"error": "Ifsc Detail does not exist"}, status=status.HTTP_404_NOT_FOUND)
        ifsc_detail_serializer = IfscDetailSerializer(
            instance=ifsc_detail,
            data=request.data,
            partial=True
        )

        if ifsc_detail_serializer.is_valid():
            ifsc_detail_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Ifsc Detail Updated",
                "data": ifsc_detail_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Ifsc Detail not Updated",
            "data": ifsc_detail_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        ifsc_detail = get_or_none(IfscDetail, id=pk)
        if isinstance(ifsc_detail, IfscDetail):
            ifsc_detail_serializer = IfscDetailSerializer(ifsc_detail)
            return Response(ifsc_detail_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Ifsc Detail does not exist"}, status=status.HTTP_404_NOT_FOUND)


class BankListView(generics.ListAPIView):
    serializer_class = BankSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    queryset = Bank.objects.exclude(deleted=True).order_by("-id")
    filter_class = BankFilter
    ordering_fields = ('id',)
    search_fields = (
        'id', 'user__username', 'bank', 'account_holder_name', 'beneficiary_code', 'account_number', 'transaction_type',
        'account_type', 'ifsc', 'address', 'city', 'remarks', 'is_verified', 'status', 'created_on',
        'created_by__username')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "Bank Account List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class BankNameListView(generics.ListAPIView):
    serializer_class = BankNameSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    queryset = BankName.objects.exclude(deleted=True).order_by("-id")
    ordering_fields = ('id',)
    search_fields = (
        'id', 'name')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "Bank Name List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class BankViewSet(viewsets.ViewSet):
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        if 'beneficiary_code' in request.data and request.data.get('beneficiary_code', None) and len(request.data.get('beneficiary_code', None)) > 3:
            if Bank.objects.filter(beneficiary_code=request.data.get('beneficiary_code')).exists():
                return error_response(msg="Beneficiary Code Already exists, Pls try with other berneficiary code",
                                      data={}, status=status.HTTP_400_BAD_REQUEST)
        if 'account_number' in request.data and request.data.get('account_number', None) and len(request.data.get('account_number', None)) > 3:
            if Bank.objects.filter(account_number=request.data.get('account_number')).exists():
                return error_response(msg="A/C No.: {} is already registered, Pls verify account number".format(request.data.get('account_number')),
                                      data={}, status=status.HTTP_400_BAD_REQUEST)
        bank_serializer = BankSerializer(data=request.data)
        if bank_serializer.is_valid():
            bank = bank_serializer.save()
            try:
                account_document = request.FILES['account_document']
            except MultiValueDictKeyError:
                account_document = None
            if settings.ENABLE_MAIL:
                if settings.ENABLE_CELERY:
                    tasks.email_add_new_beneficiary.delay(bank_id=bank.id)
                else:
                    tasks.email_add_new_beneficiary(bank_id=bank.id)
            if account_document:
                filename = '%s.%s' % (bank.account_number, get_ext(account_document.name))
            #     s3util.save_to_s3_uploads_bank_doc(filename, account_document)
            return success_response(data=bank_serializer.data,
                                    msg='Bank account number {} is created'.format(bank.account_number),
                                    status=status.HTTP_201_CREATED)
        return error_response(data=bank_serializer.errors, msg='Something went wrong',
                              status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        bank = get_or_none(Bank, id=pk)
        if not isinstance(bank, Bank):
            return Response({"error": "Bank does not exist"}, status=status.HTTP_404_NOT_FOUND)
        bank_serializer = BankSerializer(bank, data=request.data)

        if bank_serializer.is_valid():
            bank_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Bank Updated",
                "data": bank_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Bank not Updated",
            "data": bank_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        bank = get_or_none(Bank, id=pk)
        if not isinstance(bank, Bank):
            return Response({"error": "Bank does not exist"}, status=status.HTTP_404_NOT_FOUND)
        bank_serializer = BankSerializer(
            instance=bank,
            data=request.data,
            partial=True
        )

        if bank_serializer.is_valid():
            bank_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Bank Updated",
                "data": bank_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Bank not Updated",
            "data": bank_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        bank = get_or_none(Bank, id=pk)
        if isinstance(bank, Bank):
            bank_serializer = BankSerializer(bank)
            return Response(template_name='team/registrations/update-bank-account.html', data=bank_serializer.data,
                            status=status.HTTP_200_OK)
        return Response({"error": "Bank does not exist"}, status=status.HTTP_404_NOT_FOUND)


class TaxationIDViewSet(viewsets.ViewSet):

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        taxation_id_serializer = TaxationIDSerializer(data=request.data)
        if taxation_id_serializer.is_valid():
            taxation_id_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "TaxationID Created",
                "data": taxation_id_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "TaxationID not Created",
            "data": taxation_id_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        taxation_id = get_or_none(TaxationID, id=pk)
        if not isinstance(taxation_id, TaxationID):
            return Response({"error": "TaxationID does not exist"}, status=status.HTTP_404_NOT_FOUND)
        taxation_id_serializer = TaxationIDSerializer(taxation_id, data=request.data)

        if taxation_id_serializer.is_valid():
            taxation_id_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "TaxationID Updated",
                "data": taxation_id_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "TaxationID not Updated",
            "data": taxation_id_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        taxation_id = get_or_none(TaxationID, id=pk)
        if not isinstance(taxation_id, TaxationID):
            return Response({"error": "TaxationID does not exist"}, status=status.HTTP_404_NOT_FOUND)
        taxation_id_serializer = TaxationIDSerializer(
            instance=taxation_id,
            data=request.data,
            partial=True
        )

        if taxation_id_serializer.is_valid():
            taxation_id_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "TaxationID Updated",
                "data": taxation_id_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "TaxationID not Updated",
            "data": taxation_id_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        taxation_id = get_or_none(TaxationID, id=pk)
        if isinstance(taxation_id, TaxationID):
            taxation_id_serializer = TaxationIDSerializer(taxation_id)
            return Response(taxation_id_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "TaxationID does not exist"}, status=status.HTTP_404_NOT_FOUND)


class AahoOfficeListView(generics.ListAPIView):
    serializer_class = AahoOfficeSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    queryset = AahoOffice.objects.exclude(deleted=True).order_by("-id")
    filter_class = AahoOfficeFilter
    ordering_fields = ('id',)
    search_fields = (
        'id', 'branch_name', 'branch__name', 'address')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "Aaho Office List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class AahoOfficeViewSet(viewsets.ViewSet):

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        aaho_office_serializer = AahoOfficeSerializer(data=request.data)
        if aaho_office_serializer.is_valid():
            aaho_office_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Aaho Office Created",
                "data": aaho_office_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Aaho Office not Created",
            "data": aaho_office_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        aaho_office = get_or_none(AahoOffice, id=pk)
        if not isinstance(aaho_office, AahoOffice):
            return Response({"error": "Aaho Office does not exist"}, status=status.HTTP_404_NOT_FOUND)
        aaho_office_serializer = AahoOfficeSerializer(aaho_office, data=request.data)

        if aaho_office_serializer.is_valid():
            aaho_office_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Aaho Office Updated",
                "data": aaho_office_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Aaho Office not Updated",
            "data": aaho_office_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        aaho_office = get_or_none(AahoOffice, id=pk)
        if not isinstance(aaho_office, AahoOffice):
            return Response({"error": "Aaho Office does not exist"}, status=status.HTTP_404_NOT_FOUND)
        aaho_office_serializer = AahoOfficeSerializer(
            instance=aaho_office,
            data=request.data,
            partial=True
        )

        if aaho_office_serializer.is_valid():
            aaho_office_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Aaho Office Updated",
                "data": aaho_office_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Aaho Office not Updated",
            "data": aaho_office_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        aaho_office = get_or_none(AahoOffice, id=pk)
        if isinstance(aaho_office, AahoOffice):
            aaho_office_serializer = AahoOfficeSerializer(aaho_office)
            return Response(aaho_office_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Aaho Office does not exist"}, status=status.HTTP_404_NOT_FOUND)


class MultipleChoicesFilterListView(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):
        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "Multi Choices filter List"}
        filter_key = request.GET.get('filter_key', None)
        if filter_key == 'outward_payment_mode_choices':
            data["data"] = outward_payment_mode_choices()
        elif filter_key == 'outward_payment_status_choices':
            data['data'] = outward_payment_status_choices()
        elif filter_key == 'outward_payment_refund_category_choices':
            data['data'] = outward_payment_refund_category_choices()
        elif filter_key == 'inward_payment_mode_choices':
            data['data'] = inward_payment_mode_choices()
        elif filter_key == 'booking_outward_payment_status_choices':
            data['data'] = booking_outward_payment_status_choices()
        elif filter_key == 'booking_inward_payment_status_choices':
            data['data'] = booking_inward_payment_status_choices()
        elif filter_key == 'booking_invoice_status_choices':
            data['data'] = booking_invoice_status_choices()
        elif filter_key == 'booking_pod_status_choices':
            data['data'] = booking_pod_status_choices()
        elif filter_key == 'booking_billing_type_choices':
            data['data'] = booking_billing_type_choices()
        else:
            data['data'] = []
        return Response(data)
