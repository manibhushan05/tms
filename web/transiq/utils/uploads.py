import boto3
import botocore
import urllib.request
import os
import pandas as pd
from api.models import S3Upload

from api.s3 import download, download_file
from broker.models import BrokerOwner
from owner.models import Owner
from sme.models import Sme
from team.models import Invoice


def download_invoice_pdf():
    sme = Sme.objects.filter(company_code__in=['IDK', 'IDR', 'IDS', 'IDL', 'IDH', 'HPR', 'DCL', 'HPB'])
    for s in sme:
        for invoice in Invoice.objects.filter(customer_fk=s).filter(date__range=['2018-03-01', '2018-08-31']):
            if isinstance(invoice.s3_upload, S3Upload):
                download_file(invoice.s3_upload.bucket, invoice.s3_upload.key(),
                              os.path.join('invoices_file/', s.company_code, invoice.s3_upload.filename))


def download_owner_docs():
    # count = 0
    for owner in Owner.objects.order_by('-id'):
        print(owner.id, owner.get_name())
        bo = BrokerOwner.objects.filter(owner=owner)
        if bo:
            # count = count + 1
            # print('broker owner different')
            broker = bo[0].broker
            p_name = broker.get_name()
            # print(count)
        else:
            p_name = owner.get_name()
        for doc in owner.owner_files.filter(document_category__in=['PAN', 'DEC']).exclude(s3_upload=None):
            if isinstance(doc.s3_upload, S3Upload):
                download_file(doc.s3_upload.bucket, doc.s3_upload.key(),
                              os.path.join('/Users/aaho/workspace/repo/data/owner_docs/', doc.document_category,
                                           p_name + '-' + doc.s3_upload.filename))


def download_invoices_document():
    df = pd.read_excel('../../data/Sale Sample Final.xlsx')
    try:
        os.makedirs('invoice-data')
    except:
        pass
    for i, row in df.iterrows():
        try:
            invoice = Invoice.objects.get(invoice_number=row['Vch No.'])
            try:
                os.makedirs('invoice-data/'+invoice.invoice_number)
            except:
                pass
        except:
            pass
    for i, row in df.iterrows():
        try:
            invoice = Invoice.objects.get(invoice_number=row['Vch No.'])
            if isinstance(invoice.s3_upload, S3Upload):
                download_file(invoice.s3_upload.bucket, invoice.s3_upload.key(),
                              os.path.join('invoice-data/', invoice.invoice_number, invoice.s3_upload.filename))
            for booking in invoice.bookings.all():
                for doc in booking.podfile_set.filter(verified=True, is_valid=True):
                    download_file(doc.s3_upload.bucket, doc.s3_upload.key(),
                                  os.path.join('invoice-data/', invoice.invoice_number, doc.s3_upload.filename))
                for bill in booking.outward_payment_bill.all():
                    doc=S3Upload.objects.filter(filename__istartswith='{}-{}'.format('OPB', bill.bill_number),
                                            filename__iendswith='.pdf').last()
                    download_file(doc.bucket, doc.key(),
                                  os.path.join('invoice-data/', invoice.invoice_number, doc.filename))

                vehicle = booking.vehicle
                if vehicle:
                    for doc in vehicle.vehicle_files.all():
                        download_file(doc.s3_upload.bucket, doc.s3_upload.key(),
                                      os.path.join('invoice-data/', invoice.invoice_number, doc.s3_upload.filename))

                    if vehicle.owner:
                        for doc in vehicle.owner.owner_files.all():
                            download_file(doc.s3_upload.bucket, doc.s3_upload.key(),
                                          os.path.join('invoice-data/', invoice.invoice_number, doc.s3_upload.filename))

                    if vehicle.driver:
                        for doc in vehicle.driver.driver_files.all():
                            download_file(doc.s3_upload.bucket, doc.s3_upload.key(),
                                          os.path.join('invoice-data/', invoice.invoice_number, doc.s3_upload.filename))


        except Invoice.DoesNotExist:
            print(row['Vch No.'])
