import re

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models import Q
from rest_framework import serializers, ISO_8601
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from authentication.models import Profile
from employee.models import Employee
from owner.vehicle_util import display_format
from restapi.helper_api import DATE_FORMAT
from restapi.serializers.authentication import ProfileSerializer, BankSerializer
from restapi.serializers.employee import EmployeeSerializer
from restapi.serializers.utils import CitySerializer, AahoOfficeSerializer, StateSerializer
from restapi.service.validators import VEHICLE_NUMBER_REGEX, MOBILE_NUMBER_REGEX, PAN
from supplier.models import Service, Vehicle, DriverVehicle, Driver, Supplier, ContactPerson, DriverPhone, \
    VehicleStatus, VehicleInsurer, VehicleInsurance, VehiclePUC, VehicleFitness, VehiclePermit, SupplierVehicle, \
    SupplierAccountingSummary, VehicleAccountingSummary
from utils.models import VehicleBodyCategory, VehicleCategory, AahoOffice, State, City, Bank


class ServiceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(allow_null=True, max_length=50, required=False,
                                 validators=[UniqueValidator(queryset=Service.objects.all())])
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = Service.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        Service.objects.filter(id=instance.id).update(**validated_data)
        return Service.objects.get(id=instance.id)


class SupplierSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    code = serializers.CharField(allow_null=True, max_length=4, min_length=4, required=False,
                                 validators=[UniqueValidator(queryset=Supplier.objects.all())])
    address = serializers.CharField(allow_null=True, max_length=300, required=False)
    pin = serializers.CharField(allow_null=True, max_length=6, min_length=6, required=False)
    pan = serializers.CharField(allow_null=True, max_length=11, required=False,
                                validators=[UniqueValidator(queryset=Supplier.objects.all())])
    route = serializers.CharField(allow_null=True, max_length=255, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    user = serializers.SlugRelatedField(queryset=User.objects.all(),
                                        validators=[UniqueValidator(queryset=Supplier.objects.all())],
                                        slug_field="username")
    city = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=City.objects.all(), required=False)
    aaho_office = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=AahoOffice.objects.all(), required=False)
    aaho_poc = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Employee.objects.all(), required=False)

    services = serializers.PrimaryKeyRelatedField(many=True, allow_empty=False, queryset=Service.objects.all(),
                                                  required=False)
    serving_states = serializers.PrimaryKeyRelatedField(write_only=True, many=True, allow_empty=False,
                                                        queryset=State.objects.all(),
                                                        required=False)
    vehicles = serializers.SerializerMethodField()
    vehicles_data = serializers.SerializerMethodField()

    city_data = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    serving_state_list = serializers.SerializerMethodField()
    aaho_office_data = serializers.SerializerMethodField()
    aaho_poc_data = serializers.SerializerMethodField()
    contact_persons = serializers.SerializerMethodField()

    def get_vehicles_data(self, instance):
        return '\n'.join(
            ['{} ({})'.format(display_format(sv.vehicle.vehicle_number), sv.get_ownership_display()) for sv in
             instance.suppliervehicle_set.all()])

    def get_contact_persons(self, instance):
        return [{'id': row.id, 'name': row.name, 'phone': row.phone, 'email': row.email} for row in
                instance.contactperson_set.all()]

    def get_serving_state_list(self, instance):
        return StateSerializer(instance=instance.serving_states, many=True).data

    def get_aaho_office_data(self, instance):
        if instance.aaho_office:
            return AahoOfficeSerializer(instance=instance.aaho_office).data
        return {
            "id": -1,
        }

    def get_aaho_poc_data(self, instance):
        if instance.aaho_poc:
            return EmployeeSerializer(instance=instance.aaho_poc).data
        return {'id': -1}

    def get_name(self, instance):
        return instance.name

    def get_phone(self, instance):
        return instance.phone

    def get_email(self, instance):
        return instance.email

    def get_vehicles(self, instance):
        return [{'vehicle_number': sv.vehicle.vehicle_number_display, 'id': sv.vehicle.id} for sv in
                instance.suppliervehicle_set.all()]

    def get_city_data(self, instance):
        if instance.city:
            return {'name': instance.city.name, 'state': instance.city.state_name, 'id': instance.city_id,
                    'code': instance.city.code}
        return {'name': None, 'state': None, 'id': -1, 'code': None}

    def validate(self, attrs):
        user = attrs.get('user', None)
        if not isinstance(user, User):
            serializers.ValidationError('User is not yet created')
        elif not isinstance(user.profile, Profile):
            raise serializers.ValidationError('Profile is not create')
        elif user.profile.phone and Supplier.objects.filter(user__profile__phone=user.profile.phone).exists():
            raise serializers.ValidationError('phone number already exists')
        elif not attrs.get('pan', None) and not user.profile.phone:
            raise serializers.ValidationError('Please enter either phone or pan')
        return attrs

    # def get_supplier_profile(self, instance):
    #     if isinstance(instance, Supplier) and isinstance(instance.user, User) and isinstance(instance.user.profile,
    #                                                                                          Profile):
    #         return ProfileSerializer(instance=instance.user.profile).data
    #     return ProfileSerializer(instance=instance.user.profile).data

    def create(self, validated_data):
        services = []
        serving_states = []
        if "services" in validated_data.keys():
            services = validated_data.pop('services')
        if "serving_states" in validated_data.keys():
            serving_states = validated_data.pop('serving_states')
        instance = Supplier.objects.create(**validated_data)
        for service in services:
            instance.services.add(service)
        for serving_state in serving_states:
            instance.serving_states.add(serving_state)
        return instance

    def update(self, instance, validated_data):
        services = []
        serving_states = []
        if "services" in validated_data.keys():
            services = validated_data.pop('services')
            instance.services.clear()
        if "serving_states" in validated_data.keys():
            serving_states = validated_data.pop('serving_states')
            instance.serving_states.clear()
        Supplier.objects.filter(id=instance.id).update(**validated_data)
        for service in services:
            instance.services.add(service)
        for serving_state in serving_states:
            instance.serving_states.add(serving_state)
        return Supplier.objects.get(id=instance.id)


class SupplierAccountingSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    accounting_summary = serializers.JSONField(style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(),
                                                  validators=[UniqueValidator(
                                                      queryset=SupplierAccountingSummary.objects.all())])

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class VehicleAccountingSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    accounting_summary = serializers.JSONField(style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(),
                                                 validators=[
                                                     UniqueValidator(queryset=VehicleAccountingSummary.objects.all())])

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ContactPersonSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    active = serializers.BooleanField(default=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    user = serializers.SlugRelatedField(queryset=User.objects.all(),
                                        validators=[UniqueValidator(queryset=ContactPerson.objects.all())],
                                        slug_field="username")
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())

    def to_representation(self, instance):
        self.fields['supplier'] = SupplierSerializer(read_only=True)
        # self.fields['user'] = UserSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = ContactPerson.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        ContactPerson.objects.filter(id=instance.id).update(**validated_data)
        return ContactPerson.objects.get(id=instance.id)


class DriverSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    address = serializers.CharField(allow_null=True, max_length=300, required=False)
    route = serializers.CharField(allow_null=True, max_length=300, required=False)
    pan = serializers.RegexField(regex=PAN, allow_blank=True, allow_null=True, max_length=11, required=False)
    driving_licence_number = serializers.CharField(allow_null=True, max_length=50, required=False)
    driving_licence_location = serializers.CharField(allow_null=True, max_length=50, required=False)
    driving_licence_validity = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                                     input_formats=[DATE_FORMAT, ISO_8601])
    smartphone_available = serializers.BooleanField(required=False)
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    user = serializers.SlugRelatedField(queryset=User.objects.all(),
                                        validators=[UniqueValidator(queryset=Driver.objects.all())],
                                        slug_field="username")
    account_details = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Bank.objects.all(), required=False,
                                                         validators=[UniqueValidator(queryset=Driver.objects.all())])

    name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    docs = serializers.SerializerMethodField()

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
            instance.supplier_driver_files.filter(document_category__in=['DL', 'PAN']).exclude(
                Q(s3_upload=None) | Q(deleted=True))
        ]

    def get_name(self, instance):
        return instance.name

    def get_phone(self, instance):
        return instance.phone

    def to_representation(self, instance):
        self.fields['account_details'] = BankSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = Driver.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        Driver.objects.filter(id=instance.id).update(**validated_data)
        return Driver.objects.get(id=instance.id)


class DriverPhoneSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    phone = serializers.CharField(max_length=10, min_length=10, required=True,
                                  validators=[UniqueValidator(queryset=DriverPhone.objects.all())])
    active = serializers.BooleanField(default=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    driver = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["driver"] = DriverSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = DriverPhone.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        DriverPhone.objects.filter(id=instance.id).update(**validated_data)
        return DriverPhone.objects.get(id=instance.id)

    def validate_phone(self, value):
        phone_pattern = re.compile(MOBILE_NUMBER_REGEX)
        if not phone_pattern.match(value):
            raise serializers.ValidationError({"phone": "Mobile Number is not valid"})
        return value


class VehicleBodyCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        return VehicleBodyCategory.objects.create(**validated_data)

    def update(self, instance, validated_data):
        VehicleBodyCategory.objects.filter(id=instance.id).update(**validated_data)
        return VehicleBodyCategory.objects.get(id=instance.id)


class VehicleCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    vehicle_type = serializers.CharField(max_length=100, required=True,
                                         validators=[UniqueValidator(queryset=VehicleCategory.objects.all())])
    capacity = serializers.CharField(max_length=30, required=False)
    truck_body_type = serializers.CharField(max_length=50, required=False)
    description = serializers.CharField(max_length=500, required=False)
    priority = serializers.CharField(max_length=10, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    truck_body = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=VehicleBodyCategory.objects.all(),
                                                    required=False)

    def to_representation(self, instance):
        self.fields['truck_body'] = VehicleBodyCategorySerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = VehicleCategory.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        VehicleCategory.objects.filter(id=instance.id).update(**validated_data)
        return VehicleCategory.objects.get(id=instance.id)


class VehicleSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    vehicle_number = serializers.CharField(max_length=15, required=True,
                                           validators=[UniqueValidator(queryset=Vehicle.objects.all())])
    vehicle_capacity = serializers.IntegerField(allow_null=True, max_value=10000, min_value=0, required=False)
    chassis_number = serializers.CharField(allow_null=True, max_length=17, required=False)
    body_type = serializers.CharField(allow_null=True, max_length=50, required=False)
    engine_number = serializers.CharField(allow_null=True, max_length=15, required=False)
    registration_year = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                              input_formats=[DATE_FORMAT, ISO_8601])
    registration_validity = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                                  input_formats=[DATE_FORMAT, ISO_8601])
    gps_enabled = serializers.BooleanField(required=False)
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    vehicle_type = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=VehicleCategory.objects.all(),
                                                      required=False)
    vehicle_number_display = serializers.SerializerMethodField()
    owner_data = serializers.SerializerMethodField()
    vehicle_type_data = serializers.SerializerMethodField()
    driver_data = serializers.SerializerMethodField()

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
        if isinstance(instance.owner, Supplier):
            return {'id': instance.owner.id, 'name': instance.owner.name, 'phone': instance.owner.phone}
        return {'id': -1, 'name': '-', 'phone': '-'}

    def get_vehicle_type_data(self, instance):
        if isinstance(instance.vehicle_type, VehicleCategory):
            return {'id': instance.vehicle_type.id, 'name': instance.vehicle_type.vehicle_category,
                    'truck_body_type': instance.vehicle_type.truck_body_type}
        return {'id': -1, 'name': '-', 'truck_body_type': '-'}

    def validate_vehicle_number(self, value):
        vehicle_number_pattern = re.compile(VEHICLE_NUMBER_REGEX)
        if not vehicle_number_pattern.match(value):
            raise serializers.ValidationError({"vehicle_number": "Vehicle Number is not valid"})
        return value

    def create(self, validated_data):
        vehicle = Vehicle.objects.create(**validated_data)
        return vehicle

    def update(self, instance, validated_data):
        Vehicle.objects.filter(id=instance.id).update(**validated_data)
        return Vehicle.objects.get(id=instance.id)


class FMSVehicleSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    vehicle_number = serializers.CharField(max_length=15, required=True,
                                           validators=[UniqueValidator(queryset=Vehicle.objects.all())])
    vehicle_capacity = serializers.IntegerField(allow_null=True, max_value=10000, min_value=0, required=False)
    chassis_number = serializers.CharField(allow_null=True, max_length=17, required=False)
    body_type = serializers.CharField(allow_null=True, max_length=50, required=False)
    engine_number = serializers.CharField(allow_null=True, max_length=15, required=False)
    registration_year = serializers.DateField(allow_null=True, required=False, format='%Y',
                                              input_formats=[DATE_FORMAT, ISO_8601])
    registration_validity = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                                  input_formats=[DATE_FORMAT, ISO_8601])
    gps_enabled = serializers.BooleanField(required=False)
    created_on = serializers.DateTimeField(read_only=True, format=DATE_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    vehicle_type = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=VehicleCategory.objects.all(),
                                                      required=False)
    vehicle_number_display = serializers.SerializerMethodField()
    owner_data = serializers.SerializerMethodField()
    vehicle_type_data = serializers.SerializerMethodField()
    driver_data = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    rc_number = serializers.SerializerMethodField()
    permit = serializers.SerializerMethodField()
    permit_validity = serializers.SerializerMethodField()
    permit_type = serializers.SerializerMethodField()
    vehicle_model = serializers.SerializerMethodField()
    insurer = serializers.SerializerMethodField()
    insurance_number = serializers.SerializerMethodField()
    insurance_validity = serializers.SerializerMethodField()
    fitness_certificate_number = serializers.SerializerMethodField()
    fitness_certificate_issued_on = serializers.SerializerMethodField()
    fitness_certificate_validity_date = serializers.SerializerMethodField()
    puc_certificate_number = serializers.SerializerMethodField()
    puc_certificate_issued_on = serializers.SerializerMethodField()
    puc_certificate_validity_date = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    bank_account = serializers.SerializerMethodField()

    def get_bank_account(self, instance):
        return

    def get_rc_number(self, instance):
        return instance.vehicle_number

    def get_permit(self, instance):
        try:
            return instance.vehiclepermit_set.latest('expiry_date').permit_number
        except (VehiclePermit.DoesNotExist, ValueError)as e:
            return

    def get_permit_validity(self, instance):
        try:
            return instance.vehiclepermit_set.latest('expiry_date').expiry_date.strftime('%d-%b-%Y')
        except (VehiclePermit.DoesNotExist, ValueError)as e:
            return

    def get_permit_type(self, instance):
        try:
            return instance.vehiclepermit_set.latest('expiry_date').permit_type
        except (VehiclePermit.DoesNotExist, ValueError)as e:
            return

    def get_vehicle_model(self, instance):
        return

    def get_insurer(self, instance):
        try:
            return instance.vehicleinsurance_set.latest('expired_by').insurer_name
        except (VehicleInsurance.DoesNotExist, ValueError)as e:
            return

    def get_insurance_number(self, instance):
        try:
            return instance.vehicleinsurance_set.latest('expired_by').insurance_number
        except (VehicleInsurance.DoesNotExist, ValueError)as e:
            return

    def get_insurance_validity(self, instance):
        try:
            return instance.vehicleinsurance_set.latest('expired_by').expired_by.strftime('%d-%b-%Y')
        except (VehicleInsurance.DoesNotExist, ValueError)as e:
            return

    def get_fitness_certificate_number(self, instance):
        try:
            return instance.vehiclefitness_set.latest('expiry_date').serial_number
        except (VehicleFitness.DoesNotExist, ValueError)as e:
            return

    def get_fitness_certificate_issued_on(self, instance):
        try:
            return instance.vehiclefitness_set.latest('expiry_date').issued_date.strftime('%d-%b-%Y')
        except (VehicleFitness.DoesNotExist, ValueError)as e:
            return

    def get_fitness_certificate_validity_date(self, instance):
        try:
            return instance.vehiclefitness_set.latest('expiry_date').expiry_date.strftime('%d-%b-%Y')
        except (VehicleFitness.DoesNotExist, ValueError)as e:
            return

    def get_puc_certificate_number(self, instance):
        try:
            return instance.vehiclepuc_set.latest('expiry_date').serial_number
        except (VehiclePUC.DoesNotExist, ValueError)as e:
            return

    def get_puc_certificate_issued_on(self, instance):
        try:
            return instance.vehiclepuc_set.latest('expiry_date').issued_date.strftime('%d-%b-%Y')
        except (VehiclePUC.DoesNotExist, ValueError)as e:
            return

    def get_puc_certificate_validity_date(self, instance):
        try:
            return instance.vehiclepuc_set.latest('expiry_date').expiry_date.strftime('%d-%b-%Y')
        except (VehiclePUC.DoesNotExist, ValueError)as e:
            return

    def get_status(self, instance):
        return
        # def get_(self):

    #         return

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
        if isinstance(instance.owner, Supplier):
            return {'id': instance.owner.id, 'name': instance.owner.name, 'phone': instance.owner.phone}
        return {'id': -1, 'name': '-', 'phone': '-'}

    def get_vehicle_type_data(self, instance):
        if isinstance(instance.vehicle_type, VehicleCategory):
            return {'id': instance.vehicle_type.id, 'name': instance.vehicle_type.vehicle_category,
                    'truck_body_type': instance.vehicle_type.truck_body_type}
        return {'id': -1, 'name': '-', 'truck_body_type': '-'}

    def get_documents(self, instance):
        if isinstance(instance, Vehicle):
            vehicle_docs = [
                {'id': doc.id, 'url': doc.s3_upload.public_url(), 'document_category': doc.document_category,
                 'document_category_display': doc.get_document_category_display(),
                 'thumb_url': doc.s3_upload.public_url(),
                 'bucket': doc.s3_upload.bucket,
                 'folder': doc.s3_upload.folder,
                 'uuid': doc.s3_upload.uuid,
                 'filename': doc.s3_upload.filename,
                 'validity': None,
                 } for doc in
                instance.supplier_vehicle_files.exclude(deleted=True).exclude(s3_upload=None).order_by('id')]
        else:
            vehicle_docs = []
        return vehicle_docs

    def validate_vehicle_number(self, value):
        vehicle_number_pattern = re.compile(VEHICLE_NUMBER_REGEX)
        if not vehicle_number_pattern.match(value):
            raise serializers.ValidationError({"vehicle_number": "Vehicle Number is not valid"})
        return value

    def create(self, validated_data):
        vehicle = Vehicle.objects.create(**validated_data)
        return vehicle

    def update(self, instance, validated_data):
        Vehicle.objects.filter(id=instance.id).update(**validated_data)
        return Vehicle.objects.get(id=instance.id)


class DriverVehicleSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    driver = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all())
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())
    active = serializers.BooleanField(required=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def to_representation(self, instance):
        self.fields['driver'] = DriverSerializer(read_only=True)
        self.fields['vehicle'] = VehicleSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = DriverVehicle.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        DriverVehicle.objects.filter(id=instance.id).update(**validated_data)
        return DriverVehicle.objects.get(id=instance.id)


class VehicleStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    status = serializers.ChoiceField(
        choices=(('UD', 'Unloaded'), ('LG', 'Loading'), ('LD', 'Loaded'), ('UG', 'Unloading')),
        required=False)
    active = serializers.BooleanField(required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())

    def to_representation(self, instance):
        self.fields['vehicle'] = VehicleSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = VehicleStatus.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        VehicleStatus.objects.filter(id=instance.id).update(**validated_data)
        return VehicleStatus.objects.get(id=instance.id)


class VehicleInsurerSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(max_length=100, required=False,
                                 validators=[UniqueValidator(queryset=VehicleInsurer.objects.all())])
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = VehicleInsurer.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        VehicleInsurer.objects.filter(id=instance.id).update(**validated_data)
        return VehicleInsurer.objects.get(id=instance.id)


class VehicleInsuranceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    insurance_number = serializers.CharField(allow_null=True, max_length=25, required=False)
    issued_on = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                      input_formats=[DATE_FORMAT, ISO_8601])
    expired_by = serializers.DateField(format=DATE_FORMAT,
                                       input_formats=[DATE_FORMAT, ISO_8601])
    image_url = serializers.URLField(allow_null=True, max_length=200, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())
    insurer = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=VehicleInsurer.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields['vehicle'] = VehicleSerializer(read_only=True)
        self.fields['insurer'] = VehicleInsurerSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = VehicleInsurance.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        VehicleInsurance.objects.filter(id=instance.id).update(**validated_data)
        return VehicleInsurance.objects.get(id=instance.id)


class VehiclePUCSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    serial_number = serializers.CharField(allow_null=True,
                                          help_text='The serial number of the issued certificate', max_length=30,
                                          required=False)
    issued_date = serializers.DateField(allow_null=True, help_text='The date on which the test was conducted',
                                        required=False, format=DATE_FORMAT, input_formats=[DATE_FORMAT, ISO_8601])
    expiry_date = serializers.DateField(help_text='The expiry date of the PUC certificate',
                                        format=DATE_FORMAT, input_formats=[DATE_FORMAT, ISO_8601])
    readings = serializers.CharField(allow_null=True,
                                     help_text='The readings and observations from the test',
                                     max_length=250, required=False)
    image_url = serializers.URLField(allow_null=True, max_length=200, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())

    def to_representation(self, instance):
        self.fields['vehicle'] = VehicleSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = VehiclePUC.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        VehiclePUC.objects.filter(id=instance.id).update(**validated_data)
        return VehiclePUC.objects.get(id=instance.id)


class VehicleFitnessSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    serial_number = serializers.CharField(allow_null=True, max_length=30, required=False)
    issued_date = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                        input_formats=[DATE_FORMAT, ISO_8601])
    expiry_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, ISO_8601])
    image_url = serializers.URLField(allow_null=True, max_length=200, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())

    def to_representation(self, instance):
        self.fields['vehicle'] = VehicleSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = VehicleFitness.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        VehicleFitness.objects.filter(id=instance.id).update(**validated_data)
        return VehicleFitness.objects.get(id=instance.id)


class VehiclePermitSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    permit_number = serializers.CharField(allow_null=True, max_length=30, required=False)
    permit_type = serializers.CharField(allow_null=True, max_length=100, required=False)
    issued_date = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                        input_formats=[DATE_FORMAT, ISO_8601])
    expiry_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT, ISO_8601])

    image_url = serializers.URLField(allow_null=True, max_length=200, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    vehicle = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Vehicle.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields['vehicle'] = VehicleSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = VehiclePermit.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        VehiclePermit.objects.filter(id=instance.id).update(**validated_data)
        return VehiclePermit.objects.get(id=instance.id)


class SupplierVehicleSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    ownership = serializers.ChoiceField(allow_null=True, choices=(('B', 'Broker'), ('O', 'Owner')), required=True)
    active = serializers.BooleanField(required=False, default=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), required=True)
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), required=True)

    class Meta:
        validators = [UniqueTogetherValidator(queryset=SupplierVehicle.objects.all(),
                                              fields=('supplier', 'vehicle', 'ownership', 'active'))]

    def to_representation(self, instance):
        self.fields['supplier'] = SupplierSerializer(read_only=True)
        self.fields['vehicle'] = VehicleSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = SupplierVehicle.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        SupplierVehicle.objects.filter(id=instance.id).update(**validated_data)
        return SupplierVehicle.objects.get(id=instance.id)
