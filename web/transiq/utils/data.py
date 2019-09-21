import pandas as pd
from api.s3util import save_to_s3_table_dumps
from owner.vehicle_util import display_format, compare_format
from team.models import ManualBooking, OutWardPayment, InWardPayment, Invoice
from utils.models import City
from io import BytesIO
from datetime import datetime


def cities_data():
    data = []
    for city in City.objects.order_by('id'):
        data.append([
            city.id,
            city.name,
            city.state.name if city.state else '',
            city.latitude,
            city.longitude
        ])
    df = pd.DataFrame(data=data, columns=['ID', 'Name', 'State', 'Lat', 'Lng'])
    df.to_excel('cities-v7.xlsx',index=False)


def df_full_booking_excel():
    columns = [
        'Booking ID', 'LR Numbers', 'Shipment Date', 'Delivered Date', 'Billing Type', 'Source Office', 'Destination Office', 'From City',
        'To City', 'Customer who placed order', 'Customer who will make payment', 'Supplier Name', 'Supplier Phone',
        'Owner Name', 'Owner Phone', 'Vehicle Number', 'Driver Name', 'Driver Phone', 'Actual Weight',
        'Charged Weight to Customer', 'Charged Weight for Supplier', 'Customer Rate', 'Supplier Rate',
        'Total Amount from Customer', 'Refundable Amount', 'Deduction for Customer', 'Total Inward Amount', 'TDS',
        'Total Amount to Owner', 'Commission', 'LR Cost', 'Deduction for Advance', 'Deduction for Balance',
        'Other Deduction', 'Deduction Remarks', 'Invoice Status', 'Total Outward Amount', 'Outward Payment Remarks',
        'Invoice Number', 'Invoice Date', 'Invoice Amount', 'OPB Number', 'OPB Date', 'OPB Amount', 'POD Status', 'POD Date',
        'Customer who will make payment (Code)', 'Supplier Code', 'Customer Balance', 'Supplier Balance', 'CNCA',
        'CNC', 'CNS', 'DNS', 'DNC', 'Loading Charges', 'Unloading Charges', 'Detention Charges', 'Other Charges - Supplier',
        'Remarks about additional charges - Supplier', 'Additional Charges if any (+) - Customer',
        'Remarks for additional charges - Customer', 'Deductions / Discounts if any (-)',
        'Invoice remarks for deductions/discounts', 'Advance to Trans IQ', 'Booking Status'
    ]

    data = []
    for booking in ManualBooking.objects.filter(shipment_date__gte='2018-04-01').exclude(booking_status='cancelled').order_by('-shipment_date'):
        print('.')
        data.append([
            booking.booking_id,
            '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
            booking.shipment_date,
            booking.delivery_datetime if booking.delivery_datetime else '',
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
            booking.refund_amount,
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
            '\n'.join([', '.join(map(str, row)) if row else '' for row in
                       booking.outward_booking.values_list('payment_mode', 'actual_amount', 'remarks')]),
            ''.join(invoice_number if invoice_number else '' for invoice_number in
                    list(booking.invoices.values_list('invoice_number', flat=True)) +
                    list(booking.to_pay_invoices.values_list('invoice_number', flat=True))),
            ''.join([invoice_date.strftime('%d-%b-%Y') if invoice_date else '' for invoice_date in
                     list(booking.invoices.values_list('date', flat=True)) + list(
                         booking.to_pay_invoices.values_list('date', flat=True))]),
            ''.join(list(map(str, list(booking.invoices.values_list('total_amount', flat=True)))) + list(
                amount_payable_to_transiq if amount_payable_to_transiq else '' for amount_payable_to_transiq in booking.to_pay_invoices.values_list('amount_payable_to_transiq', flat=True))),
            '\n'.join(booking.outward_payment_bill.values_list('bill_number',
                                                               flat=True)) if booking.outward_payment_bill else '',
            '\n'.join([opb.bill_date.strftime('%d-%b-%Y') if opb.bill_date else '' for opb in
                       booking.outward_payment_bill.all()]),
            '\n'.join(map(str, booking.outward_payment_bill.values_list('amount',
                                                                        flat=True))) if booking.outward_payment_bill else '',
            booking.pod_status,
            booking.pod_date if booking.pod_date else '',
            booking.customer_to_be_billed_to.company_code if booking.customer_to_be_billed_to else None,
            booking.supplier.code if booking.supplier else None,
            booking.balance_for_customer,
            booking.balance_for_supplier,
            booking.adjusted_cnca_amount,
            booking.credit_amount_customer,
            booking.credit_amount_supplier,
            booking.debit_amount_supplier,
            booking.debit_amount_customer,
            booking.loading_charge,
            booking.unloading_charge,
            booking.detention_charge,
            booking.additional_charges_for_owner,
            booking.note_for_additional_owner_charges,
            booking.additional_charges_for_company,
            booking.remarks_about_additional_charges,
            booking.deductions_for_company,
            booking.invoice_remarks_for_deduction_discount,
            booking.advance_amount_from_company,
            booking.booking_status
        ])

    df = pd.DataFrame(data=data, columns=columns)
    return df
    # df.to_excel('full_bookings_data.xlsx', index=False)


