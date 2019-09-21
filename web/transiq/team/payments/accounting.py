from datetime import datetime

from pandas._libs.lib import timedelta

from api.utils import get_or_none, to_int
from broker.models import BrokerSummary, Broker
from owner.models import VehicleSummary
from supplier.models import Vehicle,VehicleAccountingSummary
from sme.models import SmeSummary, Sme
from supplier.models import SupplierAccountingSummary
from team.models import Invoice


def sme_accounting_summary():
    for sme in Sme.objects.all():
        accounting_summary = {}
        try:
            sme_summary = SmeSummary.objects.get(sme_id=sme.id)
            sme_summary.accounting_summary = accounting_summary
            sme_summary.save()
        except SmeSummary.DoesNotExist:
            sme_summary = SmeSummary.objects.create(sme=sme, accounting_summary=accounting_summary)


def vehicle_accounting_summary(vehicle):
    completed_pod_total_amount = 0
    completed_pod_paid_amount = 0
    completed_pod_balance_amount = 0
    completed_pod_credit_amount = 0
    completed_pod_debit_amount = 0
    completed_pod_adjusted_outward_amount = 0
    for booking in vehicle.manualbooking_set.filter(pod_status='completed').exclude(booking_status='cancelled'):
        completed_pod_total_amount += booking.fms_supplier_amount
        completed_pod_paid_amount += booking.fms_supplier_paid_amount
        completed_pod_balance_amount += booking.fms_balance_supplier
        completed_pod_credit_amount += booking.credit_amount_supplier
        completed_pod_debit_amount = booking.debit_amount_supplier
        completed_pod_adjusted_outward_amount = booking.adjusted_outward_amount

    pending_pod_total_amount = 0
    pending_pod_paid_amount = 0
    pending_pod_balance_amount = 0
    pending_pod_credit_amount = 0
    pending_pod_debit_amount = 0
    pending_pod_adjusted_outward_amount = 0
    for booking in vehicle.manualbooking_set.exclude(pod_status='completed').exclude(booking_status='cancelled'):
        pending_pod_total_amount += booking.fms_supplier_amount
        pending_pod_paid_amount += booking.fms_supplier_paid_amount
        pending_pod_balance_amount += booking.fms_balance_supplier
        pending_pod_credit_amount += booking.credit_amount_supplier
        pending_pod_debit_amount = booking.debit_amount_supplier
        pending_pod_adjusted_outward_amount = booking.adjusted_outward_amount

    accounting_summary = {
        'vehicle_number': vehicle.number(),
        'completed_pod': {
            'num_of_completed_pod': vehicle.manualbooking_set.filter(pod_status='completed').exclude(
                booking_status='cancelled').count(),
            'total_amount': completed_pod_total_amount,
            'paid_amount': completed_pod_paid_amount,
            'balance_amount': completed_pod_balance_amount,
            'credit_amount': completed_pod_credit_amount,
            'debit_amount': completed_pod_debit_amount,
            'adjusted_outward_amount': completed_pod_adjusted_outward_amount,
        },
        'completed_pod_balance_amount': to_int(completed_pod_balance_amount),
        'pending_pod': {
            'num_of_pending_pod': vehicle.manualbooking_set.exclude(pod_status='completed').exclude(
                booking_status='cancelled').count(),
            'total_amount': pending_pod_total_amount,
            'paid_amount': pending_pod_paid_amount,
            'balance_amount': pending_pod_balance_amount,
            'credit_amount': pending_pod_credit_amount,
            'debit_amount': pending_pod_debit_amount,
            'adjusted_outward_amount': pending_pod_adjusted_outward_amount
        }
    }
    try:
        vehicle_summary = VehicleAccountingSummary.objects.get(vehicle=vehicle)
        vehicle_summary.accounting_summary = accounting_summary
        vehicle_summary.save()
    except VehicleAccountingSummary.DoesNotExist:
        VehicleAccountingSummary.objects.create(vehicle=vehicle, accounting_summary=accounting_summary)

