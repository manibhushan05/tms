from django.contrib.auth.models import User
from rest_framework import serializers, ISO_8601
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from fms.models import Document
# from restapi.serializers.broker import DocumentSerializer
from restapi.helper_api import DATE_FORMAT
from restapi.service.validators import validate_ifsc, validate_mobile_number
from utils.models import City, State, Address, IDDetails, BankName, IfscDetail, AahoOffice, TaxationID, Bank


class StateSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(max_length=70, validators=[UniqueValidator(queryset=State.objects.all())])
    code = serializers.CharField(max_length=2,min_length=2, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = State.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        State.objects.filter(id=instance.id).update(**validated_data)
        return State.objects.get(id=instance.id)


class CitySerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(max_length=200)
    code = serializers.CharField(max_length=3, min_length=3, validators=[UniqueValidator(queryset=City.objects.all())])
    pin = serializers.CharField(allow_null=True, max_length=6, min_length=6, required=False)
    latitude = serializers.DecimalField(allow_null=True, decimal_places=12, max_digits=18, required=False)
    longitude = serializers.DecimalField(allow_null=True, decimal_places=12, max_digits=18, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=City.objects.all(),
                fields=('name', 'state')
            )
        ]

    def to_representation(self, instance):
        self.fields["state"] = StateSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = City.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        City.objects.filter(id=instance.id).update(**validated_data)
        return City.objects.get(id=instance.id)


class AddressSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    line1 = serializers.CharField(max_length=500)
    line2 = serializers.CharField(allow_null=True, max_length=200, required=False)
    line3 = serializers.CharField(allow_null=True, max_length=200, required=False)
    landmark = serializers.CharField(allow_null=True, max_length=200, required=False)
    pin = serializers.CharField(allow_null=True, min_length=6, max_length=6, required=False)
    latitude = serializers.CharField(allow_null=True, max_length=30, required=False)
    longitude = serializers.CharField(allow_null=True, max_length=30, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    city = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=City.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["city"] = CitySerializer(read_only=True)
        return super(AddressSerializer, self).to_representation(instance=instance)

    def create(self, validated_data):
        instance = Address.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        Address.objects.filter(id=instance.id).update(**validated_data)
        return Address.objects.get(id=instance.id)


class IDDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    id_type = serializers.ChoiceField(choices=(
        ('PAN', 'PAN Card'), ('DL', 'Driving Licence'), ('EL', 'Election ID'), ('AC', 'Aadhar Card'),
        ('PT', 'Passport'),
        ('RC', 'Ration Card')))
    id_number = serializers.CharField(max_length=30)
    id_issued_in = serializers.CharField(allow_null=True, max_length=255, required=False)
    validity = serializers.DateField(allow_null=True, required=False,format=DATE_FORMAT,input_formats=[DATE_FORMAT, ISO_8601])
    issue_date = serializers.DateField(allow_null=True, required=False,format=DATE_FORMAT,input_formats=[DATE_FORMAT, ISO_8601])
    id_image_url = serializers.URLField(allow_null=True, max_length=200, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    document = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Document.objects.all(), required=False)

    # def to_representation(self, instance):
    #     # self.fields["document"] = DocumentSerializer(read_only=True)
    #     return super(IDDetailsSerializer, self).to_representation(instance=instance)

    def create(self, validated_data):
        instance = IDDetails.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        IDDetails.objects.filter(id=instance.id).update(**validated_data)
        return IDDetails.objects.get(id=instance.id)


class BankNameSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(max_length=200)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = BankName.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        BankName.objects.filter(id=instance.id).update(**validated_data)
        return BankName.objects.get(id=instance.id)


class IfscDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    ifsc_code = serializers.CharField(max_length=20, validators=[UniqueValidator(queryset=IfscDetail.objects.all())])
    micr_code = serializers.CharField(allow_null=True, max_length=35, required=False)
    branch_name = serializers.CharField(allow_null=True, max_length=400, required=False)
    address = serializers.CharField(allow_null=True, max_length=400, required=False)
    contact_details = serializers.CharField(allow_null=True, max_length=400, required=False)
    centre = serializers.CharField(allow_null=True, max_length=400, required=False)
    district = serializers.CharField(allow_null=True, max_length=70, required=False)
    state = serializers.CharField(allow_null=True, max_length=70, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    bank = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=BankName.objects.all(), required=False)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def to_representation(self, instance):
        self.fields["bank"] = BankNameSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = IfscDetail.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        IfscDetail.objects.filter(id=instance.id).update(**validated_data)
        return IfscDetail.objects.get(id=instance.id)

    def validate_ifsc_code(self, value):
        if not validate_ifsc(value) and value:
            raise serializers.ValidationError("Not a valid ifsc number")
        return value

class TaxationIDSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    service_tax_number = serializers.CharField(allow_null=True, label='CST/VAT/TIN/SALES TAX',
                                               max_length=40,
                                               required=False)
    tan_number = serializers.CharField(allow_null=True, max_length=40, required=False)
    pan = serializers.CharField(allow_null=True, max_length=30, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    pan_doc = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Document.objects.all(), required=False)

    # def to_representation(self, instance):
    #     # self.fields["pan_doc"] = DocumentSerializer(read_only=True)
    #     return super().to_representation(instance=instance)

    def create(self, validated_data):
        return TaxationID.objects.create(**validated_data)

    def update(self, instance, validated_data):
        TaxationID.objects.filter(id=instance.id).update(**validated_data)
        return TaxationID.objects.get(id=instance.id)

class AahoOfficeSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    branch_name = serializers.CharField(max_length=200)
    branch_head = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=300, min_length=4)
    pin = serializers.CharField(allow_null=True, max_length=6, min_length=6)
    email = serializers.EmailField(max_length=100)
    phone = serializers.CharField(max_length=10,min_length=10)
    t1_name = serializers.CharField(allow_null=True, label='Traffic Person 1 Name', max_length=35, required=False)
    t1_phone = serializers.CharField(allow_null=True, help_text='enter 10 digit mobile number',
                                     label='Traffic Person 1 Phone',
                                     max_length=10,min_length=10, required=False)
    t2_name = serializers.CharField(allow_null=True, label='Traffic Person 2 Name', max_length=35,
                                    required=False)
    t2_phone = serializers.CharField(allow_null=True, help_text='enter 10 digit mobile number',
                                     label='Traffic Person 2 Phone',min_length=10, max_length=10, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    branch = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())



    def create(self, validated_data):
        instance = AahoOffice.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        AahoOffice.objects.filter(id=instance.id).update(**validated_data)
        return AahoOffice.objects.get(id=instance.id)

    def validate_phone(self, value):
        if not validate_mobile_number(value) and value:
            raise serializers.ValidationError("Not a valid mobile number")
        return value


    def validate_t1_phone(self, value):
        if not validate_mobile_number(value) and value:
            raise serializers.ValidationError("Not a valid mobile number")
        return value


    def validate_t2_phone(self, value):
        if not validate_mobile_number(value) and value:
            raise serializers.ValidationError("Not a valid mobile number")
        return value


class Select2BankSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    text = serializers.SerializerMethodField()

    def get_text(self, instance):
        if isinstance(instance, Bank):
            return instance.account_number
        return None
