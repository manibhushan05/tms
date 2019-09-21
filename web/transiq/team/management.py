import json
from datetime import datetime

import pandas as pd
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.models import User
from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse
from django.utils.encoding import force_text, smart_str
from django.utils.text import capfirst, slugify

from api.models import S3Upload
from api.s3util import save_to_s3_invoice
from api.utils import to_int, get_or_none
from broker.models import Broker
from employee.models import Employee, TaskEmail
from fms.models import Requirement
from owner.models import FuelCard
from restapi.helper_api import generate_credit_note_customer_serial_number, generate_debit_note_customer_serial_number, \
    generate_debit_note_supplier_serial_number
from sme.models import Sme
from team.models import ManualBooking, OutWardPayment, Invoice, LrNumber, DeletedData, CreditNoteCustomer, \
    InWardPayment, LrS3Upload, ManualBookingS3Upload, CreditDebitNoteReason, DebitNoteCustomer, DebitNoteSupplier
from team.services.create_new_tables import outward_payment
from team.views_booking import get_lr_numbers
from utils.models import AahoOffice, City

DEV_AAHO_URL = ''
LOCALHOST_AAHO_URL = 'http://127.0.0.1:8000'


def make_outward_payment():
    df = pd.read_excel('/Users/mani/Downloads/Commision paid on 28 Aug-18 Rs 48500.xlsx')
    for i, row in df.iterrows():
        outward_payment(
            paid_to=row['Paid To'],
            amount=row['Amount'],
            date=row['Date'].strftime('%d-%b-%Y'),
            fuel_card=None,
            remarks='{}, {}'.format(row['Remarks'], row['UTR']),
            booking_id_list=ManualBooking.objects.filter(booking_id=row['Booking ID']).values_list('id', flat=True),
            account_id=None,
            payment_mode='imps',
            is_sms='No',
            username='mani@aaho.in',
            is_refund_amount=True
        )


def get_deleted_objects(objs):
    collector = NestedObjects(using='default')
    collector.collect(objs)

    def format_callback(obj):
        opts = obj._meta
        no_edit_link = '%s: %s' % (capfirst(opts.verbose_name),
                                   force_text(obj))
        return no_edit_link

    to_delete = collector.nested(format_callback)
    protected = [format_callback(obj) for obj in collector.protected]
    model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}
    return model_count, protected


def verify_lr_numbers():
    source_office = AahoOffice.objects.get(id=8)
    destination_office = AahoOffice.objects.get(id=1)
    company_code = 'IDL'
    shipment_datetime = datetime.now()
    number_of_lr = 2
    get_lr_numbers(source_office, destination_office, shipment_datetime, company_code, number_of_lr,
                   created_by=User.objects.get(username='mani@aaho.in'))


def manual_booking_audit_log():
    data = []
    for booking in ManualBooking.objects.filter(shipment_date__gte='2018-03-17'):
        for history in booking.history.all():
            data.append([
                history.booking_id,
                history.history_date,
                history.get_history_type_display(),
                history.history_user.profile.name if history.history_user else '',
                history.charged_weight
            ])


def outward_payment_supplier():
    data = []
    for payment in OutWardPayment.objects.filter(paid_to__istartswith='New Visakha Road Lines').filter(
            payment_date__gte='2018-03-01').order_by('-payment_date'):
        data.append([
            payment.payment_date.strftime('%d-%b-%Y'),
            payment.paid_to,
            '\n'.join([lr.lr_number for lr in payment.booking_id.last().lr_numbers.all()]),
            '\n'.join([booking.lorry_number for booking in payment.booking_id.all()]),
            payment.actual_amount,
            payment.get_payment_mode_display(),
            payment.remarks,
        ])
    df = pd.DataFrame(data=data, columns=['Date', 'Paid To', 'Lr Number', 'Lorry Number', 'Amount', 'Mode', 'Remarks'])
    df.to_excel('Raipur Kohraput.xlsx', index=False)


def booking_cancel():
    data = []
    for booking in ManualBooking.objects.filter(booking_id__in=['AAHO05936']).order_by(
            '-shipment_date'):
        for history in booking.history.all():
            temp = []
            temp.append(history.history_date)
            temp.append(history.get_history_type_display())
            temp.append(history.history_user.profile.name if history.history_user else '')
            for attr in [field.attname for field in ManualBooking._meta.fields]:
                temp.append(getattr(history, attr))
            data.append(temp)
    df = pd.DataFrame(data=data, columns=['History Date', 'Change Type', 'Changed By'] + [field.attname for field in
                                                                                          ManualBooking._meta.fields])
    df.to_excel('cancelled booking log.xlsx', index=False)


