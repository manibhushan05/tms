from datetime import datetime, timedelta

from django.contrib.auth.models import User

from api.decorators import api_get
from api.helper import json_response
from broker.models import Broker
from fms.decorators import authenticated_user
from fms.views import get_or_none, get_vehicle_current_data
from owner.models import Vehicle
from owner.vehicle_util import compare_format, display_format
from sme.models import Sme
from team.helper.helper import to_int
from team.models import ManualBooking


def booking_status(amount):
    if amount == 0:
        return 'paid'
    else:
        return 'unpaid'


def final_payment_date(booking):
    try:
        if booking.outward_booking.all():
            return booking.outward_booking.all().latest('payment_date').payment_date.strftime('%d-%b-%Y')
        else:
            return ''
    except BaseException:
        pass


def supplier_booking_data(bookings):
    data = []
    for booking in bookings:
        if to_int(booking.total_amount_to_owner - booking.total_out_ward_amount) != 0:
            data.append(
                {
                    'status': 'unpaid',
                    'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number',
                                                                          flat=True)) if booking.lr_numbers.exists() else booking.booking_id,
                    'paid': to_int(booking.total_out_ward_amount),
                    'transaction_id': booking.id,
                    'id': booking.id,
                    'vehicle_number': display_format(booking.lorry_number),
                    'source_city': booking.from_city,
                    'destination_city': booking.to_city,
                    'amount': to_int(booking.total_amount_to_owner),
                    'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                    'balance': to_int(booking.total_amount_to_owner - booking.total_out_ward_amount),
                    'booking_id': booking.booking_id,
                    'pod_status': booking.pod_status,
                    'pod_docs': [
                        {'url': pod.s3_url if pod.s3_url else pod.s3_upload.public_url(),
                         'thumb_url': pod.s3_thumb_url if pod.s3_thumb_url else pod.s3_upload.public_url(),
                         'lr_number': pod.lr_number.lr_number if pod.lr_number else ''} for pod in
                        booking.podfile_set.all()
                    ]
                }
            )
        else:
            data.append(
                {
                    'status': 'paid',
                    'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number',
                                                                          flat=True)) if booking.lr_numbers.exists() else booking.booking_id,
                    'paid': to_int(booking.total_out_ward_amount),
                    'id': booking.id,
                    'transaction_id': booking.id,
                    'booking_id': booking.booking_id,
                    'vehicle_number': display_format(booking.lorry_number),
                    'source_city': booking.from_city,
                    'destination_city': booking.to_city,
                    'amount': to_int(booking.total_amount_to_owner),
                    'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                    'balance': to_int(booking.total_amount_to_owner - booking.total_out_ward_amount),
                    'final_payment_date': final_payment_date(booking=booking),
                    'pod_status': booking.pod_status,
                    'pod_docs': [
                        {'url': pod.s3_url if pod.s3_url else pod.s3_upload.public_url(),
                         'thumb_url': pod.s3_thumb_url if pod.s3_thumb_url else pod.s3_upload.public_url(),
                         'lr_number': pod.lr_number.lr_number if pod.lr_number else ''} for pod in
                        booking.podfile_set.all()
                    ]
                }
            )
    return data


