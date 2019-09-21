from datetime import datetime

from django.contrib.auth.models import User
from rest_framework import serializers, ISO_8601
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from api import s3util
from api.models import S3Upload
from api.utils import get_ext
from driver.models import Driver
from fileupload.models import PODFile, VehicleFile, OwnerFile, DriverFile, ChequeFile, InvoiceReceiptFile, WeighingSlip
from owner.models import Vehicle, Owner
from restapi.helper_api import DATE_FORMAT, DATETIME_FORMAT
from restapi.serializers.api import S3UploadSerializer
from restapi.serializers.authentication import UserSerializer
from restapi.serializers.driver import DriverSerializer
from restapi.serializers.owner import OwnerSerializer, VehicleSerializer
from restapi.serializers.sme import SmeSerializer
from restapi.serializers.team import LrNumberSerializer, ManualBookingSerializer, InvoiceSerializer
from sme.models import Sme
from team.models import LrNumber, ManualBooking, Invoice


class BasicPODFileSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    url = serializers.SerializerMethodField()
    lr = serializers.SerializerMethodField()
    booking = serializers.SerializerMethodField()

    def get_lr(self, instance):
        if isinstance(instance.lr_number, LrNumber):
            return {'id': instance.lr_number.id, 'lr_number': instance.lr_number.lr_number}
        return {}

    def get_booking(self, instance):
        if isinstance(instance.booking, ManualBooking):
            return {'id': instance.booking.id, 'booking_id': instance.booking.booking_id}
        return {}

    def get_url(self, instance):
        if isinstance(instance, PODFile) and isinstance(instance.s3_upload, S3Upload):
            return instance.s3_upload.public_url()
        return None

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PODFileSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    s3_thumb_url = serializers.URLField(allow_null=True, max_length=200, required=False,
                                        validators=[UniqueValidator(queryset=PODFile.objects.all())])
    serial = serializers.CharField(max_length=20)
    s3_url = serializers.URLField(required=False)
    verified = serializers.BooleanField(default=False)
    is_valid = serializers.BooleanField(default=False)
    verified_datetime = serializers.DateTimeField(
        allow_null=True, required=False, format=DATE_FORMAT, input_formats=DATETIME_FORMAT)
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT, input_formats=DATE_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    uploaded_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    verified_by = serializers.SlugRelatedField(allow_null=True, queryset=User.objects.all(), required=False,
                                               slug_field="username")
    lr_number = serializers.PrimaryKeyRelatedField(write_only=True, allow_null=True, queryset=LrNumber.objects.all(),
                                                   required=True)
    booking = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ManualBooking.objects.all())
    s3_upload = serializers.PrimaryKeyRelatedField(queryset=S3Upload.objects.all(), write_only=True, required=False)
    s3_upload_url = serializers.SerializerMethodField()

    # upload_file = serializers.SerializerMethodField()
    lr_number_data = serializers.SerializerMethodField()
    booking_id = serializers.SerializerMethodField()

    def get_lr_number_data(self, instance):
        if isinstance(instance.lr_number, LrNumber):
            return instance.lr_number.lr_number
        return None

    def get_booking_id(self, instance):
        if isinstance(instance.booking, ManualBooking):
            return instance.booking.booking_id
        return None

    class Meta:
        validators = [UniqueTogetherValidator(queryset=PODFile.objects.all(), fields=('lr_number', 'serial'))]

    def validate_created_by(self, value):
        if isinstance(self.instance, PODFile) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def validate_uploaded_by(self, value):
        if isinstance(self.instance, PODFile) and value:
            raise serializers.ValidationError("Uploaded by is immutable")
        return value

    def get_s3_upload_url(self, instance):
        if isinstance(instance, PODFile) and isinstance(instance.s3_upload, S3Upload):
            return instance.s3_upload.public_url()
        return None

    def create(self, validated_data):
        instance = PODFile.objects.create(**validated_data)
        if isinstance(instance.booking, ManualBooking):
            ManualBooking.objects.filter(id=instance.booking.id).update(
                pod_status='unverified', pod_date=datetime.now())
        return instance

    def update(self, instance, validated_data):
        PODFile.objects.filter(id=instance.id).update(**validated_data)
        return PODFile.objects.get(id=instance.id)


class WeighingSlipSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    s3_thumb_url = serializers.URLField(allow_null=True, max_length=200, required=False,
                                        validators=[UniqueValidator(queryset=WeighingSlip.objects.all())])
    serial = serializers.CharField(max_length=20)
    s3_url = serializers.URLField(required=False)
    verified = serializers.BooleanField(default=False)
    is_valid = serializers.BooleanField(default=False)
    verified_datetime = serializers.DateTimeField(
        allow_null=True, required=False, format=DATE_FORMAT, input_formats=DATETIME_FORMAT)
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT, input_formats=DATE_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    uploaded_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    verified_by = serializers.SlugRelatedField(allow_null=True, queryset=User.objects.all(), required=False,
                                               slug_field="username")

    booking = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ManualBooking.objects.all())
    s3_upload = serializers.PrimaryKeyRelatedField(queryset=S3Upload.objects.all(), write_only=True, required=False)
    s3_upload_url = serializers.SerializerMethodField()

    # upload_file = serializers.SerializerMethodField()
    lr_number_data = serializers.SerializerMethodField()
    booking_id = serializers.SerializerMethodField()

    def get_lr_number_data(self, instance):
        if isinstance(instance.lr_number, LrNumber):
            return instance.lr_number.lr_number
        return None

    def get_booking_id(self, instance):
        if isinstance(instance.booking, ManualBooking):
            return instance.booking.booking_id
        return None

    def validate_created_by(self, value):
        if isinstance(self.instance, WeighingSlip) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def validate_uploaded_by(self, value):
        if isinstance(self.instance, WeighingSlip) and value:
            raise serializers.ValidationError("Uploaded by is immutable")
        return value

    def get_s3_upload_url(self, instance):
        if isinstance(instance, WeighingSlip) and isinstance(instance.s3_upload, S3Upload):
            return instance.s3_upload.public_url()
        return None

    def create(self, validated_data):
        instance = WeighingSlip.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        WeighingSlip.objects.filter(id=instance.id).update(**validated_data)
        return WeighingSlip.objects.get(id=instance.id)


class VehicleFileSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    document_category = serializers.ChoiceField(choices=(
        ('PUC', 'Puc Certificate'), ('FIT', 'Fitness Certificate'), ('REG', 'Registration Certificate'),
        ('PERM', 'Permission Certificate'), ('INS', 'Insurance Certificate')))
    s3_url = serializers.URLField(max_length=200, validators=[UniqueValidator(queryset=VehicleFile.objects.all())])
    s3_thumb_url = serializers.URLField(allow_null=True, max_length=200, required=False,
                                        validators=[UniqueValidator(queryset=VehicleFile.objects.all())])
    serial = serializers.CharField(max_length=20)
    verified = serializers.BooleanField()
    is_valid = serializers.BooleanField()
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    uploaded_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(),required=False)
    s3_upload = serializers.PrimaryKeyRelatedField(queryset=S3Upload.objects.all())

    # class Meta:
    #     validators = [UniqueTogetherValidator(queryset=VehicleFile.objects.all(), fields=('vehicle', 'serial'))]

    def validate_created_by(self, value):
        if isinstance(self.instance, VehicleFile) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def validate_uploaded_by(self, value):
        if isinstance(self.instance, VehicleFile) and value:
            raise serializers.ValidationError("Uploaded by is immutable")
        return value

    def to_representation(self, instance):
        self.fields["vehicle"] = VehicleSerializer(read_only=True)
        self.fields["booking"] = ManualBookingSerializer(read_only=True)
        self.fields["s3_upload"] = S3UploadSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = VehicleFile.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        VehicleFile.objects.filter(id=instance.id).update(**validated_data)
        return VehicleFile.objects.get(id=instance.id)


class OwnerFileSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    document_category = serializers.ChoiceField(choices=(
        ('PAN', 'PAN Card'), ('DL', 'Driving Licence'), ('EL', 'Election ID'), ('AC', 'Aadhar Card'),
        ('PT', 'Passport'),
        ('RC', 'Ration Card'), ('DEC', 'Declaration')))
    s3_url = serializers.URLField(max_length=200, validators=[UniqueValidator(queryset=OwnerFile.objects.all())])
    s3_thumb_url = serializers.URLField(allow_null=True, max_length=200, required=False,
                                        validators=[UniqueValidator(queryset=OwnerFile.objects.all())])
    serial = serializers.CharField(max_length=20, required=True)
    verified = serializers.BooleanField(required=False)
    is_valid = serializers.BooleanField()
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    uploaded_by = serializers.SlugRelatedField(allow_null=True, queryset=User.objects.all(), required=False,
                                               slug_field="username")
    owner = serializers.PrimaryKeyRelatedField(queryset=Owner.objects.all(),allow_null=True, required=False)
    s3_upload = serializers.PrimaryKeyRelatedField(queryset=S3Upload.objects.all())

    # class Meta:
    #     validators = [UniqueTogetherValidator(queryset=OwnerFile.objects.all(), fields=('owner', 'serial'))]

    def validate_created_by(self, value):
        if isinstance(self.instance, OwnerFile) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def validate_uploaded_by(self, value):
        if isinstance(self.instance, OwnerFile) and value:
            raise serializers.ValidationError("Uploaded by is immutable")
        return value

    def to_representation(self, instance):

        self.fields["owner"] = OwnerSerializer(read_only=True)
        self.fields["s3_upload"] = S3UploadSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = OwnerFile.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        OwnerFile.objects.filter(id=instance.id).update(**validated_data)
        return OwnerFile.objects.get(id=instance.id)


class DriverFileSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    document_category = serializers.ChoiceField(allow_null=True, choices=(
        ('PAN', 'PAN Card'), ('DL', 'Driving Licence'), ('EL', 'Election ID'), ('AC', 'Aadhar Card'),
        ('PT', 'Passport'),
        ('RC', 'Ration Card')), required=False)
    s3_url = serializers.URLField(max_length=200, validators=[UniqueValidator(queryset=DriverFile.objects.all())])
    s3_thumb_url = serializers.URLField(allow_null=True, max_length=200, required=False,
                                        validators=[UniqueValidator(queryset=DriverFile.objects.all())])
    verified = serializers.BooleanField()
    is_valid = serializers.BooleanField()
    serial = serializers.CharField(max_length=20)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    uploaded_by = serializers.SlugRelatedField(allow_null=True, queryset=User.objects.all(), required=False,
                                               slug_field="username")
    driver = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all(), required=False)
    s3_upload = serializers.PrimaryKeyRelatedField(queryset=S3Upload.objects.all())

    # class Meta:
    #     validators = [UniqueTogetherValidator(queryset=DriverFile.objects.all(), fields=('driver', 'serial'))]

    def validate_created_by(self, value):
        if isinstance(self.instance, DriverFile) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def validate_uploaded_by(self, value):
        if isinstance(self.instance, DriverFile) and value:
            raise serializers.ValidationError("Uploaded by is immutable")
        return value

    def to_representation(self, instance):

        self.fields["driver"] = DriverSerializer(read_only=True)
        self.fields["s3_upload"] = S3UploadSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = DriverFile.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        DriverFile.objects.filter(id=instance.id).update(**validated_data)
        return DriverFile.objects.get(id=instance.id)


class ChequeFileSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    s3_url = serializers.URLField(allow_null=True, max_length=200, required=False,
                                  validators=[UniqueValidator(queryset=ChequeFile.objects.all())])
    resolved_datetime = serializers.DateTimeField(allow_null=True, required=False)
    customer_name = serializers.CharField(max_length=300)
    amount = serializers.IntegerField(max_value=50000000, min_value=0, required=False)
    cheque_number = serializers.CharField(max_length=6, min_length=6)
    cheque_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, ISO_8601])
    remarks = serializers.CharField(allow_null=True, max_length=300, required=False)
    is_valid = serializers.BooleanField()
    resolved = serializers.BooleanField(required=False)
    serial = serializers.CharField(max_length=20, required=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    uploaded_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    resolved_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    customer = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Sme.objects.all(), required=False)
    s3_upload = serializers.PrimaryKeyRelatedField(queryset=S3Upload.objects.all())

    public_url = serializers.SerializerMethodField()

    class Meta:
        validators = [UniqueTogetherValidator(queryset=ChequeFile.objects.all(), fields=('customer_name', 'serial'))]

    def validate_created_by(self, value):
        if isinstance(self.instance, ChequeFile) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def get_public_url(self, instance):
        if isinstance(instance, ChequeFile) and isinstance(instance.s3_upload, S3Upload):
            return instance.s3_upload.public_url()
        return None

    def validate_uploaded_by(self, value):
        if isinstance(self.instance, ChequeFile) and value:
            raise serializers.ValidationError("Uploaded by is immutable")
        return value

    def to_representation(self, instance):
        # self.fields["customer"] = SmeSerializer(read_only=True)
        self.fields["s3_upload"] = S3UploadSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = ChequeFile.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        ChequeFile.objects.filter(id=instance.id).update(**validated_data)
        return ChequeFile.objects.get(id=instance.id)


class InvoiceReceiptFileSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    invoice_number = serializers.CharField(max_length=50, required=False)
    verified = serializers.BooleanField(default=False)
    is_valid = serializers.BooleanField(default=False)
    serial = serializers.CharField(max_length=20, required=False)
    invoice_sent_mode = serializers.CharField(allow_null=True, allow_blank=True, max_length=20, required=False)
    invoice_confirm_mode = serializers.CharField(allow_null=True, max_length=20, required=False)
    invoice_confirm_by_name = serializers.CharField(allow_null=True, max_length=20, required=False)
    invoice_confirm_by_phone = serializers.CharField(allow_null=True, allow_blank=True, max_length=20, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    uploaded_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    invoice_receipt = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Invoice.objects.all(),
                                                         required=False)
    s3_upload = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=S3Upload.objects.all(), required=False)

    def validate_created_by(self, value):
        if isinstance(self.instance, InvoiceReceiptFile) and value:
            raise serializers.ValidationError("Created by is immutable")
        return value

    def validate_uploaded_by(self, value):
        if isinstance(self.instance, InvoiceReceiptFile) and value:
            raise serializers.ValidationError("Uploaded by is immutable")
        return value

    def validate_deleted(self, attrs):
        if isinstance(self.instance, InvoiceReceiptFile) and not attrs:
            if InvoiceReceiptFile.objects.filter(invoice_number=self.instance.invoice_number):
                raise serializers.ValidationError("Invoice number must be unique")
        return attrs

    def to_representation(self, instance):
        # self.fields["invoice_receipt"] = InvoiceSerializer(read_only=True)
        self.fields["s3_upload"] = S3UploadSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = InvoiceReceiptFile.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        InvoiceReceiptFile.objects.filter(id=instance.id).update(**validated_data)
        return InvoiceReceiptFile.objects.get(id=instance.id)
