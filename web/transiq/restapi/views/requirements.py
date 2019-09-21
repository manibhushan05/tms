import datetime
import json
from datetime import timedelta

from django.db.models import QuerySet, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status, filters
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from restapi.search import CustomSearch
from employee.models import Employee
from fms.models import RequirementQuote, Requirement, REQ_STATUS, REQ_CANCEL_REASONS
from restapi.filter.requirement import RequirementQuotesFilter
from restapi.helper_api import get_employee_roles
from restapi.models import EmployeeRolesMapping, EmployeeRolesFunctionalityMapping
from restapi.pagination import CustomeDatatablesPaginator
from restapi.serializers.requirements import QuoteVehiclesSerializer, RequirementVehicleQuoteSerializer, \
    RequirementQuoteSerializer, RequirementSerializer
from restapi.utils import get_or_none
from sme.models import Sme


class RequirementQuotesListView(generics.ListAPIView):
    queryset = RequirementQuote.objects.order_by('-id').exclude(deleted=True)
    serializer_class = RequirementQuoteSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = RequirementQuotesFilter
    ordering_fields = ('id',)
    search_fields = ('id', 'broker__id', 'requirement_vehicle_quote__requirement__id')

    def get(self, request, *args, **kwargs):
        if self.request.content_type != 'application/json':
            response = {"status": "failure", "msg": "Wrong Content Type. Must be application/json",
                        "data": {"requirements": {}}}
            return Response(response, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = {"status": "success", "msg": "inquiry quotes data","status_code": status.HTTP_200_OK, "http_status": status.HTTP_200_OK,
                        "data": {"requirement_quotes": serializer.data}}
            return self.get_paginated_response(response)

        serializer = self.get_serializer(queryset, many=True)
        response = {"status": "success", "msg": "inquiry quotes data","status_code": status.HTTP_200_OK, "data": {"requirement_quotes": serializer.data}}
        return Response(response)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Inquiry Quotes List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)


