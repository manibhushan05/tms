from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from rest_framework import status, viewsets
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

# UPDATES PAGE VIEWS
from employee.models import Employee
from fileupload.models import ChequeFile
from restapi.helper_api import verify_pod_data, my_uploaded_pod_data, manual_booking_id_list, check_booking_status, \
    get_booking_status_mapping_object
from restapi.models import BookingStatusesMapping, BookingStatusChain
from restapi.serializers.employee import EmployeeSerializer
from restapi.serializers.file_upload import ChequeFileSerializer
from restapi.serializers.team import InvoiceSerializer
from restapi.serializers.team import ManualBookingSerializer
from restapi.serializers.utils import IfscDetailSerializer
from restapi.service.booking import detailed_full_booking_page_data, \
    detailed_commission_booking_page_data
from restapi.service.credit_debit_note import approve_credit_note_customer_data, approve_debit_note_customer_data, \
    approve_credit_note_supplier_data, approve_debit_note_supplier_data, \
    approve_credit_note_customer_direct_advance_data
from restapi.service.invoices import get_invoice_data, get_comment_list, get_amount_data, \
    full_booking_invoice_data
from restapi.service.payments import pending_payments_data, pending_payment_adjustment_data
from restapi.service.trackvehicle import track_vehicles_data, track_vehicle_data
from restapi.utils import get_or_none
from sme.models import Sme
from team.models import LrNumber, ManualBooking, CreditNoteCustomer, CreditNoteSupplier, DebitNoteCustomer, \
    DebitNoteSupplier, CreditNoteCustomerDirectAdvance, Invoice
from utils.models import VehicleCategory, IfscDetail


class DownloadPaymentFilePage(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        return Response(status=status.HTTP_200_OK, template_name='team/download_outward_payment_file.html')


class ManualBookingCreatePageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def get_basic_full_booking(self, request):
        return Response(template_name='team/booking/fetch_full_booking_data_page.html')

    def get_confirm_booking(self, request):
        return Response(template_name='team/booking/confirm_booking_page.html')

    def get_detailed_full_booking(self, request):
        json_data = {k: request.GET.get(k) for k in request.GET.keys()}
        return Response(template_name='team/booking/full-booking.html', data=detailed_full_booking_page_data(json_data),
                        status=status.HTTP_200_OK)

    def get_detailed_full_booking_mb_id_based(self, request, pk):
        try:
            manual_booking = ManualBooking.objects.get(id=pk)
        except ManualBooking.DoesNotExist:
            return Response({"status": "failure",
                             "msg": "ManualBooking Doesn't exists",
                             "status_code": status.HTTP_400_BAD_REQUEST,
                             "data": {}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ManualBookingSerializer(instance=manual_booking)
        return Response(template_name='team/booking/detailed_lr_generation.html',
                        data=serializer.data, status=status.HTTP_200_OK)

    def get_basic_commission_booking(self, request):
        return Response(template_name='team/booking/fetch-commission-booking-data.html')

    def get_detailed_commission_booking(self, request):
        data = request.GET
        json_data = {k: data.get(k) for k in data.keys()}
        return Response(template_name='team/booking/commission-booking.html',
                        data=detailed_commission_booking_page_data(json_data))


class OutwardPaymentListPageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        return Response(template_name='team/payments/outward_payment_history.html')

    def get_payment_receipt(self, request):
        return Response(template_name='team/payments/supplier_payment_receipt.html', status=status.HTTP_200_OK)


class EmployeeProfilePageView(viewsets.ViewSet):
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def get(self, request):
        emp = get_or_none(Employee, username=User.objects.get(username=request.user.username))
        employee_serializer = EmployeeSerializer(instance=emp)
        return Response(template_name='team/employee/emp-profile.html', data=employee_serializer.data,
                        status=status.HTTP_200_OK)


class ChangePasswordPageView(viewsets.ViewSet):
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def get(self, request):
        return Response(template_name='team/employee/change-password.html', status=status.HTTP_200_OK)


class InwardPaymentListPageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        return Response(template_name='team/payments/inward_payment_history.html')


class OutwardPaymentPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request):
        return Response(status=status.HTTP_200_OK, template_name='team/payments/add_outward_payment.html')


class BookingStatusesMonitoringPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request):
        return Response(status=status.HTTP_200_OK, template_name='team/monitoring/senior_mgmt_booking_status.html')


class TaskStatusesMonitoringPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request):
        return Response(status=status.HTTP_200_OK, template_name='team/monitoring/senior_mgmt_task_status.html')