# def vehicle_accounting_summary(vehicle):
#     completed_pod_total_amount = 0
#     completed_pod_paid_amount = 0
#     completed_pod_balance_amount = 0
#     for booking in vehicle.manualbooking_set.filter(pod_status='completed').exclude(booking_status='cancelled'):
#         completed_pod_total_amount += booking.fms_supplier_amount
#         completed_pod_paid_amount += booking.fms_supplier_paid_amount
#         completed_pod_balance_amount += booking.fms_balance_supplier
#
#     pending_pod_total_amount = 0
#     pending_pod_paid_amount = 0
#     pending_pod_balance_amount = 0
#     for booking in vehicle.manualbooking_set.exclude(pod_status='completed').exclude(booking_status='cancelled'):
#         pending_pod_total_amount += booking.fms_supplier_amount
#         pending_pod_paid_amount += booking.fms_supplier_paid_amount
#         pending_pod_balance_amount += booking.fms_balance_supplier
#
#     accounting_summary = {
#         'vehicle_number': vehicle.number(),
#         'completed_pod': {
#             'num_of_completed_pod': vehicle.manualbooking_set.filter(pod_status='completed').exclude(
#                 booking_status='cancelled').count(),
#             'total_amount': completed_pod_total_amount,
#             'paid_amount': completed_pod_paid_amount,
#             'balance_amount': completed_pod_balance_amount
#         },
#         'completed_pod_balance_amount': to_int(completed_pod_balance_amount),
#         'pending_pod': {
#             'num_of_pending_pod': vehicle.manualbooking_set.exclude(pod_status='completed').exclude(
#                 booking_status='cancelled').count(),
#             'total_amount': pending_pod_total_amount,
#             'paid_amount': pending_pod_paid_amount,
#             'balance_amount': pending_pod_balance_amount
#         }
#     }
#     try:
#         vehicle_summary = VehicleSummary.objects.get(vehicle=vehicle)
#         vehicle_summary.accounting_summary = accounting_summary
#         vehicle_summary.save()
#     except VehicleSummary.DoesNotExist:
#         VehicleSummary.objects.create(vehicle=vehicle, accounting_summary=accounting_summary)
#

# def supplier_accounting_summary(broker):
#     completed_pod_total_amount = 0
#     completed_pod_paid_amount = 0
#     completed_pod_balance_amount = 0
#     for booking in broker.team_booking_broker.filter(pod_status='completed').exclude(booking_status='cancelled'):
#         completed_pod_total_amount += booking.fms_supplier_amount
#         completed_pod_paid_amount += booking.fms_supplier_paid_amount
#         completed_pod_balance_amount += booking.fms_balance_supplier
#
#     pending_pod_total_amount = 0
#     pending_pod_paid_amount = 0
#     pending_pod_balance_amount = 0
#     for booking in broker.team_booking_broker.exclude(pod_status='completed').exclude(booking_status='cancelled'):
#         pending_pod_total_amount += booking.fms_supplier_amount
#         pending_pod_paid_amount += booking.fms_supplier_paid_amount
#         pending_pod_balance_amount += booking.fms_balance_supplier
#
#     accounting_summary = {
#         'supplier_name': broker.get_name(),
#         'completed_pod': {
#             'num_of_completed_pod': broker.team_booking_broker.filter(pod_status='completed').exclude(
#                 booking_status='cancelled').count(),
#             'total_amount': completed_pod_total_amount,
#             'paid_amount': completed_pod_paid_amount,
#             'balance_amount': completed_pod_balance_amount
#         },
#         'completed_pod_balance_amount': to_int(completed_pod_balance_amount),
#         'pending_pod': {
#             'num_of_pending_pod': broker.team_booking_broker.exclude(pod_status='completed').exclude(
#                 booking_status='cancelled').count(),
#             'total_amount': pending_pod_total_amount,
#             'paid_amount': pending_pod_paid_amount,
#             'balance_amount': pending_pod_balance_amount
#         }
#     }
#     try:
#         broker_summary = BrokerSummary.objects.get(broker=broker)
#         broker_summary.accounting_summary = accounting_summary
#         broker_summary.save()
#     except BrokerSummary.DoesNotExist:
#         BrokerSummary.objects.create(broker=broker, accounting_summary=accounting_summary)


