import io
import re

import six
from boto3.session import Session
from botocore.config import Config

AWS_ACCESS_KEY = 'AKIAJXFC3JRVYNIHX2UA'
AWS_ACCESS_SECRET_KEY = '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'

S3_BUCKET_NAME_PATTERN = re.compile(r'^[a-z0-9][a-z0-9\-]{1,61}[a-z0-9]$')
S3_KEY_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9\-./_]{3,253}[a-zA-Z0-9]$')


class S3Error(AssertionError):
    pass


def get_client():
    session = Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY)
    return session.client('s3', config=Config(signature_version='s3v4'))


def validate_bucket_name(bucket):
    if not S3_BUCKET_NAME_PATTERN.match(bucket) or '--' in bucket:
        raise S3Error('invalid bucket name {}'.format(bucket))


def validate_key_name(key):
    if not S3_KEY_PATTERN.match(key):
        raise S3Error('invalid s3 key name {}'.format(key))


def validate_content(content):
    if content is None:
        raise S3Error('no content to upload')
    if not isinstance(content, bytes) and not hasattr(content, 'read'):
        raise S3Error('content is neither a string nor a file like object, content={}'.format(content))


def download(bucket, key):
    """
    always returns a byte string
    """
    validate_bucket_name(bucket)
    validate_key_name(key)
    client = get_client()

    # do a buffered download
    bytes_io = io.BytesIO()
    client.download_fileobj(bucket, key, bytes_io)

    # hope that stuff is not too big, and just return content
    return bytes_io.getvalue()

def download_file(bucket, key, filename):
    """
    always returns a byte string
    """
    validate_bucket_name(bucket)
    validate_key_name(key)
    client = get_client()

    client.download_file(bucket, key, filename)


def upload(bucket, key, content, extra_agrs):
    """replace if key exists"""
    # validate_content(content)
    validate_bucket_name(bucket)
    validate_key_name(key)
    client = get_client()
    if extra_agrs:
        client.put_object(Body=content, Bucket=bucket, Key=key, ContentType=extra_agrs['ContentType'])
    else:
        client.put_object(Body=content, Bucket=bucket, Key=key)


def delete(bucket, key):
    validate_bucket_name(bucket)
    validate_key_name(key)

    client = get_client()
    client.delete_object(Bucket=bucket, Key=key)


def modify_metadata():
    from api.models import S3Upload
    client = get_client()
    for s3_upload in S3Upload.objects.filter(folder='uploads/pod').filter(id__gte=34783).order_by('-id'):
        try:
            s3_obj = client.get_object(Bucket=s3_upload.bucket, Key=s3_upload.key())
            client.put_object(Body=s3_obj['Body'].read(), Bucket=s3_upload.bucket, Key=s3_upload.key(),
                              ContentType='image/jpeg')
            print(s3_upload.id)
        except:
            print(s3_upload.filename)
