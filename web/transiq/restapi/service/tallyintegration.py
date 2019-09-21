from datetime import timedelta, datetime
from io import BytesIO

import pandas as pd
from django.conf import settings
from django.core.mail import EmailMessage

from api.s3util import save_to_s3_tally_integration
from api.utils import to_int
from employee.models import TaskEmail
from team.models import OutWardPayment


def cash_payments():
    payment_date = (datetime.now() - timedelta(days=1))
    payments = OutWardPayment.objects.filter(payment_mode='cash',
                                             created_on__date=payment_date.date()).exclude(
        deleted=True).order_by('-id')
    data = []

    for payment in payments:
        data.append([
            'OW{}'.format(payment.id),
            payment.payment_date,
            'Payment',
            'Outward Payment - Cash (OW)',
            'CP{}OW{}'.format(payment_date.strftime('%y%m'), payment.id),
            payment.paid_to,
            to_int(payment.actual_amount),
            payment.bookings,
            to_int(payment.actual_amount),
            'New Ref',
            'Cash - {}'.format(payment.aaho_office.branch_name if payment.aaho_office else ''),
            to_int(payment.actual_amount),
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            'Being cash paid towards Lorry No {}, LR  No {}, & Aaho ID {}'.format(payment.vehicle_number,
                                                                                  payment.lr_numbers, payment.bookings),
            '',
            '',
            '',
            '',
            '',
            '',
        ])
    df = pd.DataFrame(data=data,
                      columns=['UNIQUEID', 'DATE', 'BASE VCH-TYPE', 'VOUCHER TYPE', 'VCH.NO', 'PARTY NAME', 'AMOUNT',
                               'REFERENCE NO', 'REFERENCE AMT', 'REFERENCE TYPE', 'CASH or BANK LEDGER', 'AMOUNT',
                               'Ledger1Name', 'Ledger1Amt', 'Ledger2Name', 'Ledger2Amt', 'Ledger3Name', 'Ledger3Amt',
                               'Ledger4Name',
                               'Ledger4Amt', 'Ledger5Name', 'Ledger5Amt', 'NARRATION', 'INSTRUMENT NO',
                               'INSTRUMENT DATE', 'TRANSACTION-TYPE', 'FAVOURING', 'CHEQUECROSSCOMMENT', 'BANKDATE'
                               ])
    byte_io = BytesIO()

    # Use the BytesIO object as the filehandle.
    writer = pd.ExcelWriter(byte_io, engine='xlsxwriter')

    # Write the data frame to the BytesIO object.
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    worksheet = writer.sheets['Sheet1']
    worksheet.write_comment('A1',
                            '<XMLTAGSFILENAME>Vouchers-V6-Receipts-and-Payments-with-multiple-references-xml-tags.xml</XMLTAGSFILENAME>')
    writer.save()
    content = byte_io.getvalue() or '\n'
    s3_upload = save_to_s3_tally_integration(
        'tally_upload_cash_outward_payment_entry_{}.xlsx'.format(payment_date.strftime('%y%m%d%I%M')), content)
    subject = 'Tally Upload Cash Outward Payment Entry {}'.format(payment_date.strftime('%Y-%b-%d'))
    body = 'PFA'
    email = EmailMessage(subject, body, 'AAHO OUTWARD PAYMENT',
                         to=TaskEmail.objects.filter(id=29).values_list('employee__username__profile__email',
                                                                        flat=True))
    email.attach(filename=s3_upload.filename, content=s3_upload.read(),
                 mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


def bank_transfer_payments(payments):
    # payments = OutWardPayment.objects.filter(payment_date__lte=datetime.now().today()).exclude(
    #     bank_account=None).exclude(status__in=['paid', 'reconciled'])
    data = []
    current_datetime = datetime.now()
    for payment in payments:
        data.append([
            'ZDKRW{}'.format(payment.id),
            payment.payment_date,
            'Payment',
            'Outward Payment - Bank (OW)',
            'BP{}OW{}'.format(payment.payment_date.strftime('%y%m'), payment.id),
            payment.paid_to,
            payment.actual_amount,
            payment.bookings,
            payment.actual_amount,
            'New Ref',
            'HDFC Bank 0769',
            payment.actual_amount,
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            'Being amount paid towards Lorry No {}, LR  No {}, & Aaho ID {}'.format(payment.vehicle_number,
                                                                                    payment.lr_numbers,
                                                                                    payment.bookings),
            'NEFT',
            payment.payment_date,
            'Others',
            '',
            '',
            ''
        ])
    df = pd.DataFrame(data=data,
                      columns=['UNIQUEID', 'DATE', 'BASE VCH-TYPE', 'VOUCHER TYPE', 'VCH.NO', 'PARTY NAME', 'AMOUNT',
                               'REFERENCE NO', 'REFERENCE AMT', 'REFERENCE TYPE', 'CASH or BANK LEDGER', 'AMOUNT',
                               'Ledger1Name', 'Ledger1Amt', 'Ledger2Name', 'Ledger2Amt', 'Ledger3Name', 'Ledger3Amt',
                               'Ledger4Name',
                               'Ledger4Amt', 'Ledger5Name', 'Ledger5Amt', 'NARRATION', 'INSTRUMENT NO',
                               'INSTRUMENT DATE', 'TRANSACTION-TYPE', 'FAVOURING', 'CHEQUECROSSCOMMENT', 'BANKDATE'
                               ])
    byte_io = BytesIO()

    # Use the BytesIO object as the filehandle.
    writer = pd.ExcelWriter(byte_io, engine='xlsxwriter')

    # Write the data frame to the BytesIO object.
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    worksheet = writer.sheets['Sheet1']
    worksheet.write_comment('A1',
                            '<XMLTAGSFILENAME>Vouchers-V6-Receipts-and-Payments-with-multiple-references-xml-tags.xml</XMLTAGSFILENAME>')
    writer.save()
    content = byte_io.getvalue() or '\n'
    s3_upload = save_to_s3_tally_integration(
        'tally_upload_bank_outward_payment_entry_{}.xlsx'.format(current_datetime.strftime('%y%m%d%I%M')), content)
    subject = 'Tally Upload Bank Outward Payment Entry {}'.format(current_datetime.strftime('%Y-%b-%d'))
    body = 'PFA'
    email = EmailMessage(subject, body, 'AAHO OUTWARD PAYMENT',
                         to=TaskEmail.objects.filter(id=27).values_list('employee__username__profile__email',
                                                                        flat=True))
    email.attach(filename=s3_upload.filename, content=s3_upload.read(),
                 mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


def fuel_card_payment():
    current_datetime = datetime.now() - timedelta(days=1)
    payments = OutWardPayment.objects.filter(payment_mode='fuel_card',
                                             created_on__date=current_datetime.date()).exclude(
        deleted=True).order_by('-id')
    if not payments.exists():
        return
    data = []
    for payment in payments:
        fuel_card_provider = 'Bharat Petroleum - Fuel Card' if payment.fuel_card and payment.fuel_card.card_number.startswith(
            'FC') else 'Indian Oil - Fuel Card'
        fuel_card_number = payment.fuel_card.card_number if payment.fuel_card else ''
        data.append([
            'OW{}'.format(payment.id),
            'Journal',
            'Outward Payment - Fuel Card (OW)',
            'JVFC{}OW{}'.format(current_datetime.strftime('%y%m'), payment.id),
            payment.payment_date,
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            payment.paid_to,
            -payment.actual_amount,
            '',
            '',
            payment.bookings,
            -payment.actual_amount,
            'New Ref',
            '',

            fuel_card_provider,
            payment.actual_amount,
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            'Being paid to {} Lorry No. {} Lr No.{} Aaho id. {} from {} No ({})'.format(payment.paid_to,
                                                                                        payment.vehicle_number,
                                                                                        payment.lr_numbers,
                                                                                        payment.bookings,
                                                                                        fuel_card_provider,
                                                                                        fuel_card_number),
            '',
            '',
            '',
            '',
            '',
            '',
            ''
        ])

    df = pd.DataFrame(data=data, columns=['UNIQUE-ID',
                                          'BASE VCH-TYPE',
                                          'VOUCHER-TYPE',
                                          'VCH-NO',
                                          'VCH-DATE',
                                          'REF-NO',
                                          'REF-DATE',
                                          'PARTY NAME',
                                          'AMOUNT',
                                          'COSTCATEGORY',
                                          'COSTCENTRE',
                                          'REFERENCE NO',
                                          'REFERENCE AMT',
                                          'REFERENCE TYPE',
                                          'CREDIT-DAYS',
                                          'CASH or BANK LEDGER',
                                          'AMOUNT.1',
                                          'Ledger1Name',
                                          'Ledger1Amt',
                                          'CostCategory',
                                          'CostCentre',
                                          'Ref No',
                                          'Ref Amt',
                                          'Ref Type',
                                          'Credit-Days',
                                          'Ledger2Name',
                                          'Ledger2Amt',
                                          'CostCategory.1',
                                          'CostCentre.1',
                                          'Ref No.1',
                                          'Ref Amt.1',
                                          'Ref Type.1',
                                          'Credit Days',
                                          'Ledger3Name',
                                          'Ledger3Amt',
                                          'CostCategory.2',
                                          'CostCentre.2',
                                          'Ref No.2',
                                          'Ref Amt.2',
                                          'Ref Type.2',
                                          'Credit Days.1',
                                          'Ledger4Name',
                                          'Ledger4Amt',
                                          'CostCategory.3',
                                          'CostCentre.3',
                                          'Ref No.3',
                                          'Ref Amt.3',
                                          'Ref Type.3',
                                          'Credit Days.2',
                                          'Ledger5Name',
                                          'Ledger5Amt',
                                          'CostCategory.4',
                                          'CostCentre.4',
                                          'Ref No.4',
                                          'Ref Amt.4',
                                          'Ref Type.4',
                                          'Credit Days.3',
                                          'Ledger6Name',
                                          'Ledger6Amt',
                                          'CostCategory.5',
                                          'CostCentre.5',
                                          'Ref No.5',
                                          'Ref Amt.5',
                                          'Ref Type.5',
                                          'Credit Days.4',
                                          'Ledger7Name',
                                          'Ledger7Amt',
                                          'CotCategory',
                                          'CostCentre.6',
                                          'Ref No.6',
                                          'Ref Amt.6',
                                          'Ref Type.6',
                                          'Credit Days.5',
                                          'Ledger8Name',
                                          'Ledger8Amt',
                                          'CostCategory.6',
                                          'CostCentre.7',
                                          'Ref No.7',
                                          'Ref Amt.7',
                                          'Ref Type.7',
                                          'Credit Days.6',
                                          'Ledger9Name',
                                          'Ledger9Amt',
                                          'CostCategory.7',
                                          'CostCentre.8',
                                          'Ref No.8',
                                          'Ref Amt.8',
                                          'Ref Type.8',
                                          'Credit Days.7',
                                          'Ledger10Name',
                                          'Ledger10Amt',
                                          'CostCategory.8',
                                          'CostCentre.9',
                                          'Ref No.9',
                                          'Ref Amt.9',
                                          'Ref Type.9',
                                          'Credit Days.8',
                                          'NARRATION',
                                          'INSTRUMENT NO',
                                          'INSTRUMENT DATE',
                                          'TRANSACTION-TYPE',
                                          'FAVOURING',
                                          'CHEQUECROSSCOMMENT',
                                          'BANKDATE',
                                          'COMPANY-NAME'])
    byte_io = BytesIO()

    # Use the BytesIO object as the filehandle.
    writer = pd.ExcelWriter(byte_io, engine='xlsxwriter')

    # Write the data frame to the BytesIO object.
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    worksheet = writer.sheets['Sheet1']
    worksheet.write_comment('A1',
                            '<XMLTAGSFILENAME>Vouchers-V9-Journal-with-multiple-references-xml-tags.xml</XMLTAGSFILENAME>')
    writer.save()
    content = byte_io.getvalue() or '\n'
    s3_upload = save_to_s3_tally_integration(
        'tally_upload_fuel_outward_payment_entry_{}.xlsx'.format(current_datetime.strftime('%y%m%d%I%M')), content)
    subject = 'Tally Upload Fuel Outward Payment Entry {}'.format(current_datetime.strftime('%Y-%b-%d'))
    body = 'PFA'
    email = EmailMessage(subject, body, 'AAHO OUTWARD PAYMENT',
                         to=TaskEmail.objects.filter(id=28).values_list('employee__username__profile__email',
                                                                        flat=True))
    email.attach(filename=s3_upload.filename, content=s3_upload.read(),
                 mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()