class PendingInwardPageView(viewsets.ViewSet):
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)

    def get(self, request):
        return Response(template_name='team/payments/add_received_payment.html')

    def unadjusted_list(self, request):
        return Response(template_name='team/payments/pending-payment-list.html', data={
            'pending_payments': pending_payments_data(),
        })

    def payment_adjustment(self, request):
        response = pending_payment_adjustment_data(data={
            'accept_choice': request.GET.get('accept_choice'),
            'payment_id': request.GET.get('payment_id'),
            'customer': request.GET.get('customer'),
            'tds': request.GET.get('tds'),
            'username': request.user.username,
        })
        if response['status'] != 200:
            return Response(status=response['status'], data={'msg': response['msg']})
        return Response(template_name='team/payments/payment-adjustment-page.html', status=status.HTTP_200_OK,
                        data=response['data'])


class ChequePageView(viewsets.ViewSet):
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)

    def create(self, request):
        return Response(template_name='', status=status.HTTP_200_OK)

    def uncredited_cheque_list(self, request):
        cheques = ChequeFile.objects.filter(resolved=False).order_by('cheque_date').values(
            'cheque_number', 'cheque_date', 'customer_name', 'amount', 'remarks').annotate(Count('cheque_number'))
        data = []
        for cheque in cheques:
            cheque_number = cheque['cheque_number']
            data.append({
                'id': ','.join([str(row.id) for row in ChequeFile.objects.filter(cheque_number=cheque_number)]),
                'cheque_number': cheque_number,
                'cheque_date': cheque['cheque_date'],
                'customer_name': cheque['customer_name'],
                'amount': cheque['amount'],
                'remarks': cheque['remarks'],
                'images': [{'url': row.s3_upload.public_url(), 'filename': row.cheque_number, } for row in
                           ChequeFile.objects.filter(cheque_number=cheque_number)]
            })
        return Response(template_name='team/payments/uncredited-cheques.html', status=status.HTTP_200_OK,
                        data={'cheques': data})


class InvoicePageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def list(self, request):
        return Response(template_name='team/invoices/invoice_list.html', status=status.HTTP_200_OK)

    def summary(self, request):
        return Response(template_name='team/invoices/invoice_summary_statement.html', status=status.HTTP_200_OK)

    def fetch_full_booking_invoice(self, request):
        return Response(template_name='team/invoices/fetch_full_booking_invoice_data.html', status=status.HTTP_200_OK)

    def full_booking_invoice(self, request):
        customer = get_or_none(Sme, id=request.GET.get('customer_to_be_billed'))
        return Response(template_name='team/invoices/full_booking_invoices.html',
                        data=full_booking_invoice_data(customer=customer), status=status.HTTP_200_OK)

    def fetch_commission_booking_invoice(self, request):
        return Response(template_name='team/invoices/fetch-commission-invoice.html', status=status.HTTP_200_OK)

    def commission_booking_invoice(self, request):
        customer = get_or_none(Sme, id=request.GET.get('customer_to_be_billed'))
        bookings = ManualBooking.objects.filter(id__in=request.GET.getlist('booking_id[]'))
        if not bookings.exists() or not isinstance(customer, Sme):
            return HttpResponseRedirect('/team/commission-invoice-data-page/')
        invoice_data = get_invoice_data(bookings, 'commission')
        comment_list = get_comment_list(bookings, invoice_data)
        return Response(template_name='team/invoices/commission_booking_invoice.html', status=status.HTTP_200_OK,
                        data={'booking_data': invoice_data, 'customer': customer,
                              'gst_liability': bookings.last().gst_liability,
                              'booking_ids': ','.join(map(str, bookings.values_list('id', flat=True))),
                              'comment_list': comment_list,
                              'invoice_amount_data': get_amount_data(bookings=bookings, booking_type='full'),
                              })


class LrNumberPageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def list(self, request):
        return Response(template_name='team/booking/download-lr.html', status=status.HTTP_200_OK)


class PODPageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def upload(self, request):
        return Response(template_name='', status=status.HTTP_200_OK)

    def list(self, request):
        return Response(template_name='team/booking/pod-list.html', status=status.HTTP_200_OK)

    def unverified_pod(self, request):
        return Response(template_name='team/documents/verify_pod.html', data={'bookings_data': verify_pod_data()},
                        status=status.HTTP_200_OK)

    def td_unverified_pod(self, request):
        return Response(template_name='team/documents/td_verify_pod.html', data={'bookings_data': verify_pod_data()},
                        status=status.HTTP_200_OK)

    def my_uploaded_pod(self, request):
        return Response(template_name='team/documents/uploaded-pod.html',
                        data={'bookings_data': my_uploaded_pod_data(user=request.user)}, status=status.HTTP_200_OK)


class AccountingSummaryPageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def get_placed_order_customer_summary(self, request):
        return Response(template_name='team/accounting/placed-order-customer-summary.html', status=status.HTTP_200_OK)

    def get_billed_customer_summary(self, request):
        return Response(template_name='team/accounting/billed-customer-summary.html', status=status.HTTP_200_OK)

    def get_supplier_summary(self, request):
        return Response(template_name='team/accounting/supplier-summary.html', status=status.HTTP_200_OK)

    def get_vehicle_summary(self, request):
        return Response(template_name='team/accounting/vehicle-summary.html', status=status.HTTP_200_OK)


class BankAccountPageView(viewsets.ViewSet):
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def fetch_ifsc(self, request):
        return Response(template_name='team/registrations/fetch-bank-details-using-ifsc.html',
                        status=status.HTTP_200_OK)

    def create(self, request):
        ifsc = get_or_none(IfscDetail, ifsc_code__iexact=request.GET.get('fetch_ifsc'))
        if isinstance(ifsc, IfscDetail):
            data = IfscDetailSerializer(ifsc).data
        else:
            data = {}
        return Response(template_name='team/registrations/register_beneficiary_bank_account.html',
                        status=status.HTTP_200_OK, data=data)

    def list(self, request):
        return Response(template_name='team/payments/beneficiary_list.html', status=status.HTTP_200_OK)


class TrackVehiclePageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def track_vehicles(self, request):
        return Response(template_name='team/track/track_vehicles.html', status=status.HTTP_200_OK,
                        data=track_vehicles_data())

    def track_vehicle(self, request):
        return Response(template_name='team/track/track_individual_vehicle.html', status=status.HTTP_200_OK,
                        data=track_vehicle_data(device_id=request.GET.get('gps_log_id')))


# FILE UPLOAD
class PODUploadPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request):
        lr_numbers = LrNumber.objects.filter(Q(datetime__date__gte=datetime.now().date() - timedelta(days=180)) & (
                Q(booking__pod_status='pending') | Q(booking__pod_status='rejected') | Q(
            booking__pod_status='unverified'))).order_by('-datetime').values(
            'id', 'lr_number')
        bookings = []
        for booking in ManualBooking.objects.filter(
                (Q(pod_status__iexact='pending') | Q(pod_status__iexact='rejected')) & (
                        Q(booking_id__istartswith='BROKER') | Q(booking_id__istartswith='AB'))).exclude(
            Q(booking_status='cancelled') | Q(deleted=True)):
            bookings.append({'booking_id': booking.booking_id})
        return Response({'lr_numbers': lr_numbers, 'bookings': bookings}, template_name='fileupload/pod_upload.html',
                        status=status.HTTP_200_OK)


class ChequeFilePageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request):
        cheques = ChequeFile.objects.filter(resolved=False).exclude(deleted=True).order_by('-cheque_date')
        cheques_serializer = ChequeFileSerializer(cheques, many=True)
        return Response({"data": cheques_serializer.data}, status=status.HTTP_200_OK,
                        template_name="team/payments/uncredited-cheques.html")


