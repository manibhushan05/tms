from datetime import datetime, timedelta

from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics, filters
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from api.utils import to_int
from authentication.models import Profile
from employee.models import Employee
from restapi.filter.sme import SmeFilter, SmeTaskEmailFilter, RateTypeFilter, ContractRouteFilter, LocationFilter, \
    ConsignorConsigneeFilter, ContactDetailsFilter, CustomerContractFilter, PreferredVehicleFilter
from restapi.helper_api import generate_username, error_response, success_response, get_employee_roles
from restapi.models import BookingStatusesMapping, SmePaymentFollowupComments
from restapi.pagination import CustomeDatatablesPaginator
from restapi.parser.updatawebdata import parse_update_sme_data
from restapi.search import CustomSearch
from restapi.serializers.authentication import UserSerializer, ProfileSerializer
from restapi.serializers.sme import SmeSerializer, CustomerContractSerializer, SmeTaskEmailSerializer, \
    RateTypeSerializer, ContractRouteSerializer, ContactDetailsSerializer, LocationSerializer, \
    ConsignorConsigneeSerializer, PreferredVehicleSerializer, SmeEnquirySerializer, SmeSummarySerializer
from restapi.tasks import send_customer_welcome_email
from restapi.utils import get_or_none
from sme.models import Sme, CustomerContract, SmeTaskEmail, RateType, ContractRoute, ContactDetails, Location, \
    ConsignorConsignee, PreferredVehicle, SmeEnquiry, SmeSummary
from team.models import Invoice, PendingInwardPaymentEntry, ManualBooking


class SmeTaskEmailListView(generics.ListAPIView):
    queryset = SmeTaskEmail.objects.order_by('-id').exclude(deleted=True)
    serializer_class = SmeTaskEmailSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = SmeTaskEmailFilter
    search_fields = ('name', 'id')

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


class SmeCreatePageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/register-customer.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class SmeTaskEmailViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Sme Task Email
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username

        sme_task_email_serializer = SmeTaskEmailSerializer(data=request.data)
        if sme_task_email_serializer.is_valid():
            sme_task_email_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Sme Task Email Created",
                "data": sme_task_email_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Sme Task Email not Created",
            "data": sme_task_email_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        sme_task_email = get_or_none(SmeTaskEmail, id=pk)
        if not isinstance(sme_task_email, SmeTaskEmail):
            return Response({"error": "Sme Task Email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        sme_task_email_serializer = SmeTaskEmailSerializer(sme_task_email, data=request.data)

        if sme_task_email_serializer.is_valid():
            sme_task_email_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Sme Task Email Updated",
                "data": sme_task_email_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Sme Task Email not Updated",
            "data": sme_task_email_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        sme_task_email = get_or_none(SmeTaskEmail, id=pk)
        if not isinstance(sme_task_email, SmeTaskEmail):
            return Response({"error": "Sme Task Email does not exist"}, status=status.HTTP_404_NOT_FOUND)
        sme_task_email_serializer = SmeTaskEmailSerializer(
            instance=sme_task_email,
            data=request.data,
            partial=True
        )

        if sme_task_email_serializer.is_valid():
            sme_task_email_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Sme Task Email Updated",
                "data": sme_task_email_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Sme Task Email not Updated",
            "data": sme_task_email_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        sme_task_email = get_or_none(SmeTaskEmail, id=pk)
        if isinstance(sme_task_email, SmeTaskEmail):
            sme_task_email_serializer = SmeTaskEmailSerializer(sme_task_email)
            return Response(sme_task_email_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Sme Task Email does not exist"}, status=status.HTTP_404_NOT_FOUND)


class SmeListView(generics.ListAPIView):
    # queryset = Sme.objects.order_by('-id').exclude(deleted=True).exclude(name__profile=None)
    serializer_class = SmeSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = SmeFilter
    search_fields = (
        'id', 'name__profile__name', 'name__profile__phone', 'name__profile__contact_person_name',
        'aaho_office__branch_name', 'email_tasks__name', 'company_code', 'customer_address', 'credit_period',
        'aaho_poc__username__username', 'aaho_poc__username__profile__name', 'city__name', 'gstin', 'created_on',
        'material')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Customer List"}

        if self.request.GET.get('sme_data_category') == 'poc_invoices':
            serializer = self.get_serializer(queryset, many=True)
            data["data"] = self.add_invoice_details(serializer.data, 'invoice_raised')
            data["data"] = sorted(data["data"],
                                  key=lambda k: (int(k.get('invoice_details', 0).get('overdue_amount', 0)),
                                                 int(k.get('invoice_details', 0).get('pending_amount', 0))),
                                  reverse=True)
            page = self.paginate_queryset(data["data"])
            if page is not None:
                data["data"] = page
                return self.get_paginated_response(data)

            return Response(data)
        else:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data["data"] = serializer.data
                return self.get_paginated_response(data)
            serializer = self.get_serializer(queryset, many=True)
            data["data"] = serializer.data

            return Response(data)

    def get_queryset(self):
        user = self.request.user
        employee = get_or_none(Employee, username=user)
        if self.request.GET.get('sme_data_category') == 'poc_invoices' and isinstance(employee, Employee):
            invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['invoice_raised', 'party_invoice_sent',
                                                                  'invoice_confirmed']).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            complete_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='inward_followup_completed').exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pending_payments_bookings = [x for x in invoice_confirmed_bookings if x not in complete_bookings]
            emp_roles_response = get_employee_roles(user)
            if emp_roles_response['status'] == 'success' and ('management' in emp_roles_response['roles']
                                                              or 'tech' in emp_roles_response['roles']):
                smes = Sme.objects.order_by('-id').exclude(deleted=True).exclude(name__profile=None)
            elif emp_roles_response['status'] == 'success' and ('city_head' in emp_roles_response['roles']):
                smes = Sme.objects.filter(aaho_office_id__in=employee.office_multiple.values_list('id')).exclude(
                    deleted=True).exclude(name__profile=None).order_by('-id')
            else:
                smes = Sme.objects.filter(aaho_poc__username=self.request.user).order_by('-id').exclude(
                    deleted=True).exclude(name__profile=None)

            sme_ids = list(ManualBooking.objects.filter(id__in=pending_payments_bookings,
                                                        customer_to_be_billed_to__in=smes,
                                                        inward_payment_status__in=['no_payment', 'partial_received'],
                                                        invoice_status__in=['invoice_raised', 'invoice_sent',
                                                                            'invoice_confirmed']).
                           values_list('customer_to_be_billed_to_id', flat=True))
            # sme_ids = set(sme_ids)
            return smes.filter(id__in=sme_ids)
        elif self.request.GET.get('sme_data_category') == 'web_customers_records' and isinstance(employee, Employee):
            emp_roles_response = get_employee_roles(user)
            if emp_roles_response['status'] == 'failure':
                return Sme.objects.none()
            elif ('management' in emp_roles_response['roles'] or 'tech' in emp_roles_response['roles']):
                return Sme.objects.exclude(Q(deleted=True) | Q(name__profile=None))
            else:
                return Sme.objects.filter(aaho_office__in=employee.office_multiple.all())
        return Sme.objects.exclude(deleted=True).exclude(name__profile=None)

    def add_invoice_details(self, data, status):
        pending_amount = 0
        overdue_invoices = 0
        overdue_amount = 0
        pending_invoices = 0
        # invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
        #     booking_status_chain__booking_status__status__in=['invoice_raised', 'party_invoice_sent',
        #                                                       'invoice_confirmed']).exclude(deleted=True). \
        #     values_list('manual_booking_id', flat=True)
        # complete_bookings = BookingStatusesMapping.objects.filter(
        #     booking_status_chain__booking_status__status__iexact='inward_followup_completed').exclude(deleted=True). \
        #     values_list('manual_booking_id', flat=True)
        # pending_payments_bookings = [x for x in invoice_confirmed_bookings if x not in complete_bookings]
        for sme in data:
            # invs = Invoice.objects.filter(bookings__in=pending_payments_bookings, customer_fk__id=sme['id'],
            #                               payment_received=False).distinct()
            try:
                sme_summary = SmeSummary.objects.get(sme__id=sme['id'])
            except SmeSummary.DoesNotExist:
                sme_summary = None
            if sme_summary:
                billed_sme_summary = sme_summary.billed_accounting_summary
            else:
                billed_sme_summary = None
            # for inv in invs:
            # pending_amount += to_int(inv.get_customer_balance)
            # if inv.is_overdue:
            #     overdue_invoices += 1
            # overdue_amount += to_int(inv.get_overdue_balance)
            latest_sme_comment = SmePaymentFollowupComments.objects.filter(sme__id=sme['id'],
                                                                           due_date__isnull=False).exclude(
                deleted=True).last()
            if latest_sme_comment:
                sme_due_date = str(latest_sme_comment.due_date)
            else:
                sme_due_date = None

            sme['invoice_details'] = {'pending_invoices': str(billed_sme_summary[
                                                                  'pending_invoices'] if 'pending_invoices' in billed_sme_summary else 0) if billed_sme_summary else pending_invoices,
                                      'pending_amount': str(sum(billed_sme_summary[
                                                                    'pending_payments'].values()) if 'pending_payments' in billed_sme_summary else 0) if billed_sme_summary else pending_amount,
                                      'overdue_invoices': str(billed_sme_summary[
                                                                  'overdue_invoices'] if 'overdue_invoices' in billed_sme_summary else 0) if billed_sme_summary else overdue_invoices,
                                      'overdue_amount': str(billed_sme_summary[
                                                                'overdue_amount'] if 'overdue_amount' in billed_sme_summary else 0) if billed_sme_summary else overdue_amount,
                                      'pending_inward_adjustment': str(to_int(sum(
                                          [amount + tds for amount, tds in
                                           PendingInwardPaymentEntry.objects.filter(adjusted_flag=False,
                                                                                    customer_id=sme['id']).values_list(
                                               'amount', 'tds')]))),
                                      'sme_due_date': sme_due_date}
            # overdue_invoices = 0
            # pending_amount = 0
            # overdue_amount = 0
        return data


class SmeSummaryListView(generics.ListAPIView):
    serializer_class = SmeSummarySerializer
    pagination_class = CustomeDatatablesPaginator
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    # filter_class = OwnerVehicleFilter
    search_fields = ('id', 'sme__company_code', 'sme__name__profile__name')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Success", "status_code": status.HTTP_200_OK, "msg": "Accounting Summary List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)

    def get_queryset(self):
        summary_type = self.request.GET.get('summary_type', None)
        queryset = SmeSummary.objects.exclude(deleted=True)
        emp_roles_response = get_employee_roles(self.request.user)
        if summary_type == 'billed_customer':
            queryset = queryset.exclude(billed_accounting_summary=None).annotate(
                total_amount=RawSQL("(billed_accounting_summary->>%s)::numeric", ("total_amount",))).order_by(
                '-total_amount')
            if emp_roles_response['status'] == 'success' and ('city_head' in emp_roles_response['roles']):
                employee = get_or_none(Employee, username=self.request.user)
                if isinstance(employee, Employee):
                    queryset = queryset.filter(sme__aaho_office__in=employee.office_multiple.all())
        elif summary_type == 'placed_order_customer':
            queryset = queryset.exclude(placed_order_accounting_summary=None).annotate(
                total_amount=RawSQL("(placed_order_accounting_summary->>%s)::numeric", ("total_amount",))).order_by(
                '-total_amount')
            if emp_roles_response['status'] == 'success' and ('city_head' in emp_roles_response['roles']):
                employee = get_or_none(Employee, username=self.request.user)
                if isinstance(employee, Employee):
                    queryset = queryset.filter(sme__aaho_office__in=employee.office_multiple.all())
        else:
            queryset = SmeSummary.objects.none()
        return queryset


class SmeViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Sme
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        if 'company_code' in request.data and request.data.get('company_code', None):
            if Sme.objects.filter(company_code__iexact=request.data['company_code']).exists():
                return error_response(status=status.HTTP_400_BAD_REQUEST, msg='customer code already exists', data={})
        try:
            profile_data = {
                "name": request.data["name"],
                "phone": request.data.get("phone"),
                "email": request.data.get("email", None),
                "alternate_phone": request.data.get("alternate_phone", None),
                "contact_person_name": request.data.get("contact_person_name", None),
                "contact_person_phone": request.data.get("phone"),
                "comment": request.data.get("remarks", None),
                "address": request.data.get("customer_address", None)
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
                request.data["name"] = user.username
                sme_serializer = SmeSerializer(data=request.data)
                if sme_serializer.is_valid():
                    sme = sme_serializer.save()
                    if settings.ENABLE_CELERY:
                        send_customer_welcome_email.delay(sme.id)
                    else:
                        send_customer_welcome_email(sme.id)
                    return success_response(status=status.HTTP_201_CREATED, msg='Customer is created',
                                            data=sme_serializer.data)
                user.delete()
                response = {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "status": "failure",
                    "msg": "Sme not Created",
                    "data": sme_serializer.errors
                }
                return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
            user.delete()
            return Response(profile.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        sme = get_or_none(Sme, id=pk)
        if not isinstance(sme, Sme):
            return Response({"error": "Sme does not exist"}, status=status.HTTP_404_NOT_FOUND)
        sme_serializer = SmeSerializer(sme, data=request.data)

        if sme_serializer.is_valid():
            sme_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "success",
                "msg": "Sme Updated",
                "data": sme_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "failure",
            "msg": "Sme not Updated",
            "data": sme_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        sme = get_or_none(Sme, id=pk)
        if not isinstance(sme, Sme):
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Sme Doesnot Exists', data={})

        profile = get_or_none(Profile, user=sme.name)
        parsed_data = parse_update_sme_data(request.data, id=pk)
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
        sme_serializer = SmeSerializer(
            instance=sme,
            data=parsed_data,
            partial=True
        )
        if sme_serializer.is_valid():
            sme_serializer.save()
            return success_response(status=status.HTTP_202_ACCEPTED, msg='SME updated', data=sme_serializer.data)
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Something went wrong',
                              data=sme_serializer.errors)

    def retrieve_app(self, request, pk=None):
        sme = get_or_none(Sme, id=pk)
        if isinstance(sme, Sme):
            sme_serializer = SmeSerializer(sme)
            return success_response(data=sme_serializer.data, status=status.HTTP_200_OK, msg='Sme Found')
        return error_response(data={}, status=status.HTTP_404_NOT_FOUND, msg='Sme not found')

    def retrieve(self, request, pk=None):
        sme = get_or_none(Sme, id=pk)
        if isinstance(sme, Sme):
            sme_serializer = SmeSerializer(sme)
            return Response(template_name='team/registrations/customer-update.html', data=sme_serializer.data,
                            status=status.HTTP_200_OK)
        return Response({"error": "Sme does not exist"}, status=status.HTTP_404_NOT_FOUND)


class RateTypeListView(generics.ListAPIView):
    queryset = RateType.objects.order_by('-id').exclude(deleted=True)
    serializer_class = RateTypeSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = RateTypeFilter
    search_fields = ('name', 'id')

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


class RateTypeViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on RateType
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        rate_type_serializer = RateTypeSerializer(data=request.data)
        if rate_type_serializer.is_valid():
            rate_type_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "RateType Created",
                "data": rate_type_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "RateType not Created",
            "data": rate_type_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        rate_type = get_or_none(RateType, id=pk)
        if not isinstance(rate_type, RateType):
            return Response({"error": "RateType does not exist"}, status=status.HTTP_404_NOT_FOUND)
        rate_type_serializer = RateTypeSerializer(rate_type, data=request.data)
        if rate_type_serializer.is_valid():
            rate_type_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "RateType Updated",
                "data": rate_type_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "RateType not Updated",
            "data": rate_type_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        rate_type = get_or_none(RateType, id=pk)
        if not isinstance(rate_type, RateType):
            return Response({"error": "RateType does not exist"}, status=status.HTTP_404_NOT_FOUND)
        rate_type_serializer = RateTypeSerializer(
            instance=rate_type,
            data=request.data,
            partial=True
        )

        if rate_type_serializer.is_valid():
            rate_type_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "RateType Updated",
                "data": rate_type_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "RateType not Updated",
            "data": rate_type_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        rate_type = get_or_none(RateType, id=pk)
        if isinstance(rate_type, RateType):
            rate_type_serializer = RateTypeSerializer(rate_type)
            return Response(rate_type_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "RateType does not exist"}, status=status.HTTP_404_NOT_FOUND)


