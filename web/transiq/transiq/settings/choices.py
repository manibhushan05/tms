def parse_choices():
    data = []
    for row in (
            ('paid', 'Paid'),
            ('unpaid', 'Not Paid'),
            ('reconciled', 'Reconciled'),
    ):
        data.append({'key': row[0], 'value': row[1]})
    return data


def outward_payment_mode_choices():
    return [{'key': 'cash', 'value': 'Cash'},
            {'key': 'cheque', 'value': 'Cheque'},
            {'key': 'neft', 'value': 'NEFT'},
            {'key': 'imps', 'value': 'IMPS'},
            {'key': 'rtgs', 'value': 'RTGS'},
            {'key': 'happay', 'value': 'Happay'},
            {'key': 'fuel_card', 'value': 'Fuel Card'},
            {'key': 'hdfc_internal_account', 'value': 'HDFC Internal Account'},
            {'key': 'adjustment', 'value': 'Adjustment'}]


def outward_payment_status_choices():
    return [{'key': 'paid', 'value': 'Paid'},
            {'key': 'unpaid', 'value': 'Not Paid'},
            {'key': 'reconciled', 'value': 'Reconciled'}]


def outward_payment_refund_category_choices():
    return [{'key': True, 'value': 'Yes'},
            {'key': False, 'value': 'No'}]


def inward_payment_mode_choices():
    return [{'key': 'cash', 'value': 'Cash'},
            {'key': 'cheque', 'value': 'Cheque'},
            {'key': 'neft', 'value': 'NEFT'},
            {'key': 'imps', 'value': 'IMPS'},
            {'key': 'rtgs', 'value': 'RTGS'},
            {'key': 'happay', 'value': 'Happay'},
            {'key': 'cash_deposit', 'value': 'Cash Deposit'},
            {'key': 'hdfc_internal_account', 'value': 'HDFC Internal Account'}]


def booking_outward_payment_status_choices():
    return [{'key': 'no_payment_made', 'value': 'Nil'},
            {'key': 'partial', 'value': 'Partial'},
            {'key': 'complete', 'value': 'Full'},
            {'key': 'excess', 'value': 'Excess'}]


def booking_inward_payment_status_choices():
    return [{'key': 'no_payment', 'value': 'Nil'},
            {'key': 'partial_received', 'value': 'Partial'},
            {'key': 'full_received', 'value': 'Full'},
            {'key': 'excess', 'value': 'Excess'}]


def booking_invoice_status_choices():
    return [{'key': 'no_invoice', 'value': 'NoInvoice'},
            {'key': 'invoice_raised', 'value': 'InvoiceRaised'},
            {'key': 'invoice_sent', 'value': 'InvoiceSent'},
            {'key': 'invoice_confirmed', 'value': 'InvoiceConfirmed'}]


def booking_pod_status_choices():
    return [{'key': 'pending', 'value': 'Pending'},
            {'key': 'unverified', 'value': 'Unverified'},
            {'key': 'rejected', 'value': 'Rejected'},
            {'key': 'completed', 'value': 'Delivered'}]


def booking_billing_type_choices():
    return [{'key': 'T.B.B.', 'value': 'T.B.B.'},
            {'key': 'To Pay', 'value': 'To Pay'},
            {'key': 'Paid', 'value': 'Paid'},
            {'key': 'contract', 'value': 'Contract'}]