class ManualBookingListPage(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get_partial_booking(self, request):
        return Response(status=status.HTTP_200_OK, template_name='team/booking/partial_booking.html')

    def get_full_booking(self, request):
        return Response(status=status.HTTP_200_OK, template_name='team/booking/booking-archive.html')

    def get_generate_lr(self, request):
        return Response(status=status.HTTP_200_OK, template_name='team/booking/booking_status_loaded.html')

    def get_bookings_pay_advance(self, request):
        return Response(status=status.HTTP_200_OK, template_name='team/booking/bookings_pay_advance.html')


class BookingMISPage(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        return Response(template_name='team/booking/mis-booking.html', status=status.HTTP_200_OK)


class UpdateContractBookingPage(viewsets.ViewSet):
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)

    def get(self, request):
        bookings = ManualBooking.objects.filter(Q(total_amount_to_company=0)).filter(billing_type='contract').exclude(
            Q(deleted=True) | Q(booking_status='cancelled'))
        data = []
        for booking in bookings:
            data.append({
                'id': booking.id,
                'booking_id': booking.booking_id,
                'shipment_date': booking.shipment_date.strftime('%d-%b-%Y') if booking.shipment_date else '',
                'lr_numbers': '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                'customer_name': booking.company.get_name() if booking.company else '',
                'origin': booking.from_city,
                'destination': booking.to_city,
                'weight': booking.charged_weight,
                'rate_id': '{}_{}'.format('rate', booking.booking_id),
                'amount_id': '{}_{}'.format('amount', booking.booking_id)
            })
        return Response(template_name='team/booking/update-contract-bookings-rate.html', status=status.HTTP_200_OK,
                        data={'bookings': data, 'id': ','.join(map(str, bookings.values_list('id', flat=True)))})


# UPDATE PAGE VIEWs


class PayBalanceBookingHistoryPage(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        return Response(template_name='team/payments/pay_balance_booking_history.html', status=status.HTTP_200_OK)


class RaiseInvoiceBookingHistoryPage(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        return Response(template_name='team/invoices/raise_invoice_booking_history.html', status=status.HTTP_200_OK)


class UploadInvoiceSentReceiptPage(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        booking_ids = manual_booking_id_list(user=request.user)
        invoice_raised_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='invoice_raised').exclude(
            Q(deleted=True) | Q(booking_stage='reverted')). \
            values_list('manual_booking_id', flat=True)
        party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='party_invoice_sent').exclude(
            Q(deleted=True) | Q(booking_stage='reverted')). \
            values_list('manual_booking_id', flat=True)
        invoice_not_sent_bookings = [x for x in invoice_raised_bookings if x not in party_invoice_sent_bookings]
        bookings = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_not_sent_bookings). \
            filter(invoice_status='invoice_raised').exclude(billing_type='contract')
        invoices = Invoice.objects.filter(bookings__in=bookings,
                                          date__gte=datetime.now().date() - timedelta(days=365)).distinct()
        # invoices = Invoice.objects.filter(date__gte=datetime.now() - timedelta(days=3)).exclude(deleted=True)
        serializer = InvoiceSerializer(instance=invoices, many=True)
        return Response(template_name='team/invoices/invoice_sent_receipt.html', status=status.HTTP_200_OK,
                        data={'data': serializer.data})


class ConfirmInvoiceSentPage(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        booking_ids = manual_booking_id_list(user=request.user)
        party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='party_invoice_sent').exclude(
            Q(deleted=True) | Q(booking_stage='reverted')). \
            values_list('manual_booking_id', flat=True)
        invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='invoice_confirmed').exclude(
            Q(deleted=True) | Q(booking_stage='reverted')). \
            values_list('manual_booking_id', flat=True)
        invoice_not_confirmed_bookings = [x for x in party_invoice_sent_bookings if x not in invoice_confirmed_bookings]
        bookings = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_not_confirmed_bookings). \
            filter(invoice_status='invoice_sent').exclude(billing_type='contract')
        invoices = Invoice.objects.filter(bookings__in=bookings,
                                          date__gte=datetime.now().date() - timedelta(days=365)).distinct()
        # invoices = Invoice.objects.filter(date__gte=datetime.now() - timedelta(days=3)).exclude(deleted=True)
        serializer = InvoiceSerializer(instance=invoices, many=True)
        data = self.add_booking_status_mapping_info(serializer.data)
        return Response(template_name='team/invoices/confirm_sent_invoice.html', status=status.HTTP_200_OK,
                        data={'data': data})

    def add_booking_status_mapping_info(self, data):
        for inv in data:
            inv['invoice_booking_details'] = []
            inv_bookings = Invoice.objects.get(id=inv['id']).bookings.all()
            for booking in inv_bookings:
                bsm_details = {}
                booking_invoice_confirmed = check_booking_status(booking, 'party_invoice_sent')
                booking_status_mapping_id = None
                booking_status_chain_id = None
                booking_status_mapping_booking_stage = None
                if booking_invoice_confirmed:
                    booking_status_mapping_object = get_booking_status_mapping_object(booking, 'party_invoice_sent')
                    try:
                        booking_status_chain_id = BookingStatusChain.objects.get(
                            booking_status__status='party_invoice_sent').id
                    except BookingStatusChain.DoesNotExist:
                        booking_status_chain_id = None
                    if booking_status_mapping_object:
                        booking_status_mapping_id = booking_status_mapping_object.id
                        booking_status_mapping_booking_stage = booking_status_mapping_object.booking_stage
                bsm_details['booking_id'] = booking.id
                bsm_details['booking_status_mapping_id'] = booking_status_mapping_id
                bsm_details['booking_status_chain_id'] = booking_status_chain_id
                bsm_details['booking_status_mapping_booking_stage'] = booking_status_mapping_booking_stage
                inv['invoice_booking_details'].append(bsm_details)
        return data