def supplier_accounting_summary(supplier):
    completed_pod_total_amount = 0
    completed_pod_paid_amount = 0
    completed_pod_balance_amount = 0
    completed_pod_credit_amount = 0
    completed_pod_debit_amount = 0
    completed_pod_adjusted_outward_amount = 0
    for booking in supplier.manualbooking_accounting_supplier.filter(pod_status='completed').exclude(booking_status='cancelled'):
        completed_pod_total_amount += booking.fms_supplier_amount
        completed_pod_paid_amount += booking.fms_supplier_paid_amount
        completed_pod_balance_amount += booking.fms_balance_supplier
        completed_pod_credit_amount += booking.credit_amount_supplier
        completed_pod_debit_amount = booking.debit_amount_supplier
        completed_pod_adjusted_outward_amount = booking.adjusted_outward_amount

    pending_pod_total_amount = 0
    pending_pod_paid_amount = 0
    pending_pod_balance_amount = 0
    pending_pod_credit_amount = 0
    pending_pod_debit_amount = 0
    pending_pod_adjusted_outward_amount = 0
    for booking in supplier.manualbooking_accounting_supplier.exclude(pod_status='completed').exclude(booking_status='cancelled'):
        pending_pod_total_amount += booking.fms_supplier_amount
        pending_pod_paid_amount += booking.fms_supplier_paid_amount
        pending_pod_balance_amount += booking.fms_balance_supplier
        pending_pod_credit_amount += booking.credit_amount_supplier
        pending_pod_debit_amount = booking.debit_amount_supplier
        pending_pod_adjusted_outward_amount = booking.adjusted_outward_amount

    accounting_summary = {
        'supplier_name': supplier.name,
        'supplier_code': supplier.code,
        'supplier_aaho_office': supplier.aaho_office.branch_name if supplier.aaho_office else None,
        'completed_pod': {
            'num_of_completed_pod': supplier.manualbooking_accounting_supplier.filter(pod_status='completed').exclude(
                booking_status='cancelled').count(),
            'total_amount': completed_pod_total_amount,
            'paid_amount': completed_pod_paid_amount,
            'balance_amount': completed_pod_balance_amount,
            'credit_amount': completed_pod_credit_amount,
            'debit_amount': completed_pod_debit_amount,
            'adjusted_outward_amount': completed_pod_adjusted_outward_amount,
        },
        'completed_pod_balance_amount': to_int(completed_pod_balance_amount),
        'pending_pod': {
            'num_of_pending_pod': supplier.manualbooking_accounting_supplier.exclude(pod_status='completed').exclude(
                booking_status='cancelled').count(),
            'total_amount': pending_pod_total_amount,
            'paid_amount': pending_pod_paid_amount,
            'balance_amount': pending_pod_balance_amount,
            'credit_amount': pending_pod_credit_amount,
            'debit_amount': pending_pod_debit_amount,
            'adjusted_outward_amount': pending_pod_adjusted_outward_amount
        }
    }
    try:
        supplier_summary = SupplierAccountingSummary.objects.get(supplier=supplier)
        supplier_summary.accounting_summary = accounting_summary
        supplier_summary.save()
    except SupplierAccountingSummary.DoesNotExist:
        SupplierAccountingSummary.objects.create(supplier=supplier, accounting_summary=accounting_summary)


