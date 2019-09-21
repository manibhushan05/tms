from restapi.helper_api import generate_username


def user_parser(data):
    if isinstance(data, dict):
        return {
            'username': generate_username(
                name=data.get('name', None), phone=data.get('phone', None), email=data.get('email', None)
            ),
            'password': '8UyT&RT4654',
            'profile': {
                'name': data.get('name', None),
                'contact_person_name': data.get('contact_person_name', None),
                'contact_person_phone': data.get('contact_person_phone', None),
                'phone': data.get('phone', None),
                'alternate_phone': data.get('alternate_phone', None),
                'email': data.get('email', None),
                'alternate_email': data.get('alternate_email', None),
                'address': data.get('address', None),
                'pin': data.get('pin', None),
                'designation': data.get('designation', None),
                'organization': data.get('organization', None),
                'comment': data.get('comment', None),
                'city': data.get('city', None),
            }
        }
    return None