class ProcessPaymentEnetPage(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        return Response(template_name='team/payments/process_payment_page.html', status=status.HTTP_200_OK)


class ReconcilePaymentPage(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request):
        return Response(template_name='team/payments/reconcile_payment_page.html', status=status.HTTP_200_OK)


class OwnerListPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/owner_list.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class OwnerVehicleListPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/vehicle-list.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class SmeListPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/customer-archive.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class SupplierListPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/supplier-list.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class DriverListPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/driver-list-page.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


# REGISTER PAGE VIEWS


class VehicleRegisterPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request):
        vehicle_categories = [
            {'id': vehicle_category.id, 'vehicle_type': vehicle_category.vehicle_type,
             'capacity': vehicle_category.capacity}
            for vehicle_category in VehicleCategory.objects.all()
        ]
        body_type_choices = (
            ('open', 'Open'),
            ('closed', 'Closed'),
            ('semi', 'Semi'),
            ('half', 'Half'),
            ('containerized', 'Containerized'),
        )
        gps_enable_choices = (
            ('yes', 'Yes'),
            ('no', 'No')
        )

        return Response({
            'vehicle_categories': vehicle_categories,
            'body_type_choices': body_type_choices,
            'gps_enable_choices': gps_enable_choices
        }, template_name='team/registrations/register_vehicle.html', status=status.HTTP_200_OK)


class OwnerRegisterPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/register_owner.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class SmeRegisterPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/register-customer.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class SupplierRegisterPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/register-supplier.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class DriverRegisterPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/registrations/register-driver.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


# CREDIT DEBIT NOTE


class IssueCreditDebitNotePageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/credit_debit_note/issue/issue-credit-debit-note.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class IssueCreditNoteCustomerPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/credit_debit_note/issue/issue_cnc.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class IssueCreditNoteSupplierPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/credit_debit_note/issue/issue_cns.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class IssueDebitNoteCustomerPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/credit_debit_note/issue/issue_dnc.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class IssueDebitNoteSupplierPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/credit_debit_note/issue/issue_dns.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class IssueCreditNoteCustomerDirectAdvancePageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/credit_debit_note/issue/issue_cnca.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class ApproveCreditDebitNotePageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/credit_debit_note/approve/approve_credit_debit_note_page.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK, data={
            'cnc': approve_credit_note_customer_data(),
            'dnc': approve_debit_note_customer_data(),
            'cns': approve_credit_note_supplier_data(),
            'dns': approve_debit_note_supplier_data(),
            'cnca': approve_credit_note_customer_direct_advance_data(),
        })


class ApproveCreditNoteCustomerPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request):
        data = []
        for row in CreditNoteCustomer.objects.filter(status='pending').exclude(deleted=True).order_by('created_on'):
            data.append({
                'cnc_id': row.id,
                'customer': row.customer.get_name() if row.customer else '-',
                'bookings': '\n'.join(
                    [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id,
                                 booking.booking_id)
                     for booking in row.bookings.all()]),
                'invoice': row.invoice.invoice_number if row.invoice else '-',
                'amount': row.credit_amount,
                'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
                'credit_note_number': row.credit_note_number,
                'created_by': row.created_by.username if row.created_by else '-',
                'credit_note_reason': row.reason.name if row.reason else '-',
                'remarks': row.remarks,
                'approve_cnc_form': 'approve_cnc_form_{}'.format(row.id),
                'approve_cnc_btn': 'approve_cnc_btn_{}'.format(row.id),
                'reject_cnc_btn': 'reject_cnc_btn_{}'.format(row.id),
                'input_reject_cnc_remarks': 'input_reject_cnc_remarks_{}'.format(row.id),
                'btn_status': 'btn_status_{}'.format(row.id),
                'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
                'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
            })
        return Response({'data': data}, template_name='team/credit_debit_note/approve/cnc.html',
                        status=status.HTTP_200_OK)


class ApproveCreditNoteSupplierPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request):
        data = []
        for row in CreditNoteSupplier.objects.filter(status='pending').exclude(deleted=True).order_by('created_on'):
            data.append({
                'cnc_id': row.id,
                'broker': row.broker.get_name() if row.broker else '-',
                'bookings': '\n'.join(
                    [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id,
                                 booking.booking_id)
                     for booking in row.bookings.all()]),
                'invoice': row.invoice.invoice_number if row.invoice else '-',
                'amount': row.credit_amount,
                'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
                'credit_note_number': row.credit_note_number,
                'created_by': row.created_by.username if row.created_by else '-',
                'credit_note_reason': row.reason.name if row.reason else '-',
                'remarks': row.remarks,
                'approve_cns_form': 'approve_cns_form_{}'.format(row.id),
                'approve_cns_btn': 'approve_cns_btn_{}'.format(row.id),
                'reject_cns_btn': 'reject_cns_btn_{}'.format(row.id),
                'input_reject_cns_remarks': 'input_reject_cns_remarks_{}'.format(row.id),
                'btn_status': 'btn_status_{}'.format(row.id),
                'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
                'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
            })
        return Response({'data': data}, template_name='team/credit_debit_note/approve/cns.html',
                        status=status.HTTP_200_OK)


class ApproveDebitNoteCustomerPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request):
        data = []
        for row in DebitNoteCustomer.objects.filter(status='pending').exclude(deleted=True).order_by('created_on'):
            data.append({
                'dnc_id': row.id,
                'customer': row.customer.get_name() if row.customer else '-',
                'bookings': '\n'.join(
                    [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id,
                                 booking.booking_id)
                     for booking in row.bookings.all()]),
                'invoice': row.invoice.invoice_number if row.invoice else '-',
                'amount': row.debit_amount,
                'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
                'debit_note_number': row.debit_note_number,
                'created_by': row.created_by.username if row.created_by else '-',
                'debit_note_reason': row.reason.name if row.reason else '-',
                'remarks': row.remarks,
                'approve_dnc_form': 'approve_dnc_form_{}'.format(row.id),
                'approve_dnc_btn': 'approve_dnc_btn_{}'.format(row.id),
                'reject_dnc_btn': 'reject_dnc_btn_{}'.format(row.id),
                'input_reject_dnc_remarks': 'input_reject_dnc_remarks_{}'.format(row.id),
                'btn_status': 'btn_status_{}'.format(row.id),
                'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
                'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
            })

        return Response({'data': data}, template_name='team/credit_debit_note/approve/dnc.html',
                        status=status.HTTP_200_OK)


class ApproveDebitNoteSupplierPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/credit_debit_note/issue/issue_dns.html'

    def get(self, request):
        data = []
        for row in DebitNoteSupplier.objects.filter(status='pending').exclude(deleted=True).order_by('created_on'):
            data.append({
                'cnc_id': row.id,
                'broker': row.broker.get_name() if row.broker else '-',
                'bookings': '\n'.join(
                    [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id,
                                 booking.booking_id)
                     for booking in row.bookings.all()]),
                'invoice': row.invoice.invoice_number if row.invoice else '-',
                'amount': row.debit_amount,
                'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
                'credit_note_number': row.debit_note_number,
                'created_by': row.created_by.username if row.created_by else '-',
                'credit_note_reason': row.reason.name if row.reason else '-',
                'remarks': row.remarks,
                'approve_dns_form': 'approve_dns_form_{}'.format(row.id),
                'approve_dns_btn': 'approve_dns_btn_{}'.format(row.id),
                'reject_dns_btn': 'reject_dns_btn_{}'.format(row.id),
                'input_reject_dns_remarks': 'input_reject_dns_remarks_{}'.format(row.id),
                'btn_status': 'btn_status_{}'.format(row.id),
                'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
                'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
            })
        return Response({'data': data}, template_name='team/credit_debit_note/approve/dns.html',
                        status=status.HTTP_200_OK)


