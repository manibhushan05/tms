from django.contrib.auth.models import User
from rest_framework import serializers, ISO_8601
from rest_framework.validators import UniqueValidator

from authentication.models import Profile
from employee.models import Employee
from restapi.helper_api import DATE_FORMAT, DATETIME_FORMAT
from restapi.serializers.authentication import UserSerializer, BankSerializer
from restapi.serializers.employee import EmployeeSerializer
from restapi.serializers.supplier import VehicleCategorySerializer

from restapi.serializers.utils import AahoOfficeSerializer, AddressSerializer, CitySerializer, TaxationIDSerializer
from restapi.service.validators import validate_mobile_number, validate_company_code, validate_gstin
from sme.models import SmeTaskEmail, Sme, RateType, CustomerContract, ContractRoute, ContactDetails, Location, \
    ConsignorConsignee, PreferredVehicle, SmeEnquiry, SmeSummary

from utils.models import AahoOffice, Address, City, IDDetails, Bank, TaxationID, VehicleCategory


class SmeTaskEmailSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(allow_null=True, max_length=200, required=False,
                                 validators=[UniqueValidator(queryset=SmeTaskEmail.objects.all())])
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        return SmeTaskEmail.objects.create(**validated_data)

    def update(self, instance, validated_data):
        SmeTaskEmail.objects.filter(id=instance.id).update(**validated_data)
        return SmeTaskEmail.objects.get(id=instance.id)


class BasicSmeSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    company_code = serializers.CharField(max_length=3, min_length=3,
                                         validators=[UniqueValidator(queryset=Sme.objects.all())])
    name = serializers.SerializerMethodField()

    def get_name(self, instance):
        if isinstance(instance, Sme) and isinstance(instance.name, User):
            return instance.name.username
        return None


class SmeSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    company_code = serializers.CharField(max_length=3, min_length=3,
                                         validators=[UniqueValidator(queryset=Sme.objects.all())])
    latest_lr_serial_number = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    lr_format_type = serializers.ChoiceField(allow_null=True, choices=(('S', 'Serial'), ('D', 'Default')),
                                             required=False)
    customer_address = serializers.CharField(allow_null=True, max_length=300, required=False)
    credit_period = serializers.IntegerField(allow_null=True,min_value=1,max_value=180, required=False)
    pin = serializers.CharField(allow_null=True, max_length=6, required=False)
    gstin = serializers.CharField(allow_null=True, max_length=15, required=False)
    is_gst_applicable = serializers.ChoiceField(choices=(('yes', 'Yes'), ('no', 'No'), ('unknown', 'Unknown')),
                                                required=False)
    status = serializers.ChoiceField(choices=[('active', 'active'), ('inactive', 'inactive')], required=False)
    material = serializers.CharField(allow_null=True, max_length=150, required=False)
    created_on = serializers.DateTimeField(read_only=True, format=DATETIME_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    name = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username",
                                        validators=[UniqueValidator(queryset=Sme.objects.all())])
    aaho_office = serializers.PrimaryKeyRelatedField(queryset=AahoOffice.objects.all())
    address = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Address.objects.all(), required=False,
                                                 validators=[UniqueValidator(queryset=Sme.objects.all())])
    aaho_poc = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    id_proof = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=IDDetails.objects.all(), required=False,
                                                  validators=[UniqueValidator(queryset=Sme.objects.all())])
    account_details = serializers.PrimaryKeyRelatedField(write_only=True, allow_null=True, queryset=Bank.objects.all(),
                                                         required=False,
                                                         validators=[UniqueValidator(queryset=Sme.objects.all())])
    taxation_details = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True, queryset=TaxationID.objects.all(), required=False,
        validators=[UniqueValidator(queryset=Sme.objects.all())])
    email_tasks = serializers.PrimaryKeyRelatedField(many=True, queryset=SmeTaskEmail.objects.all(), required=False)
    sme_profile = serializers.SerializerMethodField()
    city_data = serializers.SerializerMethodField()
    aaho_poc_data = serializers.SerializerMethodField()
    aaho_office_branch = serializers.SerializerMethodField()
    pan_number = serializers.SerializerMethodField()

    def validate_company_code(self, value):
        if value and not validate_company_code(value):
            raise serializers.ValidationError("Not a valid company code")
        return value

    def validate_gstin(self, value):
        if value and not validate_gstin(value):
            raise serializers.ValidationError("Not a valid gstin")
        return value

    def get_sme_profile(self, instance):
        if isinstance(instance.name, User) and isinstance(instance.name.profile, Profile):
            return {
                'id': instance.name.profile.id,
                'name': instance.get_name(),
                'contact_person_name': instance.name.profile.contact_person_name,
                'email': instance.name.profile.email,
                'contact_person_phone': instance.name.profile.contact_person_phone,
                'phone': instance.name.profile.phone,
                'alternate_phone': instance.name.profile.alternate_phone,
                'comment': instance.name.profile.comment
            }
        return {'id': -1, 'name': None, 'contact_person_name': None, 'email': None, 'contact_person_phone': None,
                'comment': None, 'alternate_phone': None}

    def get_city_data(self, instance):
        if isinstance(instance.city, City):
            return {'id': instance.city.id, 'city': instance.city.name, 'state': instance.city.state_name}
        return {'id': -1, 'city': None, 'state': None}

    def get_aaho_poc_data(self, instance):
        if isinstance(instance.aaho_poc, Employee):
            return {'id': instance.aaho_poc.id, 'name': instance.aaho_poc.emp_name(),
                    'phone': instance.aaho_poc.emp_phone()}
        return {'id': -1, 'name': None, 'phone': None}

    def get_aaho_office_branch(self, instance):
        if isinstance(instance.aaho_office, AahoOffice):
            return {'id': instance.aaho_office.id, 'branch_name': instance.aaho_office.branch_name}
        return {'id': -1, 'branch_name': None}

    def get_pan_number(self, instance):
        if instance.gstin:
            return instance.gstin[2:-3]
        return None

    def create(self, validated_data):
        email_tasks = []
        if "email_tasks" in validated_data.keys():
            email_tasks = validated_data.pop('email_tasks')
        instance = Sme.objects.create(**validated_data)
        for email_task in email_tasks:
            instance.email_tasks.add(email_task)
        return instance

    def update(self, instance, validated_data):
        email_tasks = []
        if "email_tasks" in validated_data.keys():
            email_tasks = validated_data.pop('email_tasks')
            instance.email_tasks.clear()
        Sme.objects.filter(id=instance.id).update(**validated_data)
        for email_task in email_tasks:
            instance.email_tasks.add(email_task)
        return Sme.objects.get(id=instance.id)


class SmeSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    billed_accounting_summary = serializers.JSONField(style={'base_template': 'textarea.html'})
    placed_order_accounting_summary = serializers.JSONField(style={'base_template': 'textarea.html'})
    accounting_summary = serializers.JSONField(style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    sme = serializers.PrimaryKeyRelatedField(queryset=Sme.objects.all(),
                                             validators=[UniqueValidator(queryset=SmeSummary.objects.all())])

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RateTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(allow_null=True, max_length=100, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def to_representation(self, instance):
        return super(RateTypeSerializer, self).to_representation(instance=instance)

    def create(self, validated_data):
        return RateType.objects.create(**validated_data)

    def update(self, instance, validated_data):
        RateType.objects.filter(id=instance.id).update(**validated_data)
        return RateType.objects.get(id=instance.id)


class CustomerContractSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    start_date = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                       input_formats=[DATE_FORMAT, ISO_8601])
    end_date = serializers.DateField(allow_null=True, required=False, format=DATE_FORMAT,
                                     input_formats=[DATE_FORMAT, ISO_8601])
    billing_frequency = serializers.ChoiceField(allow_null=True, choices=(
        ('d', 'Daily'), ('w', 'Weekly'), ('m', 'Monthly'), ('f', 'Fort Nightly'), ('o', 'Others')), required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    customer = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Sme.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["customer"] = SmeSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        return CustomerContract.objects.create(**validated_data)

    def update(self, instance, validated_data):
        CustomerContract.objects.filter(id=instance.id).update(**validated_data)
        return CustomerContract.objects.get(id=instance.id)


class ContractRouteSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    rate = serializers.IntegerField(max_value=2147483647, min_value=0, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    contract = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=CustomerContract.objects.all(),
                                                  required=False)
    source = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=City.objects.all(), required=False)
    destination = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=City.objects.all(), required=False)
    rate_type = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=RateType.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["contract"] = CustomerContractSerializer(read_only=True)
        self.fields["source"] = CitySerializer(read_only=True)
        self.fields["destination"] = CitySerializer(read_only=True)
        self.fields["rate_type"] = RateTypeSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        return ContractRoute.objects.create(**validated_data)

    def update(self, instance, validated_data):
        ContractRoute.objects.filter(id=instance.id).update(**validated_data)
        return ContractRoute.objects.get(id=instance.id)


class ContactDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    type = serializers.ChoiceField(allow_null=True,
                                   choices=[('primary', 'primary'), ('secondary', 'secondary')],
                                   required=False)
    name = serializers.CharField(allow_null=True, max_length=70, required=False)
    phone = serializers.CharField(allow_null=True, max_length=17, required=False)
    alternate_phone = serializers.CharField(allow_null=True, max_length=17, required=False)
    email = serializers.EmailField(allow_null=True, max_length=100, required=False)
    alternate_email = serializers.EmailField(allow_null=True, max_length=100, required=False)
    designation = serializers.CharField(allow_null=True, max_length=100, required=False)
    status = serializers.ChoiceField(choices=[('active', 'active'), ('inactive', 'inactive')], required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    sme = serializers.PrimaryKeyRelatedField(queryset=Sme.objects.all())

    def to_representation(self, instance):
        self.fields["sme"] = SmeSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        return ContactDetails.objects.create(**validated_data)

    def update(self, instance, validated_data):
        ContactDetails.objects.filter(id=instance.id).update(**validated_data)
        return ContactDetails.objects.get(id=instance.id)


class LocationSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    type = serializers.ChoiceField(allow_null=True,
                                   choices=(('loading', 'loading'), ('unloading', 'unloading')),
                                   required=False)
    address = serializers.CharField(allow_null=True, max_length=200, required=False)
    material = serializers.CharField(allow_null=True, required=False,
                                     style={'base_template': 'textarea.html'})
    latitude = serializers.CharField(allow_null=True, max_length=30, required=False)
    longitude = serializers.CharField(allow_null=True, max_length=30, required=False)
    status = serializers.ChoiceField(choices=[('active', 'active'), ('inactive', 'inactive')], required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    sme = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Sme.objects.all(), required=False)
    contact = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=ContactDetails.objects.all(), required=False,
                                                 validators=[UniqueValidator(queryset=Location.objects.all())])
    city = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=City.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["sme"] = SmeSerializer(read_only=True)
        self.fields["contact"] = ContactDetailsSerializer(read_only=True)
        self.fields["city"] = CitySerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        return Location.objects.create(**validated_data)

    def update(self, instance, validated_data):
        Location.objects.filter(id=instance.id).update(**validated_data)
        return Location.objects.get(id=instance.id)


class ConsignorConsigneeSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    type = serializers.ChoiceField(choices=(('consignor', 'consignor'), ('consignee', 'consignee')))
    name = serializers.CharField(allow_null=True, max_length=255, required=False)
    address = serializers.CharField(allow_null=True, max_length=100, required=False)
    pin = serializers.CharField(allow_null=True, max_length=6, required=False)
    phone = serializers.CharField(allow_null=True, max_length=30, required=False)
    tax_id = serializers.CharField(allow_null=True, max_length=40, required=False)
    status = serializers.ChoiceField(choices=[('active', 'active'), ('inactive', 'inactive')], required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    sme = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Sme.objects.all(), required=False)
    city = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=City.objects.all(), required=False)

    city_name = serializers.SerializerMethodField()

    def get_city_name(self, instance):
        return

    def to_representation(self, instance):
        self.fields["sme"] = SmeSerializer(read_only=True)
        self.fields["city"] = CitySerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        return ConsignorConsignee.objects.create(**validated_data)

    def update(self, instance, validated_data):
        ConsignorConsignee.objects.filter(id=instance.id).update(**validated_data)
        return ConsignorConsignee.objects.get(id=instance.id)


class PreferredVehicleSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    sme = serializers.PrimaryKeyRelatedField(queryset=Sme.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=VehicleCategory.objects.all())

    def to_representation(self, instance):
        self.fields["sme"] = SmeSerializer(read_only=True)
        self.fields["category"] = VehicleCategorySerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        return PreferredVehicle.objects.create(**validated_data)

    def update(self, instance, validated_data):
        PreferredVehicle.objects.filter(id=instance.id).update(**validated_data)
        return PreferredVehicle.objects.get(id=instance.id)


class SmeEnquirySerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    subject = serializers.CharField(allow_null=True, max_length=255, required=False)
    message = serializers.CharField(allow_null=True, max_length=500, required=False)
    status = serializers.ChoiceField(choices=[('active', 'active'), ('inactive', 'inactive')], required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    sme = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Sme.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["sme"] = SmeSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        return SmeEnquiry.objects.create(**validated_data)

    def update(self, instance, validated_data):
        SmeEnquiry.objects.filter(id=instance.id).update(**validated_data)
        return SmeEnquiry.objects.get(id=instance.id)