def mb_derived_attribute():
    amount = 0
    for booking in ManualBooking.objects.filter(shipment_date__gte='2017-04-01'):
        if booking.total_amount_to_owner != booking.supplier_amount:
            amount += booking.total_amount_to_owner - booking.supplier_amount


def check_invoice_amount():
    invoice = Invoice.objects.get(invoice_number='TB-STV2445')
    for booking in invoice.bookings.all():
        for payment in booking.inward_booking.all():
            pass


def pending_inward():
    for booking in ManualBooking.objects.all():
        if booking.pendinginwardpaymententry_set.exists() and booking.pendinginwardpaymententry_set.count() == 1:
            if booking.inward_booking.count() == 1:
                inward = booking.inward_booking.last()
                pi = booking.pendinginwardpaymententry_set.last()
                pi.inward_payment.add(inward)


def hirapower():
    data = []
    for booking in ManualBooking.objects.filter(
            Q(company_id__in=[55, 191]) | Q(customer_to_be_billed_to_id__in=[55, 191])).exclude(
        booking_status__iexact='cancelled'):
        if booking.total_amount_to_company > (booking.total_in_ward_amount + booking.tds_deducted_amount):
            data.append([
                booking.booking_id,
                '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                booking.shipment_date,
                booking.company.get_name() if booking.company else '',
                booking.customer_to_be_billed_to.get_name() if booking.customer_to_be_billed_to else '',
                booking.invoice_number,
                booking.total_amount_to_company,
                booking.total_in_ward_amount
            ])
    df = pd.DataFrame(data=data,
                      columns=['Booking ID', 'LR Number', 'Shipment Data', 'Customer who placed order',
                               'Customer who will make payment',
                               'Invoice Number', 'Total Amount to Company', 'Total Inward Amount'])
    df.to_excel('hpr_hpb_pending_payment.xlsx')


def prakash_industries_ded():
    df = pd.read_excel('../../data/Prakash shortage deductions.xlsx')
    data = []
    for i, row in df.iterrows():
        booking = ManualBooking.objects.get(booking_id=row['Booking ID'])
        data.append([
            booking.booking_id,
            booking.other_deduction,
            booking.remarks_about_deduction
        ])
    df = pd.DataFrame(data=data, columns=['Booking ID', 'Addition to Other Deduction for Supplier',
                                          'Addition to Remarks for Other Deductions'])
    df.to_excel('New Prakash shortage deductions.xlsx')


def update_prakash_deduction():
    df = pd.read_excel('../../data/Prakash shortage deductions.xlsx')
    for i, row in df.iterrows():
        booking = ManualBooking.objects.get(booking_id=row['Booking ID'])
        booking.total_amount_to_owner = booking.supplier_rate * booking.supplier_charged_weight + booking.loading_charge + booking.unloading_charge + booking.detention_charge + booking.additional_charges_for_owner - booking.lr_cost - booking.commission - booking.deduction_for_advance - booking.deduction_for_balance - booking.other_deduction
        booking.save()


def cancelled_booking_payment():
    data = []
    for booking in ManualBooking.objects.filter(booking_status='cancelled'):
        if booking.outward_booking.exists():
            for payment in booking.outward_booking.all():
                data.append([
                    payment.id,
                    payment.payment_date,
                    booking.lorry_number,
                    booking.booking_id,
                    payment.paid_to,
                    payment.actual_amount,
                    payment.get_payment_mode_display()
                ])

    df = pd.DataFrame(data=data,
                      columns=['Payment ID', 'Date', 'Lorry Number', 'Booking_id', 'Paid To', 'Actual Amount',
                               'Payment Mode'])
    df.to_excel('outward payments which belong to cancelled bookings.xlsx', index=False)


def fix_for_iot_bookings():
    df = pd.read_excel('../../data/Changes to IOT Bookings.xlsx')
    for i, row in df.iterrows():
        booking = ManualBooking.objects.get(booking_id=row['Booking ID'])
        Invoice.objects.filter(bookings=booking).delete()
        booking.party_rate = row['Party Rate']
        booking.invoice_status = 'no_invoice'
        booking.customer_to_be_billed_to = Sme.objects.get(id=499)
        booking.to_be_billed_to = 'New Era Alkaloids And Exports Ltd'
        booking.billing_address = None
        booking.billing_invoice_date = None
        booking.save()
        booking.total_amount_to_company = booking.charged_weight * booking.party_rate + booking.additional_charges_for_company - booking.deductions_for_company
        booking.save()


