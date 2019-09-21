import re

from api.helper import json_success_response, json_400_incorrect_use, json_error_response
from api.utils import get_or_none, to_int
from api.validators import VEHICLE_NUMBER
from owner.models import Vehicle
from owner.vehicle_util import compare_format


def vehicle_data(request):
    vehicle_id = request.GET.get('vehicle_id')
    vehicle_number_pattern = re.compile(VEHICLE_NUMBER[1:-2], re.IGNORECASE)
    if vehicle_id.isdigit():
        if isinstance(get_or_none(Vehicle, id=vehicle_id), Vehicle):
            vehicle = Vehicle.objects.get(id=vehicle_id)
        else:
            return json_error_response(msg="{} does not exits".format(vehicle_id), status=400)
    elif isinstance(vehicle_id, str):
        if vehicle_number_pattern.match(vehicle_id):
            if Vehicle.objects.filter(vehicle_number=compare_format(vehicle_id)).exists():
                vehicle = Vehicle.objects.filter(vehicle_number=compare_format(vehicle_id)).latest('id')
            else:
                return json_error_response(msg="{} does not exits".format(vehicle_id), status=400)
        else:
            vehicle = None
    else:
        vehicle = None

    if isinstance(vehicle, Vehicle):
        data = {}
        if vehicle.owner:
            data['owner'] = {'id': vehicle.owner.id, 'name': vehicle.owner.get_name(),
                             'phone': vehicle.owner.get_phone()}
        else:
            data['owner'] = {}
        if vehicle.vehicle_type:
            data['vehicle_category'] = {'id': vehicle.vehicle_type.id,
                                        'vehicle_category': vehicle.vehicle_type.vehicle_category}
        else:
            data['vehicle_category'] = {}
        return json_success_response(msg=data)
    else:
        return json_400_incorrect_use()
