import random
import re
import string
from datetime import datetime, timedelta
from random import randint
from sqlite3 import IntegrityError

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.helper import EMP_GROUP2, EMP_GROUP3, EMP_GROUP4, EMP_GROUP1
from api.utils import get_or_none, to_int
from broker.models import Broker
from driver.models import OTP
from employee.models import Employee
from fms.models import Requirement
from notification.models import MobileDevice
from owner.models import Owner
from owner.vehicle_util import compare_format
from restapi.dynamo.config import DynamoTablesEnvConfiguration
from restapi.dynamo.utils import DynamoTable
from restapi.tasks import send_otp_sms, send_otp_email
from restapi.utils import calculate_sundays_between_dates
from sme.models import Sme
from supplier.models import Supplier
from team.models import CreditNoteCustomerDirectAdvance, DebitNoteSupplier, DebitNoteCustomer, CreditNoteCustomer, \
    CreditNoteSupplier, DebitNoteSupplierDirectAdvance, ManualBooking, Invoice, OutWardPayment, \
    PendingInwardPaymentEntry
from utils.models import City, AahoOffice, AahoHolidays, BankHolidays

DATETIME_FORMAT = '%d-%b-%Y %H:%M %p'
DATE_FORMAT = '%d-%b-%Y'


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


def generate_otp(mobile):
    otp = OTP.generate(mobile)
    return otp


def task_send_otp_sms(mobile, otp):
    text = '%s is your OTP ' % otp
    send_otp_sms(mobile, text)


def task_send_otp_email(email, otp):
    text = '%s is your OTP ' % otp
    send_otp_email(email, text)


def get_supplier_user_data(user, profile, supplier):
    data = {
        'name': user.first_name or '',
        'contact_person_name': profile.contact_person_name or '',
        'address': supplier.address,
        'username': user.username or '',
        'phone': profile.phone or '',
        'email': profile.email or '',
        'designation': profile.designation or '',
        'id': user.id,
        'city': {'id': supplier.city.id, 'name': supplier.city.name} if isinstance(supplier.city, City) else {}
    }
    supplier = get_or_none(Supplier, user=user)
    if isinstance(supplier, Supplier):
        owner_docs = []
        pan_doc = supplier.supplier_files.filter(document_category='PAN').exclude(s3_upload=None).last()
        if pan_doc:
            owner_docs.append(
                {'id': pan_doc.id, 'url': pan_doc.s3_upload.public_url(),
                 'document_category': pan_doc.document_category,
                 'document_category_display': pan_doc.get_document_category_display(),
                 'thumb_url': pan_doc.s3_upload.public_url(),
                 'bucket': pan_doc.s3_upload.bucket,
                 'folder': pan_doc.s3_upload.folder,
                 'uuid': pan_doc.s3_upload.uuid,
                 'filename': pan_doc.s3_upload.filename,
                 'validity': None,
                 }
            )
        dec_doc = supplier.supplier_files.filter(document_category='DEC').exclude(s3_upload=None).last()
        if dec_doc:
            owner_docs.append(
                {'id': dec_doc.id, 'url': dec_doc.s3_upload.public_url(),
                 'document_category': dec_doc.document_category,
                 'document_category_display': dec_doc.get_document_category_display(),
                 'thumb_url': dec_doc.s3_upload.public_url(),
                 'bucket': dec_doc.s3_upload.bucket,
                 'folder': dec_doc.s3_upload.folder,
                 'uuid': dec_doc.s3_upload.uuid,
                 'filename': dec_doc.s3_upload.filename,
                 'validity': None,
                 }
            )
        data['pan'] = supplier.pan
        data['declaration_validity'] = '12-Mar-2019'
    else:
        owner_docs = []
    data['owner_docs'] = owner_docs
    return data


def get_broker_user_data(user, profile, broker):
    data = {
        'name': profile.name or '',
        'contact_person_name': profile.contact_person_name or '',
        'address': profile.address,
        'username': user.username or '',
        'phone': profile.phone or '',
        'email': profile.email or '',
        'designation': profile.designation or '',
        'id': user.id,
        'city': {'id': broker.city.id, 'name': broker.city.name} if isinstance(broker.city, City) else {}
    }
    owner = get_or_none(Owner, name=user)
    if isinstance(owner, Owner):
        owner_docs = []
        pan_doc = owner.owner_files.filter(document_category='PAN').exclude(s3_upload=None).last()
        if pan_doc:
            owner_docs.append(
                {'id': pan_doc.id, 'url': pan_doc.s3_upload.public_url(),
                 'document_category': pan_doc.document_category,
                 'document_category_display': pan_doc.get_document_category_display(),
                 'thumb_url': pan_doc.s3_upload.public_url(),
                 'bucket': pan_doc.s3_upload.bucket,
                 'folder': pan_doc.s3_upload.folder,
                 'uuid': pan_doc.s3_upload.uuid,
                 'filename': pan_doc.s3_upload.filename,
                 'validity': None,
                 }
            )
        dec_doc = owner.owner_files.filter(document_category='DEC').exclude(s3_upload=None).last()
        if dec_doc:
            owner_docs.append(
                {'id': dec_doc.id, 'url': dec_doc.s3_upload.public_url(),
                 'document_category': dec_doc.document_category,
                 'document_category_display': dec_doc.get_document_category_display(),
                 'thumb_url': dec_doc.s3_upload.public_url(),
                 'bucket': dec_doc.s3_upload.bucket,
                 'folder': dec_doc.s3_upload.folder,
                 'uuid': dec_doc.s3_upload.uuid,
                 'filename': dec_doc.s3_upload.filename,
                 'validity': None,
                 }
            )
        data['pan'] = owner.pan
        data['declaration_validity'] = owner.declaration_validity.strftime(
            DATE_FORMAT) if owner.declaration_validity else None
    else:
        owner_docs = []
    data['owner_docs'] = owner_docs
    return data


def get_employee_user_data(user, profile, employee):
    if not user.first_name and not user.last_name:
        full_name = ''
    else:
        full_name = user.first_name or ''
        full_name = full_name + ' ' + user.last_name or ''
    data = {
        'employee_id': employee.id,
        'full_name': full_name,
        'contact_name': profile.contact_person_name or '',
        'username': user.username or '',
        'phone': profile.phone or '',
        'email': profile.email or '',
        'designation': profile.designation or '',
        'id': user.id
    }
    return data


def generate_credit_note_customer_serial_number(sme_id):
    sme = get_or_none(Sme, id=sme_id)
    if isinstance(sme, Sme):
        code = sme.company_code
    else:
        code = 'XXX'
    if CreditNoteCustomer.objects.exists():
        serial_number = 'CNC/{}{}{}'.format(code, datetime.now().strftime('%y%m'),
                                            str(CreditNoteCustomer.objects.last().id + 1).zfill(4))

    else:
        serial_number = 'CNC/{}{}{}'.format(code, datetime.now().strftime('%y%m'), '0001')
    return serial_number


def generate_credit_note_supplier_serial_number(supplier_id):
    supplier = get_or_none(Supplier, id=supplier_id)
    if isinstance(supplier, Supplier) and supplier.code:
        code = supplier.code
    else:
        code = 'XXXX'
    if CreditNoteSupplier.objects.exists():
        serial_number = 'CNS/{}{}{}'.format(code, datetime.now().strftime('%y%m'),
                                            str(CreditNoteSupplier.objects.last().id + 1).zfill(4))

    else:
        serial_number = 'CNS/{}{}{}'.format(code, datetime.now().strftime('%y%m'), '0001')
    return serial_number


def generate_debit_note_customer_serial_number(sme_id):
    sme = get_or_none(Sme, id=sme_id)
    if isinstance(sme, Sme):
        code = sme.company_code
    else:
        code = 'XXX'
    if DebitNoteCustomer.objects.exists():
        serial_number = 'DNC/{}{}{}'.format(code, datetime.now().strftime('%y%m'),
                                            str(DebitNoteCustomer.objects.last().id + 1).zfill(4))

    else:
        serial_number = 'DNC/{}{}{}'.format(code, datetime.now().strftime('%y%m'), '0001')
    return serial_number


def generate_debit_note_supplier_serial_number(supplier_id):
    supplier = get_or_none(Supplier, id=supplier_id)
    if isinstance(supplier, Supplier) and supplier.code:
        code = supplier.code
    else:
        code = 'XXXX'
    if DebitNoteSupplier.objects.exists():
        serial_number = 'DNS/{}{}{}'.format(code, datetime.now().strftime('%y%m'),
                                            str(DebitNoteSupplier.objects.last().id + 1).zfill(4))
    else:
        serial_number = 'DNS/{}{}{}'.format(code, datetime.now().strftime('%y%m'), '0001')
    return serial_number


def generate_credit_note_customer_direct_advance_serial_number(sme_id):
    sme = get_or_none(Sme, id=sme_id)
    if isinstance(sme, Sme):
        code = sme.company_code
    else:
        code = 'XXX'
    if CreditNoteCustomerDirectAdvance.objects.exists():
        serial_number = 'CNCA/{}{}{}'.format(code, datetime.now().strftime('%y%m'),
                                             str(CreditNoteCustomerDirectAdvance.objects.last().id + 1).zfill(4))
    else:
        serial_number = 'CNCA/{}{}{}'.format(code, datetime.now().strftime('%y%m'), '0001')
    return serial_number


def generate_debit_note_supplier_direct_advance_serial_number(supplier_id):
    supplier = get_or_none(Supplier, id=supplier_id)
    if isinstance(supplier, Supplier) and supplier.code:
        code = supplier.code
    else:
        code = 'XXXX'
    if DebitNoteSupplierDirectAdvance.objects.exists():
        serial_number = 'DNSA/{}{}{}'.format(code, datetime.now().strftime('%y%m'),
                                             str(DebitNoteSupplierDirectAdvance.objects.last().id + 1).zfill(4))
    else:
        serial_number = 'DNSA/{}{}{}'.format(code, datetime.now().strftime('%y%m'), '0001')
    return serial_number


def aaho_office(user):
    employee = get_or_none(Employee, username=user)
    if employee:
        return employee.office_multiple.all()
    else:
        raise PermissionDenied


def manual_booking_id_list(user):
    if isinstance(user, User):
        office_obj = aaho_office(user=user)
        if any([g in [EMP_GROUP2, EMP_GROUP3] for g in user.groups.values_list('name', flat=True)]):
            booking_ids = ManualBooking.objects.filter(
                Q(source_office__in=office_obj) | Q(destination_office__in=office_obj)).exclude(
                Q(booking_status__icontains='cancelled') | Q(deleted=True)).values_list('id', flat=True)
        elif any([g in [EMP_GROUP1, EMP_GROUP4] for g in user.groups.values_list('name', flat=True)]):
            booking_ids = ManualBooking.objects.values_list('id', flat=True).exclude(
                Q(booking_status__icontains='cancelled') | Q(deleted=True)).values_list('id', flat=True)
        else:
            booking_ids = []
        return booking_ids
    else:
        raise PermissionDenied