def placed_order_accounting_summary(sme_id):
    sme = get_or_none(Sme, id=sme_id)
    if not isinstance(sme, Sme):
        return None
    invoice_raised_bookings = sme.mb_bill_order_placed.exclude(invoice_status__in=['no_invoice']).exclude(
        booking_status='cancelled')
    amount_0_30_days = 0
    amount_30_60_days = 0
    amount_60_90_days = 0
    amount_90_180_days = 0
    amount_gt_180_days = 0
    today = datetime.now().date()
    for booking in invoice_raised_bookings:
        invoice = booking.invoices.last()
        if isinstance(invoice, Invoice):
            if today - timedelta(days=0) >= invoice.date > today - timedelta(days=30):
                amount_0_30_days += booking.balance_for_customer
            elif today - timedelta(days=30) >= invoice.date > today - timedelta(days=60):
                amount_30_60_days += booking.balance_for_customer
            elif today - timedelta(days=60) >= invoice.date > today - timedelta(days=90):
                amount_60_90_days += booking.balance_for_customer
            elif today - timedelta(days=90) >= invoice.date > today - timedelta(days=180):
                amount_90_180_days += booking.balance_for_customer
            elif today + timedelta(days=180) >= invoice.date:
                amount_gt_180_days += booking.balance_for_customer
    invoice_unraised_bookings = sme.mb_bill_order_placed.filter(invoice_status__in=['no_invoice']).exclude(
        booking_status='cancelled')
    unbilled_amount = 0
    for booking in invoice_unraised_bookings:
        invoice = booking.invoices.last()
        if not isinstance(invoice, Invoice):
            unbilled_amount += booking.balance_for_customer
    on_account_payment = sum([amount + tds for amount, tds in
                              sme.pendinginwardpaymententry_set.filter(adjusted_flag=False).exclude(
                                  deleted=True).values_list('amount', 'tds')])
    billed_amount = amount_0_30_days + amount_30_60_days + amount_60_90_days + amount_90_180_days + amount_gt_180_days - on_account_payment
    total_amount = billed_amount + unbilled_amount
    accounting_summary = {
        "customer_code": sme.company_code,
        "customer_name": sme.get_name(),
        'aaho_poc': sme.aaho_poc_name,
        "on_account_payment": to_int(on_account_payment),
        "outstanding_balance": {
            "billed_amount": to_int(billed_amount),
            "total_amount": to_int(total_amount)
        },
        'total_amount': to_int(total_amount),
        "pending_payments": {
            "amount_0_30_days": to_int(amount_0_30_days),
            "amount_30_60_days": to_int(amount_30_60_days),
            "amount_60_90_days": to_int(amount_60_90_days),
            "amount_90_180_days": to_int(amount_90_180_days),
            "amount_gt_180_days": to_int(amount_gt_180_days)
        },
        "unbilled_amount": to_int(unbilled_amount)
    }
    try:
        sme_summary = SmeSummary.objects.get(sme_id=sme.id)
        sme_summary.placed_order_accounting_summary = accounting_summary
        sme_summary.save()
    except SmeSummary.DoesNotExist:
        SmeSummary.objects.create(sme=sme, placed_order_accounting_summary=accounting_summary)


