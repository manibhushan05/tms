import os
import re

import shortuuid as suuid

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from api import s3, s3util
from api.models import S3Upload, PaymentFile


shortuuid = suuid.ShortUUID(alphabet='0123456789abcdefghijklmnopqrstuvwxyz')

LR_PATH = os.path.join(settings.BASE_DIR, 'media/lr/')
PAYMENT_PATH = os.path.join(settings.BASE_DIR, 'media/bank_payment/')
INVOICE_PATH = os.path.join(settings.BASE_DIR, 'media/invoice/')

BANK_DOCS_PATH = os.path.join(settings.BASE_DIR, 'media/bank_account_docs/')
POD_PATH = os.path.join(settings.BASE_DIR, 'media/pod/')

PICS_PATH = os.path.join(settings.BASE_DIR, 'media/pictures/')
DOWNLOADS_PATH = os.path.join(settings.BASE_DIR, 'media/downloads/')

path_s3_dir = (
   (LR_PATH, s3util.S3_LR_DIR),
   (PAYMENT_PATH, s3util.S3_PAYMENT_DIR),
   (INVOICE_PATH, s3util.S3_INVOICE_DIR),

   (BANK_DOCS_PATH, s3util.S3_UPLOADS_BANK_DIR),
   (POD_PATH, s3util.S3_UPLOADS_POD_DIR),

   (PICS_PATH, s3util.S3_PICTURES_DIR),
   (DOWNLOADS_PATH, s3util.S3_DOWNLOADS_DIR),
)

s3_dir_path_map = dict((d, p) for p, d in path_s3_dir)


def migrate_all():
    create_s3_uuids()
    bulk_upload_files()
    create_payment_entries()


def create_payment_entries():
    s3_uploads = dict(S3Upload.objects.filter(
        folder=s3util.S3_PAYMENT_DIR, filename__startswith='RIQ76RBI'
    ).exclude(uploaded=False).values_list('filename', 'id'))

    already_created = set(PaymentFile.objects.values_list('name', flat=True))

    to_create = []
    for filename, id in s3_uploads.items():
        pattern = re.compile(r'^RIQ76RBI([0-9]{4}).*')
        match = pattern.match(filename)
        if not match:
            continue
        if filename in already_created:
            continue
        ddmm = match.groups()[0]
        day = int(ddmm[:2])
        month = int(ddmm[2:])
        if month > 12:
            day, month = month, day
        to_create.append(
            PaymentFile(date=timezone.datetime(year=2017, month=month, day=day).date(), name=filename, upload_id=id,
                        summary=False, successful=True)
        )
    PaymentFile.objects.bulk_create(to_create)


def get_new_short_uuids(count, exclude=None):
    exclude = exclude or set()
    uuids = set()
    while len(uuids) < count:
        new_uuid = shortuuid.uuid()
        if new_uuid in exclude:
            continue
        uuids.add(new_uuid)
    return uuids


def create_s3_uuids():
    bucketname = s3util.DOCUMENTS_BUCKET
    files_s3_dir_map = {}
    for path, s3_dir in path_s3_dir:
        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            if os.path.isfile(file_path):
                files_s3_dir_map[f] = s3_dir
    all_fileanames = set(files_s3_dir_map.keys())

    with transaction.atomic():
        files_present = S3Upload.objects.values_list('filename', 'uuid')
        existing_filenames = set()
        existing_uuids = set()
        for f, u in files_present:
            existing_filenames.add(f)
            existing_uuids.add(u)
        to_create_filenames = all_fileanames - existing_filenames
        new_uuids = get_new_short_uuids(count=len(to_create_filenames), exclude=existing_uuids)
        S3Upload.objects.bulk_create([S3Upload(bucket=bucketname, folder=files_s3_dir_map[f], uuid=u, filename=f
                                               ) for f, u in zip(to_create_filenames, new_uuids)])


def bulk_upload_files():
    to_upload_data = S3Upload.objects.filter(uploaded=False)
    to_upload = [(os.path.join(s3_dir_path_map[s.folder], s.filename), s.bucket, s.key(), s.id) for s in to_upload_data]
    client = s3.get_client()
    total = len(to_upload)
    count = 1
    for local_path, bucket, key, s_id in to_upload:
        count += 1
        try:
            client.upload_file(local_path, bucket, key)
            S3Upload.objects.filter(id=s_id).update(uploaded=True, uploaded_on=timezone.now())
        except Exception as e:
            pass

