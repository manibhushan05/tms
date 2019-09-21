from datetime import datetime
from django.db.models import QuerySet
from rest_framework import generics, status
from rest_framework.response import Response
from broker.models import Broker
from fms.trip_history import supplier_booking_data
from restapi.models import UserCategory
from restapi.serializers.team import ManualBookingSerializer
from sme.models import Sme
from team.models import ManualBooking
from owner.models import Vehicle
from fms.views import get_or_none
from owner.vehicle_util import compare_format, display_format


class BookingsDataListView(generics.ListAPIView):
    queryset = ManualBooking.objects.order_by('-shipment_date').exclude(booking_status__icontains='cancelled')
    serializer_class = ManualBookingSerializer

    def get_queryset(self):
        queryset = self.queryset
        return_response = {"status": "failure", "queryset": {"msg": "Booking Does Not Exist"},
                           "status_code": status.HTTP_400_BAD_REQUEST}
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
            category_id = self.request.query_params.get('category_id', None)
            vehicle_id = self.request.query_params.get('vehicle_id', None)
            for key, value in self.request.GET.items():
                if key not in ['category_id', 'vehicle_id']:
                    return_response['queryset'] = {"msg": "only category id and vehicle id is supported"}
                    return return_response
            if category_id is None:
                return_response['queryset'] = {"msg": "category_id is required field"}
                return return_response
            if vehicle_id is not None:
                # filter bookings only on vehicle id
                vehicle = get_or_none(Vehicle, id=vehicle_id)
                if not vehicle_id.isnumeric():
                    return_response = {"status": "failure", "queryset": {"msg": "Vehicle id should be a number"},
                                       "status_code": status.HTTP_400_BAD_REQUEST}
                    return return_response
                if not vehicle:
                    return_response['queryset'] = {"msg": "Vehicle Does not exist"}
                    return return_response
                queryset = queryset.filter(lorry_number__in=[display_format(compare_format(vehicle.vehicle_number))])
                if not queryset:
                    return return_response
                return_response['queryset'] = queryset
                return_response['status'] = 'success'
                return return_response

            # filter bookings on user category
            if not category_id.isnumeric():
                return_response = {"status": "failure", "queryset": {"msg": "Category id should be a number"},
                                   "status_code": status.HTTP_400_BAD_REQUEST}
                return return_response
            try:
                user_category = UserCategory.objects.get(id=category_id)
            except UserCategory.DoesNotExist:
                return_response['queryset']['msg'] = 'User Category Does Not Exist'
                return return_response
            if user_category.category == 'Customer':
                return self.get_customer_bookings_data(queryset)
            elif user_category.category == 'Supplier':
                return self.get_supplier_bookings_data(queryset)
            return_response['queryset']['msg'] = 'User Category Is Not Supported'
            return return_response
        else:
            return return_response

    def get_customer_bookings_data(self, queryset):
        return_response = {"status": "failure", "queryset": {"msg": "Booking Does Not Exist"},
                           "status_code": status.HTTP_400_BAD_REQUEST}
        try:
            customer = Sme.objects.get(name=self.request.user)
        except Sme.DoesNotExist:
            return_response['queryset']['msg'] = 'Customer Does Not Exist'
            return return_response
        queryset = queryset.filter(company=customer, shipment_date__gte=datetime(2017, 12, 1).date())
        if not queryset:
            return return_response
        return_response['queryset'] = queryset
        return_response['status'] = 'success'
        return return_response

    def get_supplier_bookings_data(self, queryset):
        return_response = {"status": "failure", "queryset": {"msg": "Booking Does Not Exist"},
                           "status_code": status.HTTP_400_BAD_REQUEST}
        try:
            broker = Broker.objects.get(name=self.request.user)
        except Broker.DoesNotExist:
            return_response['queryset']['msg'] = 'Supplier Does Not Exist'
            return return_response
        queryset = queryset.filter(supplier=broker, shipment_date__gte=datetime(2017, 12, 1).date())
        if not queryset:
            return return_response
        return_response['queryset'] = queryset
        return_response['status'] = 'success'
        return return_response

    def get(self, request, *args, **kwargs):
        q_set = self.get_queryset()
        if q_set['status'] == 'failure':
            response = {"status": "failure", "msg": q_set['queryset']['msg'], "data": {},
                        "status_code": status.HTTP_200_OK}
            return Response(response, status=q_set['status_code'])
        else:
            queryset = self.filter_queryset(q_set['queryset'])

        page = self.paginate_queryset(queryset)
        if page is not None:
            data = supplier_booking_data(bookings=page)
            response = {"status": "success", "msg": "bookings data", "http_status": status.HTTP_200_OK, "data": data,
                        "status_code": status.HTTP_200_OK}
            return self.get_paginated_response(response)

        data = supplier_booking_data(bookings=page)
        response = {"status": "success", "msg": "bookings data", "data": data, "status_code": status.HTTP_200_OK}
        return Response(response, status=status.HTTP_200_OK)
