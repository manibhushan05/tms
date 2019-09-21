from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

from employee.models import Employee
from restapi.signals import booking_status_mapping_post_save_handler
from sme.models import Sme
from team.models import ManualBooking

USER_CATEGORIES = (
    ('customer', 'Customer'),
    ('employee', 'Employee'),
    ('supplier', 'Supplier'),
    ('broker', 'Broker')
)

EMP_ROLES = (
    ('office_data_entry', 'Office Data Entry'),
    ('ops_executive', 'Ops Executive'),
    ('accounts_payable', 'Accounts Payable'),
    ('accounts_receivable', 'Accounts Receivable'),
    ('sales', 'Sales'),
    ('traffic', 'Traffic'),
    ('city_head', 'City Head'),
    ('management', 'Management'),
    ('tech', 'Technology'),
)

EMP_STATUS = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
)

ACCESS_PERMISSIONS = (
    ('read_only', 'Read Only'),
    ('edit', 'Edit'),
)

CONSUMER_PLATFORMS = (
    ('web', 'Web'),
    ('mobile', 'Mobile'),
    ('all', 'All'),
)

EMP_BOOKING_STATUS_ACTION = (
    ('responsible', 'Responsible'),
    ('dependent', 'Dependent'),
)

BOOKING_STATUSES = (
    ('confirmed', 'Confirmed'),
    ('loaded', 'Loaded'),
    ('lr_generated', 'Lr Generated'),
    ('advance_paid', 'Advance Paid'),
    ('unloaded', 'Unloaded'),
    ('pod_uploaded', 'PoD Uploaded'),
    ('pod_verified', 'PoD Verified'),
    ('invoice_raised', 'Invoice Raised'),
    ('invoice_confirmed', 'Invoice Confirmed'),
    ('balance_paid', 'Balance Paid'),
    ('party_invoice_sent', 'Party Invoice Sent'),
    ('inward_followup_completed', 'Inward Followup Completed'),
    ('complete', 'Complete'),
)

BOOKING_STATUSES_LEVEL = (
    ('primary', 'Primary'),
    ('secondary', 'Secondary'),
)

BOOKING_STATUS_STAGE = (
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
    ('reverted', 'Reverted'),
    ('escalated', 'Escalated'),
)

TD_FUNCTIONS = (
    ('new_inquiry', 'Submit New Inquiry'),
    ('customer_inquiries', 'Customer Inquiries'),
    ('open_inquiries', 'Open Inquiries'),
    ('my_inquiries', 'My Inquiries'),
    ('pending_payments', 'Pending Payments'),
    ('pending_lr', 'Pending LR'),
    ('in_transit', 'In Transit'),
    ('invoice_confirmation', 'Invoice Confirmation'),
    ('delivered', 'Delivered'),
    ('confirm_booking', 'New Booking'),
    ('lr_generation', 'Generate LR'),
    ('pay_advance', 'Pay Advance'),
    ('pay_balance', 'Pay Balance'),
    ('send_invoice', 'Send Invoice'),
    ('verify_pod', 'Verify PoD'),
    ('raise_invoice', 'Raise Invoice'),
    ('confirm_invoice', 'Confirm Invoice'),
    ('inward_entry', 'Inward Entry'),
    ('process_payments', 'Process Payments'),
    ('reconcile', 'Reconcile'),
)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class UserCategory(models.Model):
    category = models.CharField(unique=True, max_length=15, null=True, choices=USER_CATEGORIES)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='usercategory_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s' % (self.category)


class EmployeeRoles(models.Model):
    role = models.CharField(unique=True, max_length=35, null=True, choices=EMP_ROLES, default='office_data_entry')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='employeeroles_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s' % self.role

    def get_role(self):
        rol = '' if not self.role else self.get_role_display()
        return {'id': self.id, 'role': rol}


class EmployeeRolesMapping(models.Model):
    employee = models.ForeignKey(Employee, blank=True, null=True, related_name='employee_role_mapping',
                                 on_delete=models.CASCADE)
    employee_role = models.ForeignKey(EmployeeRoles, blank=True, related_name='employee_role',
                                      null=True, on_delete=models.CASCADE)
    employee_status = models.CharField(max_length=15, null=True, choices=EMP_STATUS, default='inactive')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='employeerolesmapping_created_by',
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s, %s, %s' % (self.employee.username, self.employee_role.role, self.employee_status)

    def get_employee_role_username(self):
        role = '' if not self.employee_role else self.employee_role.get_role()
        e_name = '' if not self.employee else self.employee.username.username
        return {'role': role, 'username': e_name}