def manual_booking_id_src_aaho_list(user):
    if isinstance(user, User):
        office_obj = aaho_office(user=user)
        if any([g in [EMP_GROUP2, EMP_GROUP3] for g in user.groups.values_list('name', flat=True)]):
            booking_ids = ManualBooking.objects.filter(
                Q(source_office__in=office_obj)).exclude(
                Q(booking_status__icontains='cancelled') | Q(deleted=True)).values_list('id', flat=True)
        elif any([g in [EMP_GROUP1, EMP_GROUP4] for g in user.groups.values_list('name', flat=True)]):
            booking_ids = ManualBooking.objects.values_list('id', flat=True).exclude(
                Q(booking_status__icontains='cancelled') | Q(deleted=True)).values_list('id', flat=True)
        else:
            booking_ids = []
        return booking_ids
    else:
        raise PermissionDenied


def manual_booking_id_dest_aaho_list(user):
    if isinstance(user, User):
        office_obj = aaho_office(user=user)
        if any([g in [EMP_GROUP2, EMP_GROUP3] for g in user.groups.values_list('name', flat=True)]):
            booking_ids = ManualBooking.objects.filter(
                Q(destination_office__in=office_obj)).exclude(
                Q(booking_status__icontains='cancelled') | Q(deleted=True)).values_list('id', flat=True)
        elif any([g in [EMP_GROUP1, EMP_GROUP4] for g in user.groups.values_list('name', flat=True)]):
            booking_ids = ManualBooking.objects.values_list('id', flat=True).exclude(
                Q(booking_status__icontains='cancelled') | Q(deleted=True)).values_list('id', flat=True)
        else:
            booking_ids = []
        return booking_ids
    else:
        raise PermissionDenied


def create_user(phone, name, email=None):
    password = "X@RWERT21RW!@#"
    name = re.sub('[^A-Za-z]+', '', name if name else '').lower()
    phone = re.sub('[^0-9]+', '', str(phone))
    try:
        validate_email(email)
    except ValidationError:
        email = None
    else:
        email = email
    try:
        user = User.objects.create_user(username=email, password=password)
    except (IntegrityError, ValueError):
        try:
            user = User.objects.create_user(username=re.sub('[^0-9]+', '', str(phone)), password=password)
        except (IntegrityError, ValueError):
            try:
                user = User.objects.create_user(username=name, password=password)
            except (IntegrityError, ValueError):
                while True:
                    try:
                        name = '{}{}'.format(name, ''.join(random.choice(string.ascii_lowercase) for _ in range(6)))
                        user = User.objects.create_user(username=re.sub('[^A-Za-z]+', '', name), password=password)
                        break
                    except (IntegrityError, ValueError):
                        continue
    return user


def generate_username(name, phone, email=None):
    name = re.sub('[^A-Za-z]+', '', name if name else '').lower()
    phone = re.sub('[^0-9]+', '', str(phone))
    try:
        validate_email(email)
    except ValidationError:
        email = None
    else:
        email = email
    if not email or User.objects.filter(username__iexact=email).exists():
        if not phone or User.objects.filter(username__iexact=phone).exists():
            if not name or User.objects.filter(username__iexact=name).exists():
                while True:
                    username = '{}{}'.format(name, ''.join(random.choice(string.ascii_lowercase) for _ in range(6)))
                    if User.objects.filter(username__iexact=username).exists():
                        continue
                    else:
                        break
            else:
                username = name
        else:
            username = phone
    else:
        username = email
    return username


def success_response(status, msg, data, *args, **kwargs):
    response = {
        "status_code": status,
        "status": "success",
        "msg": msg,
        "data": data
    }
    return Response(data=response, status=status)


def error_response(status, msg, data, *args, **kwargs):
    response = {
        "status_code": status,
        "status": "failure",
        "msg": msg,
        "data": data
    }
    return Response(data=response, status=status)


def generate_random_string(N=8):
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(N))


def generate_random_uppercase_string(N=8):
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase) for _ in range(N))


def generate_random_lowercase_string(N=8):
    return ''.join(
        random.SystemRandom().choice(string.ascii_lowercase) for _ in range(N))


def generate_random_string_with_given_string(value, N):
    return ''.join(
        random.SystemRandom().choice(value) for _ in range(N))


def generate_random_string_except_given_string(value, N):
    value = value.upper()
    ascii_uppercase = string.ascii_uppercase
    for char in value:
        ascii_uppercase = ascii_uppercase.replace(char, '')
    return ''.join(
        random.SystemRandom().choice(ascii_uppercase) for _ in range(N))


def generate_broker_code():
    code = generate_random_uppercase_string(N=4)
    while Broker.objects.filter(code=code).exists():
        code = generate_random_uppercase_string(N=4)
    return code


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def is_fms_user(user):
    if isinstance(user, User):
        return 'fms' in user.groups.values_list('name', flat=True) and Broker.objects.filter(name=user).exists()
    return False


def is_sme_user(user):
    if isinstance(user, User):
        return 'sme' in user.groups.values_list('name', flat=True) and Sme.objects.filter(name=user).exists()
    return False


def is_blank(string):
    return not (string and string.strip())


def django_date_format(date):
    if is_blank(date):
        return None
    elif date == 'None':
        return None
    else:
        try:
            dt = datetime.strptime(date, '%d-%b-%Y')
        except ValueError:
            try:
                dt = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                dt = None
        return dt


def verify_pod_data():
    from restapi.models import BookingStatuses, BookingStatusChain
    try:
        bs = BookingStatuses.objects.get(status='pod_uploaded')
        tl = bs.time_limit
    except BookingStatuses.DoesNotExist:
        tl = 0
    data = []
    for booking in ManualBooking.objects.filter(
            Q(pod_status__iexact='unverified')).exclude(
        Q(booking_status='cancelled') | Q(deleted=True)).order_by('id'):
        if (any([lr.pod_files.filter(verified=False, is_valid=False).exists() for lr in
                 booking.lr_numbers.all()]) or (
                    booking.podfile_set.filter(
                        verified=False,
                        is_valid=False).exists() and not booking.lr_numbers.exists())) and booking.podfile_set.exists():
            booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
            booking_status_mapping_id = None
            booking_status_chain_id = None
            booking_status_mapping_booking_stage = None
            booking_status_mapping_pod_uploaded_date = None
            if booking_pod_uploaded:
                booking_status_mapping_object = get_booking_status_mapping_object(booking, 'pod_uploaded')
                try:
                    booking_status_chain_id = BookingStatusChain.objects.get(booking_status__status='pod_uploaded').id
                except BookingStatusChain.DoesNotExist:
                    booking_status_chain_id = None
                if booking_status_mapping_object:
                    booking_status_mapping_id = booking_status_mapping_object.id
                    booking_status_mapping_booking_stage = booking_status_mapping_object.booking_stage
                    booking_status_mapping_pod_uploaded_date = booking_status_mapping_object.created_on
            booking_data = {
                'id': booking.id,
                'booking_id': booking.booking_id,
                'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                'supplier_name': booking.booking_supplier.name if isinstance(booking.booking_supplier,Supplier) else None,
                'supplier_phone':booking.booking_supplier.phone if isinstance(booking.booking_supplier,Supplier) else None,
                'from_city': booking.from_city,
                'to_city': booking.to_city,
                'vehicle_number': booking.supplier_vehicle.number() if booking.supplier_vehicle else '-',
                'party_weight': booking.charged_weight,
                'supplier_weight': booking.supplier_charged_weight,
                'loaded_weight': booking.loaded_weight,
                'delivered_weight': booking.delivered_weight,
                'form_verify_pod': '{}_{}'.format('form_verify_pod', booking.booking_id),
                'btn_accept_choice': '{}_{}'.format('btn_accept_choice', booking.booking_id),
                'btn_accept_id': '{}_{}'.format('btn_accept_id', booking.booking_id),
                'btn_reject_id': '{}_{}'.format('btn_reject_id', booking.booking_id),
                'input_party_weight': '{}_{}'.format('input_party_weight', booking.booking_id),
                'input_supplier_weight': '{}_{}'.format('input_supplier_weight', booking.booking_id),
                'input_loaded_weight': '{}_{}'.format('input_loaded_weight', booking.booking_id),
                'input_delivered_weight': '{}_{}'.format('input_delivered_weight', booking.booking_id),
                'input_delivered_date': '{}_{}'.format('input_delivered_date', booking.booking_id),
                'input_rejection_remarks': '{}_{}'.format('input_rejection_remarks', booking.booking_id),
                'div_rejection_remarks': '{}_{}'.format('div_rejection_remarks', booking.booking_id),
                'div_rejection_line': '{}_{}'.format('div_rejection_line', booking.booking_id),
                'btn_resubmit_id': '{}_btn_resubmit'.format(booking.booking_id),
                'form_resubmit_pod': '{}_form_resubmit'.format(booking.booking_id),
                'booking_status_mapping_id': booking_status_mapping_id,
                'booking_status_chain_id': booking_status_chain_id,
                'booking_status_mapping_booking_stage': booking_status_mapping_booking_stage,
                'booking_status_mapping_pod_uploaded_date': booking_status_mapping_pod_uploaded_date.strftime(
                    '%d-%b-%Y') if booking_status_mapping_pod_uploaded_date else None
            }
            pod_data = []
            if booking.lr_numbers.exists() and any(
                    [lr.pod_files.filter(verified=False, is_valid=False).exists() for lr in booking.lr_numbers.all()]):
                for lr in booking.lr_numbers.all():
                    pod_data.append({
                        'lr_number': lr.lr_number,
                        'uploaded_by': lr.pod_files.last().uploaded_by.profile.name if lr.pod_files.last() else '',
                        'uploaded_on': lr.pod_files.last().created_on.strftime(
                            '%d-%b-%Y') if lr.pod_files.last() else '',
                        'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                  'url': doc.s3_upload.public_url()} for doc in lr.pod_files.filter(verified=False)],
                        'gallery': '{}_gallery'.format(lr.lr_number)

                    })

            elif booking.podfile_set.filter(verified=False,
                                            is_valid=False).exists() and not booking.lr_numbers.exists():
                pod_data.append({
                    'lr_number': '-',
                    'uploaded_by': booking.podfile_set.last().uploaded_by.profile.name if booking.podfile_set.last() else '',
                    'uploaded_on': booking.podfile_set.last().created_on.strftime(
                        '%d-%b-%Y') if booking.podfile_set.last() else '',
                    'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                              'url': doc.s3_upload.public_url()} for doc in booking.podfile_set.filter(verified=False)],
                    'gallery': '{}_gallery'.format(booking.booking_id)

                })
            else:
                pass
            booking_data['pod_data'] = pod_data
            booking_data['pod_verify_time_limit'] = tl
            data.append(booking_data)
    return data


def verify_pod_data_count():
    return len(verify_pod_data())


