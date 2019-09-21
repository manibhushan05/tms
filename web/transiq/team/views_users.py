from __future__ import print_function, unicode_literals, division, absolute_import

import random
import re

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.shortcuts import render

from api.decorators import api_get, api_post
from api.helper import json_error_response, json_success_response
from api.utils import get_or_none, int_or_none
from authentication.models import Profile
from broker.models import Broker, BrokerVehicle, BrokerOwner
from driver.models import Driver
from employee.models import Employee
from owner.models import Vehicle, Owner
from owner.vehicle_util import display_format, compare_format
from sme.models import Sme
from team.decorators import authenticated_user
from team.helper.helper import verify_profile_phone, verify_profile_email, django_date_format, to_int
from utils.models import City, Address, TaxationID, VehicleCategory, AahoOffice, State


def create_update_profile(user, name=None, email=None, phone=None, contact_person=None, contact_person_phone=None,
                          alternate_phone=None, remarks=None):
    try:
        profile = Profile.objects.get(user=user)
        profile.name = name
        profile.phone = phone
        profile.alternate_phone = alternate_phone
        profile.contact_person_name = contact_person
        profile.contact_person_phone = contact_person_phone
        profile.email = email
        profile.comment = remarks
        profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(
            user=user,
            name=name,
            phone=phone,
            alternate_phone=alternate_phone,
            contact_person_name=contact_person,
            contact_person_phone=contact_person_phone,
            email=email,
            comment=remarks
        )
    except Profile.MultipleObjectsReturned:
        pass


def create_update_address(line1, line2=None, line3=None, city=None, pin=None, address_id=None, latitude=None,
                          longitude=None, landmark=None):
    if address_id:
        address = get_or_none(Address, id=int_or_none(address_id))
        Address.objects.filter(id=int_or_none(address_id)).update(
            line1=line1,
            line2=line2,
            line3=line3,
            city=city,
            pin=pin,
            latitude=latitude,
            longitude=longitude,
            landmark=landmark
        )
    else:
        address = Address.objects.create(
            line1=line1,
            line2=line2,
            line3=line3,
            city=city,
            pin=pin,
            latitude=latitude,
            longitude=longitude,
            landmark=landmark
        )
    return address


@authenticated_user
def sme_list(request):
    sme = Sme.objects.all().select_related('name__profile')
    return render(request, 'team/registrations/customer-archive.html', {'sme': sme})


@authenticated_user
def register_customer_template(request):
    return render(request=request, template_name='team/registrations/register-customer.html')


@authenticated_user
def register_customer(request):
    if request.POST.get('email_id') and Profile.objects.filter(email__iexact=request.POST.get('email_id')).exists():
        return json_error_response('Email ID Already Exists', status=409)
    elif Profile.objects.filter(name__iexact=request.POST.get('company_name')).exists():
        return json_error_response('Company Already Registered', status=409)
    # elif Profile.objects.filter(phone__iexact=request.POST.get('contact_person_number')).exists():
    #     return json_error_response('Phone Already Exists', status=409)
    elif Sme.objects.filter(company_code__iexact=request.POST.get('company_code')).exists():
        return json_error_response('Company Code Already Exists', status=409)
    else:
        username = "".join(re.split("[^a-zA-Z]*", request.POST.get('company_name')))[:12]
        if User.objects.filter(username__iexact=username).exists():
            username = random.randrange(999999999999, 99999999999999)
        user = User.objects.create_user(username=str(username).lower(), password='YGYUg&6677')
        create_update_profile(
            user=user,
            name=request.POST.get('company_name'),
            contact_person=request.POST.get('contact_person_name'),
            contact_person_phone=request.POST.get('contact_person_number'),
            phone=request.POST.get('contact_person_number'),
            alternate_phone=request.POST.get('alternate_number'),
            email=request.POST.get('email_id'),
            remarks=request.POST.get('remarks')
        )
        Sme.objects.create(
            name=user, company_code=request.POST.get('company_code'),
            aaho_office=get_or_none(AahoOffice, id=request.POST.get('aaho_office')),
            gstin=request.POST.get('gstin', None),
            aaho_poc=get_or_none(Employee, id=int_or_none(request.POST.get('aaho_poc'))),
            credit_period=request.POST.get('credit_period', None),
            address=create_update_address(
                line1=request.POST.get('company_address'),
                city=get_or_none(City, id=int_or_none(request.POST.get('city'))),
                pin=request.POST.get('pin')
            ),
            is_gst_applicable='no' if request.POST.get('is_gst_applicable') == 'n' else 'yes',
            customer_address=request.POST.get('company_address'),
            city=get_or_none(City, id=int_or_none(request.POST.get('city'))),
            pin=request.POST.get('pin'),
            created_by=request.user
        )
        return json_success_response('SME Successfully Registered')


