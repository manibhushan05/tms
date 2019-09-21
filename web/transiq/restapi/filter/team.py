from django_filters import rest_framework as filters

from restapi.filter.common import ListFilter
from team.models import ManualBooking, OutWardPayment, InWardPayment, Invoice, OutWardPaymentBill, \
    CreditDebitNoteReason, CreditNoteCustomer, DebitNoteCustomer, PendingInwardPaymentCreditDebitNoteCustomer, \
    CreditNoteSupplier, DebitNoteSupplier, CreditNoteCustomerDirectAdvance, DebitNoteSupplierDirectAdvance, \
    InvoiceSummary, LrNumber


class InvoiceSummaryFilters(filters.FilterSet):
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between")

    ref_number = filters.CharFilter(field_name="ref_number", label="ref_number", lookup_expr="icontains")
    ref_number_null = filters.BooleanFilter(field_name="ref_number", label="Is ref_number Null", lookup_expr="isnull")

    datetime = filters.DateFilter(field_name="datetime", label="datetime")
    datetime_between = filters.DateFromToRangeFilter(field_name="datetime", label="DateTime Between",
                                                     lookup_expr='range')
    datetime_null = filters.BooleanFilter(field_name="datetime", label="Is Datetime Null",
                                          lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')
    booking = filters.NumberFilter(field_name='booking__id', label='Booking')
    lr_number = filters.NumberFilter(field_name='booking__lr_numbers__id', label='Lr Number')

    class Meta:
        model = InvoiceSummary
        fields = []


class ManualBookingFilters(filters.FilterSet):
    billing_types = (
        ('T.B.B.', 'T.B.B.'),
        ('To Pay', 'To Pay'),
        ('Paid', 'Paid'),
        ('contract', 'Contract'),
    )
    POD_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('unverified', 'Unverified'),
        ('rejected', 'Rejected'),
        ('completed', 'Delivered')
    )
    GST_LIABILITY_CHOICES = (
        ('consignor', 'Consignor'),
        ('consignee', 'Consignee'),
        ('carrier', 'Carrier'),
        ('exempted', 'Exempted'),
    )
    TDS_CERTIFICATE_STATUS = (
        ('y', 'Yes'),
        ('n', 'No'),
    )
    INWARD_PAYMENT_STATUS = (
        ('no_payment', 'Nil'),
        ('partial_received', 'Partial'),
        ('full_received', 'Full'),
        ('excess', 'Excess'),
    )
    INVOICE_STATUS = (
        ('no_invoice', 'NoInvoice'),
        ('invoice_raised', 'InvoiceRaised'),
        ('invoice_sent', 'InvoiceSent'),
    )
    OUTWARD_STATUS = (
        ('no_payment_made', 'Nil'),
        ('partial', 'Partial'),
        ('complete', 'Full'),
        ('excess', 'Excess'),
    )
    BOOKING_STATUS = (
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    )
    IS_ADVANCE = (
        ('no', 'No'),
        ('yes', 'Yes'),
    )

    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between", lookup_expr='range')

    booking_id = filters.CharFilter(field_name="booking_id", label="Booking ID", lookup_expr="icontains")
    booking_id_null = filters.BooleanFilter(field_name="booking_id", label="Is Booking ID Null", lookup_expr="isnull")
    lr_number = filters.NumberFilter(field_name='lr_numbers__id', lookup_expr='exact', label="Lr Number")
    # invoice_nu

    billing_type = ListFilter(field_name="billing_type", label="billing_type")
    billing_type_null = filters.BooleanFilter(field_name="billing_type", label="Is billing_type Null",
                                              lookup_expr="isnull")

    gst_liability = filters.ChoiceFilter(field_name="gst_liability", label="gst_liability",
                                         choices=GST_LIABILITY_CHOICES)
    gst_liability_null = filters.BooleanFilter(field_name="gst_liability", label="Is gst_liability Null",
                                               lookup_expr="isnull")

    shipment_date = filters.DateFilter(field_name="shipment_date", label="shipment_date")
    shipment_date_between = filters.DateFromToRangeFilter(field_name="shipment_date", label="Shipment date Between",
                                                          lookup_expr='range')
    shipment_date_null = filters.BooleanFilter(field_name="shipment_date", label="Is Shipment date Null",
                                               lookup_expr="isnull")

    delivery_datetime = filters.DateTimeFilter(field_name="delivery_datetime", label="delivery_datetime")
    delivery_datetime_between = filters.DateFromToRangeFilter(field_name="delivery_datetime",
                                                              label="Delivery Datetime Between", lookup_expr='range')
    delivery_datetime_null = filters.BooleanFilter(field_name="delivery_datetime", label="Is Delivery Datetime Null",
                                                   lookup_expr="isnull")

    charged_weight = filters.NumberFilter(field_name="charged_weight", label="charged_weight")
    charged_weight_range = filters.NumericRangeFilter(field_name="charged_weight", label="charged_weight_Range",
                                                      lookup_expr='range')
    charged_weight_null = filters.BooleanFilter(field_name="charged_weight", label="Is charged_weight Null",
                                                lookup_expr="isnull")

    supplier_charged_weight = filters.NumberFilter(field_name="supplier_charged_weight",
                                                   label="supplier_charged_weight")
    supplier_charged_weight_range = filters.NumericRangeFilter(field_name="supplier_charged_weight",
                                                               label="supplier_charged_weight_Range",
                                                               lookup_expr='range')
    supplier_charged_weight_null = filters.BooleanFilter(field_name="supplier_charged_weight",
                                                         label="Is supplier_charged_weight Null",
                                                         lookup_expr="isnull")
    party_rate = filters.NumberFilter(field_name="party_rate", label="party_rate", lookup_expr='range')
    party_rate_range = filters.NumericRangeFilter(field_name="party_rate",
                                                  label="party_rate_Range", lookup_expr='range')
    party_rate_null = filters.BooleanFilter(field_name="party_rate",
                                            label="Is party_rate Null",
                                            lookup_expr="isnull")

    supplier_rate = filters.NumberFilter(field_name="supplier_rate", label="supplier_rate")
    supplier_rate_range = filters.NumericRangeFilter(field_name="supplier_rate",
                                                     label="supplier_rate_Range", lookup_expr='range')
    supplier_rate_null = filters.BooleanFilter(field_name="supplier_rate",
                                               label="Is supplier_rate Null",
                                               lookup_expr="isnull")

    total_in_ward_amount = filters.NumberFilter(field_name="total_in_ward_amount", label="total_in_ward_amount")
    total_in_ward_amount_range = filters.NumericRangeFilter(field_name="total_in_ward_amount",
                                                            label="total_in_ward_amount_Range", lookup_expr='range')
    total_in_ward_amount_null = filters.BooleanFilter(field_name="total_in_ward_amount",
                                                      label="Is total_in_ward_amount Null",
                                                      lookup_expr="isnull")

    total_out_ward_amount = filters.NumberFilter(field_name="total_out_ward_amount", label="total_out_ward_amount")
    total_out_ward_amount_range = filters.NumericRangeFilter(field_name="total_out_ward_amount",
                                                             label="total_out_ward_amount_Range", lookup_expr='range')
    total_out_ward_amount_null = filters.BooleanFilter(field_name="total_out_ward_amount",
                                                       label="Is total_out_ward_amount Null",
                                                       lookup_expr="isnull")

    total_amount_to_company = filters.NumberFilter(field_name="total_amount_to_company",
                                                   label="total_amount_to_company")
    total_amount_to_company_range = filters.NumericRangeFilter(field_name="total_amount_to_company",
                                                               label="total_amount_to_company_Range",
                                                               lookup_expr='range')
    total_amount_to_company_null = filters.BooleanFilter(field_name="total_amount_to_company",
                                                         label="Is total_amount_to_company Null",
                                                         lookup_expr="isnull")

    refund_amount = filters.NumberFilter(field_name="refund_amount", label="refund_amount")
    refund_amount_range = filters.NumericRangeFilter(field_name="refund_amount", label="refund_amount_Range",
                                                     lookup_expr='range')
    refund_amount_null = filters.BooleanFilter(field_name="refund_amount", label="Is refund_amount Null",
                                               lookup_expr="isnull")
    total_amount_to_owner = filters.NumberFilter(field_name="total_amount_to_owner", label="total_amount_to_owner")
    total_amount_to_owner_range = filters.NumericRangeFilter(field_name="total_amount_to_owner",
                                                             label="total_amount_to_owner_Range", lookup_expr='range')
    total_amount_to_owner_null = filters.BooleanFilter(field_name="total_amount_to_owner",
                                                       label="Is total_amount_to_owner Null", lookup_expr="isnull")
    loading_charge = filters.NumberFilter(field_name="loading_charge", label="loading_charge")
    loading_charge_range = filters.NumericRangeFilter(field_name="loading_charge", label="loading_charge_Range",
                                                      lookup_expr='range')
    loading_charge_null = filters.BooleanFilter(field_name="loading_charge", label="Is loading_charge Null",
                                                lookup_expr="isnull")
    unloading_charge = filters.NumberFilter(field_name="unloading_charge", label="unloading_charge")
    unloading_charge_range = filters.NumericRangeFilter(field_name="unloading_charge", label="unloading_charge_Range",
                                                        lookup_expr='range')
    unloading_charge_null = filters.BooleanFilter(field_name="unloading_charge", label="Is unloading_charge Null",
                                                  lookup_expr="isnull")
    detention_charge = filters.NumberFilter(field_name="detention_charge", label="detention_charge")
    detention_charge_range = filters.NumericRangeFilter(field_name="detention_charge", label="detention_charge_Range",
                                                        lookup_expr='range')
    detention_charge_null = filters.BooleanFilter(field_name="detention_charge", label="Is detention_charge Null",
                                                  lookup_expr="isnull")
    additional_charges_for_company = filters.NumberFilter(field_name="additional_charges_for_company",
                                                          label="additional_charges_for_company")
    additional_charges_for_company_range = filters.NumericRangeFilter(field_name="additional_charges_for_company",
                                                                      label="additional_charges_for_company_Range",
                                                                      lookup_expr='range')
    additional_charges_for_company_null = filters.BooleanFilter(field_name="additional_charges_for_company",
                                                                label="Is additional_charges_for_company Null",
                                                                lookup_expr="isnull")
    remarks_about_additional_charges = filters.CharFilter(field_name="remarks_about_additional_charges",
                                                          label="remarks_about_additional_charges",
                                                          lookup_expr="icontains")
    remarks_about_additional_charges_null = filters.BooleanFilter(field_name="remarks_about_additional_charges",
                                                                  label="Is remarks_about_additional_charges Null",
                                                                  lookup_expr="isnull")
    additional_charges_for_owner = filters.NumberFilter(field_name="additional_charges_for_owner",
                                                        label="additional_charges_for_owner")
    additional_charges_for_owner_range = filters.NumericRangeFilter(field_name="additional_charges_for_owner",
                                                                    label="additional_charges_for_owner_Range",
                                                                    lookup_expr='range')
    additional_charges_for_owner_null = filters.BooleanFilter(field_name="additional_charges_for_owner",
                                                              label="Is additional_charges_for_owner Null",
                                                              lookup_expr="isnull")

    note_for_additional_owner_charges = filters.CharFilter(field_name="note_for_additional_owner_charges",
                                                           label="note_for_additional_owner_charges",
                                                           lookup_expr="icontains")
    note_for_additional_owner_charges_null = filters.BooleanFilter(field_name="note_for_additional_owner_charges",
                                                                   label="Is note_for_additional_owner_charges Null",
                                                                   lookup_expr="isnull")

    commission = filters.NumberFilter(field_name="commission", label="commission")
    commission_range = filters.NumericRangeFilter(field_name="commission", label="commission_Range",
                                                  lookup_expr='range')
    commission_null = filters.BooleanFilter(field_name="commission", label="Is commission Null", lookup_expr="isnull")

    lr_cost = filters.NumberFilter(field_name="lr_cost", label="lr_cost")
    lr_cost_range = filters.NumericRangeFilter(field_name="lr_cost", label="lr_cost_Range", lookup_expr='range')
    lr_cost_null = filters.BooleanFilter(field_name="lr_cost", label="Is lr_cost Null", lookup_expr="isnull")

    deduction_for_advance = filters.NumberFilter(field_name="deduction_for_advance",
                                                 label="deduction_for_advance")
    deduction_for_advance_range = filters.NumericRangeFilter(field_name="deduction_for_advance",
                                                             label="deduction_for_advance_Range", lookup_expr='range')
    deduction_for_advance_null = filters.BooleanFilter(field_name="deduction_for_advance",
                                                       label="Is deduction_for_advance Null",
                                                       lookup_expr="isnull")
    deduction_for_balance = filters.NumberFilter(field_name="deduction_for_balance",
                                                 label="deduction_for_balance")
    deduction_for_balance_range = filters.NumericRangeFilter(field_name="deduction_for_balance",
                                                             label="deduction_for_balance_Range", lookup_expr='range')
    deduction_for_balance_null = filters.BooleanFilter(field_name="deduction_for_balance",
                                                       label="Is deduction_for_balance Null",
                                                       lookup_expr="isnull")
    other_deduction = filters.NumberFilter(field_name="other_deduction",
                                           label="other_deduction")
    other_deduction_range = filters.NumericRangeFilter(field_name="other_deduction",
                                                       label="other_deduction_Range", lookup_expr='range')
    other_deduction_null = filters.BooleanFilter(field_name="other_deduction",
                                                 label="Is other_deduction Null",
                                                 lookup_expr="isnull")

    remarks_about_deduction = filters.CharFilter(field_name="remarks_about_deduction",
                                                 label="remarks_about_deduction",
                                                 lookup_expr="icontains")
    remarks_about_deduction_null = filters.BooleanFilter(field_name="remarks_about_deduction",
                                                         label="Is remarks_about_deduction Null",
                                                         lookup_expr="isnull")

    deductions_for_company = filters.NumberFilter(field_name="deductions_for_company",
                                                  label="deductions_for_company")
    deductions_for_company_range = filters.NumericRangeFilter(field_name="deductions_for_company",
                                                              label="deductions_for_company_Range", lookup_expr='range')
    deductions_for_company_null = filters.BooleanFilter(field_name="deductions_for_company",
                                                        label="Is deductions_for_company Null",
                                                        lookup_expr="isnull")
    invoice_number = filters.CharFilter(field_name="invoice_number", label="invoice_number", lookup_expr="icontains")
    invoice_number_null = filters.BooleanFilter(field_name="invoice_number", label="Is invoice_number Null",
                                                lookup_expr="isnull")
    tds_deducted_amount = filters.NumberFilter(field_name="tds_deducted_amount", label="tds_deducted_amount")
    tds_deducted_amount_range = filters.NumericRangeFilter(field_name="tds_deducted_amount",
                                                           label="tds_deducted_amount_Range", lookup_expr='range')
    tds_deducted_amount_null = filters.BooleanFilter(field_name="tds_deducted_amount",
                                                     label="Is tds_deducted_amount Null",
                                                     lookup_expr="isnull")

    pod_date = filters.DateTimeFilter(field_name="pod_date", label="pod_date")
    pod_date_between = filters.DateTimeFromToRangeFilter(field_name="pod_date", label="Shipment date Between",
                                                         lookup_expr='range')
    pod_date_null = filters.BooleanFilter(field_name="pod_date", label="Is Shipment date Null",
                                          lookup_expr="isnull")

    pod_status = ListFilter(field_name="pod_status", label="pod_status")
    pod_status_null = filters.BooleanFilter(field_name="pod_status", label="Is pod_status Null", lookup_expr="isnull")

    outward_payment_status = ListFilter(field_name="outward_payment_status", label="outward_payment_status")
    outward_payment_status_null = filters.BooleanFilter(field_name="outward_payment_status",
                                                        label="Is outward_payment_status Null", lookup_expr="isnull")

    inward_payment_status = ListFilter(field_name="inward_payment_status", label="inward_payment_status")
    inward_payment_status_null = filters.BooleanFilter(field_name="inward_payment_status",
                                                       label="Is inward_payment_status Null", lookup_expr="isnull")

    invoice_status = filters.ChoiceFilter(field_name="invoice_status", label="invoice_status", choices=INVOICE_STATUS)
    invoice_status_null = filters.BooleanFilter(field_name="invoice_status",
                                                label="Is invoice_status Null", lookup_expr="isnull")

    booking_status = filters.ChoiceFilter(field_name="booking_status", label="booking_status",
                                          choices=BOOKING_STATUS)
    booking_status_null = filters.BooleanFilter(field_name="booking_status",
                                                label="Is booking_status Null", lookup_expr="isnull")
    is_advance = filters.ChoiceFilter(field_name="is_advance", label="is_advance", choices=IS_ADVANCE)
    is_advance_null = filters.BooleanFilter(field_name="is_advance", label="Is is_advance Null", lookup_expr="isnull")

    is_print_payment_mode_instruction = filters.BooleanFilter(field_name="is_print_payment_mode_instruction",
                                                              label="Is is_print_payment_mode_instruction Null")
    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    company_id = ListFilter(field_name='company_id', label='Customer who placed order')
    customer_to_be_billed_to_id = ListFilter(field_name='customer_to_be_billed_to_id',
                                             label='Customer who will make payment')
    vehicle_id = ListFilter(field_name='supplier_vehicle_id', label='vehicle')
    vehicle_number = filters.CharFilter(field_name='vehicle__vehicle_number', lookup_expr='icontains', label='vehicle_number')
    booking_supplier_id = ListFilter(field_name='booking_supplier_id', label='Supplier')
    accounting_supplier_id = ListFilter(field_name='accounting_supplier_id', label='Supplier')
    owner_supplier_id = ListFilter(field_name='owner_supplier_id', label='Supplier')
    driver_id = ListFilter(field_name='driver_supplier_id', label='Driver')
    source_office_id = ListFilter(field_name='source_office_id', label='Source Office')
    destination_office_id = ListFilter(field_name='destination_office_id', label='Destination Office')
    vehicle_category_id = ListFilter(field_name='vehicle_category_id', label='Vehicle Category')
    to_city_fk_id = ListFilter(field_name='to_city_fk_id', label='To City')
    from_city_fk_id = ListFilter(field_name='from_city_fk_id', label='From City')

    class Meta:
        model = ManualBooking
        fields = []


