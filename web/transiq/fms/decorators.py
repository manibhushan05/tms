from django.db import transaction

from api.helper import json_error_response
from broker.models import Broker, BrokerVehicle, BrokerOwner, BrokerDriver, BrokerAccount
from owner.models import Owner, Vehicle


def authenticated_user(func):
    def inner(request, *args, **kwargs):
        if not request.user:
            return json_error_response('no user present', 401)
        if not request.user.is_authenticated:
            return json_error_response('user is not authenticated', 401)
        if not request.user.is_active:
            return json_error_response('user authenticated but inactive', 401)
        if not any(g.name == 'fms' or g.name == 'sme' for g in request.user.groups.all()):
            return json_error_response('user not allowed to access this app', 401)

        broker, owner = get_broker_and_owner(request.user)

        if not broker:
            return json_error_response('user has no supplier or owner entry present', 401)

        request.broker = broker;
        request.owner = owner

        return func(request, *args, **kwargs)

    inner.__name__ = func.__name__
    inner.__module__ = func.__module__
    inner.__doc__ = func.__doc__
    inner.__dict__ = func.__dict__
    return inner


def get_broker_and_owner(user):
    try:
        broker = Broker.objects.get(name=user)
    except Broker.DoesNotExist:
        broker = None

    try:
        owner = Owner.objects.get(name=user)
    except Owner.DoesNotExist:
        owner = None

    if broker:
        return broker, owner

    if not owner:
        owner = Owner.objects.create(name=user)
        broker = Broker.objects.create(name=user)
        return broker, owner

    broker = get_new_from_owner(owner, user)
    return broker, owner


def get_new_from_owner(owner, user):
    owner_vehicles = list(
        Vehicle.objects.filter(owner=owner).values_list('id', 'driver_id', 'driver__account_details_id')
    )
    vehicle_ids = set()
    driver_ids = set()
    accounts_ids = {} if not owner.account_details_id else {owner.account_details_id: 'self'}
    for vehicle_id, driver_id, driver_ac_id in owner_vehicles:
        if vehicle_id:
            vehicle_ids.add(vehicle_id)
        if driver_id:
            driver_ids.add(driver_id)
        if driver_ac_id:
            accounts_ids[driver_ac_id] = 'driver'

    broker = Broker.objects.create(
        name=user, address=owner.address,
        account_details=owner.account_details, taxation_details=owner.taxation_details
    )
    BrokerOwner.objects.create(broker=broker, owner=owner)

    BrokerVehicle.objects.bulk_create([
        BrokerVehicle(broker=broker, vehicle_id=v) for v in vehicle_ids
    ])
    BrokerDriver.objects.bulk_create([
        BrokerDriver(broker=broker, driver_id=d) for d in driver_ids
    ])
    BrokerAccount.objects.bulk_create([
        BrokerAccount(broker=broker, account_id=a, relation=r) for a, r in accounts_ids.items()
    ])

    return broker