def download_full_booking_excel():
    df = df_full_booking_excel()
    df.to_excel('full_bookings_data.xlsx', index=False)


def s3_dump_full_booking_excel():
    df = df_full_booking_excel()
    byte_io = BytesIO()

    # Use the BytesIO object as the filehandle.
    writer = pd.ExcelWriter(byte_io, engine='xlsxwriter')

    # Write the data frame to the BytesIO object.
    df.to_excel(writer, index=False)
    writer.save()
    content = byte_io.getvalue() or '\n'
    s3_upload = save_to_s3_table_dumps(
        'manual_booking_table_{}.xlsx'.format(datetime.now().strftime('%d_%b_%Y_%I_%M_%S_%p')), content)
    # print(s3_upload.public_url())


def df_outward_payment_content():
    columns = [
        'Payment Date', 'ID', 'Paid To', 'LR Number', 'Lorry number', 'Booking ID', 'Amount', 'Fuel Card', 'Mode',
        'Remarks', 'Status', 'Is Refund', 'UTR'
    ]

    data = []
    for op in OutWardPayment.objects.filter(payment_date__gte='2018-04-01').exclude(
            deleted=True).order_by('-payment_date'):
        print('.')
        data.append([
            op.payment_date.strftime('%d-%b-%Y'),
            op.id,
            op.paid_to,
            '\n'.join([lr.lr_number for lr in op.booking_id.last().lr_numbers.all()]) if op.booking_id.last() else '',
            '\n'.join([booking.lorry_number if booking.lorry_number else '' for booking in op.booking_id.all()]) if op.booking_id else '',
            '\n'.join([booking.booking_id for booking in op.booking_id.all()]),
            op.actual_amount,
            op.fuel_card.card_number if op.fuel_card else None,
            op.get_payment_mode_display(),
            op.remarks,
            op.status,
            op.is_refund_amount,
            op.utr
        ])

    df = pd.DataFrame(data=data, columns=columns)
    return df


def download_outward_payment_excel():
    df = df_outward_payment_content()
    df.to_excel('outward_payment_data.xlsx', index=False)


def s3_dump_outward_payment_excel():
    df = df_outward_payment_content()
    byte_io = BytesIO()

    # Use the BytesIO object as the filehandle.
    writer = pd.ExcelWriter(byte_io, engine='xlsxwriter')

    # Write the data frame to the BytesIO object.
    df.to_excel(writer, index=False)
    writer.save()
    content = byte_io.getvalue() or '\n'
    s3_upload = save_to_s3_table_dumps(
        'outward_payment_table_{}.xlsx'.format(datetime.now().strftime('%d_%b_%Y_%I_%M_%S_%p')), content)
    # print(s3_upload.public_url())


