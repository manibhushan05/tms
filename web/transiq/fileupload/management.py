import boto3
import botocore

from api.s3 import download, get_client
from team.models import ManualBooking, LrNumber
from fileupload.models import PODFile, ChequeFile


def check_pod_status():
    for booking in ManualBooking.objects.all():
        for lr in booking.lr_numbers.all():
            if lr.pod_files.all():
                if booking.pod_status == 'pending':
                    print (booking)


def update_pod_lr_booking():
    for pod in PODFile.objects.all():
        pod.booking = pod.lr_number.booking
        pod.save()


def downloads_cheque_image():
    print(ChequeFile.objects.filter(customer_name__icontains='Denis Chem Lab Limited').count())
    for cheque in ChequeFile.objects.filter(customer_name__icontains='Denis Chem Lab Limited'):
        try:
            # s3.Bucket(cheque.s3_upload.bucket).download_file(cheque.s3_upload.key(), cheque.s3_upload.filename)
            # s3 = boto3.resource('s3')
            client = get_client()
            client.download_file('aahodocuments', cheque.s3_upload.key(), cheque.s3_upload.filename)
            print(cheque.s3_upload.key(), cheque.s3_upload.filename)
        except:
            raise
