from datetime import datetime, timedelta, date

from django.contrib.auth.models import User, Group
from django.db.models import Q, F

from api.helper import EMP_GROUP1, EMP_GROUP2
from api.models import S3Upload
from api.utils import to_int, format_inr, get_or_none
from supplier.models import Vehicle
from sme.models import Sme
from supplier.models import Supplier
from team.models import ManualBooking, Invoice
from utils.models import City, AahoOffice

INVOICE_EMAIL_PERIOD = 1
DISPATCH_CUSTOMER_EMAIL_PERIOD = 3


def get_dispatched_customers_list():
    bookings = ManualBooking.objects.filter(
        shipment_date=(datetime.now() - timedelta(days=DISPATCH_CUSTOMER_EMAIL_PERIOD)).date()).exclude(
        booking_status='cancelled')
    customers = list(set(list(bookings.exclude(company=None).values_list('company_id', flat=True)) + list(
        bookings.exclude(customer_to_be_billed_to=None).values_list('customer_to_be_billed_to_id', flat=True))))
    return customers


def get_customers_dispatched_shipment_email_data():
    data = []
    for sme in Sme.objects.filter(id__in=get_dispatched_customers_list()).filter(email_tasks__in=['1']):
        enable_email = False
        bookings = ManualBooking.objects.filter(
            shipment_date=(datetime.now() - timedelta(days=DISPATCH_CUSTOMER_EMAIL_PERIOD)).date()).filter(
            Q(company=sme) | Q(customer_to_be_billed_to=sme)).exclude(booking_status='cancelled')
        booking_data = []
        additional_charge_remarks = []
        count = 0
        email = []
        for booking in bookings:
            if booking.additional_charges_for_company > 0:
                count += 1
                additional_charge_remarks.append(
                    {'id': count, "message": booking.invoice_remarks_for_additional_charges})

            booking_data.append({
                'lr_number': booking.booking_id if not booking.lr_numbers.exists() else '\n'.join(
                    [lr.lr_number for lr in booking.lr_numbers.all()]),
                'vehicle_number': booking.supplier_vehicle.number() if booking.supplier_vehicle else '',
                'from': booking.from_city_fk.name if isinstance(booking.from_city_fk, City) else '',
                'to': booking.to_city_fk.name if isinstance(booking.to_city_fk, City) else '',
                'charged_weight': str(booking.charged_weight),
                'rate': str(booking.party_rate),
                'additional_charge': booking.additional_charges_for_company,
                'customer_freight': booking.customer_freight,
                'additional_charge_superscript': count if booking.additional_charges_for_company > 0 else ''
            })
            if isinstance(booking.company, Sme) and booking.company.sme_email:
                email.append(booking.company.sme_email)
                enable_email = True
            if isinstance(booking.customer_to_be_billed_to, Sme) and booking.customer_to_be_billed_to.sme_email:
                email.append(booking.customer_to_be_billed_to.sme_email)
                enable_email = True
            if isinstance(booking.company, Sme) and booking.company.sme_alt_email:
                email.append(booking.company.sme_alt_email)
                enable_email = True
            if isinstance(booking.customer_to_be_billed_to, Sme) and booking.customer_to_be_billed_to.sme_alt_email:
                email.append(booking.customer_to_be_billed_to.sme_alt_email)
                enable_email = True
            if isinstance(booking.company, Sme) and booking.company.aaho_poc_email:
                email.append(booking.company.aaho_poc_email)
            if isinstance(booking.customer_to_be_billed_to, Sme) and booking.customer_to_be_billed_to.aaho_poc_email:
                email.append(booking.customer_to_be_billed_to.aaho_poc_email)

        data.append(
            {'bookings': booking_data, 'credit_period': to_int(sme.credit_period),
             'additional_charge_remarks': additional_charge_remarks,
             'dispatch_date': (datetime.now() - timedelta(days=DISPATCH_CUSTOMER_EMAIL_PERIOD)).strftime('%d-%b-%Y'),
             'email_id_list': list(set(email)),
             'enable_email': enable_email
             }
        )
    return data


