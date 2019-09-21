import datetime
from datetime import timedelta
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from api.helper import json_response, json_error_response, json_400_incorrect_use
from api.sms import send_sms
from broker.models import Broker
from fms.forms import RequirementForm, RequirementGetForm
from fms.models import Requirement, REQ_STATUS
from api.decorators import api_get, api_post, authenticated_user
from api.utils import get_or_none, int_or_none
from sme.models import Sme
from utils.models import City, VehicleCategory, AahoOffice


RDONLY_REQ_STATUS = (
    ('cancelled', 'Cancelled'),
    ('fulfilled', 'Fulfilled'),
    ('lapsed', 'Lapsed'),
)

@api_post
@authenticated_user
def add_new_requirement(request):
    objects = parse_requirement_fields(request)
    if objects['status'] == 'failure':
        return json_response({'status': 'failure', 'msg': objects['msg']})
    objects.pop('status', None)
    try:
        Requirement.objects.create(**objects)
    except IntegrityError:
        return json_response({'status': 'failure', 'msg': 'Requirement could not be created'})

    return json_response({'status': 'success', 'msg': 'Requirement successfully submitted'})


@api_post
@authenticated_user
def update_requirement(request):
    if not request.data.get('requirement_id'):
        return json_response({'status': 'failure', 'msg': 'Requirement Id is not passed'})
    requirement = get_or_none(Requirement, id=request.data.get('requirement_id'))
    if not requirement or requirement.deleted:
        return json_response({'status': 'failure', 'msg': 'Requirement not found', 'data': {}})
    objects = parse_requirement_fields(request)
    if objects['status'] == 'failure':
        return json_response({'status': 'failure', 'msg': objects['msg']})

    requirement.client = objects['client']
    requirement.aaho_office = objects['aaho_office']
    requirement.from_shipment_date = objects['from_shipment_date']
    requirement.to_shipment_date = objects['to_shipment_date']
    requirement.from_city = objects['from_city']
    requirement.to_city = objects['to_city']
    requirement.tonnage = objects['tonnage']
    requirement.no_of_vehicles = objects['no_of_vehicles']
    requirement.material = objects['material']
    requirement.type_of_vehicle = objects['type_of_vehicle']
    requirement.rate = objects['rate']
    requirement.remark = objects['remark']
    requirement.cancel_reason = objects['cancel_reason']
    requirement.changed_by = User.objects.get(username=request.user.username)

    # print(request.data.get('req_status'))
    if requirement.req_status and request.data.get('req_status') == 'open':
        requirement.req_status = objects['req_status']
        requirement.save(update_fields=['req_status', 'material', 'client', 'aaho_office', 'from_shipment_date',
                                        'to_shipment_date', 'from_city', 'to_city', 'tonnage', 'no_of_vehicles',
                                        'material', 'type_of_vehicle', 'rate', 'remark', 'cancel_reason', 'changed_by'])
    else:
        requirement.req_status = objects['req_status']
        requirement.save()
    return json_response({'status': 'success', 'msg': 'requirement updated'})


@api_get
@authenticated_user
def get_my_requirements(request):
    user = request.user
    if any(g.name == 'sales' for g in user.groups.all()):
        # print('User is in sales group')
        requirements = Requirement.history.filter(Q(changed_by=user) | Q(created_by=user)).exclude(deleted=True)
        if not requirements:
            return json_response({'status': 'failure', 'msg': 'No requirements found', 'data': {}})
        req_ids = []
        for req in requirements:
            if req.id not in req_ids:
                req_ids.append(req.id)
        requirements = Requirement.objects.filter(id__in=req_ids).\
            exclude(deleted=True).exclude(req_status='unverified').order_by('-from_shipment_date')
        if not requirements:
            return json_response({'status': 'failure', 'msg': 'No requirements found', 'data': {}})
        return json_response(
            {'status': 'success', 'msg': 'requirements data', 'data': get_requirement_data(requirements)})
    if any(g.name == 'sme' for g in user.groups.all()):
        # print('User is in sme group')
        sme = Sme.objects.get(name=user)
        if not sme:
            return json_response({'status': 'failure', 'msg': 'No requirements found for this customer', 'data': {}})
        requirements = Requirement.objects.filter(client=sme).exclude(deleted=True).order_by('-from_shipment_date')
        return json_response(
            {'status': 'success', 'msg': 'requirements data', 'data': get_requirement_data(requirements)})
    return json_response({'status': 'failure', 'msg': 'No requirements found', 'data': {}})

