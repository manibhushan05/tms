from datetime import datetime, timedelta
from pandas import json

from api.decorators import api_post, api_get
from api.helper import json_response, json_error_response
from api.utils import int_or_none

from broker.models import BrokerVehicle, Broker
from fms.decorators import authenticated_user
from fms.views import get_or_none
from owner.models import Vehicle
from supplier.helper import compare_format
from team.models import ManualBooking
from team.helper.helper import to_int
from transaction.models import VehicleAllocated, Transaction
from django.contrib.auth.models import User
import pandas as pd
from owner.vehicle_util import display_format


@api_post
@authenticated_user
def booking_history_data(request):
    broker = Broker.objects.get(name=User.objects.get(username=request.user.username))
    broker_vehicle_ids = BrokerVehicle.objects.filter(broker=broker).values_list('vehicle_id', flat=True)
    allocated_vehicles_data = VehicleAllocated.objects.filter(vehicle_number_id__in=broker_vehicle_ids).values(
        'transaction_id', 'total_out_ward_amount', 'total_amount_to_owner', 'transaction__shipment_datetime', 'id',
        'source_city', 'destination_city', 'transaction_id', 'material', 'transaction__total_vehicle_requested',
        'transaction__transaction_status', 'transaction__transaction_id', 'vehicle_number__vehicle_number', 'lr_number')
    transaction_data = [{'id': v['id'],
                         'transaction_id': v['transaction__transaction_id'],
                         'status': v['transaction__transaction_status'],
                         'source_city': v['source_city'],
                         'destination_city': v['destination_city'],
                         'paid': str(int(v['total_out_ward_amount'])),
                         'amount': str(int(v['total_amount_to_owner'])),
                         'balance': str(int(v['total_amount_to_owner'] - v['total_out_ward_amount'])),
                         'total_vehicle_requested': v['transaction__total_vehicle_requested'],
                         'vehicle_number': display_format(v['vehicle_number__vehicle_number']),
                         'lr_number': v['lr_number'],
                         'shipment_date': v['transaction__shipment_datetime'].strftime('%d-%b-%Y')} for v in
                        allocated_vehicles_data]
    return json_response({'status': 'success', 'data': transaction_data})


@api_post
@authenticated_user
def vehicle_trip_data(request):
    data = request.data
    vehicle_id = int_or_none(data.get('vehicleId', None))
    if vehicle_id:
        vehicle = get_or_none(Vehicle, id=vehicle_id)
        if not vehicle:
            return json_error_response('Vehicle with id=%s does not exist' % vehicle_id, 404)
        else:
            broker_vehicle_ids = BrokerVehicle.objects.filter(vehicle=vehicle).values_list(
                'vehicle_id',
                flat=True)
            allocated_vehicles_data = VehicleAllocated.objects.filter(vehicle_number_id__in=broker_vehicle_ids).values(
                'transaction_id', 'total_out_ward_amount', 'total_amount_to_owner', 'transaction__shipment_datetime',
                'source_city', 'destination_city', 'transaction_id', 'material', 'transaction__total_vehicle_requested',
                'transaction__transaction_status', 'transaction__transaction_id', 'vehicle_number__vehicle_number',
                'lr_number')
            transaction_data = [{'id': v['transaction_id'],
                                 'transaction_id': v['transaction__transaction_id'],
                                 'status': v['transaction__transaction_status'],
                                 'source_city': v['source_city'],
                                 'destination_city': v['destination_city'],
                                 'paid': str(int(v['total_out_ward_amount'])),
                                 'amount': str(int(v['total_amount_to_owner'])),
                                 'balance': str(int(v['total_amount_to_owner'] - v['total_out_ward_amount'])),
                                 'total_vehicle_requested': v['transaction__total_vehicle_requested'],
                                 'vehicle_number': display_format(v['vehicle_number__vehicle_number']),
                                 'lr_number': v['lr_number'],
                                 'shipment_date': v['transaction__shipment_datetime'].strftime('%d-%b-%Y')} for v in
                                allocated_vehicles_data]
            return json_response({'status': 'success', 'data': transaction_data})
    else:
        vehicle = Vehicle()


