from __future__ import division

import pandas as pd

from broker.models import Broker
from owner.models import Owner
from owner.vehicle_util import display_format, compare_format
from sme.models import Sme
from team.models import ManualBooking, OutWardPayment, InWardPayment
from utils.models import City, Address, Bank


def update_inward_payments():
    for booking in ManualBooking.objects.all():
        amount_list = InWardPayment.objects.filter(booking_id=booking).values_list('actual_amount', flat=True)
        if sum(amount_list) - booking.total_in_ward_amount != 0:
            booking.total_in_ward_amount = sum(amount_list)
            booking.save()
        payment_plus_tds = sum(amount_list) + booking.tds_deducted_amount
        if payment_plus_tds == 0:
            booking.inward_payment_status = 'no_payment'
        elif payment_plus_tds < booking.total_amount_to_company:
            booking.inward_payment_status = 'partial_received'
        elif payment_plus_tds == booking.total_amount_to_company:
            booking.inward_payment_status = 'full_received'
        elif payment_plus_tds > booking.total_amount_to_company:
            booking.inward_payment_status = 'excess'
        booking.save()
    return 'Successfully Inward payment status updated'


def update_outward_payments():
    for booking in ManualBooking.objects.all():
        amount_list = OutWardPayment.objects.filter(booking_id=booking).values_list('actual_amount', flat=True)
        outward_payment = sum(amount_list)
        # update amount
        if outward_payment - booking.total_out_ward_amount != 0:
            booking.total_out_ward_amount = sum(amount_list)
            booking.save()
        if outward_payment < booking.total_amount_to_owner:
            booking.outward_payment_status = 'partial'
        elif outward_payment == booking.total_amount_to_owner:
            booking.outward_payment_status = 'complete'
        elif outward_payment > booking.total_amount_to_owner:
            booking.outward_payment_status = 'excess'
        else:
            print(booking.booking_id)

        booking.save()


def check_total_amount_from_company(booking):
    # booking = ManualBooking.objects.get(id=34)
    freight_to_company = booking.charged_weight * booking.party_rate
    charges = booking.additional_charges_for_company
    deduction = booking.deductions_for_company
    if abs((freight_to_company + charges - deduction) - booking.total_amount_to_company) > 0:
        print(freight_to_company, charges, deduction,
              freight_to_company + charges - deduction - booking.total_amount_to_company, booking.booking_id)


def sme_datails():
    data = []
    for sme in Sme.objects.all():
        try:
            data.append(
                [sme.id, sme.get_name(), sme.company_code, sme.get_address(), sme.city.name if sme.city else '',
                 sme.gstin])
        except:
            print(sme)

    df = pd.DataFrame(data=data, columns=['ID', 'Name', 'Code', 'Address', 'City', 'GSTIN'])
    df.to_excel('/Users/mani/workspace/aaho/data/customers.xlsx', index=False)


def bookings_with_low_profit():
    data = []
    for booking in ManualBooking.objects.filter(shipment_date__gte='2017-04-01').exclude(
            booking_status='cancelled').order_by('-shipment_date'):
        try:
            profit = round(((
                                    booking.total_amount_to_company - booking.total_amount_to_owner) / booking.total_amount_to_owner) * 100,
                           2)
            if profit < 3:
                data.append([
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
                    profit,
                    booking.commission,
                    booking.lr_cost,
                    booking.deduction_for_advance,
                    booking.deduction_for_balance,
                    booking.other_deduction,
                    booking.remarks_about_deduction,
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
                ])

        except ZeroDivisionError:
            print(booking)
    columns = ['Booking ID', 'LR Numbers', 'Shipment Date', 'Billing Type',
               'Source Office', 'Destination Office', 'From City', 'To City',
               'Customer who placed order', 'Customer who will make payment', 'Supplier Name',
               'Supplier Phone',
               'Owner Name', 'Owner Phone', 'Vehicle Number', 'Driver Name', 'Driver Phone',
               'Actual Weight',
               'Charged Weight to Customer',
               'Charged Weight for Supplier',
               'Customer Rate', 'Supplier Rate',
               'Total Amount from Customer', 'Deduction for Customer',
               'Total Inward Amount', 'TDS', 'Total Amount to Owner', '% Profit', 'Commission', 'LR Cost',
               'Deduction for Advance',
               'Deduction for Balance', 'Other Deduction', 'Deduction Remarks',
               'Total Outward Amount', 'Outward Payment Remarks', 'Invoice Number',
               'Invoice Date',
               'Invoice Amount', 'OPB Number', 'OPB Date', 'OPB Amount'

               ]
    df = pd.DataFrame(data=data, columns=columns)
    df.to_excel('profit less than 3%.xlsx', index=False)