def my_uploaded_pod_data(user):
    data = []
    for booking in ManualBooking.objects.filter(
            Q(pod_status__iexact='unverified') | Q(pod_status__iexact='rejected')).exclude(
        Q(booking_status='cancelled') | Q(deleted=True)).order_by('id'):
        if any([lr.pod_files.exists() for lr in booking.lr_numbers.all()]) and booking.podfile_set.exists():
            booking_data = {
                'id': booking.id,
                'booking_id': booking.booking_id,
                'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                'supplier_name': booking.booking_supplier.name if isinstance(booking.booking_supplier,Supplier) else None,
                'supplier_phone': booking.booking_supplier.phone if isinstance(booking.booking_supplier,Supplier) else None,
                'from_city': booking.from_city,
                'to_city': booking.to_city,
                'vehicle_number': booking.lorry_number,
                'party_weight': booking.charged_weight,
                'supplier_weight': booking.supplier_charged_weight,
                'loaded_weight': booking.loaded_weight,
                'delivered_weight': booking.delivered_weight,
                'pod_status': booking.get_pod_status_display(),
                'form_resubmit_pod': 'form_resubmit_pod_{}'.format(booking.booking_id),
                'input_resubmission_remarks': 'input_resubmission_remarks_{}'.format(booking.booking_id),
                'btn_resubmit_id': 'btn_resubmit_id_{}'.format(booking.booking_id),
                'div_resubmit_remarks': 'div_resubmit_remarks_{}'.format(booking.booking_id),
            }
            pod_data = []
            if EMP_GROUP1 in user.groups.values_list('name', flat=True):
                if booking.lr_numbers.exists() and any(
                        [lr.pod_files.exists() for lr in
                         booking.lr_numbers.all()]):
                    for lr in booking.lr_numbers.all():
                        pod_data.append({
                            'lr_number': lr.lr_number,
                            'uploaded_by': lr.pod_files.last().uploaded_by.profile.name if lr.pod_files.last() else '',
                            'uploaded_on': lr.pod_files.last().created_on.strftime(
                                '%d-%b-%Y') if lr.pod_files.last() else '',
                            'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                      'url': doc.s3_upload.public_url(), 'id': doc.id} for doc in lr.pod_files.all()],
                            'gallery': '{}_gallery'.format(lr.lr_number)
                        })
                elif booking.podfile_set.exists() and not booking.lr_numbers.exists():
                    pod_data.append({
                        'lr_number': '-',
                        'uploaded_by': booking.podfile_set.last().uploaded_by.profile.name if booking.podfile_set.last() else '',
                        'uploaded_on': booking.podfile_set.last().created_on.strftime(
                            '%d-%b-%Y') if booking.podfile_set.last() else '',
                        'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                  'url': doc.s3_upload.public_url(), 'id': doc.id} for doc in
                                 booking.podfile_set.all()],
                        'gallery': '{}_gallery'.format(booking.booking_id)
                    })
                else:
                    pass
                booking_data['rejected'] = [{'rejected_by': reject.rejected_by,
                                             'rejection_datetime': reject.created_on.strftime('%d-%b-%Y %I:%M %p'),
                                             'remarks': reject.remarks} for reject in
                                            booking.rejectedpod_set.all()]
            else:
                if booking.lr_numbers.exists() and any(
                        [lr.pod_files.filter(uploaded_by=user).exists()
                         for lr in booking.lr_numbers.all()]):
                    for lr in booking.lr_numbers.all():
                        pod_data.append({
                            'lr_number': lr.lr_number,
                            'uploaded_by': lr.pod_files.last().uploaded_by.profile.name if lr.pod_files.last() else '',
                            'uploaded_on': lr.pod_files.last().created_on.strftime(
                                '%d-%b-%Y') if lr.pod_files.last() else '',
                            'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                      'url': doc.s3_upload.public_url(), 'id': doc.id} for doc in
                                     lr.pod_files.all()],
                        })

                elif booking.podfile_set.filter(uploaded_by=user).exists() and not booking.lr_numbers.exists():
                    pod_data.append({
                        'lr_number': '-',
                        'uploaded_by': booking.podfile_set.last().uploaded_by.profile.name if booking.podfile_set.last() else '',
                        'uploaded_on': booking.podfile_set.last().created_on.strftime(
                            '%d-%b-%Y') if booking.podfile_set.last() else '',
                        'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                  'url': doc.s3_upload.public_url(), 'id': doc.id} for doc in
                                 booking.podfile_set.all()],
                    })
                else:
                    pass
                booking_data['rejected'] = [{'rejected_by': reject.rejected_by,
                                             'rejection_datetime': reject.created_on.strftime('%d-%b-%Y %I:%M %p'),
                                             'remarks': reject.remarks} for reject in
                                            booking.rejectedpod_set.all()]
            booking_data['pod_data'] = pod_data
            if pod_data:
                data.append(booking_data)
    return data


def get_employee_roles(user):
    from restapi.models import EmployeeRolesMapping
    return_response = {"status": "failure", "roles": {}, "msg": ""}
    employee = Employee.objects.filter(username=user)
    if not employee:
        return_response["msg"] = "Employee Does not exist"
        return return_response
    employee_roles = list(
        EmployeeRolesMapping.objects.filter(employee=employee[0]).values_list('employee_role__role', flat=True))
    if not employee_roles:
        return_response["msg"] = "Employee Roles Do not exist"
        return return_response
    return_response["msg"] = "Employee Roles list"
    return_response["status"] = "success"
    return_response["roles"] = employee_roles
    return return_response


def get_employee_display_roles(user):
    from restapi.models import EmployeeRolesMapping
    return_response = {"status": "failure", "roles": {}, "msg": ""}
    employee = Employee.objects.filter(username=user)
    if not employee:
        return_response["msg"] = "Employee Does not exist"
        return return_response
    employee_roles = list(
        erm.employee_role.get_role_display() for erm in EmployeeRolesMapping.objects.filter(employee=employee[0],
                                                                                            employee_status='active'))
    if not employee_roles:
        return_response["msg"] = "Employee Roles Do not exist"
        return return_response
    return_response["msg"] = "Employee Roles list"
    return_response["status"] = "success"
    return_response["roles"] = employee_roles
    return return_response


def get_td_functionality_roles_notification_users(functionality, aaho_office_id, app, role):
    from restapi.models import TaskDashboardFunctionalities, EmployeeRolesFunctionalityMapping
    td_pending_lr = TaskDashboardFunctionalities.objects.get(functionality=functionality)
    emp_roles = list(EmployeeRolesFunctionalityMapping.objects.filter(td_functionality=td_pending_lr,
                                                                      employee_role__role=role).
                     values_list('employee_role__id', flat=True))

    notification_users = User.objects.filter(employee__office_id=aaho_office_id,
                                             employee__employee_role_mapping__employee_role__id__in=emp_roles)

    q_objects = Q()
    q_objects |= Q(**{'app': app})
    mobile_device = MobileDevice.objects.filter(q_objects)
    if mobile_device:
        mobile_device = list(mobile_device.filter(user__in=notification_users).values_list('id', flat=True))
    else:
        mobile_device = None
    return mobile_device


def get_td_functionality_notification_users(functionality, aaho_office_id, app):
    from restapi.models import TaskDashboardFunctionalities, EmployeeRolesFunctionalityMapping
    td_pending_lr = TaskDashboardFunctionalities.objects.get(functionality=functionality)
    emp_roles = list(EmployeeRolesFunctionalityMapping.objects.filter(td_functionality=td_pending_lr).
                     values_list('employee_role__id', flat=True))

    notification_users = User.objects.filter(employee__office_id=aaho_office_id,
                                             employee__employee_role_mapping__employee_role__id__in=emp_roles)

    q_objects = Q()
    q_objects |= Q(**{'app': app})
    mobile_device = MobileDevice.objects.filter(q_objects)
    if mobile_device:
        mobile_device = list(mobile_device.filter(user__in=notification_users).values_list('id', flat=True))
    else:
        mobile_device = None
    return mobile_device


def get_booking_status_mapping_object(booking, status):
    from restapi.models import BookingStatusChain, BookingStatusesMapping
    booking_status_chain = get_or_none(BookingStatusChain, booking_status__status=status)
    if not isinstance(booking_status_chain, BookingStatusChain):
        return None
    booking_statuses_mapping = get_or_none(BookingStatusesMapping, booking_status_chain=booking_status_chain,
                                           manual_booking=booking)
    if not isinstance(booking_statuses_mapping, BookingStatusesMapping):
        return None
    return booking_statuses_mapping


def check_booking_status(booking, status):
    from restapi.models import BookingStatusChain, BookingStatusesMapping
    booking_status_chain = get_or_none(BookingStatusChain, booking_status__status=status)
    if not isinstance(booking_status_chain, BookingStatusChain):
        return False
    booking_statuses_mapping = get_or_none(BookingStatusesMapping, booking_status_chain=booking_status_chain,
                                           manual_booking=booking)
    if not isinstance(booking_statuses_mapping, BookingStatusesMapping):
        return False
    return True


def create_new_booking_status(booking, status, user):
    from restapi.models import BookingStatusChain, BookingStatusesMapping
    try:
        booking_status_chain = BookingStatusChain.objects.get(booking_status__status=status)
        booking_statuses_mapping = BookingStatusesMapping.objects.create(
            booking_status_chain=booking_status_chain,
            manual_booking=booking,
            booking_stage='in_progress',
            created_by=user,
            changed_by=user)
    except (BookingStatusChain.DoesNotExist, BookingStatusChain.MultipleObjectsReturned) as e:
        return


def update_booking_status(booking, status, stage, user):
    from restapi.models import BookingStatusChain, BookingStatusesMapping
    try:
        booking_status_chain = BookingStatusChain.objects.get(booking_status__status=status)
    except (BookingStatusChain.DoesNotExist, BookingStatusChain.MultipleObjectsReturned) as e:
        return
    try:
        bsm = BookingStatusesMapping.objects.get(booking_status_chain=booking_status_chain, manual_booking=booking)
        bsm.booking_stage = stage
        bsm.changed_by = user
        bsm.save()
    except (BookingStatusesMapping.DoesNotExist, BookingStatusesMapping.MultipleObjectsReturned) as e:
        print('BookingStatusesMapping DoesNotExist')
    return


