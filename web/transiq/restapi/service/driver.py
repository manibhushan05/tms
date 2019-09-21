from api.utils import parse_iso


def parse_driver_docs(data):
    parsed_data = {}
    parsed_data['id'] = data.get('id', None)
    parsed_data['name'] = data.get('name', None)
    parsed_data['phone'] = data.get('phone', None)
    parsed_data['account_details'] = data.get('account_id', None)
    doc_key = 'pan_doc'
    if doc_key in data:
        doc_id = data[doc_key].get('doc_id', None)
        parsed_data['pan'] = doc_id
    doc_key = 'dl_doc'
    if doc_key in data:
        validity = data[doc_key].get('validity', None)
        parsed_data['driving_licence_validity'] = None if not validity else parse_iso(validity).strftime(
            '%d-%b-%Y')
        parsed_data['driving_licence_number'] = data[doc_key].get('doc_id', None)
    return parsed_data


def parse_supplier_driver_docs(data):
    parsed_data = {}
    parsed_data['id'] = data.get('id', None)
    parsed_data['user_data'] = {'name': data.get('name', None), 'phone': data.get('phone', None)}
    parsed_data['account_details'] = data.get('account_id', None)
    doc_key = 'pan_doc'
    if doc_key in data:
        doc_id = data[doc_key].get('doc_id', None)
        parsed_data['pan'] = doc_id
    doc_key = 'dl_doc'
    if doc_key in data:
        validity = data[doc_key].get('validity', None)
        parsed_data['driving_licence_validity'] = None if not validity else parse_iso(validity).strftime(
            '%d-%b-%Y')
        parsed_data['driving_licence_number'] = data[doc_key].get('doc_id', None)
    return parsed_data
