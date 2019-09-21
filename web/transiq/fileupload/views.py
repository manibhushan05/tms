# encoding: utf-8
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import UnreadablePostError
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils.text import slugify
from django.views.generic import ListView
from rest_framework.authtoken.models import Token

from api import s3util
from api.helper import json_error_response
from api.models import S3Upload
from api.utils import get_ext, get_or_none, int_or_none, random_id
from fileupload.models import PODFile, VehicleFile, OwnerFile, DriverFile, ChequeFile, InvoiceReceiptFile, \
    INVOICE_SENT_MODE_CHOICES, INVOICE_CONFIRM_MODE_CHOICES, WeighingSlip
from fileupload.response import JSONResponse, response_mimetype
from fileupload.serialize import serialize
from owner.vehicle_util import display_format
from restapi.helper_api import check_booking_status, create_new_booking_status, update_booking_status
from restapi.serializers.file_upload import PODFileSerializer
from supplier.models import Supplier,Vehicle,Driver
from team.helper.helper import django_date_format
from team.models import LrNumber, ManualBooking, Invoice


def upload_pod_page(request):
    lr_numbers = LrNumber.objects.filter(Q(datetime__date__gte=datetime.now().date() - timedelta(days=180)) & (
            Q(booking__pod_status='pending') | Q(booking__pod_status='rejected') | Q(
        booking__pod_status='unverified'))).order_by('-datetime').values(
        'id', 'lr_number')
    bookings = []
    for booking in ManualBooking.objects.filter(
            (Q(pod_status__iexact='pending') | Q(pod_status__iexact='rejected')) & (
                    Q(booking_id__istartswith='BROKER') | Q(booking_id__istartswith='AB'))).exclude(
        Q(booking_status='cancelled') | Q(deleted=True)):
        bookings.append({'booking_id': booking.booking_id})
    return render(
        request=request,
        template_name='fileupload/pod_upload.html',
        context={'lr_numbers': lr_numbers, 'bookings': bookings}
    )


def upload_pod(request):
    token = get_or_none(Token, key=request.POST.get('Authorization'))
    if not isinstance(token, Token):
        return HttpResponseRedirect('/login/')
    try:
        lr_number_id = request.POST.get('lr_number', None)

        if not lr_number_id:
            return json_error_response('lr_number id not provided', status=400)
        if str(lr_number_id).startswith('BROKER') or str(lr_number_id).startswith('AB'):
            booking = get_or_none(ManualBooking, booking_id=lr_number_id)
            lr_obj = None
        else:
            lr_obj = get_or_none(LrNumber, id=lr_number_id)
            booking = None if not isinstance(lr_obj, LrNumber) else lr_obj.booking

        if not (isinstance(lr_obj, LrNumber) or isinstance(booking, ManualBooking)):
            return json_error_response('LrNumber with id=%s not found' % lr_number_id, status=404)

        if not request.FILES:
            return json_error_response('no file to upload', status=400)

        upload_file = request.FILES.get('file')
        pod_file = create_pod_file(lr_number=lr_obj, upload_file=upload_file, user=token.user, booking=booking)
        booking_unloaded = check_booking_status(booking, 'unloaded')
        if not booking_unloaded:
            create_new_booking_status(booking, 'unloaded', User.objects.get(username='admin'))
        else:
            update_booking_status(booking, 'unloaded', 'in_progress', User.objects.get(username='admin'))
        booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
        if not booking_pod_uploaded:
            create_new_booking_status(booking, 'pod_uploaded', token.user)
        else:
            update_booking_status(booking, 'pod_uploaded', 'in_progress', token.user)
        return upload_json_response(request, data={'files': [serialize(pod_file)]})
    except UnreadablePostError:
        return HttpResponseRedirect('/upload/pod/')


def delete_pod(request, pk):
    pod_file_id = pk

    if not pod_file_id:
        return json_error_response('pod_file_id not provided', status=400)

    pod_file = get_or_none(PODFile, id=pod_file_id)

    if not pod_file:
        return json_error_response('PODFile with id=%s not found' % pod_file_id, status=404)

    pod_file.s3_upload.delete_from_s3()
    pod_file.delete()

    return upload_json_response(request, True)