def add_invoice_booking_status_comment(data, c_status):
    from restapi.models import BookingStatusesMapping, BookingStatusesMappingComments
    for mb in data:
        # b_ids = []
        b_ids = mb['booking_id'].split('\n')
        mb['booking_statuses'] = []
        for b_id in b_ids:
            # booking_status_details = dict
            m_booking = ManualBooking.objects.get(booking_id=b_id)
            bsm = BookingStatusesMapping.objects.filter(manual_booking=m_booking,
                                                        booking_status_chain__booking_status__status__in=[
                                                            'invoice_raised', 'party_invoice_sent',
                                                            'invoice_confirmed']).order_by('-id')[:1]
            if bsm:
                booking_status_details = {'booking_id': bsm[0].manual_booking.booking_id,
                                          'manual_booking_id': bsm[0].manual_booking.id,
                                          'booking_status_mapping_id': bsm[0].id,
                                          'booking_status_current': bsm[
                                              0].booking_status_chain.booking_status.status,
                                          'booking_status_mapping_stage': bsm[0].booking_stage,
                                          'primary_preceded_booking_status':
                                              bsm[0].booking_status_chain.primary_preceded_booking_status.status,
                                          'primary_succeeded_booking_status':
                                              'inward_followup_completed',
                                          'secondary_preceded_booking_status':
                                              bsm[
                                                  0].booking_status_chain.secondary_preceded_booking_status.status,
                                          'secondary_succeeded_booking_status': 'inward_followup_completed'}
                bsm_cmts = BookingStatusesMappingComments.objects.filter(booking_status_mapping=bsm).order_by('-id')[:1]
                if bsm_cmts:
                    created_on = bsm_cmts[0].created_on
                    created_on_string = '(' + str(created_on.hour) + ':' + str(created_on.minute) + ' ' + \
                                        str(created_on.day) + '-' + str(created_on.month) + '-' + str(
                        created_on.year) + ')'
                    booking_status_details['booking_status_comments_id'] = bsm_cmts[0].id
                    booking_status_details['booking_status_comment'] = bsm_cmts[0].comment
                    booking_status_details['booking_status_comment_created_on'] = created_on_string
                else:
                    booking_status_details['booking_status_comments_id'] = None
                    booking_status_details['booking_status_comment'] = None
                    booking_status_details['booking_status_comment_created_on'] = None
            else:
                booking_status_details = {}
            mb['booking_statuses'].append(booking_status_details)
    return data


def get_formatted_time_date(date_time_field):
    return '(' + str(date_time_field.strftime("%H")) + ':' + str(date_time_field.strftime("%M")) + ' ' + \
           str(date_time_field.strftime("%d")) + '-' + str(date_time_field.strftime("%m")) + '-' + \
           str(date_time_field.strftime("%Y")) + ')'


def get_booking_status_filtered_ids(initial_ids, filter_params):
    from_date = datetime.strptime(str(filter_params['from_date']), '%Y-%m-%d').date() if filter_params[
        'from_date'] else None
    to_date = datetime.strptime(str(filter_params['to_date']), '%Y-%m-%d').date() if filter_params['to_date'] else None
    query = Q()
    if from_date:
        query &= Q(shipment_date__gte=from_date)
    if to_date:
        query &= Q(shipment_date__lte=to_date)
    source_office = get_or_none(AahoOffice, id=filter_params['source_office_id'])
    if source_office:
        query &= Q(source_office=get_or_none(AahoOffice, id=filter_params['source_office_id']))
    destination_office = get_or_none(AahoOffice, id=filter_params['destination_office_id'])
    if destination_office:
        query &= Q(destination_office=get_or_none(AahoOffice, id=filter_params['destination_office_id']))
    customer = get_or_none(Sme, id=filter_params['customer_id'])
    if customer:
        query &= Q(customer_to_be_billed_to=get_or_none(Sme, id=filter_params['customer_id']))
    supplier = get_or_none(Broker, id=filter_params['supplier_id'])
    if supplier:
        query &= Q(supplier=get_or_none(Broker, id=filter_params['supplier_id']))
    user = filter_params['user']
    if user:
        booking_ids = manual_booking_id_list(user=user)
        query &= Q(id__in=booking_ids)
    filtered_ids = list(ManualBooking.objects.filter(id__in=initial_ids).
                        filter(query & Q(booking_id__startswith='AH')).
                        exclude(Q(booking_status='cancelled') | Q(deleted=True)).values_list('id', flat=True))
    return filtered_ids


def get_pre_loading_bookings(filter_params=None):
    from restapi.models import BookingStatusesMapping
    pre_loading_all_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=['confirmed', 'loaded'],
        manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                        values_list('manual_booking_id', flat=True)))
    except_pre_loading_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=[
            'lr_generated', 'advance_paid', 'unloaded', 'pod_uploaded', 'pod_verified', 'invoice_raised',
            'invoice_confirmed',
            'balance_paid', 'party_invoice_sent', 'inward_followup_completed', 'complete'],
        manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                           values_list('manual_booking_id', flat=True)))
    pre_loading_bookings = [x for x in pre_loading_all_bookings if x not in except_pre_loading_bookings]
    if filter_params:
        pre_loading_bookings = get_booking_status_filtered_ids(pre_loading_bookings, filter_params)
    return pre_loading_bookings


def get_in_transit_bookings(filter_params=None):
    from restapi.models import BookingStatusesMapping
    in_transit_all_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=['lr_generated', 'advance_paid'],
        manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                       values_list('manual_booking_id', flat=True)))
    except_in_transit_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=[
            'unloaded', 'pod_uploaded', 'pod_verified', 'invoice_raised',
            'invoice_confirmed', 'party_invoice_sent', 'inward_followup_completed', 'complete'],
        manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                          values_list('manual_booking_id', flat=True)))
    in_transit_bookings = [x for x in in_transit_all_bookings if x not in except_in_transit_bookings]
    if filter_params:
        in_transit_bookings = get_booking_status_filtered_ids(in_transit_bookings, filter_params)
    return in_transit_bookings


def get_pod_due_bookings(filter_params=None):
    from restapi.models import BookingStatusesMapping
    pod_due_all_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=['unloaded']).exclude(deleted=True). \
                                    values_list('manual_booking_id', flat=True)))
    except_pod_due_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=['pod_uploaded', 'pod_verified', 'invoice_raised',
                                                          'party_invoice_sent', 'invoice_confirmed',
                                                          'inward_followup_completed', 'complete']).exclude(
        deleted=True). \
                                       values_list('manual_booking_id', flat=True)))
    pod_due_bookings = [x for x in pod_due_all_bookings if x not in except_pod_due_bookings]
    if filter_params:
        pod_due_bookings = get_booking_status_filtered_ids(pod_due_bookings, filter_params)
    return pod_due_bookings


def get_invoice_pending_bookings(filter_params=None):
    from restapi.models import BookingStatusesMapping
    invoice_pending_all_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=['pod_uploaded', 'pod_verified'],
        manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                            values_list('manual_booking_id', flat=True)))
    except_invoice_pending_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=[
            'invoice_raised'], manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(
        Q(deleted=True) | Q(booking_stage='reverted')). \
                                               values_list('manual_booking_id', flat=True)))
    invoice_pending_bookings = [x for x in invoice_pending_all_bookings if x not in except_invoice_pending_bookings]
    if filter_params:
        invoice_pending_bookings = get_booking_status_filtered_ids(invoice_pending_bookings, filter_params)
    return invoice_pending_bookings


def get_credit_period_bookings(filter_params=None):
    from restapi.models import BookingStatusesMapping
    credit_period_all_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=['invoice_raised'],
        manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                          values_list('manual_booking_id', flat=True)))
    except_credit_period_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=[
            'inward_followup_completed', 'complete'],
        manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                             values_list('manual_booking_id', flat=True)))
    credit_period_bookings = [x for x in credit_period_all_bookings if x not in except_credit_period_bookings]
    payment_not_overdue_bookings = []
    for pdb in credit_period_bookings:
        booking = get_or_none(ManualBooking, id=pdb)
        if booking:
            inv = booking.invoices.last()
            if inv and not inv.is_overdue:
                payment_not_overdue_bookings.append(pdb)
    if filter_params:
        payment_not_overdue_bookings = get_booking_status_filtered_ids(payment_not_overdue_bookings, filter_params)
    return payment_not_overdue_bookings


def get_payment_due_bookings(filter_params=None):
    from restapi.models import BookingStatusesMapping
    payment_due_all_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=['inward_followup_completed'],
        manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                        values_list('manual_booking_id', flat=True)))
    except_payment_due_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=[
            'complete'], manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                           values_list('manual_booking_id', flat=True)))
    payment_due_bookings = [x for x in payment_due_all_bookings if x not in except_payment_due_bookings]
    if filter_params:
        payment_due_bookings = get_booking_status_filtered_ids(payment_due_bookings, filter_params)
    return payment_due_bookings


def get_payment_overdue_bookings(filter_params=None):
    from restapi.models import BookingStatusesMapping
    payment_due_all_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=['invoice_raised'],
        manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                        values_list('manual_booking_id', flat=True)))
    except_payment_due_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=[
            'inward_followup_completed', 'complete'],
        manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                           values_list('manual_booking_id', flat=True)))
    payment_due_bookings = [x for x in payment_due_all_bookings if x not in except_payment_due_bookings]
    payment_overdue_bookings = []
    for pdb in payment_due_bookings:
        booking = get_or_none(ManualBooking, id=pdb)
        if booking:
            inv = booking.invoices.last()
            if inv and inv.is_overdue:
                payment_overdue_bookings.append(pdb)
    if filter_params:
        payment_overdue_bookings = get_booking_status_filtered_ids(payment_overdue_bookings, filter_params)
    return payment_overdue_bookings


def get_payment_received_bookings(filter_params=None):
    from restapi.models import BookingStatusesMapping
    payment_received_all_bookings = set(list(BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=['inward_followup_completed', 'complete'],
        manual_booking__shipment_date__gte=datetime(2018, 10, 5).date()).exclude(deleted=True). \
                                             values_list('manual_booking_id', flat=True)))
    if filter_params:
        payment_received_all_bookings = get_booking_status_filtered_ids(payment_received_all_bookings, filter_params)
    return payment_received_all_bookings


def get_bookings_total_amount_to_company(bookings):
    tac = 0
    for plb in bookings:
        booking = get_or_none(ManualBooking, id=plb)
        if booking:
            tac += (booking.total_amount_to_company - booking.credit_amount_customer - booking.tds_deducted_amount +
                    booking.debit_amount_customer)
    return tac


def get_bookings_iwp(bookings):
    iwp = 0
    for plb in bookings:
        booking = get_or_none(ManualBooking, id=plb)
        if booking:
            iwp += booking.total_in_ward_amount
    return iwp


def get_bookings_tao(bookings):
    tao = 0
    for plb in bookings:
        booking = get_or_none(ManualBooking, id=plb)
        if booking:
            tao += (booking.total_amount_to_owner + booking.credit_amount_supplier - booking.debit_amount_supplier)
    return tao


def get_bookings_owp(bookings):
    owp = 0
    for plb in bookings:
        booking = get_or_none(ManualBooking, id=plb)
        if booking:
            owp += booking.total_out_ward_amount
    return owp


