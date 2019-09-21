from django.contrib.auth.models import User
from rest_framework import serializers, ISO_8601
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from api.utils import get_or_none
from employee.models import Employee, Designation, Department, FitnessDetail, PastEmployment, PermanentAddress, \
    Referral, EmploymentAgency, CurrentEmploymentDetails, EducationalDegree, CertificationCourse, SkillSet, Nominee, \
    LeaveRecord, Salary, Task, TaskEmail
from restapi.helper_api import DATE_FORMAT, DATETIME_FORMAT
from restapi.serializers.authentication import UserSerializer, BankSerializer
from restapi.serializers.utils import CitySerializer, AahoOfficeSerializer
from restapi.service.validators import validate_mobile_number
from utils.models import City, AahoOffice, Bank


class DesignationSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(max_length=100, validators=[UniqueValidator(queryset=Designation.objects.all())])
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = Designation.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        Designation.objects.filter(id=instance.id).update(**validated_data)
        return Designation.objects.get(id=instance.id)


class DepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(max_length=100, validators=[UniqueValidator(queryset=Department.objects.all())])
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = Department.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        Department.objects.filter(id=instance.id).update(**validated_data)
        return Department.objects.get(id=instance.id)


class FitnessDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    height = serializers.DecimalField(decimal_places=2, help_text='Height in Inches', max_digits=8, required=False)
    weight = serializers.DecimalField(decimal_places=2, help_text='Weight in Kgs', max_digits=8, required=False)
    blood_group = serializers.ChoiceField(allow_blank=True, allow_null=True, choices=(
        ('o_pos', 'O+'), ('o_neg', 'O-'), ('a_pos', 'A+'), ('a_neg', 'A-'), ('b_pos', 'B+'), ('b_neg', 'B-'),
        ('ab_pos', 'AB+'), ('ab_neg', 'AB-')), required=False)
    medical_fitness = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                            style={'base_template': 'textarea.html'})
    emergency_contact_person_name = serializers.CharField(allow_blank=True, allow_null=True, max_length=35,
                                                          required=False)
    emergency_contact_person_phone = serializers.CharField(allow_blank=True, allow_null=True, max_length=15,
                                                           required=False)
    emergency_contact_person_email = serializers.EmailField(allow_blank=True, allow_null=True, max_length=35,
                                                            required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = FitnessDetail.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        FitnessDetail.objects.filter(id=instance.id).update(**validated_data)
        return FitnessDetail.objects.get(id=instance.id)


class PastEmploymentSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    joining_date = serializers.DateField(allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601],
                                         format=DATE_FORMAT)
    leaving_date = serializers.DateField(allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601],
                                         format=DATE_FORMAT)
    organisation = serializers.CharField(allow_blank=True, allow_null=True, max_length=100, required=False)
    designation = serializers.CharField(allow_blank=True, allow_null=True, max_length=100, required=False)
    reporting_manager = serializers.CharField(allow_blank=True, allow_null=True, max_length=100, required=False)
    gross_compensation = serializers.CharField(allow_blank=True, allow_null=True, max_length=20, required=False)
    reason_for_change = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                              style={'base_template': 'textarea.html'})
    total_experience = serializers.CharField(allow_blank=True, allow_null=True, help_text='In year and months',
                                             max_length=20,
                                             required=False)
    relevant_experience = serializers.CharField(allow_blank=True, allow_null=True, help_text='In year and months',
                                                max_length=20,
                                                required=False)
    created_on = serializers.DateTimeField(read_only=True, format=DATETIME_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True, format=DATETIME_FORMAT)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = PastEmployment.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        PastEmployment.objects.filter(id=instance.id).update(**validated_data)
        return PastEmployment.objects.get(id=instance.id)


class PermanentAddressSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    address = serializers.CharField(allow_blank=True, allow_null=True, max_length=200, required=False)
    pin = serializers.CharField(allow_blank=True, allow_null=True, max_length=8, required=False)
    phone = serializers.CharField(allow_blank=True, allow_null=True, max_length=15, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    city = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=City.objects.all(), required=False)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def to_representation(self, instance):
        self.fields['city'] = CitySerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = PermanentAddress.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        PermanentAddress.objects.filter(id=instance.id).update(**validated_data)
        return PermanentAddress.objects.get(id=instance.id)

    def validate_phone(self, value):
        if not validate_mobile_number(value) and value:
            raise serializers.ValidationError("Not a valid mobile number")
        return value

class ReferralSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(allow_blank=True, allow_null=True, max_length=100, required=False)
    organisation = serializers.CharField(allow_blank=True, allow_null=True, max_length=100, required=False)
    designation = serializers.CharField(allow_blank=True, allow_null=True, max_length=100, required=False)
    phone = serializers.CharField(allow_blank=True, allow_null=True, max_length=15, required=False)
    address = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    email = serializers.EmailField(allow_blank=True, allow_null=True, max_length=35, required=False)
    nature_of_assisstance = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                                  style={'base_template': 'textarea.html'})
    number_of_year = serializers.CharField(allow_blank=True, allow_null=True, max_length=5, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = Referral.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        Referral.objects.filter(id=instance.id).update(**validated_data)
        return Referral.objects.get(id=instance.id)

    def validate_phone(self, value):
        if not validate_mobile_number(value) and value:
            raise serializers.ValidationError("Not a valid mobile number")
        return value

class EmploymentAgencySerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    agency_name = serializers.CharField(allow_blank=True, allow_null=True, max_length=70, required=False)
    contact_name = serializers.CharField(allow_blank=True, allow_null=True, max_length=35, required=False)
    phone = serializers.CharField(allow_blank=True, allow_null=True, max_length=15, required=False)
    email = serializers.EmailField(allow_blank=True, allow_null=True, max_length=50, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = EmploymentAgency.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        EmploymentAgency.objects.filter(id=instance.id).update(**validated_data)
        return EmploymentAgency.objects.get(id=instance.id)


class EmployeeSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    employee_id = serializers.CharField(max_length=35,
                                        validators=[UniqueValidator(queryset=Employee.objects.all())])
    reporting_person = serializers.CharField(allow_blank=True, allow_null=True, max_length=35, required=False)
    date_of_birth = serializers.DateField(
        allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601], format=DATE_FORMAT)
    date_of_joining = serializers.DateField(
        allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601], format=DATE_FORMAT)
    date_of_leaving = serializers.DateField(
        allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601], format=DATE_FORMAT)
    gender = serializers.ChoiceField(allow_null=True, choices=(('male', 'Male'), ('female', 'Female')), required=False)
    pan = serializers.CharField(allow_blank=True, allow_null=True, max_length=20, required=False)
    aadhaar = serializers.CharField(allow_blank=True, allow_null=True, max_length=20, required=False)
    passport = serializers.CharField(allow_blank=True, allow_null=True, max_length=20, required=False)
    marital_status = serializers.ChoiceField(
        allow_blank=True, allow_null=True,
        choices=(('married', 'Married'), ('unmarried', 'Unmarried'), ('divorcee', 'Divorcee')), required=False
    )
    status = serializers.ChoiceField(allow_null=True, choices=(('active', 'Active'), ('inactive', 'Inactive')),
                                     required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    office = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=AahoOffice.objects.all(), required=False)
    username = serializers.SlugRelatedField(queryset=User.objects.all(), required=False,
                                            validators=[UniqueValidator(queryset=Employee.objects.all())],
                                            slug_field="username")
    designation = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Designation.objects.all(),
                                                     required=False)
    department = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Department.objects.all(), required=False)
    fitness_details = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=FitnessDetail.objects.all(),
                                                         required=False)
    bank = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=Bank.objects.all(), required=False,
        validators=[UniqueValidator(queryset=Employee.objects.all())])
    past_employment = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PastEmployment.objects.all(), required=False,
        validators=[UniqueValidator(queryset=Employee.objects.all())]
    )
    referral = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True, queryset=Referral.objects.all(), required=False,
        validators=[UniqueValidator(queryset=Employee.objects.all())]
    )
    permanent_address = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True, queryset=PermanentAddress.objects.all(), required=False,
        validators=[UniqueValidator(queryset=Employee.objects.all())]
    )
    employment_agency = serializers.PrimaryKeyRelatedField(write_only=True, allow_null=True,
                                                           queryset=EmploymentAgency.objects.all(),
                                                           required=False)

    office_multiple = serializers.PrimaryKeyRelatedField(write_only=True, allow_empty=False, many=True,
                                                         queryset=AahoOffice.objects.all())
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    emp_name = serializers.SerializerMethodField()
    emp_phone = serializers.SerializerMethodField()
    emp_alt_phone = serializers.SerializerMethodField()
    emp_email = serializers.SerializerMethodField()
    bank_account = serializers.SerializerMethodField()

    def get_bank_account(self, instance):
        if isinstance(instance.username, User):
            bank = get_or_none(Bank, user=instance.username)
            if isinstance(bank, Bank):
                return BankSerializer(instance=bank).data
        return {}

    def get_emp_alt_phone(self, instance):
        return instance.emp_alt_phone()

    def get_emp_name(self, instance):
        return instance.emp_name()

    def get_emp_phone(self, instance):
        return instance.emp_phone()

    def get_emp_email(self, instance):
        return instance.emp_email

    def create(self, validated_data):
        office_multiple = []
        if "office_multiple" in validated_data.keys():
            office_multiple = validated_data.pop("office_multiple")
        instance = Employee.objects.create(**validated_data)
        for office in office_multiple:
            instance.office_multiple.add(office)
        return instance

    def update(self, instance, validated_data):

        office_multiple = []
        if "office_multiple" in validated_data.keys():
            instance.office_multiple.clear()
            office_multiple = validated_data.pop("office_multiple")
        Employee.objects.filter(id=instance.id).update(**validated_data)
        for office in office_multiple:
            instance.office_multiple.add(office)
        return Employee.objects.get(id=instance.id)


class CurrentEmploymentDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    current_job_responsibilities = serializers.CharField(allow_blank=True, allow_null=True,
                                                         label='Outline briefly current job responsibilities',
                                                         required=False,
                                                         style={'base_template': 'textarea.html'})
    present_salary = serializers.IntegerField(help_text='CTC P.A.', max_value=2147483647, min_value=-2147483648,
                                              required=False)
    role = serializers.CharField(allow_blank=True, allow_null=True, max_length=200, required=False)
    e_shops = serializers.CharField(allow_blank=True, allow_null=True, max_length=50, required=False)
    date_of_acquisition = serializers.CharField(allow_blank=True, allow_null=True, max_length=15, required=False)
    date_of_vesting = serializers.CharField(allow_blank=True, allow_null=True, max_length=15, required=False)
    date_of_selling = serializers.CharField(allow_blank=True, allow_null=True, max_length=15, required=False)
    pan = serializers.CharField(allow_blank=True, allow_null=True, max_length=15, required=False)
    id_type = serializers.CharField(allow_blank=True, allow_null=True, max_length=70, required=False)
    id_number = serializers.CharField(allow_blank=True, allow_null=True, max_length=25, required=False)
    pf_account = serializers.CharField(allow_blank=True, allow_null=True, max_length=35, required=False)
    remarks = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                    style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    employee = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Employee.objects.all(), required=False)
    designation = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Designation.objects.all(),
                                                     required=False)
    department = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Department.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["employee"] = EmployeeSerializer(read_only=True)
        self.fields["designation"] = DesignationSerializer(read_only=True)
        self.fields["department"] = DepartmentSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = CurrentEmploymentDetails.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        CurrentEmploymentDetails.objects.filter(id=instance.id).update(**validated_data)
        return CurrentEmploymentDetails.objects.get(id=instance.id)


class EducationalDegreeSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    course_name = serializers.CharField(allow_blank=True, allow_null=True, max_length=50, required=False)
    college_name = serializers.CharField(allow_blank=True, allow_null=True, max_length=200, required=False)
    university_name = serializers.CharField(allow_blank=True, allow_null=True, max_length=200, required=False)
    specialization = serializers.CharField(allow_blank=True, allow_null=True, max_length=200, required=False)
    marks_obtained = serializers.CharField(allow_blank=True, allow_null=True, max_length=20, required=False)
    max_marks = serializers.CharField(allow_blank=True, allow_null=True, max_length=10, required=False)
    passing_year = serializers.DateField(allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601],
                                         format=DATE_FORMAT)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    employee = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Employee.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["employee"] = EmployeeSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = EducationalDegree.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        EducationalDegree.objects.filter(id=instance.id).update(**validated_data)
        return EducationalDegree.objects.get(id=instance.id)


class CertificationCourseSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    course_name = serializers.CharField(allow_blank=True, allow_null=True, max_length=200, required=False)
    obtained_from = serializers.CharField(allow_blank=True, allow_null=True, max_length=200, required=False)
    validity = serializers.DateField(allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601],
                                     format=DATE_FORMAT)
    quality = serializers.CharField(allow_blank=True, allow_null=True, max_length=20, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    employee = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Employee.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["employee"] = EmployeeSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = CertificationCourse.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        CertificationCourse.objects.filter(id=instance.id).update(**validated_data)
        return CertificationCourse.objects.get(id=instance.id)


class SkillSetSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    technical_skill = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                            style={'base_template': 'textarea.html'})
    professional_skill = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                               style={'base_template': 'textarea.html'})
    others = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                   style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    employee = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Employee.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["employee"] = EmployeeSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = SkillSet.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        SkillSet.objects.filter(id=instance.id).update(**validated_data)
        return SkillSet.objects.get(id=instance.id)


class NomineeSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name_of_nominee = serializers.CharField(allow_blank=True, allow_null=True, max_length=35, required=False)
    relationship_with_employee = serializers.CharField(allow_blank=True, allow_null=True, max_length=35, required=False)
    type_of_nomination = serializers.CharField(allow_blank=True, allow_null=True, max_length=35, required=False)
    nominee_age = serializers.CharField(allow_blank=True, allow_null=True, max_length=10, required=False)
    percentage_share = serializers.DecimalField(decimal_places=2, help_text='Max share is 100.00', max_digits=8,
                                                required=False)
    address = serializers.CharField(allow_blank=True, allow_null=True, max_length=200, required=False)
    pin = serializers.CharField(allow_blank=True, allow_null=True, max_length=8, required=False)
    phone = serializers.CharField(allow_blank=True, allow_null=True, max_length=15, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    employee = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Employee.objects.all(), required=False)
    city = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=City.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["employee"] = EmployeeSerializer(read_only=True)
        self.fields["city"] = CitySerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = Nominee.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        Nominee.objects.filter(id=instance.id).update(**validated_data)
        return Nominee.objects.get(id=instance.id)

    def validate_phone(self, value):
        if not validate_mobile_number(value) and value:
            raise serializers.ValidationError("Not a valid mobile number")
        return value

class LeaveRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    leave_approval_status = serializers.ChoiceField(
        choices=(('Approved', 'Approved'), ('Cancelled', 'Cancelled'), ('Pending', 'Pending')), required=False)
    leave_category = serializers.ChoiceField(
        choices=(('Paid Leave', 'Paid Leave'), ('Casual Leave', 'Casual Leave'), ('Medical Leave', 'Medical Leave')))
    from_date = serializers.DateField(allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601],
                                      format=DATE_FORMAT)
    to_date = serializers.DateField(allow_null=True, required=False, input_formats=[DATE_FORMAT, ISO_8601],
                                    format=DATE_FORMAT)
    reason_for_leave = serializers.CharField(required=False,
                                             style={'base_template': 'textarea.html'})
    leave_balance = serializers.CharField(allow_blank=True, allow_null=True, max_length=70, required=False)
    remarks = serializers.CharField(allow_blank=True, allow_null=True, required=False,
                                    style={'base_template': 'textarea.html'})
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    employee = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Employee.objects.all(), required=False)
    sanctioning_person = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Employee.objects.all(),
                                                            required=False)

    def to_representation(self, instance):
        self.fields["employee"] = EmployeeSerializer(read_only=True)
        self.fields["sanctioning_person"] = EmployeeSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = LeaveRecord.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        LeaveRecord.objects.filter(id=instance.id).update(**validated_data)
        return LeaveRecord.objects.get(id=instance.id)


class SalarySerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    pan_number = serializers.CharField(allow_blank=True, allow_null=True, max_length=13, required=False)
    total_salary = serializers.IntegerField(allow_null=True, label='A. Total Salary', max_value=2147483647,
                                            min_value=0,
                                            required=False)
    advance_payment = serializers.IntegerField(allow_null=True, label='B. Advance', max_value=2147483647,
                                               min_value=0,
                                               required=False)
    travel_allowance = serializers.IntegerField(allow_null=True, label='C. Travel Allowance', max_value=2147483647,
                                                min_value=-2147483648, required=False)
    food_allowance = serializers.IntegerField(allow_null=True, label='D. Food Allowance', max_value=2147483647,
                                              min_value=-2147483648, required=False)
    mobile_allowance = serializers.IntegerField(allow_null=True, label='E. Mobile Allowance', max_value=2147483647,
                                                min_value=-2147483648, required=False)
    tax_deduction = serializers.IntegerField(allow_null=True, label='F. Mobile Allowance', max_value=2147483647,
                                             min_value=-2147483648, required=False)
    bill_submission = serializers.IntegerField(allow_null=True, label='G. Bill submission (apart from C, D, E)',
                                               max_value=2147483647, min_value=-2147483648, required=False)
    net_payable = serializers.IntegerField(allow_null=True, label='H. Net Payable (A-B+C+D+E-F+G)',
                                           max_value=2147483647,
                                           min_value=-2147483648, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    employee = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Employee.objects.all(), required=False)

    def to_representation(self, instance):
        self.fields["employee"] = EmployeeSerializer(read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        instance = Salary.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        Salary.objects.filter(id=instance.id).update(**validated_data)
        return Salary.objects.get(id=instance.id)


class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    name = serializers.CharField(max_length=70, validators=[UniqueValidator(queryset=Task.objects.all())])
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        instance = Task.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        Task.objects.filter(id=instance.id).update(**validated_data)
        return Task.objects.get(id=instance.id)


class TaskEmailSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    office = serializers.PrimaryKeyRelatedField(queryset=AahoOffice.objects.all(), required=True)
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=True)
    employee = serializers.PrimaryKeyRelatedField(allow_empty=False, many=True, queryset=Employee.objects.all())

    def to_representation(self, instance):
        self.fields["office"] = AahoOfficeSerializer(read_only=True)
        self.fields["task"] = TaskSerializer(read_only=True)
        self.fields["employee"] = EmployeeSerializer(many=True, read_only=True)
        return super().to_representation(instance=instance)

    def create(self, validated_data):
        employee = []
        if "employee" in validated_data.keys():
            employee = validated_data.pop("employee")
        instance = TaskEmail.objects.create(**validated_data)
        for employ in employee:
            instance.employee.add(employ)
        return instance

    def update(self, instance, validated_data):
        employee = []
        if "employee" in validated_data.keys():
            instance.employee.clear()
            employee = validated_data.pop("employee")
        TaskEmail.objects.filter(id=instance.id).update(**validated_data)
        for employ in employee:
            instance.employee.add(employ)
        return TaskEmail.objects.get(id=instance.id)
