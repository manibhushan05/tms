import os
import urllib
import boto3
import botocore
from api import s3

from django.conf import settings

BASE_DIR = settings.BASE_DIR

BUCKET_NAME = 'fmsdocuments'


def s3_url(key):
    return 'https://' + BUCKET_NAME + '.s3.amazonaws.com/' + key


def doc_filename(vehicle_number, doc_type, doc_id):
    file_name = vehicle_number.replace(' ', '') + '_' + doc_type
    if doc_id and doc_id.strip():
        file_name = file_name + '_' + doc_id.replace(' ', '')
    file_name += '.jpg'
    return file_name


def doc_filepath(vehicle_number, doc_type, doc_id):
    dir_path = doc_dirpath(vehicle_number)
    file_name = doc_filename(vehicle_number, doc_type, doc_id)

    doc_file = os.path.join(dir_path, file_name)
    return doc_file


def doc_dirpath(vehicle_number):
    sub_dir = vehicle_number.replace(' ', '')

    doc_dir = os.path.join(BASE_DIR, 'fms', 'docs', sub_dir, 'images')
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir)

    return doc_dir


def downloadable_documents_data(vehicle, excluded):
    data = vehicle.to_json()
    doc_fields = {
        'rc_doc': 'REGISTRATION',
        'insurance_doc': 'INSURANCE',
        'permit_doc': 'PERMIT',
        'fitness_doc': 'FITNESS',
        'puc_doc': 'PUC',
        'owner_pan_doc': 'PAN',
        'owner_dec_doc': 'DECLARATION',
        'driver_dl_doc': 'DRIVER_LICENCE',
    }

    excluded_key_map = {
        'rc_doc': 'rc',
        'insurance_doc': 'in',
        'permit_doc': 'perm',
        'fitness_doc': 'fit',
        'puc_doc': 'puc',
        'owner_pan_doc': 'pan',
        'owner_dec_doc': 'dec',
        'driver_dl_doc': 'dl',
    }

    to_download = {}

    for key, doc_type in doc_fields.items():
        if excluded_key_map[key] in excluded:
            continue
        doc_data = data.get(key, None)
        s3_key = None if not doc_data else doc_data.get('url', None)
        doc_id = None if not doc_data else doc_data.get('doc_id', None)
        if s3_key:
            doc_data['s3_key'] = s3_key
            doc_data['s3_url'] = s3_url(s3_key)
            doc_data['filename'] = doc_filename(vehicle.number().upper(), doc_type, doc_id)
            doc_data['doc_type'] = doc_type
            to_download[key] = doc_data

    return to_download


def valid_fms_documents_s3():
    conn = s3.get_client()  # again assumes boto.cfg setup, assume AWS S3
    for key in conn.list_objects(Bucket='fmsdocuments')['Contents']:
        s3_key=key['Key'].split('/')
        print(s3_key[-1])
        if s3_key[-1]:
            urllib.urlretrieve('https://s3-ap-southeast-1.amazonaws.com/fmsdocuments/%s'%(key['Key']), s3_key[-1])