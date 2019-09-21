from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from authentication.models import Profile
from broker.models import Broker, BrokerVehicle, BrokerOwner, BrokerDriver, BrokerAccount, BrokerSummary
from driver.models import Driver
from employee.models import Employee
from owner.models import Owner, Vehicle
from restapi.helper_api import DATETIME_FORMAT
from restapi.serializers.authentication import UserSerializer, BankSerializer, ProfileSerializer
from restapi.serializers.driver import DriverSerializer
from restapi.serializers.employee import EmployeeSerializer
from restapi.serializers.owner import VehicleSerializer, OwnerSerializer
from restapi.serializers.utils import CitySerializer, AddressSerializer, AahoOfficeSerializer
from restapi.service.validators import validate_pan
from utils.models import Address, City, AahoOffice, Bank, State


class BrokerSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    code = serializers.CharField(max_length=4, min_length=4)
    route = serializers.CharField(allow_null=True, max_length=400, required=False)
    pan = serializers.CharField( allow_null=True, max_length=10, min_length=10, required=False)
    id_proof = serializers.CharField(allow_blank=True, max_length=70, required=False)

    created_on = serializers.DateTimeField(read_only=True, format=DATETIME_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True, format=DATETIME_FORMAT)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, format=DATETIME_FORMAT)

    name = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all(),
                                              validators=[UniqueValidator(queryset=Broker.objects.all())])
    profile = serializers.SerializerMethodField()
    address = serializers.PrimaryKeyRelatedField(write_only=True, allow_null=True, queryset=Address.objects.all(),
                                                 required=False,
                                                 validators=[UniqueValidator(queryset=Broker.objects.all())])
    full_address = serializers.SerializerMethodField()
    aaho_office = serializers.PrimaryKeyRelatedField(write_only=True, queryset=AahoOffice.objects.all())
    aaho_office_data = serializers.SerializerMethodField()
    aaho_poc = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Employee.objects.all())
    aaho_poc_data = serializers.SerializerMethodField()
    city = serializers.PrimaryKeyRelatedField(write_only=True, allow_null=True, queryset=City.objects.all(),
                                              required=False)
    city_data = serializers.SerializerMethodField()
    account_details = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True, queryset=Bank.objects.all(), required=False,
        validators=[UniqueValidator(queryset=Broker.objects.all())])
    bank_account = serializers.SerializerMethodField()
    broker_vehicles = serializers.SerializerMethodField()
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    vehicles = serializers.SerializerMethodField()
    destination_state = serializers.PrimaryKeyRelatedField(write_only=True,allow_empty=True, many=True, queryset=State.objects.all())
    destination_state_data = serializers.SerializerMethodField()

    def validate_pan(self, value):
        if not validate_pan(value) and value:
            raise serializers.ValidationError("Not a valid pan")
        return value

    def get_destination_state_data(self, instance):
        d_states = instance.destination_state.all()
        d_states_json = []
        for ds in d_states:
            d_states_json.append({"id": ds.id, "state": ds.name})
        return d_states_json

    def get_vehicles(self, instance):
        return instance.vehicles

    def get_profile(self, instance):
        if isinstance(instance.name, User) and isinstance(instance.name.profile, Profile):
            return ProfileSerializer(instance=instance.name.profile).data
        return {}

    def get_city_data(self, instance):
        if isinstance(instance.city, City):
            return {'id': instance.city.id, 'city': instance.city.name, 'state': instance.city.state_name}
        return {'id': -1, 'state': None, 'city': None}

    def get_broker_vehicles(self, instance):
        return "\n".join([bv.vehicle.number() for bv in instance.broker_vehicle.all()])

    def get_bank_account(self, instance):
        if isinstance(instance.account_details, Bank):
            return {'id': instance.account_details.id, 'account_number': instance.account_details.account_number,
                    'beneficiary_name': instance.account_details.account_holder_name,
                    'beneficiary_code': instance.account_details.beneficiary_code,
                    'ifsc': instance.account_details.ifsc}
        return {}

    def get_aaho_office_data(self, instance):
        if isinstance(instance.aaho_office, AahoOffice):
            return {'id': instance.aaho_office.id, 'branch_name': instance.aaho_office.branch_name}
        return {'id': -1, 'branch_name': None}

    def get_aaho_poc_data(self, instance):
        if isinstance(instance.aaho_poc, Employee):
            return {'id': instance.aaho_poc.id, 'name': instance.aaho_poc.emp_name(),
                    'phone': instance.aaho_poc.emp_phone(), 'alt_phone': instance.aaho_poc.emp_alt_phone(),
                    'username': instance.aaho_poc.emp_username()}
        return {}

    def get_full_address(self, instance):
        if isinstance(instance.address, Address):
            return instance.address.full_address()
        return ''

    def create(self, validated_data):
        dest_states = []
        if "destination_state" in validated_data.keys():
            dest_states = validated_data.pop('destination_state')
        instance = Broker.objects.create(**validated_data)
        for dest_state in dest_states:
            instance.destination_state.add(dest_state)
        return instance

    def update(self, instance, validated_data):
        dest_states = []
        if "destination_state" in validated_data.keys():
            dest_states = validated_data.pop('destination_state')
            instance.destination_state.clear()
        Broker.objects.filter(id=instance.id).update(**validated_data)
        for dest_state in dest_states:
            instance.destination_state.add(dest_state)
        return Broker.objects.get(id=instance.id)


class BrokerSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    accounting_summary = serializers.JSONField(style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    broker = serializers.PrimaryKeyRelatedField(queryset=Broker.objects.all(),
                                                validators=[UniqueValidator(queryset=BrokerSummary.objects.all())])

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class BrokerVehicleSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    datetime = serializers.DateTimeField(allow_null=True, required=False)
    latest = serializers.BooleanField(read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    broker = serializers.PrimaryKeyRelatedField(queryset=Broker.objects.all(), required=True)
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), required=True)
    account_details = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Bank.objects.all(),
                                                         required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    class Meta:
        validators = [UniqueTogetherValidator(queryset=BrokerVehicle.objects.all(), fields=('broker', 'vehicle'))]

    def to_representation(self, instance):
        # self.fields['broker'] = BrokerSerializer(read_only=True)
        # self.fields['vehicle'] = VehicleSerializer(read_only=True)
        # self.fields['account_details'] = BankSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = BrokerVehicle.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        BrokerVehicle.objects.filter(id=instance.id).update(**validated_data)
        return BrokerVehicle.objects.get(id=instance.id)


class BrokerOwnerSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    broker = serializers.PrimaryKeyRelatedField(queryset=Broker.objects.all(), required=True)
    owner = serializers.PrimaryKeyRelatedField(queryset=Owner.objects.all(), required=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    class Meta:
        validators = [UniqueTogetherValidator(queryset=BrokerOwner.objects.all(), fields=('broker', 'owner'))]

    def to_representation(self, instance):
        self.fields['broker'] = BrokerSerializer(read_only=True)
        self.fields['owner'] = OwnerSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = BrokerOwner.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        BrokerOwner.objects.filter(id=instance.id).update(**validated_data)
        return BrokerOwner.objects.get(id=instance.id)


class BrokerDriverSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    broker = serializers.PrimaryKeyRelatedField(queryset=Broker.objects.all(), required=True)
    driver = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all(), required=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    class Meta:
        validators = [UniqueTogetherValidator(queryset=BrokerDriver.objects.all(), fields=('broker', 'driver'))]

    def to_representation(self, instance):
        self.fields['broker'] = BrokerSerializer(read_only=True)
        self.fields['driver'] = DriverSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = BrokerDriver.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        BrokerDriver.objects.filter(id=instance.id).update(**validated_data)
        return BrokerDriver.objects.get(id=instance.id)


class BrokerAccountSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    relation = serializers.ChoiceField(choices=(('self', 'self'), ('driver', 'driver'), ('owner', 'owner')),
                                       required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    broker = serializers.PrimaryKeyRelatedField(queryset=Broker.objects.all(), required=True)
    account = serializers.PrimaryKeyRelatedField(queryset=Bank.objects.all(), required=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    class Meta:
        validators = [UniqueTogetherValidator(queryset=BrokerAccount.objects.all(), fields=('broker', 'account'))]

    def to_representation(self, instance):
        self.fields['broker'] = BrokerSerializer(read_only=True)
        self.fields['account'] = BankSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = BrokerAccount.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        BrokerAccount.objects.filter(id=instance.id).update(**validated_data)
        return BrokerAccount.objects.get(id=instance.id)