def get_invoice_customers_list():
    invoices = Invoice.objects.filter(
        created_on__date=(datetime.now() - timedelta(days=INVOICE_EMAIL_PERIOD)).date()).exclude(
        deleted=True)
    return list(set(list(invoices.values_list('customer_fk_id', flat=True))))


def get_invoice_customers_email_data():
    data = []

    for sme in Sme.objects.filter(id__in=get_invoice_customers_list()).filter(email_tasks__in=['2']):
        enable_email = False
        invoices_data = []
        number_of_shipment = 0
        invoices = Invoice.objects.filter(
            created_on__date=(datetime.now() - timedelta(days=INVOICE_EMAIL_PERIOD)).date(), customer_fk=sme)
        pod_files = []
        invoices_file = []
        for invoice in invoices:
            number_of_shipment += invoice.bookings.count()
            invoices_data.append({
                'invoice_number': invoice.invoice_number,
                'invoice_date': invoice.date.strftime('%d-%b-%Y') if invoice.date else '',
                'invoice_amount': '{}'.format(format_inr(invoice.total_amount)),
                'due_date': (invoice.date + timedelta(days=to_int(sme.credit_period))).strftime(
                    '%d-%b-%Y') if invoice.date else ''
            })
            if isinstance(invoice.s3_upload, S3Upload):
                invoices_file.append(invoice.s3_upload)
            for booking in invoice.bookings.all():
                for pod in booking.podfile_set.filter(verified=True, is_valid=True).all():
                    if isinstance(pod.s3_upload, S3Upload):
                        pod_files.append(pod.s3_upload)
        email_id_list = []
        if sme.aaho_poc_email:
            email_id_list.append(sme.aaho_poc_email)

        if sme.sme_email:
            enable_email = True
            email_id_list.append(sme.sme_email)
        if sme.sme_alt_email:
            enable_email = True
            email_id_list.append(sme.sme_alt_email)
        data.append({
            'invoices_data': invoices_data,
            'number_of_shipment': number_of_shipment,
            'email_id_list': email_id_list,
            'invoices_file': invoices_file,
            'pod_files': pod_files,
            'credit_period': to_int(sme.credit_period),
            'enable_email': enable_email,
            'invoice_created_on': (datetime.now() - timedelta(days=INVOICE_EMAIL_PERIOD)).strftime('%d-%b-%Y')
        })
    return data


def number_days_old(dt):
    if isinstance(dt, datetime) or isinstance(dt, date):
        return '{} Days'.format((datetime.now().date() - dt).days)
    return ''