def amount_diff_inward_payment():
    data = []
    for booking in ManualBooking.objects.filter(total_amount_to_company__gt=0):
        if 0 < booking.total_amount_to_company - (booking.total_in_ward_amount + booking.tds_deducted_amount) < 10:
            booking.total_in_ward_amount = booking.total_in_ward_amount + (
                    booking.total_amount_to_company - (booking.total_in_ward_amount + booking.tds_deducted_amount))
            booking.save()
    #         data.append([
    #             booking.id,
    #             booking.booking_id,
    #             booking.total_amount_to_company,
    #             booking.total_in_ward_amount,
    #             booking.tds_deducted_amount,
    #             booking.total_amount_to_company - (booking.total_in_ward_amount + booking.tds_deducted_amount),
    #             sum(booking.inward_booking.values_list('actual_amount', flat=True)),
    #             sum(booking.inward_booking.values_list('tds', flat=True)),
    #
    #         ])
    # df = pd.DataFrame(data=data,
    #                   columns=['ID', 'Booking ID', 'Total Amount to Customer', 'Total Inward Amount', 'Total TDS',
    #                            'Amount Diff', 'Inward table entry amount', 'Inward table entry tds'])
    # df.to_excel('Less amount diff for inward payment.xlsx', index=False)


def delete_duplicate_invoice():
    df = pd.read_excel('../../data/duplicate invoies to Delete.xlsx')
    for i, row in df.iterrows():
        invoice = Invoice.objects.get(invoice_number=row['Delete This Invoices'])
        DeletedData.objects.create(model='invoice', data=json.loads(
            serializers.serialize(format='json', queryset=Invoice.objects.filter(id=invoice.id),
                                  use_natural_foreign_keys=True).strip("[]")))
        try:
            for booking in invoice.bookings.all():
                booking.invoice_status = 'no_invoice'
                booking.to_be_billed_to = None
                booking.invoice_number = None
                booking.billing_invoice_date = None
                booking.save()
                Invoice.objects.filter(id=invoice.id).delete()
        except:
            Invoice.objects.filter(id=invoice.id).delete()


def create_invoice():
    df = pd.read_excel('../../data/idl/Invoice Apr 1-20 Revised on 180505.xlsx')
    lrs = LrNumber.objects.filter(lr_number__in=list(df['id']))
    bookings = ManualBooking.objects.filter(id__in=lrs.values_list('booking__id', flat=True))

    company_name = 'IDL Explosives Ltd - Kukatpally'
    address = 'GOCL Corporation Ltd, IDL Road, Opp. Metro Cash & Carry, Kukatpally, Hyderabad - 18'
    date = '2018-05-31'
    invoice_number = 'AH/IDL/1804004A'
    sme = Sme.objects.get(id=399)
    pin = None
    city = City.objects.get(id=779)
    invoice = Invoice.objects.create(
        invoice_number=invoice_number,
        date=date,
        company_name=company_name,
        customer_fk=sme,
        address=address,
        gstin='37AACCI4429C3ZS',
        city=city,
        pin=pin,
        total_amount=3756,
        advance_payment=0,
        remarks=None,
        service_tax_paid_by='consignor',
        created_by=User.objects.get(id=161),
        changed_by=User.objects.get(id=161),
        summary_required=False,
        s3_upload=S3Upload.objects.get(id=44374)
    )
    for booking in bookings:
        invoice.bookings.add(booking)
        booking.to_be_billed_to = company_name
        booking.billing_address = address
        booking.invoice_number = invoice_number
        booking.billing_invoice_date = date
        booking.customer_to_be_billed_to = sme
        booking.invoice_status = 'invoice_sent'
        booking.save()


def prepare_test_environment():
    emp = Employee.objects.get(id=66)
    for task in TaskEmail.objects.all():
        task.employee.clear()
        task.employee.add(emp)
    user = User.objects.get(id=2926)
    Broker.objects.filter(name=User.objects.get(username='roku')).update(name=user)


def excess_supplier_payment():
    for booking in ManualBooking.objects.exclude(outward_payment_status='no_payment_made'):
        if to_int(booking.total_amount_to_owner) < to_int(
                sum(booking.outward_booking.exclude(is_refund_amount=True).values_list('actual_amount', flat=True))):
            pass


