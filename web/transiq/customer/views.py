from datetime import datetime

from django.contrib.auth import authenticate, login, logout

from api.decorators import api_post, api_get
from api.helper import json_response, json_400_incorrect_use, json_401_wrong_credentials, \
    json_401_inactive_user
from api.utils import get_or_none

from customer.decorators import authenticated_user
from customer.sql import get_ranking_results
from fms.trip_history import supplier_booking_data, customer_booking_data
from sme.models import Sme, ContactDetails
from team.models import ManualBooking
from transaction.models import UserVendor
from utils.models import City, VehicleCategory, Address


@api_get
def login_status(request):
    if request.user and request.user.is_authenticated:
        if request.user.is_active:
            return json_response({'status': 'success', 'state': 'logged_in', 'msg': 'user logged in and active'})
        else:
            return json_response({'status': 'success', 'state': 'inactive', 'msg': 'user logged in but inactive'})
    else:
        return json_response({'status': 'success', 'state': 'logged_out', 'msg': 'user logged out'})


@api_post
def api_login(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if not username or not password:
        return json_400_incorrect_use()
    user = authenticate(username=username, password=password)
    if user is None:
        return json_401_wrong_credentials()
    if not user.is_active:
        return json_401_inactive_user()
    login(request, user)
    return json_response({'status': 'success', 'msg': 'login successful'})


@api_post
def api_logout(request):
    if request.user and request.user.is_authenticated:
        logout(request)
        return json_response({'status': 'success', 'msg': 'logout successful'})
    else:
        return json_response({'status': 'success', 'msg': 'already logged out'})


@api_post
@authenticated_user
def change_password(request):
    current_password = request.data.get('current_password', None)
    new_password = request.data.get('new_password', None)

    if not current_password or not new_password:
        return json_400_incorrect_use()

    if not request.user.check_password(current_password):
        return json_response({'status': 'error', 'msg': 'incorrect password'}, status=403)

    if len(new_password) < 8:
        return json_response({'status': 'error', 'msg': 'password should be minimum 8 characters long'}, status=400)

    request.user.set_password(new_password)
    request.user.save()
    return json_response({'status': 'success', 'msg': 'password changed'})


@api_post
@authenticated_user
def edit_profile(request):
    if not any((f in request.data) for f in ['full_name', 'contact_name', 'address', 'phone', 'email', 'designation']):
        return json_400_incorrect_use()

    try:
        sme = Sme.objects.get(name=request.user)
        contact = ContactDetails.objects.filter(status='active', sme=sme).order_by('type')[0]
    except Sme.DoesNotExist:
        return json_400_incorrect_use()
    except IndexError:
        contact = ContactDetails.objects.create(sme=sme)

    if 'full_name' in request.data:
        request.user.first_name = request.data['full_name']
        request.user.save()

    contact_mod = False

    if 'contact_name' in request.data:
        contact.name = request.data['contact_name']
        contact_mod = True

    if 'address' in request.data and request.data['address']:
        save_sme_address(sme, request.data['address'])

    if 'phone' in request.data:
        contact.phone = request.data['phone']
        contact_mod = True

    if 'email' in request.data:
        contact.email = request.data['email']
        contact_mod = True

    if 'designation' in request.data:
        contact.designation = request.data['designation']
        contact_mod = True

    if contact_mod:
        contact.save()

    return json_response({'status': 'success', 'msg': 'profile edited', 'user': get_user_data(request.user, contact, sme)})


@api_get
@authenticated_user
def app_data(request):
    cities = City.objects.filter(state_id__isnull=False).order_by('name').values('id', 'name', 'state__name')
    cities = [{'id': c['id'], 'name': c['name'], 'state': c['state__name']} for c in cities]
    vehicle_data = list(VehicleCategory.objects.order_by('-priority').values('id', 'vehicle_type', 'capacity'))
    vendor_data = list(UserVendor.objects.filter(user=request.user).order_by('id').values('id', 'name', 'phone'))

    customer_id = ''
    aaho_office_id = ''
    try:
        sme = Sme.objects.get(name=request.user)
        contact = ContactDetails.objects.filter(status='active', sme=sme).order_by('type')[0]
        customer_id = sme.id
        aaho_office = sme.aaho_office
        if not aaho_office:
            aaho_office_id = sme.aaho_poc.office.id
        else:
            aaho_office_id = sme.aaho_office.id
        # print(sme)
        # print(customer_id)
        # print(aaho_office_id)
    except Sme.DoesNotExist:
        return json_400_incorrect_use()
    except IndexError:
        contact = ContactDetails.objects.create(sme=sme, name=request.user.first_name)

    city_scores, address_scores = get_ranking_results(request.user.id)

    data = {
        'cities': cities,
        'vehicles': vehicle_data,
        'vendors': vendor_data,
        'city_scores': city_scores,
        'address_scores': address_scores,
        'user': get_user_data(request.user, contact, sme),
        'customer_id': customer_id,
        'aaho_office_id': aaho_office_id
    }
    return json_response({'status': 'success', 'msg': 'app data', 'data': data})


def get_user_data(user, contact, sme):
    address = sme.address
    address_data = {} if not address else {
        'id': address.id,
        'line1': address.line1 or '',
        'line2': address.line2 or '',
        'line3': address.line3 or '',
        'landmark': address.landmark or '',
        'pin': address.pin or '',
        'city': {
            'id': address.city.id,
            'name': address.city.name,
            'state': address.city.state.name
        }
    }
    return {
        'full_name': user.first_name or '',
        'contact_name': contact.name or '',
        'address': address_data,
        'username': user.username or '',
        'phone': contact.phone or '',
        'email': contact.email or '',
        'designation': contact.designation or '',
        'id': user.id
    }

@api_get
@authenticated_user
def team_customer_booking_data(request):
    print(request.data)
    customer = Sme.objects.get(name=request.user)
    # broker = Broker.objects.get(name=User.objects.get(username=request.user.username))
    bookings = ManualBooking.objects.filter(company=customer,
                                            shipment_date__gte=datetime(2017, 12, 1).date()).exclude(
        booking_status__icontains='cancelled').order_by('-shipment_date')
    return json_response({'status': 'success', 'data': customer_booking_data(bookings=bookings)})


def save_sme_address(sme, address_data):
    line1 = address_data.get('line1', None)
    line2 = address_data.get('line2', None)
    line3 = address_data.get('line3', None)
    pin = address_data.get('pin', None)
    landmark = address_data.get('landmark', None)
    city_data = address_data.get('city', None)
    city_id = None if not city_data else city_data.get('id', None)
    city = None if not city_id else get_or_none(City, id=city_id)

    if not line1 or not city:
        return

    req_address_id = address_data.get('id', None)
    try:
        req_address_id = int(req_address_id)
    except ValueError:
        req_address_id = None

    address_id = req_address_id or sme.address_id
    address = None if not address_id else (get_or_none(Address, id=address_id) or Address())

    address.line1 = line1
    address.line2 = line2
    address.line3 = line3
    address.pin = pin
    address.landmark = landmark
    address.city_id = city.id

    address.save()
    sme.address = address
    sme.save()





