@api_post
@authenticated_user
def mb_vehicle_trip_data(request):
    data = request.data
    vehicle_id = int_or_none(data.get('vehicleId', None))
    if vehicle_id:
        vehicle = int_or_none(get_or_none(Vehicle, id=vehicle_id))
        if not vehicle:
            return json_error_response('Vehicle with id=%s does not exist' % vehicle_id, 404)
        else:
            data = []
            for booking in ManualBooking.objects.filter(
                    lorry_number__in=[display_format(compare_format(vehicle.vehicle_number))]).order_by(
                '-shipment_date'):
                if to_int(booking.total_amount_to_owner - booking.total_out_ward_amount) != 0:
                    data.append(
                        {
                            'status': 'unpaid',
                            'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                            'paid': to_int(booking.total_out_ward_amount),
                            'id': booking.id,
                            'total_vehicle_requested': None,
                            'vehicle_number': display_format(booking.lorry_number),
                            'source_city': booking.from_city,
                            'destination_city': booking.to_city,
                            'amount': to_int(booking.total_amount_to_owner),
                            'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                            'balance': to_int(booking.total_amount_to_owner - booking.total_out_ward_amount),
                            'transaction_id': booking.booking_id
                        }
                    )
                else:
                    data.append(
                        {
                            'status': 'paid',
                            'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                            'paid': to_int(booking.total_out_ward_amount),
                            'id': booking.id,
                            'total_vehicle_requested': None,
                            'vehicle_number': display_format(booking.lorry_number),
                            'source_city': booking.from_city,
                            'destination_city': booking.to_city,
                            'amount': to_int(booking.total_amount_to_owner),
                            'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                            'balance': to_int(booking.total_amount_to_owner - booking.total_out_ward_amount),
                            'final_payment_date': final_payment_date(booking=booking),
                            'transaction_id': booking.booking_id
                        }
                    )
            return json_response({'status': 'success', 'data': data})


def get_allocated_vehicle(request):
    data = json.loads(request.body)
    transaction = Transaction.objects.get(transaction_id=data['transaction_id'])
    allocated_vehicle_list = []
    for value in transaction.allocated_vehicle.all():
        temp = []
        temp.append(value.vehicle_number.vehicle_type.vehicle_type + ", " + value.vehicle_number.vehicle_type.capacity)
        temp.append(value.vehicle_number.vehicle_number)
        temp.append(value.vehicle_number.driver.driving_licence_number)
        temp.append(value.vehicle_number.driver.name)
        temp.append(value.vehicle_number.driver.phone)
        allocated_vehicle_list.append(temp)
    df_allocated = pd.DataFrame(allocated_vehicle_list,
                                columns=['vehicle_type', 'vehicle_number', 'driving_licence', 'driver_name',
                                         'driver_phone'])
    data_allocated = df_allocated.reset_index().to_json(orient='records')
    data_allocated = json.loads(data_allocated)
    return data_allocated


def loading_unloading_points(request):
    data = json.loads(request.body)
    transaction = Transaction.objects.get(transaction_id=data['transaction_id'])
    locations = transaction.loading_unloading_location.all()
    loading_list = []
    unloading_list = []
    for value in locations:
        temp1 = []
        temp2 = []
        if value.type == 'loading':
            temp1.append(value.address)
            temp1.append(value.city.name)
            loading_list.append(temp1)
        elif value.type == 'unloading':
            temp2.append(value.address)
            temp2.append(value.city.name)
            unloading_list.append(temp2)
    df_loading = pd.DataFrame(loading_list, columns=['address', 'city'])
    loading_details = df_loading.reset_index().to_json(orient='records')
    loading_json = json.loads(loading_details)
    df_unloading = pd.DataFrame(unloading_list, columns=['address', 'city'])
    unloading_details = df_unloading.reset_index().to_json(orient='records')
    unloading_json = json.loads(unloading_details)

    return {"loading": loading_json, "unloading": unloading_json, "material": transaction.material}


def format_date_obj(date_obj):
    if date_obj is None:
        return ''
    else:
        date_obj.strftime('%d %b %Y')


def get_vehicle_data(trans_id):
    allocated_vehicle = VehicleAllocated.objects.get(id=trans_id)
    if allocated_vehicle.vehicle_number is None:
        data = {'vehicle_type': '', 'vehicle_number': '', 'dl_number': '', 'dl_validity': '', 'driver_name': '',
                'driver_phone': ''}
    else:
        data = {}
        data['vehicle_type'] = allocated_vehicle.vehicle_number.vehicle_type.vehicle_type
        data['vehicle_number'] = display_format(allocated_vehicle.vehicle_number.vehicle_number)
        if allocated_vehicle.vehicle_number.driver is not None:
            data['dl_number'] = allocated_vehicle.vehicle_number.driver.driving_licence_number
            data['dl_validity'] = datetime.strptime(
                str(allocated_vehicle.vehicle_number.driver.driving_licence_validity), '%Y-%m-%d').strftime('%d %b %Y')
            data['driver_name'] = allocated_vehicle.vehicle_number.driver.name
            data['driver_phone'] = allocated_vehicle.vehicle_number.driver.phone
        else:
            data['dl_number'] = ''
            data['dl_validity'] = ''
            data['driver_name'] = ''
            data['driver_phone'] = ''
    return data