def check_booking_status():
    for booking in ManualBooking.objects.order_by('shipment_date'):
        if booking.balance_for_supplier == 0 and booking.outward_payment_status != 'complete':
            print(booking.booking_status, booking.outward_booking.all())
            print(booking.total_amount_to_owner,
                  sum(booking.outward_booking.exclude(is_refund_amount=True).values_list('actual_amount', flat=True)),
                  booking.booking_id)


def sync_invoice_booking():
    for booking in ManualBooking.objects.all():
        if booking.invoices.exists() and booking.invoice_status == 'no_invoice':
            invoice = booking.invoices.last()
            booking.invoice_status = 'invoice_raised'
            booking.invoice_number = invoice.invoice_number
            # booking.customer_to_be_billed_to=invoice
            booking.to_be_billed_to = invoice.company_name
            booking.billing_invoice_date = invoice.date
            booking.billing_address = invoice.address
            booking.save()


def update_invoice():
    invoice = Invoice.objects.get(id=4790)
    for booking in invoice.bookings.all():
        booking.invoice_number = invoice.invoice_number
        booking.save()


def change_fuel_card_date():
    df = pd.read_excel('/Users/mani/Downloads/Date change on dashboard for fuel card.xlsx')
    for i, row in df.iterrows():
        OutWardPayment.objects.filter(id=row['ID']).update(payment_date=row['Date to change'])


def cnc_data():
    data = []
    for cnc in CreditNoteCustomer.objects.exclude(deleted=True):
        data.append([
            cnc.id,
            cnc.credit_note_number,
            cnc.customer_name,
            cnc.booking_list,
            cnc.invoice_number,
            cnc.credit_amount,
            cnc.adjusted_amount,
            cnc.created_by_user,
            cnc.created_on,
            cnc.adjusted_by_user,
            cnc.adjusted_on,
            cnc.approved_by_user,
            cnc.approved_on,
            cnc.remarks,
            cnc.get_status_display()
        ])
    df = pd.DataFrame(data=data, columns=['ID', 'Credit Note Number', 'Customer Name', 'Bookings', 'Invoice Number',
                                          'Credit Amount', 'Adjusted Amount', 'Issued By', 'Issued On', 'Adjusted By',
                                          'Adjusted On', 'Approved By', 'Approved On', 'Remarks', 'Status'])
    df.to_excel('credit_note_customer.xlsx', index=False)


def color_code_update_for_booking():
    for booking in ManualBooking.objects.order_by('-id'):
        print(booking.id, booking.booking_id, booking.shipment_date)
        try:
            booking.save()
        except:
            print(booking.booking_id, booking.shipment_date)


def manual_booking_data():
    queryset = ManualBooking.objects.filter(shipment_date__gte='2018-04-01').exclude(
        booking_status='cancelled').order_by('-id')
    columns = [field.verbose_name for field in ManualBooking._meta.fields]
    data = []
    for obj in queryset:
        print(obj, obj.shipment_date)
        row = [smart_str(getattr(obj, field.name)) for field in ManualBooking._meta.fields]
        data.append(row)
    df = pd.DataFrame(data=data, columns=columns)
    df.to_excel('Booking Data 2018-04-01 to 2018-10-03.xlsx', index=False)


def clean_chiripal_invoices():
    for invoice in Invoice.objects.filter(customer_fk_id=65).filter(payment_received=True):
        amount = 0
        for booking in invoice.bookings.all():
            amount += booking.balance_for_customer
            if invoice.invoice_number == '002':
                print(booking.booking_id, booking.balance_for_customer)
        if amount < 10:
            pass
            # print(invoice,amount)


def delete_outward_payment():
    df = pd.read_excel('/Users/mani/Downloads/Outward Payments Thu, Oct 4, 2018, 857 PM.xlsx')
    for i, row in df.iterrows():
        obj = OutWardPayment.objects.filter(id=row['ID'])
        print(row['ID'], obj)
        # for value in obj:
        #     try:
        #         for booking in value.booking_id.all():
        #             outward_amount = sum(
        #                 booking.outward_booking.values_list('actual_amount', flat=True))
        #             booking.total_out_ward_amount = outward_amount
        #             if outward_amount <= 0:
        #                 booking.outward_payment_status = 'no_payment_made'
        #             booking.save()
        #         value.delete()
        #     except Exception as e:

        #         raise e