@authenticated_user
def update_customer_page(request):
    customer = get_or_none(Sme, id=int_or_none(request.GET.get('customer_id')))
    employees = Employee.objects.exclude(status='inactive')
    return render(request=request, template_name='team/registrations/customer-update.html',
                  context={'customer': customer, 'employees': employees})


@authenticated_user
def update_customer(request):
    sme = get_or_none(Sme, id=int_or_none(request.POST.get('customer_id')))
    # phone_status, msg = verify_profile_phone(username=sme.name.username,
    #                                          phone=request.POST.get('contact_person_number'),
    #                                          alt_phone=request.POST.get('alternate_number'))
    # if phone_status:
    #     return json_error_response(msg=msg, status=409)

    create_update_profile(
        user=sme.name,
        name=request.POST.get('company_name'),
        contact_person=request.POST.get('contact_person_name'),
        contact_person_phone=request.POST.get('contact_person_number'),
        phone=request.POST.get('contact_person_number'),
        alternate_phone=request.POST.get('alternate_number'),
        email=request.POST.get('email_id'),
        remarks=request.POST.get('remarks')
    )

    create_update_address(
        address_id=sme.address_id,
        line1=request.POST.get('company_address'),
        city=get_or_none(City, id=int_or_none(request.POST.get('city'))),
        pin=request.POST.get('pin')
    )
    sme.customer_address = request.POST.get('company_address')
    sme.aaho_office = get_or_none(AahoOffice, id=request.POST.get('aaho_office'))
    sme.city = get_or_none(City, id=int_or_none(request.POST.get('city')))
    sme.pin = request.POST.get('pin')
    sme.gstin = sme.gstin if not request.POST.get('gstin') else request.POST.get('gstin')
    sme.is_gst_applicable = request.POST.get('is_gst_applicable')
    sme.aaho_poc = get_or_none(Employee, id=int_or_none(request.POST.get('aaho_poc')))
    sme.credit_period = request.POST.get('credit_period', None)
    sme.save()
    return json_success_response(msg="success")


@authenticated_user
def register_supplier_template(request):
    return render(request=request, template_name='team/registrations/register-supplier.html')


@authenticated_user
def register_supplier(request):
    if request.POST.get('email_id') and Profile.objects.filter(email__iexact=request.POST.get('email_id')).exists():
        return json_error_response('Email ID Already Exists', status=409)
    elif Profile.objects.filter(name__iexact=request.POST.get('supplier_name')).exists():
        return json_error_response('Supplier Already Registered', status=409)
    elif Profile.objects.filter(phone=request.POST.get('contact_person_number')).exists():
        return json_error_response('Phone Already Exists', status=409)
    elif request.POST.get('pan') and TaxationID.objects.filter(pan__iexact=request.POST.get('pan')).exists():
        return json_error_response('PAN Already Exists', status=409)
    else:
        username = "".join(re.split("[^a-zA-Z]*", request.POST.get('supplier_name')))[:12]
        if User.objects.filter(username__iexact=username).exists():
            username = random.randrange(999999999999, 99999999999999)
        user = User.objects.create_user(username=str(username).lower(), password='YGYUg&6677')
        create_update_profile(
            user=user,
            name=request.POST.get('supplier_name'),
            contact_person=request.POST.get('contact_person_name'),
            contact_person_phone=request.POST.get('contact_person_number'),
            phone=request.POST.get('contact_person_number'),
            alternate_phone=request.POST.get('alternate_number'),
            email=request.POST.get('email_id'),
            remarks=request.POST.get('remarks')
        )
        instance = Broker.objects.create(
            name=user,
            city=get_or_none(City, id=int_or_none(request.POST.get('supplier_city'))),
            route=request.POST.get('route'),
            taxation_details=None if not request.POST.get('pan') else TaxationID.objects.create(
                pan=request.POST.get('pan')
            ),
            aaho_office=get_or_none(AahoOffice, id=request.POST.get('aaho_office'))
        )
        dest_states = request.POST.getlist('destination_states[]')
        if dest_states:
            if 'select_all' in dest_states:
                dest_states = State.objects.values_list('id', flat=True)
            for dest_state in dest_states:
                instance.destination_state.add(dest_state)
        return json_success_response('Supplier Successfully Registered')