def notify_weekly_partial_tbb_data():
    data = []
    for office in AahoOffice.objects.all():
        email_id_list = office.employee_office_multiple.filter(
            username__in=User.objects.filter(
                groups__in=Group.objects.filter(name__in=[EMP_GROUP1, EMP_GROUP2]))).exclude(
            status__iexact='inactive').exclude(username__profile__email=None).values_list(
            'username__profile__email', flat=True)
        bookings = ManualBooking.objects.filter(source_office=office, billing_type='T.B.B.').exclude(
            booking_status='cancelled').order_by('shipment_date')
        booking_data = []
        number_of_open_booking = 0
        number_of_pod_pending = 0
        number_of_pod_received_invoice_not_raised = 0
        number_of_pod_received_outward_payment_pending = 0
        number_of_pod_received_inward_payment_pending = 0
        for booking in bookings:
            if booking.balance_for_customer > 0 or booking.balance_for_supplier != 0:
                if booking.pod_status == 'pending':
                    number_of_pod_pending += 1
                if booking.pod_status == 'completed' and not booking.invoices.exists():
                    number_of_pod_received_invoice_not_raised += 1
                if booking.pod_status == 'completed' and booking.balance_for_supplier > 0:
                    number_of_pod_received_outward_payment_pending += 1
                if booking.pod_status == 'completed' and booking.balance_for_customer > 0:
                    number_of_pod_received_inward_payment_pending += 1
                number_of_open_booking += 1
                booking_data.append({
                    'booking_id': booking.booking_id,
                    'shipment_date': booking.shipment_date.strftime('%d-%b-%Y') if booking.shipment_date else '',
                    'billing_invoice_date': booking.billing_invoice_date.strftime(
                        '%d-%b-%Y') if booking.billing_invoice_date else '',
                    'invoice_age': number_days_old(booking.billing_invoice_date),
                    'lr_number': booking.booking_id if not booking.lr_numbers.exists() else '\n'.join(
                        [lr.lr_number for lr in booking.lr_numbers.all()]),
                    'customer_placed_order': booking.company.get_name() if isinstance(booking.company, Sme) else '',
                    'supplier': booking.truck_broker_owner_name,
                    'pod_status': booking.get_pod_status_display(),
                    'invoice_status': booking.get_invoice_status_display(),
                    'from_city': booking.from_city_fk.name if isinstance(booking.from_city_fk, City) else '',
                    'to_city': booking.to_city_fk.name if isinstance(booking.to_city_fk, City) else '',
                    'vehicle_number': booking.supplier_vehicle.number() if isinstance(booking.supplier_vehicle, Vehicle) else ''
                })
        data.append({
            'number_of_open_booking': number_of_open_booking,
            'number_of_pod_pending': number_of_pod_pending,
            'number_of_pod_received_invoice_not_raised': number_of_pod_received_invoice_not_raised,
            'number_of_pod_received_outward_payment_pending': number_of_pod_received_outward_payment_pending,
            'number_of_pod_received_inward_payment_pending': number_of_pod_received_inward_payment_pending,
            'branch_name': office.branch_name,
            'email_id_list': list(email_id_list),
            'bookings': booking_data
        })
    return data


def notify_admins_about_to_pay_booking_data():
    data = []
    for office in AahoOffice.objects.all():
        email_id_list = office.employee_office_multiple.filter(
            username__in=User.objects.filter(
                groups__in=Group.objects.filter(name__in=[EMP_GROUP1, EMP_GROUP2]))).exclude(
            status__iexact='inactive').exclude(username__profile__email=None).values_list(
            'username__profile__email', flat=True)
        booking_data = []
        number_of_open_booking = 0
        bookings = ManualBooking.objects.filter(
            (Q(source_office=office) | Q(destination_office=office)) & Q(billing_type='To Pay') & Q(
                shipment_date__gte='2017-01-01')).exclude(booking_status='cancelled').order_by('shipment_date')
        for booking in bookings:
            if booking.balance_for_customer > 0:
                number_of_open_booking += 1
                booking_data.append({
                    'booking_id': booking.booking_id,
                    'shipment_date': booking.shipment_date.strftime('%d-%b-%Y') if booking.shipment_date else '',
                    'billing_invoice_date': booking.billing_invoice_date.strftime(
                        '%d-%b-%Y') if booking.billing_invoice_date else '',
                    'invoice_age': number_days_old(booking.billing_invoice_date),
                    'lr_number': booking.booking_id if not booking.lr_numbers.exists() else '\n'.join(
                        [lr.lr_number for lr in booking.lr_numbers.all()]),
                    'customer_placed_order': booking.company.get_name() if isinstance(booking.company, Sme) else '',
                    'total_amount_to_company': booking.total_amount_to_company,
                    'total_in_ward_amount': booking.total_in_ward_amount,
                    'tds_deducted_amount': booking.tds_deducted_amount,
                    'from_city': booking.from_city_fk.name if isinstance(booking.from_city_fk, City) else '',
                    'to_city': booking.to_city_fk.name if isinstance(booking.to_city_fk, City) else '',
                    'vehicle_number': booking.supplier_vehicle.number() if isinstance(booking.supplier_vehicle, Vehicle) else ''
                })
        data.append({'email_id_list': list(email_id_list), 'number_of_open_booking': number_of_open_booking,
                     'bookings': booking_data, 'branch_name': office.branch_name})
    return data