def mismatch_supplier():
    for booking in ManualBooking.objects.order_by('-id'):
        if booking.supplier:
            if booking.truck_broker_owner_name != booking.supplier.get_name():
                booking.truck_broker_owner_name = booking.supplier.get_name()
                booking.truck_broker_owner_phone = booking.supplier.get_phone()
                booking.save()
                print(booking.booking_id, booking.truck_broker_owner_name, booking.supplier.get_name())


def create_lr_s3_upload_object():
    for lr in LrNumber.objects.order_by('id'):
        s3_files = S3Upload.objects.filter(filename='{}.pdf'.format(lr.lr_number)).order_by('-id')
        if s3_files.exists():
            valid_file = s3_files[:1][0]
            invalid_file = s3_files[1:]
            print(valid_file)
            LrS3Upload.objects.create(lr_number=lr, s3_upload=valid_file, is_valid=True)
            for f in invalid_file:
                LrS3Upload.objects.create(lr_number=lr, s3_upload=f, is_valid=False)


def get_lr_zipfile_name(booking):
    lr = booking.lr_numbers.all()
    if lr.count() == 0:
        return None
    if lr.count() == 1:
        return '{}.zip'.format(lr.last().lr_number.lower())
    else:
        return '{}.zip'.format('_'.join([lr.first().lr_number] + [value.lr_number[-3:] for value in lr[1:]]).lower())


def create_booking_s3_upload():
    for booking in ManualBooking.objects.exclude(lr_numbers=None):
        zip_filename = get_lr_zipfile_name(booking)
        s3_files = S3Upload.objects.filter(filename__iexact=zip_filename).order_by('-id')
        if not ManualBookingS3Upload.objects.filter(booking=booking).exists() and s3_files.exists():
            valid_file = s3_files[:1][0]
            print(valid_file)
            ManualBookingS3Upload.objects.create(booking=booking, s3_upload=valid_file, is_valid=True)
            for f in s3_files[1:]:
                ManualBookingS3Upload.objects.create(booking=booking, s3_upload=f, is_valid=False)


def invoices_data_tejas():
    data = []
    for invoice in Invoice.objects.filter(date__gte='2018-04-01'):
        if invoice.bookings.count() == 1:
            data.append([
                invoice.date,
                invoice.invoice_number,
                invoice.customer_fk.get_name() if invoice.customer_fk else None,
                '\n'.join(invoice.bookings.values_list('booking_id', flat=True)),
                '\n'.join(invoice.bookings.last().lr_numbers.values_list('lr_number', flat=True)),
                sum([booking.customer_amount for booking in invoice.bookings.all()[:1]]),
                invoice.total_amount
            ])
        elif invoice.bookings.count() > 1:
            data.append([
                invoice.date,
                invoice.invoice_number,
                invoice.customer_fk.get_name() if invoice.customer_fk else None,
                '\n'.join(invoice.bookings.all()[:1].values_list('booking_id', flat=True)),
                '\n'.join(['\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in
                           invoice.bookings.all()[:1]]),
                sum([booking.customer_amount for booking in invoice.bookings.all()[:1]]),
                invoice.total_amount
            ])
            for booking in invoice.bookings.all()[1:]:
                data.append([
                    '',
                    '',
                    '',
                    booking.booking_id,
                    '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                    booking.customer_amount,
                    ''
                ])
    df = pd.DataFrame(data=data,
                      columns=['Date', 'Invoice Number', 'Customer', 'Booking', 'Lr Number', 'Booking Amount',
                               'Invoice Amount'])
    df.to_excel('Invoices Data.xlsx', index=False)


