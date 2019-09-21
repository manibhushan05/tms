from django_filters import rest_framework as filters

from fileupload.models import PODFile, VehicleFile, OwnerFile, DriverFile, ChequeFile, InvoiceReceiptFile


class PODFileFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    uploaded_by = filters.CharFilter(name="uploaded_by__username", label="Uploaded By name", lookup_expr="icontains")
    uploaded_by_null = filters.BooleanFilter(name="uploaded_by", label="Is Uploaded By Null", lookup_expr="isnull")

    verified_by = filters.CharFilter(name="verified_by__username", label="Verified By name", lookup_expr="icontains")
    verified_by_null = filters.BooleanFilter(name="verified_by", label="Is Verified By Null", lookup_expr="isnull")

    lr_number = filters.NumberFilter(name="lr_number__id", label="Lr Number name", lookup_expr="exact")
    lr_number_null = filters.BooleanFilter(name="lr_number", label="Is Lr Number Null", lookup_expr="isnull")

    booking_null = filters.BooleanFilter(name="booking", label="Is booking Null", lookup_expr="isnull")
    booking = filters.CharFilter(name="booking__id", label="Booking ID", lookup_expr="exact")

    s3_upload = filters.CharFilter(name="s3_upload__filename", label="S3 Upload Filename", lookup_expr='icontains')
    s3_upload_null = filters.BooleanFilter(name="s3_upload", label="Is S3 Upload",
                                           lookup_expr="isnull")

    s3_url = filters.CharFilter(name="s3_url", label="S3 Url", lookup_expr='icontains')
    s3_url_null = filters.BooleanFilter(name="s3_url", label="Is S3 Url Null", lookup_expr="isnull")

    s3_thumb_url = filters.CharFilter(name="s3_thumb_url", label="S3 thumb Url", lookup_expr='icontains')
    s3_thumb_url_null = filters.BooleanFilter(name="s3_thumb_url", label="Is S3 thumb Url Null", lookup_expr="isnull")

    serial = filters.CharFilter(name="serial", label="Serial Url", lookup_expr='icontains')

    verified = filters.BooleanFilter(name="verified", label="Verified", lookup_expr='exact')

    is_valid = filters.BooleanFilter(name="is_valid", label="Is Valid", lookup_expr='exact')

    verified_datetime = filters.IsoDateTimeFilter(name="verified_datetime", label="Verified datetime")
    verified_datetime_between = filters.DateTimeFromToRangeFilter(name="verified_datetime",
                                                                  label="Verified Datetime Between")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = PODFile
        fields = []


class VehicleFileFilter(filters.FilterSet):
    document_categories_choices = (
        ('PUC', 'Puc Certificate'),
        ('FIT', 'Fitness Certificate'),
        ('REG', 'Registration Certificate'),
        ('PERM', 'Permission Certificate'),
        ('INS', 'Insurance Certificate'),
    )

    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    uploaded_by = filters.CharFilter(name="uploaded_by__username", label="Uploaded By name", lookup_expr="icontains")
    uploaded_by_null = filters.BooleanFilter(name="uploaded_by", label="Is Uploaded By Null", lookup_expr="isnull")

    vehicle_null = filters.BooleanFilter(name="vehicle", label="Is Vehicle Null", lookup_expr="isnull")
    vehicle_number = filters.CharFilter(name="vehicle__vehicle_number", label="Vehicle Number", lookup_expr="icontains")
    vehicle_type = filters.CharFilter(name="vehicle__vehicle_type__vehicle_type", label="Vehicle Type",
                                      lookup_expr="icontains")

    document_category = filters.ChoiceFilter(name="document_category", label="Document Category",
                                             choices=document_categories_choices)
    document_category_null = filters.BooleanFilter(name="document_category", label="Is Document Category Null",
                                                   lookup_expr="isnull")

    s3_upload = filters.CharFilter(name="s3_upload__filename", label="S3 Upload Filename", lookup_expr='icontains')
    s3_upload_null = filters.BooleanFilter(name="s3_upload", label="Is S3 Upload",
                                           lookup_expr="isnull")

    s3_url = filters.CharFilter(name="s3_url", label="S3 Url", lookup_expr='icontains')
    s3_url_null = filters.BooleanFilter(name="s3_url", label="Is S3 Url Null", lookup_expr="isnull")

    s3_thumb_url = filters.CharFilter(name="s3_thumb_url", label="S3 thumb Url", lookup_expr='icontains')
    s3_thumb_url_null = filters.BooleanFilter(name="s3_thumb_url", label="Is S3 thumb Url Null", lookup_expr="isnull")

    serial = filters.CharFilter(name="serial", label="Serial Url", lookup_expr='icontains')

    verified = filters.BooleanFilter(name="verified", label="Verified", lookup_expr='exact')

    is_valid = filters.BooleanFilter(name="is_valid", label="Is Valid", lookup_expr='exact')

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = VehicleFile
        fields = []


