import json
from datetime import datetime

from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.html import format_html

from api.helper import json_error_response, json_success_response, EMP_GROUP1
from api.models import S3Upload
from api.utils import get_or_none, int_or_none
from fileupload.models import PODFile
from team.decorators import authenticated_user
from team.helper.helper import to_int, django_date_format, to_float
from team.models import ManualBooking, RejectedPOD


@authenticated_user
def unverified_documents_data(request):
    start = to_int(request.GET.get('start'))
    end = start + to_int(request.GET.get('length'))
    s3_uploads = S3Upload.objects.filter(Q(verified=False) & (
            Q(filename__iendswith='.jpg') | Q(filename__iendswith='.jpeg') | Q(filename__iendswith='.png'))).order_by(
        '-uploaded_on')
    data = []
    for s3 in s3_uploads[start:end]:
        data.append([
            s3.uploaded_on.strftime('%d-%b-%Y') if s3.uploaded_on else '',
            s3.folder,
            s3.filename,
            format_html('''<a href="{}"><i class="fa fa-image" style="font-size: 24px"  aria-hidden="true"></i></a>''',
                        s3.public_url()),
            format_html(
                '''<form action="/team/verify-documents/" method="GET">   
                        <input type="hidden" name="s3_upload_id" value="{}">
                        <button type="submit" class="btn btn-success" name="accept_choice" value="accept"><i style="font-size: 24px" 
                        class="fa fa-check-circle"></i></button> 
                        <button type="submit" class="btn btn-danger" name="accept_choice" value="reject"><i
                        style="font-size: 24px" class="fa fa-times-circle"></i></button>
                    </form>''', s3.id
            )
        ])
    data = {
        "draw": to_int(request.GET.get('draw')),
        "recordsTotal": s3_uploads.count(),
        "recordsFiltered": s3_uploads.count(),
        "data": data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')



@authenticated_user
def verify_documents(request):
    accept_choice = request.GET.get('accept_choice')
    s3_upload = get_or_none(S3Upload, id=int_or_none(request.GET.get('s3_upload_id')))
    if accept_choice == 'accept' and isinstance(s3_upload, S3Upload):
        S3Upload.objects.filter(id=int_or_none(request.GET.get('s3_upload_id'))).update(verified=True, is_valid=True)
    elif accept_choice == 'reject' and isinstance(s3_upload, S3Upload):
        S3Upload.objects.filter(id=int_or_none(request.GET.get('s3_upload_id'))).update(verified=True, is_valid=False)
    else:
        pass
    return HttpResponseRedirect('/team/unverified-documents/')


@authenticated_user
def unverified_pod_page(request):
    data = []
    for booking in ManualBooking.objects.filter(
            Q(pod_status__iexact='unverified')).exclude(
        Q(booking_status='cancelled') | Q(deleted=True)).order_by('id'):
        if any([lr.pod_files.filter(verified=False, is_valid=False).exists() for lr in
                booking.lr_numbers.all()]) and booking.podfile_set.exists():
            booking_data = {
                'id': booking.id,
                'booking_id': booking.booking_id,
                'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                'supplier_name': booking.truck_broker_owner_name,
                'supplier_phone': booking.truck_broker_owner_phone,
                'from_city': booking.from_city,
                'to_city': booking.to_city,
                'vehicle_number': booking.supplier_vehicle.number() if booking.supplier_vehicle else '-',
                'party_weight': booking.charged_weight,
                'supplier_weight': booking.supplier_charged_weight,
                'loaded_weight': booking.loaded_weight,
                'delivered_weight': booking.delivered_weight,
                'form_verify_pod': '{}_{}'.format('form_verify_pod', booking.booking_id),
                'btn_accept_choice': '{}_{}'.format('btn_accept_choice', booking.booking_id),
                'btn_accept_id': '{}_{}'.format('btn_accept_id', booking.booking_id),
                'btn_reject_id': '{}_{}'.format('btn_reject_id', booking.booking_id),
                'input_party_weight': '{}_{}'.format('input_party_weight', booking.booking_id),
                'input_supplier_weight': '{}_{}'.format('input_supplier_weight', booking.booking_id),
                'input_loaded_weight': '{}_{}'.format('input_loaded_weight', booking.booking_id),
                'input_delivered_weight': '{}_{}'.format('input_delivered_weight', booking.booking_id),
                'input_delivered_date': '{}_{}'.format('input_delivered_date', booking.booking_id),
                'input_rejection_remarks': '{}_{}'.format('input_rejection_remarks', booking.booking_id),
                'div_rejection_remarks': '{}_{}'.format('div_rejection_remarks', booking.booking_id),
                'div_rejection_line': '{}_{}'.format('div_rejection_line', booking.booking_id),
                'btn_resubmit_id': '{}_btn_resubmit'.format(booking.booking_id),
                'form_resubmit_pod': '{}_form_resubmit'.format(booking.booking_id)
            }
            pod_data = []
            if booking.lr_numbers.exists() and any(
                    [lr.pod_files.filter(verified=False, is_valid=False).exists() for lr in booking.lr_numbers.all()]):
                for lr in booking.lr_numbers.all():
                    pod_data.append({
                        'lr_number': lr.lr_number,
                        'uploaded_by': lr.pod_files.last().uploaded_by.profile.name if lr.pod_files.last() else '',
                        'uploaded_on': lr.pod_files.last().created_on.strftime(
                            '%d-%b-%Y') if lr.pod_files.last() else '',
                        'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                  'url': doc.s3_upload.public_url()} for doc in lr.pod_files.filter(verified=False)],
                        'gallery': '{}_gallery'.format(lr.lr_number)

                    })

            elif booking.podfile_set.filter(verified=False,
                                            is_valid=False).exists() and not booking.lr_numbers.exists():
                pod_data.append({
                    'lr_number': '-',
                    'uploaded_by': booking.podfile_set.last().uploaded_by.profile.name if booking.podfile_set.last() else '',
                    'uploaded_on': booking.podfile_set.last().created_on.strftime(
                        '%d-%b-%Y') if booking.podfile_set.last() else '',
                    'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                              'url': doc.s3_upload.public_url()} for doc in booking.podfile_set.filter(verified=False)],
                    'gallery': '{}_gallery'.format(booking.booking_id)

                })
            else:
                pass
            booking_data['pod_data'] = pod_data
            data.append(booking_data)
    return render(request=request, template_name='team/documents/verify_pod.html', context={'bookings_data': data})


@authenticated_user
def update_booking_pod_data(request):
    approve_type = request.POST.get('accept_choice')
    if approve_type == 'accept':
        booking = ManualBooking.objects.get(id=request.POST.get('booking_id'))
        booking.supplier_charged_weight = to_float(request.POST.get('supplier_weight'))
        booking.charged_weight = to_float(request.POST.get('party_weight'))
        booking.loaded_weight = to_float(request.POST.get('loaded_weight'))
        booking.delivered_weight = to_float(request.POST.get('delivered_weight'))
        booking.pod_date = datetime.now()
        booking.delivery_datetime = django_date_format(request.POST.get('delivery_datetime'))
        for pod in PODFile.objects.filter(booking=booking).exclude(verified=True):
            pod.is_valid = True
            pod.verified = True
            pod.verified_by = request.user
            pod.verified_datetime = datetime.now()
            pod.save()
            S3Upload.objects.filter(id=pod.s3_upload_id).update(is_valid=True, verified=True)
        # if verify_pod(booking=booking):
        booking.pod_status = 'completed'
        booking.save()
        return json_success_response(msg='POD for booking ID {} is Accepted'.format(booking.booking_id))
    elif approve_type == 'reject':
        booking = ManualBooking.objects.get(id=request.POST.get('booking_id'))
        booking.pod_status = 'rejected'
        booking.save()
        for lr in booking.lr_numbers.all():
            RejectedPOD.objects.create(booking=booking, lr=lr, remarks=request.POST.get('rejection_remark'),
                                       rejected_by=request.user)
        if not booking.lr_numbers.exists():
            RejectedPOD.objects.create(booking=booking, remarks=request.POST.get('rejection_remark'),
                                       rejected_by=request.user)
        for pod in PODFile.objects.filter(booking=booking).exclude(verified=True):
            pod.is_valid = False
            pod.verified = True
            pod.verified_by = request.user
            pod.verified_datetime = datetime.now()
            pod.save()
            S3Upload.objects.filter(id=pod.s3_upload_id).update(is_valid=False, verified=True)
        return json_success_response(msg='POD for booking ID {} is rejected'.format(booking.booking_id))
    return json_error_response(msg='fail', status=404)


@authenticated_user
def my_pod_uploaded_documents_page(request):
    data = []
    for booking in ManualBooking.objects.filter(
            Q(pod_status__iexact='unverified') | Q(pod_status__iexact='rejected')).exclude(
        Q(booking_status='cancelled') | Q(deleted=True)).order_by('id'):
        if any([lr.pod_files.exists() for lr in booking.lr_numbers.all()]) and booking.podfile_set.exists():
            booking_data = {
                'id': booking.id,
                'booking_id': booking.booking_id,
                'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                'supplier_name': booking.truck_broker_owner_name,
                'supplier_phone': booking.truck_broker_owner_phone,
                'from_city': booking.from_city,
                'to_city': booking.to_city,
                'vehicle_number': booking.lorry_number,
                'party_weight': booking.charged_weight,
                'supplier_weight': booking.supplier_charged_weight,
                'loaded_weight': booking.loaded_weight,
                'delivered_weight': booking.delivered_weight,
                'pod_status': booking.get_pod_status_display(),
                'form_resubmit_pod': 'form_resubmit_pod_{}'.format(booking.booking_id),
                'input_resubmission_remarks': 'input_resubmission_remarks_{}'.format(booking.booking_id),
                'btn_resubmit_id': 'btn_resubmit_id_{}'.format(booking.booking_id),
                'div_resubmit_remarks': 'div_resubmit_remarks_{}'.format(booking.booking_id),
            }
            pod_data = []
            if EMP_GROUP1 in request.user.groups.values_list('name', flat=True):
                if booking.lr_numbers.exists() and any(
                        [lr.pod_files.exists() for lr in
                         booking.lr_numbers.all()]):
                    for lr in booking.lr_numbers.all():
                        pod_data.append({
                            'lr_number': lr.lr_number,
                            'uploaded_by': lr.pod_files.last().uploaded_by.profile.name if lr.pod_files.last() else '',
                            'uploaded_on': lr.pod_files.last().created_on.strftime(
                                '%d-%b-%Y') if lr.pod_files.last() else '',
                            'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                      'url': doc.s3_upload.public_url(), 'id': doc.id} for doc in lr.pod_files.all()],
                            'gallery': '{}_gallery'.format(lr.lr_number)
                        })
                elif booking.podfile_set.exists() and not booking.lr_numbers.exists():
                    pod_data.append({
                        'lr_number': '-',
                        'uploaded_by': booking.podfile_set.last().uploaded_by.profile.name if booking.podfile_set.last() else '',
                        'uploaded_on': booking.podfile_set.last().created_on.strftime(
                            '%d-%b-%Y') if booking.podfile_set.last() else '',
                        'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                  'url': doc.s3_upload.public_url(), 'id': doc.id} for doc in
                                 booking.podfile_set.all()],
                        'gallery': '{}_gallery'.format(booking.booking_id)
                    })
                else:
                    pass
                booking_data['rejected'] = [{'rejected_by': reject.rejected_by,
                                             'rejection_datetime': reject.created_on.strftime('%d-%b-%Y %I:%M %p'),
                                             'remarks': reject.remarks} for reject in
                                            booking.rejectedpod_set.all()]
            else:
                if booking.lr_numbers.exists() and any(
                        [lr.pod_files.filter(uploaded_by=request.user).exists()
                         for lr in booking.lr_numbers.all()]):
                    for lr in booking.lr_numbers.all():
                        pod_data.append({
                            'lr_number': lr.lr_number,
                            'uploaded_by': lr.pod_files.last().uploaded_by.profile.name if lr.pod_files.last() else '',
                            'uploaded_on': lr.pod_files.last().created_on.strftime(
                                '%d-%b-%Y') if lr.pod_files.last() else '',
                            'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                      'url': doc.s3_upload.public_url(), 'id': doc.id} for doc in
                                     lr.pod_files.all()],
                        })

                elif booking.podfile_set.filter(uploaded_by=request.user).exists() and not booking.lr_numbers.exists():
                    pod_data.append({
                        'lr_number': '-',
                        'uploaded_by': booking.podfile_set.last().uploaded_by.profile.name if booking.podfile_set.last() else '',
                        'uploaded_on': booking.podfile_set.last().created_on.strftime(
                            '%d-%b-%Y') if booking.podfile_set.last() else '',
                        'docs': [{'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                  'url': doc.s3_upload.public_url(), 'id': doc.id} for doc in
                                 booking.podfile_set.all()],
                    })
                else:
                    pass
                booking_data['rejected'] = [{'rejected_by': reject.rejected_by,
                                             'rejection_datetime': reject.created_on.strftime('%d-%b-%Y %I:%M %p'),
                                             'remarks': reject.remarks} for reject in
                                            booking.rejectedpod_set.all()]
            booking_data['pod_data'] = pod_data
            if pod_data:
                data.append(booking_data)
    return render(request=request, template_name='team/documents/uploaded-pod.html',
                  context={'bookings_data': data})


def resubmit_rejected_pod(request):
    resubmission_remark = request.POST.get('resubmission_remark')
    booking_id = request.POST.get('booking_id')
    resubmitted_pod = request.POST.getlist('resubmitted_pod')
    if not resubmission_remark:
        return json_error_response(msg="Remarks is mandatory", status=400)
    if not booking_id:
        return json_error_response(msg="Booking id is required", status=400)
    booking = get_or_none(ManualBooking, booking_id=booking_id)
    if not isinstance(booking, ManualBooking):
        return json_error_response(msg="BAD request", status=400)
    if not PODFile.objects.filter(booking=booking).exists():
        return json_error_response("BAD Request", status=400)
    PODFile.objects.filter(id__in=resubmitted_pod).update(verified=False, is_valid=False)
    PODFile.objects.filter(booking=booking).exclude(id__in=resubmitted_pod).update(verified=True, is_valid=False)
    booking.pod_status = 'unverified'
    booking.save()
    return json_success_response(msg="success")


def pod_delivered_date_validation(request):
    return json_success_response(msg="Valid")