def get_bookings_monitoring_status(response_json, filter_params):
    # Line no. 987 to 1001 - to be removed after some testing for few days
    status_list = []
    status_list.extend(get_pre_loading_bookings(filter_params))
    status_list.extend(get_in_transit_bookings(filter_params))
    status_list.extend(get_pod_due_bookings(filter_params))
    status_list.extend(get_invoice_pending_bookings(filter_params))
    status_list.extend(get_credit_period_bookings(filter_params))
    status_list.extend(get_payment_overdue_bookings(filter_params))
    status_list.extend(get_payment_received_bookings(filter_params))
    mb = set(list(ManualBooking.objects.filter(booking_id__startswith='AH',
                                               shipment_date__gte=datetime(2018, 10, 5).date()).exclude(
        Q(booking_status='cancelled') | Q(deleted=True)).values_list('id', flat=True)))
    non_status_list = [x for x in mb if x not in status_list]

    response_json['pre_loading'] = len(get_pre_loading_bookings(filter_params))
    response_json['in_transit'] = len(get_in_transit_bookings(filter_params))
    response_json['pod_due'] = len(get_pod_due_bookings(filter_params))
    response_json['invoice_pending'] = len(get_invoice_pending_bookings(filter_params))
    response_json['credit_period'] = len(get_credit_period_bookings(filter_params))
    response_json['payment_due'] = len(get_payment_due_bookings(filter_params))
    response_json['payment_overdue'] = len(get_payment_overdue_bookings(filter_params))
    response_json['payment_received'] = len(get_payment_received_bookings(filter_params))
    return response_json


def get_bookings_monitoring_tac(response_json, filter_params):
    response_json['pre_loading'] = get_bookings_total_amount_to_company(get_pre_loading_bookings(filter_params))
    response_json['in_transit'] = get_bookings_total_amount_to_company(get_in_transit_bookings(filter_params))
    response_json['pod_due'] = get_bookings_total_amount_to_company(get_pod_due_bookings(filter_params))
    response_json['invoice_pending'] = get_bookings_total_amount_to_company(get_invoice_pending_bookings(filter_params))
    response_json['credit_period'] = get_bookings_total_amount_to_company(get_credit_period_bookings(filter_params))
    response_json['payment_due'] = get_bookings_total_amount_to_company(get_payment_due_bookings(filter_params))
    response_json['payment_overdue'] = get_bookings_total_amount_to_company(get_payment_overdue_bookings(filter_params))
    response_json['payment_received'] = get_bookings_total_amount_to_company(
        get_payment_received_bookings(filter_params))
    return response_json


def get_bookings_monitoring_iwp(response_json, filter_params):
    response_json['pre_loading'] = get_bookings_iwp(get_pre_loading_bookings(filter_params))
    response_json['in_transit'] = get_bookings_iwp(get_in_transit_bookings(filter_params))
    response_json['pod_due'] = get_bookings_iwp(get_pod_due_bookings(filter_params))
    response_json['invoice_pending'] = get_bookings_iwp(get_invoice_pending_bookings(filter_params))
    response_json['credit_period'] = get_bookings_iwp(get_credit_period_bookings(filter_params))
    response_json['payment_due'] = get_bookings_iwp(get_payment_due_bookings(filter_params))
    response_json['payment_overdue'] = get_bookings_iwp(get_payment_overdue_bookings(filter_params))
    response_json['payment_received'] = get_bookings_iwp(get_payment_received_bookings(filter_params))
    return response_json


def get_bookings_monitoring_tao(response_json, filter_params):
    response_json['pre_loading'] = get_bookings_tao(get_pre_loading_bookings(filter_params))
    response_json['in_transit'] = get_bookings_tao(get_in_transit_bookings(filter_params))
    response_json['pod_due'] = get_bookings_tao(get_pod_due_bookings(filter_params))
    response_json['invoice_pending'] = get_bookings_tao(get_invoice_pending_bookings(filter_params))
    response_json['credit_period'] = get_bookings_tao(get_credit_period_bookings(filter_params))
    response_json['payment_due'] = get_bookings_tao(get_payment_due_bookings(filter_params))
    response_json['payment_overdue'] = get_bookings_tao(get_payment_overdue_bookings(filter_params))
    response_json['payment_received'] = get_bookings_tao(get_payment_received_bookings(filter_params))
    return response_json


def get_bookings_monitoring_owp(response_json, filter_params):
    response_json['pre_loading'] = get_bookings_owp(get_pre_loading_bookings(filter_params))
    response_json['in_transit'] = get_bookings_owp(get_in_transit_bookings(filter_params))
    response_json['pod_due'] = get_bookings_owp(get_pod_due_bookings(filter_params))
    response_json['invoice_pending'] = get_bookings_owp(get_invoice_pending_bookings(filter_params))
    response_json['credit_period'] = get_bookings_owp(get_credit_period_bookings(filter_params))
    response_json['payment_due'] = get_bookings_owp(get_payment_due_bookings(filter_params))
    response_json['payment_overdue'] = get_bookings_owp(get_payment_overdue_bookings(filter_params))
    response_json['payment_received'] = get_bookings_owp(get_payment_received_bookings(filter_params))
    return response_json


