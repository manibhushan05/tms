from broker.models import Broker
from owner.models import Owner
from sme.models import Sme
from utils.models import State


def parse_update_owner_data(data, id):
    '''

    :param data: {
              "owner_id": "1704",
              "name": "Bombay Uttranchal",
              "phone": "9320548368",
              "pan": "cbapk7807p",
              "route": "noidas",
              "vehicles_detail": [
                "4483",
                "4437",
                "4405",
                "4349",
                "4345",
                "4318"
              ],
              "contact_person_name": "Sharma hgg",
              "contact_person_phone": "9320548368",
              "alternate_phone": "89789374238",
              "owner_address": "owner addresss",
              "city": "326",
              "pin": "400073",
              "remarks": "Remarks"
            }
    :return:
    '''
    owner = Owner.objects.get(id=id)
    parsed_data = {
        'pan': data.get('pan', None),
        'owner_address': data.get('owner_address', None),
        'route_temp': data.get('route', None),
        'city': data.get('city', owner.city_id),
        'pin': data.get('pin', None),
        'profile_data': {
            'name': data.get('name', None),
            'contact_person_name': data.get('contact_person_name', None),
            'phone': data.get('phone', None),
            'contact_person_phone': data.get('contact_person_phone', None),
            'alternate_phone': data.get('alternate_phone', None),
            'comment': data.get('remarks', None),
            'address': data.get('owner_address', None),
            'city': data.get('city', None),
        },
        'vehicles_detail': data.get('vehicles_detail', [])
    }
    return parsed_data


def parse_update_sme_data(data, id):
    '''

    :param data: {
          'customer_id': '690',
          'is_gst_applicable': 'yes',
          'gstin': '37AJUPR6135N1Z7',
          'company_name': 'Sri Hanuman Agencies',
          'company_code': 'SKA',
          'credit_period': '1',
          'aaho_poc': '23',
          'contact_person_name': 'Ramesh',
          'contact_person_number': '9515453270',
          'alternate_number': '8767834323',
          'email_id': 'mani@aaho.in',
          'company_address': 'D wo. 6 - 46/ Sri hanuman Residency, Gendada,',
          'city': '493',
          'aaho_office': '3',
          'pin': '530045',
          'remarks': 'renmam'
        }
    :return:
    '''
    sme = Sme.objects.get(id=id)
    parsed_data = {
        'aaho_office': data.get('aaho_office', sme.aaho_office_id),
        'customer_address': data.get('customer_address', None),
        'city': data.get('city', sme.city_id),
        'pin': data.get('pin', None),
        'gstin': data.get('gstin', sme.gstin),
        'is_gst_applicable': data.get('is_gst_applicable', sme.is_gst_applicable),
        'aaho_poc': data.get('aaho_poc', sme.aaho_poc_id),
        'credit_period': data.get('credit_period', None),
        'profile_data': {
            'name': data.get('company_name', None),
            'contact_person_name': data.get('contact_person_name', None),
            'contact_person_phone': data.get('contact_person_number', None),
            'alternate_phone': data.get('alternate_number', None),
            'comment': data.get('remarks', None),
            'address': data.get('customer_address', None),
            'email': data.get('email_id', None),
            'city': data.get('city', None),
        }
    }
    return parsed_data


def parse_broker_update_data(data, id):
    if "destination_state" in data.keys():
        destination_states = data.pop('destination_state')
        if destination_states and 'select_all' in destination_states:
            destination_states = State.objects.values_list('id', flat=True)
    else:
        destination_states = []
    broker = Broker.objects.get(id=id)
    parsed_data = {
        'pan': data.get('pan', None),
        'destination_state': destination_states,
        'city': data.get('city', broker.city_id),
        'route': data.get('route', None),
        'aaho_office': data.get('aaho_office', broker.aaho_office_id),
        'changed_by': data.get('changed_by', broker.changed_by.username if broker.changed_by else None),
        'profile_data': {
            'name': data.get('supplier_name', None),
            'contact_person_name': data.get('contact_person_name', None),
            'contact_person_phone': data.get('contact_person_phone', None),
            'phone': data.get('contact_person_phone', None),
            'alternate_phone': data.get('alternate_phone', None),
            'comment': data.get('remarks', None),
            'email': data.get('email', None),
            'city': data.get('city', None),
        }
    }
    return parsed_data
