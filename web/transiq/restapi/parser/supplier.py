from django.contrib.auth.models import User

from owner.vehicle_util import compare_format
from restapi.helper_api import generate_random_lowercase_string, generate_random_uppercase_string
from restapi.utils import get_or_none
from supplier.models import Supplier
from utils.models import City


def generate_supplier_code():
    code = generate_random_uppercase_string(N=4)
    while Supplier.objects.filter(code=code).exists():
        code = generate_random_uppercase_string(N=4)
    return code


def generate_username():
    username = generate_random_lowercase_string(N=20)
    while User.objects.filter(username=username).exists():
        username = generate_random_lowercase_string(N=20)
    return username


def parse_supplier_registration_data(data):
    parsed_data = {
        "user": {
            "username": generate_username(),
            "password": 'Yt@U7866TR.12'
        },
        'profile': {
            'name': data.get('supplier_name', None),
            'contact_person_name': data.get('contact_person_name', None),
            'contact_person_phone': data.get('contact_person_phone', None),
            'phone': data.get('phone', None),
            'alternate_phone': data.get('alternate_phone', None),
            'email': data.get('email', None),
            'alternate_email': data.get('alternate_email', None),
            'address': data.get('address', None),
            'pin': data.get('pin', None),
            'comment': data.get('comment', None),
            'city': data.get('supplier_city', None),
        },
        'supplier': {
            'address': data.get('address', None),
            'pin': data.get('pin', None),
            'pan': data.get('pan', None),
            'code': generate_supplier_code(),
            'route': data.get('route', None),
            'created_by': data.get('created_by', None),
            'changed_by': data.get('changed_by', None),
            'city': data.get('supplier_city', None),
            'aaho_office': data.get('aaho_office', None),
            'aaho_poc': data.get('aaho_poc', None),
            'serving_states': data.get('serving_states', None),
        },
        'contact_person': [
            {
                "user": {
                    "username": generate_username(),
                    "password": 'Yt@U7866TR.12'
                },
                'profile': {
                    'name': row.get('name', None),
                    'contact_person_name': row.get('contact_person_name', None),
                    'contact_person_phone': row.get('contact_person_phone', None),
                    'phone': row.get('phone', None),
                    'alternate_phone': row.get('alternate_phone', None),
                    'email': row.get('email', None),
                    'alternate_email': row.get('alternate_email', None),
                    'address': row.get('address', None),
                    'pin': row.get('pin', None),
                    'comment': row.get('comment', None),
                    'city': data.get('supplier_city', None),
                },
            } for row in data.get('contact_person', [])
        ]

    }
    return parsed_data


def parse_supplier_update_data(data):
    parsed_data = {
        'profile': {
            'name': data.get('supplier_name', None),
            'contact_person_name': data.get('contact_person_name', None),
            'contact_person_phone': data.get('contact_person_phone', None),
            'phone': data.get('phone', None),
            'alternate_phone': data.get('alternate_phone', None),
            'email': data.get('email', None),
            'alternate_email': data.get('alternate_email', None),
            'address': data.get('address', None),
            'pin': data.get('pin', None),
            'comment': data.get('comment', None),
            'city': data.get('supplier_city', None),
        },
        'supplier': {
            'address': data.get('address', None),
            'pin': data.get('pin', None),
            'pan': data.get('pan', None),
            'route': data.get('route', None),
            'changed_by': data.get('changed_by', None),
            'city': data.get('supplier_city', None),
            'aaho_office': data.get('aaho_office', None),
            'aaho_poc': data.get('aaho_poc', None),
            'serving_states': data.get('serving_states', None),
        },
        'contact_person': [
            {
                'name': row.get('name', None),
                'contact_person_name': row.get('contact_person_name', None),
                'contact_person_phone': row.get('contact_person_phone', None),
                'phone': row.get('phone', None),
                'alternate_phone': row.get('alternate_phone', None),
                'email': row.get('email', None),
                'alternate_email': row.get('alternate_email', None),
                'address': row.get('address', None),
                'pin': row.get('pin', None),
                'comment': row.get('comment', None),
                'city': data.get('supplier_city', None),

            } for row in data.get('contact_person', [])
        ]

    }
    return parsed_data


def parse_driver_registration_data(data):
    if 'driver_phone' in data and data.get('driver_phone'):
        phone = data.get('driver_phone')[0].get('phone', None)
    else:
        phone = None
    if 'dl_city' in data:
        city = get_or_none(City, id=data.get('dl_city'))
        if isinstance(city, City):
            driving_licence_location = city.name
        else:
            driving_licence_location = None
    else:
        driving_licence_location = None

    parsed_data = {
        "user": {
            "username": generate_username(),
            "password": 'Yt@U7866TR.12'
        },
        'profile': {
            'name': data.get('driver_name', None),
            'phone': phone
        },
        'driver': {
            'driving_licence_number': data.get('dl_number', None),
            'driving_licence_validity': data.get('dl_validity', None),
            'route': data.get('driver_route', None),
            'created_by': data.get('created_by', None),
            'changed_by': data.get('changed_by', None),
            'driving_licence_location': driving_licence_location,
        },
        'driver_phone': [
            {
                'phone': row.get('phone', None),
                'created_by': data.get('created_by', None),
                'changed_by': data.get('changed_by', None)
            } for row in data.get('driver_phone', [])
        ]
    }
    return parsed_data


