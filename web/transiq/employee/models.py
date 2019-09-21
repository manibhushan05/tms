from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from utils.models import AahoOffice, Address, Bank, City


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="department_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="department_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Designation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="designation_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="designation_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class PastEmployment(models.Model):
    joining_date = models.DateField(blank=True, null=True)
    leaving_date = models.DateField(blank=True, null=True)
    organisation = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    reporting_manager = models.CharField(max_length=100, blank=True, null=True)
    gross_compensation = models.CharField(max_length=20, blank=True, null=True)
    reason_for_change = models.TextField(blank=True, null=True)
    total_experience = models.CharField(max_length=20, blank=True, null=True, help_text='In year and months')
    relevant_experience = models.CharField(max_length=20, blank=True, null=True, help_text='In year and months')
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="past_employment_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="past_employment_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.organisation


class Referral(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    organisation = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(max_length=35, blank=True, null=True)
    nature_of_assisstance = models.TextField(blank=True, null=True)
    number_of_year = models.CharField(max_length=5, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="referral_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="referral_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class PermanentAddress(models.Model):
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=8, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="permanent_address_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="permanent_address_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s, %s, %s' % (self.address, self.city, self.pin)


class EmploymentAgency(models.Model):
    agency_name = models.CharField(max_length=70, blank=True, null=True)
    contact_name = models.CharField(max_length=35, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="employment_agency_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="employment_agency_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.agency_name


class FitnessDetail(models.Model):
    BLOOD_GROUP_STATUS = (
        ('o_pos', 'O+'),
        ('o_neg', 'O-'),
        ('a_pos', 'A+'),
        ('a_neg', 'A-'),
        ('b_pos', 'B+'),
        ('b_neg', 'B-'),
        ('ab_pos', 'AB+'),
        ('ab_neg', 'AB-'),
    )
    height = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text='Height in Inches')
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text='Weight in Kgs')
    blood_group = models.CharField(max_length=10, blank=True, null=True, choices=BLOOD_GROUP_STATUS)
    medical_fitness = models.TextField(blank=True, null=True)
    emergency_contact_person_name = models.CharField(max_length=35, blank=True, null=True)
    emergency_contact_person_phone = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_person_email = models.EmailField(max_length=35, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="fitness_detail_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="fitness_detail_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return 'ID: %s, Height: %s, Weight: %s' % (self.id, self.height, self.weight)


class Employee(models.Model):
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
    office = models.ForeignKey(AahoOffice, null=True, related_name='employee', on_delete=models.CASCADE)
    office_multiple = models.ManyToManyField(AahoOffice, related_name="employee_office_multiple")
    username = models.OneToOneField(User, null=True, related_name='employee', on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=35, unique=True)
    designation = models.ForeignKey(Designation, blank=True, null=True, related_name='employee_designation',
                                    on_delete=models.CASCADE)
    department = models.ForeignKey(Department, blank=True, null=True, related_name='employee_department',
                                   on_delete=models.CASCADE)
    reporting_person = models.CharField(max_length=35, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    date_of_leaving = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICE, null=True)
    pan = models.CharField(max_length=20, blank=True, null=True)
    aadhaar = models.CharField(max_length=20, blank=True, null=True)
    passport = models.CharField(max_length=20, blank=True, null=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS, null=True, blank=True)
    status = models.CharField(max_length=35, choices=STATUS, null=True, default='active')
    fitness_details = models.ForeignKey(FitnessDetail, null=True, blank=True, on_delete=models.CASCADE)
    bank = models.OneToOneField(Bank, blank=True, null=True, on_delete=models.CASCADE)
    past_employment = models.OneToOneField(PastEmployment, blank=True, null=True, related_name='past_emp_employee',
                                           on_delete=models.CASCADE)
    referral = models.OneToOneField(Referral, blank=True, null=True, related_name='referral_employee',
                                    on_delete=models.CASCADE)
    permanent_address = models.OneToOneField(PermanentAddress, blank=True, null=True,
                                             related_name='permanent_address_employee', on_delete=models.CASCADE)
    employment_agency = models.ForeignKey(EmploymentAgency, blank=True, null=True, related_name='emp_agency_employee',
                                          on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="employee_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="employee_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'inactive':
            for task in TaskEmail.objects.filter(employee=self):
                task.employee.remove(self)
            User.objects.filter(id=self.username_id).update(
                is_superuser=False,
                is_active=False,
                is_staff=False
            )

    def emp_name(self):
        try:
            return self.username.profile.name
        except:
            return ''

    def emp_phone(self):
        try:
            return self.username.profile.phone
        except:
            return ''

    @property
    def emp_email(self):
        try:
            return self.username.profile.email
        except:
            return ''

    def emp_alt_phone(self):
        try:
            return self.username.profile.alternate_phone
        except:
            return ''

    def emp_username(self):
        if isinstance(self.username, User):
            return self.username.username
        return ''

    def __str__(self):
        return '%s' % (self.emp_name())


class CurrentEmploymentDetails(models.Model):
    employee = models.ForeignKey(Employee, blank=True, null=True, related_name='current_emp_details',
                                 on_delete=models.CASCADE)
    current_job_responsibilities = models.TextField(blank=True, null=True,
                                                    verbose_name="Outline briefly current job responsibilities")
    present_salary = models.IntegerField(default=0, help_text='CTC P.A.')
    role = models.CharField(max_length=200, blank=True, null=True)
    designation = models.ForeignKey(Designation, blank=True, null=True, related_name='current_employee_designation',
                                    on_delete=models.CASCADE)
    department = models.ForeignKey(Department, blank=True, null=True, related_name='current_employee_department',
                                   on_delete=models.CASCADE)
    e_shops = models.CharField(max_length=50, blank=True, null=True)
    date_of_acquisition = models.CharField(max_length=15, blank=True, null=True)
    date_of_vesting = models.CharField(max_length=15, blank=True, null=True)
    date_of_selling = models.CharField(max_length=15, blank=True, null=True)
    pan = models.CharField(max_length=15, blank=True, null=True)
    id_type = models.CharField(max_length=70, blank=True, null=True)
    id_number = models.CharField(max_length=25, blank=True, null=True)
    pf_account = models.CharField(max_length=35, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="current_employment_details_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="current_employment_details_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s' % (self.employee)


class EducationalDegree(models.Model):
    employee = models.ForeignKey(Employee, null=True, related_name='educational_degree', on_delete=models.CASCADE)
    course_name = models.CharField(max_length=50, blank=True, null=True)
    college_name = models.CharField(max_length=200, blank=True, null=True)
    university_name = models.CharField(max_length=200, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    marks_obtained = models.CharField(max_length=20, blank=True, null=True)
    max_marks = models.CharField(max_length=10, blank=True, null=True)
    passing_year = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="educational_degree_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="educational_degree_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s' % (self.employee)


class CertificationCourse(models.Model):
    employee = models.ForeignKey(Employee, blank=True, null=True, related_name='certificates', on_delete=models.CASCADE)
    course_name = models.CharField(max_length=200, blank=True, null=True)
    obtained_from = models.CharField(max_length=200, blank=True, null=True)
    validity = models.DateField(blank=True, null=True)
    quality = models.CharField(max_length=20, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="certification_course_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="certification_course_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s' % (self.employee)


class SkillSet(models.Model):
    employee = models.ForeignKey(Employee, blank=True, null=True, related_name='skill_set', on_delete=models.CASCADE)
    technical_skill = models.TextField(blank=True, null=True)
    professional_skill = models.TextField(blank=True, null=True)
    others = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="skill_set_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="skill_set_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s" % (self.id)


class Nominee(models.Model):
    employee = models.ForeignKey(Employee, blank=True, null=True, related_name='nominee', on_delete=models.CASCADE)
    name_of_nominee = models.CharField(max_length=35, blank=True, null=True)
    relationship_with_employee = models.CharField(max_length=35, blank=True, null=True)
    type_of_nomination = models.CharField(max_length=35, blank=True, null=True)
    nominee_age = models.CharField(max_length=10, blank=True, null=True)
    percentage_share = models.DecimalField(max_digits=8, decimal_places=2, default=0.00,
                                           help_text='Max share is 100.00')
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=8, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="nominee_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="nominee_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s' % (self.employee)


class LeaveRecord(models.Model):
    leave_category_choice = (
        ('Paid Leave', 'Paid Leave'),
        ('Casual Leave', 'Casual Leave'),
        ('Medical Leave', 'Medical Leave'),
    )
    leave_approval_status_choice = (
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
        ('Pending', 'Pending')
    )
    employee = models.ForeignKey(Employee, blank=True, null=True, related_name='leave_record', on_delete=models.CASCADE)
    leave_approval_status = models.CharField(max_length=10, choices=leave_approval_status_choice, default='Pending')
    leave_category = models.CharField(max_length=20, choices=leave_category_choice)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    reason_for_leave = models.TextField(blank=True, null=True)
    sanctioning_person = models.ForeignKey(Employee, blank=True, null=True, related_name='sanction_leave_emp',
                                           on_delete=models.CASCADE)
    leave_balance = models.CharField(max_length=70, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="leave_record_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="leave_record_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s' % (self.employee)


class Salary(models.Model):
    employee = models.ForeignKey(Employee, blank=True, null=True, related_name='salary', on_delete=models.CASCADE)
    pan_number = models.CharField(max_length=13, blank=True, null=True)
    total_salary = models.IntegerField(blank=True, null=True, verbose_name='A. Total Salary', default=0)
    advance_payment = models.IntegerField(blank=True, null=True, verbose_name='B. Advance', default=0)
    travel_allowance = models.IntegerField(blank=True, null=True, verbose_name='C. Travel Allowance', default=0)
    food_allowance = models.IntegerField(blank=True, null=True, verbose_name='D. Food Allowance', default=0)
    mobile_allowance = models.IntegerField(blank=True, null=True, verbose_name='E. Mobile Allowance', default=0)
    tax_deduction = models.IntegerField(blank=True, null=True, verbose_name='F. Mobile Allowance', default=0)
    bill_submission = models.IntegerField(blank=True, null=True, verbose_name='G. Bill submission (apart from C, D, E)',
                                          default=0)
    net_payable = models.IntegerField(default=0, blank=True, null=True, verbose_name='H. Net Payable (A-B+C+D+E-F+G)')
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="salary_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="salary_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.employee.emp_name()


class Task(models.Model):
    name = models.CharField(max_length=70, unique=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="task_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="task_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class TaskEmail(models.Model):
    office = models.ForeignKey(AahoOffice, related_name='task_eamil_office', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name='task_email_work', on_delete=models.CASCADE)
    employee = models.ManyToManyField(Employee, limit_choices_to={'status': 'active'})
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="task_email_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="task_email_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('office', 'task')

    def __str__(self):
        return "%s, %s" % (self.task, self.office)