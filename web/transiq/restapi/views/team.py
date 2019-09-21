import os
import io

import zipfile
from datetime import datetime, timedelta

import pandas as pd
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics, filters
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api import s3util
from api.models import S3Upload, google_reverse_geocode
from api.s3util import save_to_s3_bulk_inward_payments, save_to_s3_bulk_reconcile_outward_payments
from api.utils import int_or_none, to_int
from broker.models import Broker
from driver.models import GPSDevice
from employee.models import Employee
from fileupload.models import PODFile
from owner.models import FuelCard
from supplier.models import Vehicle, Supplier
from report import invoice
from report.lr_html import generate_lorry_receipt
from report.outward_payments_receipt import generate_receipt
from restapi.filter.team import OutwardPaymentFilters, InwardPaymentFilters, InvoiceFilters, \
    OutwardPaymentBillFilters, CreditNoteSupplierFilters, DebitNoteSupplierFilters, \
    CreditNoteCustomerFilters, DebitNoteCustomerFilters, CreditNoteCustomerDirectAdvanceFilters, \
    DebitNoteSupplierDirectAdvanceFilters, InvoiceSummaryFilters, LrNumberFilter, ManualBookingFilters, \
    DataTablesFilters
from restapi.helper_api import django_date_format, manual_booking_id_dest_aaho_list, get_employee_roles, \
    add_invoice_booking_status_comment, check_booking_status, get_booking_status_mapping_object, \
    get_formatted_time_date, create_new_booking_status, update_booking_status, get_gps_device_location_from_dynamo
from restapi.helper_api import manual_booking_id_list, is_fms_user, is_sme_user, success_response, error_response
from restapi.models import BookingStatusesMappingComments, BookingStatusesMapping, BookingStatusesMappingLocation, \
    EmployeeRolesMapping, BookingStatuses, BookingStatusChain
from restapi.pagination import CustomeDatatablesPaginator
from restapi.parser.payments import parse_outward_payment_data, parse_pending_inward_adjustment_data
from restapi.search import CustomSearch
from restapi.serializers.file_upload import PODFileSerializer
from restapi.serializers.team import InvoiceSerializer, InvoiceSummarySerializer, ManualBookingSerializer, \
    LrNumberSerializer, RejectedPODSerializer, BookingConsignorConsigneeSerializer, BookingInsuranceSerializer, \
    InWardPaymentSerializer, OutWardPaymentSerializer, OutWardPaymentBillSerializer, ToPayInvoiceSerializer, \
    PendingInwardPaymentEntrySerializer, CreditDebitNoteReasonSerializer, CreditNoteCustomerSerializer, \
    DebitNoteCustomerSerializer, CreditNoteSupplierSerializer, DebitNoteSupplierSerializer, \
    CreditNoteCustomerDirectAdvanceSerializer, DebitNoteSupplierDirectAdvanceSerializer, ManualBookingMISSerializer, \
    FMSManualBookingSerializer, TinyManualBookingSerializer, ConnectManualBookingSerializer, DataTablesFilterSerializer
from restapi.serializers.utils import AahoOfficeSerializer
from restapi.service.booking import booking_create_data, get_lr_numbers, update_booking_field
from restapi.service.invoices import parse_single_invoice_data
from restapi.service.payment_files import get_today_payments, send_sales_report, payment_summary_today
from restapi.service.payments import payment_mode_date, adjust_outward_payment_adjustment_mode
from restapi.tasks import generate_lorry_receipt_task
from api.utils import get_or_none
from sme.models import Sme
from team import tasks
from team.models import InvoiceSummary, ManualBooking, LrNumber, RejectedPOD, BookingConsignorConsignee, \
    BookingInsurance, InWardPayment, OutWardPayment, OutWardPaymentBill, Invoice, ToPayInvoice, \
    PendingInwardPaymentEntry, CreditDebitNoteReason, CreditNoteCustomer, DebitNoteCustomer, CreditNoteSupplier, \
    DebitNoteSupplier, CreditNoteCustomerDirectAdvance, DebitNoteSupplierDirectAdvance, ManualBookingSummary, \
    PendingInwardPaymentCreditDebitNoteCustomer, DataTablesFilter
from team.payments.accounting import placed_order_accounting_summary, billed_customer_accounting_summary
from team.views_booking import check_gps_device_attach
from utils.models import AahoOffice, Bank, State


class DashboardPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/dashboard.html'

    def post(self, request):
        return Response(status=status.HTTP_200_OK)

    def perform_authentication(self, request):
        try:
            token = Token.objects.get(key=request.stream.POST['token'])
            request.user = token.user
        except (Token.DoesNotExist, AttributeError) as e:
            raise PermissionDenied


class MobileDashboardPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'mobile/dashboard.html'

    def post(self, request):
        return Response(status=status.HTTP_200_OK)

    def perform_authentication(self, request):
        try:
            token = Token.objects.get(key=request.stream.POST['token'])
            request.user = token.user
        except (Token.DoesNotExist, AttributeError) as e:
            raise PermissionDenied


class DownloadPaymentFiles(viewsets.ViewSet):
    def download_today_payment_file(self, request):
        dl_url = get_today_payments()
        if dl_url:
            return success_response(status=status.HTTP_200_OK, msg=dl_url, data={})
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg="No file created", data={})

    def send_today_payment_file(self, request):
        dl_url = payment_summary_today()
        if dl_url:
            return success_response(status=status.HTTP_200_OK, msg=dl_url, data={})
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg="No file created", data={})

    def send_previous_day_sales_report(self, request):
        dl_url = send_sales_report()
        if dl_url:
            return success_response(status=status.HTTP_200_OK, msg=dl_url, data={})
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg="No file created", data={})


class InvoiceSummaryListView(generics.ListAPIView):
    serializer_class = InvoiceSummarySerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    queryset = InvoiceSummary.objects.exclude(deleted=True).order_by("-id")
    filter_class = InvoiceSummaryFilters
    ordering_fields = ('id', 'date')
    search_fields = (
        'id', 'booking__booking_id', 'booking__lr_numbers__lr_number', 'ref_number', 'datetime', 'created_by__username',
        'created_on')

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


