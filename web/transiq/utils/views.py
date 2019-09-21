from __future__ import division, print_function
import json

from django.db.models import Q
from django.http import HttpResponse

from api.decorators import authenticated_user
from api.utils import to_int
from broker.models import Broker
from driver.models import Driver
from employee.models import Employee
from owner.models import Owner, Vehicle
from owner.vehicle_util import display_format
from sme.models import Sme
from team.models import ManualBooking, LrNumber, Invoice
from utils.models import City, VehicleCategory, AahoOffice, State


def city_data(request):
    cities = City.objects.all()
    rows = to_int(request.GET.get('page'))
    search_value = request.GET.get('search')
    if search_value:
        cities = City.objects.filter(
            Q(name__icontains=search_value) | Q(state__name__icontains=search_value) | Q(code__icontains=search_value))
    data = []
    for city in cities.order_by('name')[:rows]:
        data.append({
            'id': city.id,
            'text': '{}, {}, {}'.format(city.name, city.code, city.state.name if city.state else '')
        })
    data = {
        'results': data,
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def state_data(request):
    states = State.objects.all()
    rows = to_int(request.GET.get('page'))
    search_value = request.GET.get('search')
    if search_value:
        states = State.objects.filter(
            Q(name__icontains=search_value))
    data = []
    for state in states.order_by('name')[:rows]:
        data.append({
            'id': state.id,
            'text': '{}'.format(state.name)
        })
    data = {
        'results': data,
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def customers_data(request):
    customers = Sme.objects.all()
    rows = to_int(request.GET.get('page'))
    search_value = request.GET.get('search')
    if search_value:
        customers = Sme.objects.filter(
            Q(name__profile__name__icontains=search_value) | Q(company_code__iexact=search_value)
        )
    data = []

    for customer in customers[:rows]:
        data.append({
            'id': customer.id,
            'text': '{}, {}'.format(customer.get_name(), customer.company_code),
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def employees_data(request):
    employees = Employee.objects.exclude(status__iexact='inactive')
    rows = to_int(request.GET.get('page'))
    search_value = request.GET.get('search')
    if search_value:
        employees = Employee.objects.filter(
            Q(username__profile__name__icontains=search_value) | Q(username__profile__phone__icontains=search_value)
        ).exclude(status__iexact='inactive')
    data = []
    for employee in employees[:rows]:
        data.append({
            'id': employee.id,
            'text': '{}, {}'.format(employee.emp_name(), employee.emp_phone()),
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def owners_data(request):
    rows = to_int(request.GET.get('page'))
    owners = Owner.objects.exclude(Q(name__profile__name=None))

    search_value = request.GET.get('search')
    if search_value:
        owners = Owner.objects.filter(
            Q(name__profile__name__icontains=search_value) | Q(name__profile__name__icontains=search_value)).exclude(
            Q(name__profile__name=None))
    data = []
    for owner in owners[:rows]:
        data.append({
            'id': owner.id,
            'text': '{}, {}'.format(owner.get_name(), owner.get_phone())
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def brokers_data(request):
    rows = to_int(request.GET.get('page'))
    search_value = request.GET.get('search')
    brokers = Broker.objects.exclude(Q(name__profile__name=None))
    if search_value:
        brokers = Broker.objects.filter(
            Q(name__profile__name__icontains=search_value) | Q(name__profile__name__icontains=search_value)).exclude(
            Q(name__profile__name=None))
    data = []
    for broker in brokers[:rows]:
        data.append({
            'id': broker.id,
            'text': '{}, {}'.format(broker.get_name(), broker.get_phone())
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def vehicles_data(request):
    rows = to_int(request.GET.get('page'))
    search_value = request.GET.get('search')
    vehicles = Vehicle.objects.exclude(Q(vehicle_number=None))
    if search_value:
        vehicles = Vehicle.objects.filter(
            Q(vehicle_number__icontains=''.join(ch.lower() for ch in search_value if ch.isalnum()))).exclude(
            Q(vehicle_number=None))
    data = []
    for vehicle in vehicles[:rows]:
        data.append({
            'id': vehicle.id,
            'text': '{}'.format(display_format(vehicle.vehicle_number))
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def drivers_data(request):
    rows = to_int(request.GET.get('page'))
    search_value = request.GET.get('search')
    drivers = Driver.objects.all()
    if search_value:
        drivers = Driver.objects.filter(Q(name__icontains=search_value) | Q(phone__icontains=search_value)).exclude(
            Q(phone=None))
    data = []
    for driver in drivers.order_by('-name')[:rows]:
        data.append({
            'id': driver.id,
            'text': '{}, {}'.format(driver.name if driver.name else '', driver.phone)
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def booking_id_lr_data(request):
    rows = to_int(request.GET.get('page'))
    search_value = request.GET.get('search')
    bookings = ManualBooking.objects.exclude(booking_status__iexact='cancelled').order_by('-id', '-shipment_date')
    if search_value:
        bookings = ManualBooking.objects.filter(Q(booking_id__icontains=search_value) | Q(
            id__in=LrNumber.objects.filter(lr_number__icontains=search_value).values_list('booking__id', flat=True))
                                                ).exclude(booking_status__iexact='cancelled').order_by('-id',
                                                                                                       '-shipment_date')
    data = []
    for booking in bookings[:rows]:
        data.append({
            'id': booking.id,
            'text': '{}( {} )'.format(booking.booking_id, ', '.join(
                booking.lr_numbers.values_list(
                    'lr_number', flat=True))) if booking.lr_numbers.exists() else booking.booking_id
        })
    data = {
        'results': data
    }
    print(data)
    return HttpResponse(json.dumps(data), content_type='application/json')


def invoice_number_data(request):
    rows = to_int(request.GET.get('page'))
    search_key = request.GET.get('search')
    tbb_invoices = Invoice.objects.order_by('-id', '-date')
    if search_key:
        tbb_invoices = Invoice.objects.filter(invoice_number__iexact=search_key).order_by('-id', '-date')
    data = []
    for invoice in tbb_invoices[:rows]:
        data.append({
            'id': invoice.invoice_number,
            'text': invoice.invoice_number
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def vehicle_categories_data(request):
    rows = to_int(request.GET.get('page'))
    search_key = request.GET.get('search')
    vehicle_categories = VehicleCategory.objects.all()
    if search_key:
        vehicle_categories = VehicleCategory.objects.filter(
            Q(vehicle_type__icontains=search_key) | Q(capacity__icontains=search_key) | Q(
                truck_body_type__icontains=search_key))
    data = []
    for vehicle_category in vehicle_categories.order_by('vehicle_type')[:rows]:
        data.append({
            'id': vehicle_category.id,
            'text': vehicle_category.vehicle_category
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def aaho_office_data(request):
    rows = to_int(request.GET.get('page'))
    search_value = request.GET.get('search')
    aaho_offices = AahoOffice.objects.all()
    if search_value:
        aaho_offices = AahoOffice.objects.filter(
            Q(branch_name__icontains=search_value) | Q(branch__name__icontains=search_value)
            | Q(branch__code__icontains=search_value))

    data = []
    for aaho_office in aaho_offices.order_by('branch_name')[:rows]:
        data.append({
            'id': aaho_office.id,
            'text': '{}'.format(aaho_office.branch_name)
        })
    data = {
        'results': data,
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