class RequirementQuotesViewSet(viewsets.ViewSet):
    """

    A simple ViewSet for listing or retrieving Requirement Quotes.

    """

    def create(self, request):
        quote_vehicles_serializer = QuoteVehiclesSerializer(data=request.data)
        if quote_vehicles_serializer.is_valid():
            response = quote_vehicles_serializer.check_vehicle_no_pattern(quote_vehicles_serializer.validated_data)
            if response['status'] == 'failure':
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            quote_vehicles = quote_vehicles_serializer.save()
        else:
            return Response(quote_vehicles_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        data.update({'quote_vehicle_id': quote_vehicles.id})
        requirement_vehicle_quote_serializer = RequirementVehicleQuoteSerializer(data=data)
        if requirement_vehicle_quote_serializer.is_valid():
            requirement_vehicle_quote = requirement_vehicle_quote_serializer.save()
        else:
            return Response(requirement_vehicle_quote_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        data.update({'requirement_vehicle_quote_id': requirement_vehicle_quote.id})
        requirement_quote_serializer = RequirementQuoteSerializer(data=data)
        if requirement_quote_serializer.is_valid():
            requirement_quote_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Inquiry Quote Created",
                "data": requirement_quote_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "Error",
                "msg": "Inquiry Quote not Created",
                "data": requirement_quote_serializer.errors
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = RequirementQuote.objects.all().exclude(deleted=True)
        req_quote = get_object_or_404(queryset, pk=pk)
        serializer = RequirementQuoteSerializer(req_quote)
        if self.request.content_type != 'application/json':
            response = {"status": "failure", "msg": "Wrong Content Type. Must be application/json",
                        "data": {"requirements": {}}}
            return Response(response, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        if self.request.content_type != 'application/json':
            response = {"status": "failure", "msg": "Wrong Content Type. Must be application/json",
                        "data": {"requirements": {}}}
            return Response(response, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        quote_vehicles_serializer = QuoteVehiclesSerializer(data=request.data)
        if quote_vehicles_serializer.is_valid():
            response = quote_vehicles_serializer.check_vehicle_no_pattern(quote_vehicles_serializer.validated_data)
            if response['status'] == 'failure':
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            quote_vehicles = quote_vehicles_serializer.save()
        else:
            return Response(quote_vehicles_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        data.update({'quote_vehicle_id': quote_vehicles.id})
        requirement_vehicle_quote_serializer = RequirementVehicleQuoteSerializer(data=data)
        if requirement_vehicle_quote_serializer.is_valid():
            requirement_vehicle_quote = requirement_vehicle_quote_serializer.save()
        else:
            return Response(requirement_vehicle_quote_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        data.update({'requirement_vehicle_quote_id': requirement_vehicle_quote.id})
        try:
            req_quote = RequirementQuote.objects.get(id=pk)
        except RequirementQuote.DoesNotExist:
            return Response({"status": "Inquiry Quote Doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        requirement_quote_serializer = RequirementQuoteSerializer(instance=req_quote, data=data)
        if requirement_quote_serializer.is_valid():
            req_quote = requirement_quote_serializer.save()
            if req_quote:
                response = {
                    "status_code": status.HTTP_202_ACCEPTED,
                    "status": "Success",
                    "msg": "Inquiry Quote Updated",
                    "data": requirement_quote_serializer.data
                }
                return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Inquiry Quote not Updated",
            "data": requirement_quote_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = RequirementQuote.objects.all()
        requirement_quote = get_object_or_404(queryset, pk=pk)
        serializer = RequirementQuoteSerializer(requirement_quote)
        requirement_quote.deleted = True
        requirement_quote.deleted_on = timezone.now()
        requirement_quote.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequirementListView(generics.ListAPIView):
    queryset = Requirement.objects.order_by('-id').exclude(deleted=True)
    serializer_class = RequirementSerializer
    pagination_class = CustomeDatatablesPaginator
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('id',)
    # filter_class =RequirementFilters

    search_fields = (
        'id', 'from_shipment_date', 'to_shipment_date', 'client__name__profile__name', 'from_city__name',
        'to_city__name', 'aaho_office__branch_name', 'tonnage', 'no_of_vehicles', 'rate', 'material',
        'type_of_vehicle__vehicle_type','req_status', 'remark','cancel_reason')

    user_filter = False

    def get_queryset(self):
        queryset = self.queryset
        return_response = {"status": "failure", "queryset": "Inquiry Does Not Exist",
                           "status_code": status.HTTP_200_OK}
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
            aaho_office_id = self.request.query_params.get('aaho_office_id', None)
            requirement_status = self.request.query_params.get('requirement_status', None)
            if aaho_office_id is None and requirement_status is None and not self.user_filter:
                return_response['queryset'] = queryset
                return_response['status'] = 'success'
                return return_response
            else:
                if self.user_filter:
                    return self.get_user_filtered_requirements()
                if len(self.request.query_params) <= 3:
                    return self.get_filtered_requirements(queryset, aaho_office_id, requirement_status)
                else:
                    return_response['queryset'] = {"msg": "Check API params"}
                    return_response['status_code'] = status.HTTP_400_BAD_REQUEST
                    return return_response
        else:
            return return_response

    def get_filtered_requirements(self, queryset, aaho_office_id, requirement_status):
        return_response = {"status": "failure", "queryset": {"msg": "No inquiry found"},
                           "status_code": status.HTTP_400_BAD_REQUEST}
        q_objects = Q()
        unfiltered_queryset = queryset
        no_filter = False
        city_head_filter = False
        emp_roles_response = get_employee_roles(self.request.user)
        if emp_roles_response['status'] == 'success' and ('management' in emp_roles_response['roles']
                                                          or 'tech' in emp_roles_response['roles']):
            no_filter = True
        elif emp_roles_response['status'] == 'success' and ('city_head' in emp_roles_response['roles']):
            city_head_filter = True

        if aaho_office_id and requirement_status:
            q_objects |= Q(**{'aaho_office': aaho_office_id, 'req_status': requirement_status})
        elif requirement_status:
            q_objects |= Q(**{'req_status': requirement_status})
        else:
            q_objects |= Q(**{'aaho_office': aaho_office_id})

        if requirement_status and requirement_status not in [x[0] for x in REQ_STATUS]:
            return_response['queryset']['msg'] = 'Inquiry status is wrong'
            return return_response

        queryset = queryset.filter(q_objects)
        present = datetime.datetime.now()
        if not no_filter:
            queryset = queryset.filter(
                Q(to_shipment_date__isnull=False, from_shipment_date__lte=(present.date() + timedelta(days=3)),
                  to_shipment_date__gte=present.date()) |
                Q(to_shipment_date__isnull=True, from_shipment_date__range=(present.date(), (present.date() + timedelta(days=3)))))

        if requirement_status == 'unverified':
            emp_functions = EmployeeRolesFunctionalityMapping.objects.filter(
                employee_role__employee_role__employee__username=self.request.user,
                td_functionality__functionality='customer_inquiries')
            if emp_functions and emp_functions.count() == 1 and emp_functions[0].employee_role.role == 'sales':
                queryset = queryset.filter(client__aaho_poc__username=self.request.user)

        if city_head_filter:
            employee = get_or_none(Employee, username=self.request.user)
            if requirement_status:
                queryset = unfiltered_queryset.filter(aaho_office_id__in=employee.office_multiple.values_list('id'), req_status=requirement_status)
            else:
                queryset = unfiltered_queryset.filter(aaho_office_id__in=employee.office_multiple.values_list('id'))

        if not queryset:
            return return_response

        return_response['queryset'] = queryset
        return_response['status'] = 'success'
        return return_response

    def get_user_filtered_requirements(self):
        user = self.request.user
        return_response = {"status": "failure", "queryset": {"msg": "No inquiry found"},
                           "status_code": status.HTTP_404_NOT_FOUND}

        if any(g.name == 'sales' for g in user.groups.all()):
            queryset = Requirement.history.filter(Q(changed_by=user) | Q(created_by=user)).exclude(
                deleted=True)
            if not queryset:
                return return_response
            req_ids = []
            for req in queryset:
                if req.id not in req_ids:
                    req_ids.append(req.id)
            queryset = Requirement.objects.filter(id__in=req_ids).exclude(deleted=True).exclude(
                req_status='unverified').order_by('-from_shipment_date')
            if not queryset:
                return return_response
            return_response['queryset'] = queryset
            return_response['status'] = 'success'
            return return_response
        if any(g.name == 'sme' for g in user.groups.all()):
            sme = Sme.objects.get(name=user)
            if not sme:
                return return_response
            queryset = Requirement.objects.filter(client=sme).exclude(deleted=True).order_by(
                '-from_shipment_date')
            return_response['queryset'] = queryset
            return_response['status'] = 'success'
            return return_response

        return_response['queryset']['msg'] = 'Does Not support this user'
        return_response['status_code'] = status.HTTP_400_BAD_REQUEST
        return return_response

    def get(self, request, *args, **kwargs):
        q_set = self.get_queryset()
        if q_set['status'] == 'failure':
            response = {"status": "failure", "msg": q_set['queryset']['msg'], "data": {},
                        "status_code": q_set['status_code']}
            return Response(response, status=q_set['status_code'])
        else:
            queryset = self.filter_queryset(q_set['queryset'])

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = {"status": "success", "msg": "inquiry data", "http_status": status.HTTP_200_OK,
                        "data": serializer.data, "status_code": status.HTTP_200_OK}
            return self.get_paginated_response(response)

        serializer = self.get_serializer(queryset, many=True)
        response = {"status": "success", "msg": "inquiry data", "data": {"requirements": serializer.data},
                    "status_code": status.HTTP_200_OK}
        return Response(response, status=status.HTTP_200_OK)


class RequirementUserListView(RequirementListView):
    user_filter = True


class RequirementViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving Requirements.

    """

    def create(self, request):
        requirement_serializer = RequirementSerializer(data=request.data)
        if requirement_serializer.is_valid():
            requirement_serializer.validated_data['user'] = self.request.user
            requirement_serializer.save()
            # response = {'status': 'success', 'msg': 'Requirement successfully submitted', 'data':
            #     {'id': requirement_serializer.data['id']}}
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "success",
                "msg": "Inquiry Created",
                "data": {'id': requirement_serializer.data['id']}
            }
            return Response(response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "failure",
            "msg": "Inquiry not Created",
            "data": requirement_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = Requirement.objects.all().exclude(deleted=True)
        req = get_object_or_404(queryset, pk=pk)
        serializer = RequirementSerializer(req)
        response = {'status': 'success', 'msg': 'inquiry data', 'data': serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, pk=None):

        if self.request.content_type != 'application/json':
            response = {"status": "failure", "msg": "Wrong Content Type. Must be application/json",
                        "data": {"requirements": {}}}
            return Response(response, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        try:
            req = Requirement.objects.get(id=pk, deleted=False)
        except Requirement.DoesNotExist:
            return Response({"status": "failure", "msg": "Inquiry Doesn't exists"},
                            status=status.HTTP_400_BAD_REQUEST)
        requirement_serializer = RequirementSerializer(instance=req, data=request.data)
        if requirement_serializer.is_valid():
            requirement_serializer.validated_data['user'] = self.request.user
            req_ser = requirement_serializer.save()
            if req_ser:
                # response = {'status': 'success', 'msg': 'Requirement successfully updated', 'data':
                #     {'id': requirement_serializer.data['id']}}
                response = {
                    "status_code": status.HTTP_202_ACCEPTED,
                    "status": "success",
                    "msg": "Inquiry Updated",
                    "data": {'id': requirement_serializer.data['id']}
                }
                return Response(response, status=status.HTTP_202_ACCEPTED)
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "failure",
                "msg": "Inquiry not Updated",
                "data": requirement_serializer.errors
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve_cancel_reasons(self, request):
        reasons = dict(REQ_CANCEL_REASONS)
        response = {
            "status_code": status.HTTP_200_OK,
            "status": "success",
            "msg": "Inquiry Cancellation reasons",
            "data": reasons
        }
        return Response(data=response, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        queryset = Requirement.objects.all()
        requirement = get_object_or_404(queryset, pk=pk)
        serializer = RequirementSerializer(requirement)
        requirement.deleted = True
        requirement.deleted_on = timezone.now()
        requirement.save()
        response = {'status': 'success', 'msg': 'Inquiry deleted', 'data': {'id': serializer.data['id']}}
        return Response(response, status=status.HTTP_200_OK)