def pod_list(request):
    files = [serialize(p) for p in PODFile.objects.select_related('lr_number', 's3_upload').all()]
    return upload_json_response(request, data={'files': files})


def upload_json_response(request, data):
    response = JSONResponse(data, mimetype=response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def get_new_serial(model, **kwargs):
    retry = 0
    while True:
        if retry > 8:
            raise AssertionError('Max retry reached, something is not right')
        serial = random_id(num_digits=8)
        exists = model.objects.filter(serial=serial, **kwargs).exists()
        if not exists:
            return serial
        retry += 1


def create_pod_file(lr_number, upload_file, user, booking):
    orig_filename = upload_file.name
    if isinstance(booking, ManualBooking):
        serial = get_new_serial(PODFile, booking=booking)
        new_filename = 'POD-%s-%s.%s' % (slugify(booking.booking_id), serial, get_ext(orig_filename))
        mb = ManualBooking.objects.get(booking_id=booking.booking_id)
        mb.pod_status = 'unverified'
        mb.pod_date = datetime.now()
        mb.save()
    elif isinstance(lr_number, LrNumber):
        serial = get_new_serial(PODFile, lr_number=lr_number)
        new_filename = 'POD-%s-%s.%s' % (slugify(lr_number.lr_number), serial, get_ext(orig_filename))
        mb = ManualBooking.objects.get(booking_id=lr_number.booking.booking_id)
        mb.pod_status = 'unverified'
        mb.pod_date = datetime.now()
        mb.save()
    else:
        serial = random_id(num_digits=8)
        new_filename = 'POD-%s-%s.%s' % (serial, serial, get_ext(orig_filename))

    s3_upload = s3util.save_to_s3_uploads_pod(new_filename, upload_file)
    podfile_serializer = PODFileSerializer(data={
        'serial': serial,
        'lr_number': lr_number.id if isinstance(lr_number, LrNumber) else None,
        'booking': booking.id if isinstance(booking, ManualBooking) else None,
        'uploaded_by': user.username,
        'changed_by': user.username,
        's3_upload': s3_upload.id
    })
    if podfile_serializer.is_valid():
        pod_file = podfile_serializer.save()
        print(pod_file)
        return pod_file
    return None


'''
Upload weight receipt file
'''


def upload_weighing_slip_docs(request):
    token = get_or_none(Token, key=request.POST.get('Authorization'))
    if not isinstance(token, Token):
        return HttpResponseRedirect('/login/')
    try:
        mb_id = int_or_none(request.POST.get('mb_id', None))

        if not mb_id:
            return json_error_response('mb_id id not provided', status=400)

        booking = get_or_none(ManualBooking, id=mb_id)

        if not isinstance(booking, ManualBooking):
            return json_error_response('Manual Booking with id=%s not found' % mb_id, status=404)

        if not request.FILES:
            return json_error_response('no file to upload', status=400)

        upload_file = request.FILES.get('file')
        weighing_slip_files = create_weighing_slip_file(booking, upload_file, token.user)

        return upload_json_response(request, data={'files': [serialize(weighing_slip_files)]})
    except UnreadablePostError:
        return HttpResponseRedirect('/upload/upload-vehicle-document-page/')


def create_weighing_slip_file(booking, upload_file, user):
    orig_filename = upload_file.name
    serial = get_new_serial(WeighingSlip, booking=booking)
    new_filename = 'weighing-slip-{}-{}.{}'.format(
        slugify(booking.booking_id), serial, get_ext(orig_filename)
    )
    s3_upload = s3util.save_to_s3_uploads_weighing_slip(new_filename, upload_file)
    weighing_slip = WeighingSlip.objects.create(booking=booking,  serial=serial,verified=True,is_valid=True,
                                                s3_upload=s3_upload, uploaded_by=user)
    return weighing_slip


def create_weighing_slip_entries():
    uploads = S3Upload.objects.filter(folder='uploads/weighingslip')
    for up in uploads:
        vehicle = None if up.filename.startswith('.') else up.filename.split('-')[1]
        if not vehicle:
            continue
        if '_' in up.filename:
            serial = up.filename[13:20]
        else:
            serial = ''
        vehicle = Vehicle.objects.get(id=vehicle)
        try:
            VehicleFile.objects.create(
                vehicle=vehicle,
                serial=serial,
                s3_upload=up,
            )
        except:
            pass


def weighing_slip_list(request):
    files = [serialize(p) for p in WeighingSlip.objects.all()]
    return upload_json_response(request, data={'files': files})


def delete_weighing_slip(request, pk):
    weighing_slip_id = pk

    if not weighing_slip_id:
        return json_error_response('weighing_slip_id not provided', status=400)

    weighing_slip = get_or_none(WeighingSlip, id=weighing_slip_id)

    if not weighing_slip:
        return json_error_response('weighing_slip_id with id=%s not found' % weighing_slip_id, status=404)

    weighing_slip.s3_upload.delete_from_s3()
    weighing_slip.delete()

    return upload_json_response(request, True)


'''
VEHICLE DOCUMENTS UPLAOD

'''


def upload_vehicle_document_page(request):
    document_categories = (
        ('PUC', 'Puc Certificate'),
        ('FIT', 'Fitness Certificate'),
        ('REG', 'Registration Certificate'),
        ('PERM', 'Permit Certificate'),
        ('INS', 'Insurance Certificate'),
    )
    vehicles = [{'id': vehicle.id, 'vehicle_number': display_format(vehicle.vehicle_number)} for vehicle in
                Vehicle.objects.all()]
    return render(
        request=request,
        template_name='fileupload/upload_vehicle_documents.html',
        context={'document_categories': document_categories, 'vehicles': vehicles}
    )


def upload_vehicle_docs(request):
    token = get_or_none(Token, key=request.POST.get('Authorization'))
    if not isinstance(token, Token):
        return HttpResponseRedirect('/login/')
    try:
        vehicle_number_id = int_or_none(request.POST.get('vehicle_number', None))
        document_category = request.POST.get('document_category', None)

        if not vehicle_number_id:
            return json_error_response('vehicle_number id not provided', status=400)
        if not document_category:
            return json_error_response('document category id not provided', status=400)

        vehicle = get_or_none(Vehicle, id=vehicle_number_id)

        if not vehicle:
            return json_error_response('Vehicle with id=%s not found' % vehicle_number_id, status=404)

        if not request.FILES:
            return json_error_response('no file to upload', status=400)

        upload_file = request.FILES.get('file')
        vehicle_files = create_vehicle_file(vehicle, document_category, upload_file, token.user)

        return upload_json_response(request, data={'files': [serialize(vehicle_files)]})
    except UnreadablePostError:
        return HttpResponseRedirect('/upload/upload-vehicle-document-page/')


def create_vehicle_file(vehicle, document_category, upload_file, user):
    orig_filename = upload_file.name
    serial = get_new_serial(VehicleFile, supplier_vehicle=vehicle)
    new_filename = 'vehicle-%s-%s-%s.%s' % (
        document_category.lower(), slugify(vehicle.vehicle_number), serial, get_ext(orig_filename)
    )
    s3_upload = s3util.save_to_s3_uploads_vehicle(new_filename, upload_file)
    vehicle_file = VehicleFile.objects.create(supplier_vehicle=vehicle, document_category=document_category, serial=serial,
                                              s3_upload=s3_upload, uploaded_by=user)
    return vehicle_file


def create_vehicle_entries():
    uploads = S3Upload.objects.filter(folder='uploads/vehicle')
    for up in uploads:
        vehicle = None if up.filename.startswith('.') else up.filename.split('-')[1]
        if not vehicle:
            continue
        if '_' in up.filename:
            serial = up.filename[13:20]
        else:
            serial = ''
        vehicle = Vehicle.objects.get(id=vehicle)
        try:
            VehicleFile.objects.create(
                vehicle=vehicle,
                serial=serial,
                s3_upload=up,
            )
        except:
            pass


def vehicle_list(request):
    files = [serialize(p) for p in VehicleFile.objects.select_related('vehicle', 's3_upload').all()]
    return upload_json_response(request, data={'files': files})


def delete_vehicle(request, pk):
    vehicle_file_id = pk

    if not vehicle_file_id:
        return json_error_response('vehicle_file_id not provided', status=400)

    vehicle_file = get_or_none(VehicleFile, id=vehicle_file_id)

    if not vehicle_file:
        return json_error_response('VehicleFile with id=%s not found' % vehicle_file_id, status=404)

    vehicle_file.s3_upload.delete_from_s3()
    vehicle_file.delete()

    return upload_json_response(request, True)


'''
SUPPLIER DOCUMENTS UPLAOD

'''


def upload_supplier_document_page(request):
    document_categories = (
        ('PAN', 'PAN Card'),
        ('DL', 'Driving Licence'),
        ('EL', 'Election ID'),
        ('AC', 'Aadhar Card'),
        ('PT', 'Passport'),
        ('RC', 'Ration Card'),
        ('DEC', 'Declaration'),
    )
    suppliers = [{'id': supplier.id, 'name': supplier.name, 'phone': supplier.phone} for supplier in
                 Supplier.objects.all()]
    return render(
        request=request,
        template_name='fileupload/upload_supplier_documents.html',
        context={'document_categories': document_categories, 'suppliers': suppliers}
    )


def upload_supplier_docs(request):
    token = get_or_none(Token, key=request.POST.get('Authorization'))
    print(token)
    if not isinstance(token, Token):
        return HttpResponseRedirect('/login/')
    try:
        supplier_id = int_or_none(request.POST.get('supplier', None))
        document_category = request.POST.get('document_category', None)

        if not supplier_id:
            return json_error_response('supplier_id id not provided', status=400)
        if not document_category:
            return json_error_response('document category id not provided', status=400)

        supplier = get_or_none(Supplier, id=supplier_id)
        print(supplier)
        if not supplier:
            return json_error_response('Supplier with id=%s not found' % supplier_id, status=404)

        if not request.FILES:
            return json_error_response('no file to upload', status=400)

        upload_file = request.FILES.get('file')
        vehicle_files = create_supplier_file(supplier, document_category, upload_file, token.user)

        return upload_json_response(request, data={'files': [serialize(vehicle_files)]})
    except UnreadablePostError:
        return HttpResponseRedirect('/upload/upload-supplier-document-page/')


def create_supplier_file(supplier, document_category, upload_file, user):
    orig_filename = upload_file.name
    serial = get_new_serial(OwnerFile, supplier=supplier)
    new_filename = 'supplier-%s-%s-%s-%s.%s' % (
        document_category.lower(), slugify(supplier.name), slugify(supplier.phone), serial,
        get_ext(orig_filename)
    )
    s3_upload = s3util.save_to_s3_uploads_supplier(new_filename, upload_file)
    supplier_file = OwnerFile.objects.create(supplier=supplier, document_category=document_category, serial=serial,
                                             s3_upload=s3_upload, uploaded_by=user)
    return supplier_file


def create_supplier_entries():
    uploads = S3Upload.objects.filter(folder='uploads/supplier')
    for up in uploads:
        supplier = None if up.filename.startswith('.') else up.filename.split('-')[1]
        if not supplier:
            continue
        if '_' in up.filename:
            serial = up.filename[13:20]
        else:
            serial = ''
        supplier_obj = Supplier.objects.get(id=supplier)
        try:
            OwnerFile.objects.create(
                supplier=supplier_obj,
                serial=serial,
                s3_upload=up,
            )
        except:
            pass


def supplier_list(request):
    files = [serialize(p) for p in OwnerFile.objects.select_related('supplier', 's3_upload').all()]
    return upload_json_response(request, data={'files': files})


def delete_supplier(request, pk):
    supplier_file_id = pk

    if not supplier_file_id:
        return json_error_response('supplier_file_id not provided', status=400)

    supplier_file = get_or_none(OwnerFile, id=supplier_file_id)

    if not supplier_file:
        return json_error_response('SupplierFile with id=%s not found' % supplier_file_id, status=404)

    supplier_file.s3_upload.delete_from_s3()
    supplier_file.delete()

    return upload_json_response(request, True)


'''
DRIVER DOCUMENTS UPLAOD

'''


def upload_driver_document_page(request):
    document_categories = (
        ('PAN', 'PAN Card'),
        ('DL', 'Driving Licence'),
        ('EL', 'Election ID'),
        ('AC', 'Aadhar Card'),
        ('PT', 'Passport'),
        ('RC', 'Ration Card'),
    )
    drivers = [{'id': driver.id, 'name': driver.name, 'phone': driver.phone} for driver in
               Driver.objects.all()]
    return render(
        request=request,
        template_name='fileupload/upload_driver_documents.html',
        context={'document_categories': document_categories, 'drivers': drivers}
    )


def upload_driver_docs(request):
    token = get_or_none(Token, key=request.POST.get('Authorization'))
    if not isinstance(token, Token):
        return HttpResponseRedirect('/login/')
    try:
        driver_id = int_or_none(request.POST.get('driver', None))
        document_category = request.POST.get('document_category', None)

        if not driver_id:
            return json_error_response('driver_id id not provided', status=400)
        if not document_category:
            return json_error_response('document category id not provided', status=400)

        driver = get_or_none(Driver, id=driver_id)

        if not driver:
            return json_error_response('Driver with id=%s not found' % driver, status=404)

        if not request.FILES:
            return json_error_response('no file to upload', status=400)

        upload_file = request.FILES.get('file')
        driver_files = create_driver_file(driver, document_category, upload_file, token.user)

        return upload_json_response(request, data={'files': [serialize(driver_files)]})
    except UnreadablePostError:
        return HttpResponseRedirect('/upload/upload-driver-document-page/')


def create_driver_file(driver, document_category, upload_file, user):
    orig_filename = upload_file.name
    serial = get_new_serial(DriverFile, supplier_driver=driver)
    new_filename = 'driver-%s-%s-%s-%s.%s' % (
        document_category.lower(), slugify(driver.name), slugify(driver.phone), serial,
        get_ext(orig_filename)
    )
    s3_upload = s3util.save_to_s3_uploads_driver(new_filename, upload_file)
    driver_file = DriverFile.objects.create(supplier_driver=driver, document_category=document_category, serial=serial,
                                            s3_upload=s3_upload, uploaded_by=user)
    return driver_file


def create_driver_entries():
    uploads = S3Upload.objects.filter(folder='uploads/driver')
    for up in uploads:
        driver = None if up.filename.startswith('.') else up.filename.split('-')[1]
        if not driver:
            continue
        if '_' in up.filename:
            serial = up.filename[13:20]
        else:
            serial = ''
        driver_obj = Driver.objects.get(id=driver)
        try:
            DriverFile.objects.create(
                driver=driver_obj,
                serial=serial,
                s3_upload=up,
            )
        except:
            pass


def driver_list(request):
    files = [serialize(p) for p in DriverFile.objects.select_related('driver', 's3_upload').all()]
    return upload_json_response(request, data={'files': files})


def delete_driver(request, pk):
    driver_file_id = pk

    if not driver_file_id:
        return json_error_response('driver_file_id not provided', status=400)

    driver_file = get_or_none(DriverFile, id=driver_file_id)

    if not driver_file:
        return json_error_response('DriverFile with id=%s not found' % driver_file_id, status=404)

    driver_file.s3_upload.delete_from_s3()
    driver_file.delete()

    return upload_json_response(request, True)


def upload_cheque_document_page(request):
    return render(
        request=request,
        template_name='fileupload/upload_cheque.html',
        context={}
    )


def upload_cheque_docs(request):
    token = get_or_none(Token, key=request.POST.get('Authorization'))
    if not isinstance(token, Token):
        return HttpResponseRedirect('/login/')
    try:
        customer_name = request.POST.get('customer_name', None)
        amount = int_or_none(request.POST.get('amount', None))
        cheque_number = request.POST.get('cheque_number', None)
        remarks = request.POST.get('remarks', None)
        cheque_date = request.POST.get('cheque_date', None)

        if not customer_name:
            return json_error_response('customer_name id not provided', status=400)

        if not amount:
            return json_error_response('amount id not provided', status=400)

        if not cheque_date:
            return json_error_response('Cheque Date not provided', status=400)

        if not (cheque_number and len(cheque_number) == 6):
            return json_error_response('cheque_number id not provided', status=400)

        if ChequeFile.objects.filter(cheque_number__iexact=cheque_number,
                                     cheque_date=django_date_format(cheque_date)):
            return json_error_response('Cheque Number is not unique', status=400)

        if not request.FILES:
            return json_error_response('no file to upload', status=400)

        upload_file = request.FILES.get('file')
        cheque_files = create_cheque_file(customer_name=customer_name, amount=amount, cheque_number=cheque_number,
                                          remarks=remarks, upload_file=upload_file, user=token.user,
                                          cheque_date=django_date_format(cheque_date))

        return upload_json_response(request, data={'files': [serialize(cheque_files)]})
    except UnreadablePostError:
        return HttpResponseRedirect('/upload/upload-cheque-document-page/')


def create_cheque_file(customer_name, amount, cheque_number, remarks, upload_file, user, cheque_date):
    orig_filename = upload_file.name
    serial = get_new_serial(ChequeFile, customer_name=customer_name)
    new_filename = 'cheque-%s-%s.%s' % (
        slugify(customer_name), serial, get_ext(orig_filename)
    )
    s3_upload = s3util.save_to_s3_payment_cheque(new_filename, upload_file)
    cheque_file = ChequeFile.objects.create(
        customer_name=customer_name,
        amount=amount,
        cheque_number=cheque_number,
        remarks=remarks,
        serial=serial,
        s3_upload=s3_upload,
        uploaded_by=user,
        cheque_date=cheque_date
    )
    return cheque_file


def create_cheque_entries():
    uploads = S3Upload.objects.filter(folder='uploads/cheque')
    for up in uploads:
        cheque = None if up.filename.startswith('.') else up.filename.split('-')[1]
        if not cheque:
            continue
        if '_' in up.filename:
            serial = up.filename[13:20]
        else:
            serial = ''
        try:
            ChequeFile.objects.create(
                serial=serial,
                s3_upload=up,
            )
        except:
            pass


def cheque_list(request):
    files = [serialize(p) for p in ChequeFile.objects.select_related('customer_name', 's3_upload').all()]
    return upload_json_response(request, data={'files': files})


class ChequeFileListView(ListView):
    model = ChequeFile

    def render_to_response(self, context, **response_kwargs):
        files = [serialize(p) for p in self.get_queryset().order_by('cheque_date')[0:0]]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


def delete_cheque(request, pk):
    cheque_file_id = pk

    if not cheque_file_id:
        return json_error_response('cheque_file_id not provided', status=400)

    cheque_file = get_or_none(ChequeFile, id=cheque_file_id)

    if not cheque_file:
        return json_error_response('ChequeFile with id=%s not found' % cheque_file_id, status=404)

    cheque_file.s3_upload.delete_from_s3()
    cheque_file.delete()

    return upload_json_response(request, True)


def upload_invoice_receipt_page(request):
    return render(
        request=request,
        template_name='fileupload/invoice_receipt.html',
        context={}
    )


def update_invoice_booking_status(invoice_id, mode, user):
    invoice = get_or_none(Invoice, id=invoice_id)
    if invoice:
        i_bookings = invoice.bookings.all()
        for booking in i_bookings:
            if mode == 'party_invoice_sent':
                ManualBooking.objects.filter(id=booking.id).update(invoice_status='invoice_sent')
            if mode == 'invoice_confirmed':
                ManualBooking.objects.filter(id=booking.id).update(invoice_status='invoice_confirmed')
            party_invoice_sent = check_booking_status(booking, mode)
            if not party_invoice_sent:
                create_new_booking_status(booking, mode, user)
            else:
                update_booking_status(booking, mode, 'in_progress', user)


def upload_invoice_receipt_docs(request):
    token = get_or_none(Token, key=request.POST.get('Authorization'))
    if not isinstance(token, Token):
        return HttpResponseRedirect('/login/')
    try:
        invoice = get_or_none(Invoice, invoice_number=request.POST.get('invoice_number', None))
        if not isinstance(invoice, Invoice):
            return json_error_response('invoice_number doesnot  exists', status=400)

        if not request.FILES:
            return json_error_response('no file to upload', status=400)

        invoice_sent_mode = request.POST.get('invoice_sent_mode', None)
        invoice_confirm_mode = request.POST.get('invoice_confirm_mode', None)
        invoice_confirm_by_name = request.POST.get('invoice_confirm_by_name', None)
        invoice_confirm_by_phone = request.POST.get('invoice_confirm_by_phone', None)
        if invoice_sent_mode:
            if invoice_sent_mode not in [x[0] for x in INVOICE_SENT_MODE_CHOICES]:
                return json_error_response('Invalid Invoice Sent Mode', status=400)
        if invoice_confirm_mode:
            if invoice_confirm_mode not in [x[0] for x in INVOICE_CONFIRM_MODE_CHOICES]:
                return json_error_response('Invalid Invoice Confirm Mode', status=400)
            if invoice_confirm_mode == 'PH' and not invoice_confirm_by_name and not invoice_confirm_by_phone:
                return json_error_response('Invoice Confirm Name and Phone required', status=400)
        if not invoice_sent_mode and not invoice_confirm_mode:
            return json_error_response('Invoice Sent or Confirm Mode Required', status=400)

        if 'file' in request.FILES:
            upload_file = request.FILES.get('file')
        else:
            upload_file = None
        invoice_receipt = create_invoice_receipt_file(invoice.invoice_number, upload_file, token.user,
                                                      invoice_sent_mode, invoice_confirm_mode, invoice_confirm_by_name,
                                                      invoice_confirm_by_phone)
        if invoice_sent_mode:
            update_invoice_booking_status(invoice.id, 'party_invoice_sent', token.user)
        if invoice_confirm_mode:
            update_invoice_booking_status(invoice.id, 'invoice_confirmed', token.user)
        return upload_json_response(request, data={'files': [serialize(invoice_receipt)]})
    except UnreadablePostError:
        return HttpResponseRedirect('/upload/upload-cheque-document-page/')


def create_invoice_receipt_file(invoice_number, upload_file, user, invoice_sent_mode, invoice_confirm_mode,
                                invoice_confirm_by_name, invoice_confirm_by_phone):
    serial = get_new_serial(InvoiceReceiptFile, invoice_number=invoice_number)
    if upload_file:
        orig_filename = upload_file.name
        new_filename = 'inv-receipt-%s-%s.%s' % (
            slugify(invoice_number), serial, get_ext(orig_filename)
        )
        s3_upload = s3util.save_to_s3_payment_invoice_receipt(new_filename, upload_file)
    else:
        s3_upload = None
    invoice_receipt_file = InvoiceReceiptFile.objects.create(
        serial=serial,
        invoice_number=invoice_number,
        invoice_receipt=Invoice.objects.filter(invoice_number=invoice_number).last(),
        s3_upload=s3_upload,
        uploaded_by=user,
        invoice_sent_mode=invoice_sent_mode,
        invoice_confirm_mode=invoice_confirm_mode,
        invoice_confirm_by_name=invoice_confirm_by_name,
        invoice_confirm_by_phone=invoice_confirm_by_phone,
    )
    return invoice_receipt_file


def invoice_receipt_list(request):
    files = [serialize(p) for p in InvoiceReceiptFile.objects.all()]
    return upload_json_response(request, data={'files': files})


class InvoiceReceiptListView(ListView):
    model = InvoiceReceiptFile

    def render_to_response(self, context, **response_kwargs):
        files = [serialize(p) for p in self.get_queryset().order_by('created_on')[0:0]]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


def delete_invoice_receipt(request, pk):
    invoice_receipt_id = pk

    if not invoice_receipt_id:
        return json_error_response('cheque_file_id not provided', status=400)

    invoice_receipt = get_or_none(InvoiceReceiptFile, id=invoice_receipt_id)

    if not invoice_receipt:
        return json_error_response('ChequeFile with id=%s not found' % invoice_receipt_id, status=404)

    invoice_receipt.s3_upload.delete_from_s3()
    invoice_receipt.delete()
    return upload_json_response(request, True)
