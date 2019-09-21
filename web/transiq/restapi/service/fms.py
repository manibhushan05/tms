from api.utils import parse_iso
from owner.vehicle_util import compare_format


def parse_vehicle_docs(data):
    parsed_data = {}
    parsed_data['id'] = data['id']
    parsed_data['vehicle_number'] = compare_format(data['vehicle_number'])
    parsed_data['status'] = data.get('status',None)
    parsed_data['bank_account'] = data.get('account_id', None)
    # parsed_data['vehicle_model'] = data['vehicle_model']
    doc_key = 'puc_doc'
    if doc_key in data:
        doc_id = data[doc_key].get('doc_id', None)
        validity = data[doc_key].get('validity', None)
        parsed_data['puc_certificate_validity_date'] = None if not validity else parse_iso(validity).strftime(
            '%d-%b-%Y')
        parsed_data['puc_certificate_number'] = doc_id

    doc_key = 'fitness_doc'
    if doc_key in data:
        doc_id = data[doc_key].get('doc_id', None)
        validity = data[doc_key].get('validity', None)
        parsed_data['fitness_certificate_validity_date'] = None if not validity else parse_iso(validity).strftime(
            '%d-%b-%Y')
        parsed_data['fitness_certificate_number'] = doc_id

    doc_key = 'permit_doc'
    if doc_key in data:
        doc_id = data[doc_key].get('doc_id', None)
        validity = data[doc_key].get('validity', None)
        permit_type = data[doc_key].get('permit_type', None)
        parsed_data['permit_validity'] = None if not validity else parse_iso(validity).strftime('%d-%b-%Y')
        parsed_data['permit'] = doc_id
        parsed_data['permit_type'] = permit_type

    doc_key = 'insurance_doc'
    if doc_key in data:
        doc_id = data[doc_key].get('doc_id', None)
        validity = data[doc_key].get('validity', None)
        insurer_name = data[doc_key].get('insurer_name', None)

        parsed_data['insurance_validity'] = None if not validity else parse_iso(validity).strftime('%d-%b-%Y')
        parsed_data['insurance_number'] = doc_id
        parsed_data['insurer'] = insurer_name

    doc_key = 'rc_doc'
    if doc_key in data:
        validity = data[doc_key].get('validity', None)
        registration_year = data[doc_key].get('manufacture_year', None)
        parsed_data['registration_validity'] = None if not validity else parse_iso(validity).strftime('%d-%b-%Y')
        parsed_data['registration_year'] = '{}-01-01'.format(registration_year)
    parsed_data['owner_data'] = {}
    doc_key = 'owner_pan_doc'
    if doc_key in data:
        parsed_data['owner_data']['pan'] = data[doc_key].get('doc_id', None)
    doc_key = 'owner_dec_doc'
    if doc_key in data:
        validity = data[doc_key].get('validity', None)
        parsed_data['owner_data']['declaration_validity'] = None if not validity else parse_iso(validity).strftime(
            '%d-%b-%Y')
    parsed_data['driver_data'] = {}
    doc_key = 'driver_dl_doc'
    if doc_key in data:
        validity = data[doc_key].get('validity', None)
        parsed_data['driver_data']['driving_licence_validity'] = None if not validity else parse_iso(validity).strftime(
            '%d-%b-%Y')
        parsed_data['driver_data']['driving_licence_number'] = data[doc_key].get('doc_id', None)
    return parsed_data


