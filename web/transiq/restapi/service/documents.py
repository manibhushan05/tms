from datetime import datetime

from api import s3util
from api.utils import get_ext, random_id
from fileupload.models import PODFile
from team.models import ManualBooking, LrNumber

MIMEANY = '*/*'
MIMEJSON = 'application/json'
MIMETEXT = 'text/plain'


def response_mimetype(request):
    """response_mimetype -- Return a proper response mimetype, accordingly to
    what the client accepts, as available in the `HTTP_ACCEPT` header.

    request -- a HttpRequest instance.

    """
    can_json = MIMEJSON in request.META['HTTP_ACCEPT']
    can_json |= MIMEANY in request.META['HTTP_ACCEPT']
    return MIMEJSON if can_json else MIMETEXT


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
        new_filename = 'POD-%s-%s.%s' % (booking.booking_id, serial, get_ext(orig_filename))
        mb = ManualBooking.objects.get(booking_id=booking.booking_id)
        mb.pod_status = 'unverified'
        mb.pod_date = datetime.now()
        mb.save()
    elif isinstance(lr_number, LrNumber):
        serial = get_new_serial(PODFile, lr_number=lr_number)
        new_filename = 'POD-%s-%s.%s' % (lr_number.lr_number, serial, get_ext(orig_filename))
        mb = ManualBooking.objects.get(booking_id=lr_number.booking.booking_id)
        mb.pod_status = 'unverified'
        mb.pod_date = datetime.now()
        mb.save()
    else:
        serial = random_id(num_digits=8)
        new_filename = 'POD-%s-%s.%s' % (serial, serial, get_ext(orig_filename))

    s3_upload = s3util.save_to_s3_uploads_pod(new_filename, upload_file)
    pod_file = PODFile.objects.create(
        lr_number=lr_number if isinstance(lr_number, LrNumber) else None,
        serial=serial,
        s3_upload=s3_upload,
        uploaded_by=user,
        booking=booking if isinstance(booking, ManualBooking) else None
    )
    return pod_file