class BookingStatuses(models.Model):
    status = models.CharField(max_length=35, null=True, choices=BOOKING_STATUSES, default='confirmed')
    # Time limit is in minutes
    time_limit = models.IntegerField(blank=True, null=True, default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='bookingstatus_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s, %s' % (self.get_status_display(), self.time_limit)

    def get_status(self):
        return '' if not self.status else self.get_status_display()


class BookingStatusChain(models.Model):
    booking_status = models.ForeignKey(BookingStatuses, null=True, related_name='booking_status', on_delete=models.CASCADE)
    level = models.CharField(max_length=15, null=True, choices=BOOKING_STATUSES_LEVEL, default='secondary')
    primary_preceded_booking_status = models.ForeignKey(BookingStatuses, null=True,
                                                        related_name='primary_preceded_booking_status', on_delete=models.CASCADE)
    primary_succeeded_booking_status = models.ForeignKey(BookingStatuses, null=True,
                                                         related_name='primary_succeeded_booking_status', on_delete=models.CASCADE)
    secondary_preceded_booking_status = models.ForeignKey(BookingStatuses, null=True,
                                                        related_name='secondary_preceded_booking_status', on_delete=models.CASCADE)
    secondary_succeeded_booking_status = models.ForeignKey(BookingStatuses, null=True,
                                                         related_name='secondary_succeeded_booking_status', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='bookingstatuschain_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s' % self.booking_status.get_status_display()

    def get_booking_status(self):
        return '' if not self.booking_status else self.booking_status.get_status_display()


class EmployeeRolesBookingStatusMapping(models.Model):
    employee_roles_mapping = models.ForeignKey(EmployeeRolesMapping, blank=True, null=True, on_delete=models.CASCADE)
    booking_status_chain = models.ForeignKey(BookingStatusChain, blank=True, null=True, on_delete=models.CASCADE)
    assignment_status = models.CharField(max_length=15, null=True, choices=EMP_STATUS, default='inactive')
    action = models.CharField(max_length=15, null=True, choices=EMP_BOOKING_STATUS_ACTION, default='responsible')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='er_bs_mapping_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s, %s, %s' % (self.employee_roles_mapping.employee.username,
                           self.employee_roles_mapping.employee_role.role, self.booking_status_chain.booking_status.status)


class BookingStatusesMapping(models.Model):

    manual_booking = models.ForeignKey(ManualBooking, blank=True, null=True, related_name='bookings',
                                on_delete=models.CASCADE)
    booking_status_chain = models.ForeignKey(BookingStatusChain, blank=True, null=True, on_delete=models.CASCADE)
    booking_stage = models.CharField(max_length=15, null=True, choices=BOOKING_STATUS_STAGE, default='in_progress')
    due_date = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='bs_mapping_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s, %s, %s' % (self.manual_booking.booking_id if self.manual_booking else '',
                               self.booking_status_chain.booking_status.status if self.booking_status_chain else '',
                               self.booking_stage)

    def get_booking_status_mapping(self):
        return {'booking_id': self.manual_booking.booking_id, 'booking_status': self.booking_status_chain.booking_status.status,
                 'booking_stage': self.booking_stage}


post_save.connect(booking_status_mapping_post_save_handler, sender=BookingStatusesMapping)


class BookingStatusesMappingComments(models.Model):
    booking_status_mapping = models.ForeignKey(BookingStatusesMapping, blank=True, null=True,
                                               related_name='booking_status_mapping_comments', on_delete=models.CASCADE)
    comment = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='bs_mapping_cmts_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def get_booking_status_comment(self):
        bs_mapping = '' if not self.booking_status_mapping else self.booking_status_mapping.get_booking_status_mapping()
        return {'id': self.id, 'booking_status_mapping': bs_mapping, 'comment': self.comment, 'created_on': self.created_on}

    def __str__(self):
        return '%s' % self.id


class BookingStatusesMappingLocation(models.Model):
    booking_status_mapping = models.ForeignKey(BookingStatusesMapping, blank=True, null=True, on_delete=models.CASCADE)
    #booking or vehicle
    latitude = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    longitude = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    district = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True, default='India')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='bs_mapping_location_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s, %s, %s, %s' % (self.booking_status_mapping.manual_booking.booking_id,
                               self.booking_status_mapping.booking_status_chain.booking_status.status, self.latitude,
                               self.longitude)


class TaskDashboardFunctionalities(models.Model):
    functionality = models.CharField(unique=True, max_length=35, null=True, choices=TD_FUNCTIONS, default='new_inquiry')
    consumer = models.CharField(max_length=35, null=True, choices=CONSUMER_PLATFORMS, default='web')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='td_functionality_created_by', on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s' % self.functionality

    def get_functionality(self):
        func = '' if not self.functionality else self.functionality
        return {'id': self.id, 'functionality': func, 'consumer': self.consumer}


class EmployeeRolesFunctionalityMapping(models.Model):
    td_functionality = models.ForeignKey(TaskDashboardFunctionalities, blank=True, null=True, on_delete=models.CASCADE)
    employee_role = models.ForeignKey(EmployeeRoles, blank=True, null=True, on_delete=models.CASCADE)
    caption = models.CharField(max_length=35, null=True, blank=True)
    access = models.CharField(max_length=20, null=True, choices=ACCESS_PERMISSIONS, default='edit')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='employeerolesfunctionality_created_by',
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s, %s, %s' % (self.td_functionality.functionality, self.employee_role.role, self.caption)

    def get_employee_role_functionality(self):
        role = '' if not self.employee_role else self.employee_role.get_role()
        func = '' if not self.td_functionality else self.td_functionality.functionality
        return {'role': role, 'functionality': func}


class SmePaymentFollowupComments(models.Model):
    sme = models.ForeignKey(Sme, blank=True, null=True, related_name="sme_payment_followup", on_delete=models.CASCADE)
    comment = models.CharField(max_length=150, null=True, blank=True)
    due_date = models.DateField(blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='sme_payment_followup_created_by',
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'is_staff': True})
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return '%s, %s, %s' % (self.sme_id, self.comment, self.due_date)
