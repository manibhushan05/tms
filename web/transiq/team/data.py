import pandas as pd

from broker.models import Broker
from owner.models import Owner, Vehicle
from owner.vehicle_util import compare_format
from sme.models import Sme
from team.models import ManualBooking, DeletedData, OutWardPayment


def booking_customer_make_payment():
    data = []
    for booking in ManualBooking.objects.order_by('-id', '-shipment_date'):
        data.append([
            booking.id,
            booking.booking_id,
            booking.shipment_date.strftime('%d-%b-%Y'),
            booking.customer_to_be_billed_to_id,
            booking.customer_to_be_billed_to.get_name() if booking.customer_to_be_billed_to else ''
        ])
    df = pd.DataFrame(data=data, columns=['ID', 'Booking ID', 'Shipment Date', 'Customer ID', 'Customer'])
    df.to_excel('Bookings customer.xlsx', index=False)


def invoice_deleted_data():
    DeletedData.objects.filter(model=None).update(model='invoice')
    data = []
    for dd in DeletedData.objects.filter(model__in=['to_pay_invoice', 'tbb_pay_invoice']):
        try:
            company = dd.data['fields']['company']
        except KeyError:
            company = dd.data['fields']['company_name']
        try:
            amount = dd.data['fields']['total_amount']
        except KeyError:
            amount = dd.data['fields']['total_payable_freight']
        if company.startswith('SONIC'):
            booking_id = [booking['fields']['booking_id'] for booking in dd.data['fields']['bookings']]
            bookings = ManualBooking.objects.filter(booking_id__in=booking_id)
            lr_number = '\n'.join(
                ['\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in bookings])
            data.append([
                company,
                '\n'.join(bookings.values_list('booking_id', flat=True)),
                lr_number,
                dd.data['fields']['invoice_number'],
                dd.data['fields']['date'],
                amount,
            ])
    df = pd.DataFrame(data=data,
                      columns=['Company name', 'Booking ID', 'LR Number(s)', 'Invoice Number', 'Date', 'Amount'])
    df.to_excel('Delete Invoice of Sonic Thermal.xlsx')


def supplier_data():
    data = []
    for broker in Broker.objects.all():
        data.append([
            broker.id,
            broker.get_name(),
            broker.get_phone(),
            broker.get_alt_phone(),
            broker.created_on,
            broker.team_booking_broker.filter(shipment_date__month=broker.created_on.month,
                                              shipment_date__year=broker.created_on.year).exclude(
                booking_status='cancelled').count(),
            '\n'.join([booking.booking_id for booking in
                       broker.team_booking_broker.filter(shipment_date__month=broker.created_on.month,
                                                         shipment_date__year=broker.created_on.year).exclude(
                           booking_status='cancelled')])
        ])
    df = pd.DataFrame(data=data,
                      columns=['id', 'Name', 'Phone', 'Alt Phone', 'Registered on', 'Number of booking', 'bookings'])
    df.to_excel('supplier data.xlsx', index=False)


def owners_booking_data():
    data = []
    for owner in Owner.objects.all():
        data.append([
            owner.id,
            owner.get_name(),
            owner.get_phone(),
            owner.created_on,
            owner.manualbooking_set.filter(shipment_date__month=owner.created_on.month,
                                           shipment_date__year=owner.created_on.year).exclude(
                booking_status='cancelled').count(),
            '\n'.join([booking.booking_id for booking in
                       owner.manualbooking_set.filter(shipment_date__month=owner.created_on.month,
                                                      shipment_date__year=owner.created_on.year).exclude(
                           booking_status='cancelled')])
        ])
    df = pd.DataFrame(data=data,
                      columns=['id', 'Name', 'Phone', 'Registered on', 'Number of booking', 'bookings'])

    df.to_excel('owner data.xlsx', index=False)


def customer_booking_data():
    data = []
    for sme in Sme.objects.all():
        data.append([
            sme.id,
            sme.company_code,
            sme.get_name(),
            sme.created_on,
            sme.mb_bill_order_placed.filter(shipment_date__month=sme.created_on.month,
                                            shipment_date__year=sme.created_on.year).exclude(
                booking_status='cancelled').count(),
            '\n'.join([booking.booking_id for booking in
                       sme.mb_bill_order_placed.filter(shipment_date__month=sme.created_on.month,
                                                       shipment_date__year=sme.created_on.year).exclude(
                           booking_status='cancelled')])
        ])
    df = pd.DataFrame(data=data,
                      columns=['id', 'company_code', 'Name', 'Registered on', 'Number of booking', 'bookings'])

    df.to_excel('Customer data.xlsx', index=False)


def vehicle_data():
    data = []
    for vehicle in Vehicle.objects.filter():
        data.append([
            vehicle.id,
            vehicle.number(),
            vehicle.vehicle_type.get_name() if vehicle.vehicle_type else '',
            vehicle.created_on
        ])
    df = pd.DataFrame(data=data, columns=['ID', 'Vehicle Number', 'Vehicle Type', 'Created On'])
    df.to_excel('Vehicles.xlsx', index=False)


def manual_booking_data():
    data = []
    for booking in ManualBooking.objects.exclude(booking_status='cancelled'):
        try:
            vehicle = Vehicle.objects.get(vehicle_number=compare_format(booking.lorry_number))
            vehhicle_type = vehicle.vehicle_type.get_name() if vehicle.vehicle_type else ''
        except Vehicle.DoesNotExist:
            vehhicle_type = ''
        data.append([
            booking.id,
            booking.booking_id,
            booking.lorry_number,
            booking.type_of_vehicle
        ])


def daily_mail_pending_pod_test_data():
    return {'bookings': [{'lr_number': 'SGR180718104',
                          'vehicle_number': 'CG04 LV 2999',
                          'from': 'Rajim',
                          'to': 'Visakhapatnam',
                          'charged_weight': '25.000',
                          'rate': '1050',
                          'additional_charge': 100,
                          'customer_freight': 26250,
                          'additional_charge_superscript': 1},
                         {'lr_number': 'SGR180718103',
                          'vehicle_number': 'CG04 LQ 2999',
                          'from': 'Rajim',
                          'to': 'Visakhapatnam',
                          'charged_weight': '25.000',
                          'rate': '1050',
                          'additional_charge': 121,
                          'customer_freight': 26250,
                          'additional_charge_superscript': 2},
                         {'lr_number': 'SGR180718102',
                          'vehicle_number': 'PB02 CR 6233',
                          'from': 'Rajim',
                          'to': 'Visakhapatnam',
                          'charged_weight': '28.000',
                          'rate': '1050',
                          'additional_charge': 0,
                          'customer_freight': 29400,
                          'additional_charge_superscript': ''}],
            'credit_period': 15,
            'additional_charge_remarks': [
                {'id': 1, 'message': 'Invoice remarks for additional charges 1'},
                {'id': 2, 'message': 'Invoice remarks for additional charges 2'}],
            'dispatch_date': '18-Jul-2018',
            'email_id_list': ['kamalstc5544@gmail.com',
                              'naresh@aaho.in',
                              'pkrathoretcil80@gmail.com'],
            'enable_email': True}


def outward_payment_dump():
    data = []
    for payment in OutWardPayment.objects.filter(
            payment_date__gte='2018-03-01').order_by('-payment_date'):
        data.append([
            payment.payment_date.strftime('%d-%b-%Y'),
            payment.id,
            payment.paid_to,
            '\n'.join([lr.lr_number for lr in payment.booking_id.last().lr_numbers.all()]),
            '\n'.join([booking.lorry_number for booking in payment.booking_id.all()]),
            '\n'.join([booking.booking_id for booking in payment.booking_id.all()]),
            payment.actual_amount,
            payment.fuel_card.card_number if payment.fuel_card else None,
            payment.get_payment_mode_display(),
            payment.remarks,
            payment.status,
            payment.is_refund_amount,
            payment.utr
        ])
    df = pd.DataFrame(data=data, columns=['Date', 'ID', 'Paid To', 'Lr Number', 'Lorry Number', 'Booking ID', 'Amount',
                                          'Fuel Card', 'Mode', 'Remarks', 'Status', 'Is Refund', 'UTR'])
    df.to_excel('Outward_Payment_2018.xlsx', index=False)