class ApproveCreditNoteCustomerDirectAdvancePageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'team/credit_debit_note/issue/issue_cnca.html'

    def get(self, request):
        data = []
        for row in CreditNoteCustomerDirectAdvance.objects.filter(status='pending').exclude(deleted=True).order_by(
                'created_on'):
            data.append({
                'cnc_id': row.id,
                'broker': row.broker.get_name() if row.broker else '-',
                'customer': row.customer.get_name() if row.customer else '-',
                'bookings': '\n'.join(
                    [format_html('''<a href="/team/booking-edit/?booking_id={}">{}</a>''', booking.id,
                                 booking.booking_id)
                     for booking in row.bookings.all()]),
                'invoice': row.invoice.invoice_number if row.invoice else '-',
                'amount': row.credit_amount,
                'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
                'credit_note_number': row.credit_note_number,
                'created_by': row.created_by.username if row.created_by else '-',
                'credit_note_reason': row.reason.name if row.reason else '-',
                'remarks': row.remarks,
                'approve_cnca_form': 'approve_cnca_form_{}'.format(row.id),
                'approve_cnca_btn': 'approve_cnca_btn_{}'.format(row.id),
                'reject_cnca_btn': 'reject_cnca_btn_{}'.format(row.id),
                'input_reject_cnca_remarks': 'input_reject_cnca_remarks_{}'.format(row.id),
                'btn_status': 'btn_status_{}'.format(row.id),
                'div_rejection_remarks': 'div_rejection_remarks_{}'.format(row.id),
                'div_rejection_line': 'div_rejection_line_{}'.format(row.id),
            })
        return Response({'data': data}, template_name='team/credit_debit_note/approve/cnca.html',
                        status=status.HTTP_200_OK)


class MobilePageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def dashboard(self, request):
        return Response(template_name='mobile/dashboard.html', status=status.HTTP_200_OK)


class DocumentUploadPageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def pod(self, request):
        lr_numbers = LrNumber.objects.filter(Q(datetime__date__gte=datetime.now().date() - timedelta(days=180)) & (
                Q(booking__pod_status='pending') | Q(booking__pod_status='rejected') | Q(
            booking__pod_status='unverified'))).order_by('-datetime').values(
            'id', 'lr_number')
        bookings = []
        for booking in ManualBooking.objects.filter(
                (Q(pod_status__iexact='pending') | Q(pod_status__iexact='rejected')) & (
                        Q(booking_id__istartswith='BROKER') | Q(booking_id__istartswith='AB'))).exclude(
            Q(booking_status='cancelled') | Q(deleted=True)):
            bookings.append({'booking_id': booking.booking_id})
        return Response(template_name='fileupload/pod_upload.html', status=status.HTTP_200_OK)

    def vehicle(self, request):
        return Response(template_name='fileupload/upload_vehicle_documents.html', status=status.HTTP_200_OK)

    def supplier(self, request):
        return Response(template_name='fileupload/upload_supplier_documents.html', status=status.HTTP_200_OK)

    def weighing_slip(self, request):
        return Response(template_name='fileupload/weighing_slip_upload.html', status=status.HTTP_200_OK)

    def owner(self, request):
        return Response(template_name='fileupload/upload_owner_documents.html', status=status.HTTP_200_OK)

    def driver(self, request):
        return Response(template_name='fileupload/upload_driver_documents.html', status=status.HTTP_200_OK)

    def cheque(self, request):
        return Response(template_name='fileupload/upload_cheque.html', status=status.HTTP_200_OK)

    def invoice_receipt(self, request):
        return Response(template_name='fileupload/invoice_receipt.html', status=status.HTTP_200_OK)
