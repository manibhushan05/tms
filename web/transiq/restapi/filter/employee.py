from django_filters import rest_framework as filters

from employee.models import Employee


class EmployeeFilter(filters.FilterSet):
    GENDER_CHOICE = (
        ('male', 'Male'),
        ('female', 'Female')
    )
    MARITAL_STATUS = (
        ('married', 'Married'),
        ('unmarried', 'Unmarried'),
        ('divorcee', 'Divorcee')
    )
    STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    aaho_office = filters.CharFilter(name="office__branch_name", label="Aaho Office branch name",
                                     lookup_expr='icontains')
    aaho_office_null = filters.BooleanFilter(name="office", label="Is Aaho Office Null", lookup_expr="isnull")

    office_multiple = filters.CharFilter(name="office_multiple__branch_name", label="Multiple Office branch names",
                                         lookup_expr='icontains')
    office_multiple_null = filters.BooleanFilter(name="office_multiple", label="Is Multiple Office Null",
                                                 lookup_expr="isnull")

    username = filters.CharFilter(name="username__username", label="User name", lookup_expr='icontains')
    username_null = filters.BooleanFilter(name="username", label="Is Username Null", lookup_expr="isnull")

    employee_id = filters.CharFilter(name='employee_id', label="Employee ID", lookup_expr="icontains")

    designation = filters.CharFilter(name='designation__name', label="Designation", lookup_expr="exact")
    designation_null = filters.BooleanFilter(name="designation", label="Is Designation Null", lookup_expr="isnull")

    department = filters.CharFilter(name='department__name', label="Department", lookup_expr="exact")
    department_null = filters.BooleanFilter(name="department", label="Is Department Null", lookup_expr="isnull")

    reporting_person = filters.CharFilter(name='reporting_person', label="Reporting Person", lookup_expr="exact")
    reporting_person_null = filters.BooleanFilter(name="reporting_person", label="Is Reporting Person Null",
                                                  lookup_expr="isnull")

    date_of_birth = filters.IsoDateTimeFilter(name="date_of_birth", label="DOB")
    date_of_birth_between = filters.DateTimeFromToRangeFilter(name="date_of_birth", label="DOB Between")

    date_of_joining = filters.IsoDateTimeFilter(name="date_of_joining", label="Date Of joining")
    date_of_joining_between = filters.DateTimeFromToRangeFilter(name="date_of_joining", label="Date of joining Between")

    date_of_leaving = filters.IsoDateTimeFilter(name="date_of_leaving", label="Date of Leaving")
    date_of_leaving_between = filters.DateTimeFromToRangeFilter(name="date_of_leaving", label="Date of Leaving between")

    gender = filters.ChoiceFilter(name="gender", choices=GENDER_CHOICE)

    pan = filters.CharFilter(name="pan", label="PAN", lookup_expr='icontains')
    pan_null = filters.BooleanFilter(name="pan", label="Is PAN Null", lookup_expr="isnull")

    aadhaar = filters.CharFilter(name="aadhaar", label="Adhaar", lookup_expr='icontains')
    aadhaar_null = filters.BooleanFilter(name="aadhaar", label="Is Adhaar Null", lookup_expr="isnull")

    passport = filters.CharFilter(name="passport", label="Passport", lookup_expr='icontains')
    passport_null = filters.BooleanFilter(name="passport", label="Is Passport Null", lookup_expr="isnull")

    marital_status = filters.ChoiceFilter(name="marital_status", choices=MARITAL_STATUS)
    marital_status_null = filters.BooleanFilter(name="marital_status", label="Is Marital Status Null",
                                                lookup_expr="isnull")

    blood_group = filters.CharFilter(name="fitness_details__blood_group", label="Blood_group", lookup_expr='icontains')
    blood_group_null = filters.BooleanFilter(name="fitness_details__blood_group", label="Is Blood group Null",
                                             lookup_expr="isnull")

    bank_null = filters.BooleanFilter(name="bank", label="Is Bank Null", lookup_expr="isnull")
    account_number = filters.CharFilter(name="bank__account_number", label="Account Number",
                                        lookup_expr='exact')
    bank_name = filters.CharFilter(name="bank__bank", label="Bank Name", lookup_expr='icontains')
    ifsc = filters.CharFilter(name="bank__ifsc", label="IFSC Code", lookup_expr='icontains')

    past_employment_null = filters.BooleanFilter(name="past_employment", label="Is Past Employment Null",
                                                 lookup_expr="isnull")
    previous_organisation = filters.CharFilter(name="past_employment__organisation", label="Previous Organistion",
                                               lookup_expr='icontains')
    previous_designation = filters.CharFilter(name="past_employment__designation", label="Previous Designation",
                                              lookup_expr='icontains')

    referral = filters.CharFilter(name="referral__name", label="Referral", lookup_expr='icontains')
    referral_null = filters.BooleanFilter(name="referral", label="Is Referral Null", lookup_expr="isnull")

    permanent_address = filters.CharFilter(name="permanent_address__address", label="Permanent address",
                                           lookup_expr='icontains')
    permanent_address_null = filters.BooleanFilter(name="permanent_address", label="Is Permanent address Null",
                                                   lookup_expr="isnull")

    employment_agency = filters.CharFilter(name="employment_agency__agency_name", label="Employment Agency",
                                           lookup_expr='icontains')
    employment_agency_null = filters.BooleanFilter(name="employment_agency", label="Is Employment Agency Null",
                                                   lookup_expr="isnull")

    status = filters.ChoiceFilter(name="status", choices=(('active', 'active'), ('inactive', 'inactive')),
                                  label="Status")

    created_by = filters.CharFilter(name="created_by__username", label="Created By name", lookup_expr="icontains")
    created_by_null = filters.BooleanFilter(name="created_by", label="Is Created By Null", lookup_expr="isnull")

    created_on = filters.IsoDateTimeFilter(name="created_on", label="Created on")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = Employee
        fields = []
