from datetime import datetime

from api.decorators import api_post
from api.helper import json_response, json_error_response, json_success_response
from api.utils import get_or_none, parse_iso, int_or_none
from broker.models import BrokerVehicle, BrokerDriver, BrokerOwner
from driver.models import Driver, VEHICLE_STATUS_CHOICES
from fms.decorators import authenticated_user
from fms.models import Document
from owner.models import Vehicle, Owner
from utils.models import City, VehicleCategory, Bank, TaxationID


@api_post
@authenticated_user
def add_edit_vehicle(request):
    data = request.data
    vehicle_id = data.get('id', None)

    if vehicle_id:
        vehicle = get_or_none(Vehicle, id=int_or_none(vehicle_id))
        if not vehicle:
            return json_error_response('Vehicle with id=%s does not exist' % vehicle_id, 404)
    else:
        vehicle = Vehicle()

    vehicle_number = data.get('vehicle_number', None)
    if not vehicle_number and not vehicle_id:
        return json_error_response('vehicle number required', 400)

    owner_id = (data.get('owner', None) or {}).get('id', None)
    owner = None
    if owner_id:
        owner = get_or_none(Owner, id=int_or_none(owner_id))
        if not owner:
            return json_error_response('Owner with id=%s does not exist' % owner_id, 404)

    ac_id = (data.get('account', None) or {}).get('id', None)
    account = None
    if ac_id:
        account = get_or_none(Bank, id=int_or_none(ac_id))
        if not account:
            return json_error_response('Bank account with id=%s does not exist' % ac_id, 404)

    driver_id = (data.get('driver', None) or {}).get('id', None)
    driver = None
    if driver_id:
        driver = get_or_none(Driver, id=int_or_none(driver_id))
        if not driver:
            return json_error_response('Driver with id=%s does not exist' % driver_id, 404)

    current_city_id = data.get('current_city', None)
    current_city = None
    if current_city_id:
        current_city = get_or_none(City, id=int_or_none(current_city_id))
        if not current_city:
            return json_error_response('City with id=%s does not exist' % current_city_id, 404)

    vehicle_type_id = data.get('vehicle_type', None)
    vehicle_type = None
    has_vehicle_type_data = 'vehicle_type' in data
    if vehicle_type_id:
        vehicle_type = get_or_none(VehicleCategory, id=int_or_none(vehicle_type_id))
        if not vehicle_type:
            return json_error_response('VehicleCategory with id=%s does not exist' % vehicle_type_id, 404)
    else:
        new_category_type = data.get('new_vehicle_category_type', None)
        new_category_capacity = data.get('new_vehicle_category_capacity', None)
        new_category_type = None if not new_category_type else new_category_type.strip()
        new_category_capacity = None if not new_category_capacity else new_category_capacity.strip()
        if new_category_type:
            has_vehicle_type_data = True
            vehicle_type, _ = VehicleCategory.objects.get_or_create(
                vehicle_type=new_category_type, capacity=new_category_capacity)

    if 'owner' in data:
        vehicle.owner = owner

    if 'driver' in data:
        Vehicle.objects.filter(driver=driver).update(driver=None)
        vehicle.driver = driver

    if 'current_city' in data:
        vehicle.current_city = current_city

    if has_vehicle_type_data:
        vehicle.vehicle_type = vehicle_type

    normal_fields = [
        'vehicle_number', 'vehicle_model', 'chassis_number', 'engine_number', 'sim_number',
        'sim_operator', 'gps_enabled'
    ]

    for field in normal_fields:
        if field in data:
            setattr(vehicle, field, data.get(field, None))

    vehicle_status = data.get('status', None)
    if vehicle_status:
        if vehicle_status not in dict(VEHICLE_STATUS_CHOICES):
            return json_response({'status': 'error', 'msg': 'not a valid vehicle_status'}, status=400)
        vehicle.status = vehicle_status
        if vehicle.driver_app_user:
            vehicle.driver_app_user.vehicle_status = vehicle_status
            vehicle.driver_app_user.save()

    vehicle.save()

    broker_vehicle, _created = BrokerVehicle.objects.get_or_create(broker=request.broker, vehicle=vehicle)
    if 'account' in data:
        broker_vehicle.account_details = account
        broker_vehicle.save()

    if owner:
        BrokerOwner.objects.get_or_create(broker=request.broker, owner=owner)
    if driver:
        BrokerDriver.objects.get_or_create(broker=request.broker, driver=driver)

    edited = False

    doc_key = 'rc_doc'
    if doc_key in data and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        thumb = data[doc_key].get('thumb_url', None)
        doc = Document.new(
            user=request.user, bearer=vehicle, field_name='registration_certificate',
            document_type='REG', document=data[doc_key]['url'], doc_id=doc_id, thumb=thumb
        )
        doc.save()
        registration_year = data[doc_key].get('manufacture_year', None)
        validity = data[doc_key].get('validity', None)

        vehicle.registration_certificate = doc
        registration_year = None if not registration_year else registration_year.strip()
        try:
            registration_year = int(registration_year)
        except ValueError:
            registration_year = None
        vehicle.registration_year = None if registration_year is None else datetime(year=registration_year, month=1,
                                                                                    day=1).date()
        vehicle.registration_validity = None if not validity else parse_iso(validity)
        edited = True

    doc_key = 'permit_doc'
    if doc_key in data and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        thumb = data[doc_key].get('thumb_url', None)
        doc = Document.new(
            user=request.user, bearer=vehicle, field_name='permit_certificate',
            document_type='PERM', document=data[doc_key]['url'], doc_id=doc_id, thumb=thumb
        )
        doc.save()
        permit_type = data[doc_key].get('permit_type', None)
        validity = data[doc_key].get('validity', None)

        vehicle.permit_certificate = doc
        vehicle.permit_type = permit_type
        vehicle.permit_validity = None if not validity else parse_iso(validity)
        vehicle.permit = doc_id
        edited = True

    doc_key = 'insurance_doc'
    if doc_key in data and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        thumb = data[doc_key].get('thumb_url', None)
        doc = Document.new(
            user=request.user, bearer=vehicle, field_name='insurance_certificate',
            document_type='INS', document=data[doc_key]['url'], doc_id=doc_id, thumb=thumb
        )
        doc.save()
        insurer_name = data[doc_key].get('insurer_name', None)
        validity = data[doc_key].get('validity', None)

        vehicle.insurance_certificate = doc
        vehicle.insurer = insurer_name
        vehicle.insurance_validity = None if not validity else parse_iso(validity)
        vehicle.insurance_number = doc_id
        edited = True

    doc_key = 'fitness_doc'
    if doc_key in data and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        thumb = data[doc_key].get('thumb_url', None)
        doc = Document.new(
            user=request.user, bearer=vehicle, field_name='fitness_certificate',
            document_type='FIT', document=data[doc_key]['url'], doc_id=doc_id, thumb=thumb
        )
        doc.save()
        validity = data[doc_key].get('validity', None)

        vehicle.fitness_certificate = doc
        vehicle.fitness_certificate_validity_date = None if not validity else parse_iso(validity)
        vehicle.fitness_certificate_number = doc_id
        edited = True

    doc_key = 'puc_doc'
    if doc_key in data and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        thumb = data[doc_key].get('thumb_url', None)
        doc = Document.new(
            user=request.user, bearer=vehicle, field_name='puc_doc',
            document_type='PUC', document=data[doc_key]['url'], doc_id=doc_id, thumb=thumb
        )
        doc.save()
        validity = data[doc_key].get('validity', None)

        vehicle.puc_certificate = doc
        vehicle.puc_certificate_validity_date = None if not validity else parse_iso(validity)
        vehicle.puc_certificate_number = doc_id
        edited = True

    if edited:
        vehicle.save()

    doc_key = 'owner_pan_doc'
    if doc_key in data and vehicle.owner and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        thumb = data[doc_key].get('thumb_url', None)
        doc = Document.new(
            user=request.user, bearer=vehicle.owner, field_name='taxation_details',
            document_type='PAN', document=data[doc_key]['url'], doc_id=doc_id, thumb=thumb
        )
        doc.save()

        taxation_details = vehicle.owner.taxation_details or TaxationID()
        taxation_details.pan_doc = doc
        taxation_details.pan = doc_id
        taxation_details.save()

        owner = vehicle.owner
        owner.taxation_details = taxation_details
        owner.save()
        vehicle.owner = owner

    doc_key = 'owner_dec_doc'
    if doc_key in data and vehicle.owner and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        thumb = data[doc_key].get('thumb_url', None)
        doc = Document.new(
            user=request.user, bearer=vehicle.owner, field_name='declaration',
            document_type='DEC', document=data[doc_key]['url'], doc_id=doc_id, thumb=thumb
        )
        doc.save()

        validity = data[doc_key].get('validity', None)

        owner = vehicle.owner

        owner.declaration = doc.document
        owner.declaration_doc = doc
        owner.declaration_validity = None if not validity else parse_iso(validity)
        owner.save()
        vehicle.owner = owner

    doc_key = 'driver_dl_doc'
    if doc_key in data and vehicle.driver and data[doc_key].get('url'):
        doc_id = data[doc_key].get('doc_id', None)
        thumb = data[doc_key].get('thumb_url', None)
        doc = Document.new(
            user=request.user, bearer=vehicle.driver, field_name='driving_licence',
            document_type='DL', document=data[doc_key]['url'], doc_id=doc_id, thumb=thumb
        )
        doc.save()

        validity = data[doc_key].get('validity', None)
        issue_loc = data[doc_key].get('issue_location', None)

        driver = vehicle.driver

        driver.driving_licence_number = doc_id
        driver.driving_licence = doc
        driver.driving_licence_location = issue_loc
        driver.driving_licence_validity = None if not validity else parse_iso(validity)
        driver.save()

        vehicle.driver = driver

    return json_success_response(
        'vehicle details %s' % ('edited' if vehicle_id else 'saved'),
        data=vehicle.to_json()
    )