@authenticated_user
def supplier_list(request):
    supplier = Broker.objects.all().select_related('name__profile')
    return render(request, 'team/registrations/supplier-list.html', {'supplier': supplier})


@authenticated_user
def update_supplier_page(request):
    supplier = get_or_none(Broker, id=int_or_none(request.GET.get('supplier_id')))
    return render(request=request, template_name='team/registrations/update-supplier.html',
                  context={'supplier': supplier})


@authenticated_user
def update_supplier(request):
    supplier = get_or_none(Broker, id=int_or_none(request.POST.get('supplier_id')))
    phone_status, msg = verify_profile_phone(
        username=supplier.name.username,
        phone=request.POST.get('contact_person_number'),
        alt_phone=request.POST.get('alternate_number')
    )
    if phone_status:
        return json_error_response(msg=msg, status=409)
    email_status, msg = verify_profile_email(
        username=supplier.name.username,
        email=request.POST.get('email'),
        alt_email=None
    )
    if email_status:
        return json_error_response(msg=msg, status=409)

    if request.POST.get('pan') and Broker.objects.exclude(
            name=supplier.name).filter(pan=request.POST.get('pan')).exists():
        return json_error_response("PAN Already exists", status=409)

    profile = Profile.objects.get(user=supplier.name)
    profile.name = request.POST.get('supplier_name')
    profile.contact_person_name = request.POST.get('contact_person_name')
    profile.phone = request.POST.get('phone')
    profile.alternate_phone = request.POST.get('alt_phone')
    profile.email = request.POST.get('email')
    profile.comment = request.POST.get('remarks')
    profile.save()
    create_update_profile(
        user=supplier.name,
        name=request.POST.get('supplier_name'),
        contact_person=request.POST.get('contact_person_name'),
        contact_person_phone=request.POST.get('contact_person_number'),
        phone=request.POST.get('contact_person_number'),
        alternate_phone=request.POST.get('alternate_number'),
        email=request.POST.get('email'),
        remarks=request.POST.get('remarks')
    )
    supplier.pan = request.POST.get('pan')
    supplier.route = request.POST.get('route')
    supplier.city = get_or_none(City, id=int_or_none(request.POST.get('supplier_city')))
    supplier.aaho_office = get_or_none(AahoOffice, id=request.POST.get('aaho_office'))
    supplier.destination_state.clear()
    dest_states = request.POST.getlist('destination_states[]')
    if dest_states:
        if 'select_all' in dest_states:
            dest_states = State.objects.values_list('id', flat=True)
        for dest_state in dest_states:
            supplier.destination_state.add(dest_state)
    supplier.save()
    return json_success_response("success")


@authenticated_user
def update_driver_page(request):
    driver = get_or_none(Driver, id=int_or_none(request.GET.get('driver_id')))
    return render(request=request, template_name='team/registrations/driver-update.html', context={'driver': driver})


@authenticated_user
def update_driver_details(request):
    if Driver.objects.filter(phone=request.POST.get('driver_phone_number')).exclude(
            id=int_or_none(request.POST.get('driver_id'))).exists():
        return json_error_response("Phone Already Exists", status=409)
    driver = get_or_none(Driver, id=int_or_none(request.POST.get('driver_id')))
    if driver:
        driver.name = request.POST.get('driver_name')
        driver.phone = request.POST.get('driver_phone_number')
        driver.alt_phone = request.POST.get('driver_alt_phone_number1')
        driver.alt_phone2 = request.POST.get('driver_alt_phone_number2')
        driver.driving_licence_number = request.POST.get('dl_number')
        driver.driving_licence_validity = django_date_format(request.POST.get('dl_validity'))
        driver.route = request.POST.get('route')
        driver.save()
    return json_success_response("Updated success")


@authenticated_user
def register_driver_page(request):
    return render(request=request, template_name='team/registrations/register-driver.html')


@authenticated_user
def register_driver(request):
    if Driver.objects.filter(phone=request.POST.get('driver_phone_number')).exists():
        return json_error_response('Driver Already Exists', status=409)
    else:
        Driver.objects.create(
            name=request.POST.get('driver_name'),
            phone=request.POST.get('driver_phone_number'),
            alt_phone=request.POST.get('driver_alt_phone_number1'),
            alt_phone2=request.POST.get('driver_alt_phone_number2'),
            driving_licence_number=request.POST.get('dl_number'),
            driving_licence_validity=django_date_format(request.POST.get('dl_validity')),
            route=request.POST.get('route'),
            driving_licence_location=request.POST.get('driver_city')
        )
        return json_success_response('Driver Successfully Registered')