class TaskFunctionalitySwitcher():
    # def __init__(self, booking_instance):
    #     self.booking_instance = booking_instance

    def case(self, user, key, aaho_office, filter_params, duration):
        self.user = user
        self.aaho_office = aaho_office
        self.filter_params = filter_params
        self.duration = duration
        self.overdue_less_2_holiday_count = self.get_company_holiday_count((datetime.now().date() - timedelta(days=2)), datetime.now().date())
        self.overdue_2_to_7_holiday_count = self.get_company_holiday_count((datetime.now().date() - timedelta(days=7)), (datetime.now().date() - timedelta(days=2)))
        self.overdue_7_to_30_holiday_count = self.get_company_holiday_count((datetime.now().date() - timedelta(days=30)), (datetime.now().date() - timedelta(days=7)))
        self.overdue_less_2_bank_holiday_count = self.get_bank_holiday_count((datetime.now().date() - timedelta(days=2)), datetime.now().date())
        self.overdue_2_to_7_bank_holiday_count = self.get_bank_holiday_count((datetime.now().date() - timedelta(days=7)), (datetime.now().date() - timedelta(days=2)))
        self.overdue_7_to_30_bank_holiday_count = self.get_bank_holiday_count((datetime.now().date() - timedelta(days=30)), (datetime.now().date() - timedelta(days=7)))
        self.overdue_less_2_delta1 = 0
        self.overdue_less_2_delta2 = 2 + self.overdue_less_2_holiday_count
        self.overdue_2_to_7_delta1 = self.get_overdue_2_to_7_delta1()
        self.overdue_2_to_7_delta2 = self.get_overdue_2_to_7_delta2()
        self.overdue_7_to_30_delta1 = self.get_overdue_7_to_30_delta1()
        self.overdue_7_to_30_delta2 = self.get_overdue_7_to_30_delta2()
        method_name = 'task_' + str(key)
        method = getattr(self, method_name, lambda: 'Invalid Task Functionality')
        return method()

    def get_overdue_2_to_7_delta1(self):
        if self.overdue_less_2_holiday_count > 0:
            delta1 = 2 + self.overdue_less_2_holiday_count
        else:
            delta1 = 2
        return delta1

    def get_overdue_2_to_7_delta2(self):
        if self.overdue_less_2_holiday_count > 0:
            delta2 = 7 + self.overdue_less_2_holiday_count + self.overdue_2_to_7_holiday_count
        else:
            delta2 = 7 + self.overdue_2_to_7_holiday_count
        return  delta2

    def get_overdue_7_to_30_delta1(self):
        if self.overdue_2_to_7_holiday_count > 0:
            if self.overdue_less_2_holiday_count > 0:
                delta1 = 7 + self.overdue_less_2_holiday_count + self.overdue_2_to_7_holiday_count
            else:
                delta1 = 7 + self.overdue_2_to_7_holiday_count
        elif self.overdue_less_2_holiday_count > 0:
            delta1 = 7 + self.overdue_less_2_holiday_count
        else:
            delta1 = 7
        return delta1

    def get_overdue_7_to_30_delta2(self):
        if self.overdue_2_to_7_holiday_count > 0:
            if self.overdue_less_2_holiday_count > 0:
                delta2 = 30 + self.overdue_less_2_holiday_count + self.overdue_2_to_7_holiday_count + self.overdue_7_to_30_holiday_count
            else:
                delta2 = 30 + self.overdue_2_to_7_holiday_count + self.overdue_7_to_30_holiday_count
        elif self.overdue_less_2_holiday_count > 0:
            delta2 = 30 + self.overdue_less_2_holiday_count + self.overdue_7_to_30_holiday_count
        else:
            delta2 = 30 + self.overdue_7_to_30_holiday_count
        return delta2

    def get_company_holiday_count(self, start_date, end_date):
        holiday_count = AahoHolidays.objects.filter(status='active',
                                                    date__lt=end_date,
                                                    date__gte=start_date,
                                                    offices__in=[self.aaho_office]).count()
        sundays_count = calculate_sundays_between_dates(start_date, end_date)
        return holiday_count + sundays_count

    def get_bank_holiday_count(self, start_date, end_date):
        company_holiday_dates = list(AahoHolidays.objects.filter(status='active',
                                                    date__lt=end_date,
                                                    date__gte=start_date).values_list('date', flat=True))
        holiday_count = BankHolidays.objects.filter(date__lt=end_date,
                                                    date__gte=start_date).exclude(date__in=company_holiday_dates).count()
        return holiday_count

    def task_reconcile(self):
        # print('Task Reconcile')
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            owp = OutWardPayment.objects.filter(status__in=['reconciled'],
                                                payment_date__gte=datetime.now().date() - timedelta(days=delta)). \
                exclude(Q(bank_account=None) | Q(deleted=True))
            count = owp.count()
        if self.duration == 'pending_total':
            owp = OutWardPayment.objects.filter(
                payment_date__gte='2018-10-29', status='paid',
                payment_mode__in=['neft', 'imps', 'hdfc_internal_account', 'cheque']).exclude(bank_account=None)
            count = owp.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            owp = OutWardPayment.objects.filter(
                status='paid', payment_mode__in=['neft', 'imps', 'hdfc_internal_account', 'cheque'],
                payment_date__lt=(datetime.now().date() - timedelta(days=delta1)),
                payment_date__gte=(datetime.now().date() - timedelta(days=delta2))).exclude(bank_account=None)
            count = owp.count()
            details = 'OWP Reconcile Overdue for Booking Ids: ' + ', '.join(owp.values_list('booking_id__booking_id', flat=True))
        return {'count': count, 'details': details}

    def task_process_payments(self):
        # print('Task Process Payments')
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            owp = OutWardPayment.objects.filter(status__in=['paid', 'reconciled'],
                                          payment_date__gte=datetime.now().date() - timedelta(days=delta)).\
                exclude(Q(bank_account=None) | Q(deleted=True))
            count = owp.count()
        if self.duration == 'pending_total':
            owp = OutWardPayment.objects.exclude(bank_account=None).exclude(
                Q(status__in=['paid', 'reconciled']) | Q(deleted=True))
            count = owp.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            owp = OutWardPayment.objects.filter(status__in=['unpaid'],
                                                payment_date__lt=(datetime.now().date() - timedelta(days=delta1)),
                                                payment_date__gte=(datetime.now().date() - timedelta(days=delta2))).\
                exclude(Q(bank_account=None) | Q(deleted=True))
            count = owp.count()
            details = 'OWP Process Payments Overdue for Booking Ids: ' + ', '.join(owp.values_list('booking_id__booking_id', flat=True))
        return {'count': count, 'details': details}

    def task_inward_entry(self):
        # print('Task Inward Entry')
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            pip = PendingInwardPaymentEntry.objects.filter(adjusted_flag=True,
                                                payment_date__gte=datetime.now().date() - timedelta(days=delta))
            count = pip.count()
        if self.duration == 'pending_total':
            pip = PendingInwardPaymentEntry.objects.filter(adjusted_flag=False)
            count = pip.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            pip = PendingInwardPaymentEntry.objects.filter(adjusted_flag=False,
                                                payment_date__lt=(datetime.now().date() - timedelta(days=delta1)),
                                                payment_date__gte=(datetime.now().date() - timedelta(days=delta2)))
            count = pip.count()
            details = '\nPending Inward Payment Entry Overdue for Ids: ' + ', '.join(map(str, list(pip.values_list('id', flat=True))))
        return {'count': count, 'details': details}

    def task_confirm_invoice(self):
        # print('Task Confirm Invoice')
        from restapi.models import BookingStatusesMapping, BookingStatuses
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='invoice_confirmed',
                manual_booking__source_office=self.aaho_office, created_on__gte=datetime.now().date() - timedelta(days=delta)).\
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            bookings = ManualBooking.objects.filter(id__in=invoice_confirmed_bookings).exclude(billing_type='contract')
            count = Invoice.objects.filter(bookings__in=bookings).distinct().count()
        if self.duration == 'pending_total':
            party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='party_invoice_sent',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='invoice_confirmed',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            invoice_not_confirmed_bookings = [x for x in party_invoice_sent_bookings if
                                              x not in invoice_confirmed_bookings]
            bookings = ManualBooking.objects.filter(id__in=invoice_not_confirmed_bookings).exclude(billing_type='contract')
            count = Invoice.objects.filter(bookings__in=bookings).distinct().count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            try:
                bs = BookingStatuses.objects.get(status='party_invoice_sent')
                tl = bs.time_limit
            except BookingStatuses.DoesNotExist:
                tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            party_invoice_sent_overdue_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='party_invoice_sent',
                manual_booking__source_office=self.aaho_office, created_on__lt=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1)),
                created_on__gte=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta2))).\
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='invoice_confirmed',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            invoice_not_confirmed_overdue_bookings = [x for x in party_invoice_sent_overdue_bookings if
                                              x not in invoice_confirmed_bookings]
            bookings = ManualBooking.objects.filter(id__in=invoice_not_confirmed_overdue_bookings).exclude(
                billing_type='contract')
            invs = Invoice.objects.filter(bookings__in=bookings).distinct()
            count = invs.count()
            details = '\nConfirm Invoice Overdue Invoice Ids: ' + ', '.join(
                invs.values_list('invoice_number', flat=True))
        return {'count': count, 'details': details}

    def task_raise_invoice(self):
        # print('Task Raise Invoice')
        from restapi.models import BookingStatusesMapping, BookingStatuses
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            invoice_raised_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='invoice_raised',
                manual_booking__source_office=self.aaho_office,
                created_on__gte=datetime.now().date() - timedelta(days=delta)). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            bookings = ManualBooking.objects.filter(id__in=invoice_raised_bookings).filter(
            Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
            Q(booking_id__startswith='AH')).exclude(
            Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
            count = bookings.count()
        if self.duration == 'pending_total':
            pod_verified_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_verified',
                manual_booking__source_office=self.aaho_office).exclude(Q(deleted=True)). \
                values_list('manual_booking_id', flat=True)
            invoice_raised_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='invoice_raised',
                manual_booking__source_office=self.aaho_office).exclude(
                Q(deleted=True) | Q(booking_stage='reverted')). \
                values_list('manual_booking_id', flat=True)
            invoice_not_raised_bookings = [x for x in pod_verified_bookings if x not in invoice_raised_bookings]
            bookings = ManualBooking.objects.filter(id__in=invoice_not_raised_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
            count = bookings.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            try:
                bs = BookingStatuses.objects.get(status='pod_verified')
                tl = bs.time_limit
            except BookingStatuses.DoesNotExist:
                tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            pod_verified_overdue_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_verified',
                manual_booking__source_office=self.aaho_office,
                created_on__lt=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1)),
                created_on__gte=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta2))). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            invoice_raised_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='invoice_raised',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            invoice_not_raised_overdue_bookings = [x for x in pod_verified_overdue_bookings if
                                                      x not in invoice_raised_bookings]
            bookings = ManualBooking.objects.filter(id__in=invoice_not_raised_overdue_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
            count = bookings.count()
            details = '\nRaise Invoice Overdue Booking Ids: ' + ', '.join(
                bookings.values_list('booking_id', flat=True))
        return {'count': count, 'details': details}

    def task_verify_pod(self):
        # print('Task Verify PoD')
        from restapi.models import BookingStatusesMapping, BookingStatuses
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            pod_verified_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_verified',
                manual_booking__source_office=self.aaho_office,
                created_on__gte=datetime.now().date() - timedelta(days=delta)). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            bookings = ManualBooking.objects.filter(id__in=pod_verified_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
            count = bookings.count()
        if self.duration == 'pending_total':
            pod_uploaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_uploaded',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pod_verified_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_verified',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pod_not_verified_bookings = [x for x in pod_uploaded_bookings if
                                              x not in pod_verified_bookings]
            bookings = ManualBooking.objects.filter(id__in=pod_not_verified_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
            count = bookings.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            try:
                bs = BookingStatuses.objects.get(status='pod_uploaded')
                tl = bs.time_limit
            except BookingStatuses.DoesNotExist:
                tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            pod_uploaded_overdue_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_uploaded',
                manual_booking__source_office=self.aaho_office,
                created_on__lt=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1)),
                created_on__gte=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta2))). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            pod_verified_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_verified',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pod_not_verified_overdue_bookings = [x for x in pod_uploaded_overdue_bookings if
                                                      x not in pod_verified_bookings]
            bookings = ManualBooking.objects.filter(id__in=pod_not_verified_overdue_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
            count = bookings.count()
            details = '\nVerify PoD Overdue Booking Ids: ' + ', '.join(
                bookings.values_list('booking_id', flat=True))
        return {'count': count, 'details': details}

    def task_send_invoice(self):
        # print('Task Send Invoice')
        from restapi.models import BookingStatusesMapping, BookingStatuses
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            invoice_sent_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='party_invoice_sent',
                manual_booking__source_office=self.aaho_office,
                created_on__gte=datetime.now().date() - timedelta(days=delta)). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            bookings = ManualBooking.objects.filter(id__in=invoice_sent_bookings).exclude(billing_type='contract')
            count = Invoice.objects.filter(bookings__in=bookings).distinct().count()
        if self.duration == 'pending_total':
            invoice_raised_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='invoice_raised',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            invoice_sent_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='party_invoice_sent',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            invoice_not_confirmed_bookings = [x for x in invoice_raised_bookings if
                                              x not in invoice_sent_bookings]
            bookings = ManualBooking.objects.filter(id__in=invoice_not_confirmed_bookings).exclude(
                billing_type='contract')
            count = Invoice.objects.filter(bookings__in=bookings).distinct().count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            try:
                bs = BookingStatuses.objects.get(status='invoice_raised')
                tl = bs.time_limit
            except BookingStatuses.DoesNotExist:
                tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            invoice_raised_overdue_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='invoice_raised',
                manual_booking__source_office=self.aaho_office,
                created_on__lt=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1)),
                created_on__gte=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta2))). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            invoice_sent_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='party_invoice_sent',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            invoice_not_confirmed_overdue_bookings = [x for x in invoice_raised_overdue_bookings if
                                                      x not in invoice_sent_bookings]
            bookings = ManualBooking.objects.filter(id__in=invoice_not_confirmed_overdue_bookings).exclude(
                billing_type='contract')
            invs = Invoice.objects.filter(bookings__in=bookings).distinct()
            count = invs.count()
            details = '\nSend Invoice Overdue Invoice Ids: ' + ', '.join(
                invs.values_list('invoice_number', flat=True))
        return {'count': count, 'details': details}

    def task_pay_balance(self):
        # print('Task Pay Balance')
        from restapi.models import BookingStatusesMapping, BookingStatuses
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            balance_paid_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='balance_paid',
                manual_booking__source_office=self.aaho_office,
                created_on__gte=datetime.now().date() - timedelta(days=delta)). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            bookings = ManualBooking.objects.filter(id__in=balance_paid_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
            count = bookings.count()
        if self.duration == 'pending_total':
            pod_verified_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_verified',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            balance_paid_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='balance_paid',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            balance_not_paid_bookings = [x for x in pod_verified_bookings if
                                              x not in balance_paid_bookings]
            bookings = ManualBooking.objects.filter(id__in=balance_not_paid_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
            count = bookings.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            self.overdue_less_2_holiday_count += self.overdue_less_2_bank_holiday_count
            self.overdue_2_to_7_holiday_count += self.overdue_2_to_7_bank_holiday_count
            self.overdue_7_to_30_holiday_count += self.overdue_7_to_30_bank_holiday_count
            try:
                bs = BookingStatuses.objects.get(status='pod_verified')
                tl = bs.time_limit
            except BookingStatuses.DoesNotExist:
                tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.get_overdue_2_to_7_delta1()
                delta2 = self.get_overdue_2_to_7_delta2()
            else:
                delta1 = self.get_overdue_7_to_30_delta1()
                delta2 = self.get_overdue_7_to_30_delta2()
            pod_verified_overdue_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_verified',
                manual_booking__source_office=self.aaho_office,
                created_on__lt=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1)),
                created_on__gte=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta2))). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            balance_paid_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='balance_paid',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            balance_not_paid_overdue_bookings = [x for x in pod_verified_overdue_bookings if
                                                      x not in balance_paid_bookings]
            bookings = ManualBooking.objects.filter(id__in=balance_not_paid_overdue_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
            count = bookings.count()
            details = '\nPay Balance Overdue Booking Ids: ' + ', '.join(
                bookings.values_list('booking_id', flat=True))
        return {'count': count, 'details': details}

    def task_pay_advance(self):
        # print('Task Pay Advance')
        from restapi.models import BookingStatusesMapping, BookingStatuses
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            advance_paid_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='advance_paid',
                manual_booking__source_office=self.aaho_office,
                created_on__gte=datetime.now().date() - timedelta(days=delta)). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            bookings = ManualBooking.objects.filter(id__in=advance_paid_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
            count = bookings.count()
        if self.duration == 'pending_total':
            lr_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='lr_generated',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            advance_paid_delivered_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['advance_paid', 'unloaded'],
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            advance_not_paid_bookings = [x for x in lr_bookings if x not in advance_paid_delivered_bookings]
            bookings = ManualBooking.objects.filter(id__in=advance_not_paid_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=115)).date()) & Q(
                    booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            try:
                bs = BookingStatuses.objects.get(status='lr_generated')
                tl = bs.time_limit
            except BookingStatuses.DoesNotExist:
                tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            lr_bookings_overdue_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='lr_generated',
                manual_booking__source_office=self.aaho_office,
                created_on__lt=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1)),
                created_on__gte=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta2))). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            advance_paid_delivered_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['advance_paid', 'unloaded'],
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            advance_not_paid_overdue_bookings = [x for x in lr_bookings_overdue_bookings if
                                                 x not in advance_paid_delivered_bookings]
            bookings = ManualBooking.objects.filter(id__in=advance_not_paid_overdue_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=115)).date()) & Q(
                    booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
            details = '\nPay Advance Overdue Booking Ids: ' + ', '.join(
                bookings.values_list('booking_id', flat=True))
        return {'count': count, 'details': details}

    def task_lr_generation(self):
        # print('Task Generate LR')
        from restapi.models import BookingStatusesMapping, BookingStatuses
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            lr_generated_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='lr_generated',
                manual_booking__source_office=self.aaho_office,
                created_on__gte=datetime.now().date() - timedelta(days=delta)). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            bookings = ManualBooking.objects.filter(id__in=lr_generated_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct().order_by('-shipment_date')
            count = bookings.count()
        if self.duration == 'pending_total':
            loaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='loaded',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            lr_generated_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='lr_generated',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            lr_not_generated_bookings = [x for x in loaded_bookings if x not in lr_generated_bookings]
            bookings = ManualBooking.objects.filter(id__in=lr_not_generated_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            try:
                bs = BookingStatuses.objects.get(status='loaded')
                tl = bs.time_limit
            except BookingStatuses.DoesNotExist:
                tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            loaded_overdue_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='loaded',
                manual_booking__source_office=self.aaho_office,
                created_on__lt=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1)),
                created_on__gte=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta2))). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            lr_generated_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='lr_generated',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            lr_not_generated_bookings = [x for x in loaded_overdue_bookings if
                                                 x not in lr_generated_bookings]
            bookings = ManualBooking.objects.filter(id__in=lr_not_generated_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            details = '\nLR Generation Overdue Booking Ids: ' + ', '.join(
                bookings.values_list('booking_id', flat=True))
            count = bookings.count()
        return {'count': count, 'details': details}

    def task_confirm_booking(self):
        # print('Task New Booking')
        return {'count': 0, 'details': ''}

    def task_delivered(self):
        # print('Task Delivered')
        from restapi.models import BookingStatusesMapping, BookingStatuses
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            pod_uploaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_uploaded',
                manual_booking__destination_office=self.aaho_office,
                created_on__gte=datetime.now().date() - timedelta(days=delta)). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            bookings = ManualBooking.objects.filter(id__in=pod_uploaded_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
        if self.duration == 'pending_total':
            unloaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='unloaded',
                manual_booking__destination_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pod_uploaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_uploaded',
                manual_booking__destination_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pod_not_uploaded_bookings = [x for x in unloaded_bookings if x not in pod_uploaded_bookings]
            bookings = ManualBooking.objects.filter(id__in=pod_not_uploaded_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            try:
                bs = BookingStatuses.objects.get(status='unloaded')
                tl = bs.time_limit
            except BookingStatuses.DoesNotExist:
                tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            unloaded_overdue_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='unloaded',
                manual_booking__destination_office=self.aaho_office,
                created_on__lt=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1)),
                created_on__gte=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta2))). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            pod_uploaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='pod_uploaded',
                manual_booking__destination_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pod_not_uploaded_overdue_bookings = [x for x in unloaded_overdue_bookings if
                                             x not in pod_uploaded_bookings]
            bookings = ManualBooking.objects.filter(id__in=pod_not_uploaded_overdue_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
            details = '\nPoD Upload Overdue Booking Ids: ' + ', '.join(
                bookings.values_list('booking_id', flat=True))
        return {'count': count, 'details': details}

    def task_invoice_confirmation(self):
        # print('Task Invoice Confirmation')
        from restapi.models import BookingStatusesMapping, BookingStatuses
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30

            escalated_ic = BookingStatusesMapping.history.filter(
                booking_status_chain__booking_status__status__iexact='party_invoice_sent',booking_stage='escalated',
                created_on__gte=datetime.now().date() - timedelta(days=delta)).exclude(deleted=True).\
                values_list('manual_booking_id', flat=True)

            done_ic = BookingStatusesMapping.history.filter(
                booking_status_chain__booking_status__status__iexact='party_invoice_sent',
                booking_stage__in=['in_progress', 'done'],
                created_on__gte=datetime.now().date() - timedelta(days=delta)).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)

            escalated_done = list(set(escalated_ic).intersection(set(done_ic)))
            bookings = ManualBooking.objects.filter(id__in=escalated_done).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
        # print('Invoice Confirmation count: ',count)
        return {'count': count, 'details': details}

    def task_in_transit(self):
        # print('Task In Transit')
        from restapi.models import BookingStatusesMapping, BookingStatuses, BookingStatusesMappingLocation
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            unloaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='unloaded',
                manual_booking__destination_office=self.aaho_office,
                created_on__gte=datetime.now().date() - timedelta(days=delta)). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            bookings = ManualBooking.objects.filter(id__in=unloaded_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
        if self.duration == 'pending_total':
            lr_generated_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='lr_generated',
                manual_booking__destination_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            unloaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='unloaded',
                manual_booking__destination_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            not_unloaded_bookings = [x for x in lr_generated_bookings if x not in unloaded_bookings]
            bookings = ManualBooking.objects.filter(id__in=not_unloaded_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            try:
                bs = BookingStatuses.objects.get(status='lr_generated')
                tl = bs.time_limit
            except BookingStatuses.DoesNotExist:
                tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            lr_generated_overdue_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='lr_generated',
                manual_booking__destination_office=self.aaho_office,
                created_on__lt=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1)),
                created_on__gte=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta2))). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            unloaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='unloaded',
                manual_booking__destination_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            not_unloaded_overdue_bookings = [x for x in lr_generated_overdue_bookings if
                                         x not in unloaded_bookings]
            overdue_comments = 0
            overdue_comments_details = []
            for not_unloaded_overdue_booking in not_unloaded_overdue_bookings:
                lr_generated_bookings_mapping_comment = BookingStatusesMappingLocation.objects.filter(
                    booking_status_mapping__manual_booking_id=not_unloaded_overdue_booking).exclude(
                    Q(booking_status_mapping__manual_booking__booking_status='cancelled') |
                    Q(booking_status_mapping__manual_booking__deleted=True) |
                    Q(deleted=True)).order_by('-id')[:1]
                if not lr_generated_bookings_mapping_comment:
                    # print(not_unloaded_overdue_booking)
                    # continue
                    bsm = BookingStatusesMapping.objects.filter(manual_booking_id=not_unloaded_overdue_booking).exclude(deleted=True).order_by('-id')[:1]
                    cond1 = bsm[0].created_on.date() < (datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1))
                    cond2 = bsm[0].created_on.date() >= (datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1))
                    booking_id = bsm[0].manual_booking.booking_id
                else:
                    cond1 = lr_generated_bookings_mapping_comment[0].created_on.date() < (datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1))
                    cond2 = lr_generated_bookings_mapping_comment[0].created_on.date() >= (datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta2))
                    booking_id = lr_generated_bookings_mapping_comment[0].booking_status_mapping.manual_booking.booking_id
                if cond1 and cond2:
                    overdue_comments += 1
                    overdue_comments_details.append(booking_id)
            count = overdue_comments
            details = '\nUnload Overdue Booking Ids: ' + ', '.join(overdue_comments_details)
        return {'count': count, 'details': details}

    def task_pending_lr(self):
        # print('Task Pending LR')
        from restapi.models import BookingStatusesMapping, BookingStatuses
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            loaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='loaded',
                manual_booking__source_office=self.aaho_office,
                created_on__gte=datetime.now().date() - timedelta(days=delta)). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            bookings = ManualBooking.objects.filter(id__in=loaded_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
        if self.duration == 'pending_total':
            confirmed_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='confirmed',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            loaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='loaded',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            not_loaded_bookings = [x for x in confirmed_bookings if x not in loaded_bookings]
            bookings = ManualBooking.objects.filter(id__in=not_loaded_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            try:
                bs = BookingStatuses.objects.get(status='confirmed')
                tl = bs.time_limit
            except BookingStatuses.DoesNotExist:
                tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            confirmed_overdue_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='confirmed',
                manual_booking__source_office=self.aaho_office,
                created_on__lt=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta1)),
                created_on__gte=(datetime.now().date() - timedelta(minutes=tl) - timedelta(days=delta2))). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            loaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='loaded',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            lr_not_generated_bookings = [x for x in confirmed_overdue_bookings if
                                         x not in loaded_bookings]
            bookings = ManualBooking.objects.filter(id__in=lr_not_generated_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            count = bookings.count()
            details = '\nLoading Overdue Booking Ids: ' + ', '.join(
                bookings.values_list('booking_id', flat=True))
        return {'count': count, 'details': details}

    def task_pending_payments(self):
        # print('Task Pending Payments')
        from restapi.models import BookingStatusesMapping, BookingStatuses
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            inward_followup_completed_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='inward_followup_completed',
                manual_booking__source_office=self.aaho_office,
                created_on__gte=datetime.now().date() - timedelta(days=delta)). \
                exclude(deleted=True).values_list('manual_booking_id', flat=True)
            bookings = ManualBooking.objects.filter(id__in=inward_followup_completed_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            invs = Invoice.objects.filter(bookings__in=bookings, payment_received=False,
                                   date__gte=datetime.now().date() - timedelta(days=500)).distinct()

            count = invs.count()
        if self.duration == 'pending_total':
            invoicing_done_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['invoice_raised', 'party_invoice_sent', 'invoice_confirmed'],
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            inward_followup_completed_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='inward_followup_completed',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pending_payments_bookings = [x for x in invoicing_done_bookings if x not in inward_followup_completed_bookings]
            bookings = ManualBooking.objects.filter(id__in=pending_payments_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            invs = Invoice.objects.filter(bookings__in=bookings, payment_received=False,
                                          date__gte=datetime.now().date() - timedelta(days=500)).distinct()

            count = invs.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            invoicing_done_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=['invoice_raised', 'party_invoice_sent',
                                                                  'invoice_confirmed'],
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            inward_followup_completed_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__iexact='inward_followup_completed',
                manual_booking__source_office=self.aaho_office).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pending_payments_bookings = [x for x in invoicing_done_bookings if
                                         x not in inward_followup_completed_bookings]
            overdue_invoices = 0
            overdue_invoices_ids = []
            bookings = ManualBooking.objects.filter(id__in=pending_payments_bookings).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
            invs = Invoice.objects.filter(bookings__in=bookings, payment_received=False,
                                          date__gte=datetime.now().date() - timedelta(days=500)).distinct()
            for inv in invs:
                cond1 = (inv.date < (
                            datetime.now().date() - timedelta(days=to_int(inv.customer_fk.credit_period)) - timedelta(
                        days=delta1)))
                cond2 = (inv.date >= (
                            datetime.now().date() - timedelta(days=to_int(inv.customer_fk.credit_period)) - timedelta(
                        days=delta2)))
                if inv.customer_fk and cond1 and cond2:
                    overdue_invoices += 1
                    overdue_invoices_ids.append(inv.invoice_number)
            count = overdue_invoices
            details = '\nPending Payments Overdue Invoice Ids: ' + ', '.join(overdue_invoices_ids)
        return {'count': count, 'details': details}

    def task_my_inquiries(self):
        # print('Task My Inquiries')
        return {'count': 0, 'details': ''}

    def task_open_inquiries(self):
        # print('Task Open Inquiries')
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            inquiries = Requirement.objects.filter(aaho_office=self.aaho_office,
                                                   req_status__in=['fulfilled', 'cancelled'],
                                                   updated_on__gte=datetime.now().date() - timedelta(days=delta)).\
                values_list('id', flat=True)

            count = inquiries.count()
        if self.duration == 'pending_total':
            inquiries = Requirement.objects.filter(aaho_office=self.aaho_office,
                                                   req_status='open'). \
                values_list('id', flat=True)
            count = inquiries.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            inquiries = Requirement.objects.filter(aaho_office=self.aaho_office,
                                                   req_status='open',
                                                   updated_on__lt=(datetime.now().date() - timedelta(
                                                       minutes=tl) - timedelta(days=delta1)),
                                                   updated_on__gte=(datetime.now().date() - timedelta(
                                                       minutes=tl) - timedelta(days=delta2))
                                                   ).values_list('id', flat=True)
            count = inquiries.count()
            details = '\nOpen Inquiries Overdue Inquiry Ids: ' + ', '.join(map(str, list(inquiries.values_list('id', flat=True))))
        return {'count': count, 'details': details}

    def task_customer_inquiries(self):
        # print('Task Customer Inquiries')
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            inquiries = Requirement.objects.filter(aaho_office=self.aaho_office,
                                                   created_by__in=User.objects.filter(groups__name='sme')).\
                values_list('id', flat=True)
            open_inqs = set(Requirement.history.filter(id__in=inquiries, req_status='open',
                                                       updated_on__gte=datetime.now().date() - timedelta(days=delta)).
                            values_list('id', flat=True))
            count = len(open_inqs)
        if self.duration == 'pending_total':
            inquiries = Requirement.objects.filter(aaho_office=self.aaho_office,
                                                   created_by__in=User.objects.filter(groups__name='sme'),
                                                   req_status='unverified').values_list('id', flat=True)
            count = inquiries.count()
        if self.duration == 'overdue_less_2' or self.duration == 'overdue_2_to_7' or self.duration == 'overdue_7_to_30':
            tl = 0
            if self.duration == 'overdue_less_2':
                delta1 = self.overdue_less_2_delta1
                delta2 = self.overdue_less_2_delta2
            elif self.duration == 'overdue_2_to_7':
                delta1 = self.overdue_2_to_7_delta1
                delta2 = self.overdue_2_to_7_delta2
            else:
                delta1 = self.overdue_7_to_30_delta1
                delta2 = self.overdue_7_to_30_delta2
            inquiries = Requirement.objects.filter(aaho_office=self.aaho_office,
                                                   created_by__in=User.objects.filter(groups__name='sme'),
                                                   req_status='unverified',
                                                   created_on__lt=(datetime.now().date() - timedelta(
                                                       minutes=tl) - timedelta(days=delta1)),
                                                   created_on__gte=(datetime.now().date() - timedelta(
                                                       minutes=tl) - timedelta(days=delta2))
                                                   ).values_list('id', flat=True)
            count = inquiries.count()
            details = '\nCustomer Inquiries Overdue Inquiry Ids: ' + ', '.join(map(str, list(inquiries.values_list('id', flat=True))))
        return {'count': count, 'details': details}

    def task_new_inquiry(self):
        # print('Task New Inquiry')
        count = 0
        details = ''
        if self.duration == 'last_week' or self.duration == 'last_month':
            if self.duration == 'last_week':
                delta = 7
            else:
                delta = 30
            inquiries = Requirement.objects.filter(aaho_office=self.aaho_office,
                                                   created_by__in=User.objects.filter(groups__name='sales'),
                                                   created_on__gte=datetime.now().date() - timedelta(days=delta))
            count = inquiries.count()
        return {'count': count, 'details': details}


def get_tasks_completed_last_week(user, functionality, aaho_office, filter_params):
    bss = TaskFunctionalitySwitcher()
    return bss.case(user, functionality, aaho_office, filter_params, 'last_week')
    # return 0


def get_tasks_completed_last_month(user, functionality, aaho_office, filter_params):
    bss = TaskFunctionalitySwitcher()
    return bss.case(user, functionality, aaho_office, filter_params, 'last_month')


def get_tasks_pending_total(user, functionality, aaho_office, filter_params):
    bss = TaskFunctionalitySwitcher()
    return bss.case(user, functionality, aaho_office, filter_params, 'pending_total')


def get_tasks_overdue_less_2_days(user, functionality, aaho_office, filter_params):
    bss = TaskFunctionalitySwitcher()
    return bss.case(user, functionality, aaho_office, filter_params, 'overdue_less_2')


def get_tasks_overdue_2_to_7_days(user, functionality, aaho_office, filter_params):
    bss = TaskFunctionalitySwitcher()
    return bss.case(user, functionality, aaho_office, filter_params, 'overdue_2_to_7')


def get_tasks_overdue_7_to_30_days(user, functionality, aaho_office, filter_params):
    bss = TaskFunctionalitySwitcher()
    return bss.case(user, functionality, aaho_office, filter_params, 'overdue_7_to_30')


def get_total_tasks_completed_last_week(user, functionalities, aaho_office, filter_params):
    count = 0
    for func in functionalities:
        count += get_tasks_completed_last_week(user, func, aaho_office, filter_params)['count']
    return count


def get_total_tasks_completed_last_month(user, functionalities, aaho_office, filter_params):
    count = 0
    for func in functionalities:
        count += get_tasks_completed_last_month(user, func, aaho_office, filter_params)['count']
    return count


def get_total_tasks_pending_total(user, functionalities, aaho_office, filter_params):
    count = 0
    for func in functionalities:
        count += get_tasks_pending_total(user, func, aaho_office, filter_params)['count']
    return count


def get_total_tasks_overdue_less_2_days(user, functionalities, aaho_office, filter_params):
    count = 0
    for func in functionalities:
        count += get_tasks_overdue_less_2_days(user, func, aaho_office, filter_params)['count']
    return count


def get_total_tasks_overdue_less_2_days_details(user, functionalities, aaho_office, filter_params):
    details = ''
    for func in functionalities:
        count = get_tasks_overdue_less_2_days(user, func, aaho_office, filter_params)['count']
        if count > 0:
            details += '<div> </div>'
            details += '<div>' + get_tasks_overdue_less_2_days(user, func, aaho_office, filter_params)['details'] + '</div>'
    return details


def get_total_tasks_overdue_2_to_7_days(user, functionalities, aaho_office, filter_params):
    count = 0
    for func in functionalities:
        count += get_tasks_overdue_2_to_7_days(user, func, aaho_office, filter_params)['count']
    return count


def get_total_tasks_overdue_2_to_7_days_details(user, functionalities, aaho_office, filter_params):
    details = ''
    for func in functionalities:
        count = get_tasks_overdue_2_to_7_days(user, func, aaho_office, filter_params)['count']
        if count > 0:
            details += '<div> </div>'
            details += '<div>' + get_tasks_overdue_2_to_7_days(user, func, aaho_office, filter_params)['details'] + '</div>'
    return details


def get_total_tasks_overdue_7_to_30_days(user, functionalities, aaho_office, filter_params):
    count = 0
    for func in functionalities:
        count += get_tasks_overdue_7_to_30_days(user, func, aaho_office, filter_params)['count']
    return count


def get_total_tasks_overdue_7_to_30_days_details(user, functionalities, aaho_office, filter_params):
    details = ''
    for func in functionalities:
        count = get_tasks_overdue_7_to_30_days(user, func, aaho_office, filter_params)['count']
        if count > 0:
            details += '<div> </div>'
            details += '<div>' + get_tasks_overdue_7_to_30_days(user, func, aaho_office, filter_params)['details'] + '</div>'
    return details


def get_tasks_monitoring_row(user, role_id, aaho_office, response_json, filter_params):
    from restapi.models import EmployeeRolesFunctionalityMapping
    functionalities = set(
        EmployeeRolesFunctionalityMapping.objects.filter(employee_role__id=role_id, access='edit').
            exclude(employee_role__role__in=['tech', 'management', 'city_head']).values_list('td_functionality__functionality', flat=True))

    response_json['task_completed_this_week'] = get_total_tasks_completed_last_week(user, functionalities, aaho_office, filter_params)
    response_json['task_completed_this_month'] = get_total_tasks_completed_last_month(user, functionalities, aaho_office, filter_params)
    response_json['pending_tasks'] = get_total_tasks_pending_total(user, functionalities, aaho_office, filter_params)
    response_json['overdue_task_less_2_days'] = get_total_tasks_overdue_less_2_days(user, functionalities, aaho_office, filter_params)
    response_json['overdue_task_less_2_days_details'] = get_total_tasks_overdue_less_2_days_details(user, functionalities, aaho_office, filter_params)
    response_json['overdue_task_2_to_7_days'] = get_total_tasks_overdue_2_to_7_days(user, functionalities, aaho_office, filter_params)
    response_json['overdue_task_2_to_7_days_details'] = get_total_tasks_overdue_2_to_7_days_details(user, functionalities, aaho_office, filter_params)
    response_json['overdue_task_7_to_30_days'] = get_total_tasks_overdue_7_to_30_days(user, functionalities, aaho_office, filter_params)
    response_json['overdue_task_7_to_30_days_details'] = get_total_tasks_overdue_7_to_30_days_details(user, functionalities, aaho_office, filter_params)
    return response_json


def get_gps_device_location_from_dynamo(vehicle_number):
    dtc = DynamoTablesEnvConfiguration()
    gps_dt = DynamoTable(dtc.GPS_LOCATION)
    for item in gps_dt.scan():
        if item.vehicle_number == compare_format(vehicle_number) and item.is_active and item.location_time:
            return item
    return None
