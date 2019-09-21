from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers, ISO_8601
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from driver.models import Driver, DriverAppUser, GPSLogNew, OTP, GPSDevice, GPSDeviceLog, TracknovateGPSDevice, \
    TracknovateGPSDeviceLog, WaytrackerGPSDevice, WaytrackerGPSDeviceLog, TempoGoGPSDevice, TempoGoGPSDeviceLog, \
    SecuGPSDevice, SecuGPSDeviceLog, MahindraGPSDevice, MahindraGPSDeviceLog, BharatGPSTrackerLog, GPSDeviceProvider
from fms.models import Document
from owner.models import Vehicle
from restapi.helper_api import DATE_FORMAT, DATETIME_FORMAT
from restapi.serializers.authentication import BankSerializer
from restapi.service.validators import PAN, MOBILE_NUMBER_REGEX, validate_mobile_number, validate_vehicle_number
from utils.models import TaxationID, IDDetails, Address, Bank


class TrackVehicleSerializer(serializers.Serializer):
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, read_only=True)
    vehicle_status = serializers.ChoiceField(allow_null=True, choices=(
        ('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
                                             required=False, read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False, read_only=True)
    driver_number = serializers.CharField(allow_null=True, max_length=20, required=False, read_only=True)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False, read_only=True)
    device_id = serializers.CharField(max_length=50, read_only=True)
    source = serializers.CharField(max_length=50, read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class DriverSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField( max_length=35, required=True)
    phone = serializers.RegexField(regex=MOBILE_NUMBER_REGEX,
                                   validators=[UniqueValidator(queryset=Driver.objects.all())])
    alt_phone = serializers.RegexField(regex=MOBILE_NUMBER_REGEX, allow_blank=True, allow_null=True, min_length=10,
                                       max_length=10, required=False)
    alt_phone2 = serializers.RegexField(regex=MOBILE_NUMBER_REGEX, allow_blank=True, allow_null=True, min_length=10,
                                        max_length=10, required=False)
    pan = serializers.RegexField(regex=PAN, allow_blank=True, allow_null=True, max_length=11, required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=50, required=False)
    driving_licence_location = serializers.CharField(allow_null=True, max_length=50, required=False)
    driving_licence_validity = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                                     input_formats=[DATE_FORMAT, ISO_8601])
    smartphone_available = serializers.BooleanField(required=False)
    route = serializers.CharField(allow_null=True, allow_blank=True, max_length=255, required=False)
    priority_level = serializers.CharField(allow_null=True, max_length=255, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    address = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Address.objects.all(), required=False,
                                                 validators=[UniqueValidator(queryset=Driver.objects.all())])
    id_proof = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=IDDetails.objects.all(), required=False,
                                                  validators=[UniqueValidator(queryset=Driver.objects.all())])
    account_details = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Bank.objects.all(), required=False,
                                                         validators=[UniqueValidator(queryset=Driver.objects.all())])
    taxation_id = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=TaxationID.objects.all(), required=False,
                                                     validators=[UniqueValidator(queryset=Driver.objects.all())])
    driving_licence = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Document.objects.all(),
                                                         required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = Driver.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        Driver.objects.filter(id=instance.id).update(**validated_data)
        return Driver.objects.get(id=instance.id)


class FMSDriverSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(read_only=True)
    phone = serializers.CharField(read_only=True)
    driving_licence_number = serializers.CharField(read_only=True)
    driving_licence_location = serializers.CharField(read_only=True)
    pan = serializers.CharField(read_only=True)
    driving_licence_validity = serializers.DateField(read_only=True, format=DATE_FORMAT,
                                                     input_formats=[DATE_FORMAT, ISO_8601])
    docs = serializers.SerializerMethodField()
    account_details = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Bank.objects.all(), required=False,
                                                         validators=[UniqueValidator(queryset=Driver.objects.all())])

    def to_representation(self, instance):
        self.fields['account_details'] = BankSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def get_docs(self, instance):
        return [
            {'id': doc.id, 'url': doc.s3_upload.public_url(), 'document_category': doc.document_category,
             'document_category_display': doc.get_document_category_display(),
             'thumb_url': doc.s3_upload.public_url(),
             'bucket': doc.s3_upload.bucket,
             'folder': doc.s3_upload.folder,
             'uuid': doc.s3_upload.uuid,
             'filename': doc.s3_upload.filename,
             'validity': None,
             } for doc in
            instance.driver_files.filter(document_category__in=['DL', 'PAN']).exclude(
                Q(s3_upload=None) | Q(deleted=True))
        ]

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        excluded_fields = [
            'driving_licence_number', 'driving_licence_location', 'driving_licence_validity', 'docs'
        ]
        for field in excluded_fields:
            kwargs['child'].fields.pop(field)
        return serializers.ListSerializer(*args, **kwargs)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class DriverAppUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    device_id = serializers.CharField(max_length=50, validators=[UniqueValidator(queryset=DriverAppUser.objects.all())])
    auth_token = serializers.CharField(max_length=40,
                                       validators=[UniqueValidator(queryset=DriverAppUser.objects.all())])
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    number_verified = serializers.BooleanField(required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(
        choices=(('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
        required=False)
    location_time = serializers.DateTimeField(allow_null=True, required=False)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    is_active = serializers.BooleanField(required=False)
    inactive_sms_sent_at = serializers.DateTimeField(allow_null=True, required=False)
    driver = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Driver.objects.all(), required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def to_representation(self, instance):
        self.fields['driver'] = DriverSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = DriverAppUser.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        DriverAppUser.objects.filter(id=instance.id).update(**validated_data)
        return DriverAppUser.objects.get(id=instance.id)


class GPSLogNewSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    datetime = serializers.DateTimeField(help_text='log time', required=True)
    device_id = serializers.CharField(help_text='imei or uuid generated on phone', max_length=50, required=True)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    altitude = serializers.FloatField(allow_null=True, required=False)
    speed = serializers.FloatField(allow_null=True, required=False)
    course = serializers.FloatField(allow_null=True, required=False)
    accuracy = serializers.FloatField(allow_null=True, required=False)
    provider = serializers.CharField(allow_null=True, max_length=20, required=False)
    battery = serializers.FloatField(allow_null=True, required=False)
    total_memory = serializers.FloatField(allow_null=True, required=False)
    available_memory = serializers.FloatField(allow_null=True, required=False)
    threshold = serializers.FloatField(allow_null=True, required=False)
    low_memory = serializers.BooleanField(required=False)
    android_release = serializers.CharField(allow_null=True, max_length=20, required=False)
    android_sdk_int = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=-2147483648,
                                               required=False)
    version_name = serializers.CharField(allow_null=True, max_length=20, required=False)
    version_code = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=-2147483648,
                                            required=False)
    brand = serializers.CharField(allow_null=True, max_length=30, required=False)
    manufacturer = serializers.CharField(allow_null=True, max_length=30, required=False)
    product = serializers.CharField(allow_null=True, max_length=30, required=False)
    device = serializers.CharField(allow_null=True, max_length=30, required=False)
    model = serializers.CharField(allow_null=True, max_length=30, required=False)
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(allow_null=True, choices=(
        ('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
                                             required=False)
    driver = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=DriverAppUser.objects.all(), required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def to_representation(self, instance):
        self.fields['driver'] = DriverAppUserSerializer(read_only=True)
        return super().to_representation(instance=instance)

    class Meta:
        validators = [UniqueTogetherValidator(queryset=GPSLogNew.objects.all(), fields=('device_id', 'datetime'))]

    def create(self, validated_data):
        instance = GPSLogNew.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        GPSLogNew.objects.filter(id=instance.id).update(**validated_data)
        return GPSLogNew.objects.get(id=instance.id)


class OTPSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    phone = serializers.CharField(max_length=20, validators=[UniqueValidator(queryset=OTP.objects.all())])
    expires_at = serializers.DateTimeField()
    otp = serializers.CharField(max_length=8)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = OTP.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        OTP.objects.filter(id=instance.id).update(**validated_data)
        return OTP.objects.get(id=instance.id)


class GPSDeviceProviderSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(allow_blank=True, allow_null=True, max_length=50, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class GPSDeviceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    device_id = serializers.CharField(allow_null=True, max_length=50, required=False)
    imei = serializers.CharField(allow_null=True, max_length=40, required=False)
    address = serializers.CharField(allow_blank=True, allow_null=True, max_length=500, required=False)
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True,min_length=10, max_length=10, required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_blank=True, allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(
        choices=(('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
        required=False)
    location_time = serializers.DateTimeField(allow_null=True, required=False, format=DATETIME_FORMAT)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    is_active = serializers.BooleanField(required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    device_provider = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=GPSDeviceProvider.objects.all(),
                                                         required=False)
    vehicle = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Vehicle.objects.all(), required=False)
    driver = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Driver.objects.all(), required=False)

    device_provider_data = serializers.SerializerMethodField()

    class Meta:
        validators = [
            UniqueTogetherValidator(queryset=GPSDevice.objects.all(), fields=('device_id', 'device_provider'))]

    def get_device_provider_data(self, instance):
        if isinstance(instance.device_provider, GPSDeviceProvider):
            return {'id': instance.device_provider.id, 'name': instance.device_provider.name}
        return {'id': -1, 'name': None}

    def to_representation(self, instance):
        self.fields['driver'] = DriverSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = GPSDevice.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        GPSDevice.objects.filter(id=instance.id).update(**validated_data)
        return GPSDevice.objects.get(id=instance.id)

    def validate_driver_number(self, value):
        if not validate_mobile_number(value) and value:
            raise serializers.ValidationError("Not a valid mobile number")
        return value

    def validate_vehicle_number(self, value):
        if not validate_vehicle_number(value) and value:
            raise serializers.ValidationError("Not a valid vehicle number")
        return value


class GPSDeviceLogSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    location_id = serializers.CharField(max_length=40,
                                        validators=[UniqueValidator(queryset=GPSDeviceLog.objects.all())])
    datetime = serializers.DateTimeField(help_text='log time')
    vehicle_id = serializers.CharField(help_text='imei or uuid generated on phone', max_length=50)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    altitude = serializers.FloatField(allow_null=True, required=False)
    speed = serializers.FloatField(allow_null=True, required=False)
    course = serializers.FloatField(allow_null=True, required=False)
    accuracy = serializers.FloatField(allow_null=True, required=False)
    engine_on = serializers.BooleanField(required=False)
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(allow_null=True, choices=(
        ('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
                                             required=False)
    device = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=GPSDevice.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields['device'] = GPSDeviceSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = GPSDeviceLog.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        GPSDeviceLog.objects.filter(id=instance.id).update(**validated_data)
        return GPSDeviceLog.objects.get(id=instance.id)


class TracknovateGPSDeviceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    phone = serializers.CharField(max_length=20)
    sim_number = serializers.CharField(max_length=20)
    vehicle_id = serializers.CharField(max_length=40,
                                       validators=[UniqueValidator(queryset=TracknovateGPSDevice.objects.all())])
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    number_verified = serializers.BooleanField(required=False)
    current_duration = serializers.CharField(allow_null=True, required=False, style={'base_template': 'textarea.html'})
    current_vstatus = serializers.CharField(allow_null=True, required=False, style={'base_template': 'textarea.html'})
    driving_licence_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(
        choices=(('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
        required=False)
    location_time = serializers.DateTimeField(allow_null=True, required=False)
    is_active = serializers.BooleanField(required=False)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    inactive_sms_sent_at = serializers.DateTimeField(allow_null=True, required=False)
    driver = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Driver.objects.all(),
                                                required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def to_representation(self, instance):
        self.fields['driver'] = DriverSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = TracknovateGPSDevice.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        TracknovateGPSDevice.objects.filter(id=instance.id).update(**validated_data)
        return TracknovateGPSDevice.objects.get(id=instance.id)


class TracknovateGPSDeviceLogSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    datetime = serializers.DateTimeField(help_text='log time')
    vehicle_id = serializers.CharField(max_length=50)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    altitude = serializers.FloatField(allow_null=True, required=False)
    speed = serializers.FloatField(allow_null=True, required=False)
    course = serializers.FloatField(allow_null=True, required=False)
    accuracy = serializers.FloatField(allow_null=True, required=False)
    engine_on = serializers.BooleanField(required=False)
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(allow_null=True, choices=(
        ('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
                                             required=False)
    device = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=TracknovateGPSDevice.objects.all(),
                                                required=False)

    def to_representation(self, instance):
        self.fields['device'] = TracknovateGPSDeviceSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = TracknovateGPSDeviceLog.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        TracknovateGPSDeviceLog.objects.filter(id=instance.id).update(**validated_data)
        return TracknovateGPSDeviceLog.objects.get(id=instance.id)


class WaytrackerGPSDeviceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    vehicle_id = serializers.CharField(max_length=40,
                                       validators=[UniqueValidator(queryset=WaytrackerGPSDevice.objects.all())])
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    number_verified = serializers.BooleanField(required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(
        choices=(('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
        required=False)
    location_time = serializers.DateTimeField(allow_null=True, required=False)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    is_active = serializers.BooleanField(required=False)
    inactive_sms_sent_at = serializers.DateTimeField(allow_null=True, required=False)
    driver = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Driver.objects.all(),
                                                required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def to_representation(self, instance):
        self.fields['driver'] = DriverSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = WaytrackerGPSDevice.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        WaytrackerGPSDevice.objects.filter(id=instance.id).update(**validated_data)
        return WaytrackerGPSDevice.objects.get(id=instance.id)


class WaytrackerGPSDeviceLogSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    datetime = serializers.DateTimeField(help_text='log time')
    vehicle_id = serializers.CharField(max_length=50)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    altitude = serializers.FloatField(allow_null=True, required=False)
    speed = serializers.FloatField(allow_null=True, required=False)
    course = serializers.FloatField(allow_null=True, required=False)
    accuracy = serializers.FloatField(allow_null=True, required=False)
    engine_on = serializers.BooleanField(required=False)
    fuel = serializers.CharField(allow_null=True, max_length=10, required=False)
    nearest_site = serializers.CharField(allow_null=True, max_length=150, required=False)
    nearest_location = serializers.CharField(allow_null=True, max_length=150, required=False)
    idle_time = serializers.CharField(allow_null=True, max_length=20, required=False)
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(allow_null=True, choices=(
        ('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
                                             required=False)
    device = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=WaytrackerGPSDevice.objects.all(),
                                                required=False)

    def to_representation(self, instance):
        self.fields['device'] = WaytrackerGPSDeviceSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = WaytrackerGPSDeviceLog.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        WaytrackerGPSDeviceLog.objects.filter(id=instance.id).update(**validated_data)
        return WaytrackerGPSDeviceLog.objects.get(id=instance.id)


class TempoGoGPSDeviceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    device_id = serializers.CharField(max_length=50,validators=[UniqueValidator(queryset=TempoGoGPSDevice.objects.all())])
    imei = serializers.CharField(max_length=50,validators=[UniqueValidator(queryset=TempoGoGPSDevice.objects.all())])
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True,min_length=10, max_length=10, required=False)
    number_verified = serializers.BooleanField(required=False)
    driving_licence_number = serializers.CharField(allow_blank=True, allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(
        allow_null=True, max_length=20, validators=[UniqueValidator(queryset=TempoGoGPSDevice.objects.all())],
        required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(
        choices=(('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
        required=False)
    location_time = serializers.DateTimeField(allow_null=True, required=False)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    is_active = serializers.BooleanField(required=False)
    inactive_sms_sent_at = serializers.DateTimeField(allow_null=True, required=False)
    driver = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Driver.objects.all(),
                                                required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", required=False)

    source = serializers.SerializerMethodField()

    def get_source(self, instance):
        if isinstance(instance, TempoGoGPSDevice):
            return "tempo-go"
        return None

    def to_representation(self, instance):
        self.fields['driver'] = DriverSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = TempoGoGPSDevice.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        TempoGoGPSDevice.objects.filter(id=instance.id).update(**validated_data)
        return TempoGoGPSDevice.objects.get(id=instance.id)

    def validate_driver_number(self, value):
        if not validate_mobile_number(value) and value:
            raise serializers.ValidationError("Not a valid mobile number")
        return value

    def validate_vehicle_number(self, value):
        if not validate_vehicle_number(value) and value:
            raise serializers.ValidationError("Not a valid vehicle number")
        return value



class TempoGoGPSDeviceLogSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    gps_log_id = serializers.CharField(max_length=50, required=True)
    datetime = serializers.DateTimeField(help_text='log time', required=True)
    vehicle_id = serializers.CharField(max_length=50)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    speed = serializers.FloatField(allow_null=True, required=False, min_value=0.0)
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True,min_length=10, max_length=10, required=False)
    driving_licence_number = serializers.CharField(allow_blank=True, allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(allow_null=True, choices=(
        ('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
                                             required=False)
    device = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=TempoGoGPSDevice.objects.all(),
                                                required=False)

    class Meta:
        validators = [UniqueTogetherValidator(queryset=TempoGoGPSDeviceLog.objects.all(),
                                              fields=('gps_log_id', 'datetime'))]

    def to_representation(self, instance):
        self.fields['device'] = TempoGoGPSDeviceSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = TempoGoGPSDeviceLog.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        TempoGoGPSDeviceLog.objects.filter(id=instance.id).update(**validated_data)
        return TempoGoGPSDeviceLog.objects.get(id=instance.id)

    def validate_driver_number(self, value):
        if not validate_mobile_number(value) and value:
            raise serializers.ValidationError("Not a valid mobile number")
        return value

    def validate_vehicle_number(self, value):
        if not validate_vehicle_number(value) and value:
            raise serializers.ValidationError("Not a valid vehicle number")
        return value


class SecuGPSDeviceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    device_id = serializers.CharField(max_length=50, validators=[UniqueValidator(queryset=SecuGPSDevice.objects.all())])
    imei = serializers.CharField(max_length=50)
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    number_verified = serializers.BooleanField(required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(
        choices=(('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
        required=False)
    location_time = serializers.DateTimeField(allow_null=True, required=False)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    address = serializers.CharField(allow_null=True, max_length=300, required=False)
    status = serializers.CharField(allow_null=True, max_length=300, required=False)
    is_active = serializers.BooleanField(required=False)
    inactive_sms_sent_at = serializers.DateTimeField(allow_null=True, required=False)
    driver = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Driver.objects.all(), required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def to_representation(self, instance):
        self.fields['driver'] = DriverSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = SecuGPSDevice.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        SecuGPSDevice.objects.filter(id=instance.id).update(**validated_data)
        return SecuGPSDevice.objects.get(id=instance.id)


class SecuGPSDeviceLogSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    datetime = serializers.DateTimeField(help_text='log time')
    vehicle_id = serializers.CharField(max_length=50)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    speed = serializers.FloatField(allow_null=True, required=False)
    address = serializers.CharField(allow_null=True, max_length=300, required=False)
    status = serializers.CharField(allow_null=True, max_length=300, required=False)
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(allow_null=True, choices=(
        ('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
                                             required=False)
    device = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=SecuGPSDevice.objects.all(),
                                                required=False)

    def to_representation(self, instance):
        self.fields['device'] = SecuGPSDeviceSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = SecuGPSDeviceLog.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        SecuGPSDeviceLog.objects.filter(id=instance.id).update(**validated_data)
        return SecuGPSDeviceLog.objects.get(id=instance.id)


class MahindraGPSDeviceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    device_id = serializers.CharField(max_length=50,
                                      validators=[UniqueValidator(queryset=MahindraGPSDevice.objects.all())])
    imei = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True,min_length=10, max_length=10, required=False)
    number_verified = serializers.BooleanField(required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=20, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(
        choices=(('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
        required=False)
    location_time = serializers.DateTimeField(allow_null=True, required=False)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    address = serializers.CharField(allow_null=True, max_length=300, required=False)
    status = serializers.CharField(allow_null=True, max_length=300, required=False)
    is_active = serializers.BooleanField(required=False)
    inactive_sms_sent_at = serializers.DateTimeField(allow_null=True, required=False)
    driver = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Driver.objects.all(),
                                                required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    source = serializers.SerializerMethodField()

    def get_source(self, instance):
        if isinstance(instance, MahindraGPSDevice):
            return "mahindra-gps-device"
        return None

    def to_representation(self, instance):
        self.fields['driver'] = DriverSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = MahindraGPSDevice.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        MahindraGPSDevice.objects.filter(id=instance.id).update(**validated_data)
        return MahindraGPSDevice.objects.get(id=instance.id)

    def validate_driver_number(self, value):
        if not validate_mobile_number(value) and value:
            raise serializers.ValidationError("Not a valid mobile number")
        return value

    def validate_vehicle_number(self, value):
        if not validate_vehicle_number(value) and value:
            raise serializers.ValidationError("Not a valid vehicle number")
        return value

class MahindraGPSDeviceLogSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    datetime = serializers.DateTimeField(help_text='log time')
    vehicle_id = serializers.CharField(max_length=50)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    speed = serializers.FloatField(allow_null=True, required=False,min_value=0.0)
    fuel_efficiency = serializers.CharField(allow_null=True, max_length=30, required=False)
    address = serializers.CharField(allow_null=True, max_length=300, required=False)
    status = serializers.CharField(allow_null=True, max_length=300, required=False)
    driver_name = serializers.CharField(allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_null=True,min_length=10, max_length=10, required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(allow_null=True, choices=(
        ('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
                                             required=False)
    device = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=MahindraGPSDevice.objects.all(),
                                                required=False)

    def to_representation(self, instance):
        self.fields['device'] = MahindraGPSDeviceSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = MahindraGPSDeviceLog.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        MahindraGPSDeviceLog.objects.filter(id=instance.id).update(**validated_data)
        return MahindraGPSDeviceLog.objects.get(id=instance.id)

    def validate_driver_number(self, value):
        if not validate_mobile_number(value) and value:
            raise serializers.ValidationError("Not a valid mobile number")
        return value

    def validate_vehicle_number(self, value):
        if not validate_vehicle_number(value) and value:
            raise serializers.ValidationError("Not a valid vehicle number")
        return value

class BharatGPSTrackerLogSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    position_id = serializers.CharField(max_length=30,
                                        validators=[UniqueValidator(queryset=BharatGPSTrackerLog.objects.all())],
                                        allow_null=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    datetime = serializers.DateTimeField(help_text='log time', input_formats=['%d-%m-%Y %H:%M:%S', ISO_8601])
    latitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=10, max_digits=20, required=False)
    speed = serializers.FloatField(allow_null=True, required=False)
    address = serializers.CharField(allow_null=True, max_length=300, required=False)
    status = serializers.CharField(allow_null=True, max_length=300, required=False)
    driver_name = serializers.CharField(allow_blank=True, allow_null=True, max_length=50, required=False)
    driver_number = serializers.CharField(allow_blank=True, allow_null=True, max_length=40, required=False)
    driving_licence_number = serializers.CharField(allow_blank=True, allow_null=True, max_length=40, required=False)
    vehicle_number = serializers.CharField(allow_blank=True, allow_null=True, max_length=40, required=False)
    vehicle_type = serializers.CharField(allow_blank=True, allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(allow_blank=True, allow_null=True, choices=(
        ('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
                                             required=False)
    device = serializers.PrimaryKeyRelatedField(queryset=GPSDevice.objects.all())

    def create(self, validated_data):
        instance = BharatGPSTrackerLog.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        BharatGPSTrackerLog.objects.filter(id=instance.id).update(**validated_data)
        return BharatGPSTrackerLog.objects.get(id=instance.id)