class OwnerFileFilter(filters.FilterSet):
    document_categories_choices = (
        ('PAN', 'PAN Card'),
        ('DL', 'Driving Licence'),
        ('EL', 'Election ID'),
        ('AC', 'Aadhar Card'),
        ('PT', 'Passport'),
        ('RC', 'Ration Card'),
        ('DEC', 'Declaration'),
    )

    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    uploaded_by = filters.CharFilter(name="uploaded_by__username", label="Uploaded By name", lookup_expr="icontains")
    uploaded_by_null = filters.BooleanFilter(name="uploaded_by", label="Is Uploaded By Null", lookup_expr="isnull")

    owner_null = filters.BooleanFilter(name="owner", label="Is Owner Null", lookup_expr="isnull")
    owner = filters.CharFilter(name="owner__name__username", label="Owner Name", lookup_expr="icontains")

    document_category = filters.ChoiceFilter(name="document_category", label="Document Category",
                                             choices=document_categories_choices)
    document_category_null = filters.BooleanFilter(name="document_category", label="Is Document Category Null",
                                                   lookup_expr="isnull")

    s3_upload = filters.CharFilter(name="s3_upload__filename", label="S3 Upload Filename", lookup_expr='icontains')
    s3_upload_null = filters.BooleanFilter(name="s3_upload", label="Is S3 Upload",
                                           lookup_expr="isnull")

    s3_url = filters.CharFilter(name="s3_url", label="S3 Url", lookup_expr='icontains')
    s3_url_null = filters.BooleanFilter(name="s3_url", label="Is S3 Url Null", lookup_expr="isnull")

    s3_thumb_url = filters.CharFilter(name="s3_thumb_url", label="S3 thumb Url", lookup_expr='icontains')
    s3_thumb_url_null = filters.BooleanFilter(name="s3_thumb_url", label="Is S3 thumb Url Null", lookup_expr="isnull")

    serial = filters.CharFilter(name="serial", label="Serial Url", lookup_expr='icontains')

    verified = filters.BooleanFilter(name="verified", label="Verified", lookup_expr='exact')

    is_valid = filters.BooleanFilter(name="is_valid", label="Is Valid", lookup_expr='exact')

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = OwnerFile
        fields = []


class DriverFileFilter(filters.FilterSet):
    document_categories_choices = (
        ('PAN', 'PAN Card'),
        ('DL', 'Driving Licence'),
        ('EL', 'Election ID'),
        ('AC', 'Aadhar Card'),
        ('PT', 'Passport'),
        ('RC', 'Ration Card'),
    )

    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    uploaded_by = filters.CharFilter(name="uploaded_by__username", label="Uploaded By name", lookup_expr="icontains")
    uploaded_by_null = filters.BooleanFilter(name="uploaded_by", label="Is Uploaded By Null", lookup_expr="isnull")

    driver_null = filters.BooleanFilter(name="driver", label="Is Driver Null", lookup_expr="isnull")
    driver = filters.CharFilter(name="driver__name", label="Driver Name", lookup_expr="icontains")

    document_category = filters.ChoiceFilter(name="document_category", label="Document Category",
                                             choices=document_categories_choices)
    document_category_null = filters.BooleanFilter(name="document_category", label="Is Document Category Null",
                                                   lookup_expr="isnull")

    s3_upload = filters.CharFilter(name="s3_upload__filename", label="S3 Upload Filename", lookup_expr='icontains')
    s3_upload_null = filters.BooleanFilter(name="s3_upload", label="Is S3 Upload",
                                           lookup_expr="isnull")

    s3_url = filters.CharFilter(name="s3_url", label="S3 Url", lookup_expr='icontains')
    s3_url_null = filters.BooleanFilter(name="s3_url", label="Is S3 Url Null", lookup_expr="isnull")

    s3_thumb_url = filters.CharFilter(name="s3_thumb_url", label="S3 thumb Url", lookup_expr='icontains')
    s3_thumb_url_null = filters.BooleanFilter(name="s3_thumb_url", label="Is S3 thumb Url Null", lookup_expr="isnull")

    serial = filters.CharFilter(name="serial", label="Serial Url", lookup_expr='icontains')

    verified = filters.BooleanFilter(name="verified", label="Verified", lookup_expr='exact')

    is_valid = filters.BooleanFilter(name="is_valid", label="Is Valid", lookup_expr='exact')

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = DriverFile
        fields = []


class ChequeFileFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    uploaded_by = filters.CharFilter(name="uploaded_by__username", label="Uploaded By name", lookup_expr="icontains")
    uploaded_by_null = filters.BooleanFilter(name="uploaded_by", label="Is Uploaded By Null", lookup_expr="isnull")

    resolved_by = filters.CharFilter(name="resolved_by__username", label="Resolved By name", lookup_expr="icontains")
    resolved_by_null = filters.BooleanFilter(name="resolved_by", label="Is Resolved By Null", lookup_expr="isnull")

    customer_name = filters.CharFilter(name="customer_name", label="Customer Name", lookup_expr="icontains")
    customer_name_null = filters.BooleanFilter(name="customer_name", label="Is Customer Name Null",
                                               lookup_expr="isnull")

    customer_null = filters.BooleanFilter(name="customer", label="Is Customer Null", lookup_expr="isnull")
    customer = filters.CharFilter(name="customer__name__username", label="Customer", lookup_expr="icontains")

    amount = filters.NumberFilter(name="amount", label="Amount", lookup_expr="exact")
    amount_between = filters.NumericRangeFilter(name="amount", label="Amount Range")

    cheque_number_null = filters.BooleanFilter(name="cheque_number", label="Is Cheque Number Null",
                                               lookup_expr="isnull")
    cheque_number = filters.CharFilter(name="cheque_number", label="Cheque Number", lookup_expr="icontains")

    cheque_date_null = filters.BooleanFilter(name="cheque_date", label="Is Cheque Date Null", lookup_expr="isnull")
    cheque_date = filters.DateFilter(name="cheque_date", label="Cheque Date ")
    cheque_date_between = filters.DateTimeFromToRangeFilter(name="cheque_date", label="Cheque Date Between")

    remarks = filters.CharFilter(name="remarks", label="Remarks", lookup_expr='icontains')
    remarks_null = filters.BooleanFilter(name="remarks", label="Is Remarks Null", lookup_expr="isnull")

    s3_upload = filters.CharFilter(name="s3_upload__filename", label="S3 Upload Filename", lookup_expr='icontains')
    s3_upload_null = filters.BooleanFilter(name="s3_upload", label="Is S3 Upload",
                                           lookup_expr="isnull")

    serial = filters.CharFilter(name="serial", label="Serial Url", lookup_expr='icontains')

    resolved = filters.BooleanFilter(name="resolved", label="Resolved", lookup_expr='exact')

    is_valid = filters.BooleanFilter(name="is_valid", label="Is Valid", lookup_expr='exact')

    resolved_datetime = filters.IsoDateTimeFilter(name="resolved_datetime", label="resolved datetime")
    resolved_datetime_between = filters.DateTimeFromToRangeFilter(name="resolved_datetime",
                                                                  label="resolved Datetime Between")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = ChequeFile
        fields = []


class InvoiceReceiptFileFilter(filters.FilterSet):
    document_categories_choices = (
        ('PAN', 'PAN Card'),
        ('DL', 'Driving Licence'),
        ('EL', 'Election ID'),
        ('AC', 'Aadhar Card'),
        ('PT', 'Passport'),
        ('RC', 'Ration Card'),
    )

    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    uploaded_by = filters.CharFilter(name="uploaded_by__username", label="Uploaded By name", lookup_expr="icontains")
    uploaded_by_null = filters.BooleanFilter(name="uploaded_by", label="Is Uploaded By Null", lookup_expr="isnull")

    invoice_number_null = filters.BooleanFilter(name="invoice_number", label="Is Invoice Number Null",
                                                lookup_expr="isnull")
    invoice_number = filters.CharFilter(name="invoice_number", label="Invoice Number", lookup_expr="icontains")

    invoice_receipt_null = filters.BooleanFilter(name="invoice_receipt", label="Is Invoice receipt Null",
                                                 lookup_expr="isnull")
    invoice_receipt = filters.CharFilter(name="invoice_receipt__invoice_number", label="Invoice receipt invoice number",
                                         lookup_expr="icontains")

    s3_upload = filters.CharFilter(name="s3_upload__filename", label="S3 Upload Filename", lookup_expr='icontains')
    s3_upload_null = filters.BooleanFilter(name="s3_upload", label="Is S3 Upload",
                                           lookup_expr="isnull")

    serial = filters.CharFilter(name="serial", label="Serial Url", lookup_expr='icontains')

    verified = filters.BooleanFilter(name="verified", label="Verified", lookup_expr='exact')

    is_valid = filters.BooleanFilter(name="is_valid", label="Is Valid", lookup_expr='exact')

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = InvoiceReceiptFile
        fields = []
