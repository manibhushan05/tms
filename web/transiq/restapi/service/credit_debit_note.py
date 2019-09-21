from django.utils.html import format_html

from supplier.models import Supplier
from team.models import CreditNoteCustomer, DebitNoteCustomer, CreditNoteSupplier, DebitNoteSupplier, \
    CreditNoteCustomerDirectAdvance


def approve_credit_note_customer_data():
    data = []
    for row in CreditNoteCustomer.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': [{'id': booking.id, 'booking_id': booking.booking_id} for booking in row.bookings.all()],
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_cnc_form': 'approve_cnc_form_{}'.format(row.id),
            'approve_cnc_btn': 'approve_cnc_btn_{}'.format(row.id),
            'reject_cnc_btn': 'reject_cnc_btn_{}'.format(row.id),
            'input_reject_cnc_remarks': 'input_reject_cnc_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_cnc_remarks': 'div_rejection_cnc_remarks_{}'.format(row.id),
            'div_rejection_cnc_line': 'div_rejection_cnc_line_{}'.format(row.id),
        })
    return data


def approve_debit_note_customer_data():
    data = []
    for row in DebitNoteCustomer.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'dnc_id': row.id,
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': [{'id': booking.id, 'booking_id': booking.booking_id} for booking in row.bookings.all()],
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.debit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'debit_note_number': row.debit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'debit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_dnc_form': 'approve_dnc_form_{}'.format(row.id),
            'approve_dnc_btn': 'approve_dnc_btn_{}'.format(row.id),
            'reject_dnc_btn': 'reject_dnc_btn_{}'.format(row.id),
            'input_reject_dnc_remarks': 'input_reject_dnc_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_dnc_remarks': 'div_rejection_dnc_remarks_{}'.format(row.id),
            'div_rejection_dnc_line': 'div_rejection_dnc_line_{}'.format(row.id),
        })
    return data


def approve_credit_note_supplier_data():
    data = []
    for row in CreditNoteSupplier.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'supplier': row.accounting_supplier.name if isinstance(row.accounting_supplier,Supplier) else '-',
            'bookings': [{'id': booking.id, 'booking_id': booking.booking_id} for booking in row.bookings.all()],
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_cns_form': 'approve_cns_form_{}'.format(row.id),
            'approve_cns_btn': 'approve_cns_btn_{}'.format(row.id),
            'reject_cns_btn': 'reject_cns_btn_{}'.format(row.id),
            'input_reject_cns_remarks': 'input_reject_cns_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_cns_remarks': 'div_rejection_cns_remarks_{}'.format(row.id),
            'div_rejection_cns_line': 'div_rejection_cns_line_{}'.format(row.id),
        })
    return data


def approve_debit_note_supplier_data():
    data = []
    for row in DebitNoteSupplier.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'supplier': row.accounting_supplier.name if isinstance(row.accounting_supplier,Supplier) else '-',
            'bookings': [{'id': booking.id, 'booking_id': booking.booking_id} for booking in row.bookings.all()],
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.debit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.debit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_dns_form': 'approve_dns_form_{}'.format(row.id),
            'approve_dns_btn': 'approve_dns_btn_{}'.format(row.id),
            'reject_dns_btn': 'reject_dns_btn_{}'.format(row.id),
            'input_reject_dns_remarks': 'input_reject_dns_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_dns_remarks': 'div_rejection_dns_remarks_{}'.format(row.id),
            'div_rejection_dns_line': 'div_rejection_dns_line_{}'.format(row.id),
        })
    return data


def approve_credit_note_customer_direct_advance_data():
    data = []
    for row in CreditNoteCustomerDirectAdvance.objects.filter(status='pending').order_by('created_on'):
        data.append({
            'cnc_id': row.id,
            'supplier': row.accounting_supplier.name if isinstance(row.accounting_supplier,Supplier) else '-',
            'customer': row.customer.get_name() if row.customer else '-',
            'bookings': [{'id': booking.id, 'booking_id': booking.booking_id} for booking in row.bookings.all()],
            'invoice': row.invoice.invoice_number if row.invoice else '-',
            'amount': row.credit_amount,
            'created_on': row.created_on.strftime('%d-%b-%Y') if row.created_on else '-',
            'credit_note_number': row.credit_note_number,
            'created_by': row.created_by.username if row.created_by else '-',
            'credit_note_reason': row.reason.name if row.reason else '-',
            'remarks': row.remarks,
            'approve_cnca_form': 'approve_cnca_form_{}'.format(row.id),
            'approve_cnca_btn': 'approve_cnca_btn_{}'.format(row.id),
            'reject_cnca_btn': 'reject_cnca_btn_{}'.format(row.id),
            'input_reject_cnca_remarks': 'input_reject_cnca_remarks_{}'.format(row.id),
            'btn_status': 'btn_status_{}'.format(row.id),
            'div_rejection_cnca_remarks': 'div_rejection_cnca_remarks_{}'.format(row.id),
            'div_rejection_cnca_line': 'div_rejection_cnca_line_{}'.format(row.id),
        })
    return data