class CustomerContractListView(generics.ListAPIView):
    queryset = CustomerContract.objects.order_by('-id').exclude(deleted=True)
    serializer_class = CustomerContractSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = CustomerContractFilter
    search_fields = ('customer__name__username', 'id', 'customer__company_code', 'billing_frequency')

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


class CustomerContractViewSet(viewsets.ViewSet):
    """
            API for CRUP operation on Customer Contract
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        customer_contract_serializer = CustomerContractSerializer(data=request.data)
        if customer_contract_serializer.is_valid():
            customer_contract_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Customer Contract Created",
                "data": customer_contract_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Customer Contract not Created",
            "data": customer_contract_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        customer_contract = get_or_none(CustomerContract, id=pk)
        if not isinstance(customer_contract, CustomerContract):
            return Response({"error": "Customer Contract does not exist"}, status=status.HTTP_404_NOT_FOUND)
        customer_contract_serializer = CustomerContractSerializer(customer_contract, data=request.data)

        if customer_contract_serializer.is_valid():
            customer_contract_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Customer Contract Updated",
                "data": customer_contract_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Customer Contract not Updated",
            "data": customer_contract_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        customer_contract = get_or_none(CustomerContract, id=pk)
        if not isinstance(customer_contract, CustomerContract):
            return Response({"error": "Customer Contract does not exist"}, status=status.HTTP_404_NOT_FOUND)

        customer_contract_serializer = CustomerContractSerializer(
            instance=customer_contract,
            data=request.data,
            partial=True
        )

        if customer_contract_serializer.is_valid():
            customer_contract_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Customer Contract Updated",
                "data": customer_contract_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Customer Contract not Updated",
            "data": customer_contract_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        customer_contract = get_or_none(CustomerContract, id=pk)
        if isinstance(customer_contract, CustomerContract):
            customer_contract_serializer = CustomerContractSerializer(customer_contract)
            return Response(customer_contract_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Customer Contract does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def contract_customer_data(self, request):
        sme_id = request.GET.get('sme_id')
        customer = get_or_none(Sme, id=sme_id)
        if isinstance(customer, Sme):
            today = datetime.now().date()
            if customer.customercontract_set.filter(Q(start_date__lte=today) & Q(end_date__gte=today)).exclude(
                    deleted=True).exists():
                data = {'id': customer.id, 'name': customer.get_name(), 'code': customer.company_code,
                        'is_contract': True}
            else:
                data = {'id': customer.id, 'name': customer.get_name(), 'code': customer.company_code,
                        'is_contract': False}
        else:
            data = {'id': -1, 'name': '', 'code': '', 'is_contract': False}
        return Response(data=data, status=status.HTTP_200_OK)


class ContractRouteListView(generics.ListAPIView):
    queryset = ContractRoute.objects.order_by('-id').exclude(deleted=True)
    serializer_class = ContractRouteSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = ContractRouteFilter
    search_fields = ('source__name', 'id', 'destination__name', 'rate_type__name')

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


class ContractRouteViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Contract Route
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username

        contract_route_serializer = ContractRouteSerializer(data=request.data)
        if contract_route_serializer.is_valid():
            contract_route_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Contract Route Created",
                "data": contract_route_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Contract Route not Created",
            "data": contract_route_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        contract_route = get_or_none(ContractRoute, id=pk)
        if not isinstance(contract_route, ContractRoute):
            return Response({"error": "Contract Route does not exist"}, status=status.HTTP_404_NOT_FOUND)
        contract_route_serializer = ContractRouteSerializer(contract_route, data=request.data)

        if contract_route_serializer.is_valid():
            contract_route_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Contract Route Updated",
                "data": contract_route_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Contract Route not Updated",
            "data": contract_route_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        contract_route = get_or_none(ContractRoute, id=pk)
        if not isinstance(contract_route, ContractRoute):
            return Response({"error": "Contract Route does not exist"}, status=status.HTTP_404_NOT_FOUND)
        contract_route_serializer = ContractRouteSerializer(
            instance=contract_route,
            data=request.data,
            partial=True
        )

        if contract_route_serializer.is_valid():
            contract_route_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Contract Route Updated",
                "data": contract_route_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Contract Route not Updated",
            "data": contract_route_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        contract_route = get_or_none(ContractRoute, id=pk)
        if isinstance(contract_route, ContractRoute):
            contract_route_serializer = ContractRouteSerializer(contract_route)
            return Response(contract_route_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Contract Route does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ContactDetailsListView(generics.ListAPIView):
    queryset = ContactDetails.objects.order_by('-id').exclude(deleted=True)
    serializer_class = ContactDetailsSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = ContactDetailsFilter
    search_fields = ('sme__name__username', 'id', 'type', 'name', 'phone', 'email', 'designation', 'status')

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


class ContactDetailsViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Contact Details
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username

        contact_details_serializer = ContactDetailsSerializer(data=request.data)
        if contact_details_serializer.is_valid():
            contact_details_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Contact Details Created",
                "data": contact_details_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Contact Details not Created",
            "data": contact_details_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        contact_details = get_or_none(ContactDetails, id=pk)
        if not isinstance(contact_details, ContactDetails):
            return Response({"error": "Contact Details does not exist"}, status=status.HTTP_404_NOT_FOUND)
        contact_details_serializer = ContactDetailsSerializer(contact_details, data=request.data)

        if contact_details_serializer.is_valid():
            contact_details_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Contact Details Updated",
                "data": contact_details_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Contact Details not Updated",
            "data": contact_details_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        contact_details = get_or_none(ContactDetails, id=pk)
        if not isinstance(contact_details, ContactDetails):
            return Response({"error": "Contact Details does not exist"}, status=status.HTTP_404_NOT_FOUND)
        contact_details_serializer = ContactDetailsSerializer(
            instance=contact_details,
            data=request.data,
            partial=True
        )

        if contact_details_serializer.is_valid():
            contact_details_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Contact Details Updated",
                "data": contact_details_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Contact Details not Updated",
            "data": contact_details_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        contact_details = get_or_none(ContactDetails, id=pk)
        if isinstance(contact_details, ContactDetails):
            contact_details_serializer = ContactDetailsSerializer(contact_details)
            return Response(contact_details_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Contact Details does not exist"}, status=status.HTTP_404_NOT_FOUND)


class LocationListView(generics.ListAPIView):
    queryset = Location.objects.order_by('-id').exclude(deleted=True)
    serializer_class = LocationSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = LocationFilter
    search_fields = (
        'sme__name__username', 'sme__company_code', 'id', 'type', 'contact__name', 'address', 'city__name', 'material',
        'status')

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


class LocationViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Location
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username

        location_serializer = LocationSerializer(data=request.data)
        if location_serializer.is_valid():
            location_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Location Created",
                "data": location_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Location not Created",
            "data": location_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        location = get_or_none(Location, id=pk)
        if not isinstance(location, Location):
            return Response({"error": "Location does not exist"}, status=status.HTTP_404_NOT_FOUND)
        location_serializer = LocationSerializer(location, data=request.data)

        if location_serializer.is_valid():
            location_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Location Updated",
                "data": location_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Location not Updated",
            "data": location_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        location = get_or_none(Location, id=pk)
        if not isinstance(location, Location):
            return Response({"error": "Location does not exist"}, status=status.HTTP_404_NOT_FOUND)
        location_serializer = LocationSerializer(
            instance=location,
            data=request.data,
            partial=True
        )

        if location_serializer.is_valid():
            location_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Location Updated",
                "data": location_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Location not Updated",
            "data": location_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        location = get_or_none(Location, id=pk)
        if isinstance(location, Location):
            location_serializer = LocationSerializer(location)
            return Response(location_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Location does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ConsignorConsigneeListView(generics.ListAPIView):
    queryset = ConsignorConsignee.objects.order_by('-id').exclude(deleted=True)
    serializer_class = ConsignorConsigneeSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = ConsignorConsigneeFilter
    search_fields = (
        'sme__name__username', 'sme__company_code', 'id', 'type', 'pin', 'address', 'city__name', 'phone', 'tax_id',
        'status')

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


class ConsignorConsigneeViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on ConsignorConsignee
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username

        consignor_consignee_serializer = ConsignorConsigneeSerializer(data=request.data)
        if consignor_consignee_serializer.is_valid():
            consignor_consignee_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "ConsignorConsignee Created",
                "data": consignor_consignee_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "ConsignorConsignee not Created",
            "data": consignor_consignee_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        consignor_consignee = get_or_none(ConsignorConsignee, id=pk)
        if not isinstance(consignor_consignee, ConsignorConsignee):
            return Response({"error": "ConsignorConsignee does not exist"}, status=status.HTTP_404_NOT_FOUND)
        consignor_consignee_serializer = ConsignorConsigneeSerializer(consignor_consignee, data=request.data)

        if consignor_consignee_serializer.is_valid():
            consignor_consignee_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "ConsignorConsignee Updated",
                "data": consignor_consignee_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "ConsignorConsignee not Updated",
            "data": consignor_consignee_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        consignor_consignee = get_or_none(ConsignorConsignee, id=pk)
        if not isinstance(consignor_consignee, ConsignorConsignee):
            return Response({"error": "ConsignorConsignee does not exist"}, status=status.HTTP_404_NOT_FOUND)
        consignor_consignee_serializer = ConsignorConsigneeSerializer(
            instance=consignor_consignee,
            data=request.data,
            partial=True
        )

        if consignor_consignee_serializer.is_valid():
            consignor_consignee_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "ConsignorConsignee Updated",
                "data": consignor_consignee_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "ConsignorConsignee not Updated",
            "data": consignor_consignee_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        consignor_consignee = get_or_none(ConsignorConsignee, id=pk)
        if isinstance(consignor_consignee, ConsignorConsignee):
            consignor_consignee_serializer = ConsignorConsigneeSerializer(consignor_consignee)
            return Response(consignor_consignee_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "ConsignorConsignee does not exist"}, status=status.HTTP_404_NOT_FOUND)


class PreferredVehicleListView(generics.ListAPIView):
    queryset = PreferredVehicle.objects.order_by('-id').exclude(deleted=True)
    serializer_class = PreferredVehicleSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = PreferredVehicleFilter
    search_fields = (
        'sme__name__username', 'sme__company_code', 'id', 'category__vehicle_type', 'category__truck_body_type',
        'created_by__username'
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


class PreferredVehicleViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Preferred Vehicle
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username

        preferred_vehicle_serializer = PreferredVehicleSerializer(data=request.data)
        if preferred_vehicle_serializer.is_valid():
            preferred_vehicle_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Preferred Vehicle Created",
                "data": preferred_vehicle_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Preferred Vehicle not Created",
            "data": preferred_vehicle_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        preferred_vehicle = get_or_none(PreferredVehicle, id=pk)
        if not isinstance(preferred_vehicle, PreferredVehicle):
            return Response({"error": "Preferred Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        preferred_vehicle_serializer = PreferredVehicleSerializer(preferred_vehicle, data=request.data)

        if preferred_vehicle_serializer.is_valid():
            preferred_vehicle_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Preferred Vehicle Updated",
                "data": preferred_vehicle_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Preferred Vehicle not Updated",
            "data": preferred_vehicle_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        preferred_vehicle = get_or_none(PreferredVehicle, id=pk)
        if not isinstance(preferred_vehicle, PreferredVehicle):
            return Response({"error": "Preferred Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)
        preferred_vehicle_serializer = PreferredVehicleSerializer(
            instance=preferred_vehicle,
            data=request.data,
            partial=True
        )

        if preferred_vehicle_serializer.is_valid():
            preferred_vehicle_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Preferred Vehicle Updated",
                "data": preferred_vehicle_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Preferred Vehicle not Updated",
            "data": preferred_vehicle_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        preferred_vehicle = get_or_none(PreferredVehicle, id=pk)
        if isinstance(preferred_vehicle, PreferredVehicle):
            preferred_vehicle_serializer = PreferredVehicleSerializer(preferred_vehicle)
            return Response(preferred_vehicle_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Preferred Vehicle does not exist"}, status=status.HTTP_404_NOT_FOUND)


class SmeEnquiryViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on SmeEnquiry
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        sme = get_or_none(Sme, name=request.user)
        if not isinstance(sme, Sme):
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Customer Does not exists", data={})
        request.data['sme'] = sme.id
        sme_enquiry_serializer = SmeEnquirySerializer(data=request.data)
        if sme_enquiry_serializer.is_valid():
            sme_enquiry_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "SmeEnquiry Created",
                "data": sme_enquiry_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "SmeEnquiry not Created",
            "data": sme_enquiry_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        sme_enquiry = get_or_none(SmeEnquiry, id=pk)
        if not isinstance(sme_enquiry, SmeEnquiry):
            return Response({"error": "SmeEnquiry does not exist"}, status=status.HTTP_404_NOT_FOUND)
        sme_enquiry_serializer = SmeEnquirySerializer(sme_enquiry, data=request.data)

        if sme_enquiry_serializer.is_valid():
            sme_enquiry_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "SmeEnquiry Updated",
                "data": sme_enquiry_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "SmeEnquiry not Updated",
            "data": sme_enquiry_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        sme_enquiry = get_or_none(SmeEnquiry, id=pk)
        if not isinstance(sme_enquiry, SmeEnquiry):
            return Response({"error": "SmeEnquiry does not exist"}, status=status.HTTP_404_NOT_FOUND)
        sme_enquiry_serializer = SmeEnquirySerializer(
            instance=sme_enquiry,
            data=request.data,
            partial=True
        )

        if sme_enquiry_serializer.is_valid():
            sme_enquiry_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "SmeEnquiry Updated",
                "data": sme_enquiry_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "SmeEnquiry not Updated",
            "data": sme_enquiry_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        sme_enquiry = get_or_none(SmeEnquiry, id=pk)
        if isinstance(sme_enquiry, SmeEnquiry):
            sme_enquiry_serializer = SmeEnquirySerializer(sme_enquiry)
            return Response(sme_enquiry_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "SmeEnquiry does not exist"}, status=status.HTTP_404_NOT_FOUND)