def extra_booking_charges_tejas():
    data = []
    bookings = ManualBooking.objects.filter(
        Q(additional_charges_for_company__gt=0) | Q(deductions_for_company__gt=0) | Q(
            advance_amount_from_company__gt=0)).filter(shipment_date__gt='2018-01-01').exclude(
        booking_status='cancelled')
    for invoice in Invoice.objects.filter(date__gte='2018-04-01'):
        if invoice.bookings.count() == 1:
            booking = invoice.bookings.last()
            data.append([
                invoice.date,
                invoice.invoice_number,
                invoice.customer_fk.get_name() if invoice.customer_fk else None,
                booking.booking_id,
                '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                booking.total_amount_to_company,
                invoice.total_amount,
                booking.additional_charges_for_company,
                booking.deductions_for_company,
                booking.advance_amount_from_company
            ])
        elif invoice.bookings.count() > 1:
            booking = invoice.bookings.all()[0]
            data.append([
                invoice.date,
                invoice.invoice_number,
                invoice.customer_fk.get_name() if invoice.customer_fk else None,
                '\n'.join(invoice.bookings.all()[:1].values_list('booking_id', flat=True)),
                '\n'.join(['\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)) for booking in
                           invoice.bookings.all()[:1]]),
                sum([booking.customer_amount for booking in invoice.bookings.all()[:1]]),
                invoice.total_amount,
                booking.additional_charges_for_company,
                booking.deductions_for_company,
                booking.advance_amount_from_company
            ])
            for booking in invoice.bookings.all()[1:]:
                data.append([
                    '',
                    '',
                    '',
                    booking.booking_id,
                    '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                    booking.customer_amount,
                    '',
                    booking.additional_charges_for_company,
                    booking.deductions_for_company,
                    booking.advance_amount_from_company
                ])
    df = pd.DataFrame(data=data,
                      columns=['Date', 'Invoice Number', 'Customer', 'Booking', 'Lr Number', 'Booking Amount',
                               'Invoice Amount',
                               'Additional Charges', 'Deductions', 'Advance'])
    df.to_excel('Invoices with extra charges Data.xlsx', index=False)


def raipur_broker_data():
    data = []
    suppliers = ManualBooking.objects.filter(source_office_id=2).exclude(supplier=None).values_list('supplier_id',
                                                                                                    flat=True)
    for broker in Broker.objects.filter(id__in=list(set(suppliers))):
        data.append([broker.get_name(), broker.get_phone(), broker.get_alt_phone(),
                     broker.team_booking_broker.exclude(booking_status='cancelled').count()])
    df = pd.DataFrame(data=data, columns=['Name', 'Phone', 'Alt Phone', 'Number of Bookings'])
    df.to_excel('Raipur Suppliers.xlsx', index=False)


def reconcile_outward_payment():
    df = pd.read_excel('/Users/mani/Downloads/HDFC Bank Statement 29th To 31st Oct 2018.xlsx')
    print(df)
    for i, row in df.iterrows():
        narration = row['Narration']
        if narration[-8:-6] == 'OW':
            payment = get_or_none(OutWardPayment, id=narration[-5:])
            if isinstance(payment, OutWardPayment):
                payment.status = 'reconciled'
                payment.utr = row['Chq./Ref.No.']
                payment.save()
                print(payment)


def settle_girija_satvik():
    pass


def generate_invoice_satvik_girija():
    from restapi.serializers.team import InvoiceSerializer
    df = pd.read_excel('/Users/mani/Downloads/satvik.xlsm')
    for i, row in df.iterrows():
        booking = ManualBooking.objects.get(booking_id=row['Booking No'])
        sme = Sme.objects.get(name__profile__name=row['Company Name'])
        data = {
            'invoice_number': row['Invoice No'],
            'bookings': [booking.id],
            'date': row['Invoice Date'].date(),
            'company_name': row['Company Name'],
            'customer_fk': sme.id,
            'address': row['Address'],
            'pin': row['pin'],
            'city': row['City'],
            'total_amount': to_int(row['Invoice Amt']),
            'created_by': 'mani@aaho.in',
            'changed_by': 'mani@aaho.in',
            'gstin': None,
            'service_tax_paid_by': None,
            'service_tax_aaho': 0,
            's3_upload': None
        }
        invoice_serializer = InvoiceSerializer(data=data)
        if invoice_serializer.is_valid():
            invoice_serializer.save()
        print(invoice_serializer.errors)


def upload_invoice_docs():
    name = 'AHIDR18075046'
    content = open('../../data/{}.pdf'.format(name), 'rb')
    filename = '{}.pdf'.format(slugify('AHIDR18075046'))
    save_to_s3_invoice(filename=filename, content=content)


def upload_invoice_docs_satvik():
    from os import listdir
    from os.path import isfile, join
    mypath = '/Users/mani/Downloads/Girija Invoices'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for inv in onlyfiles:
        invoice = Invoice.objects.get(invoice_number=inv[-14:-4])
        print(invoice)
        content = open('/Users/mani/Downloads/Girija Invoices/{}'.format(inv), 'rb')
        filename = '{}.pdf'.format(slugify(invoice.invoice_number))
        s3 = save_to_s3_invoice(filename=filename, content=content)
        invoice.s3_upload = s3
        invoice.save()