def notify_pod_received_invoice_not_raised_data():
    data = []
    for office in AahoOffice.objects.all():
        bookings = ManualBooking.objects.filter(Q(source_office=office) | Q(destination_office=office)).filter(
            Q(pod_status='completed') & Q(invoice_status='no_invoice')).exclude(booking_status='cancelled')
        booking_data = []
        for booking in bookings:
            booking_data.append({
                'lr_number': booking.booking_id if not booking.lr_numbers.exists() else '\n'.join(
                    [lr.lr_number for lr in booking.lr_numbers.all()]),
                'shipment_date': booking.shipment_date.strftime('%d-%b-%Y') if booking.shipment_date else '',
                'customer_to_be_billed_to': booking.customer_to_be_billed_to.get_name() if isinstance(
                    booking.customer_to_be_billed_to, Sme) else '',
                'from_city': booking.from_city_fk.name if isinstance(booking.from_city_fk, City) else '',
                'to_city': booking.to_city_fk.name if isinstance(booking.to_city_fk, City) else '',
                'vehicle_number': booking.supplier_vehicle.number() if isinstance(booking.supplier_vehicle, Vehicle) else '',
                'total_amount_to_company': booking.total_amount_to_company,
                'pod_date': booking.pod_date.strftime('%d-%b-%Y') if booking.pod_date else ''
            })

    return data


def booking_summary_data(bookings):
    data = {'pending_pod': {'balance': 0, 'amount_paid': 0, 'total_amount': 0, 'number_of_booking': 0},
            'delivered_pod': {'balance': 0, 'amount_paid': 0, 'total_amount': 0, 'number_of_booking': 0},
            'completed_booking': {'total_amount': 0, 'number_of_booking': 0}}
    # PENDING POD
    total_amount = 0
    paid_amount = 0
    balance_amount = 0
    credit_amount = 0
    debit_amount = 0
    adjusted_outward_amount=0
    for booking in bookings.exclude(pod_status='completed'):
        total_amount += booking.fms_supplier_amount
        paid_amount += booking.fms_supplier_paid_amount
        balance_amount += booking.fms_balance_supplier
        credit_amount += booking.credit_amount_supplier
        debit_amount = booking.debit_amount_supplier
        adjusted_outward_amount = booking.adjusted_outward_amount
    data['pending_pod']['balance'] = balance_amount
    data['pending_pod']['amount_paid'] = paid_amount
    data['pending_pod']['total_amount'] = total_amount
    data['pending_pod']['credit_amount'] = credit_amount
    data['pending_pod']['debit_amount'] = debit_amount
    data['pending_pod']['adjusted_outward_amount'] = adjusted_outward_amount
    data['pending_pod']['number_of_booking'] = bookings.exclude(pod_status='completed').count()
    # DELIVERED POD AND INCOMPLETE OUTWARD PAYMENT
    total_amount = 0
    paid_amount = 0
    balance_amount = 0
    credit_amount = 0
    debit_amount = 0
    adjusted_outward_amount=0

    for booking in bookings.filter(pod_status='completed', outward_payment_status__in=['no_payment_made', 'partial']):
        total_amount += booking.fms_supplier_amount
        paid_amount += booking.fms_supplier_paid_amount
        balance_amount += booking.fms_balance_supplier
        credit_amount += booking.credit_amount_supplier
        debit_amount = booking.debit_amount_supplier
        adjusted_outward_amount = booking.adjusted_outward_amount
    data['delivered_pod']['balance'] = balance_amount
    data['delivered_pod']['amount_paid'] = paid_amount
    data['delivered_pod']['total_amount'] = total_amount
    data['delivered_pod']['credit_amount'] = credit_amount
    data['delivered_pod']['debit_amount'] = debit_amount
    data['pending_pod']['adjusted_outward_amount'] = adjusted_outward_amount
    data['delivered_pod']['number_of_booking'] = bookings.filter(pod_status='completed',
                                                                 outward_payment_status__in=['no_payment_made',
                                                                                             'partial']).count()

    # DELIVERED POD AND COMPLETE OUTWARD PAYMENT
    total_amount = 0

    for booking in bookings.filter(outward_payment_status__in=['complete', 'excess']):
        total_amount += booking.fms_supplier_amount
    data['completed_booking']['total_amount'] = total_amount
    data['completed_booking']['number_of_booking'] = bookings.filter(
        outward_payment_status__in=['complete', 'excess']).count()

    return data