@api_get
@authenticated_user
def driver_list_page(request):
    drivers = Driver.objects.all()
    return render(request=request, template_name='team/registrations/driver-list-page.html',
                  context={'drivers': drivers})


def update_broker_vehicle(broker, vehicle=None):
    pass


@authenticated_user
@api_get
def owner_registration_page(request):
    return render(request=request, template_name='team/registrations/register_owner.html')


@authenticated_user
@api_post
def register_owner(request):
    username = "".join(re.split("[^a-zA-Z]*", request.POST.get('owner_name')))[:12]
    owner_name = request.POST.get('owner_name')
    pan = request.POST.get('pan')
    if User.objects.filter(username__iexact=username).exists():
        username = random.randrange(999999999999, 99999999999999)
    # if owner_name in Owner.objects.values_list('name__profile__name', flat=True):
    #     return json_error_response(msg='Owner {} already exists'.format(request.POST.get('owner_name')), status=409)
    # if request.POST.get('pan') in Owner.objects.values_list('pan', flat=True):
    #     return json_error_response(msg='Pan {} already exists for {}'.format(owner_name, ''.join(
    #         Owner.objects.filter(pan=pan).values_list('name__profile__name', flat=True))), status=409)
    #
    # if Vehicle.objects.filter(id__in=request.POST.getlist('vehicle_id[]')).exclude(owner=None):
    #     print (Vehicle.objects.filter(id__in=request.POST.getlist('vehicle_id[]')).exclude(owner=None))
    user = User.objects.create_user(username=str(username).lower(), password='YGYUg&6677')
    Profile.objects.create(
        user=user,
        name=request.POST.get('owner_name'),
        phone=request.POST.get('owner_phone', None),
        contact_person_name=request.POST.get('contact_person_name'),
        contact_person_phone=request.POST.get('contact_person_phone'),
        alternate_phone=request.POST.get('alternate_number'),
        email=request.POST.get('email'),
        comment=request.POST.get('remarks')
    )
    owner = Owner.objects.create(
        name=user,
        address=Address.objects.create(
            line1=request.POST.get('owner_address'),
            city=get_or_none(City, id=int_or_none(request.POST.get('city'))),
            pin=request.POST.get('pin', None)
        ),
        route_temp=request.POST.get('route'),
        pan=request.POST.get('pan')
    )
    Broker.objects.create(
        name=user,
        address=Address.objects.create(
            line1=request.POST.get('owner_address'),
            city=get_or_none(City, id=int_or_none(request.POST.get('city'))),
            pin=request.POST.get('pin', None)
        ),
        route=request.POST.get('route'),
        pan=request.POST.get('pan')
    )
    try:
        for vehicle in Vehicle.objects.filter(id__in=request.POST.getlist('vehicle_id[]')):
            vehicle.owner = owner
            vehicle.save()
    except ValueError:
        pass
    return json_success_response(msg="success")


@authenticated_user
@api_get
def update_owner_page(request):
    owner = get_or_none(Owner, id=int_or_none(request.GET.get('owner_id')))
    vehicles = [{'id': vehicle.id, 'vehicle_number': display_format(vehicle.vehicle_number)} for vehicle in
                Vehicle.objects.filter(owner=None)]
    owner_vehicles = [{'id': vehicle.id, 'vehicle_number': display_format(vehicle.vehicle_number)} for vehicle in
                      Vehicle.objects.filter(owner=owner)]

    return render(
        request=request,
        template_name='team/registrations/owner-update.html',
        context={
            'owner': owner,
            'vehicles': vehicles,
            'owner_vehicles': owner_vehicles,
        },
    )


def owner_list(request):
    return render(request=request, template_name='team/registrations/owner_list.html')