def outward_payment_status(booking):
    if isinstance(booking, ManualBooking):
        if to_int(booking.amount_paid_to_supplier) == 0:
            return 'no_payment_made'
        elif 0 < to_int(booking.amount_paid_to_supplier) < to_int(booking.supplier_amount):
            return 'partial'
        elif to_int(booking.amount_paid_to_supplier) == to_int(booking.supplier_amount):
            return 'complete'
        elif to_int(booking.amount_paid_to_supplier) > to_int(booking.supplier_amount):
            return 'excess'
        else:
            return None
    return None


def check_rounding_customer_amount():
    data = []
    for booking in ManualBooking.objects.exclude(booking_status='cancelled').order_by('-id'):
        if -2 < booking.balance_for_customer < 2 and booking.balance_for_customer != 0:
            print(booking.booking_id, booking.shipment_date)
            data.append([
                booking.id,
                booking.booking_id,
                booking.shipment_date,
                booking.company.get_name() if booking.company else None,
                booking.customer_to_be_billed_to.get_name() if booking.customer_to_be_billed_to else None,
                booking.charged_weight,
                booking.party_rate,
                booking.additional_charges_for_company,
                booking.invoice_remarks_for_additional_charges,
                booking.deductions_for_company,
                booking.invoice_remarks_for_deduction_discount,
                booking.total_amount_to_company,
                booking.customer_amount,
                booking.inward_amount,
                booking.tds_amount_customer,
                booking.credit_amount_customer,
                booking.debit_amount_customer,
                booking.balance_for_customer
            ])
    df = pd.DataFrame(data=data, columns=['ID', 'Booking ID', 'Shipment Date', 'Customer Who Placed order',
                                          'Customer Who will Make Payment', 'Party Charged Weight', 'Party rate',
                                          'Additional Charge', 'Additional Charge Amount', 'Deductions',
                                          'Deduction Remarks', 'Total Amount', 'customer_amount', 'Total Inward Amount',
                                          'Total TDS Amount', 'Credit Amount', 'Debit Amount',
                                          'Customer Balance Amount'])
    df.to_excel('Customers rounding balance amount.xlsx', index=False)


def check_rounding_supplier_amount():
    data = []
    for booking in ManualBooking.objects.exclude(booking_status='cancelled').order_by('-id'):
        if -20 < booking.balance_for_supplier < 20 and booking.balance_for_supplier != 0:
            data.append([
                booking.id,
                booking.shipment_date,
                booking.booking_id,
                booking.lorry_number,
                booking.truck_broker_owner_name,
                booking.truck_broker_owner_phone,
                booking.supplier_charged_weight,
                booking.supplier_rate,
                booking.loading_charge,
                booking.unloading_charge,
                booking.detention_charge,
                booking.additional_charges_for_owner,
                booking.note_for_additional_owner_charges,
                booking.commission,
                booking.lr_cost,
                booking.deduction_for_advance,
                booking.deduction_for_balance,
                booking.other_deduction,
                booking.remarks_about_deduction,
                booking.total_amount_to_owner,
                booking.supplier_amount,
                booking.outward_amount,
                booking.credit_amount_supplier,
                booking.debit_amount_supplier,
                booking.balance_for_supplier,
            ])
    df = pd.DataFrame(data=data,
                      columns=['ID', 'Shipment Date', 'Booking ID', 'Vehicle Number', 'Supplier name', 'Supplier Phone',
                               'Weight', 'Rate', 'Loading Charge', 'Unloading Charge', 'Detention Charge',
                               'Additional Charge', 'Additional Charge Remarks', 'Commission', 'Lr Cost',
                               'Deduction for advance', 'deduction for balance', 'Other Deduction',
                               'Deduction Remarks', 'Total Amount', 'Supplier Amount', 'Outward Amount',
                               'Credit Amount', 'Debit Amount', 'Balance'])
    df.to_excel('supplier amount.xlsx', index=False)


def create_new_username_fms():
    data = []
    df = pd.read_excel('/Users/mani/Downloads/UPDATED LIST.xlsx')
    for i, row in df.iterrows():
        user = User.objects.get(id=row['User ID'])
        data.append([
            user.id,
            user.profile.name,
            user.username,
            row['New Password'],
            user.profile.phone
        ])
    df1 = pd.DataFrame(data=data, columns=['id', 'name', 'username', 'password', 'phone'])
    df1.to_excel('fms_users.xlsx', index=False)


