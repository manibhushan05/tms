from django.contrib.auth.models import User
from rest_framework import serializers, ISO_8601
from rest_framework.validators import UniqueValidator

from authentication.models import Profile
from driver.models import Driver, DriverAppUser
from owner.models import Route, Owner, Vehicle, FuelCard, FuelCardTransaction, VehicleSummary
from owner.vehicle_util import display_format
from restapi.helper_api import DATE_FORMAT
from restapi.serializers.authentication import ProfileSerializer, BankSerializer
from restapi.serializers.utils import CitySerializer
from restapi.service.validators import validate_vehicle_number, validate_pan
from utils.models import Address, City, VehicleCategory, Bank


class RouteSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    source = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    destination = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    def to_representation(self, instance):
        self.fields["source"] = CitySerializer(read_only=True)
        self.fields["destination"] = CitySerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = Route.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        Route.objects.filter(id=instance.id).update(**validated_data)
        return Route.objects.get(id=instance.id)


class OwnerSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    owner_address = serializers.CharField(allow_null=True, min_length=3, max_length=300, required=False)
    pin = serializers.CharField(max_length=6, min_length=6, required=False)
    route_temp = serializers.CharField(allow_null=True, min_length=3, max_length=300, required=False)
    pan = serializers.CharField(allow_null=True, max_length=11, required=False,
                                validators=[UniqueValidator(queryset=Owner.objects.all())])
    declaration = serializers.CharField(allow_null=True, max_length=255, required=False)
    declaration_validity = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                                 input_formats=[DATE_FORMAT, ISO_8601])
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT, input_formats=[DATE_FORMAT, ISO_8601])
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    name = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), validators=[UniqueValidator(queryset=Owner.objects.all())], required=False)

    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    account_details = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Bank.objects.all(),
                                                         required=False,
                                                         validators=[UniqueValidator(queryset=Owner.objects.all())])

    address = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Address.objects.all(), required=False,
                                                 validators=[UniqueValidator(queryset=Owner.objects.all())])
    owner_profile = serializers.SerializerMethodField()
    vehicle_list = serializers.SerializerMethodField()
    city_data = serializers.SerializerMethodField()
    owner_phone = serializers.CharField(write_only=True, required=False)

    def validate_owner_phone(self, attrs):
        if Owner.objects.exclude(deleted=True).filter(name__profile__phone=attrs).exists():
            raise serializers.ValidationError("Owner Phone must be unique")
        return attrs

    def validate_pan(self,attrs):
        if attrs and not validate_pan(attrs):
            raise  serializers.ValidationError('PAN is not valid')
        return attrs

    def get_city_data(self, instance):
        if isinstance(instance.city, City):
            return {'id': instance.city.id, 'name': instance.city.name, 'state': instance.city.state_name}
        return {}

    def get_vehicle_list(self, instance):
        if isinstance(instance, Owner):
            return [{'id': vehicle.id, 'vehicle_number': vehicle.number()} for vehicle in
                    Vehicle.objects.filter(owner=instance)]
        return []

    def get_owner_profile(self, instance):
        if isinstance(instance.name, User) and isinstance(instance.name.profile, Profile):
            return ProfileSerializer(instance.name.profile).data
        return {}

    def create(self, validated_data):
        routes = []
        if "route" in validated_data.keys():
            routes = validated_data.pop('route')

        validated_data.pop("owner_phone")

        instance = Owner.objects.create(**validated_data)
        for route in routes:
            instance.route.add(route)

        return instance

    def update(self, instance, validated_data):
        routes = []
        if "route" in validated_data.keys():
            instance.route.clear()
            routes = validated_data.pop('route')
        Owner.objects.filter(id=instance.id).update(**validated_data)

        for route in routes:
            instance.route.add(route)
        return Owner.objects.get(id=instance.id)


class VehicleSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    vehicle_number = serializers.CharField(max_length=18, validators=[UniqueValidator(queryset=Vehicle.objects.all())])
    rc_number = serializers.CharField(allow_null=True,min_length=3 ,max_length=20, required=False)
    permit = serializers.CharField(allow_null=True,min_length=3, max_length=25, required=False)

    permit_validity = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                            input_formats=[DATE_FORMAT, ISO_8601])

    permit_type = serializers.CharField(allow_null=True,min_length=3 ,max_length=70, required=False)
    vehicle_capacity = serializers.IntegerField(allow_null=True, label='Exact Vehicle Capacity in Kg',
                                                max_value=2147483647,
                                                min_value=-2147483648, required=False)
    body_type = serializers.ChoiceField( choices=(
        ('open', 'Open'), ('closed', 'Closed'), ('semi', 'Semi'), ('half', 'Half'), ('containerized', 'Containerized')),
                                        required=True)
    vehicle_model = serializers.CharField(allow_null=True, min_length=3,max_length=30, required=False)
    chassis_number = serializers.CharField(allow_null=True,min_length=3, max_length=255, required=False)
    engine_number = serializers.CharField(allow_null=True,min_length=3, max_length=255, required=False)
    insurer = serializers.CharField(allow_null=True,min_length=3, max_length=100, required=False)
    insurance_number = serializers.CharField(allow_null=True,min_length=3, max_length=30, required=False)
    insurance_validity = serializers.DateField(allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601],
                                               format=DATE_FORMAT)
    registration_year = serializers.DateField(allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601],
                                              format=DATE_FORMAT)
    registration_validity = serializers.DateField(allow_null=True, required=False,
                                                  input_formats=[DATE_FORMAT, ISO_8601],
                                                  format=DATE_FORMAT)
    fitness_certificate_number = serializers.CharField(
        allow_null=True,min_length=3, max_length=255, required=False)
    fitness_certificate_issued_on = serializers.DateField(
        allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601], format=DATE_FORMAT)
    fitness_certificate_validity_date = serializers.DateField(
        allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601], format=DATE_FORMAT)
    puc_certificate_number = serializers.CharField(allow_null=True, min_length=3,max_length=255, required=False)
    puc_certificate_issued_on = serializers.DateField(
        allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601], format=DATE_FORMAT)
    puc_certificate_validity_date = serializers.DateField(
        allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601], format=DATE_FORMAT)

    status = serializers.ChoiceField(
        choices=(('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
        required=False)
    gps_enabled = serializers.BooleanField(required=False)
    supplier_name = serializers.CharField(allow_null=True, max_length=70, required=False)
    supplier_phone = serializers.CharField(allow_null=True, max_length=30, required=False)
    owner_name = serializers.CharField(allow_null=True, max_length=70, required=False)
    owner_phone = serializers.CharField(allow_null=True, max_length=30, required=False)
    updated_on = serializers.DateTimeField(read_only=True)
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)

    owner = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Owner.objects.all(), required=False)
    driver = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Driver.objects.all(), required=False,
                                                validators=[UniqueValidator(queryset=Vehicle.objects.all())])
    driver_app_user = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=DriverAppUser.objects.all(),
                                                         required=False)
    vehicle_type = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=VehicleCategory.objects.all(),
                                                      required=False)
    route = serializers.PrimaryKeyRelatedField(many=True, queryset=Route.objects.all(), required=False)
    bank_account = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Bank.objects.all(), required=False)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    owner_data = serializers.SerializerMethodField()
    vehicle_type_data = serializers.SerializerMethodField()
    vehicle_number_display = serializers.SerializerMethodField()
    driver_data = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    def validate_vehicle_number(self, value):
        if not validate_vehicle_number(value) and value:
            raise serializers.ValidationError("Not a valid vehicle number")
        return value

    def get_driver_data(self, instance):
        if isinstance(instance.driver, Driver):
            return {
                'id': instance.driver.id, 'name': instance.driver.name, 'phone': instance.driver.phone,
                'dl_number': instance.driver.driving_licence_number,
                'dl_validity': instance.driver.driving_licence_validity.strftime(
                    DATE_FORMAT) if instance.driver.driving_licence_validity else None,
                'dl_location': instance.driver.driving_licence_location}
        return {'id': '-1', 'name': '-', 'phone': None, 'dl_number': None, 'dl_validity': None, 'dl_location': None}

    def get_vehicle_number_display(self, instance):
        return display_format(instance.vehicle_number)

    def get_owner_data(self, instance):
        if isinstance(instance.owner, Owner):
            return {'id': instance.owner.id, 'name': instance.owner.get_name(), 'phone': instance.owner.get_phone()}
        return {'id': -1, 'name': '-', 'phone': '-'}

    def get_vehicle_type_data(self, instance):
        if isinstance(instance.vehicle_type, VehicleCategory):
            return {'id': instance.vehicle_type.id, 'name': instance.vehicle_type.get_name()}
        return {'id': 0, 'name': '-'}

    def get_documents(self, instance):
        if isinstance(instance, Vehicle):
            return [{'id': doc.id, 'url': doc.s3_upload.public_url(), 'document_category': doc.document_category,
                     'document_category_display': doc.get_document_category_display(),
                     'thumb_url': doc.s3_upload.public_url(),
                     'bucket': doc.s3_upload.bucket,
                     'folder': doc.s3_upload.folder,
                     'uuid': doc.s3_upload.uuid,
                     'filename': doc.s3_upload.filename,
                     'validity': None,
                     } for doc in
                    instance.vehicle_files.exclude(deleted=True).exclude(s3_upload=None).order_by('id')]
        return []

    def create(self, validated_data):
        routes = []
        if "route" in validated_data.keys():
            routes = validated_data.pop('route')
        instance = Vehicle.objects.create(**validated_data)
        for route in routes:
            instance.route.add(route)
        return instance

    def update(self, instance, validated_data):
        routes = []
        if "route" in validated_data.keys():
            instance.route.clear()
            routes = validated_data.pop('route')
        Vehicle.objects.filter(id=instance.id).update(**validated_data)
        for route in routes:
            instance.route.add(route)
        return Vehicle.objects.get(id=instance.id)


class VehicleSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    accounting_summary = serializers.JSONField(style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(),
                                                 validators=[UniqueValidator(queryset=VehicleSummary.objects.all())])

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class FMSVehicleSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    vehicle_number = serializers.CharField(write_only=True, max_length=18,
                                           validators=[UniqueValidator(queryset=Vehicle.objects.all())])
    rc_number = serializers.CharField(allow_null=True ,max_length=20, required=False)
    permit = serializers.CharField(allow_null=True,min_length=3, max_length=25, required=False)

    permit_validity = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                            input_formats=[DATE_FORMAT, ISO_8601])

    permit_type = serializers.CharField(allow_null=True, max_length=70, required=False)
    vehicle_capacity = serializers.IntegerField(allow_null=True, label='Exact Vehicle Capacity in Kg',
                                                max_value=2147483647,
                                                min_value=-2147483648, required=False)
    body_type = serializers.ChoiceField(allow_null=True, choices=(
        ('open', 'Open'), ('closed', 'Closed'), ('semi', 'Semi'), ('half', 'Half'), ('containerized', 'Containerized')),
                                        required=False)
    vehicle_model = serializers.CharField(allow_null=True, max_length=30, required=False)
    chassis_number = serializers.CharField(allow_null=True, max_length=255, required=False)
    engine_number = serializers.CharField(allow_null=True, max_length=255, required=False)
    insurer = serializers.CharField(allow_null=True, max_length=100, required=False)
    insurance_number = serializers.CharField(allow_null=True, max_length=30, required=False)
    insurance_validity = serializers.DateField(allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601],
                                               format=DATE_FORMAT)
    registration_year = serializers.DateField(allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601],
                                              format='%Y')
    registration_validity = serializers.DateField(allow_null=True, required=False,
                                                  input_formats=[DATE_FORMAT, ISO_8601],
                                                  format=DATE_FORMAT)
    fitness_certificate_number = serializers.CharField(
        allow_null=True, max_length=255, required=False)
    fitness_certificate_issued_on = serializers.DateField(
        allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601], format=DATE_FORMAT)
    fitness_certificate_validity_date = serializers.DateField(
        allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601], format=DATE_FORMAT)
    puc_certificate_number = serializers.CharField(allow_null=True, max_length=255, required=False)
    puc_certificate_issued_on = serializers.DateField(
        allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601], format=DATE_FORMAT)
    puc_certificate_validity_date = serializers.DateField(
        allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601], format=DATE_FORMAT)

    status = serializers.ChoiceField(
        choices=(('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
        required=False)
    gps_enabled = serializers.BooleanField(required=False)
    supplier_name = serializers.CharField(allow_null=True, max_length=70, required=False)
    supplier_phone = serializers.CharField(allow_null=True, max_length=30, required=False)
    owner_name = serializers.CharField(allow_null=True, max_length=70, required=False)
    owner_phone = serializers.CharField(allow_null=True, max_length=30, required=False)
    updated_on = serializers.DateTimeField(read_only=True)
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)

    owner = serializers.PrimaryKeyRelatedField(write_only=True, allow_null=True, queryset=Owner.objects.all(),
                                               required=False)
    driver = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Driver.objects.all(), required=False,
                                                validators=[UniqueValidator(queryset=Vehicle.objects.all())])
    driver_app_user = serializers.PrimaryKeyRelatedField(write_only=True, allow_null=True,
                                                         queryset=DriverAppUser.objects.all(),
                                                         required=False)
    vehicle_type = serializers.PrimaryKeyRelatedField(write_only=True, allow_null=True,
                                                      queryset=VehicleCategory.objects.all(),
                                                      required=False)
    route = serializers.PrimaryKeyRelatedField(many=True, queryset=Route.objects.all(), required=False)
    bank_account = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Bank.objects.all(), required=False)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    owner_data = serializers.SerializerMethodField()
    vehicle_type_data = serializers.SerializerMethodField()
    vehicle_number_display = serializers.SerializerMethodField()
    driver_data = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    def get_driver_data(self, instance):
        if isinstance(instance.driver, Driver):
            return {'id': instance.driver.id, 'name': instance.driver.name, 'phone': instance.driver.phone,
                    'dl_number': instance.driver.driving_licence_number,
                    'dl_validity': instance.driver.driving_licence_validity.strftime(
                        DATE_FORMAT) if instance.driver.driving_licence_validity else None,
                    'dl_location': instance.driver.driving_licence_location}
        return {'id': '-1', 'name': '-', 'phone': None, 'dl_number': None, 'dl_validity': None, 'dl_location': None}

    def to_representation(self, instance):
        self.fields['bank_account'] = BankSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def get_vehicle_number_display(self, instance):
        return display_format(instance.vehicle_number)

    def get_owner_data(self, instance):
        if isinstance(instance.owner, Owner):
            return {'id': instance.owner.id, 'name': instance.owner.get_name(), 'phone': instance.owner.get_phone(),
                    'pan': instance.owner.pan, 'declaration_validity': instance.owner.declaration_validity.strftime(
                    DATE_FORMAT) if instance.owner.declaration_validity else None}
        return {'id': -1, 'name': None, 'phone': None, 'pan': None, 'declaration_validity': None}

    def get_vehicle_type_data(self, instance):
        if isinstance(instance.vehicle_type, VehicleCategory):
            return {'id': instance.vehicle_type.id, 'name': instance.vehicle_type.get_name()}
        return {'id': 0, 'name': '-'}

    def get_documents(self, instance):
        vehicle_docs = [{'id': doc.id, 'url': doc.s3_upload.public_url(), 'document_category': doc.document_category,
                         'document_category_display': doc.get_document_category_display(),
                         'thumb_url': doc.s3_upload.public_url(),
                         'bucket': doc.s3_upload.bucket,
                         'folder': doc.s3_upload.folder,
                         'uuid': doc.s3_upload.uuid,
                         'filename': doc.s3_upload.filename,
                         'validity': None,
                         } for doc in
                        instance.vehicle_files.exclude(deleted=True).exclude(s3_upload=None)]
        if isinstance(instance.owner, Owner):
            owner_docs = [{'id': doc.id, 'url': doc.s3_upload.public_url(), 'document_category': doc.document_category,
                           'document_category_display': doc.get_document_category_display(),
                           'thumb_url': doc.s3_upload.public_url(),
                           'bucket': doc.s3_upload.bucket,
                           'folder': doc.s3_upload.folder,
                           'uuid': doc.s3_upload.uuid,
                           'filename': doc.s3_upload.filename,
                           'validity': None,
                           } for doc in
                          instance.owner.owner_files.exclude(s3_upload=None)]
        else:
            owner_docs = []
        if isinstance(instance.driver, Driver):
            driver_docs = [{'id': doc.id, 'url': doc.s3_upload.public_url(), 'document_category': doc.document_category,
                            'document_category_display': doc.get_document_category_display(),
                            'thumb_url': doc.s3_upload.public_url(),
                            'bucket': doc.s3_upload.bucket,
                            'folder': doc.s3_upload.folder,
                            'uuid': doc.s3_upload.uuid,
                            'filename': doc.s3_upload.filename,
                            'validity': None,
                            } for doc in
                           instance.driver.driver_files.exclude(s3_upload=None)]
        else:
            driver_docs = []
        return vehicle_docs + owner_docs + driver_docs

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        excluded_fields = [
            'documents', 'driver_data', 'driver_app_user', 'rc_number', 'permit', 'permit_validity', 'permit_type',
            'vehicle_capacity', 'chassis_number', 'engine_number', 'insurer', 'insurance_number', 'insurance_validity',
            'registration_year', 'registration_validity', 'fitness_certificate_number', 'fitness_certificate_issued_on',
            'fitness_certificate_validity_date', 'puc_certificate_number', 'puc_certificate_issued_on', 'route',
            'puc_certificate_validity_date', 'status', 'gps_enabled', 'supplier_name', 'supplier_phone', 'owner_name',
            'updated_on', 'created_on', 'deleted', 'deleted_on', 'created_by', 'changed_by', 'body_type',
            'vehicle_model', 'owner_phone', 'driver', 'owner_data'
        ]
        for field in excluded_fields:
            kwargs['child'].fields.pop(field)
        return serializers.ListSerializer(*args, **kwargs)

    def create(self, validated_data):
        routes = []
        if "route" in validated_data.keys():
            routes = validated_data.pop('route')
        instance = Vehicle.objects.create(**validated_data)
        for route in routes:
            instance.route.add(route)
        return instance

    def update(self, instance, validated_data):
        routes = []
        if "route" in validated_data.keys():
            instance.route.clear()
            routes = validated_data.pop('route')
        Vehicle.objects.filter(id=instance.id).update(**validated_data)
        for route in routes:
            instance.route.add(route)
        return Vehicle.objects.get(id=instance.id)