def customer_booking_data(bookings):
    data = []
    for booking in bookings:
        gps_data = get_vehicle_current_data(booking.vehicle.vehicle_number)
        current_location = {}
        if len(gps_data) > 0:
            current_location = gps_data[0]['location']

        # print(booking.vehicle.id)
        if to_int(booking.total_amount_to_owner - booking.total_out_ward_amount) != 0:
            data.append(
                {
                    'status': 'unpaid',
                    'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number',
                                                                          flat=True)) if booking.lr_numbers.exists() else booking.booking_id,
                    'paid': to_int(booking.total_out_ward_amount),
                    'transaction_id': booking.id,
                    'id': booking.vehicle.id,
                    'vehicle_number': display_format(booking.lorry_number),
                    'source_city': booking.from_city,
                    'destination_city': booking.to_city,
                    'amount': to_int(booking.total_amount_to_owner),
                    'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                    'balance': to_int(booking.total_amount_to_owner - booking.total_out_ward_amount),
                    'booking_id': booking.booking_id,
                    'pod_status': booking.pod_status,
                    'pod_docs': [
                        {'url': pod.s3_url if pod.s3_url else pod.s3_upload.public_url(),
                         'thumb_url': pod.s3_thumb_url if pod.s3_thumb_url else pod.s3_upload.public_url(),
                         'lr_number': pod.lr_number.lr_number if pod.lr_number else ''} for pod in
                        booking.podfile_set.all()
                    ],
                    'current_location': current_location
                }
            )
        else:
            data.append(
                {
                    'status': 'paid',
                    'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number',
                                                                          flat=True)) if booking.lr_numbers.exists() else booking.booking_id,
                    'paid': to_int(booking.total_out_ward_amount),
                    'id': booking.vehicle.id,
                    'transaction_id': booking.id,
                    'booking_id': booking.booking_id,
                    'vehicle_number': display_format(booking.lorry_number),
                    'source_city': booking.from_city,
                    'destination_city': booking.to_city,
                    'amount': to_int(booking.total_amount_to_owner),
                    'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                    'balance': to_int(booking.total_amount_to_owner - booking.total_out_ward_amount),
                    'final_payment_date': final_payment_date(booking=booking),
                    'pod_status': booking.pod_status,
                    'pod_docs': [
                        {'url': pod.s3_url if pod.s3_url else pod.s3_upload.public_url(),
                         'thumb_url': pod.s3_thumb_url if pod.s3_thumb_url else pod.s3_upload.public_url(),
                         'lr_number': pod.lr_number.lr_number if pod.lr_number else ''} for pod in
                        booking.podfile_set.all()
                    ],
                    'current_location': current_location
                }
            )
    return data


@api_get
@authenticated_user
def team_booking_data(request, vehicle_id):
    print(request.data)
    if to_int(vehicle_id) != 9999999 and isinstance(get_or_none(Vehicle, id=vehicle_id), Vehicle):
        vehicle = get_or_none(Vehicle, id=vehicle_id)
        bookings = ManualBooking.objects.filter(
            lorry_number__in=[display_format(compare_format(vehicle.vehicle_number))]).exclude(
            booking_status__icontains='cancelled').order_by('-shipment_date')
    else:
        broker = Broker.objects.get(name=User.objects.get(username=request.user.username))
        bookings = ManualBooking.objects.filter(supplier=broker,
                                                shipment_date__gte=datetime(2017, 12, 1).date()).exclude(
            booking_status__icontains='cancelled').order_by('-shipment_date')
    return json_response({'status': 'success', 'data': supplier_booking_data(bookings=bookings)})


@api_get
@authenticated_user
def team_customer_booking_data(request):
    print(request.data)
    customer = Sme.objects.get(name=request.user)
    # broker = Broker.objects.get(name=User.objects.get(username=request.user.username))
    bookings = ManualBooking.objects.filter(company=customer,
                                            shipment_date__gte=datetime(2017, 12, 1).date()).exclude(
        booking_status__icontains='cancelled').order_by('-shipment_date')
    return json_response({'status': 'success', 'data': supplier_booking_data(bookings=bookings)})

