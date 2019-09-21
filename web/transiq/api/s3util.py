import re

import shortuuid
from datetime import datetime
from django.conf import settings
from django.http.response import Http404, HttpResponseRedirect
from django.utils import timezone

from api import s3
from api.models import S3Upload
from api.utils import get_or_none

DOCUMENTS_BUCKET = settings.S3_REPORTS_BUCKET

S3_LR_DIR = 'lr'
S3_PAYMENT_DIR = 'payment'
S3_TALLY_INTEGRATION_DIR = 'tallyintegration'
S3_INVOICE_DIR = 'invoice'
S3_TABLE_DUMPS = 'table_dumps'

S3_DOWNLOADS_DIR = 'downloads'
S3_PICTURES_DIR = 'pictures'

S3_UPLOAD_DAILY_FREIGHT_DIR = 'freight'
S3_UPLOAD_GPS_LOG_DIR = 'gpsLog'
S3_UPLOAD_BULK_INWARD_PAYMENT_DIR = 'uploads/creditinward'
S3_UPLOAD_BULK_RECONCILE_OUTWARD_PAYMENT_DIR = 'uploads/reconcileoutwardpayments'

S3_UPLOADS_POD_DIR = 'uploads/pod'
S3_UPLOADS_VEHICLE_DIR = 'uploads/vehicle'
S3_UPLOADS_WEIGHING_SLIP_DIR = 'uploads/weighingslip'
S3_UPLOADS_DRIVER_DIR = 'uploads/driver'
S3_UPLOADS_OWNER_DIR = 'uploads/owner'
S3_UPLOADS_BANK_DIR = 'uploads/bank'
S3_UPLOADS_CHEQUE_DIR = 'uploads/cheque'
S3_UPLOADS_INVOICE_RECEIPT_DIR = 'uploads/invreceipt'
S3_SALES_REPORT_DIR = 'salesReport'
S3_INQUIRY_REPORT_DIR = 'inquiryReport'

S3_DIRS = [S3_LR_DIR, S3_PAYMENT_DIR, S3_INVOICE_DIR, S3_DOWNLOADS_DIR, S3_PICTURES_DIR, S3_UPLOADS_POD_DIR,
           S3_UPLOADS_BANK_DIR, S3_UPLOAD_DAILY_FREIGHT_DIR, S3_UPLOADS_VEHICLE_DIR, S3_UPLOADS_OWNER_DIR,
           S3_UPLOADS_DRIVER_DIR, S3_SALES_REPORT_DIR, S3_UPLOADS_CHEQUE_DIR, S3_UPLOAD_BULK_INWARD_PAYMENT_DIR,
           S3_UPLOADS_INVOICE_RECEIPT_DIR, S3_UPLOAD_GPS_LOG_DIR, S3_UPLOAD_BULK_RECONCILE_OUTWARD_PAYMENT_DIR,
           S3_TALLY_INTEGRATION_DIR, S3_TABLE_DUMPS, S3_UPLOADS_WEIGHING_SLIP_DIR, S3_INQUIRY_REPORT_DIR]

S3_FILE_NAME_PATTERN = re.compile(r'^[A-Za-z0-9_\-]+\.[A-Za-z0-9]{3,4}$')
S3_DIR_PATTERN = re.compile(r'|'.join([r'^%s$' % d for d in S3_DIRS]))


def redirect_to_s3_file(file_name):
    s3_upload = get_or_none(S3Upload, filename=file_name)
    if not s3_upload or s3_upload.deleted or not s3_upload.uploaded:
        raise Http404
    return HttpResponseRedirect(s3_upload.public_url())


def validate_filename(filename):
    if not S3_FILE_NAME_PATTERN.match(filename):
        raise s3.S3Error('%s filename not valid' % filename)


def validate_dir(folder):
    if not S3_DIR_PATTERN.match(folder):
        raise s3.S3Error('%s folder name not valid' % folder)


def create_s3_upload(folder, filename, verified=True, is_valid=True):
    validate_dir(folder)
    validate_filename(filename)
    uuid = get_short_uuid()
    s3_upload = get_or_create_s3_upload(bucket=DOCUMENTS_BUCKET, folder=folder, filename=filename, uuid=uuid,
                                        verified=verified, is_valid=is_valid)
    return s3_upload


def do_s3_upload(s3_upload, content, extra_agrs):
    s3.upload(s3_upload.bucket, s3_upload.key(), content, extra_agrs)
    s3_upload.uploaded = True
    s3_upload.uploaded_on = timezone.now()
    s3_upload.save()
    return s3_upload


def save_to_s3_lr(filename, content):
    return save_to_s3(S3_LR_DIR, filename, content, extra_agrs={'ContentType': 'application/pdf'})


def save_to_s3_lr_zip(filename, content):
    return save_to_s3(S3_LR_DIR, filename, content, extra_agrs={'ContentType': 'binary/octet-stream'})


def save_to_s3_payment(filename, content):
    return save_to_s3(S3_PAYMENT_DIR, filename, content, extra_agrs={})