def df_inward_payment_content():
    columns = [
        'Payment Date', 'ID', 'Received From', 'LR Number', 'Lorry number', 'Booking ID', 'Actual Amount',
        'Expected Amount', 'TDS', 'Mode', 'Trn', 'Remarks', 'Invoice Number'
    ]

    data = []
    for ip in InWardPayment.objects.filter(payment_date__gte='2018-04-01').exclude(
            deleted=True).order_by('-payment_date'):
        print('.')
        data.append([
            ip.payment_date.strftime('%d-%b-%Y'),
            ip.id,
            ip.received_from,
            '\n'.join([lr.lr_number for lr in ip.booking_id.last().lr_numbers.all()]) if ip.booking_id.last() else '',
            '\n'.join([booking.lorry_number if booking.lorry_number else '' for booking in ip.booking_id.all()]) if ip.booking_id else '',
            '\n'.join([booking.booking_id for booking in ip.booking_id.all()]),
            ip.actual_amount,
            ip.expected_amount,
            ip.tds,
            ip.get_payment_mode_display(),
            ip.trn,
            ip.remarks,
            ip.invoice_number
        ])

    df = pd.DataFrame(data=data, columns=columns)
    return df


def download_inward_payment_excel():
    df = df_inward_payment_content()
    df.to_excel('inward_payment_data.xlsx', index=False)


def s3_dump_inward_payment_excel():
    df = df_inward_payment_content()
    byte_io = BytesIO()

    # Use the BytesIO object as the filehandle.
    writer = pd.ExcelWriter(byte_io, engine='xlsxwriter')

    # Write the data frame to the BytesIO object.
    df.to_excel(writer, index=False)
    writer.save()
    content = byte_io.getvalue() or '\n'
    s3_upload = save_to_s3_table_dumps(
        'inward_payment_table_{}.xlsx'.format(datetime.now().strftime('%d_%b_%Y_%I_%M_%S_%p')), content)
    # print(s3_upload.public_url())


def df_invoice_content():
    columns = [
        'ID', 'Invoice Number', 'LR Number', 'Lorry number', 'Booking ID',
        'Date', 'Company Name', 'Customer', 'Payment Received', 'Address',
        'City', 'Pin', 'GSTIN', 'Total Amount', 'Advance Payment', 'Remarks',
        'Service Tax Paid By', 'Service Tax Aaho'
    ]

    data = []
    for invoice in Invoice.objects.filter(date__gte='2018-04-01').exclude(
            deleted=True).order_by('-date'):
        print('.')
        data.append([
            invoice.id,
            invoice.invoice_number,
            '\n'.join([lr.lr_number for lr in invoice.bookings.last().lr_numbers.all()]) if invoice.bookings.last() else '',
            '\n'.join([booking.lorry_number if booking.lorry_number else '' for booking in invoice.bookings.all()]) if invoice.bookings else '',
            '\n'.join([booking.booking_id for booking in invoice.bookings.all()]),
            invoice.date.strftime('%d-%b-%Y'),
            invoice.company_name,
            invoice.customer_fk.get_name() if invoice.customer_fk else '',
            invoice.payment_received,
            invoice.address,
            invoice.city.name if invoice.city else '',
            invoice.pin,
            invoice.gstin,
            invoice.total_amount,
            invoice.advance_payment,
            invoice.remarks,
            invoice.service_tax_paid_by,
            invoice.service_tax_aaho
        ])

    df = pd.DataFrame(data=data, columns=columns)
    return df


def download_invoice_excel():
    df = df_invoice_content()
    df.to_excel('invoice_data.xlsx', index=False)


def s3_dump_invoice_excel():
    df = df_invoice_content()
    byte_io = BytesIO()

    # Use the BytesIO object as the filehandle.
    writer = pd.ExcelWriter(byte_io, engine='xlsxwriter')

    # Write the data frame to the BytesIO object.
    df.to_excel(writer, index=False)
    writer.save()
    content = byte_io.getvalue() or '\n'
    s3_upload = save_to_s3_table_dumps(
        'invoice_table_{}.xlsx'.format(datetime.now().strftime('%d_%b_%Y_%I_%M_%S_%p')), content)
    # print(s3_upload.public_url())
