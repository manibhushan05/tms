from django.db.models import Q
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, filters, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils import get_or_none
from fileupload.models import PODFile
from restapi.filter.team import InvoiceFilters
from restapi.pagination import CustomeDatatablesPaginator
from restapi.search import CustomSearch
from restapi.serializers.file_upload import PODFileSerializer
from restapi.serializers.team import InvoiceSerializer
from sme.filters import BookingFilters
from sme.models import Sme, SmeSummary
from sme.serializer import BookingSerializer
from team.models import ManualBooking, Invoice


class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    pagination_class = CustomeDatatablesPaginator
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('id',)
    filter_class = BookingFilters

    search_fields = ('lr_numbers__lr_number',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.distinct()
        total_weight = 0
        total_amount = 0
        total_balance = 0
        weighted_avg_rate = 0
        for booking in queryset:
            total_amount += booking.customer_amount
            total_balance += booking.balance_for_customer
            total_weight += booking.charged_weight
            weighted_avg_rate += booking.party_rate * booking.charged_weight
        try:
            weighted_avg_rate = weighted_avg_rate // total_weight
        except ZeroDivisionError:
            weighted_avg_rate = 0

        summary = {'number_of_bookings': queryset.count(), 'total_weight': total_weight, 'total_amount': total_amount,
                   'total_balance': total_balance, 'weighted_avg_rate': weighted_avg_rate}

        data = {"status": "Success", "status_code": status.HTTP_200_OK, "msg": "Bookings List", 'summary': summary}
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)
        data["data"] = serializer.data
        return Response(data)

    def get_serializer_class(self):
        return BookingSerializer

    def get_queryset(self):
        sme = get_or_none(Sme, name=self.request.user)
        if isinstance(sme, Sme):
            return ManualBooking.objects.filter(company=sme).exclude(Q(booking_status='cancelled') | Q(deleted=True))
        return ManualBooking.objects.none()


class InvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    filter_backends = (CustomSearch, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = InvoiceFilters
    ordering_fields = ('id', 'date')
    search_fields = (
        'id', 'bookings__lr_numbers__lr_number', 'invoice_number', 'total_amount')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        summary = {
            "aaho_poc": "",
            "customer_code": "",
            "customer_name": "",
            "on_account_payment": 0,
            "outstanding_balance": {
                "billed_amount": 0,
                "total_amount": 0
            },
            "pending_payments": {
                "amount_0_30_days": 0,
                "amount_30_60_days": 0,
                "amount_60_90_days": 0,
                "amount_90_180_days": 0,
                "amount_gt_180_days": 0
            },
            "total_amount": 0,
            "unbilled_amount": 0
        }
        customer = get_or_none(Sme, name=self.request.user)
        if isinstance(customer, Sme):
            sme_summary = get_or_none(SmeSummary, sme=customer)
            if isinstance(sme_summary, SmeSummary) and sme_summary.placed_order_accounting_summary:
                summary = sme_summary.placed_order_accounting_summary

        data = {"status": "Success", "status_code": status.HTTP_200_OK, "msg": "Invoices List", 'summary': summary}
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)
        data["data"] = serializer.data
        return Response(data)

    def get_queryset(self):
        customer = get_or_none(Sme, name=self.request.user)
        if isinstance(customer, Sme):
            return Invoice.objects.filter(customer_fk=customer).exclude(deleted=True).distinct()
        return Invoice.objects.none()


class DashboardPageView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'sme/bookings.html'

    def post(self, request):
        return Response(status=status.HTTP_200_OK)

    def perform_authentication(self, request):
        try:
            token = Token.objects.get(key=request.stream.POST['token'])
            request.user = token.user
        except (Token.DoesNotExist, AttributeError) as e:
            raise PermissionDenied


class CustomerPageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def bookings(self, request):
        return Response(status=status.HTTP_200_OK, template_name='sme/bookings.html')

    def contact_us(self, request):
        return Response(status=status.HTTP_200_OK, template_name='sme/contact_us.html')

    def policy(self, request):
        return Response(status=status.HTTP_200_OK, template_name='sme/policy.html')

    def change_password(self, request):
        return Response(status=status.HTTP_200_OK, template_name='sme/change-password.html')

    def invoices(self, request):
        return Response(status=status.HTTP_200_OK, template_name='sme/invoices.html')


def customer_login_page(request):
    return render(request=request, template_name='sme/login.html')