class LrNumberFilter(filters.FilterSet):
    POD_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('unverified', 'Unverified'),
        ('rejected', 'Rejected'),
        ('completed', 'Delivered')
    )
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between", lookup_expr='range')

    booking = filters.CharFilter(field_name="booking__id", label="Booking", lookup_expr="exact")
    booking_null = filters.BooleanFilter(field_name="booking__booking_id", label="Is Booking Null",
                                         lookup_expr="isnull")

    lr_number = filters.CharFilter(field_name="lr_number", label="LR Number", lookup_expr="icontains")
    lr_number_null = filters.BooleanFilter(field_name="lr_number", label="Is LR Number Null",
                                           lookup_expr="isnull")

    datetime = filters.DateFilter(field_name="datetime", label="datetime")
    datetime_between = filters.DateFromToRangeFilter(field_name="datetime", label="DateTime Between",
                                                     lookup_expr='range')
    datetime_null = filters.BooleanFilter(field_name="datetime", label="Is Datetime Null",
                                          lookup_expr="isnull")

    source_office = filters.CharFilter(field_name="source_office__branch_name", label="Source Office",
                                       lookup_expr="icontains")
    source_office_null = filters.BooleanFilter(field_name="source_office__branch_name", label="Is Source Office Null",
                                               lookup_expr="isnull")
    destination_office = filters.CharFilter(field_name="destination_office__branch_name", label="Source Office",
                                            lookup_expr="icontains")
    destination_office_null = filters.BooleanFilter(field_name="destination_office__branch_name",
                                                    label="Is Source Office Null",
                                                    lookup_expr="isnull")

    pod_status = filters.ChoiceFilter(field_name="pod_status", label="pod_status", choices=POD_STATUS_CHOICES)
    pod_status_null = filters.BooleanFilter(field_name="pod_status", label="Is pod_status Null",
                                            lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    class Meta:
        model = LrNumber
        fields = []


class OutwardPaymentFilters(filters.FilterSet):
    mode = (
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('neft', 'NEFT'),
        ('imps', 'IMPS'),
        ('rtgs', 'RTGS'),
        ('happay', 'Happay'),
        ('fuel_card', 'Fuel Card'),
        ('hdfc_internal_account', 'HDFC Internal Account'),
        ('adjustment', 'Adjustment')
    )
    STATUS = (
        ('paid', 'Paid'),
        ('unpaid', 'Not Paid'),
        ('reconciled', 'Reconciled')
    )
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between")

    paid_to = filters.CharFilter(field_name="paid_to", label="Paid To", lookup_expr="icontains")
    paid_to_null = filters.BooleanFilter(field_name="paid_to", label="Is Paid To Null", lookup_expr="isnull")

    utr = filters.CharFilter(field_name="utr", label="UTR", lookup_expr="icontains")
    utr_null = filters.BooleanFilter(field_name="utr", label="Is UTR Null", lookup_expr="isnull")

    lorry_number = filters.CharFilter(field_name="lorry_number", label="Lorry Number", lookup_expr="icontains")
    lorry_number_null = filters.BooleanFilter(field_name="lorry_number", label="Is Lorry Number Null",
                                              lookup_expr="isnull")

    actual_amount = filters.NumberFilter(field_name="actual_amount",
                                         label="actual_amount")
    actual_amount_range = filters.NumericRangeFilter(field_name="actual_amount", label="actual_amount_Range",
                                                     lookup_expr='range')
    actual_amount_null = filters.BooleanFilter(field_name="actual_amount", label="Is actual_amount Null",
                                               lookup_expr="isnull")
    expected_amount = filters.NumberFilter(field_name="expected_amount", label="expected_amount")
    expected_amount_range = filters.NumericRangeFilter(field_name="expected_amount", label="expected_amount_Range")
    expected_amount_null = filters.BooleanFilter(field_name="expected_amount", label="Is expected_amount Null",
                                                 lookup_expr="isnull")
    payment_mode = ListFilter(field_name="payment_mode", label="payment_mode")
    payment_mode_null = filters.BooleanFilter(field_name="payment_mode", label="Is payment_mode Null",
                                              lookup_expr="isnull")
    remarks = filters.CharFilter(field_name="remarks", label="Remarks", lookup_expr="icontains")
    remarks_null = filters.BooleanFilter(field_name="remarks", label="Is Remarks Null", lookup_expr="isnull")

    payment_date = filters.DateFilter(field_name="payment_date", label="payment_date")
    payment_date_between = filters.DateFromToRangeFilter(field_name="payment_date", label="Shipment date Between",
                                                         lookup_expr='range')
    payment_date_null = filters.BooleanFilter(field_name="payment_date", label="Is Shipment date Null",
                                              lookup_expr="isnull")

    invoice_number = filters.CharFilter(field_name="invoice_number", label="Invoice Number", lookup_expr="icontains")
    invoice_number_null = filters.BooleanFilter(field_name="invoice_number", label="Is Invoice Number Null",
                                                lookup_expr="isnull")

    status =ListFilter(field_name="status", label="status")
    status_null = filters.BooleanFilter(field_name="status", label="Is status Null", lookup_expr="isnull")

    is_sms_supplier = filters.BooleanFilter(field_name="is_sms_supplier", label="Is is_sms_supplier Null")
    is_refund_amount = filters.BooleanFilter(field_name="is_refund_amount", label="Is is_refund_amount Null")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    booking = ListFilter(field_name='booking_id__id', label='Booking')
    bank_account = ListFilter(field_name='bank_account__id', label='Bank Account')
    fuel_card = ListFilter(field_name='fuel_card__id', label='Fuel Card')
    lr_number = ListFilter(field_name='booking_id__lr_numbers__id', label='Lr Number')
    vehicle_id = ListFilter(field_name='booking_id__vehicle__id', label='Vehicle Number')

    class Meta:
        model = OutWardPayment
        fields = []


class InwardPaymentFilters(filters.FilterSet):
    modes = (
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('neft', 'NEFT'),
        ('imps', 'IMPS'),
        ('rtgs', 'RTGS'),
        ('happay', 'Happay'),
        ('cash_deposit', 'Cash Deposit'),
        ('hdfc_internal_account', 'HDFC Internal Account'),
    )

    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between")

    received_from = filters.CharFilter(field_name="received_from", label="received_from", lookup_expr="icontains")
    received_from_null = filters.BooleanFilter(field_name="received_from", label="Is received_from Null",
                                               lookup_expr="isnull")

    tds = filters.NumberFilter(field_name="tds", label="tds")
    tds_range = filters.NumericRangeFilter(field_name="tds", label="tds_Range", lookup_expr='range')
    tds_null = filters.BooleanFilter(field_name="tds", label="Is tds Null", lookup_expr="isnull")

    actual_amount = filters.NumberFilter(field_name="actual_amount",
                                         label="actual_amount")
    actual_amount_range = filters.NumericRangeFilter(field_name="actual_amount", label="actual_amount_Range",
                                                     lookup_expr='range')
    actual_amount_null = filters.BooleanFilter(field_name="actual_amount", label="Is actual_amount Null",
                                               lookup_expr="isnull")
    expected_amount = filters.NumberFilter(field_name="expected_amount", label="expected_amount")
    expected_amount_range = filters.NumericRangeFilter(field_name="expected_amount", label="expected_amount_Range",
                                                       lookup_expr='range')
    expected_amount_null = filters.BooleanFilter(field_name="expected_amount", label="Is expected_amount Null",
                                                 lookup_expr="isnull")

    payment_mode = ListFilter(field_name="payment_mode", label="payment_mode")
    payment_mode_null = filters.BooleanFilter(field_name="payment_mode", label="Is payment_mode Null",
                                              lookup_expr="isnull")

    payment_date = filters.DateFilter(field_name="payment_date", label="payment_date")
    payment_date_between = filters.DateFromToRangeFilter(field_name="payment_date", label="Shipment date Between",
                                                         lookup_expr='range')
    payment_date_null = filters.BooleanFilter(field_name="payment_date", label="Is Shipment date Null",
                                              lookup_expr="isnull")

    trn = filters.CharFilter(field_name="trn", label="Lorry Number", lookup_expr="icontains")
    trn_null = filters.BooleanFilter(field_name="trn", label="Is Lorry Number Null",
                                     lookup_expr="isnull")

    remarks = filters.CharFilter(field_name="remarks", label="Remarks", lookup_expr="icontains")
    remarks_null = filters.BooleanFilter(field_name="remarks", label="Is Remarks Null", lookup_expr="isnull")

    invoice_number = filters.CharFilter(field_name="invoice_number", label="Invoice Number", lookup_expr="icontains")
    invoice_number_null = filters.BooleanFilter(field_name="invoice_number", label="Is Invoice Number Null",
                                                lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    booking = ListFilter(field_name='booking_id__id', label='Booking')
    lr_number = ListFilter(field_name='booking_id__lr_numbers__id', label='Lr Number')
    vehicle_id = ListFilter(field_name='booking_id__vehicle__id', label='Vehicle Number')

    class Meta:
        model = InWardPayment
        fields = []


class InvoiceFilters(filters.FilterSet):
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between")

    invoice_number = filters.CharFilter(field_name="invoice_number", label="invoice_number", lookup_expr="icontains")
    invoice_number_null = filters.BooleanFilter(field_name="invoice_number", label="Is invoice_number Null",
                                                lookup_expr="isnull")

    date = filters.DateFilter(field_name="date", label="date")
    date_between = filters.DateFromToRangeFilter(field_name="date", label="Shipment date Between", lookup_expr='range')
    date_null = filters.BooleanFilter(field_name="date", label="Is Shipment date Null",
                                      lookup_expr="isnull")
    company_name = filters.CharFilter(field_name="company_name", label="company_name", lookup_expr="icontains")
    company_name_null = filters.BooleanFilter(field_name="company_name", label="Is company_name Null",
                                              lookup_expr="isnull")

    payment_received = filters.BooleanFilter(field_name="payment_received", label="Payment_received")

    address = filters.CharFilter(field_name="address", label="address", lookup_expr="icontains")
    address_null = filters.BooleanFilter(field_name="address", label="Is address Null",
                                         lookup_expr="isnull")

    pin = filters.CharFilter(field_name="pin", label="pin", lookup_expr="icontains")
    pin_null = filters.BooleanFilter(field_name="pin", label="Is pin Null",
                                     lookup_expr="isnull")

    gstin = filters.CharFilter(field_name="gstin", label="gstin", lookup_expr="icontains")
    gstin_null = filters.BooleanFilter(field_name="gstin", label="Is gstin Null",
                                       lookup_expr="isnull")

    total_amount = filters.NumberFilter(field_name="total_amount",
                                        label="total_amount")
    total_amount_range = filters.NumericRangeFilter(field_name="total_amount", label="total_amount_Range",
                                                    lookup_expr='range')
    total_amount_null = filters.BooleanFilter(field_name="total_amount", label="Is total_amount Null",
                                              lookup_expr="isnull")
    advance_payment = filters.NumberFilter(field_name="advance_payment", label="advance_payment")
    advance_payment_range = filters.NumericRangeFilter(field_name="advance_payment", label="advance_payment_Range",
                                                       lookup_expr='range')
    advance_payment_null = filters.BooleanFilter(field_name="advance_payment", label="Is advance_payment Null",
                                                 lookup_expr="isnull")

    remarks = filters.CharFilter(field_name="remarks", label="Remarks", lookup_expr="icontains")
    remarks_null = filters.BooleanFilter(field_name="remarks", label="Is Remarks Null", lookup_expr="isnull")

    service_tax_paid_by = filters.CharFilter(field_name="service_tax_paid_by", label="service_tax_paid_by",
                                             lookup_expr="icontains")
    service_tax_paid_by_null = filters.BooleanFilter(field_name="service_tax_paid_by",
                                                     label="Is service_tax_paid_by Null",
                                                     lookup_expr="isnull")
    service_tax_aaho = filters.NumberFilter(field_name="service_tax_aaho", label="service_tax_aaho")
    service_tax_aaho_range = filters.NumericRangeFilter(field_name="service_tax_aaho", label="service_tax_aaho_Range",
                                                        lookup_expr='range')
    service_tax_aaho_null = filters.BooleanFilter(field_name="service_tax_aaho", label="Is service_tax_aaho Null",
                                                  lookup_expr="isnull")

    summary_required = filters.BooleanFilter(field_name="summary_required", label="Summary Required")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    customer = ListFilter(field_name='customer_fk_id', label='Customer')
    booking = ListFilter(field_name='bookings__id', label='Booking')
    lr_number = ListFilter(field_name='bookings__lr_numbers__id', label='Lr Number')

    class Meta:
        model = Invoice
        fields = []


class OutwardPaymentBillFilters(filters.FilterSet):
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between")

    bill_number = filters.CharFilter(field_name="bill_number", label="Bill Number", lookup_expr="icontains")
    bill_number_null = filters.BooleanFilter(field_name="bill_number", label="Is Bill Number Null",
                                             lookup_expr="isnull")

    bill_date = filters.DateFilter(field_name="bill_date", label="bill_date")
    bill_date_between = filters.DateFromToRangeFilter(field_name="bill_date", label="Bill date Between",
                                                      lookup_expr='range')
    bill_date_null = filters.BooleanFilter(field_name="bill_date", label="Is Shipment date Null",
                                           lookup_expr="isnull")

    amount = filters.NumberFilter(field_name="amount",
                                  label="amount")
    amount_range = filters.NumericRangeFilter(field_name="amount", label="amount_Range", lookup_expr='range')
    amount_null = filters.BooleanFilter(field_name="amount", label="Is amount Null",
                                        lookup_expr="isnull")

    vehicle_number = filters.CharFilter(field_name="vehicle_number", label="Vehicle Number", lookup_expr="icontains")
    vehicle_number_null = filters.BooleanFilter(field_name="vehicle_number", label="Is Vehicle Number Null",
                                                lookup_expr="isnull")

    loading_date = filters.DateFilter(field_name="loading_date", label="loading_date")
    loading_date_between = filters.DateFromToRangeFilter(field_name="loading_date", label="Bill date Between",
                                                         lookup_expr='range')
    loading_date_null = filters.BooleanFilter(field_name="loading_date", label="Is Shipment date Null",
                                              lookup_expr="isnull")

    weight = filters.CharFilter(field_name="weight", label="Weight", lookup_expr="icontains")
    weight_null = filters.BooleanFilter(field_name="weight", label="Is Weight Null",
                                        lookup_expr="isnull")

    paid_to = filters.CharFilter(field_name="paid_to", label="Paid to", lookup_expr="icontains")
    paid_to_null = filters.BooleanFilter(field_name="paid_to", label="Is Paid To Null",
                                         lookup_expr="isnull")
    pan_number = filters.CharFilter(field_name="pan_number", label="PAN Number", lookup_expr="icontains")
    pan_number_null = filters.BooleanFilter(field_name="pan_number", label="Is PAN Number Null",
                                            lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')
    booking = filters.NumberFilter(field_name='booking__id', label='Booking')
    lr_number = filters.NumberFilter(field_name='booking__lr_numbers__id', label='Lr Number')

    class Meta:
        model = OutWardPaymentBill
        fields = []


class CreditDebitNoteReasonFilters(filters.FilterSet):
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between")

    name = filters.CharFilter(field_name="name", label="Reason", lookup_expr="icontains")
    name_null = filters.BooleanFilter(field_name="name", label="Is Reason Null",
                                      lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    class Meta:
        model = CreditDebitNoteReason
        fields = []


class CreditNoteCustomerFilters(filters.FilterSet):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between")

    credit_note_number = filters.CharFilter(field_name="credit_note_number", label="Paid to",
                                            lookup_expr="icontains")
    credit_note_number_null = filters.BooleanFilter(field_name="credit_note_number",
                                                    label="Is Paid To Null",
                                                    lookup_expr="isnull")
    credit_amount = filters.NumberFilter(field_name="credit_amount", label="credit_amount")
    credit_amount_range = filters.NumericRangeFilter(field_name="credit_amount", label="credit_amount_Range",
                                                     lookup_expr='range')
    credit_amount_null = filters.BooleanFilter(field_name="credit_amount", label="Is credit_amount Null",
                                               lookup_expr="isnull")

    adjusted_amount = filters.NumberFilter(field_name="adjusted_amount", label="adjusted_amount")
    adjusted_amount_range = filters.NumericRangeFilter(field_name="adjusted_amount", label="adjusted_amount_Range",
                                                       lookup_expr='range')
    adjusted_amount_null = filters.BooleanFilter(field_name="adjusted_amount", label="Is adjusted_amount Null",
                                                 lookup_expr="isnull")

    approved_by = filters.CharFilter(name="approved_by__username", label="Approved By name", lookup_expr="icontains")
    approved_by_null = filters.BooleanFilter(name="approved_by", label="Is Approved By Null", lookup_expr="isnull")
    approved_on = filters.IsoDateTimeFilter(name="approved_on", label="Approved on")
    approved_between = filters.DateTimeFromToRangeFilter(field_name="approved_on", label="Approved Between",
                                                         lookup_expr='range')

    adjusted_by = filters.CharFilter(name="adjusted_by__username", label="Adjusted By name", lookup_expr="icontains")
    adjusted_by_null = filters.BooleanFilter(name="adjusted_by", label="Is Adjusted By Null", lookup_expr="isnull")
    adjusted_on = filters.IsoDateTimeFilter(name="adjusted_on", label="Adjusted on")
    adjusted_between = filters.DateTimeFromToRangeFilter(field_name="Adjusted_on", label="adjusted Between",
                                                         lookup_expr='range')

    remarks = filters.CharFilter(field_name="remarks", label="Remarks", lookup_expr="icontains")
    remarks_null = filters.BooleanFilter(field_name="remarks", label="Is Remarks Null", lookup_expr="isnull")

    status = filters.ChoiceFilter(field_name="status", label="status",
                                  choices=STATUS_CHOICES)
    status_null = filters.BooleanFilter(field_name="status", label="Is status Null",
                                        lookup_expr="isnull")

    rejected_by = filters.CharFilter(name="rejected_by__username", label="rejected By name", lookup_expr="icontains")
    rejected_by_null = filters.BooleanFilter(name="rejected_by", label="Is rejected By Null", lookup_expr="isnull")
    rejected_on = filters.IsoDateTimeFilter(name="rejected_on", label="rejected on")
    rejected_between = filters.DateTimeFromToRangeFilter(field_name="rejected_on", label="rejected Between",
                                                         lookup_expr='range')
    rejection_reason = filters.CharFilter(field_name="rejection_reason", label="rejection_reason",
                                          lookup_expr="icontains")
    rejection_reason_null = filters.BooleanFilter(field_name="rejection_reason", label="Is rejection_reason Null",
                                                  lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    class Meta:
        model = CreditNoteCustomer
        fields = []


class DebitNoteCustomerFilters(filters.FilterSet):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between")

    debit_note_number = filters.CharFilter(field_name="debit_note_number", label="Paid to",
                                           lookup_expr="icontains")
    debit_note_number_null = filters.BooleanFilter(field_name="debit_note_number",
                                                   label="Is Paid To Null",
                                                   lookup_expr="isnull")
    debit_amount = filters.NumberFilter(field_name="debit_amount", label="debit_amount")
    debit_amount_range = filters.NumericRangeFilter(field_name="debit_amount", label="debit_amount_Range",
                                                    lookup_expr='range')
    debit_amount_null = filters.BooleanFilter(field_name="debit_amount", label="Is debit_amount Null",
                                              lookup_expr="isnull")

    adjusted_amount = filters.NumberFilter(field_name="adjusted_amount", label="adjusted_amount")
    adjusted_amount_range = filters.NumericRangeFilter(field_name="adjusted_amount", label="adjusted_amount_Range",
                                                       lookup_expr='range')
    adjusted_amount_null = filters.BooleanFilter(field_name="adjusted_amount", label="Is adjusted_amount Null",
                                                 lookup_expr="isnull")

    approved_by = filters.CharFilter(name="approved_by__username", label="Approved By name", lookup_expr="icontains")
    approved_by_null = filters.BooleanFilter(name="approved_by", label="Is Approved By Null", lookup_expr="isnull")
    approved_on = filters.IsoDateTimeFilter(name="approved_on", label="Approved on")
    approved_between = filters.DateTimeFromToRangeFilter(field_name="approved_on", label="Approved Between",
                                                         lookup_expr='range')

    adjusted_by = filters.CharFilter(name="adjusted_by__username", label="Adjusted By name", lookup_expr="icontains")
    adjusted_by_null = filters.BooleanFilter(name="adjusted_by", label="Is Adjusted By Null", lookup_expr="isnull")
    adjusted_on = filters.IsoDateTimeFilter(name="adjusted_on", label="Adjusted on")
    adjusted_between = filters.DateTimeFromToRangeFilter(field_name="Adjusted_on", label="adjusted Between",
                                                         lookup_expr='range')

    remarks = filters.CharFilter(field_name="remarks", label="Remarks", lookup_expr="icontains")
    remarks_null = filters.BooleanFilter(field_name="remarks", label="Is Remarks Null", lookup_expr="isnull")

    status = filters.ChoiceFilter(field_name="status", label="status",
                                  choices=STATUS_CHOICES)
    status_null = filters.BooleanFilter(field_name="status", label="Is status Null",
                                        lookup_expr="isnull")

    rejected_by = filters.CharFilter(name="rejected_by__username", label="rejected By name", lookup_expr="icontains")
    rejected_by_null = filters.BooleanFilter(name="rejected_by", label="Is rejected By Null", lookup_expr="isnull")
    rejected_on = filters.IsoDateTimeFilter(name="rejected_on", label="rejected on")
    rejected_between = filters.DateTimeFromToRangeFilter(field_name="rejected_on", label="rejected Between",
                                                         lookup_expr='range')
    rejection_reason = filters.CharFilter(field_name="rejection_reason", label="rejection_reason",
                                          lookup_expr="icontains")
    rejection_reason_null = filters.BooleanFilter(field_name="rejection_reason", label="Is rejection_reason Null",
                                                  lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    class Meta:
        model = DebitNoteCustomer
        fields = []


#
#
# class PendingInwardPaymentCreditDebitNoteCustomerFilters(filters.FilterSet):
#     id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
#     id_range = filters.RangeFilter(field_name="id", label="ID Between")
#
#     adjusted_amount = filters.NumberFilter(field_name="adjusted_amount", label="adjusted_amount")
#     adjusted_amount_range = filters.NumericRangeFilter(field_name="adjusted_amount", label="adjusted_amount_Range")
#     adjusted_amount_null = filters.BooleanFilter(field_name="adjusted_amount", label="Is adjusted_amount Null",
#                                                  lookup_expr="isnull")
#     created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
#     created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")
#     created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
#     created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between")
#
#     class Meta:
#         model = PendingInwardPaymentCreditDebitNoteCustomer
#         fields = []


class CreditNoteSupplierFilters(filters.FilterSet):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between", lookup_expr='range')

    credit_note_number = filters.CharFilter(field_name="credit_note_number", label="Paid to",
                                            lookup_expr="icontains")
    credit_note_number_null = filters.BooleanFilter(field_name="credit_note_number",
                                                    label="Is Paid To Null",
                                                    lookup_expr="isnull")
    credit_amount = filters.NumberFilter(field_name="credit_amount", label="credit_amount")
    credit_amount_range = filters.NumericRangeFilter(field_name="credit_amount", label="credit_amount_Range",
                                                     lookup_expr='range')
    credit_amount_null = filters.BooleanFilter(field_name="credit_amount", label="Is credit_amount Null",
                                               lookup_expr="isnull")

    adjusted_amount = filters.NumberFilter(field_name="adjusted_amount", label="adjusted_amount")
    adjusted_amount_range = filters.NumericRangeFilter(field_name="adjusted_amount", label="adjusted_amount_Range",
                                                       lookup_expr='range')
    adjusted_amount_null = filters.BooleanFilter(field_name="adjusted_amount", label="Is adjusted_amount Null",
                                                 lookup_expr="isnull")

    approved_by = filters.CharFilter(name="approved_by__username", label="Approved By name", lookup_expr="icontains")
    approved_by_null = filters.BooleanFilter(name="approved_by", label="Is Approved By Null", lookup_expr="isnull")
    approved_on = filters.IsoDateTimeFilter(name="approved_on", label="Approved on")
    approved_between = filters.DateTimeFromToRangeFilter(field_name="approved_on", label="Approved Between",
                                                         lookup_expr='range')

    adjusted_by = filters.CharFilter(name="adjusted_by__username", label="Adjusted By name", lookup_expr="icontains")
    adjusted_by_null = filters.BooleanFilter(name="adjusted_by", label="Is Adjusted By Null", lookup_expr="isnull")
    adjusted_on = filters.IsoDateTimeFilter(name="adjusted_on", label="Adjusted on")
    adjusted_between = filters.DateTimeFromToRangeFilter(field_name="Adjusted_on", label="adjusted Between",
                                                         lookup_expr='range')

    remarks = filters.CharFilter(field_name="remarks", label="Remarks", lookup_expr="icontains")
    remarks_null = filters.BooleanFilter(field_name="remarks", label="Is Remarks Null", lookup_expr="isnull")

    status = filters.ChoiceFilter(field_name="status", label="status",
                                  choices=STATUS_CHOICES)
    status_null = filters.BooleanFilter(field_name="status", label="Is status Null",
                                        lookup_expr="isnull")

    rejected_by = filters.CharFilter(name="rejected_by__username", label="rejected By name", lookup_expr="icontains")
    rejected_by_null = filters.BooleanFilter(name="rejected_by", label="Is rejected By Null", lookup_expr="isnull")
    rejected_on = filters.IsoDateTimeFilter(name="rejected_on", label="rejected on")
    rejected_between = filters.DateTimeFromToRangeFilter(field_name="rejected_on", label="rejected Between",
                                                         lookup_expr='range')
    rejection_reason = filters.CharFilter(field_name="rejection_reason", label="rejection_reason",
                                          lookup_expr="icontains")
    rejection_reason_null = filters.BooleanFilter(field_name="rejection_reason", label="Is rejection_reason Null",
                                                  lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    class Meta:
        model = CreditNoteSupplier
        fields = []


class DebitNoteSupplierFilters(filters.FilterSet):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between", lookup_expr='range')

    debit_note_number = filters.CharFilter(field_name="debit_note_number", label="Paid to",
                                           lookup_expr="icontains")
    debit_note_number_null = filters.BooleanFilter(field_name="debit_note_number",
                                                   label="Is Paid To Null",
                                                   lookup_expr="isnull")
    debit_amount = filters.NumberFilter(field_name="debit_amount", label="debit_amount")
    debit_amount_range = filters.NumericRangeFilter(field_name="debit_amount", label="debit_amount_Range",
                                                    lookup_expr='range')
    debit_amount_null = filters.BooleanFilter(field_name="debit_amount", label="Is debit_amount Null",
                                              lookup_expr="isnull")

    adjusted_amount = filters.NumberFilter(field_name="adjusted_amount", label="adjusted_amount")
    adjusted_amount_range = filters.NumericRangeFilter(field_name="adjusted_amount", label="adjusted_amount_Range",
                                                       lookup_expr='range')
    adjusted_amount_null = filters.BooleanFilter(field_name="adjusted_amount", label="Is adjusted_amount Null",
                                                 lookup_expr="isnull")

    approved_by = filters.CharFilter(name="approved_by__username", label="Approved By name", lookup_expr="icontains")
    approved_by_null = filters.BooleanFilter(name="approved_by", label="Is Approved By Null", lookup_expr="isnull")
    approved_on = filters.IsoDateTimeFilter(name="approved_on", label="Approved on")
    approved_between = filters.DateTimeFromToRangeFilter(field_name="approved_on", label="Approved Between",
                                                         lookup_expr='range')

    adjusted_by = filters.CharFilter(name="adjusted_by__username", label="Adjusted By name", lookup_expr="icontains")
    adjusted_by_null = filters.BooleanFilter(name="adjusted_by", label="Is Adjusted By Null", lookup_expr="isnull")
    adjusted_on = filters.IsoDateTimeFilter(name="adjusted_on", label="Adjusted on")
    adjusted_between = filters.DateTimeFromToRangeFilter(field_name="Adjusted_on", label="adjusted Between",
                                                         lookup_expr='range')

    remarks = filters.CharFilter(field_name="remarks", label="Remarks", lookup_expr="icontains")
    remarks_null = filters.BooleanFilter(field_name="remarks", label="Is Remarks Null", lookup_expr="isnull")

    status = filters.ChoiceFilter(field_name="status", label="status",
                                  choices=STATUS_CHOICES)
    status_null = filters.BooleanFilter(field_name="status", label="Is status Null",
                                        lookup_expr="isnull")

    rejected_by = filters.CharFilter(name="rejected_by__username", label="rejected By name", lookup_expr="icontains")
    rejected_by_null = filters.BooleanFilter(name="rejected_by", label="Is rejected By Null", lookup_expr="isnull")
    rejected_on = filters.IsoDateTimeFilter(name="rejected_on", label="rejected on")
    rejected_between = filters.DateTimeFromToRangeFilter(field_name="rejected_on", label="rejected Between",
                                                         lookup_expr='range')
    rejection_reason = filters.CharFilter(field_name="rejection_reason", label="rejection_reason",
                                          lookup_expr="icontains")
    rejection_reason_null = filters.BooleanFilter(field_name="rejection_reason", label="Is rejection_reason Null",
                                                  lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    class Meta:
        model = DebitNoteSupplier
        fields = []


class CreditNoteCustomerDirectAdvanceFilters(filters.FilterSet):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between")

    credit_note_number = filters.CharFilter(field_name="credit_note_number", label="Paid to",
                                            lookup_expr="icontains")
    credit_note_number_null = filters.BooleanFilter(field_name="credit_note_number",
                                                    label="Is Paid To Null",
                                                    lookup_expr="isnull")
    credit_amount = filters.NumberFilter(field_name="credit_amount", label="credit_amount")
    credit_amount_range = filters.NumericRangeFilter(field_name="credit_amount", label="credit_amount_Range",
                                                     lookup_expr='range')
    credit_amount_null = filters.BooleanFilter(field_name="credit_amount", label="Is credit_amount Null",
                                               lookup_expr="isnull")

    adjusted_amount = filters.NumberFilter(field_name="adjusted_amount", label="adjusted_amount")
    adjusted_amount_range = filters.NumericRangeFilter(field_name="adjusted_amount", label="adjusted_amount_Range",
                                                       lookup_expr='range')
    adjusted_amount_null = filters.BooleanFilter(field_name="adjusted_amount", label="Is adjusted_amount Null",
                                                 lookup_expr="isnull")

    approved_by = filters.CharFilter(name="approved_by__username", label="Approved By name", lookup_expr="icontains")
    approved_by_null = filters.BooleanFilter(name="approved_by", label="Is Approved By Null", lookup_expr="isnull")
    approved_on = filters.IsoDateTimeFilter(name="approved_on", label="Approved on")
    approved_between = filters.DateTimeFromToRangeFilter(field_name="approved_on", label="Approved Between",
                                                         lookup_expr='range')

    adjusted_by = filters.CharFilter(name="adjusted_by__username", label="Adjusted By name", lookup_expr="icontains")
    adjusted_by_null = filters.BooleanFilter(name="adjusted_by", label="Is Adjusted By Null", lookup_expr="isnull")
    adjusted_on = filters.IsoDateTimeFilter(name="adjusted_on", label="Adjusted on")
    adjusted_between = filters.DateTimeFromToRangeFilter(field_name="Adjusted_on", label="adjusted Between",
                                                         lookup_expr='range')

    remarks = filters.CharFilter(field_name="remarks", label="Remarks", lookup_expr="icontains")
    remarks_null = filters.BooleanFilter(field_name="remarks", label="Is Remarks Null", lookup_expr="isnull")

    status = filters.ChoiceFilter(field_name="status", label="status",
                                  choices=STATUS_CHOICES)
    status_null = filters.BooleanFilter(field_name="status", label="Is status Null",
                                        lookup_expr="isnull")

    rejected_by = filters.CharFilter(name="rejected_by__username", label="rejected By name", lookup_expr="icontains")
    rejected_by_null = filters.BooleanFilter(name="rejected_by", label="Is rejected By Null", lookup_expr="isnull")
    rejected_on = filters.IsoDateTimeFilter(name="rejected_on", label="rejected on")
    rejected_between = filters.DateTimeFromToRangeFilter(field_name="rejected_on", label="rejected Between",
                                                         lookup_expr='range')
    rejection_reason = filters.CharFilter(field_name="rejection_reason", label="rejection_reason",
                                          lookup_expr="icontains")
    rejection_reason_null = filters.BooleanFilter(field_name="rejection_reason", label="Is rejection_reason Null",
                                                  lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    class Meta:
        model = CreditNoteCustomerDirectAdvance
        fields = []


class DebitNoteSupplierDirectAdvanceFilters(filters.FilterSet):
    STATUS_CHOICES = (
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Adjusted'),
        ('adjusted', 'Fully Adjusted')
    )
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between")

    debit_note_number = filters.CharFilter(field_name="debit_note_number", label="Paid to",
                                           lookup_expr="icontains")
    debit_note_number_null = filters.BooleanFilter(field_name="debit_note_number",
                                                   label="Is Paid To Null",
                                                   lookup_expr="isnull")
    debit_amount = filters.NumberFilter(field_name="debit_amount", label="debit_amount")
    debit_amount_range = filters.NumericRangeFilter(field_name="debit_amount", label="debit_amount_Range",
                                                    lookup_expr='range')
    debit_amount_null = filters.BooleanFilter(field_name="debit_amount", label="Is debit_amount Null",
                                              lookup_expr="isnull")

    adjusted_amount = filters.NumberFilter(field_name="adjusted_amount", label="adjusted_amount")
    adjusted_amount_range = filters.NumericRangeFilter(field_name="adjusted_amount", label="adjusted_amount_Range",
                                                       lookup_expr='range')
    adjusted_amount_null = filters.BooleanFilter(field_name="adjusted_amount", label="Is adjusted_amount Null",
                                                 lookup_expr="isnull")

    approved_by = filters.CharFilter(name="approved_by__username", label="Approved By name", lookup_expr="icontains")
    approved_by_null = filters.BooleanFilter(name="approved_by", label="Is Approved By Null", lookup_expr="isnull")
    approved_on = filters.IsoDateTimeFilter(name="approved_on", label="Approved on")
    approved_between = filters.DateTimeFromToRangeFilter(field_name="approved_on", label="Approved Between",
                                                         lookup_expr='range')

    adjusted_by = filters.CharFilter(name="adjusted_by__username", label="Adjusted By name", lookup_expr="icontains")
    adjusted_by_null = filters.BooleanFilter(name="adjusted_by", label="Is Adjusted By Null", lookup_expr="isnull")
    adjusted_on = filters.IsoDateTimeFilter(name="adjusted_on", label="Adjusted on")
    adjusted_between = filters.DateTimeFromToRangeFilter(field_name="Adjusted_on", label="adjusted Between",
                                                         lookup_expr='range')

    remarks = filters.CharFilter(field_name="remarks", label="Remarks", lookup_expr="icontains")
    remarks_null = filters.BooleanFilter(field_name="remarks", label="Is Remarks Null", lookup_expr="isnull")

    status = filters.ChoiceFilter(field_name="status", label="status",
                                  choices=STATUS_CHOICES)
    status_null = filters.BooleanFilter(field_name="status", label="Is status Null",
                                        lookup_expr="isnull")

    rejected_by = filters.CharFilter(name="rejected_by__username", label="rejected By name", lookup_expr="icontains")
    rejected_by_null = filters.BooleanFilter(name="rejected_by", label="Is rejected By Null", lookup_expr="isnull")
    rejected_on = filters.IsoDateTimeFilter(name="rejected_on", label="rejected on")
    rejected_between = filters.DateTimeFromToRangeFilter(field_name="rejected_on", label="rejected Between",
                                                         lookup_expr='range')
    rejection_reason = filters.CharFilter(field_name="rejection_reason", label="rejection_reason",
                                          lookup_expr="icontains")
    rejection_reason_null = filters.BooleanFilter(field_name="rejection_reason", label="Is rejection_reason Null",
                                                  lookup_expr="isnull")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")
    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(field_name="created_on", label="Created Between",
                                                        lookup_expr='range')

    class Meta:
        model = DebitNoteSupplierDirectAdvance
        fields = []


class DataTablesFilters(filters.FilterSet):
    id = filters.NumberFilter(field_name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(field_name="id", label="ID Between", lookup_expr='range')
    table_name = filters.CharFilter(field_name='table_name', label='Table Name')
