from api.helper import json_error_response, json_success_response
from api.utils import get_or_none, int_or_none
from report.outward_payments_receipt import generate_receipt
from team.decorators import only_post, authenticated_user
from .models import ManualBooking
from .models import OutWardPayment


@only_post
@authenticated_user
def outward_payments_bill(request):
    booking_id = request.POST.get('booking_id', None)
    if not booking_id:
        return json_error_response('booking_id not provided', status=400)

    manual_booking = get_or_none(ManualBooking, id=booking_id)
    if not manual_booking:
        return json_error_response('ManualBooking with booking_id=%s does not exist' % booking_id, status=404)

    payment_ids = request.POST.getlist('bill_nums', None) or []
    ids = [] if not payment_ids else payment_ids[0].split(',')
    ids = [int_or_none(i) for i in ids]
    ids = [i for i in ids if i is not None]

    if not ids:
        return json_error_response('no bill numbers provided', status=400)

    outward_payments = list(OutWardPayment.objects.filter(id__in=ids).exclude(is_refund_amount=True))
    all_exist = not all([not value.outward_payment_bill.exists() for value in outward_payments])

    if all_exist:
        return json_error_response('bill already exists', status=400)

    bill_number, s3_upload = generate_receipt(booking=manual_booking,
                                              payments_id=OutWardPayment.objects.filter(id__in=ids).exclude(
                                                  is_refund_amount=True).values_list('id', flat=True),created_by=request.user)
    return json_success_response('bill generated', bill_number=bill_number, url=s3_upload.public_url())