def save_to_s3_table_dumps(filename, content):
    return save_to_s3(S3_TABLE_DUMPS, filename, content,
                      extra_agrs={'ContentType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})


def save_to_s3_tally_integration(filename, content):
    return save_to_s3(S3_TALLY_INTEGRATION_DIR, filename, content,
                      extra_agrs={'ContentType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})


def save_to_s3_daily_sales_report(filename, content):
    return save_to_s3(S3_SALES_REPORT_DIR, filename, content, extra_agrs={})


def save_to_s3_weekly_inquiry_report(filename, content):
    return save_to_s3(S3_INQUIRY_REPORT_DIR, filename, content, extra_agrs={})


def save_to_s3_payment_cheque(filename, content):
    return save_to_s3(S3_UPLOADS_CHEQUE_DIR, filename, content, extra_agrs={'ContentType': 'image/jpeg'})


def save_to_s3_gps_log(filename, content):
    return save_to_s3(S3_UPLOAD_GPS_LOG_DIR, filename, content, extra_agrs={'ContentType': 'binary/octet-stream'})


def save_to_s3_payment_invoice_receipt(filename, content):
    return save_to_s3(S3_UPLOADS_INVOICE_RECEIPT_DIR, filename, content, extra_agrs={'ContentType': 'image/jpeg'})


def save_to_s3_invoice(filename, content):
    return save_to_s3(S3_INVOICE_DIR, filename, content, extra_agrs={'ContentType': 'binary/octet-stream'})


def save_to_s3_downloads(filename, content):
    return save_to_s3(S3_DOWNLOADS_DIR, filename, content, extra_agrs={'ContentType': 'binary/octet-stream'})


def save_to_s3_uploads_pod(filename, content):
    return save_to_s3(S3_UPLOADS_POD_DIR, filename, content, extra_agrs={'ContentType': 'image/jpeg'})


def save_to_s3_uploads_vehicle(filename, content):
    return save_to_s3(S3_UPLOADS_VEHICLE_DIR, filename, content, extra_agrs={'ContentType': 'image/jpeg'})


def save_to_s3_uploads_supplier(filename, content):
    return save_to_s3(S3_UPLOADS_OWNER_DIR, filename, content, extra_agrs={'ContentType': 'image/jpeg'})


def save_to_s3_uploads_weighing_slip(filename, content):
    return save_to_s3(S3_UPLOADS_WEIGHING_SLIP_DIR, filename, content, extra_agrs={'ContentType': 'image/jpeg'})


def save_to_s3_uploads_owner(filename, content):
    return save_to_s3(S3_UPLOADS_OWNER_DIR, filename, content, extra_agrs={'ContentType': 'image/jpeg'})


def save_to_s3_uploads_driver(filename, content):
    return save_to_s3(S3_UPLOADS_DRIVER_DIR, filename, content, extra_agrs={'ContentType': 'image/jpeg'})


def save_to_s3_daily_freight(filename, content):
    return save_to_s3(S3_UPLOAD_DAILY_FREIGHT_DIR, filename, content, extra_agrs={'ContentType': 'binary/octet-stream'})


def save_to_s3_bulk_inward_payments(filename, content):
    return save_to_s3(S3_UPLOAD_BULK_INWARD_PAYMENT_DIR, filename, content,
                      extra_agrs={'ContentType': 'binary/octet-stream'})


def save_to_s3_bulk_reconcile_outward_payments(filename, content):
    return save_to_s3(S3_UPLOAD_BULK_RECONCILE_OUTWARD_PAYMENT_DIR, filename, content,
                      extra_agrs={'ContentType': 'binary/octet-stream'})


def save_to_s3_uploads_bank_doc(filename, content):
    return save_to_s3(S3_UPLOADS_BANK_DIR, filename, content, extra_agrs={})


def save_to_s3(folder, filename, content, extra_agrs):
    """overwrites if filename already exists"""
    if not content:
        raise s3.S3Error('no content')
    validate_dir(folder)
    validate_filename(filename)
    uuid = get_short_uuid()
    s3_upload = get_or_create_s3_upload(bucket=DOCUMENTS_BUCKET, folder=folder, filename=filename, uuid=uuid,
                                        verified=True, is_valid=True)
    return do_s3_upload(s3_upload=s3_upload, content=content, extra_agrs=extra_agrs)


def get_s3_upload(folder, filename):
    validate_dir(folder)
    validate_filename(filename)
    s3_upload = get_or_none(S3Upload, filename=filename)
    return s3_upload


def get_or_create_s3_upload(folder, filename, uuid, bucket, verified=True, is_valid=True):
    s3_upload = S3Upload(uuid=uuid if uuid else get_short_uuid(),
                         filename=filename if filename else get_short_uuid())
    s3_upload.bucket = bucket if bucket else 'fmsdocuments'
    s3_upload.folder = folder if folder else 'unknown'
    s3_upload.uploaded = False
    s3_upload.uploaded_on = datetime.now()
    s3_upload.verified = verified
    s3_upload.is_valid = is_valid
    s3_upload.save()

    return s3_upload


def get_latest(folder):
    validate_dir(folder)
    try:
        return S3Upload.objects.filter(folder=folder).latest('created_on')
    except S3Upload.DoesNotExist:
        return None


def get_short_uuid():
    exists = True
    new_uuid = None
    retries = 0
    while exists and retries < 4:
        new_uuid = shortuuid.uuid()
        exists = S3Upload.objects.filter(uuid=new_uuid).exists()
        retries += 1
    if not new_uuid:
        raise AssertionError('something has went very wrong')
    return new_uuid