def parse_supplier_vehicles_docs(data):
    parsed_data = {}
    parsed_data['id'] = data['id']
    parsed_data['vehicle_number'] = compare_format(data['vehicle_number'])
    parsed_data['status'] = data['status']
    parsed_data['bank_account'] = data.get('account_id', None)
    # parsed_data['vehicle_model'] = data['vehicle_model']
    doc_key = 'puc_doc'
    if doc_key in data:
        doc_id = data[doc_key].get('doc_id', None)
        validity = data[doc_key].get('validity', None)
        parsed_data['puc_certificate_validity_date'] = None if not validity else parse_iso(validity).strftime(
            '%d-%b-%Y')
        parsed_data['puc_certificate_number'] = doc_id

    doc_key = 'fitness_doc'
    if doc_key in data:
        doc_id = data[doc_key].get('doc_id', None)
        validity = data[doc_key].get('validity', None)
        parsed_data['fitness_certificate_validity_date'] = None if not validity else parse_iso(validity).strftime(
            '%d-%b-%Y')
        parsed_data['fitness_certificate_number'] = doc_id

    doc_key = 'permit_doc'
    if doc_key in data:
        doc_id = data[doc_key].get('doc_id', None)
        validity = data[doc_key].get('validity', None)
        permit_type = data[doc_key].get('permit_type', None)
        parsed_data['permit_validity'] = None if not validity else parse_iso(validity).strftime('%d-%b-%Y')
        parsed_data['permit'] = doc_id
        parsed_data['permit_type'] = permit_type

    doc_key = 'insurance_doc'
    if doc_key in data:
        doc_id = data[doc_key].get('doc_id', None)
        validity = data[doc_key].get('validity', None)
        insurer_name = data[doc_key].get('insurer_name', None)

        parsed_data['insurance_validity'] = None if not validity else parse_iso(validity).strftime('%d-%b-%Y')
        parsed_data['insurance_number'] = doc_id
        parsed_data['insurer'] = insurer_name

    doc_key = 'rc_doc'
    if doc_key in data:
        validity = data[doc_key].get('validity', None)
        registration_year = data[doc_key].get('manufacture_year', None)
        parsed_data['registration_validity'] = None if not validity else parse_iso(validity).strftime('%d-%b-%Y')
        parsed_data['registration_year'] = '{}-01-01'.format(registration_year)
    parsed_data['owner_data'] = {}
    doc_key = 'owner_pan_doc'
    if doc_key in data:
        parsed_data['owner_data']['pan'] = data[doc_key].get('doc_id', None)
    doc_key = 'owner_dec_doc'
    if doc_key in data:
        validity = data[doc_key].get('validity', None)
        parsed_data['owner_data']['declaration_validity'] = None if not validity else parse_iso(validity).strftime(
            '%d-%b-%Y')
    parsed_data['driver_data'] = {}
    doc_key = 'driver_dl_doc'
    if doc_key in data:
        validity = data[doc_key].get('validity', None)
        parsed_data['driver_data']['driving_licence_validity'] = None if not validity else parse_iso(validity).strftime(
            '%d-%b-%Y')
        parsed_data['driver_data']['driving_licence_number'] = data[doc_key].get('doc_id', None)
    return parsed_data


def parse_profile_data(data):
    parsed_data = {}
    profile_data = {}
    broker_data = {}
    owner_data = {}
    if 'name' in data:
        profile_data['name'] = data.get('name', None)
    if 'contact_person_name' in data:
        profile_data['contact_person_name'] = data.get('contact_person_name', None)
    if 'phone' in data:
        profile_data['phone'] = data.get('phone', None)
        profile_data['contact_person_phone'] = data.get('phone', None)
    if 'email' in data:
        profile_data['email'] = data.get('email', None)
    if 'designation' in data:
        profile_data['designation'] = data.get('designation', None)
    if 'address' in data:
        profile_data['address'] = data.get('address', None)
    if 'city' in data:
        profile_data['city'] = data.get('city', None)
        broker_data['city'] = data.get('city', None)

    doc_key = 'pan_doc'
    if doc_key in data:
        broker_data['pan'] = data[doc_key].get('doc_id', None)
        owner_data['pan'] = data[doc_key].get('doc_id', None)
    doc_key = 'dec_doc'
    if doc_key in data:
        validity = data[doc_key].get('validity', None)
        owner_data['declaration_validity'] = None if not validity else parse_iso(validity).strftime(
            '%d-%b-%Y')
    parsed_data['profile_data'] = profile_data
    parsed_data['broker_data'] = broker_data
    parsed_data['owner_data'] = owner_data
    return parsed_data