@api_get
@authenticated_user
def trip_details(request, booking_id):
    booking = ManualBooking.objects.get(id=booking_id)
    data = {}
    data.update({'status': 'success'})
    data.update(
        {
            'basic_details': {
                'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                'source_city': booking.from_city,
                'destination_city': booking.to_city,
                'shipment_date': None if not booking.shipment_date else booking.shipment_date.strftime('%d-%b-%Y'),
                'vehicle_number': booking.lorry_number,
                'weight': float(booking.supplier_charged_weight),
                'rate': float(booking.supplier_rate),
                'bill_number': 'OPB-{}'.format(
                    ''.join(booking.outward_payment_bill.values_list('bill_number', flat=True))),
                'pod_docs': [
                    {'url': pod.s3_url, 'thumb_url': pod.s3_thumb_url} for pod in booking.podfile_set.all()
                ]
            }
        }
    )
    data.update(
        {
            'rates': {
                'weight': float(booking.supplier_charged_weight),
                'rate': float(booking.supplier_rate),
                'freight': int(float(booking.supplier_charged_weight) * float(booking.supplier_rate)),
                'loading': booking.loading_charge,
                'unloading': booking.unloading_charge,
                'detention': booking.detention_charge,
                'additional': booking.additional_charges_for_company,
                'commission': booking.commission,
                'lr_charge': booking.lr_cost,
                'deduction_for_advance': booking.deduction_for_advance,
                'deduction_for_balance': booking.deduction_for_balance,
                'other_deduction': booking.other_deduction,
                'total_amount_to_owner': int(booking.total_amount_to_owner),
                'total_out_ward_amount': int(booking.total_out_ward_amount),
            }
        }
    )
    data.update(
        {
            'payments': [
                {
                    'amount': float(payment.actual_amount),
                    'paid_to': payment.paid_to,
                    'remarks': payment.remarks,
                    'payment_mode': payment.get_payment_mode_display(),
                    'account_number': None if not payment.bank_account else payment.bank_account.account_number,
                    'fuel_card': None if not payment.fuel_card else payment.fuel_card.card_number,
                    'date': None if not payment.payment_date else payment.payment_date.strftime('%d-%b-%Y')
                } for payment in booking.outward_booking.all().exclude(is_refund_amount=True)
            ]
        }
    )
    return json_response(data=data)


@api_get
@authenticated_user
def customer_trip_details(request, booking_id):
    booking = ManualBooking.objects.get(id=booking_id)
    data = {}
    data.update({'status': 'success'})
    data.update(
        {
            'basic_details': {
                'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                'source_city': booking.from_city,
                'destination_city': booking.to_city,
                'shipment_date': None if not booking.shipment_date else booking.shipment_date.strftime('%d-%b-%Y'),
                'vehicle_number': booking.lorry_number,
                'weight': float(booking.charged_weight),
                'rate': float(booking.party_rate),
                'bill_number': 'OPB-{}'.format(
                    ''.join(booking.outward_payment_bill.values_list('bill_number', flat=True))),
                'pod_docs': [
                    {'url': pod.s3_url, 'thumb_url': pod.s3_thumb_url} for pod in booking.podfile_set.all()
                ]
            }
        }
    )
    data.update(
        {
            'rates': {
                'weight': float(booking.charged_weight),
                'rate': float(booking.party_rate),
                'freight': int(float(booking.charged_weight) * float(booking.party_rate)),
                'loading': booking.loading_charge,
                'unloading': booking.unloading_charge,
                'detention': booking.detention_charge,
                'additional': booking.additional_charges_for_company,
                'company_remarks': booking.invoice_remarks_for_additional_charges,
                'commission': booking.commission,
                'lr_charge': booking.lr_cost,
                'deductions_for_company': booking.deductions_for_company,
                'deduction_remarks_company': booking.invoice_remarks_for_deduction_discount,
                'deduction_for_advance': booking.deduction_for_advance,
                'deduction_for_balance': booking.deduction_for_balance,
                'other_deduction': booking.other_deduction,
                'total_amount_to_company': int(booking.total_amount_to_company),
                'total_out_ward_amount': int(booking.total_out_ward_amount),
            }
        }
    )
    data.update(
        {
            'payments': [
                {
                    'amount': float(payment.actual_amount),
                    'paid_to': payment.paid_to,
                    'remarks': payment.remarks,
                    'payment_mode': payment.get_payment_mode_display(),
                    'account_number': None if not payment.bank_account else payment.bank_account.account_number,
                    'fuel_card': None if not payment.fuel_card else payment.fuel_card.card_number,
                    'date': None if not payment.payment_date else payment.payment_date.strftime('%d-%b-%Y')
                } for payment in booking.outward_booking.all().exclude(is_refund_amount=True)
            ]
        }
    )
    return json_response(data=data)