def billed_customer_accounting_summary(sme_id):
    sme = get_or_none(Sme, id=sme_id)
    if not isinstance(sme, Sme):
        return None
    print(sme)
    print(sme.pendinginwardpaymententry_set.filter(adjusted_flag=False))
    invoice_raised_bookings = sme.mb_bill_paid_by.exclude(invoice_status__in=['no_invoice']).exclude(
        booking_status='cancelled')
    amount_0_30_days = 0
    amount_30_60_days = 0
    amount_60_90_days = 0
    amount_90_180_days = 0
    amount_gt_180_days = 0
    today = datetime.now().date()
    for booking in invoice_raised_bookings:
        invoice = booking.invoices.last()
        if isinstance(invoice, Invoice):
            if today - timedelta(days=0) >= invoice.date > today - timedelta(days=30):
                amount_0_30_days += booking.balance_for_customer
            elif today - timedelta(days=30) >= invoice.date > today - timedelta(days=60):
                amount_30_60_days += booking.balance_for_customer
            elif today - timedelta(days=60) >= invoice.date > today - timedelta(days=90):
                amount_60_90_days += booking.balance_for_customer
            elif today - timedelta(days=90) >= invoice.date > today - timedelta(days=180):
                amount_90_180_days += booking.balance_for_customer
            elif today + timedelta(days=180) >= invoice.date:
                amount_gt_180_days += booking.balance_for_customer

    # Added by Ravindra temporary for overdue and pending amount - Can merge into existing code later
    from restapi.models import BookingStatusesMapping
    pending_amount = 0
    overdue_invoices = 0
    overdue_amount = 0
    pending_invoices = 0
    invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=['invoice_raised', 'party_invoice_sent',
                                                          'invoice_confirmed']).exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    complete_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='inward_followup_completed').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    pending_payments_bookings = [x for x in invoice_confirmed_bookings if x not in complete_bookings]
    invs = Invoice.objects.filter(bookings__in=pending_payments_bookings, customer_fk=sme,
                                  payment_received=False).distinct()
    pending_invoices = invs.count()
    for inv in invs:
        pending_amount += to_int(inv.get_customer_balance)
        if inv.is_overdue:
            overdue_invoices += 1
            overdue_amount += to_int(inv.get_overdue_balance)
    # ----------------

    confirm_unbilled_amount = 0
    for booking in sme.mb_bill_paid_by.filter(invoice_status__in=['no_invoice']).exclude(
            booking_status='cancelled'):
        invoice = booking.invoices.last()
        if not isinstance(invoice, Invoice):
            confirm_unbilled_amount += booking.balance_for_customer
    unconfirm_unbilled_amount = 0
    for booking in sme.mb_bill_order_placed.filter(invoice_status__in=['no_invoice']).filter(
            customer_to_be_billed_to=None).exclude(
        booking_status='cancelled'):
        invoice = booking.invoices.last()
        if not isinstance(invoice, Invoice):
            unconfirm_unbilled_amount += booking.balance_for_customer
    unbilled_amount = confirm_unbilled_amount + unconfirm_unbilled_amount
    on_account_payment = sum([amount + tds for amount, tds in
                              sme.pendinginwardpaymententry_set.filter(adjusted_flag=False).exclude(
                                  deleted=True).values_list('amount', 'tds')])
    billed_amount = amount_0_30_days + amount_30_60_days + amount_60_90_days + amount_90_180_days + amount_gt_180_days - on_account_payment
    total_amount = billed_amount + unbilled_amount
    accounting_summary = {
        "customer_code": sme.company_code,
        "customer_name": sme.get_name(),
        'aaho_poc': sme.aaho_poc_name,
        "on_account_payment": to_int(on_account_payment),
        "outstanding_balance": {
            "billed_amount": to_int(billed_amount),
            "total_amount": to_int(total_amount)
        },
        'total_amount': to_int(total_amount),
        "pending_payments": {
            "amount_0_30_days": to_int(amount_0_30_days),
            "amount_30_60_days": to_int(amount_30_60_days),
            "amount_60_90_days": to_int(amount_60_90_days),
            "amount_90_180_days": to_int(amount_90_180_days),
            "amount_gt_180_days": to_int(amount_gt_180_days)
        },
        "unbilled_amount": to_int(unbilled_amount),
        "unconfirm_unbilled_amount": to_int(unconfirm_unbilled_amount),
        "confirm_unbilled_amount": to_int(confirm_unbilled_amount),
        "overdue_amount": to_int(overdue_amount),
        "pending_amount": to_int(pending_amount),
        "overdue_invoices": to_int(overdue_invoices),
        "pending_invoices": to_int(pending_invoices)
    }
    try:
        sme_summary = SmeSummary.objects.get(sme_id=sme.id)
        sme_summary.billed_accounting_summary = accounting_summary
        sme_summary.save()
    except SmeSummary.DoesNotExist:
        SmeSummary.objects.create(sme=sme, billed_accounting_summary=accounting_summary)


def prepare_data():
    for vehicle in Vehicle.objects.all():
        print(vehicle)
        vehicle_accounting_summary(vehicle)
    for broker in Broker.objects.all():
        print(broker)
        supplier_accounting_summary(broker)
    for sme in Sme.objects.all():
        print(sme)
        placed_order_accounting_summary(sme.id)
        billed_customer_accounting_summary(sme.id)