@authenticated_user
@api_post
def update_owner(request):
    if request.POST.get('owner_name') in Owner.objects.exclude(
            name__profile__name=request.POST.get('owner_name')).values_list('name__profile__name', flat=True):
        return json_error_response(msg='Owner {} already exists'.format(request.POST.get('owner_name')), status=409)
    owner = get_or_none(Owner, id=int_or_none(request.POST.get('owner_id')))
    if owner:
        profile = Profile.objects.get(user=owner.name)
        profile.name = request.POST.get('owner_name')
        profile.phone = request.POST.get('owner_phone')
        profile.alternate_phone = request.POST.get('alternate_number')
        profile.contact_person_name = request.POST.get('contact_person_name')
        profile.contact_person_phone = request.POST.get('contact_person_phone')
        profile.comment = request.POST.get('remarks')
        profile.save()
        if not owner.address:
            owner.address = Address.objects.create(
                line1=request.POST.get('owner_address'),
                city=get_or_none(City, id=int_or_none(request.POST.get('city'))),
                pin=request.POST.get('pin')
            )
        else:
            address = Address.objects.get(id=owner.address.id)
            address.line1 = request.POST.get('owner_address')
            address.city = get_or_none(City, id=request.POST.get('city'))
            address.pin = request.POST.get('pin')
            address.save()
        owner.temp_address = request.POST.get('owner_address')
        owner.route_temp = request.POST.get('route')
        owner.pan = request.POST.get('pan')
        owner.save()
    broker = get_or_none(Broker, name=owner.name)
    if broker:
        if broker.address:
            broker.address = Address.objects.create(
                line1=request.POST.get('owner_address'),
                city=get_or_none(City, id=int_or_none(request.POST.get('city'))),
                pin=request.POST.get('pin')
            )
        else:
            address = get_or_none(Address, id=None if not broker.address else broker.address.id)
            if address:
                address.line1 = request.POST.get('owner_address')
                address.city = get_or_none(City, id=int_or_none(request.POST.get('city')))
                address.pin = request.POST.get('pin')
                address.save()
        broker.pan = request.POST.get('pan')
        broker.route = request.POST.get('route')
        broker.city = get_or_none(City, id=int_or_none(request.POST.get('city', None)))
        broker.save()
    else:
        Broker.objects.create(
            name=None if not owner.name else owner.name,
            address=owner.address,
            pan=owner.pan,
            city=get_or_none(City, id=int_or_none(request.POST.get('city', None))),
            route=request.POST.get('route')
        )

    for vehicle in Vehicle.objects.filter(id__in=request.POST.getlist('vehicle_id[]')):
        vehicle.owner = owner
        vehicle.save()
        broker = Broker.objects.get(name=owner.name)
        try:
            BrokerVehicle.objects.create(broker=broker, vehicle=vehicle)
        except IntegrityError:
            pass
    return json_success_response(msg="success")


@authenticated_user
def vehicle_registration_page(request):
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

    return render(
        request=request,
        template_name='team/registrations/register_vehicle.html',
        context={
            'vehicle_categories': vehicle_categories,
            'body_type_choices': body_type_choices,
            'gps_enable_choices': gps_enable_choices
        }
    )


def create_broker_owner(owner):
    if isinstance(owner, Owner):
        if not Broker.objects.filter(name=owner.name).exists():
            broker = Broker.objects.create(
                name=None if not owner.name else owner.name,
                address=owner.owner_address,
                pan=owner.pan,
                city=owner.city,
                route=owner.route_temp
            )
        else:
            try:
                broker = Broker.objects.get(name=owner.name)
            except Broker.MultipleObjectsReturned:
                broker = Broker.objects.last()
        try:
            BrokerOwner.objects.create(broker=broker, owner=owner)
        except IntegrityError:
            msg = 'Broker Owner Relationship already exists'
            return None
    else:
        return None


def owner_vehicle(owner, vehicle):
    pass


def broker_vehicle(broker, vehicle):
    pass