def supplier_booking_summary_data(user_id=None):
    data = {'pending_pod': {'balance': 0, 'amount_paid': 0, 'total_amount': 0, 'number_of_booking': 0},
            'delivered_pod': {'balance': 0, 'amount_paid': 0, 'total_amount': 0, 'number_of_booking': 0},
            'completed_booking': {'total_amount': 0, 'number_of_booking': 0}}
    supplier = get_or_none(Supplier, user_id=user_id)
    if not isinstance(supplier, Supplier):
        return data
    if isinstance(supplier, Supplier):
        bookings = ManualBooking.objects.filter(booking_supplier=supplier, shipment_date__gte='2017-12-01').exclude(
            Q(booking_status='cancelled') | Q(deleted=True))
    else:
        bookings = ManualBooking.objects.none()
    return booking_summary_data(bookings)


def vehicle_booking_summary_data(user_id=None, vehicle_id=None):
    data = {'pending_pod': {'balance': 0, 'amount_paid': 0, 'total_amount': 0, 'number_of_booking': 0},
            'delivered_pod': {'balance': 0, 'amount_paid': 0, 'total_amount': 0, 'number_of_booking': 0},
            'completed_booking': {'total_amount': 0, 'number_of_booking': 0}}
    supplier = get_or_none(Supplier, user_id=user_id)
    vehicle = get_or_none(Vehicle, id=vehicle_id)
    if not isinstance(supplier, Supplier) and not isinstance(vehicle, Vehicle):
        return data
    if isinstance(vehicle, Vehicle):
        bookings = ManualBooking.objects.filter(booking_supplier=supplier, supplier_vehicle=vehicle,
                                                shipment_date__gte='2017-12-01').exclude(
            Q(booking_status='cancelled') | Q(deleted=True))
    else:
        bookings = ManualBooking.objects.none()
    return booking_summary_data(bookings)


def notify_excess_outward_payment_data(bookings):
    data = []
    for booking in bookings:
        if booking.balance_for_supplier < -1:
            data.append({
                'shipment_date': booking.shipment_date.strftime('%d-%b-%Y') if booking.shipment_date else '-',
                'booking_id': booking.booking_id,
                'lr_numbers': '\n'.join(lr.lr_number for lr in booking.lr_numbers.all()),
                'supplier_name': booking.supplier.get_name() if booking.supplier else booking.truck_broker_owner_name,
                'from_city': booking.from_city_fk.name if booking.from_city_fk else '-',
                'to_city': booking.to_city_fk.name if booking.to_city_fk else '-',
                'vehicle_number': booking.vehicle_number,
                'total_amount': booking.supplier_amount,
                'paid_amount': booking.amount_paid_to_supplier,
                'balance': booking.balance_for_supplier
            })
    return data


def notify_excess_outward_payment_email_id():
    from restapi.models import EmployeeRolesMapping
    emp = list(set(list(
        EmployeeRolesMapping.objects.filter(employee_role__role__in=['city_head', 'traffic', 'office_data_entry'],
                                            employee_status='active').values_list('employee_id', flat=True))))
    mgmt = list(set(list(EmployeeRolesMapping.objects.filter(employee_role__role__in=['management'],
                                                             employee_status='active').values_list(
        'employee__username__profile__email', flat=True))))

    # for role in EmployeeRoles.objects.filter(role__in=[ 'city_head', 'traffic', 'office_data_entry']):
    #     for emp in role.employee_role.exclude(employee=None):
    #         print(emp.employee.emp_name(), emp.employee.office_multiple.values_list('id', flat=True))