def sme_consignor_details():
    bookings = ManualBooking.objects.exclude(consignor_name=None).values_list(
        'consignor_name',
        'consignor_address',
        'consignor_city',
        'consignor_pin',
        'consignor_phone'
    )
    data = list(set(bookings))
    df = pd.DataFrame(data, columns=['Name', 'Address', 'City', 'Pin', 'Phone'])
    df = df.sort(columns=['Name'])
    df.to_excel('consignors.xlsx', index=False)


def brokers_data():
    data = []
    for broker in Broker.objects.all().order_by('-id'):
        temp = []
        temp.append(broker.id)
        temp.append(broker.name.username)
        temp.append(broker.get_name())
        temp.append(broker.get_phone())
        temp.append(broker.get_alt_phone())
        for bv in broker.broker_vehicle.all():
            temp.append(bv.vehicle.vehicle_number)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df.to_excel('brokers_data.xlsx', index=False)


def owners_data():
    data = []
    for owner in Owner.objects.all():
        temp = []
        temp.append(owner.id)
        temp.append(owner.name.username)
        temp.append(owner.get_name())
        temp.append(owner.get_phone())
        for vehicle in owner.vehicle_owner.all():
            temp.append(vehicle.vehicle_number)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df.to_excel('owners_data.xlsx', index=False)


def update_city_data():
    df = pd.read_excel('../../data/cities v1.2.xlsx')
    for i, row in df.iterrows():
        try:
            city = City.objects.get(code=row['Code'])
            if ManualBooking.objects.filter(from_city__icontains=row['Name']).exists() or ManualBooking.objects.filter(
                    to_city__icontains=row['Name']).exists():
                print(ManualBooking.objects.filter(from_city__icontains=row['Name']).count(),
                      ManualBooking.objects.filter(to_city__icontains=row['Name']).count(), row['Name'], row['Code'])
                ManualBooking.objects.filter(from_city__icontains=row['Name']).update(from_city_fk=city)
                ManualBooking.objects.filter(to_city__icontains=row['Name']).update(to_city_fk=city)
        except City.DoesNotExist:
            pass


def delete_city():
    ManualBooking.objects.filter(to_city_fk=City.objects.get(id=407)).update(to_city_fk=City.objects.get(id=519))
    ManualBooking.objects.filter(from_city_fk=City.objects.get(id=407)).update(from_city_fk=City.objects.get(id=519))
    ManualBooking.objects.filter(consignor_city_fk=City.objects.get(id=407)).update(
        consignor_city_fk=City.objects.get(id=519))
    ManualBooking.objects.filter(consignee_city_fk=City.objects.get(id=407)).update(
        consignee_city_fk=City.objects.get(id=519))
    Address.objects.filter(city=City.objects.get(id=407)).update(
        city=City.objects.get(id=519))


def bank_account_details():
    data = []
    for bank in Bank.objects.all():
        data.append([
            bank.id,
            bank.user.profile.name if bank.user else '',
            bank.bank,
            bank.account_holder_name,
            bank.beneficiary_code,
            str(bank.account_number),
            bank.ifsc,
            bank.get_transaction_type_display(),
            bank.get_account_type_display()

        ])
    df = pd.DataFrame(
        data=data,
        columns=['ID', 'User', 'Bank Name', 'Account Holder Name', 'Beneficiary Code', 'Account Number', 'IFSC',
                 'Transaction Type', 'Account Type']
    )
