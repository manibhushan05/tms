from __future__ import unicode_literals

from datetime import datetime, timedelta

import pandas as pd
from django.contrib.auth.models import Group, User
from django.db.models import Q, Count

from api.models import S3Upload
from authentication.models import Profile
from broker.models import Broker, BrokerVehicle
from fileupload.models import OwnerFile
from fms.models import Document
from owner.vehicle_util import display_format, compare_format
from team.models import ManualBooking


def transaction_data():
    booking = ManualBooking.objects.get(id=3684)
    data = {}
    data.update({'status': 'success'})

    data.update(
        {
            'basic_data': {
                'lr_number': '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                'from_city': booking.from_city,
                'to_city': booking.to_city,
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

    return data


def check_fms_user_docs():
    print ([{'id': owner.id, 'name': owner.owner.get_name(), 'url': owner.s3_upload.public_url()} for owner in
            OwnerFile.objects.all()])


def download_master_table(filename, bookings):
    columns = [
        'Booking ID', 'LR Numbers', 'Shipment Date', 'Billing Type', 'Source Office', 'Destination Office', 'From City',
        'To City', 'Customer who placed order', 'Customer who will make payment', 'Supplier Name', 'Supplier Phone',
        'Owner Name', 'Owner Phone', 'Vehicle Number', 'Driver Name', 'Driver Phone', 'Actual Weight',
        'Charged Weight to Customer', 'Charged Weight for Supplier', 'Customer Rate', 'Supplier Rate',
        'Total Amount from Customer', 'Deduction for Customer', 'Total Inward Amount', 'TDS', 'Total Amount to Owner',
        'Commission', 'LR Cost', 'Deduction for Advance', 'Deduction for Balance', 'Other Deduction',
        'Deduction Remarks', 'Invoice Status', 'Total Outward Amount', 'Outward Payment Remarks', 'Invoice Number',
        'Invoice Date',
        'Invoice Amount', 'OPB Number', 'OPB Date', 'OPB Amount'
    ]
    data = [[
        booking.booking_id,
        '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
        booking.shipment_date,
        booking.get_billing_type_display(),
        booking.source_office.branch.name if booking.source_office else '',
        booking.destination_office.branch.name if booking.destination_office else '',
        booking.from_city,
        booking.to_city,
        booking.company.get_name() if booking.company else '',
        booking.customer_to_be_billed_to.get_name() if booking.customer_to_be_billed_to else '',
        booking.truck_broker_owner_name,
        booking.truck_broker_owner_phone,
        booking.truck_owner_name,
        booking.truck_owner_phone,
        display_format(compare_format(booking.lorry_number)),
        booking.driver_name,
        booking.driver_phone,
        booking.loaded_weight,
        booking.charged_weight,
        booking.supplier_charged_weight,
        booking.party_rate,
        booking.supplier_rate,
        booking.total_amount_to_company,
        booking.deductions_for_company,
        booking.total_in_ward_amount,
        booking.tds_deducted_amount,
        booking.total_amount_to_owner,
        booking.commission,
        booking.lr_cost,
        booking.deduction_for_advance,
        booking.deduction_for_balance,
        booking.other_deduction,
        booking.remarks_about_deduction,
        booking.get_invoice_status_display(),
        sum(booking.outward_booking.values_list('actual_amount', flat=True)),
        '\n'.join([', '.join(map(str, row)) for row in
                   booking.outward_booking.values_list('payment_mode', 'actual_amount', 'remarks')]),
        ''.join(list(booking.invoices.values_list('invoice_number', flat=True)) + list(
            booking.to_pay_invoices.values_list('invoice_number', flat=True))),
        ''.join([invoice_date.strftime('%d-%b-%Y') if invoice_date else '' for invoice_date in
                 list(booking.invoices.values_list('date', flat=True)) + list(
                     booking.to_pay_invoices.values_list('date', flat=True))]),
        ''.join(map(str, list(booking.invoices.values_list('total_amount', flat=True))) + list(
            booking.to_pay_invoices.values_list('amount_payable_to_transiq', flat=True))),
        '\n'.join(booking.outward_payment_bill.values_list('bill_number', flat=True)),
        '\n'.join([opb.bill_date.strftime('%d-%b-%Y') if opb.bill_date else '' for opb in
                   booking.outward_payment_bill.all()]),
        '\n'.join(map(str, booking.outward_payment_bill.values_list('amount', flat=True)))
    ] for booking in bookings]

    df = pd.DataFrame(data=data, columns=columns)
    df.to_excel(filename, index=False)


def fms_booking_data():
    group = Group.objects.get(name='fms')
    for user in group.user_set.all():
        # print user, user.profile.name

        bookings = ManualBooking.objects.filter(
            Q(truck_broker_owner_phone=user.profile.phone) | Q(truck_owner_phone=user.profile.phone)).filter(
            shipment_date__gte=datetime.now().date() - timedelta(days=90)).exclude(
            booking_status__icontains='cancelled').order_by('-shipment_date')
        download_master_table(filename=user.profile.name + '_new.xlsx', bookings=bookings)
        try:
            broker = Broker.objects.filter(name=User.objects.get(username=user.profile.phone)).last()
            broker_vehicle = BrokerVehicle.objects.filter(broker=broker).values_list('vehicle__vehicle_number',
                                                                                     flat=True)
            vehicles = [display_format(vehicle) for vehicle in broker_vehicle]
            bookings = ManualBooking.objects.filter(lorry_number__in=vehicles,
                                                    shipment_date__gte=datetime.now().date() - timedelta(
                                                        days=90)).exclude(
                booking_status__icontains='cancelled').order_by('-shipment_date')
            print ('old', user.profile.name, bookings.count())
            download_master_table(filename=user.profile.name + '_old.xlsx', bookings=bookings)
        except:
            print (user)


def booking_supplier_owner():
    for booking in ManualBooking.objects.filter(shipment_date__gte='2017-10-01').exclude(
        booking_status__icontains='cancelled').order_by('shipment_date'):
        try:
            broker = Broker.objects.get(name__profile__phone=booking.truck_broker_owner_phone)
            # print (broker)
        except Broker.DoesNotExist:
            pass
            # print booking.shipment_date
        except Broker.MultipleObjectsReturned:
            broker = Broker.objects.filter(name__profile__phone=booking.truck_broker_owner_phone).filter(
                name__profile__name__iexact=booking.truck_broker_owner_name)
            if broker.count() > 1:
                print (broker)


def clean_broker_data():
    print(Profile.objects.annotate(phone_c=Count('phone')).filter(phone_c__gte=1))


def mobile_for_otp():
    for broker in Broker.objects.filter(name__in=User.objects.filter(groups__name='fms')):
        try:
            user_data = broker.name.username
            if Broker.objects.filter(name__username=user_data).exists():
                try:
                    broker = Broker.objects.get(name__username=user_data)
                    if broker.name:
                        phone = broker.name.profile.phone
                        if phone:
                            data = {
                                'phone': phone,
                                'authkey': '115151AKpRGb9tug57565bd3'
                            }
                            print(data)
                        else:
                            print(
                            {'status': 'error', 'msg': 'Phone does not exit exits, Please contact to AAHO'}, broker)
                    else:
                        print({'status': 'error', 'msg': 'User does not exit exits, Please contact to AAHO'})
                except Broker.DoesNotExist:
                    print({'status': 'error', 'msg': 'User does not exit exits, Please contact to AAHO'})
                except Broker.MultipleObjectsReturned:
                    print({'status': 'error', 'msg': 'Multiple user with same phone number exits'})

            elif Broker.objects.filter(name__profile__phone=user_data).exists():
                try:
                    broker = Broker.objects.get(name__profile__phone=user_data)
                    if broker.name:
                        phone = broker.name.profile.phone
                        if phone:
                            data = {
                                'phone': phone,
                                'authkey': '115151AKpRGb9tug57565bd3'
                            }
                            print(data)
                        else:
                            print({'status': 'error', 'msg': 'Phone does not exit exits, Please contact to AAHO'})
                    else:
                        print({'status': 'error', 'msg': 'Phone does not exit exits, Please contact to AAHO'})
                except Broker.DoesNotExist:
                    print({'status': 'error', 'msg': 'User doesnot exits'})
                except Broker.MultipleObjectsReturned:
                    if user_data:
                        print({'status': 'error', 'msg': 'Multiple user with %s phone number exits' % (user_data)})
                    else:
                        print({'status': 'error', 'msg': 'Phone does not exit exits, Please contact to AAHO'})
            else:
                print({'status': 'error', 'msg': 'User doesnot exits'})
        except:
            pass


def trip_history_test():
    bookings = ManualBooking.objects.order_by('-shipment_date')
    for booking in bookings:
        for lr in booking.lr_numbers.all():
            if S3Upload.objects.filter(filename__contains=lr.lr_number+'.pdf').count() <1:
                print(S3Upload.objects.filter(filename__iexact=lr.lr_number+'.pdf'),lr.lr_number)


def documents_verification():
    print("mani")
    for doc in Document.objects.all():
        if doc.ins_vehicle.all() or doc.reg_vehicle.all() or doc.puc_vehicle.all() or doc.fit_vehicle.all() or doc.perm_vehicle.all():
            pass
        else:
            print(doc,doc.ins_vehicle.all() , doc.reg_vehicle.all() , doc.puc_vehicle.all() , doc.fit_vehicle.all() , doc.perm_vehicle.all())



def fms_users():
    fms=User.objects.filter(groups__name='fms')
    data=[]
    for user in fms:
        data.append([user.username,user.profile.name,user.profile.phone,user.profile.alternate_phone])
    df=pd.DataFrame(data=data,columns=['Username','Name','Phone','Alt Phone'])
    df.to_excel('fms_users.xlsx',index=False)