@api_get
def get_filtered_requirements(request):
    # user = request.user
    aaho_office_id = request.GET.get('aaho_office_id', None)
    req_status = request.GET.get('requirement_status', None)
    q_objects = Q()
    if not aaho_office_id:
        return json_response({'status': 'failure', 'msg': 'Aaho Office ID is not passed'})

    if req_status not in [x[0] for x in REQ_STATUS]:
        return json_response({'status': 'failure', 'msg': 'Requirement status is wrong'})

    aaho_office = get_or_none(AahoOffice, id=aaho_office_id)
    q_objects |= Q(**{'aaho_office': aaho_office, 'req_status': req_status})

    present = datetime.datetime.now()
    requirements = Requirement.objects.filter(q_objects).exclude(deleted=True)
    requirements_with_todate = requirements.filter(to_shipment_date__isnull=False,
                                                   from_shipment_date__lte=(present.date() + timedelta(days=3)),
                                                   to_shipment_date__gte=present.date())
    requirements_without_todate = requirements.filter(to_shipment_date__isnull=True,
                                                      from_shipment_date__range=(present.date(), (present.date() + timedelta(days=3))))
    requirements = requirements_with_todate.union(requirements_without_todate)
    if not requirements:
        return json_response({'status': 'failure', 'msg': 'No requirements found', 'data': {}})
    return json_response({'status': 'success', 'msg': 'requirements data', 'data': get_requirement_data(requirements)})


@api_post
def get_all_requirements(request):
    requirements = Requirement.objects.all().exclude(deleted=True)
    if not requirements:
        return json_response({'status': 'failure', 'msg': 'No requirements found', 'data': {}})
    return json_response({'status': 'success', 'msg': 'requirements data', 'data': get_requirement_data(requirements)})


@api_post
def get_requirement(request):
    form = RequirementGetForm(request.data)
    if not form.is_valid():
        return json_response({'status': 'failure', 'msg': 'Incorrect values'})
    req = Requirement.objects.filter(id=request.data.get('requirement_id')).exclude(deleted=True)
    if not req:
        return json_response({'status': 'failure', 'msg': 'Requirement not found', 'data': {}})
    return json_response({'status': 'success', 'msg': 'requirement data', 'data': get_requirement_data(req)})


@api_post
@authenticated_user
def delete_requirement(request):
    form = RequirementGetForm(request.data)
    if not form.is_valid():
        return json_response({'status': 'failure', 'msg': 'Incorrect values'})
    requirement = get_or_none(Requirement, id=request.data.get('requirement_id'))
    if not requirement or requirement.deleted:
        return json_response({'status': 'failure', 'msg': 'Requirement not found', 'data': {}})
    requirement.deleted = True
    requirement.deleted_on = timezone.now()
    requirement.save(update_fields=['deleted', 'deleted_on'])
    return json_response({'status': 'success', 'msg': 'requirement deleted'})


def get_requirement_data(requirements):
    req_data = []
    for req in requirements:
        if req.req_status in [x[0] for x in RDONLY_REQ_STATUS]:
            rdonly = True
        else:
            rdonly = False
        req_data.append({
            'id': req.id,
            'client': req.client.get_name() if req.client else '',
            'client_id': req.client.id if req.client else None,
            'from_city': req.from_city.name if req.from_city else '',
            'from_city_id': req.from_city.id if req.from_city else None,
            'to_city': req.to_city.name if req.to_city else '',
            'to_city_id': req.to_city.id if req.to_city else None,
            'aaho_office': req.aaho_office.branch_name if req.aaho_office else '',
            'aaho_office_id': req.aaho_office.id if req.aaho_office else None,
            'from_state': req.from_city.state.name if req.from_city and req.from_city.state else '',
            'to_state': req.to_city.state.name if req.to_city and req.to_city.state else '',
            'material': req.material,
            'from_shipment_date': str(req.from_shipment_date),
            'to_shipment_date': str(req.to_shipment_date),
            'tonnage': str(req.tonnage),
            'no_of_vehicles': req.no_of_vehicles,
            'type_of_vehicle': req.type_of_vehicle.name() if req.type_of_vehicle else '',
            'type_of_vehicle_id': req.type_of_vehicle.id if req.type_of_vehicle else None,
            'rate': req.rate,
            'req_status': req.req_status,
            'remark': req.remark,
            'cancel_reason': req.cancel_reason,
            'read_only': rdonly
        })
    data = {
        'requirements': req_data
    }
    return data