def create_cnc():
    df = pd.read_excel('/Users/mani/Downloads/Customers rounding balance amount.xlsx')
    for i, row in df.iterrows():
        if row['Customer Balance Amount'] == -1:
            booking = ManualBooking.objects.get(id=row['ID'])
            sme = Sme.objects.get(name__profile__name=row['Customer Who will Make Payment'])
            # cnc=CreditNoteCustomer.objects.create(
            #     credit_note_number=generate_credit_note_customer_serial_number(sme_id=sme.id),
            #     credit_amount=1,
            #     adjusted_amount=1,
            #     adjusted_by=User.objects.get(username='mani@aaho.in'),
            #     approved_by=User.objects.get(username='mani@aaho.in'),
            #     created_by=User.objects.get(username='mani@aaho.in'),
            #     changed_by=User.objects.get(username='mani@aaho.in'),
            #     approved_on=datetime.now(),
            #     adjusted_on=datetime.now(),
            #     reason=CreditDebitNoteReason.objects.get(id=4),
            #     remarks="round off adjustment",
            #     customer=sme,
            #     status='adjusted'
            # )
            # cnc.bookings.add(booking)
            dnc = DebitNoteCustomer.objects.create(
                debit_note_number=generate_debit_note_customer_serial_number(sme_id=sme.id),
                debit_amount=1,
                adjusted_amount=1,
                adjusted_by=User.objects.get(username='mani@aaho.in'),
                approved_by=User.objects.get(username='mani@aaho.in'),
                created_by=User.objects.get(username='mani@aaho.in'),
                changed_by=User.objects.get(username='mani@aaho.in'),
                approved_on=datetime.now(),
                adjusted_on=datetime.now(),
                reason=CreditDebitNoteReason.objects.get(id=4),
                remarks="round off adjustment",
                customer=sme,
                status='adjusted'
            )
            dnc.bookings.add(booking)


def create_dnc():
    df = pd.read_excel('/Users/mani/Downloads/supplier amount.xlsx')
    for i, row in df.iterrows():
        broker = Broker.objects.filter(name__profile__name=row['Supplier name']).last()
        print(broker)
        booking = ManualBooking.objects.get(id=row['ID'])
        dnc = DebitNoteSupplier.objects.create(
            debit_note_number=generate_debit_note_supplier_serial_number(broker_id=broker.id) if broker else 1000000,
            debit_amount=1,
            adjusted_amount=1,
            adjusted_by=User.objects.get(username='mani@aaho.in'),
            approved_by=User.objects.get(username='mani@aaho.in'),
            created_by=User.objects.get(username='mani@aaho.in'),
            changed_by=User.objects.get(username='mani@aaho.in'),
            approved_on=datetime.now(),
            adjusted_on=datetime.now(),
            reason=CreditDebitNoteReason.objects.get(id=4),
            remarks="round off adjustment",
            broker=broker,
            status='adjusted'
        )
        dnc.bookings.add(booking)


def check_wrong_invoice_payment_recieved_status():
    print(sum([invoice.invoice_balance for invoice in Invoice.objects.filter(customer_fk_id=65)]))
    # for booking in ManualBooking.objects.filter(company__company_code='CRP'):
    #     if booking.balance_for_customer != 0:
    #         print(booking.booking_id,booking.balance_for_customer )

    for invoice in Invoice.objects.filter(customer_fk_id=65):
        print(invoice, invoice.invoice_balance)


def invoices_without_customer_fk():
    data = []
    for invoice in Invoice.objects.filter(customer_fk=None).order_by('-date'):
        data.append([
            invoice.id,
            invoice.date,
            invoice.invoice_number,
            invoice.company_name
        ])
    df = pd.DataFrame(data=data, columns=['id', 'date', 'invoice number', 'customer'])
    df.to_excel('invoices_without_customer_fk.xlsx', index=False)


def booking_with_wrong_invoice_status():
    for booking in ManualBooking.objects.all():
        if booking.invoices.exists() and booking.invoice_status == 'no_invoice':
            print(booking)



def fuel_card_last_payment():
    data=[]
    for card in FuelCard.objects.all():
        if card.outwardpayment_set.exists():
            data.append([
                card.card_number,
                card.outwardpayment_set.latest('payment_date').payment_date
            ])
    df=pd.DataFrame(data=data,columns=['Card number','Last Payment Date'])
    df.to_excel('card payments.xlsx',index=False)