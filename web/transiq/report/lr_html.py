import io
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED

from django.conf import settings

from api import s3util
from api.utils import display_date_format, display_datetime_format
from supplier.models import Vehicle
from report.util import aaho_office_details, get_company_data, get_lr_pdf_content
from team.helper.helper import to_int
from team.models import ManualBooking, ManualBookingS3Upload, LrS3Upload
from team.tasks import email_lr
from utils.models import AahoOffice, City


def get_lr_zipfile_name(booking):
    lr = booking.lr_numbers.all()
    if lr.count() == 0:
        return None
    if lr.count() == 1:
        return '{}.zip'.format(lr.last().lr_number.lower())
    else:
        return '{}.zip'.format('_'.join([lr.first().lr_number] + [value.lr_number[-3:] for value in lr[1:]]).lower())


def generate_lorry_receipt(booking):
    if not booking.lr_numbers.exists():
        return
    data = get_lr_data(booking)
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "a", ZIP_DEFLATED, False) as zip_file:
        for lr in booking.lr_numbers.all():
            data['lr_number'] = lr.lr_number
            content = get_lr_pdf_content(data)
            s3_upload = s3util.save_to_s3_lr(filename='{}.pdf'.format(lr.lr_number), content=content)
            LrS3Upload.objects.filter(lr_number=lr).update(is_valid=False)
            LrS3Upload.objects.create(lr_number=lr, s3_upload=s3_upload, is_valid=True)
            zip_file.writestr('{}.pdf'.format(lr.lr_number), content.getvalue())
    if settings.ENABLE_MAIL:
        email_lr.delay(booking.id)
    if get_lr_zipfile_name(booking=booking):
        s3_upload = s3util.save_to_s3_lr_zip(filename=get_lr_zipfile_name(booking=booking).format(booking.booking_id),
                                             content=zip_buffer.getvalue())
        ManualBookingS3Upload.objects.filter(booking=booking).update(is_valid=False)
        ManualBookingS3Upload.objects.create(booking=booking, s3_upload=s3_upload, is_valid=True)
    return


def get_date(date_str):
    try:
        d = datetime.strptime(date_str, '%d-%b-%Y %I:%M %p')
    except ValueError:
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            d = None
    return '' if not d else d.strftime('%d-%b-%Y')


def field_name():
    for field in ManualBooking._meta.get_fields(include_hidden=True, include_parents=True):
        print(field.get_internal_type())


def get_lr_data(booking):
    char_fields = ['consignor_name', 'consignor_address', 'consignor_pin', 'consignor_phone',
                   'consignor_gstin', 'consignee_name', 'consignee_address', 'consignee_pin',
                   'consignee_phone', 'consignee_gstin', 'billing_type',
                   'road_permit_number', 'party_invoice_number', 'party_invoice_amount', 'number_of_package',
                   'material', 'insurance_provider', 'insurance_policy_number', 'insurance_risk',
                   'gst_liability', 'driver_phone', 'driver_dl_number']
    text_fields = []
    date_fields = ['shipment_date', 'party_invoice_date', 'insurance_date', 'driver_dl_validity',
                   'billing_invoice_date']
    datetime_fields = []
    data = {}
    for prop in char_fields:
        data[prop] = '' if not getattr(booking, prop, '') else getattr(booking, prop, '')
    for prop in date_fields:
        data[prop] = display_date_format(getattr(booking, prop, ''))
    for prop in datetime_fields:
        data[prop] = display_datetime_format(getattr(booking, prop, ''))
    data['transiq'] = get_company_data()
    data['driver_dl_number'] = '' if not booking.driver_dl_number else booking.driver_dl_number
    data['from_city'] = '' if not isinstance(booking.from_city_fk, City) else booking.from_city_fk.name
    data['lorry_number'] = '' if not isinstance(booking.supplier_vehicle, Vehicle) else booking.supplier_vehicle.number()
    data['to_city'] = '' if not isinstance(booking.to_city_fk, City) else booking.to_city_fk.name
    data['consignor_city'] = '' if not isinstance(booking.consignor_city_fk, City) else booking.consignor_city_fk.name
    data['consignee_city'] = '' if not isinstance(booking.consignee_city_fk, City) else booking.consignee_city_fk.name
    data['driver_phone'] = booking.driver_phone if booking.driver_phone else ''
    if isinstance(booking.source_office, AahoOffice):
        branch = AahoOffice.objects.get(id=booking.source_office.id)
        branch_name = branch.branch.name if branch.branch else ''
    else:
        branch_name = ''
    data['branch'] = branch_name
    data['delivery_office'] = ''

    if to_int(data['party_invoice_amount']) == 0:
        data['party_invoice_amount'] = ''
    else:
        data['party_invoice_amount'] = '' if to_int(data['party_invoice_amount']) == 0 else to_int(
            data['party_invoice_amount'])

    if booking.insured_amount < 1:
        data['insurance_amount'] = ''

    office_id = '' if not booking.source_office else booking.source_office.id
    office_address, office_phone = aaho_office_details(office_id=office_id)
    data['office_id'] = office_id
    data['office_address'] = office_address
    data['office_phone'] = office_phone
    data['is_print_payment_mode_instruction'] = booking.is_print_payment_mode_instruction
    return data