def parse_requirement_fields(load):
    user = load.user
    data = load.data
    form = RequirementForm(data)
    if not form.is_valid():
        return {'status': 'failure', 'msg': 'Pls enter all * fields'}
    from_shipment_date = data.get('from_shipment_date', None)
    to_shipment_date = data.get('to_shipment_date', None)
    # print(to_shipment_date)
    try:
        present = datetime.datetime.now()
        from_dt = datetime.datetime.strptime(from_shipment_date, '%Y-%m-%d')
        if from_dt.date() < present.date():
            return {'status': 'failure', 'msg': 'From Date should be greater than or equal to Today'}
        if to_shipment_date:
            to_date = datetime.datetime.strptime(to_shipment_date, '%Y-%m-%d')
            if to_date < from_dt:
                return {'status': 'failure', 'msg': 'To Date should be greater than From Date'}
            if to_date.date() < present.date():
                return {'status': 'failure', 'msg': 'To Date should be greater than or equal to Today'}
        else:
            to_shipment_date = None
    except ValueError:
        return {'status': 'failure', 'msg': 'Incorrect date format, should be YYYY-MM-DD'}

    tonnage = data.get('tonnage', None)
    no_of_vehicles = data.get('no_of_vehicles', None)
    material = data.get('material', None)
    rate = data.get('rate', None)

    if not tonnage and not no_of_vehicles:
        return {'status': 'failure', 'msg': 'Enter Either Tonnage or No of Vehicles'}

    if data.get('from_city_id', None) == data.get('to_city_id', None):
        return {'status': 'failure', 'msg': 'From City and To City should be different'}

    client = get_or_none(Sme, id=int_or_none(data.get('client_id')))
    if not isinstance(client, Sme):
        return {'status': 'failure', 'msg': 'Incorrect client '}
    from_city = get_or_none(City, id=data.get('from_city_id', None))
    if not isinstance(from_city, City):
        return {'status': 'failure', 'msg': 'Incorrect from city '}
    to_city = get_or_none(City, id=data.get('to_city_id', None))
    if not isinstance(to_city, City):
        return {'status': 'failure', 'msg': 'Incorrect to city '}
    type_of_vehicle = get_or_none(VehicleCategory, id=int_or_none(data.get('vehicle_type_id')))
    aaho_office = get_or_none(AahoOffice, id=data.get('aaho_office_id', None))
    if not isinstance(aaho_office, AahoOffice):
        return {'status': 'failure', 'msg': 'Incorrect Aaho Office'}
    created_by = User.objects.get(username=user.username)
    if tonnage and not no_of_vehicles:
        no_of_vehicles = None
    if no_of_vehicles and not tonnage:
        tonnage = None
    if not rate:
        rate = None
    if not type_of_vehicle:
        type_of_vehicle = None
    else:
        if not isinstance(type_of_vehicle, VehicleCategory):
            return {'status': 'failure', 'msg': 'Incorrect vehicle type'}

    req_status = data.get('req_status', None)
    if req_status not in [x[0] for x in REQ_STATUS]:
        return {'status': 'failure', 'msg': 'Requirement status is wrong'}

    remark = data.get('remark', None)
    if not remark:
        remark = None

    cancel_reason = data.get('cancel_reason', None)
    if not cancel_reason:
        cancel_reason = None

    objects = {'status': 'success', 'client': client, 'from_shipment_date': from_shipment_date,
               'to_shipment_date': to_shipment_date, 'from_city': from_city, 'to_city': to_city,
               'aaho_office': aaho_office, 'tonnage': tonnage,
               'no_of_vehicles': no_of_vehicles, 'material': material, 'type_of_vehicle': type_of_vehicle,
               'rate': rate, 'created_by': created_by, 'req_status': req_status, 'remark': remark,
               'cancel_reason': cancel_reason}
    return objects

@api_post
@authenticated_user
def send_app_update_sms_to_fms_users(request):
    if not request.data.get('app_link'):
        return json_response({'status': 'failure', 'msg': 'Pls pass app link'})
    brokers = Broker.objects.all().exclude(deleted=True)
    mobiles_list = []
    for broker in brokers:
        if broker:
            usr = broker.name
            if any(g.name == 'fms' for g in usr.groups.all()):
                if broker.get_phone() not in mobiles_list:
                    mobiles_list.append(broker.get_phone())
    mobiles = ', '.join(mobiles_list)
    print(mobiles)
    template = "We have added new features to Aaho FMS app. Please click the link to update: {}".format(request.data.get('app_link'))
    print(template)
    send_sms(mobiles, template)
    return json_response({'status': 'success', 'msg': 'Sms sent successfully  to FMS users'})