@authenticated_user
@api_post
def register_vehicle(request):
    if Vehicle.objects.filter(vehicle_number=compare_format(request.POST.get('vehicle_number'))).exists():
        return json_error_response(msg="Vehicle Already Exists", status=409)
    owner = get_or_none(Owner, id=int_or_none(request.POST.get('owner_id', None)))
    vehicle = Vehicle.objects.create(
        owner=owner,
        vehicle_number=compare_format(request.POST.get('vehicle_number')),
        rc_number=request.POST.get('rc_number'),
        permit=request.POST.get('permit_number'),
        permit_validity=django_date_format(request.POST.get('permit_validity')),
        permit_type=request.POST.get('permit_type'),
        vehicle_type=get_or_none(VehicleCategory, id=int_or_none(request.POST.get('vehicle_category'))),
        vehicle_capacity=to_int(request.POST.get('exact_vehicle_capacity')),
        body_type=request.POST.get('vehicle_body_type'),
        vehicle_model=request.POST.get('vehicle_model'),
        chassis_number=request.POST.get('chassis_number'),
        engine_number=request.POST.get('engine_number'),
        insurer=request.POST.get('insurer'),
        insurance_number=request.POST.get('insurance_number'),
        insurance_validity=django_date_format(request.POST.get('insurance_validity')),
        registration_year=None if not request.POST.get('registration_year') else django_date_format(
            '01-Jan-' + request.POST.get('registration_year').strip()),
        registration_validity=django_date_format(request.POST.get('registration_validity')),
        fitness_certificate_number=request.POST.get('fitness_certificate_number'),
        fitness_certificate_issued_on=django_date_format(request.POST.get('fitness_certificate_issued_on')),
        fitness_certificate_validity_date=django_date_format(request.POST.get('fitness_certificate_validity')),
        puc_certificate_number=request.POST.get('puc_certificate_number'),
        puc_certificate_issued_on=django_date_format(request.POST.get('puc_certificate_issued_on')),
        puc_certificate_validity_date=django_date_format(request.POST.get('puc_certificate_validity')),
        gps_enabled=False if request.POST.get('gps_enable') == 'no' else True,
        changed_by=request.user
    )
    if owner:
        create_broker_owner(owner=owner)
        broker = Broker.objects.get(name=owner.name)
        update_broker_vehicle(broker=broker, vehicle=vehicle)
    return json_success_response(msg="Success")


# @authenticated_user
def vehicle_archive(request):
    return render(request=request, template_name='team/registrations/vehicle-list.html')


@authenticated_user
@api_get
def update_vehicle_page(request):
    vehicle = Vehicle.objects.get(id=int_or_none(request.GET.get('vehicle_id', None)))
    owners = [{'id': owner.id, 'name': owner.get_name(), 'phone': owner.get_phone()} for owner in Owner.objects.all()]
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
    return render(
        request=request, template_name='team/registrations/update-vehicle.html',
        context={
            'vehicle': vehicle,
            'owners': owners,
            'vehicle_categories': vehicle_categories,
            'body_type_choices': body_type_choices,
            'gps_enable_choices': gps_enable_choices
        }
    )


@authenticated_user
@api_post
def update_vehicle(request):
    vehicle = Vehicle.objects.get(id=int_or_none(request.POST.get('vehicle_id')))
    vehicle.owner = get_or_none(Owner, id=int_or_none(request.POST.get('owner_id', None)))
    vehicle.vehicle_number = compare_format(request.POST.get('vehicle_number'))
    vehicle.rc_number = request.POST.get('rc_number')
    vehicle.permit = request.POST.get('permit_number')
    vehicle.permit_validity = django_date_format(request.POST.get('permit_validity'))
    vehicle.permit_type = request.POST.get('permit_type')
    vehicle.vehicle_type = get_or_none(VehicleCategory, id=int_or_none(request.POST.get('vehicle_category')))
    vehicle.vehicle_capacity = to_int(request.POST.get('exact_vehicle_capacity'))
    vehicle.body_type = request.POST.get('vehicle_body_type')
    vehicle.vehicle_model = request.POST.get('vehicle_model')
    vehicle.chassis_number = request.POST.get('chassis_number')
    vehicle.engine_number = request.POST.get('engine_number')
    vehicle.insurer = request.POST.get('insurer')
    vehicle.insurance_number = request.POST.get('insurance_number')
    vehicle.insurance_validity = django_date_format(request.POST.get('insurance_validity'))
    vehicle.registration_year = None if not request.POST.get('registration_year') else django_date_format(
        '01-Jan-' + request.POST.get('registration_year').strip())
    vehicle.registration_validity = django_date_format(request.POST.get('registration_validity'))
    vehicle.fitness_certificate_number = request.POST.get('fitness_certificate_number')
    vehicle.fitness_certificate_issued_on = django_date_format(request.POST.get('fitness_certificate_issued_on'))
    vehicle.fitness_certificate_validity_date = django_date_format(request.POST.get('fitness_certificate_validity'))
    vehicle.puc_certificate_number = request.POST.get('puc_certificate_number')
    vehicle.puc_certificate_issued_on = django_date_format(request.POST.get('puc_certificate_issued_on'))
    vehicle.puc_certificate_validity_date = django_date_format(request.POST.get('puc_certificate_validity'))
    vehicle.gps_enabled = False if request.POST.get('gps_enable') == 'no' else True
    vehicle.changed_by = request.user
    vehicle.save()
    return json_success_response("success")
