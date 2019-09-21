from django.conf import settings
from django.core.mail.message import EmailMessage
from django.template import Template, Context

DOCUMENT_EMAIL_TEMPLATE = Template("""
Document Details for vehicle {{ vehicle_number }} -

VEHICLE DETAILS:

Vehicle Number - {{ vehicle_number }}
Vehicle Type - {{ vehicle_type }}

DOCUMENT DOWNLOAD LINK:

{{ download_link | safe }}

DOCUMENTS:

""")

RC_DOC_TEMPLATE = Template("""
Registration Certificate -

Image - {{ filename }}
{% if doc_id %}Certificate Number - {{doc_id}}\n{% endif %}{% if validity %}Validity - {{validity}}\n{% endif %}
{% if manufacture_year %}Registration Year - {{ manufacture_year }}{% endif %}
""")

PUC_DOC_TEMPLATE = Template("""
PUC Certificate -

Image - {{ filename }}
{% if doc_id %}Certificate Number - {{doc_id}}\n{% endif %}{% if validity %}Validity - {{validity}}\n{% endif %}
""")

FITNESS_DOC_TEMPLATE = Template("""
Fitness Certificate -

Image - {{ filename }}
{% if doc_id %}Certificate Number - {{doc_id}}\n{% endif %}{% if validity %}Validity - {{validity}}\n{% endif %}
""")

PERMIT_DOC_TEMPLATE = Template("""
Permit -

Image - {{ filename }}
{% if doc_id %}Permit Number - {{doc_id}}\n{% endif %}{% if validity %}Validity - {{validity}}\n{% endif %}
{% if permit_type %}Permit Type - {{ permit_type }}{% endif %}
""")

INSURANCE_DOC_TEMPLATE = Template("""
Insurance -

Image - {{ filename }}
{% if doc_id %}Insurance Number - {{doc_id}}\n{% endif %}{% if validity %}Validity - {{validity}}\n{% endif %}
{% if insurer_name %}Insurer - {{ insurer_name }}{% endif %}
""")

DL_DOC_TEMPLATE = Template("""
Driver's Licence -

Driver - {{ driver_name }}
Image - {{ filename }}
{% if doc_id %}Licence Number - {{doc_id}}\n{% endif %}{% if validity %}Validity - {{validity}}\n{% endif %}
{% if issue_location %}Issued in - {{ issue_location }}{% endif %}
""")

OWNER_DEC_DOC_TEMPLATE = Template("""
Owner's Declaration -

Owner - {{ owner_name }}
Image - {{ filename }}
{% if doc_id %}Declaration Number - {{doc_id}}\n{% endif %}{% if validity %}Validity - {{validity}}\n{% endif %}
""")

OWNER_PAN_DOC_TEMPLATE = Template("""
Owner's PAN Card -

Owner - {{ owner_name }}
Image - {{ filename }}
{% if doc_id %}PAN Number - {{doc_id}}\n{% endif %}{% if validity %}Validity - {{validity}}\n{% endif %}
""")

ACCOUNT_DOC_TEMPLATE = Template("""
Bank Account -

Account Holder's Name - {{ account_holder_name }}
Account Number - {{ account_number }}
Account Type - {{ account_type_verbose }}
{% if bank %}Bank - {{bank}}\n{% endif %}IFSC Code - {{ifsc}}
""")


def get_email_text(document_data, vehicle_data, extra, account_data):
    text = DOCUMENT_EMAIL_TEMPLATE.render(Context(vehicle_data))
    text += doc_string(document_data, extra, 'rc_doc', RC_DOC_TEMPLATE)
    text += doc_string(document_data, extra, 'insurance_doc', INSURANCE_DOC_TEMPLATE)
    text += doc_string(document_data, extra, 'permit_doc', PERMIT_DOC_TEMPLATE)
    text += doc_string(document_data, extra, 'fitness_doc', FITNESS_DOC_TEMPLATE)
    text += doc_string(document_data, extra, 'puc_doc', PUC_DOC_TEMPLATE)
    text += doc_string(document_data, extra, 'owner_pan_doc', OWNER_PAN_DOC_TEMPLATE)
    text += doc_string(document_data, extra, 'owner_dec_doc', OWNER_DEC_DOC_TEMPLATE)
    text += doc_string(document_data, extra, 'driver_dl_doc', DL_DOC_TEMPLATE)
    text += account_string(account_data)
    return text


def account_string(account_data):
    if not account_data:
        return ''
    text = '\n' + ACCOUNT_DOC_TEMPLATE.render(Context(account_data)).strip() + '\n\n'
    return text


def doc_string(data, extra, key, template):
    doc_data = data.get(key, None)
    if not doc_data or not doc_data.get('filename', None):
        return ''
    context = {}
    context.update(doc_data)
    context.update(extra)
    text = '\n' + template.render(Context(context)).strip() + '\n\n'
    return text


def doc_download_link(vid, key, excluded):
    ex_string = '' if not excluded else ','.join(excluded)
    return 'http://aaho.in/api/fms/vehicle/download-documents/%s/?k=%s&ex=%s' % (vid, key, ex_string)


def send_documents_email(vehicle, account, doc_data, emails, excluded, key):
    vehicle_data = {
        'vehicle_number': vehicle.number(),
        'vehicle_type': '' if not vehicle.vehicle_type else vehicle.vehicle_type.name(),
        'download_link': doc_download_link(vehicle.id, key, excluded)
    }
    extra = {
        'owner_name': None if not vehicle.owner else vehicle.owner.name,
        'driver_name': None if not vehicle.driver else vehicle.driver.name,
    }
    account_data = None if not account else account.to_json()

    body = get_email_text(doc_data, vehicle_data, extra, account_data)
    subject = '[Aaho] Documents for Vehicle %s' % vehicle.number()

    email = EmailMessage(subject, body, to=emails)
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()