def get_basic_transaction_data(trans_id):
    allocated_vehicles_data = VehicleAllocated.objects.filter(id=trans_id).values(
        'transaction_id', 'total_out_ward_amount', 'total_amount_to_owner', 'transaction__shipment_datetime', 'id',
        'source_city', 'destination_city', 'transaction_id', 'material', 'transaction__total_vehicle_requested',
        'transaction__transaction_status', 'transaction__transaction_id', 'vehicle_number__vehicle_number', 'lr_number')
    transaction_data = [{'id': v['id'],
                         'transaction_id': v['transaction__transaction_id'],
                         'status': v['transaction__transaction_status'],
                         'source_city': v['source_city'],
                         'destination_city': v['destination_city'],
                         'paid': str(int(v['total_out_ward_amount'])),
                         'amount': str(int(v['total_amount_to_owner'])),
                         'balance': str(int(v['total_amount_to_owner'] - v['total_out_ward_amount'])),
                         'total_vehicle_requested': v['transaction__total_vehicle_requested'],
                         'vehicle_number': display_format(v['vehicle_number__vehicle_number']),
                         'lr_number': v['lr_number'],
                         'shipment_date': v['transaction__shipment_datetime'].strftime('%d-%b-%Y')} for v in
                        allocated_vehicles_data]
    return transaction_data


def get_payment_data(trans_id):
    allocated_vehicle = VehicleAllocated.objects.get(id=trans_id)
    payment = allocated_vehicle.outward_payment_allocated_vehicle.values('id', 'payment_id', 'amount', 'payment_mode',
                                                                         'datetime', 'remarks', 'paid_to')
    payment_data = [{'id': value['id'],
                     'amount': value['amount'],
                     'payment_id': value['payment_id'],
                     'payment_mode': value['payment_mode'],
                     'remarks': value['remarks'],
                     'paid_to': value['paid_to'],
                     'datetime': value['datetime'].strftime('%d %b %Y'),
                     } for value in payment]
    return payment_data


@api_post
@authenticated_user
def complete_trip_details(request):
    data = request.data
    return json_response({'basic_details': get_basic_transaction_data(data.get("trans_id")),
                          'vehicle_info': get_vehicle_data(data.get('trans_id')),
                          'payment_info': get_payment_data(data.get('trans_id'))})


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


@api_get
@authenticated_user
def team_booking_data(request):
    broker = Broker.objects.get(name=User.objects.get(username=request.user.username))
    broker_vehicle = BrokerVehicle.objects.filter(broker=broker).values_list('vehicle__vehicle_number', flat=True)
    vehicles = [display_format(vehicle) for vehicle in broker_vehicle]
    data = []
    for booking in ManualBooking.objects.filter(lorry_number__in=vehicles,
                                                shipment_date__gte=datetime.now().date() - timedelta(days=90)).exclude(
        booking_status__icontains='cancelled').order_by('-shipment_date'):
        if to_int(booking.total_amount_to_owner - booking.total_out_ward_amount) != 0:
            data.append(
                {
                    'status': 'unpaid',
                    'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                    'paid': to_int(booking.total_out_ward_amount),
                    'id': booking.id,
                    'total_vehicle_requested': None,
                    'vehicle_number': display_format(booking.lorry_number),
                    'source_city': booking.from_city,
                    'destination_city': booking.to_city,
                    'amount': to_int(booking.total_amount_to_owner),
                    'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                    'balance': to_int(booking.total_amount_to_owner - booking.total_out_ward_amount),
                    'transaction_id': booking.booking_id,
                    'pod_status': booking.pod_status
                }
            )
        else:
            data.append(
                {
                    'status': 'paid',
                    'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                    'paid': to_int(booking.total_out_ward_amount),
                    'id': booking.id,
                    'total_vehicle_requested': None,
                    'vehicle_number': display_format(booking.lorry_number),
                    'source_city': booking.from_city,
                    'destination_city': booking.to_city,
                    'amount': to_int(booking.total_amount_to_owner),
                    'shipment_date': booking.shipment_date.strftime('%d-%b-%Y'),
                    'balance': to_int(booking.total_amount_to_owner - booking.total_out_ward_amount),
                    'final_payment_date': final_payment_date(booking=booking),
                    'transaction_id': booking.booking_id,
                    'pod_status': booking.pod_status
                }
            )
    return json_response({'status': 'success', 'data': data})


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
                    ''.join(booking.outward_payment_bill.values_list('bill_number', flat=True)))
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
                } for payment in booking.outward_booking.all()
            ]
        }
    )
    return json_response(data=data)