class InvoiceSummaryViewSet(viewsets.ViewSet):
    """
        API to create Invoice Summary
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        invoice_summary_serializer = InvoiceSummarySerializer(data=request.data)
        if invoice_summary_serializer.is_valid():
            invoice_summary_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Invoice summary Created",
                "data": invoice_summary_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Invoice summary not Created",
            "data": invoice_summary_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        invoice_summary = get_or_none(InvoiceSummary, id=pk)
        if not isinstance(invoice_summary, InvoiceSummary):
            return Response({"error": "Invoice summary does not exist"}, status=status.HTTP_404_NOT_FOUND)
        invoice_summary_serializer = InvoiceSummarySerializer(invoice_summary, data=request.data)

        if invoice_summary_serializer.is_valid():
            invoice_summary_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Invoice summary Updated",
                "data": invoice_summary_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Invoice summary not Updated",
            "data": invoice_summary_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        invoice_summary = get_or_none(InvoiceSummary, id=pk)
        if not isinstance(invoice_summary, InvoiceSummary):
            return Response({"error": "Invoice summary does not exist"}, status=status.HTTP_404_NOT_FOUND)
        invoice_summary_serializer = InvoiceSummarySerializer(
            instance=invoice_summary,
            data=request.data,
            partial=True
        )

        if invoice_summary_serializer.is_valid():
            invoice_summary_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Invoice summary Updated",
                "data": invoice_summary_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Invoice summary not Updated",
            "data": invoice_summary_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        invoice_summary = get_or_none(InvoiceSummary, id=pk)
        if isinstance(invoice_summary, InvoiceSummary):
            invoice_summary_serializer = InvoiceSummarySerializer(invoice_summary)
            return Response(invoice_summary_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Invoice summary does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ManualBookingListView(generics.ListAPIView):
    serializer_class = ManualBookingSerializer
    pagination_class = CustomeDatatablesPaginator
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('id',)
    filter_class = ManualBookingFilters

    search_fields = (
        'id', 'shipment_date', 'booking_id', 'lr_numbers__lr_number', 'booking_status_color__keyword', 'company_code',
        'consignor_name', 'billing_type', 'company__name__profile__name',
        'customer_to_be_billed_to__name__profile__name',
        'gst_liability', 'shipment_date', 'from_city', 'to_city', 'supplier_vehicle__vehicle_number',
        'type_of_vehicle', 'charged_weight', 'supplier_charged_weight', 'party_rate', 'supplier_rate',
        'total_in_ward_amount', 'total_out_ward_amount', 'total_amount_to_company', 'advance_amount_from_company',
        'refund_amount', 'total_amount_to_owner', 'loading_charge', 'unloading_charge', 'detention_charge',
        'additional_charges_for_company', 'remarks_about_additional_charges', 'additional_charges_for_owner',
        'note_for_additional_owner_charges', 'remarks_about_deduction', 'invoice_number', 'pod_status',
        'outward_payment_status', 'inward_payment_status', 'invoice_status', 'comments', 'tds_certificate_status',
        'booking_status', 'is_print_payment_mode_instruction', 'created_by__username', 'supplier__name__profile__name',
        'supplier__name__profile__phone')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        APP_CATEGORY = self.request.META.get('HTTP_APP_CATEGORY')
        if APP_CATEGORY == 'fms':
            vehicle_id = self.request.GET.get('vehicle_id', None)
            queryset = self.get_queryset()
            if vehicle_id and isinstance(get_or_none(Vehicle, id=vehicle_id), Vehicle):
                try:
                    manual_booking_summary = ManualBookingSummary.objects.get(supplier_vehicle_id=vehicle_id)
                    summary = manual_booking_summary.summary
                except ManualBookingSummary.DoesNotExist:
                    summary = {}
            else:
                try:
                    manual_booking_summary = ManualBookingSummary.objects.get(user=request.user)
                    summary = manual_booking_summary.summary
                except ManualBookingSummary.DoesNotExist:
                    summary = {}
        else:
            summary = {}

        data = {"status": "Success", "status_code": status.HTTP_200_OK, "msg": "Bookings List", 'summary': summary}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            if self.request.GET.get('booking_data_category') == 'incomplete_lr':
                data["data"] = self.add_booking_status_comment(data["data"], 'incomplete_lr')
            if self.request.GET.get('booking_data_category') == 'in_transit':
                data["data"] = self.add_booking_status_location(data["data"])
            if self.request.GET.get('booking_data_category') == 'delivered':
                data["data"] = self.add_booking_status_comment(data["data"], 'unloaded')
            if self.request.GET.get('booking_data_category') == 'invoice_confirmation':
                data["data"] = self.add_booking_status_comment(data["data"], 'party_invoice_sent')
            if self.request.GET.get('booking_data_category') == 'raise_invoice':
                data["data"] = self.add_booking_status_comment(data["data"], 'invoice_raised')
                try:
                    bs = BookingStatuses.objects.get(status='pod_verified')
                    tl = bs.time_limit
                except BookingStatuses.DoesNotExist:
                    tl = 0
                b_ids = list(queryset.values_list('id', flat=True))
                overdue_bookings = BookingStatusesMapping.objects.filter(manual_booking__id__in=b_ids,
                                                                         booking_status_chain__booking_status__status__iexact='pod_verified',
                                                                         created_on__lte=(datetime.now() - timedelta(
                                                                             minutes=tl)).date())
                data['summary'] = {'overdue': overdue_bookings.count(),
                                   'pending': (queryset.count() - overdue_bookings.count()),
                                   'overdue_bookings_list': overdue_bookings.values_list('manual_booking_id',
                                                                                         flat=True)}
            return self.get_paginated_response(data)
        serializer = self.get_serializer(queryset, many=True)
        if self.request.GET.get('booking_data_category') == 'incomplete_lr':
            data["data"] = self.add_booking_status_comment(data["data"], 'incomplete_lr')
        if self.request.GET.get('booking_data_category') == 'in_transit':
            data["data"] = self.add_booking_status_location(data["data"])
        if self.request.GET.get('booking_data_category') == 'delivered':
            data["data"] = self.add_booking_status_comment(data["data"], 'unloaded')
        if self.request.GET.get('booking_data_category') == 'invoice_confirmation':
            data["data"] = self.add_booking_status_comment(data["data"], 'party_invoice_sent')
        if self.request.GET.get('booking_data_category') == 'raise_invoice':
            data["data"] = self.add_booking_status_comment(data["data"], 'invoice_raised')
            try:
                bs = BookingStatuses.objects.get(status='pod_verified')
                tl = bs.time_limit
            except BookingStatuses.DoesNotExist:
                tl = 0
            b_ids = list(queryset.values_list('id', flat=True))
            overdue_bookings = BookingStatusesMapping.objects.filter(manual_booking__id__in=b_ids,
                                                                     booking_status_chain__booking_status__status__iexact='pod_verified',
                                                                     created_on__lte=(datetime.now() - timedelta(
                                                                         minutes=tl)).date())
            data['summary'] = {'overdue': overdue_bookings.count(),
                               'pending': (queryset.count() - overdue_bookings.count()),
                               'overdue_bookings_list': overdue_bookings.values_list('manual_booking_id', flat=True)}
        data["data"] = serializer.data
        return Response(data)

    def get_serializer_class(self):
        APP_CATEGORY = self.request.META.get('HTTP_APP_CATEGORY')
        if APP_CATEGORY == 'fms':
            return FMSManualBookingSerializer
        elif APP_CATEGORY == 'connect':
            return ConnectManualBookingSerializer
        return ManualBookingSerializer

    def get_queryset(self):
        user = self.request.user
        APP_CATEGORY = self.request.META.get('HTTP_APP_CATEGORY')
        if APP_CATEGORY == 'fms':
            supplier = get_or_none(Supplier, user=self.request.user)
            if not isinstance(supplier, Supplier):
                return ManualBooking.objects.none()
            if self.request.GET.get('booking_data_category') == 'pending_pod_bookings':
                filter_kwarg = Q(pod_status__in=['pending', 'unverified', 'rejected'])
            elif self.request.GET.get('booking_data_category') == 'pending_supplier_payment_bookings':
                filter_kwarg = Q(pod_status='completed') & Q(outward_payment_status__in=['no_payment_made', 'partial'])
            elif self.request.GET.get('booking_data_category') == 'completed_supplier_payment_bookings':
                filter_kwarg = Q(outward_payment_status__in=['complete', 'excess'])
            else:
                filter_kwarg = Q(shipment_date__gte='2017-12-01')
            vehicle_id = self.request.GET.get('vehicle_id', None)
            if vehicle_id:
                try:
                    vehicle = Vehicle.objects.get(id=vehicle_id)
                    bookings = vehicle.manualbooking_set.filter(
                        booking_supplier=supplier, shipment_date__gte='2017-12-01').filter(filter_kwarg).exclude(
                        booking_status='cancelled').order_by('-id')
                    return bookings
                except (Vehicle.DoesNotExist, Vehicle.MultipleObjectsReturned) as e:
                    return ManualBooking.objects.none()
            return ManualBooking.objects.filter(
                booking_supplier=supplier, shipment_date__gte='2017-12-01').filter(
                filter_kwarg).exclude(booking_status='cancelled').order_by('-id')
        elif is_sme_user(user=self.request.user):
            return ManualBooking.objects.filter(Q(company=get_or_none(Sme, name=self.request.user)) | Q(
                customer_to_be_billed_to=get_or_none(Sme, name=self.request.user))).exclude(
                booking_status='cancelled').order_by('-id')
        booking_ids = manual_booking_id_list(user=user)
        if self.request.GET.get('booking_data_category') == 'partial_booking_page':
            return ManualBooking.objects.filter(
                id__in=booking_ids).exclude(booking_id__startswith='AH', lr_numbers=None).exclude(
                (Q(total_in_ward_amount__gte=F('total_amount_to_company') - F('tds_deducted_amount')) & Q(
                    total_out_ward_amount__exact=F('total_amount_to_owner'))) | Q(
                    booking_status='cancelled')).order_by('-id')
        elif self.request.GET.get('booking_data_category') == 'all_booking_page':
            return ManualBooking.objects.filter(
                id__in=booking_ids).exclude(booking_id__startswith='AH', lr_numbers=None).exclude(
                Q(booking_status='cancelled')).order_by('-id')
        elif self.request.GET.get('booking_data_category') == 'incomplete_lr':
            return ManualBooking.objects.filter(id__in=booking_ids).filter(
                Q(lr_numbers=None) & Q(shipment_date__gte=(datetime.now() - timedelta(days=10)).date()) & Q(
                    booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True))
        elif self.request.GET.get('booking_data_category') == 'loaded_bookings':
            loaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='loaded'
            ).values_list('manual_booking_id', flat=True)
            return ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=loaded_bookings).filter(
                Q(lr_numbers=None) & Q(shipment_date__gte=(datetime.now() - timedelta(days=115)).date()) & Q(
                    booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True))
        elif self.request.GET.get('booking_data_category') == 'advance_not_paid':
            lr_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='lr_generated').exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            advance_paid_delivered_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['advance_paid', 'unloaded']).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            advance_not_paid_bookings = [x for x in lr_bookings if x not in advance_paid_delivered_bookings]
            return ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=advance_not_paid_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=115)).date()) & Q(
                    booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True)).distinct()
        elif self.request.GET.get('booking_data_category') == 'pay_balance':
            pod_verified_bookings = BookingStatusesMapping.objects.filter(
                Q(booking_status_chain__booking_status__status__iexact='pod_verified') |
                (Q(manual_booking__pod_status='not_required') & Q(
                    booking_status_chain__booking_status__status__iexact='unloaded'))). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            balance_paid_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['balance_paid']).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            balance_not_paid_bookings = [x for x in pod_verified_bookings if x not in balance_paid_bookings]
            return ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=balance_not_paid_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=115)).date()) & Q(
                    booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True)).distinct()
        elif self.request.GET.get('booking_data_category') == 'in_transit':
            booking_dst_ids = manual_booking_id_dest_aaho_list(user=user)
            lr_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='lr_generated').exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            unloaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['unloaded', 'pod_uploaded'],
                booking_stage__in=['in_progress', 'done']).exclude(deleted=True).values_list('manual_booking_id',
                                                                                             flat=True)
            in_transit_bookings = [x for x in lr_bookings if x not in unloaded_bookings]
            return ManualBooking.objects.filter(id__in=booking_dst_ids).filter(id__in=in_transit_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=115)).date()) & Q(
                    booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('shipment_date')
        elif self.request.GET.get('booking_data_category') == 'delivered':
            booking_dst_ids = manual_booking_id_dest_aaho_list(user=user)
            try:
                employee = Employee.objects.get(username=user)
            except Employee.DoesNotExist:
                employee = None
            try:
                if EmployeeRolesMapping.objects.filter(employee=employee).count() == 1:
                    emp_role_mapping = EmployeeRolesMapping.objects.get(employee=employee, employee_role__role='sales')
                else:
                    emp_role_mapping = None
            except EmployeeRolesMapping.DoesNotExist:
                emp_role_mapping = None
            if emp_role_mapping:
                pod_uploaded_bookings = BookingStatusesMapping.objects.filter(
                    booking_status_chain__booking_status__status__in=[
                        'unloaded', 'pod_uploaded'], booking_stage='escalated').exclude(deleted=True). \
                    values_list('manual_booking_id', flat=True)
                pod_verified_bookings = BookingStatusesMapping.objects.filter(
                    booking_status_chain__booking_status__status__in=[
                        'pod_verified', 'inward_followup_completed', 'complete'], booking_stage='escalated').exclude(
                    deleted=True). \
                    values_list('manual_booking_id', flat=True)
                unloaded_bookings = [x for x in pod_uploaded_bookings if x not in pod_verified_bookings]
            else:
                pod_uploaded_bookings = BookingStatusesMapping.objects.filter(
                    booking_status_chain__booking_status__status__in=[
                        'unloaded', 'pod_uploaded'], booking_stage__in=['in_progress', 'done']).exclude(deleted=True). \
                    values_list('manual_booking_id', flat=True)
                pod_verified_bookings = BookingStatusesMapping.objects.filter(
                    booking_status_chain__booking_status__status__in=[
                        'pod_verified', 'inward_followup_completed', 'complete']).exclude(deleted=True). \
                    values_list('manual_booking_id', flat=True)
                unloaded_bookings = [x for x in pod_uploaded_bookings if x not in pod_verified_bookings]
            return ManualBooking.objects.filter(id__in=booking_dst_ids).filter(id__in=unloaded_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) & (Q(
                    booking_id__startswith='AH')) | Q(booking_id__startswith='AAHO')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True) | Q(pod_status='not_required')).distinct().order_by(
                'pod_status')
        elif self.request.GET.get('booking_data_category') == 'invoice_confirmation':
            invoice_sent_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='party_invoice_sent').exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            emp_roles_response = get_employee_roles(user)
            if emp_roles_response['status'] == 'success' and ('city_head' in emp_roles_response['roles']
                                                              or 'management' in emp_roles_response['roles']
                                                              or 'tech' in emp_roles_response['roles']):
                return ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_sent_bookings).filter(
                    Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                    Q(booking_id__startswith='AH') & Q(invoice_status='invoice_sent')).exclude(
                    Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            else:
                return ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_sent_bookings).filter(
                    Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                    Q(booking_id__startswith='AH') & Q(invoice_status='invoice_sent') &
                    Q(customer_to_be_billed_to__aaho_poc__username=user)).exclude(
                    Q(booking_status='cancelled') | Q(deleted=True)).distinct()
        elif self.request.GET.get('booking_data_category') == 'raise_invoice':
            pod_verified_bookings = BookingStatusesMapping.objects.filter(
                Q(booking_status_chain__booking_status__status__iexact='pod_verified') |
                (Q(manual_booking__pod_status='not_required') & Q(
                    booking_status_chain__booking_status__status__iexact='unloaded'))). \
                exclude(Q(deleted=True)).values_list('manual_booking_id', flat=True)
            invoice_raised_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['invoice_raised', 'inward_followup_completed',
                                                                  'complete']).exclude(
                Q(deleted=True) | Q(booking_stage='reverted')). \
                values_list('manual_booking_id', flat=True)
            invoice_not_raised_bookings = [x for x in pod_verified_bookings if x not in invoice_raised_bookings]
            return ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_not_raised_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
        return ManualBooking.objects.filter(id__in=booking_ids).order_by('-id')

    def add_booking_status_comment(self, data, c_status):
        overdue_calculated = False
        try:
            bs = BookingStatuses.objects.get(status=c_status)
            tl = bs.time_limit
        except BookingStatuses.DoesNotExist:
            tl = 0
        for mb in data:
            m_booking = ManualBooking.objects.get(id=mb['id'])
            bsm = BookingStatusesMapping.objects.filter(manual_booking=m_booking).order_by('-id')[:1]
            if bsm:
                bsm_unloaded_pod_uploaded = None
                if c_status == 'unloaded':
                    bsm_unloaded_pod_uploaded = BookingStatusesMapping.objects.filter(manual_booking=m_booking,
                                                                                      booking_status_chain__booking_status__status__in=
                                                                                      ['unloaded',
                                                                                       'pod_uploaded']).order_by('-id')[
                                                :1]
                    bsm_unloaded = BookingStatusesMapping.objects.filter(manual_booking=m_booking,
                                                                         booking_status_chain__booking_status__status=
                                                                         'unloaded')
                    if bsm_unloaded:
                        overdue_calculated = True
                        if bsm_unloaded[0].due_date:
                            if bsm_unloaded[0].due_date < datetime.now():
                                ovedue_date_filter = True
                            else:
                                ovedue_date_filter = False
                        else:
                            ovedue_date_filter = True
                        if (bsm_unloaded[0].created_on + timedelta(
                                minutes=bsm_unloaded[
                                    0].booking_status_chain.booking_status.time_limit)) < datetime.now() and ovedue_date_filter:
                            overdue = True
                        else:
                            overdue = False
                if not overdue_calculated:
                    if bsm[0].due_date:
                        if bsm[0].due_date < datetime.now():
                            ovedue_date_filter = True
                        else:
                            ovedue_date_filter = False
                    else:
                        ovedue_date_filter = True
                    if (bsm[0].created_on + timedelta(
                            minutes=bsm[
                                0].booking_status_chain.booking_status.time_limit)) < datetime.now() and ovedue_date_filter:
                        overdue = True
                    else:
                        overdue = False
                if bsm_unloaded_pod_uploaded:
                    variable_bsm = bsm_unloaded_pod_uploaded[0]
                else:
                    variable_bsm = bsm[0]
                mb['booking_status_details'] = {'booking_id': variable_bsm.manual_booking.booking_id,
                                                'booking_status_mapping_id': variable_bsm.id,
                                                'booking_status_current': variable_bsm.booking_status_chain.booking_status.status,
                                                'booking_status_mapping_stage': variable_bsm.booking_stage,
                                                'primary_preceded_booking_status':
                                                    variable_bsm.booking_status_chain.primary_preceded_booking_status.status,
                                                'primary_succeeded_booking_status':
                                                    variable_bsm.booking_status_chain.primary_succeeded_booking_status.status,
                                                'secondary_preceded_booking_status':
                                                    variable_bsm.booking_status_chain.secondary_preceded_booking_status.status,
                                                'secondary_succeeded_booking_status':
                                                    variable_bsm.booking_status_chain.secondary_succeeded_booking_status.status,
                                                'time_limit': tl,
                                                'current_status_overdue': overdue,
                                                'booking_status_mapping_created_on': variable_bsm.created_on.date(),
                                                'due_date': variable_bsm.due_date.strftime(
                                                    '%d-%m-%Y') if variable_bsm.due_date else None,
                                                'booking_status_mapping_chain_id': variable_bsm.booking_status_chain.id}
                bsm_cmts = BookingStatusesMappingComments.objects.filter(booking_status_mapping=bsm).order_by('-id')[:1]
                if bsm_cmts:
                    mb['booking_status_details']['booking_status_comments_id'] = bsm_cmts[0].id
                    mb['booking_status_details']['booking_status_comment'] = bsm_cmts[0].comment
                    mb['booking_status_details']['booking_status_comment_created_on'] = get_formatted_time_date(
                        bsm_cmts[0].created_on)
                else:
                    mb['booking_status_details']['booking_status_comments_id'] = None
                    mb['booking_status_details']['booking_status_comment'] = None
                    mb['booking_status_details']['booking_status_comment_created_on'] = None
            else:
                mb['booking_status_details'] = {}
        return data

    def add_booking_status_location(self, data):
        for mb in data:
            l_bs_mapping_id = None
            m_booking = ManualBooking.objects.get(id=mb['id'])
            bsm_location = BookingStatusesMappingLocation.objects.filter(
                booking_status_mapping__manual_booking=m_booking).order_by('-id')[:1]
            # gps_device_location = GPSDevice.objects.filter(vehicle=m_booking.vehicle).order_by('id').last()
            gps_device_location = get_gps_device_location_from_dynamo(m_booking.vehicle_number)
            bsm_loading = BookingStatusesMapping.objects.filter(manual_booking=m_booking,
                                                                booking_status_chain__booking_status__status='loaded')
            if bsm_loading:
                loading_date = datetime.strptime(str(bsm_loading[0].created_on.date()), '%Y-%m-%d').strftime("%d-%b-%Y")
            else:
                loading_date = ''
            bsm_cmts = BookingStatusesMappingComments.objects.filter(
                booking_status_mapping__manual_booking=m_booking).order_by('-id')[:1]
            bsm_lr_generated = BookingStatusesMapping.objects.filter(manual_booking=m_booking,
                                                                     booking_status_chain__booking_status__status__in=
                                                                     ['lr_generated', 'advance_paid']).order_by('-id')[
                               :1]
            if bsm_cmts and bsm_lr_generated:
                booking_status_mapping_comment = {'booking_status_comment': bsm_cmts[0].comment,
                                                  'booking_status_comments_id': bsm_cmts[0].id,
                                                  'booking_status_comment_created_on': get_formatted_time_date(
                                                      bsm_cmts[0].created_on),
                                                  'booking_status_current': bsm_lr_generated[0].
                                                      booking_status_chain.booking_status.status,
                                                  'primary_preceded_booking_status': bsm_lr_generated[0].
                                                      booking_status_chain.primary_preceded_booking_status.status,
                                                  'primary_succeeded_booking_status': bsm_lr_generated[0].
                                                      booking_status_chain.primary_succeeded_booking_status.status,
                                                  'secondary_preceded_booking_status': bsm_lr_generated[0].
                                                      booking_status_chain.secondary_preceded_booking_status.status,
                                                  'secondary_succeeded_booking_status': bsm_lr_generated[0].
                                                      booking_status_chain.secondary_succeeded_booking_status.status,
                                                  }
                l_bs_mapping_id = bsm_lr_generated[0].id
            else:
                booking_status_mapping_comment = {}
            if bsm_location or gps_device_location:
                if not bsm_location or \
                        (gps_device_location and bsm_location and
                         gps_device_location.location_time.replace(tzinfo=None) > bsm_location[0].created_on):
                    booking_id = m_booking.booking_id
                    id = gps_device_location.device_id
                    latitude = gps_device_location.latitude
                    longitude = gps_device_location.longitude
                    reverse_geocode = google_reverse_geocode(latitude, longitude)
                    city = reverse_geocode['district']
                    district = reverse_geocode['district']
                    state = reverse_geocode['state']
                    country = 'India'
                    # overdue_date = gps_device_location.location_time
                    overdue_date = gps_device_location.location_time.replace(tzinfo=None)
                    formatted_created_on = get_formatted_time_date(gps_device_location.location_time)
                else:
                    state = get_or_none(State, name=bsm_location[0].state)
                    if state:
                        code = state.code
                    else:
                        code = bsm_location[0].state
                    booking_id = bsm_location[0].booking_status_mapping.manual_booking.booking_id
                    id = bsm_location[0].id
                    latitude = bsm_location[0].latitude
                    longitude = bsm_location[0].longitude
                    city = bsm_location[0].city
                    district = bsm_location[0].district
                    state = code
                    country = 'India'
                    overdue_date = bsm_location[0].created_on
                    formatted_created_on = get_formatted_time_date(bsm_location[0].created_on)

                if not l_bs_mapping_id:
                    l_bs_mapping_id = bsm_location[0].booking_status_mapping.id
                if overdue_date <= (datetime.now() - timedelta(days=1)):
                    location_overdue = True
                else:
                    location_overdue = False
                mb['booking_status_details'] = {
                    'booking_id': booking_id,
                    'booking_status_mapping_id': l_bs_mapping_id,
                    'booking_status_mapping_location': {
                        'id': id,
                        'latitude': latitude,
                        'longitude': longitude,
                        'city': city,
                        'district': district,
                        'state': state,
                        'country': country,
                        'created_on': formatted_created_on,
                        'location_overdue': location_overdue
                    },
                    'booking_loading_date': loading_date,
                    'booking_status_mapping_comment': booking_status_mapping_comment
                }
            else:
                if not l_bs_mapping_id:
                    bsm_lr = BookingStatusesMapping.objects.filter(manual_booking=m_booking,
                                                                   booking_status_chain__booking_status__status='lr_generated')
                    l_bs_mapping_id = bsm_lr[0].id
                mb['booking_status_details'] = {
                    'booking_id': mb['booking_id'],
                    'booking_status_mapping_id': l_bs_mapping_id,
                    'booking_loading_date': loading_date,
                    'booking_status_mapping_location': {},
                    'booking_status_mapping_comment': booking_status_mapping_comment
                }
        return data


class OutwardPaymentListView(generics.ListAPIView):
    serializer_class = OutWardPaymentSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = OutwardPaymentFilters
    ordering_fields = ('id', 'date')
    search_fields = (
        'id', 'paid_to', 'booking_id__booking_id', 'booking_id__lr_numbers__lr_number',
        'payment_mode', 'actual_amount', 'remarks', 'payment_date', 'utr',
        'invoice_number', 'status', 'created_by__username', 'is_refund_amount')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "Outward Payment List", 'amount': 10}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            if request.GET.get('outward_payment_data_category') in ['process_payment_enet', 'reconcile']:
                amount = sum(queryset.values_list('actual_amount', flat=True))
                data['summary'] = {'amount': amount, 'count': queryset.count()}
            return self.get_paginated_response(data)
        serializer = self.get_serializer(queryset, many=True)
        data['data'] = serializer.data
        if request.GET.get('outward_payment_data_category') in ['process_payment_enet', 'reconcile']:
            amount = sum(queryset.values_list('actual_amount', flat=True))
            data['summary'] = {'amount': amount, 'count': queryset.count()}
            return Response(data=data)
        data["data"] = serializer.data
        return Response(data)

    def get_queryset(self):
        user = self.request.user
        booking_ids = manual_booking_id_list(user=user)
        outward_payments = OutWardPayment.objects.filter(
            booking_id__in=ManualBooking.objects.filter(id__in=booking_ids)).exclude(
            deleted=True)
        if self.request.GET.get('outward_payment_data_category') == 'process_payment_enet':
            return OutWardPayment.objects.exclude(bank_account=None).exclude(
                Q(status__in=['paid', 'reconciled']) | Q(deleted=True))
        if self.request.GET.get('outward_payment_data_category') == 'reconcile':
            return OutWardPayment.objects.filter(
                payment_date__gte='2018-10-29', status='paid',
                payment_mode__in=['neft', 'imps', 'hdfc_internal_account', 'cheque']).exclude(bank_account=None)
        return outward_payments


class TinyManualBookingListView(generics.ListAPIView):
    serializer_class = TinyManualBookingSerializer
    search_fields = ('id', 'booking_id', 'lr_numbers__lr_number')
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('-id',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Booking List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)

    def get_queryset(self):
        if self.request.GET.get('queryset') == 'full_booking_invoice':
            return ManualBooking.objects.filter(Q(invoice_status='no_invoice') & (
                    Q(booking_id__istartswith='aaho') | Q(booking_id__istartswith='ah'))).exclude(
                Q(booking_status='cancelled') | Q(deleted=True))
        elif self.request.GET.get('queryset') == 'comm_booking_invoice':
            return ManualBooking.objects.filter(Q(invoice_status='no_invoice') & (
                    Q(booking_id__istartswith='broker') | Q(booking_id__istartswith='ab'))).exclude(
                Q(booking_status='cancelled') | Q(deleted=True))
        elif self.request.GET.get('queryset') == 'outward_payment':
            return ManualBooking.objects.filter(outward_payment_status__in=['no_payment_made', 'partial']).exclude(
                booking_id__startswith='AH', lr_numbers=None).exclude(
                Q(booking_status='cancelled') | Q(deleted=True))

        return ManualBooking.objects.exclude(Q(booking_status='cancelled') | Q(deleted=True))


class CreditDebitNoteReasonListView(generics.ListAPIView):
    serializer_class = CreditDebitNoteReasonSerializer
    search_fields = ('id', 'name')
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('-id',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successful", "status_code": status.HTTP_200_OK, "msg": "Credit Debit Note Reason List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data
        return Response(data)

    def get_queryset(self):
        return CreditDebitNoteReason.objects.exclude(deleted=True)


class OutwardPaymentBillListView(generics.ListAPIView):
    serializer_class = OutWardPaymentBillSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = OutwardPaymentBillFilters
    ordering_fields = ('id', 'date')

    search_fields = ['id', 'booking__booking_id', 'bill_number', 'bill_date', 'amount', 'vehicle_number', 'lr_number',
                     'from_city', 'to_city', 'loading_date', 'paid_to']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "OutwardPaymentBill List"}
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

        booking_ids = manual_booking_id_list(user=user)
        return OutWardPaymentBill.objects.filter(booking__in=ManualBooking.objects.filter(id__in=booking_ids)).exclude(
            deleted=True).order_by("-id")


class InwardPaymentListView(generics.ListAPIView):
    serializer_class = InWardPaymentSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = InwardPaymentFilters
    ordering_fields = ('id', 'date')
    search_fields = (
        'id', 'booking_id__booking_id', 'booking_id__lr_numbers__lr_number', 'booking_id__vehicle__vehicle_number',
        'received_from', 'tds', 'actual_amount', 'payment_mode', 'payment_date',
        'trn', 'remarks', 'invoice_number', 'created_by__username', 'created_on')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Inward Payment List"}
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

        booking_ids = manual_booking_id_list(user=user)
        return InWardPayment.objects.filter(booking_id__in=ManualBooking.objects.filter(id__in=booking_ids)). \
            exclude(deleted=True).order_by('-id', '-payment_date')


class InvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = InvoiceFilters
    ordering_fields = ('id', 'date')
    search_fields = (
        'id', 'bookings__booking_id', 'bookings__lr_numbers__lr_number', 'bookings__vehicle__vehicle_number',
        'invoice_number', 'date', 'company_name', 'payment_received', 'gstin', 'total_amount', 'remarks',
        'created_by__username', 'created_on')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Invoice List"}

        if self.request.GET.get('invoice_data_category') == 'pending_payments':
            serializer = self.get_serializer(queryset, many=True)
            data["data"] = add_invoice_booking_status_comment(serializer.data, 'invoice_confirmed')
            data["data"] = sorted(data["data"], key=lambda k: datetime.strptime(k.get('due_date', 0), '%d-%b-%Y'),
                                  reverse=False)
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
        if self.request.GET.get('invoice_data_category') == 'send_invoice':
            booking_ids = manual_booking_id_list(user=user)
            invoice_raised_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='invoice_raised').exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['party_invoice_sent', 'inward_followup_completed',
                                                                  'complete']).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            invoice_not_sent_bookings = [x for x in invoice_raised_bookings if x not in party_invoice_sent_bookings]
            bookings = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_not_sent_bookings). \
                filter(invoice_status='invoice_raised').exclude(billing_type='contract')
            return Invoice.objects.filter(bookings__in=bookings,
                                          date__gte=datetime.now().date() - timedelta(days=365)).distinct()
        if self.request.GET.get('invoice_data_category') == 'confirm_invoice':
            booking_ids = manual_booking_id_list(user=user)
            party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='party_invoice_sent').exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['invoice_confirmed', 'inward_followup_completed',
                                                                  'complete']).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            invoice_not_confirmed_bookings = [x for x in party_invoice_sent_bookings if
                                              x not in invoice_confirmed_bookings]
            bookings = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_not_confirmed_bookings). \
                filter(invoice_status='invoice_sent').exclude(billing_type='contract')
            return Invoice.objects.filter(bookings__in=bookings,
                                          date__gte=datetime.now().date() - timedelta(days=365)).distinct()
        if self.request.GET.get('invoice_data_category') == 'pending_payments':
            customer_id = self.request.GET.get('customer_id')
            invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['invoice_raised', 'party_invoice_sent',
                                                                  'invoice_confirmed']).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            complete_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='inward_followup_completed').exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pending_payments_bookings = [x for x in invoice_confirmed_bookings if x not in complete_bookings]

            emp_roles_response = get_employee_roles(user)
            if emp_roles_response['status'] == 'success' and ('city_head' in emp_roles_response['roles']
                                                              or 'management' in emp_roles_response['roles']
                                                              or 'tech' in emp_roles_response['roles']):
                bookings = ManualBooking.objects.filter(id__in=pending_payments_bookings,
                                                        invoice_status__in=['invoice_raised', 'invoice_sent',
                                                                            'invoice_confirmed'],
                                                        customer_to_be_billed_to__id=customer_id).exclude(
                    Q(booking_status='cancelled') | Q(deleted=True)).distinct()

            else:
                bookings = ManualBooking.objects.filter(id__in=pending_payments_bookings,
                                                        invoice_status__in=['invoice_raised', 'invoice_sent',
                                                                            'invoice_confirmed'],
                                                        customer_to_be_billed_to__aaho_poc__username=user,
                                                        customer_to_be_billed_to__id=customer_id).exclude(
                    Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            return Invoice.objects.filter(bookings__in=bookings, payment_received=False,
                                          date__gte=datetime.now().date() - timedelta(days=500)).distinct()
        if self.request.GET.get('invoice_data_category') == 'customer_invoices':
            customer = get_or_none(Sme, name=self.request.user)
            if isinstance(customer, Sme):
                return Invoice.objects.filter(customer_fk=customer).exclude(deleted=True).distinct()
            return Invoice.objects.none()
        booking_ids = manual_booking_id_list(user=user)
        return Invoice.objects.filter(bookings__in=ManualBooking.objects.filter(id__in=booking_ids)). \
            exclude(deleted=True).distinct()


class ManualBookingMISListView(generics.ListAPIView):
    serializer_class = ManualBookingMISSerializer
    queryset = ManualBooking.objects.exclude(
        Q(deleted=True) | Q(booking_status='cancelled')).order_by("-id", '-shipment_date')
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('id',)

    search_fields = ['id', 'booking_id', 'company_code', 'vehicle__vehicle_number', 'shipment_date', 'created_on__date',
                     'truck_broker_owner_name', 'truck_broker_owner_phone', 'truck_owner_name', 'truck_owner_phone',
                     'company__name__profile__name', 'customer_to_be_billed_to__name__profile__name',
                     'customer_to_be_billed_to__company_code', 'company__company_code', 'pod_status', 'invoice_status',
                     'lr_numbers__lr_number', 'delivered_date', '']

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


class ManualBookingViewSet(viewsets.ViewSet):
    """
        API to create Invoice Summary
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def create_mb(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        data = request.data
        data['booking_category'] = 'create_full_booking'
        data['generate-booking-and-finish'] = 'quick_full_booking'
        data['user'] = request.user.username

        data = booking_create_data(data)
        manual_booking_serializer = ManualBookingSerializer(data=data)
        if manual_booking_serializer.is_valid():
            mb = manual_booking_serializer.save()
            val_data = {
                'mb_id': mb.id,
                'status': 'confirmed',
                'user': request.user
            }
            data = manual_booking_serializer.data
            data['booking_statuses_mapping'] = manual_booking_serializer.create_booking_status_mapping(val_data)
            return success_response(status=status.HTTP_201_CREATED, data=data, msg="Manual Booking Created")
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Manual Booking not Created",
                              data=manual_booking_serializer.errors)

    def create_commission_booking(self, request):
        data = request.data
        data['user'] = request.user.username
        data['booking_category'] = 'create_commission_booking'
        data = booking_create_data(data=data)
        manual_booking_serializer = ManualBookingSerializer(data=data)
        if manual_booking_serializer.is_valid():
            booking = manual_booking_serializer.save()
            val_data = {
                'mb_id': booking.id,
                'status': 'confirmed',
                'user': request.user
            }
            data = manual_booking_serializer.data
            data['booking_statuses_mapping'] = manual_booking_serializer.create_booking_status_mapping(val_data)
            if settings.ENABLE_SMS:
                tasks.full_booking_sms_customer.delay(booking_id=booking.id)
                tasks.full_booking_sms_employee.delay(booking_id=booking.id)
            if check_gps_device_attach(booking.lorry_number):
                if settings.ENABLE_SMS:
                    tasks.tracking_sms_customer.delay(booking_id=booking.id)
            return success_response(status=status.HTTP_201_CREATED, msg="Manual Booking Created",
                                    data=manual_booking_serializer.data)
        return error_response(status=status.HTTP_400_BAD_REQUEST, data=manual_booking_serializer.errors,
                              msg="Manual Booking not Created")

    def create_full_booking(self, request):
        data = request.data
        data['user'] = request.user.username
        data['booking_category'] = 'create_full_booking'
        data = booking_create_data(data=data)
        manual_booking_serializer = ManualBookingSerializer(data=data)
        if manual_booking_serializer.is_valid():
            mb = manual_booking_serializer.save()
            customer = get_or_none(Sme, id=int_or_none(request.data.get('customer_placed_order')))
            shipment_datetime = data.get('shipment_date')
            number_of_lr = to_int(request.data.get("number_of_lr"))
            if mb.booking_id.startswith('AH'):
                lr_numbers = get_lr_numbers(
                    booking=mb,
                    source_office=mb.source_office if isinstance(mb, ManualBooking) else None,
                    destination_office=get_or_none(AahoOffice, id=int_or_none(request.POST.get('destination_office'))),
                    shipment_datetime=shipment_datetime,
                    company_code=customer.company_code if isinstance(customer, Sme) else '',
                    number_of_lr=number_of_lr,
                    created_by=request.user
                )
                msg = '{} generated successfully'.format(', '.join(lr_numbers))
                generate_lorry_receipt(mb)
            else:
                msg = ''
            if settings.ENABLE_SMS:
                tasks.full_booking_sms_customer.delay(booking_id=mb.id)
                tasks.full_booking_sms_employee.delay(booking_id=mb.id)
            if check_gps_device_attach(mb.lorry_number):
                if settings.ENABLE_SMS:
                    tasks.tracking_sms_customer.delay(booking_id=mb.id)
            return success_response(status=status.HTTP_201_CREATED, msg=msg, data=manual_booking_serializer.data)
        return error_response(status=status.HTTP_400_BAD_REQUEST, data=manual_booking_serializer.errors,
                              msg="Manual Booking not Created")

    def reprint_lr(self, request, pk=None):
        booking = get_or_none(ManualBooking, id=pk)
        if not isinstance(booking, ManualBooking):
            return error_response(status=400, data={}, msg="Invalid Booking ID")
        zip_s3_upload = generate_lorry_receipt(booking)
        return success_response(
            status=status.HTTP_200_OK,
            msg=zip_s3_upload.public_url() if isinstance(zip_s3_upload, S3Upload) else None,
            data={}
        )

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        manual_booking = get_or_none(ManualBooking, id=pk)
        if not isinstance(manual_booking, ManualBooking):
            return Response({"error": "Manual booking does not exist"}, status=status.HTTP_404_NOT_FOUND)
        manual_booking_serializer = ManualBookingSerializer(manual_booking, data=request.data)

        if manual_booking_serializer.is_valid():
            manual_booking_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Manual Booking Updated",
                "data": manual_booking_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Manual Booking not Updated",
            "data": manual_booking_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        manual_booking = get_or_none(ManualBooking, id=pk)
        if not isinstance(manual_booking, ManualBooking):
            return Response({"error": "Manual Booking does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if 'booking_id' in request.data:
            request.data.pop('booking_id')
        manual_booking_serializer = ManualBookingSerializer(
            instance=manual_booking,
            data=request.data,
            partial=True
        )

        if manual_booking_serializer.is_valid():
            manual_booking_serializer.save()
            return success_response(status=status.HTTP_202_ACCEPTED, data=manual_booking_serializer.data,
                                    msg='Booking updated')
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Manual Booking not Updated",
            "data": manual_booking_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update_contract_booking(self, request):
        for row in request.data.get('data', []):
            if to_int(row.get('rate', None)) > 0:
                booking = get_or_none(ManualBooking, id=row['id'])
                if isinstance(booking, ManualBooking):
                    manual_booking_serializer = ManualBookingSerializer(
                        instance=booking,
                        data={'party_rate': row.get('rate', 0)},
                        partial=True
                    )
                    if manual_booking_serializer.is_valid():
                        manual_booking_serializer.save()
        return success_response(status=status.HTTP_200_OK, msg='Rate updated successfull', data={})

    def retrieve(self, request, pk=None):
        APP_CATEGORY = self.request.META.get('HTTP_APP_CATEGORY')

        booking = get_or_none(ManualBooking, id=pk)
        if isinstance(booking, ManualBooking):
            manual_booking_serializer = ManualBookingSerializer(booking)
            if APP_CATEGORY == 'fms':
                manual_booking_serializer = FMSManualBookingSerializer(booking)
                return success_response(status=status.HTTP_200_OK, msg="DATA", data=manual_booking_serializer.data)
            if APP_CATEGORY == 'connect':
                manual_booking_serializer = ConnectManualBookingSerializer(booking)
                return success_response(status=status.HTTP_200_OK, msg="DATA", data=manual_booking_serializer.data)
            if booking.booking_id.startswith('AH') or booking.booking_id.startswith('AAHO'):
                template_name = 'team/booking/update-full-booking.html'
            else:
                template_name = 'team/booking/update-commission-booking.html'
            employee = get_or_none(Employee, username=request.user)
            data = manual_booking_serializer.data
            if isinstance(employee, Employee):
                employee_aaho_offices = AahoOfficeSerializer(instance=employee.office_multiple.all(), many=True).data
            else:
                employee_aaho_offices = []
            data['employee_aaho_offices'] = employee_aaho_offices
            return Response(data=data, template_name=template_name, status=status.HTTP_200_OK)
        return Response({"error": "Manual booking does not exist"}, status=status.HTTP_404_NOT_FOUND)


class LrNumberListView(generics.ListAPIView):
    serializer_class = LrNumberSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = LrNumberFilter
    ordering_fields = ('id', 'date')
    search_fields = ['id', 'booking__booking_id', 'datetime', 'lr_number']

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
        if is_sme_user(user=self.request.user):
            sme = get_or_none(Sme, name=self.request.user)
            if isinstance(sme, Sme):
                return LrNumber.objects.filter(booking__company=sme).order_by("-id")
            return LrNumber.objects.none()
        user = self.request.user
        booking_ids = manual_booking_id_list(user=user)
        return LrNumber.objects.filter(booking__in=ManualBooking.objects.filter(id__in=booking_ids)).exclude(
            deleted=True).order_by("-id")


class LrNumberViewSet(viewsets.ViewSet):
    """
        API for CRUP of Lr Number
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        lr_number_serializer = LrNumberSerializer(data=request.data)
        if lr_number_serializer.is_valid():
            lr_number_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Lr Number Created",
                "data": lr_number_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Lr Number not Created",
            "data": lr_number_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def create_confirmed_booking_lr(self, request):
        request.data['user'] = request.user.username
        booking = get_or_none(ManualBooking, id=request.data.get('mb_id'))
        if isinstance(booking, ManualBooking):
            # data = parse_create_confirmed_booking_lr_data(data=request.data, existing_booking=booking)
            manual_booking_serializer = ManualBookingSerializer(instance=booking, data=request.data, partial=True)
            if manual_booking_serializer.is_valid():
                mb = manual_booking_serializer.save()
                customer = mb.company
                shipment_datetime = mb.shipment_date
                number_of_lr = to_int(request.data.get("number_of_lr", 1))
                lr_numbers = get_lr_numbers(
                    booking=mb,
                    source_office=mb.source_office,
                    destination_office=mb.destination_office,
                    shipment_datetime=shipment_datetime,
                    company_code=customer.company_code if isinstance(customer, Sme) else '',
                    number_of_lr=number_of_lr,
                    created_by=request.user
                )
                msg = '{} generated successfully'.format(', '.join(lr_numbers))
                # generate_lorry_receipt(mb)
                if settings.ENABLE_CELERY:
                    generate_lorry_receipt_task.delay(mb.id)
                else:
                    generate_lorry_receipt_task(mb.id)
                val_data = dict()
                val_data['mb_id'] = manual_booking_serializer.data['id']
                val_data['status'] = 'lr_generated'
                val_data['user'] = self.request.user
                response_data = manual_booking_serializer.data
                response_data['booking_statuses_mapping'] = manual_booking_serializer.create_booking_status_mapping(
                    val_data)
                return success_response(msg=msg, status=status.HTTP_201_CREATED, data=response_data)
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Invalid data",
                                  data=manual_booking_serializer.errors)
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Invalid Booking ID", data={})

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        lr_number = get_or_none(LrNumber, id=pk)
        if not isinstance(lr_number, LrNumber):
            return Response({"error": "Lr Number does not exist"}, status=status.HTTP_404_NOT_FOUND)
        lr_number_serializer = LrNumberSerializer(lr_number, data=request.data)

        if lr_number_serializer.is_valid():
            lr_number_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Lr Number Updated",
                "data": lr_number_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Lr Number not Updated",
            "data": lr_number_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        lr_number = get_or_none(LrNumber, id=pk)
        if not isinstance(lr_number, LrNumber):
            return Response({"error": "Lr Number does not exist"}, status=status.HTTP_404_NOT_FOUND)
        lr_number_serializer = LrNumberSerializer(
            instance=lr_number,
            data=request.data,
            partial=True
        )

        if lr_number_serializer.is_valid():
            lr_number_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Lr Number Updated",
                "data": lr_number_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Lr Number not Updated",
            "data": lr_number_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        lr_number = get_or_none(LrNumber, id=pk)
        if isinstance(lr_number, LrNumber):
            lr_number_serializer = LrNumberSerializer(lr_number)
            return Response(lr_number_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Lr Number does not exist"}, status=status.HTTP_404_NOT_FOUND)


class RejectedPODViewSet(viewsets.ViewSet):
    """
        API for CRUD operation on Rejected POD
    """

    def create(self, request):
        # request.data["created_by"] = self.request.user.username
        # request.data["changed_by"] = self.request.user.username
        request.data["rejected_by"] = self.request.user.username
        rejected_pod_serializer = RejectedPODSerializer(data=request.data)
        if rejected_pod_serializer.is_valid():
            rejected_pod_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Rejected POD Created",
                "data": rejected_pod_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Rejected POD not Created",
            "data": rejected_pod_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    # def update(self, request, pk=None):
    #     request.data["changed_by"] = self.request.user.username
    #     rejected_pod = get_or_none(RejectedPOD, id=pk)
    #     if not isinstance(rejected_pod, RejectedPOD):
    #         return Response({"error": "Rejected POD does not exist"}, status=status.HTTP_404_NOT_FOUND)
    #     rejected_pod_serializer = RejectedPODSerializer(rejected_pod, data=request.data)
    #
    #     if rejected_pod_serializer.is_valid():
    #         rejected_pod_serializer.save()
    #         return Response(rejected_pod_serializer.data, status=status.HTTP_202_ACCEPTED)
    #     return Response(rejected_pod_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def partial_update(self, request, pk=None):
    #     request.data["changed_by"] = self.request.user.username
    #     rejected_pod = get_or_none(RejectedPOD, id=pk)
    #     if not isinstance(rejected_pod, RejectedPOD):
    #         return Response({"error": "Rejected POD does not exist"}, status=status.HTTP_404_NOT_FOUND)
    #     rejected_pod_serializer = RejectedPODSerializer(
    #         instance=rejected_pod,
    #         data=request.data,
    #         partial=True
    #     )
    #
    #     if rejected_pod_serializer.is_valid():
    #         rejected_pod_serializer.save()
    #         return Response(rejected_pod_serializer.data, status=status.HTTP_202_ACCEPTED)
    #     return Response(rejected_pod_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        rejected_pod = get_or_none(RejectedPOD, id=pk)
        if isinstance(rejected_pod, RejectedPOD):
            rejected_pod_serializer = RejectedPODSerializer(rejected_pod)
            return Response(rejected_pod_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Rejected POD does not exist"}, status=status.HTTP_404_NOT_FOUND)


class BookingConsignorConsigneeViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on BookingConsignorConsignee
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        booking_consignor_consignee_serializer = BookingConsignorConsigneeSerializer(data=request.data)
        if booking_consignor_consignee_serializer.is_valid():
            booking_consignor_consignee_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Booking consignor consignee Created",
                "data": booking_consignor_consignee_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Booking consignor consignee not Created",
            "data": booking_consignor_consignee_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        booking_consignor_consignee = get_or_none(BookingConsignorConsignee, id=pk)
        if not isinstance(booking_consignor_consignee, BookingConsignorConsignee):
            return Response({"error": "Booking consignor consignee does not exist"}, status=status.HTTP_404_NOT_FOUND)
        booking_consignor_consignee_serializer = BookingConsignorConsigneeSerializer(booking_consignor_consignee,
                                                                                     data=request.data)

        if booking_consignor_consignee_serializer.is_valid():
            booking_consignor_consignee_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Booking consignor consignee Updated",
                "data": booking_consignor_consignee_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Booking consignor consignee not Updated",
            "data": booking_consignor_consignee_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        booking_consignor_consignee = get_or_none(BookingConsignorConsignee, id=pk)
        if not isinstance(booking_consignor_consignee, BookingConsignorConsignee):
            return Response({"error": "Booking consignor consignee does not exist"}, status=status.HTTP_404_NOT_FOUND)
        booking_consignor_consignee_serializer = BookingConsignorConsigneeSerializer(
            instance=booking_consignor_consignee,
            data=request.data,
            partial=True
        )

        if booking_consignor_consignee_serializer.is_valid():
            booking_consignor_consignee_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Booking consignor consignee Updated",
                "data": booking_consignor_consignee_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Booking consignor consignee not Updated",
            "data": booking_consignor_consignee_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        booking_consignor_consignee = get_or_none(BookingConsignorConsignee, id=pk)
        if isinstance(booking_consignor_consignee, BookingConsignorConsignee):
            booking_consignor_consignee_serializer = BookingConsignorConsigneeSerializer(booking_consignor_consignee)
            return Response(booking_consignor_consignee_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Booking consignor consignee does not exist"}, status=status.HTTP_404_NOT_FOUND)


class BookingInsuranceViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Booking Insurance
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        booking_insurance_serializers = BookingInsuranceSerializer(data=request.data)
        if booking_insurance_serializers.is_valid():
            booking_insurance_serializers.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Booking insurance Created",
                "data": booking_insurance_serializers.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Booking insurance not Created",
            "data": booking_insurance_serializers.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        booking_insurance = get_or_none(BookingInsurance, id=pk)
        if not isinstance(booking_insurance, BookingInsurance):
            return Response({"error": "Booking insurance  does not exist"}, status=status.HTTP_404_NOT_FOUND)
        booking_insurance_serializers = BookingInsuranceSerializer(booking_insurance, data=request.data)

        if booking_insurance_serializers.is_valid():
            booking_insurance_serializers.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Booking insurance Updated",
                "data": booking_insurance_serializers.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Booking insurance not Updated",
            "data": booking_insurance_serializers.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        booking_insurance = get_or_none(BookingInsurance, id=pk)
        if not isinstance(booking_insurance, BookingInsurance):
            return Response({"error": "Booking insurance does not exist"}, status=status.HTTP_404_NOT_FOUND)
        booking_insurance_serializers = BookingInsuranceSerializer(
            instance=booking_insurance,
            data=request.data,
            partial=True
        )

        if booking_insurance_serializers.is_valid():
            booking_insurance_serializers.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Booking insurance Updated",
                "data": booking_insurance_serializers.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Booking insurance not Updated",
            "data": booking_insurance_serializers.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        booking_insurance = get_or_none(BookingInsurance, id=pk)
        if isinstance(booking_insurance, BookingInsurance):
            booking_insurance_serializers = BookingInsuranceSerializer(booking_insurance)
            return Response(data=booking_insurance_serializers.data, status=status.HTTP_200_OK)
        return Response({"error": "Booking insurance does not exist"}, status=status.HTTP_404_NOT_FOUND)


class InWardPaymentViewSet(viewsets.ViewSet):
    """
        API for CRUD operation on InWard Payment
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        inward_payment_serializer = InWardPaymentSerializer(data=request.data)
        if inward_payment_serializer.is_valid():
            inward_payment_serializer.save()
            return success_response(data=inward_payment_serializer.data, status=status.HTTP_201_CREATED,
                                    msg="InWard Payment Created")
        return error_response(data=inward_payment_serializer.errors, msg="InWard Payment not Created",
                              status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        inward_payment = get_or_none(InWardPayment, id=pk)
        if not isinstance(inward_payment, InWardPayment):
            return Response({"error": "InWard Payment  does not exist"}, status=status.HTTP_404_NOT_FOUND)
        inward_payment_serializer = InWardPaymentSerializer(inward_payment, data=request.data)

        if inward_payment_serializer.is_valid():
            inward_payment_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "InWard Payment Updated",
                "data": inward_payment_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "InWard Payment not Updated",
            "data": inward_payment_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        inward_payment = get_or_none(InWardPayment, id=pk)
        if not isinstance(inward_payment, InWardPayment):
            return Response({"error": "InWard Payment does not exist"}, status=status.HTTP_404_NOT_FOUND)
        inward_payment_serializer = InWardPaymentSerializer(
            instance=inward_payment,
            data=request.data,
            partial=True
        )

        if inward_payment_serializer.is_valid():
            inward_payment_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "InWard Payment Updated",
                "data": inward_payment_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "InWard Payment not Updated",
            "data": inward_payment_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        inward_payment = get_or_none(InWardPayment, id=pk)
        if isinstance(inward_payment, InWardPayment):
            inward_payment_serializer = InWardPaymentSerializer(inward_payment)
            return Response(template_name='team/payments/update_inward_payment.html',
                            data=inward_payment_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "InWard Payment does not exist"}, status=status.HTTP_404_NOT_FOUND)


class OutWardPaymentViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on OutWard Payment
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    parser_classes = (MultiPartParser, JSONParser)

    def create(self, request):
        if "created_by" not in request.data:
            request.data["created_by"] = self.request.user.username
        if "changed_by" not in request.data:
            request.data["changed_by"] = self.request.user.username
        data = parse_outward_payment_data(request.data)
        data['aaho_office'] = request.data.get('aaho_office', None)
        outward_payment_serializer = OutWardPaymentSerializer(data=data)
        if outward_payment_serializer.is_valid():
            payment = outward_payment_serializer.save()
            if payment.payment_mode == 'adjustment':
                adjust_outward_payment_adjustment_mode(payment_id=payment.id, username=request.user.username)
            if settings.ENABLE_MAIL:
                if settings.ENABLE_CELERY:
                    tasks.email_outward_payment.delay(payment_id=payment.id)
                else:
                    tasks.email_outward_payment(payment_id=payment.id)
            if payment.is_sms_supplier and settings.ENABLE_SMS:
                if settings.ENABLE_CELERY:
                    tasks.sms_outward_payment.delay(payment_id=payment.id)
                else:
                    tasks.sms_outward_payment(payment_id=payment.id)
            return success_response(status=status.HTTP_201_CREATED, msg='Outward payment created',
                                    data=outward_payment_serializer.data)
        return error_response(data=outward_payment_serializer.errors, msg="OutWard Payment not Created",
                              status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        outward_payment = get_or_none(OutWardPayment, id=pk)
        if not isinstance(outward_payment, OutWardPayment):
            return Response({"error": "OutWard Payment  does not exist"}, status=status.HTTP_404_NOT_FOUND)
        outward_payment_serializer = OutWardPaymentSerializer(outward_payment, data=request.data)

        if outward_payment_serializer.is_valid():
            outward_payment_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "OutWard Payment Updated",
                "data": outward_payment_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "OutWard Payment not Updated",
            "data": outward_payment_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        outward_payment = get_or_none(OutWardPayment, id=pk)
        if not isinstance(outward_payment, OutWardPayment):
            return Response({"error": "OutWard Payment does not exist"}, status=status.HTTP_404_NOT_FOUND)
        outward_payment_serializer = OutWardPaymentSerializer(
            instance=outward_payment,
            data=request.data,
            partial=True
        )

        if outward_payment_serializer.is_valid():
            outward_payment_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "OutWard Payment Updated",
                "data": outward_payment_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "OutWard Payment not Updated",
            "data": outward_payment_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def reconcile_payments(self, request):
        if not request.data:
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Empty Data", data={})
        for row in request.data:
            row['changed_by'] = request.user.username
            row['status'] = 'reconciled'
            payment = get_or_none(OutWardPayment, id=row.get('id', None))
            if isinstance(payment, OutWardPayment):
                serializer = OutWardPaymentSerializer(instance=payment, data=row, partial=True)
                if serializer.is_valid():
                    payment = serializer.save()

                else:
                    return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Invalid data",
                                          data=serializer.errors)
            else:
                return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Booking  Doesn't Exists", data={})
        return success_response(status=status.HTTP_202_ACCEPTED, msg='Reconciled payments', data={})

    def reconcile_bulk_payments(self, request):
        ext = os.path.splitext(str(request.FILES['payment_file']))[1]
        s3_obj = save_to_s3_bulk_reconcile_outward_payments(datetime.now().strftime('%Y%m%d%H%M') + ext,
                                                            request.FILES['payment_file'])
        filename = s3_obj.public_url()
        df = pd.read_excel(filename)
        df = df.fillna('')
        unconciled_payments = []
        invalid_data = []
        for i, row in df.iterrows():
            payment = get_or_none(OutWardPayment, id=to_int(row['Narration'][-6:]))
            if isinstance(payment, OutWardPayment) and payment.status != 'reconciled':
                data = {
                    'changed_by': request.user.username,
                    'utr': row['Chq./Ref.No.'],
                    'status': 'reconciled'
                }
                serializer = OutWardPaymentSerializer(instance=payment, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    invalid_data.append(row['Chq./Ref.No.'])
            else:
                unconciled_payments.append(row['Chq./Ref.No.'])
        if invalid_data:
            return error_response(status=status.HTTP_400_BAD_REQUEST, data={},
                                  msg='Payment data is invalid for Chq./Ref.No.: {}'.format(', '.join(invalid_data)))
        if unconciled_payments:
            return error_response(status=status.HTTP_400_BAD_REQUEST, data={},
                                  msg='Payment is not reconciled for Chq./Ref.No.: {}'.format(
                                      ', '.join(unconciled_payments)))
        return success_response(status=status.HTTP_201_CREATED, msg='Reconciled payments', data={})

    def retrieve(self, request, pk=None):
        outward_payment = get_or_none(OutWardPayment, id=pk)
        if isinstance(outward_payment, OutWardPayment):
            outward_payment_serializer = OutWardPaymentSerializer(outward_payment)
            return Response(template_name='team/payments/update_outward_payment.html',
                            data=outward_payment_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "OutWard Payment does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def payment_mode_date_message(self, request):
        payment_mode = request.GET.get('payment_mode')
        bank_account_id = request.GET.get('account_id')
        fuel_card_id = request.GET.get('fuel_card')
        date = request.GET.get('payment_date')
        amount = to_int(request.GET.get('amount'))
        if payment_mode == 'bank_transfer':
            bank = get_or_none(Bank, id=bank_account_id)
            if isinstance(bank, Bank) and isinstance(django_date_format(date), datetime):
                mode, payment_date = payment_mode_date(current_datetime=datetime.now(), bank=bank, amount=amount,
                                                       payment_date=django_date_format(date))
                return success_response(msg='Payment will be processed on {} to Account {}({})'.format(
                    payment_date.strftime('%d-%b-%Y') if payment_date else 'Unknown', bank.account_number,
                    bank.account_holder_name), data={'mode': mode, 'payment_date': payment_date},
                    status=status.HTTP_200_OK)
            else:
                return error_response(msg="Information is incorrect ", status=400, data={})
        elif payment_mode == 'fuel_card':
            fuel_card = get_or_none(FuelCard, id=fuel_card_id)
            if isinstance(fuel_card, FuelCard):
                payment_date = django_date_format(date)
                return success_response(msg='Payment will be processed on {} to Fuel Card {}'.format(
                    payment_date.strftime('%d-%b-%Y') if payment_date else 'Unknown', fuel_card.card_number),
                    data={'mode': payment_mode, 'payment_date': date},
                    status=status.HTTP_200_OK)
            else:
                return error_response(msg="Information is incorrect ", status=400, data={})
        return success_response(msg='Payment will be processed on {} through {} '.format(date, payment_mode),
                                data={'mode': payment_mode, 'payment_date': date},
                                status=status.HTTP_200_OK)


class OutWardPaymentBillViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on OutWard Payment Bill
    """

    def create(self, request):
        request.data["changed_by"] = self.request.user.username
        request.data["created_by"] = self.request.user.username
        outward_payment_bill_serializer = OutWardPaymentBillSerializer(data=request.data)
        if outward_payment_bill_serializer.is_valid():
            outward_payment_bill_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "OutWard Payment Bill Created",
                "data": outward_payment_bill_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "OutWard Payment Bill not Created",
            "data": outward_payment_bill_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def create_bill_doc(self, request):
        if not OutWardPayment.objects.filter(id__in=request.data.get('bill_nums').split(',')).exists():
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Payment ID does not exists", data={})
        booking = get_or_none(ManualBooking, id=request.data.get('booking_id'))
        if isinstance(booking, ManualBooking):
            bill_number, s3_upload = generate_receipt(
                booking=booking,
                payments_id=OutWardPayment.objects.filter(id__in=request.data.get('bill_nums').split(',')).exclude(
                    is_refund_amount=True).values_list('id', flat=True), created_by=request.user)
            return success_response(status=status.HTTP_201_CREATED, data={}, msg=s3_upload.public_url())
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Something went wrong', data={})

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        outward_payment_bill = get_or_none(OutWardPaymentBill, id=pk)
        if not isinstance(outward_payment_bill, OutWardPaymentBill):
            return Response({"error": "OutWard Payment Bill does not exist"}, status=status.HTTP_404_NOT_FOUND)
        outward_payment_bill_serializer = OutWardPaymentBillSerializer(outward_payment_bill, data=request.data)

        if outward_payment_bill_serializer.is_valid():
            outward_payment_bill_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "OutWard Payment Bill Updated",
                "data": outward_payment_bill_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "OutWard Payment Bill not Updated",
            "data": outward_payment_bill_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        outward_payment_bill = get_or_none(OutWardPaymentBill, id=pk)
        if not isinstance(outward_payment_bill, OutWardPaymentBill):
            return Response({"error": "OutWard Payment Bill does not exist"}, status=status.HTTP_404_NOT_FOUND)
        outward_payment_bill_serializer = OutWardPaymentBillSerializer(
            instance=outward_payment_bill,
            data=request.data,
            partial=True
        )

        if outward_payment_bill_serializer.is_valid():
            outward_payment_bill_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "OutWard Payment Bill Updated",
                "data": outward_payment_bill_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "OutWard Payment Bill not Updated",
            "data": outward_payment_bill_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        outward_payment_bill = get_or_none(OutWardPaymentBill, id=pk)
        if isinstance(outward_payment_bill, OutWardPaymentBill):
            outward_payment_bill_serializer = OutWardPaymentBillSerializer(outward_payment_bill)
            return Response(outward_payment_bill_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "OutWard Payment Bill does not exist"}, status=status.HTTP_404_NOT_FOUND)


class InvoiceViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Invoice
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def create(self, request):
        request.data["changed_by"] = self.request.user.username
        request.data["created_by"] = self.request.user.username
        invoice_serializer = InvoiceSerializer(data=request.data)
        if invoice_serializer.is_valid():
            invoice_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Invoice Created",
                "data": invoice_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Invoice not Created",
            "data": invoice_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def create_single_booking_invoice(self, request):
        request.data['username'] = request.user.username
        data = request.data
        if Invoice.objects.filter(bookings=get_or_none(ManualBooking, id=data.get('booking_id'))).exists():
            return error_response(msg="Invoice is already created", status=status.HTTP_400_BAD_REQUEST, data={})
        try:
            invoice.make_invoice(
                ManualBooking.objects.filter(id=data.get('booking_id')),
                booking_type='full',
                form_data=parse_single_invoice_data(data=data),
                created_by=request.user
            )
            return success_response(status=status.HTTP_201_CREATED, msg="Invoice Created", data={})
        except invoice.InvoiceError:
            return error_response(msg="Invoice is already created", status=status.HTTP_400_BAD_REQUEST, data={})

    def invoice_multiple_commission_booking(self, request):
        bookings = ManualBooking.objects.filter(id__in=request.data.get('booking_ids').split(','))
        if bookings.exists():
            invoice.make_invoice(bookings, booking_type='commission', form_data=request.data, created_by=request.user)
            return success_response(status=status.HTTP_201_CREATED, msg="Invoice created", data={})
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg='something went wrong', data={})

    def invoice_multiple_full_booking(self, request):
        bookings = ManualBooking.objects.filter(id__in=request.data.get('booking_ids').split(','))
        summary_required = True if request.data.get('invoice_summary') == 'on' and bookings.count() > 2 else False
        combined_invoice = True if request.data.get('combined_invoice') == 'on' else False

        try:
            unique_booking_ids = request.data.get('booking_ids').split(',')
            customer_to_be_billed_to = request.data.get('to_be_billed_to')
            for id in unique_booking_ids:
                update_data = {'booking_id': id, 'to_be_billed_to': customer_to_be_billed_to}
                update_booking_field(update_data)

            # bookings = ManualBooking.objects.filter(booking_id__in=request.POST.get('booking_ids').split(','))
            invoice_summary = invoice.make_invoice(bookings, booking_type='full', form_data=request.data,
                                                   created_by=request.user, summary_required=summary_required,
                                                   combined_invoice=combined_invoice)
            data = []
            if combined_invoice:
                booking = bookings.last()
                inv = Invoice.objects.filter(bookings=booking).last()
                if isinstance(inv, Invoice) and inv.s3_upload:
                    data.append({
                        's3_url': inv.s3_upload.public_url(),
                        'filename': inv.s3_upload.filename
                    })
                    return Response(template_name='team/invoices/download-generated-invoice-pdf.html',
                                    data={'download_invoice': False, 'data': data})

            zip_filename = "invoices.zip"
            zip_bytes_io = io.BytesIO()
            zf = zipfile.ZipFile(zip_bytes_io, "w")

            for booking in bookings:
                if Invoice.objects.filter(bookings=booking).exclude(deleted=True).exists():
                    inv = Invoice.objects.filter(bookings=booking).exclude(deleted=True).last()
                    if isinstance(inv, Invoice) and inv.s3_upload:
                        data.append({
                            's3_url': inv.s3_upload.public_url(),
                            'filename': inv.s3_upload.filename
                        })
                        file_response = requests.get(inv.s3_upload.public_url())
                        zf.writestr(inv.s3_upload.filename, file_response.content)
            if isinstance(invoice_summary, InvoiceSummary) and invoice_summary.s3_upload:
                data.append({
                    's3_url': invoice_summary.s3_upload.public_url(),
                    'filename': invoice_summary.s3_upload.filename
                })
                file_response = requests.get(invoice_summary.s3_upload.public_url())
                zf.writestr(invoice_summary.s3_upload.filename, file_response.content)
            zf.close()
            zip_s3_upload = s3util.save_to_s3_invoice(filename=zip_filename, content=zip_bytes_io.getvalue())
            data.append({
                's3_url': zip_s3_upload.public_url(),
                'filename': 'Download All'
            })
            return Response(template_name='team/invoices/download-generated-invoice-pdf.html',
                            data={'download_invoice': True, 'data': data}, status=status.HTTP_201_CREATED)
        except invoice.InvoiceError:
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg='error', data={})

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        invoice = get_or_none(Invoice, id=pk)
        if not isinstance(invoice, Invoice):
            return Response({"error": "Invoice does not exist"}, status=status.HTTP_404_NOT_FOUND)
        invoice_serializer = InvoiceSerializer(invoice, data=request.data)

        if invoice_serializer.is_valid():
            invoice_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Invoice Updated",
                "data": invoice_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Invoice not Updated",
            "data": invoice_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        invoice = get_or_none(Invoice, id=pk)
        if not isinstance(invoice, Invoice):
            return Response({"error": "Invoice does not exist"}, status=status.HTTP_404_NOT_FOUND)
        invoice_serializer = InvoiceSerializer(
            instance=invoice,
            data=request.data,
            partial=True
        )

        if invoice_serializer.is_valid():
            invoice_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Invoice Updated",
                "data": invoice_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Invoice not Updated",
            "data": invoice_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        invoice = get_or_none(Invoice, id=pk)
        if isinstance(invoice, Invoice):
            invoice_serializer = InvoiceSerializer(invoice)
            return Response(invoice_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Invoice does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def pod_files(self, request, pk):
        invoice = get_or_none(Invoice, id=pk)
        if isinstance(invoice, Invoice):
            pod = PODFile.objects.filter(booking__invoices__id=pk).filter(verified=True, is_valid=True).exclude(
                deleted=True)
            return Response(data=PODFileSerializer(instance=pod, many=True).data, status=status.HTTP_200_OK)
        return Response({"error": "Invoice does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ToPayInvoiceViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on To Pay Invoice
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        to_pay_invoice_serializer = ToPayInvoiceSerializer(data=request.data)
        if to_pay_invoice_serializer.is_valid():
            to_pay_invoice_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "To Pay Invoice Created",
                "data": to_pay_invoice_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "To Pay Invoice not Created",
            "data": to_pay_invoice_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        to_pay_invoice = get_or_none(ToPayInvoice, id=pk)
        if not isinstance(to_pay_invoice, ToPayInvoice):
            return Response({"error": "To Pay Invoice does not exist"}, status=status.HTTP_404_NOT_FOUND)
        to_pay_invoice_serializer = ToPayInvoiceSerializer(to_pay_invoice, data=request.data)

        if to_pay_invoice_serializer.is_valid():
            to_pay_invoice_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "To Pay Invoice Updated",
                "data": to_pay_invoice_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "To Pay Invoice not Updated",
            "data": to_pay_invoice_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        to_pay_invoice = get_or_none(ToPayInvoice, id=pk)
        if not isinstance(to_pay_invoice, ToPayInvoice):
            return Response({"error": "To Pay Invoice does not exist"}, status=status.HTTP_404_NOT_FOUND)
        to_pay_invoice_serializer = ToPayInvoiceSerializer(
            instance=to_pay_invoice,
            data=request.data,
            partial=True
        )

        if to_pay_invoice_serializer.is_valid():
            to_pay_invoice_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "To Pay Invoice Updated",
                "data": to_pay_invoice_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "To Pay Invoice not Updated",
            "data": to_pay_invoice_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        to_pay_invoice = get_or_none(ToPayInvoice, id=pk)
        if isinstance(to_pay_invoice, ToPayInvoice):
            to_pay_invoice_serializer = ToPayInvoiceSerializer(to_pay_invoice)
            return Response(to_pay_invoice_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "To Pay Invoice does not exist"}, status=status.HTTP_404_NOT_FOUND)


class PendingInwardPaymentEntryViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Pending Inward Payment Entry
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    parser_classes = (MultiPartParser, JSONParser)

    def create(self, request):
        request.data["uploaded_by"] = self.request.user.username
        pending_inward_payment_entry_serializer = PendingInwardPaymentEntrySerializer(data=request.data)
        if pending_inward_payment_entry_serializer.is_valid():
            pending_inward = pending_inward_payment_entry_serializer.save()
            if isinstance(pending_inward.customer, Sme):
                placed_order_accounting_summary(sme_id=pending_inward.customer.id)
                billed_customer_accounting_summary(sme_id=pending_inward.customer.id)
            return success_response(status=status.HTTP_201_CREATED, msg="Pending inward payment entry Created",
                                    data=pending_inward_payment_entry_serializer.data)
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Something Went wrong",
                              data=pending_inward_payment_entry_serializer.errors)

    def bulk_create(self, request):
        save_to_s3_bulk_inward_payments(datetime.now().strftime('%Y%m%d%H%M') + '.xlsx', request.FILES['payment_file'])
        filename = S3Upload.objects.filter(folder__iexact='uploads/creditinward').latest('created_on').public_url()
        df = pd.read_excel(filename)
        df = df.fillna('')
        invalid_format = False
        invalid_format_error = []
        for i, row in df.iterrows():
            try:
                if not isinstance(row['Date'], datetime):
                    datetime.strptime(row['Date'], '%d/%m/%y')
            except ValueError:
                invalid_format = True
                invalid_format_error.append('Date Format Error for TRN: %s, Date: %s, Amount: %s' % (
                    row['ChqUTR No.'], row['Date'], str(row['Amount'])))
            payment_mode = row['Mode']
            if payment_mode and payment_mode.lower() in ['cash', 'neft', 'imps', 'cheque', 'rtgs',
                                                         'hdfc_internal_account']:
                payment_mode.lower()
            else:
                invalid_format = True
                invalid_format_error.append('Payment Mode Format Error for TRN: %s, Date: %s, Amount: %s' % (
                    row['ChqUTR No.'], row['Date'], str(row['Amount'])))
            try:
                float(row['Amount'])
            except ValueError:
                invalid_format = True
                invalid_format_error.append('Amount Format Error for TRN: %s, Date: %s, Amount: %s' % (
                    row['ChqUTR No.'], row['Date'], str(row['Amount'])))
        if invalid_format:
            return Response(template_name='team/payments/add_received_payment.html', status=status.HTTP_200_OK, data={
                'duplicate_payments': [],
                'success_payments': [],
                'upload_file': True,
                'invalid_format_error': invalid_format_error
            })

        success_payment_id = []
        duplicate_payment_id = []
        for i, row in df.iterrows():
            payment_date = datetime.strptime(row['Date'], '%d/%m/%y') if not isinstance(row['Date'], datetime) else \
                row['Date']
            if PendingInwardPaymentEntry.objects.filter(
                    trn=row['ChqUTR No.'], payment_date=payment_date).exists():
                for value in PendingInwardPaymentEntry.objects.filter(
                        trn=row['ChqUTR No.'], payment_date=payment_date):
                    duplicate_payment_id.append(value.id)
            else:

                payment_mode = row['Mode']
                if payment_mode and payment_mode.lower() in ['cash', 'neft', 'imps', 'cheque', 'rtgs',
                                                             'hdfc_internal_account']:
                    payment_mode = payment_mode.lower()
                else:
                    payment_mode = None
                pending_payment_entry = PendingInwardPaymentEntry.objects.create(
                    customer_name=row['Party Name'],
                    payment_mode=payment_mode,
                    amount=to_int(row['Amount']),
                    payment_date=payment_date,
                    additional_remark=row['Narration'],
                    trn=row['ChqUTR No.'],
                    uploaded_by=request.user,
                    uploaded_datetime=datetime.now(),
                )
                if isinstance(pending_payment_entry.customer, Sme):
                    placed_order_accounting_summary(sme_id=pending_payment_entry.customer.id)
                    billed_customer_accounting_summary(sme_id=pending_payment_entry.customer.id)
                success_payment_id.append(pending_payment_entry.id)
        return Response(template_name='team/payments/add_received_payment.html', data={
            'duplicate_payments': PendingInwardPaymentEntrySerializer(
                instance=PendingInwardPaymentEntry.objects.filter(id__in=duplicate_payment_id), many=True).data,
            'success_payments': PendingInwardPaymentEntrySerializer(
                instance=PendingInwardPaymentEntry.objects.filter(id__in=success_payment_id), many=True).data,
            'upload_file': True,
        })

    def bulk_adjust(self, request):
        request.data['username'] = request.user.username
        data = request.data
        pending_payment = get_or_none(PendingInwardPaymentEntry, id=request.data.get('payment_id', -1))
        if not isinstance(pending_payment, PendingInwardPaymentEntry) or pending_payment.adjusted_flag:
            return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Already Adjusted", data={})
        if isinstance(pending_payment, PendingInwardPaymentEntry):
            pending_payment_serializer = PendingInwardPaymentEntrySerializer(instance=pending_payment, data={
                'adjusted_by': request.user.username,
                'adjusted_flag': True,
                'credited_flag': True,
                'adjusted_datetime': datetime.now(),
            }, partial=True)
            if pending_payment_serializer.is_valid():
                pending_inward_entry = pending_payment_serializer.save()
                if isinstance(pending_inward_entry.customer, Sme):
                    placed_order_accounting_summary(sme_id=pending_inward_entry.customer.id)
                    billed_customer_accounting_summary(sme_id=pending_inward_entry.customer.id)
            else:
                return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Invalid data',
                                      data=pending_payment_serializer.errors)
        for cnc in data.get('cnc', []):
            if to_int(cnc.get('amount', 0)) > 0:
                cnc_object = get_or_none(CreditNoteCustomer, id=cnc.get('id', None))
                if isinstance(cnc_object, CreditNoteCustomer):
                    cnc_object.adjusted_amount = cnc_object.adjusted_amount + to_int(cnc.get('amount', 0))
                    cnc_object.adjusted_by = request.user
                    cnc_object.adjusted_on = datetime.now()
                    cnc_object.status = 'adjusted' if to_int(
                        cnc.get('amount', 0)) == cnc_object.credit_amount else 'partial'
                    cnc_object.save()
                    PendingInwardPaymentCreditDebitNoteCustomer.objects.create(
                        cnc=cnc_object, pending_inward=pending_payment,
                        adjusted_amount=to_int(cnc.get('amount', 0)),
                        created_by=request.user,
                        changed_by=request.user
                    )
        for dnc in data.get('dnc', []):
            if to_int(dnc.get('amount', 0)) > 0:
                dnc_object = get_or_none(DebitNoteCustomer, id=dnc.get('id', None))
                if isinstance(dnc_object, DebitNoteCustomer):
                    dnc_object.adjusted_amount = dnc_object.adjusted_amount + to_int(dnc.get('amount', 0))
                    dnc_object.adjusted_by = request.user
                    dnc_object.adjusted_on = datetime.now()
                    dnc_object.status = 'adjusted' if to_int(
                        dnc.get('amount', 0)) == dnc_object.debit_amount else 'partial'
                    dnc_object.save()
                    PendingInwardPaymentCreditDebitNoteCustomer.objects.create(
                        dnc=dnc_object, pending_inward=pending_payment,
                        adjusted_amount=to_int(dnc.get('amount', 0)),
                        created_by=request.user,
                        changed_by=request.user
                    )
        inward_payments_data, bookings_id = parse_pending_inward_adjustment_data(data)
        for inwrad_payment in inward_payments_data:
            inward_payment_serializer = InWardPaymentSerializer(data=inwrad_payment)
            if inward_payment_serializer.is_valid():
                ip = inward_payment_serializer.save()
                pending_payment.inward_payment.add(ip)
            else:
                return error_response(status=status.HTTP_400_BAD_REQUEST, msg='Something went wrong', data={})
        for booking in ManualBooking.objects.filter(id__in=bookings_id):
            pending_payment.bookings.add(booking)
        for invoice in Invoice.objects.filter(bookings__in=ManualBooking.objects.filter(id__in=bookings_id)):
            amount = 0
            for booking in invoice.bookings.all():
                amount += booking.balance_for_customer
            if -20 < amount < 20:
                invoice.payment_received = True
                invoice.save()
                for booking in invoice.bookings.all():
                    booking_inv_raised = check_booking_status(booking, 'invoice_raised')
                    if booking_inv_raised:
                        booking_inv_sent = check_booking_status(booking, 'party_invoice_sent')
                        if not booking_inv_sent:
                            create_new_booking_status(booking, 'party_invoice_sent', User.objects.get(username='admin'))
                        else:
                            update_booking_status(booking, 'party_invoice_sent', 'in_progress',
                                                  User.objects.get(username='admin'))
                        booking_inv_confirmed = check_booking_status(booking, 'invoice_confirmed')
                        if not booking_inv_confirmed:
                            create_new_booking_status(booking, 'invoice_confirmed', User.objects.get(username='admin'))
                        else:
                            update_booking_status(booking, 'invoice_confirmed', 'in_progress',
                                                  User.objects.get(username='admin'))
        return success_response(status=status.HTTP_200_OK, msg='Fully Adjusted', data={})

    def update(self, request, pk=None):
        request.data["adjusted_by"] = self.request.user.username
        pending_inward_payment_entry = get_or_none(PendingInwardPaymentEntry, id=pk)
        if not isinstance(pending_inward_payment_entry, PendingInwardPaymentEntry):
            return Response({"error": "Pending inward payment entry does not exist"}, status=status.HTTP_404_NOT_FOUND)

        pending_inward_payment_entry_serializer = PendingInwardPaymentEntrySerializer(
            instance=pending_inward_payment_entry,
            data=request.data
        )
        if pending_inward_payment_entry_serializer.is_valid():
            pending_payment_entry = pending_inward_payment_entry_serializer.save()
            if isinstance(pending_payment_entry.customer, Sme):
                placed_order_accounting_summary(sme_id=pending_payment_entry.customer.id)
                billed_customer_accounting_summary(sme_id=pending_payment_entry.customer.id)
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Pending inward payment entry Updated",
                "data": pending_inward_payment_entry_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Pending inward payment entry not Updated",
            "data": pending_inward_payment_entry_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["adjusted_by"] = self.request.user.username
        pending_inward_payment_entry = get_or_none(PendingInwardPaymentEntry, id=pk)
        if not isinstance(pending_inward_payment_entry, PendingInwardPaymentEntry):
            return Response({"error": "Pending inward payment entry does not exist"}, status=status.HTTP_404_NOT_FOUND)
        pending_inward_payment_entry_serializer = PendingInwardPaymentEntrySerializer(
            instance=pending_inward_payment_entry,
            data=request.data,
            partial=True
        )

        if pending_inward_payment_entry_serializer.is_valid():
            pending_payment_entry = pending_inward_payment_entry_serializer.save()
            if isinstance(pending_payment_entry.customer, Sme):
                placed_order_accounting_summary(sme_id=pending_payment_entry.customer.id)
                billed_customer_accounting_summary(sme_id=pending_payment_entry.customer.id)
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Pending inward payment entry Updated",
                "data": pending_inward_payment_entry_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Pending inward payment entry not Updated",
            "data": pending_inward_payment_entry_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        pending_inward_payment_entry = get_or_none(PendingInwardPaymentEntry, id=pk)
        if isinstance(pending_inward_payment_entry, PendingInwardPaymentEntry):
            pending_inward_payment_entry_serializer = PendingInwardPaymentEntrySerializer(pending_inward_payment_entry)
            return Response(pending_inward_payment_entry_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Pending inward payment entry does not exist"}, status=status.HTTP_404_NOT_FOUND)


class CreditDebitNoteReasonViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Credit Debit Note Reason
    """

    def create(self, request):
        request.data["changed_by"] = self.request.user.username
        request.data["created_by"] = self.request.user.username
        credit_debit_note_reason_serializer = CreditDebitNoteReasonSerializer(data=request.data)
        if credit_debit_note_reason_serializer.is_valid():
            credit_debit_note_reason_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Credit Debit Note Reason Created",
                "data": credit_debit_note_reason_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Credit Debit Note Reason not Created",
            "data": credit_debit_note_reason_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        credit_debit_note_reason = get_or_none(CreditDebitNoteReason, id=pk)
        if not isinstance(credit_debit_note_reason, CreditDebitNoteReason):
            return Response({"error": "Credit Debit Note Reason does not exist"}, status=status.HTTP_404_NOT_FOUND)
        credit_debit_note_reason_serializer = CreditDebitNoteReasonSerializer(credit_debit_note_reason,
                                                                              data=request.data)

        if credit_debit_note_reason_serializer.is_valid():
            credit_debit_note_reason_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Credit Debit Note Reason Updated",
                "data": credit_debit_note_reason_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Credit Debit Note Reason not Updated",
            "data": credit_debit_note_reason_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        credit_debit_note_reason = get_or_none(CreditDebitNoteReason, id=pk)
        if not isinstance(credit_debit_note_reason, CreditDebitNoteReason):
            return Response({"error": "Credit Debit Note Reason does not exist"}, status=status.HTTP_404_NOT_FOUND)
        credit_debit_note_reason_serializer = CreditDebitNoteReasonSerializer(
            instance=credit_debit_note_reason,
            data=request.data,
            partial=True
        )

        if credit_debit_note_reason_serializer.is_valid():
            credit_debit_note_reason_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Credit Debit Note Reason Updated",
                "data": credit_debit_note_reason_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Credit Debit Note Reason not Updated",
            "data": credit_debit_note_reason_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        credit_debit_note_reason = get_or_none(CreditDebitNoteReason, id=pk)
        if isinstance(credit_debit_note_reason, CreditDebitNoteReason):
            credit_debit_note_reason_serializer = CreditDebitNoteReasonSerializer(credit_debit_note_reason)
            return Response(credit_debit_note_reason_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Credit Debit Note Reason does not exist"}, status=status.HTTP_404_NOT_FOUND)


class CreditNoteCustomerListView(generics.ListAPIView):
    serializer_class = CreditNoteCustomerSerializer
    queryset = CreditNoteCustomer.objects.all().order_by('-id')
    # pagination_class = StandardResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = CreditNoteCustomerFilters
    ordering_fields = ('id',)
    search_fields = (
        'id', 'credit_note_number', 'credit_amount', 'adjusted_amount', 'approved_by__username', 'approved_on',
        'adjusted_by__username', 'adjusted_on', 'remarks', 'status', 'rejected_by__username', 'rejected_on',
        'rejection_reason', 'created_by__username', 'created_on')

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


class CreditNoteCustomerViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Credit Note Customer
    """

    def create(self, request):
        request.data["changed_by"] = self.request.user.username
        request.data["created_by"] = self.request.user.username
        if 'status' in request.data and request.data['status'] in ['approved', 'rejected', 'partial', 'adjusted']:
            return error_response(status=status.HTTP_400_BAD_REQUEST, data={}, msg="Not a valid status")
        credit_note_customer_serializer = CreditNoteCustomerSerializer(data=request.data)

        if credit_note_customer_serializer.is_valid():
            credit_note_customer_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": 'Credit Note ID {} is generated'.format(
                    credit_note_customer_serializer.data['credit_note_number']),
                "data": credit_note_customer_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)

            # return Response(
            #     {"data": credit_note_customer_serializer.data, "msg": 'Credit Note ID {} is generated'.format(
            #         credit_note_customer_serializer.data['credit_note_number'])}, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Credit Note Customer not Created",
            "data": credit_note_customer_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        credit_note_customer = get_or_none(CreditNoteCustomer, id=pk)
        if not isinstance(credit_note_customer, CreditNoteCustomer):
            return Response({"error": "Credit Note Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)
        credit_note_customer_serializer = CreditNoteCustomerSerializer(credit_note_customer, data=request.data)

        if credit_note_customer_serializer.is_valid():
            credit_note_customer_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Credit Note Customer Updated",
                "data": credit_note_customer_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Credit Note Customer not Updated",
            "data": credit_note_customer_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        credit_note_customer = get_or_none(CreditNoteCustomer, id=pk)
        if not isinstance(credit_note_customer, CreditNoteCustomer):
            return Response({"error": "Credit Note Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        if data.get('status', None) == 'approved' and credit_note_customer.bookings.count() == 1:
            data['adjusted_amount'] = credit_note_customer.credit_amount
            data['status'] = 'adjusted'
            data['adjusted_by'] = request.user.username
            data['adjusted_on'] = datetime.now()
            if Invoice.objects.filter(bookings__in=credit_note_customer.bookings.all()).exists():
                data['invoice'] = Invoice.objects.filter(bookings__in=credit_note_customer.bookings.all()).last().id
        credit_note_customer_serializer = CreditNoteCustomerSerializer(
            instance=credit_note_customer,
            data=data,
            partial=True
        )

        if credit_note_customer_serializer.is_valid():
            credit_note_customer_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Credit Note Customer Updated",
                "data": credit_note_customer_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Credit Note Customer not Updated",
            "data": credit_note_customer_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        credit_note_customer = get_or_none(CreditNoteCustomer, id=pk)
        if isinstance(credit_note_customer, CreditNoteCustomer):
            credit_note_customer_serializer = CreditNoteCustomerSerializer(credit_note_customer)
            return Response(credit_note_customer_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Credit Note Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DebitNoteCustomerListView(generics.ListAPIView):
    serializer_class = DebitNoteCustomerSerializer
    queryset = DebitNoteCustomer.objects.all().order_by('-id')
    # pagination_class = StandardResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = DebitNoteCustomerFilters
    ordering_fields = ('id',)
    search_fields = (
        'id', 'debit_note_number', 'debit_amount', 'adjusted_amount', 'approved_by__username', 'approved_on',
        'adjusted_by__username', 'adjusted_on', 'remarks', 'status', 'rejected_by__username', 'rejected_on',
        'rejection_reason', 'created_by__username', 'created_on')

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


class DebitNoteCustomerViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Debit Note Customer
    """

    def create(self, request):
        request.data["changed_by"] = self.request.user.username
        request.data["created_by"] = self.request.user.username
        if 'status' in request.data and request.data['status'] in ['approved', 'rejected', 'partial', 'adjusted']:
            return error_response(status=status.HTTP_400_BAD_REQUEST, data={}, msg="Not a valid status")
        debit_note_customer_serializer = DebitNoteCustomerSerializer(data=request.data)
        if debit_note_customer_serializer.is_valid():
            debit_note_customer_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": 'Debit Note ID {} is generated'.format(debit_note_customer_serializer.data['debit_note_number']),
                "data": debit_note_customer_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
            # return Response(
            #     {"data": debit_note_customer_serializer.data, "msg": 'Debit Note ID {} is generated'.format(
            #         debit_note_customer_serializer.data['debit_note_number'])}, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Supplier Vehicle not Created",
            "data": debit_note_customer_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        debit_note_customer = get_or_none(DebitNoteCustomer, id=pk)
        if not isinstance(debit_note_customer, DebitNoteCustomer):
            return Response({"error": "Debit Note Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)
        debit_note_customer_serializer = DebitNoteCustomerSerializer(debit_note_customer, data=request.data)

        if debit_note_customer_serializer.is_valid():
            debit_note_customer_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Supplier Vehicle Updated",
                "data": debit_note_customer_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Supplier Vehicle not Updated",
            "data": debit_note_customer_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        debit_note_customer = get_or_none(DebitNoteCustomer, id=pk)
        if not isinstance(debit_note_customer, DebitNoteCustomer):
            return Response({"error": "Debit Note Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        if data.get('status', None) == 'approved' and debit_note_customer.bookings.count() == 1:
            data['adjusted_amount'] = debit_note_customer.debit_amount
            data['status'] = 'adjusted'
            data['adjusted_by'] = request.user.username
            data['adjusted_on'] = datetime.now()
            if Invoice.objects.filter(bookings__in=debit_note_customer.bookings.all()).exists():
                data['invoice'] = Invoice.objects.filter(bookings__in=debit_note_customer.bookings.all()).last().id
        debit_note_customer_serializer = DebitNoteCustomerSerializer(
            instance=debit_note_customer,
            data=data,
            partial=True
        )

        if debit_note_customer_serializer.is_valid():
            debit_note_customer_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Supplier Vehicle Updated",
                "data": debit_note_customer_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Supplier Vehicle not Updated",
            "data": debit_note_customer_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        debit_note_customer = get_or_none(DebitNoteCustomer, id=pk)
        if isinstance(debit_note_customer, DebitNoteCustomer):
            debit_note_customer_serializer = DebitNoteCustomerSerializer(debit_note_customer)
            return Response(debit_note_customer_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Debit Note Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)


class CreditNoteSupplierListView(generics.ListAPIView):
    serializer_class = CreditNoteSupplierSerializer
    queryset = CreditNoteSupplier.objects.all().order_by('-id')
    # pagination_class = StandardResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = CreditNoteSupplierFilters
    ordering_fields = ('id',)
    search_fields = (
        'id', 'credit_note_number', 'credit_amount', 'adjusted_amount', 'approved_by__username', 'approved_on',
        'adjusted_by__username', 'adjusted_on', 'remarks', 'status', 'rejected_by__username', 'rejected_on',
        'rejection_reason', 'created_by__username', 'created_on')

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


class CreditNoteSupplierViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Credit Note Supplier
    """

    def create(self, request):
        request.data["changed_by"] = self.request.user.username
        request.data["created_by"] = self.request.user.username
        if 'status' in request.data and request.data['status'] in ['approved', 'rejected', 'partial', 'adjusted']:
            return error_response(status=status.HTTP_400_BAD_REQUEST, data={}, msg="Not a valid status")
        credit_note_supplier_serializer = CreditNoteSupplierSerializer(data=request.data)
        if credit_note_supplier_serializer.is_valid():
            credit_note_supplier_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": 'Credit Note ID {} is generated'.format(
                    credit_note_supplier_serializer.data['credit_note_number']),
                "data": credit_note_supplier_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
            # return Response(
            #     {"data": credit_note_supplier_serializer.data, "msg": 'Credit Note ID {} is generated'.format(
            #         credit_note_supplier_serializer.data['credit_note_number'])}, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Credit Note Supplier not Created",
            "data": credit_note_supplier_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        credit_note_supplier = get_or_none(CreditNoteSupplier, id=pk)
        if not isinstance(credit_note_supplier, CreditNoteSupplier):
            return Response({"error": "Credit Note Supplier does not exist"}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        if data.get('status', None) == 'approved' and credit_note_supplier.bookings.count() == 1:
            data['adjusted_amount'] = credit_note_supplier.credit_amount
            data['status'] = 'adjusted'
            data['adjusted_by'] = request.user.username
            data['adjusted_on'] = datetime.now()
            if Invoice.objects.filter(bookings__in=credit_note_supplier.bookings.all()).exists():
                data['invoice'] = Invoice.objects.filter(bookings__in=credit_note_supplier.bookings.all()).last().id
        credit_note_supplier_serializer = CreditNoteSupplierSerializer(credit_note_supplier, data=request.data)

        if credit_note_supplier_serializer.is_valid():
            credit_note_supplier_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Credit Note Supplier Updated",
                "data": credit_note_supplier_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Credit Note Supplier not Updated",
            "data": credit_note_supplier_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        credit_note_supplier = get_or_none(CreditNoteSupplier, id=pk)
        if not isinstance(credit_note_supplier, CreditNoteSupplier):
            return Response({"error": "Credit Note Supplier does not exist"}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        if data.get('status', None) == 'approved' and credit_note_supplier.bookings.count() == 1:
            data['adjusted_amount'] = credit_note_supplier.credit_amount
            data['status'] = 'adjusted'
            data['adjusted_by'] = request.user.username
            data['adjusted_on'] = datetime.now()
            if Invoice.objects.filter(bookings__in=credit_note_supplier.bookings.all()).exists():
                data['invoice'] = Invoice.objects.filter(bookings__in=credit_note_supplier.bookings.all()).last().id
        credit_note_supplier_serializer = CreditNoteSupplierSerializer(
            instance=credit_note_supplier,
            data=data,
            partial=True
        )

        if credit_note_supplier_serializer.is_valid():
            credit_note_supplier_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Credit Note Supplier Updated",
                "data": credit_note_supplier_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Credit Note Supplier not Updated",
            "data": credit_note_supplier_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        credit_note_supplier = get_or_none(CreditNoteSupplier, id=pk)
        if isinstance(credit_note_supplier, CreditNoteSupplier):
            credit_note_supplier_serializer = CreditNoteSupplierSerializer(credit_note_supplier)
            return Response(credit_note_supplier_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Credit Note Supplier does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DebitNoteSupplierListView(generics.ListAPIView):
    serializer_class = DebitNoteSupplierSerializer
    queryset = DebitNoteSupplier.objects.all().order_by('-id')
    # pagination_class = StandardResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = DebitNoteSupplierFilters
    ordering_fields = ('id',)
    search_fields = (
        'id', 'debit_note_number', 'debit_amount', 'adjusted_amount', 'approved_by__username', 'approved_on',
        'adjusted_by__username', 'adjusted_on', 'remarks', 'status', 'rejected_by__username', 'rejected_on',
        'rejection_reason', 'created_by__username', 'created_on')

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


class DebitNoteSupplierViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Debit Note Supplier
    """

    def create(self, request):
        request.data["changed_by"] = self.request.user.username
        request.data["created_by"] = self.request.user.username
        if 'status' in request.data and request.data['status'] in ['approved', 'rejected', 'partial', 'adjusted']:
            return error_response(status=status.HTTP_400_BAD_REQUEST, data={}, msg="Not a valid status")
        debit_note_supplier_serializer = DebitNoteSupplierSerializer(data=request.data)
        if debit_note_supplier_serializer.is_valid():
            debit_note_supplier_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": 'Debit Note ID {} is generated'.format(debit_note_supplier_serializer.data['debit_note_number']),
                "data": debit_note_supplier_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
            # return Response(
            #     {"data": debit_note_supplier_serializer.data, "msg": 'Debit Note ID {} is generated'.format(
            #         debit_note_supplier_serializer.data['debit_note_number'])}, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Debit Note Supplier not Created",
            "data": debit_note_supplier_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        debit_note_supplier = get_or_none(DebitNoteSupplier, id=pk)
        if not isinstance(debit_note_supplier, DebitNoteSupplier):
            return Response({"error": "Debit Note Supplier does not exist"}, status=status.HTTP_404_NOT_FOUND)
        debit_note_supplier_serializer = DebitNoteSupplierSerializer(debit_note_supplier, data=request.data)

        if debit_note_supplier_serializer.is_valid():
            debit_note_supplier_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Debit Note Supplier Updated",
                "data": debit_note_supplier_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Debit Note Supplier not Updated",
            "data": debit_note_supplier_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        debit_note_supplier = get_or_none(DebitNoteSupplier, id=pk)
        if not isinstance(debit_note_supplier, DebitNoteSupplier):
            return Response({"error": "Debit Note Supplier does not exist"}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        if data.get('status') == 'approved' and debit_note_supplier.bookings.count() == 1:
            data['adjusted_amount'] = debit_note_supplier.debit_amount
            data['status'] = 'adjusted'
            data['adjusted_by'] = request.user.username
            data['adjusted_on'] = datetime.now()
            if Invoice.objects.filter(bookings__in=debit_note_supplier.bookings.all()).exists():
                data['invoice'] = Invoice.objects.filter(bookings__in=debit_note_supplier.bookings.all()).last().id
        debit_note_supplier_serializer = DebitNoteSupplierSerializer(
            instance=debit_note_supplier,
            data=data,
            partial=True
        )

        if debit_note_supplier_serializer.is_valid():
            debit_note_supplier_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Debit Note Supplier Updated",
                "data": debit_note_supplier_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Debit Note Supplier not Updated",
            "data": debit_note_supplier_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        debit_note_supplier = get_or_none(DebitNoteSupplier, id=pk)
        if isinstance(debit_note_supplier, DebitNoteSupplier):
            debit_note_supplier_serializer = DebitNoteSupplierSerializer(debit_note_supplier)
            return Response(debit_note_supplier_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Debit Note Supplier does not exist"}, status=status.HTTP_404_NOT_FOUND)


class CreditNoteCustomerDirectAdvanceListView(generics.ListAPIView):
    serializer_class = CreditNoteCustomerDirectAdvanceSerializer
    queryset = CreditNoteCustomerDirectAdvance.objects.all().order_by('-id')
    # pagination_class = StandardResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = CreditNoteCustomerDirectAdvanceFilters
    ordering_fields = ('id',)
    search_fields = (
        'id', 'credit_note_number', 'credit_amount', 'adjusted_amount', 'approved_by__username', 'approved_on',
        'adjusted_by__username', 'adjusted_on', 'remarks', 'status', 'rejected_by__username', 'rejected_on',
        'rejection_reason', 'created_by__username', 'created_on')

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


class CreditNoteCustomerDirectAdvanceViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on CreditNoteCustomerDirectAdvance
    """

    def create(self, request):
        request.data["changed_by"] = self.request.user.username
        request.data["created_by"] = self.request.user.username
        if 'status' in request.data and request.data['status'] in ['approved', 'rejected', 'partial', 'adjusted']:
            return error_response(status=status.HTTP_400_BAD_REQUEST, data={}, msg="Not a valid status")
        credit_note_customer_direct_advance_serializer = CreditNoteCustomerDirectAdvanceSerializer(data=request.data)
        if credit_note_customer_direct_advance_serializer.is_valid():
            credit_note_customer_direct_advance_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": 'Credit Note ID {} is generated'.format(
                    credit_note_customer_direct_advance_serializer.data['credit_note_number']),
                "data": credit_note_customer_direct_advance_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "CreditNoteCustomerDirectAdvance not Created",
            "data": credit_note_customer_direct_advance_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        credit_note_customer_direct_advance = get_or_none(CreditNoteCustomerDirectAdvance, id=pk)
        if not isinstance(credit_note_customer_direct_advance, CreditNoteCustomerDirectAdvance):
            return Response({"error": "CreditNoteCustomerDirectAdvance does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        credit_note_customer_direct_advance_serializer = CreditNoteCustomerDirectAdvanceSerializer(
            credit_note_customer_direct_advance, data=request.data)

        if credit_note_customer_direct_advance_serializer.is_valid():
            credit_note_customer_direct_advance_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "CreditNoteCustomerDirectAdvance Updated",
                "data": credit_note_customer_direct_advance_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "CreditNoteCustomerDirectAdvance not Updated",
            "data": credit_note_customer_direct_advance_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        credit_note_customer_direct_advance = get_or_none(CreditNoteCustomerDirectAdvance, id=pk)
        if not isinstance(credit_note_customer_direct_advance, CreditNoteCustomerDirectAdvance):
            return Response({"error": "CreditNoteCustomerDirectAdvance does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        data = request.data
        if data.get('status', None) == 'approved' and credit_note_customer_direct_advance.bookings.count() == 1:
            data['adjusted_amount'] = credit_note_customer_direct_advance.credit_amount
            data['status'] = 'adjusted'
            data['adjusted_by'] = request.user.username
            data['adjusted_on'] = datetime.now()
            if Invoice.objects.filter(bookings__in=credit_note_customer_direct_advance.bookings.all()).exists():
                data['invoice'] = Invoice.objects.filter(
                    bookings__in=credit_note_customer_direct_advance.bookings.all()).last().id
        credit_note_customer_direct_advance_serializer = CreditNoteCustomerDirectAdvanceSerializer(
            instance=credit_note_customer_direct_advance,
            data=data,
            partial=True
        )

        if credit_note_customer_direct_advance_serializer.is_valid():
            credit_note_customer_direct_advance_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "CreditNoteCustomerDirectAdvance Updated",
                "data": credit_note_customer_direct_advance_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "CreditNoteCustomerDirectAdvance not Updated",
            "data": credit_note_customer_direct_advance_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        credit_note_customer_direct_advance = get_or_none(CreditNoteCustomerDirectAdvance, id=pk)
        if isinstance(credit_note_customer_direct_advance, CreditNoteCustomerDirectAdvance):
            credit_note_customer_direct_advance_serializer = CreditNoteCustomerDirectAdvanceSerializer(
                credit_note_customer_direct_advance)
            return Response(credit_note_customer_direct_advance_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "CreditNoteCustomerDirectAdvance does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DebitNoteSupplierDirectAdvanceListView(generics.ListAPIView):
    serializer_class = DebitNoteSupplierDirectAdvanceSerializer
    queryset = DebitNoteSupplierDirectAdvance.objects.all().order_by('-id')
    # pagination_class = StandardResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = DebitNoteSupplierDirectAdvanceFilters
    ordering_fields = ('id',)
    search_fields = (
        'id', 'debit_note_number', 'debit_amount', 'adjusted_amount', 'approved_by__username', 'approved_on',
        'adjusted_by__username', 'adjusted_on', 'remarks', 'status', 'rejected_by__username', 'rejected_on',
        'rejection_reason', 'created_by__username', 'created_on')

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


class DebitNoteSupplierDirectAdvanceViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on DebitNoteSupplierDirectAdvance
    """

    def create(self, request):
        request.data["changed_by"] = self.request.user.username
        request.data["created_by"] = self.request.user.username
        if 'status' in request.data and request.data['status'] in ['approved', 'rejected', 'partial', 'adjusted']:
            return error_response(status=status.HTTP_400_BAD_REQUEST, data={}, msg="Not a valid status")
        debit_note_supplier_direct_advance_serializer = DebitNoteSupplierDirectAdvanceSerializer(data=request.data)
        if debit_note_supplier_direct_advance_serializer.is_valid():
            debit_note_supplier_direct_advance_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "DebitNoteSupplierDirectAdvance Created",
                "data": debit_note_supplier_direct_advance_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "DebitNoteSupplierDirectAdvance not Created",
            "data": debit_note_supplier_direct_advance_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        debit_note_supplier_direct_advance = get_or_none(DebitNoteSupplierDirectAdvance, id=pk)
        if not isinstance(debit_note_supplier_direct_advance, DebitNoteSupplierDirectAdvance):
            return Response({"error": "DebitNoteSupplierDirectAdvance does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        debit_note_supplier_direct_advance_serializer = DebitNoteSupplierDirectAdvanceSerializer(
            debit_note_supplier_direct_advance, data=request.data)

        if debit_note_supplier_direct_advance_serializer.is_valid():
            debit_note_supplier_direct_advance_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "DebitNoteSupplierDirectAdvance Updated",
                "data": debit_note_supplier_direct_advance_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "DebitNoteSupplierDirectAdvance not Updated",
            "data": debit_note_supplier_direct_advance_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        debit_note_supplier_direct_advance = get_or_none(DebitNoteSupplierDirectAdvance, id=pk)
        if not isinstance(debit_note_supplier_direct_advance, DebitNoteSupplierDirectAdvance):
            return Response({"error": "DebitNoteSupplierDirectAdvance does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        debit_note_supplier_direct_advance_serializer = DebitNoteSupplierDirectAdvanceSerializer(
            instance=debit_note_supplier_direct_advance,
            data=request.data,
            partial=True
        )

        if debit_note_supplier_direct_advance_serializer.is_valid():
            debit_note_supplier_direct_advance_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "DebitNoteSupplierDirectAdvance Updated",
                "data": debit_note_supplier_direct_advance_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "DebitNoteSupplierDirectAdvance not Updated",
            "data": debit_note_supplier_direct_advance_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        debit_note_supplier_direct_advance = get_or_none(DebitNoteSupplierDirectAdvance, id=pk)
        if isinstance(debit_note_supplier_direct_advance, DebitNoteSupplierDirectAdvance):
            debit_note_supplier_direct_advance_serializer = DebitNoteSupplierDirectAdvanceSerializer(
                debit_note_supplier_direct_advance)
            return Response(debit_note_supplier_direct_advance_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "DebitNoteSupplierDirectAdvance does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DataTablesFilterListView(generics.ListAPIView):
    serializer_class = DataTablesFilterSerializer
    queryset = DataTablesFilter.objects.order_by('-id')
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = DataTablesFilters
    ordering_fields = ('id',)
    search_fields = (
        'id', 'table_name', 'created_by__username', 'created_on')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "Successfull", "status_code": status.HTTP_200_OK, "msg": "DataTablesFilter List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class DataTablesFilterViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        instance = get_or_none(DataTablesFilter, id=pk)
        if isinstance(instance, DataTablesFilter):
            serializer = DataTablesFilterSerializer(instance=instance)
            return success_response(status=status.HTTP_200_OK, msg="data", data=serializer.data)
        return error_response(status=status.HTTP_404_NOT_FOUND, msg="Doesn't Exists", data={})