class Select2FuelCardSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    text = serializers.SerializerMethodField()

    def get_text(self, instance):
        if isinstance(instance, FuelCard):
            return instance.card_number
        return None


class FuelCardSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    customer_id = serializers.CharField(max_length=30, required=False)
    card_number = serializers.CharField(allow_null=True, max_length=40, required=False,
                                        validators=[UniqueValidator(queryset=FuelCard.objects.all())])
    issue_date = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                       input_formats=[DATE_FORMAT, ISO_8601])
    expiry_date = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                        input_formats=[DATE_FORMAT, ISO_8601])
    update_on = serializers.DateTimeField(read_only=True)
    created_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = FuelCard.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        FuelCard.objects.filter(id=instance.id).update(**validated_data)
        return FuelCard.objects.get(id=instance.id)


class FuelCardTransactionSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    paid_to = serializers.CharField(allow_null=True, max_length=70, required=False)
    amount = serializers.IntegerField(max_value=2147483647, min_value=-2147483648, required=False)
    payment_date = serializers.DateTimeField()
    update_on = serializers.DateTimeField(read_only=True)
    created_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())
    fuel_card = serializers.PrimaryKeyRelatedField(queryset=FuelCard.objects.all())

    def to_representation(self, instance):
        self.fields["vehicle"] = VehicleSerializer(read_only=True)
        self.fields["fuel_card"] = FuelCardSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = FuelCardTransaction.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        FuelCardTransaction.objects.filter(id=instance.id).update(**validated_data)
        return FuelCardTransaction.objects.get(id=instance.id)