def parse_driver_update_form(data):
    parsed_data = {
        'profile': {
            'name': data.get('name', None),
            'phone': data.get('driver_phone')[0].get('phone', None) if data.get('driver_phone', []) else None
        },
        'driver_data': {
            'driving_licence_number': data.get('driving_licence_number', None),
            'driving_licence_validity': data.get('driving_licence_validity', None),
            'route': data.get('route', None),
            "changed_by": data.get("changed_by", None)
        }
    }
    return parsed_data


def parse_vehicle_registration_data(data):
    parsed_data = {
        'vehicle': {
            'vehicle_number': compare_format(data.get('vehicle_number', None)),
            'vehicle_capacity': data.get('vehicle_capacity', None),
            'chassis_number': data.get('chassis_number', None),
            'engine_number': data.get('engine_number', None),
            'registration_year': '01-Jan-{}'.format(data.get('registration_year', None).strip()) if data.get(
                'registration_year', None) else None,
            'registration_validity': data.get('registration_validity', None),
            'gps_enabled': data.get('gps_enabled', False),
            'vehicle_type': data.get('vehicle_type', None),
            'body_type': data.get('body_type', None),
            'created_by': data.get('created_by', None),
            'changed_by': data.get('changed_by', None),
        },
        'insurance': {
            'insurance_number': data.get('insurance_number', None),
            'issued_date': data.get('insurance_issued_on', None),
            'expired_by': data.get('insurance_validity', None),
            'created_by': data.get('created_by', None),
            'changed_by': data.get('changed_by', None),
        },
        'permit': {
            'permit_number': data.get('permit', None),
            'permit_type': data.get('permit_type', None),
            'issued_date': data.get('permit_issued_on', None),
            'expiry_date': data.get('permit_validity', None),
            'created_by': data.get('created_by', None),
            'changed_by': data.get('changed_by', None),
        },
        'fitness': {
            'serial_number': data.get('fitness_certificate_number', None),
            'issued_date': data.get('fitness_certificate_issued_on', None),
            'expiry_date': data.get('fitness_certificate_validity_date', None),
            'created_by': data.get('created_by', None),
            'changed_by': data.get('changed_by', None),
        },
        'puc': {
            'serial_number': data.get('puc_certificate_number', None),
            'issued_date': data.get('puc_certificate_issued_on', None),
            'expiry_date': data.get('puc_certificate_validity_date', None),
            'created_by': data.get('created_by', None),
            'changed_by': data.get('changed_by', None),
        },
        'vehicle_supplier': {
            'ownership': 'O',
            'supplier': data.get('owner', None),
            'created_by': data.get('created_by', None),
            'changed_by': data.get('changed_by', None),
        }
    }
    return parsed_data


def parse_vehicle_update_data(data):
    parsed_data = {
        'vehicle': {
            'vehicle_number': compare_format(data.get('vehicle_number', None)),
            'vehicle_capacity': data.get('vehicle_capacity', None),
            'chassis_number': data.get('chassis_number', None),
            'engine_number': data.get('engine_number', None),
            'registration_year': '01-Jan-{}'.format(data.get('registration_year', None).strip()) if data.get(
                'registration_year', None) else None,
            'registration_validity': data.get('registration_validity', None),
            'gps_enabled': data.get('gps_enabled', False),
            'body_type': data.get('body_type', None),
            'vehicle_type': data.get('vehicle_type', None),
            'changed_by': data.get('changed_by', None),
        },
        'insurance': {
            'vehicle_id': data.get('vehicle_id', None),
            'insurance_number': data.get('insurance_number', None),
            'issued_date': data.get('insurance_issued_on', None),
            'expired_by': data.get('insurance_validity', None),
            'changed_by': data.get('changed_by', None),
        },
        'permit': {
            'vehicle_id': data.get('vehicle_id', None),
            'permit_number': data.get('permit', None),
            'permit_type': data.get('permit_type', None),
            'issued_date': data.get('permit_issued_on', None),
            'expiry_date': data.get('permit_validity', None),
            'changed_by': data.get('changed_by', None),
        },
        'fitness': {
            'vehicle_id': data.get('vehicle_id', None),
            'serial_number': data.get('fitness_certificate_number', None),
            'issued_date': data.get('fitness_certificate_issued_on', None),
            'expiry_date': data.get('fitness_certificate_validity_date', None),
            'changed_by': data.get('changed_by', None),
        },
        'puc': {
            'vehicle_id': data.get('vehicle_id', None),
            'serial_number': data.get('puc_certificate_number', None),
            'issued_date': data.get('puc_certificate_issued_on', None),
            'expiry_date': data.get('puc_certificate_validity_date', None),
            'changed_by': data.get('changed_by', None),
        },
        'vehicle_supplier': {
            'vehicle_id': data.get('vehicle_id', None),
            'ownership': 'O',
            'supplier': data.get('owner', None),
            'changed_by': data.get('changed_by', None),
        }
    }
    return parsed_data
