from django.db.models import Q
from rest_framework import serializers
import requests
from django.utils import timezone
from django.db import IntegrityError
from api.utils import get_or_none, int_or_none
from employee.models import Employee
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from restapi.helper_api import manual_booking_id_list, manual_booking_id_dest_aaho_list, verify_pod_data_count, \
    get_employee_roles
from restapi.models import EMP_ROLES, EmployeeRoles, EMP_STATUS, EmployeeRolesMapping, BOOKING_STATUSES, \
    BookingStatuses, BOOKING_STATUSES_LEVEL, BookingStatusChain, EMP_BOOKING_STATUS_ACTION, \
    EmployeeRolesBookingStatusMapping, BOOKING_STATUS_STAGE, BookingStatusesMapping, TD_FUNCTIONS, \
    TaskDashboardFunctionalities, EmployeeRolesFunctionalityMapping, BookingStatusesMappingComments, \
    BookingStatusesMappingLocation, ACCESS_PERMISSIONS, CONSUMER_PLATFORMS, SmePaymentFollowupComments
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from restapi.views import requirements
from sme.models import Sme
from team.models import ManualBooking, Invoice, OutWardPayment, PendingInwardPaymentEntry


class EmployeeRolesSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    role = serializers.ChoiceField(allow_null=True, choices=EMP_ROLES, required=True,
                                   validators=[
                                       UniqueValidator(queryset=EmployeeRoles.objects.all().exclude(deleted=True))])
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False, write_only=True)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, write_only=True)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    def create(self, validated_data):
        try:
            emp_role = EmployeeRoles.objects.create(**validated_data)
        except (IntegrityError, EmployeeRoles.DoesNotExist):
            raise serializers.ValidationError({'status': 'failure', 'msg': 'EmployeeRoles could not be created'})
        return emp_role

    def update(self, instance, validated_data):
        instance.role = validated_data['role']
        instance.changed_by = validated_data['changed_by']
        instance.save()
        return instance


class EmployeeRolesMappingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    employee_id = serializers.IntegerField(required=True)
    employee = serializers.SerializerMethodField()
    employee_role_id = serializers.IntegerField(required=True)
    employee_role = serializers.SerializerMethodField()
    employee_status = serializers.ChoiceField(allow_null=True, choices=EMP_STATUS, required=True)

    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False, write_only=True)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, write_only=True)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    class Meta:
        validators = [UniqueTogetherValidator(queryset=EmployeeRolesMapping.objects.all().exclude(deleted=True),
                                              fields=('employee_id', 'employee_role_id'))]

    def create(self, validated_data):
        try:
            employee = Employee.objects.get(id=validated_data['employee_id'])
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee Does Not Exist")
        try:
            employee_role = EmployeeRoles.objects.get(id=validated_data['employee_role_id'])
        except EmployeeRoles.DoesNotExist:
            raise serializers.ValidationError("EmployeeRoles Does Not Exist")
        employee_role_mapping = EmployeeRolesMapping.objects.create(employee=employee, employee_role=employee_role,
                                                                    employee_status=validated_data['employee_status'],
                                                                    created_by=validated_data['created_by'])
        return employee_role_mapping

    def update(self, instance, validated_data):
        try:
            employee = Employee.objects.get(id=validated_data['employee_id'])
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee Does Not Exist")
        try:
            employee_role = EmployeeRoles.objects.get(id=validated_data['employee_role_id'])
        except EmployeeRoles.DoesNotExist:
            raise serializers.ValidationError("EmployeeRoles Does Not Exist")
        instance.employee = employee
        instance.employee_role = employee_role
        instance.employee_status = validated_data['employee_status']
        instance.changed_by = validated_data['changed_by']
        instance.save()
        return instance

    def get_employee(self, obj):
        employee = get_or_none(Employee, id=int_or_none(obj.employee_id))
        if not employee:
            raise serializers.ValidationError("Employee Does Not Exist")
        return {'employee_name': employee.emp_name(), "aaho_office_id": employee.office.id}

    def get_employee_role(self, obj):
        employee_role = get_or_none(EmployeeRoles, id=int_or_none(obj.employee_role_id))
        if not employee_role:
            raise serializers.ValidationError("EmployeeRoles Does Not Exist")
        return employee_role.get_role()


class BookingStatusesSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.ChoiceField(allow_null=True, choices=BOOKING_STATUSES, required=True,
                                     validators=[
                                         UniqueValidator(queryset=BookingStatuses.objects.all().exclude(deleted=True))])
    time_limit = serializers.IntegerField(required=True)

    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False, write_only=True)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, write_only=True)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    def create(self, validated_data):
        try:
            bs = BookingStatuses.objects.create(**validated_data)
        except (IntegrityError, BookingStatuses.DoesNotExist):
            raise serializers.ValidationError({'status': 'failure', 'msg': 'BookingStatuses could not be created'})
        return bs

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.time_limit = validated_data['time_limit']
        instance.changed_by = validated_data['changed_by']
        instance.save()
        return instance


class BookingStatusChainSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    booking_status_id = serializers.IntegerField(required=True)
    booking_status = serializers.SerializerMethodField()
    level = serializers.ChoiceField(allow_null=True, choices=BOOKING_STATUSES_LEVEL, required=True)
    primary_preceded_booking_status_id = serializers.IntegerField(required=True)
    primary_preceded_booking_status = serializers.SerializerMethodField()
    primary_succeeded_booking_status_id = serializers.IntegerField(required=True)
    primary_succeeded_booking_status = serializers.SerializerMethodField()
    secondary_preceded_booking_status_id = serializers.IntegerField(required=True)
    secondary_preceded_booking_status = serializers.SerializerMethodField()
    secondary_succeeded_booking_status_id = serializers.IntegerField(required=True)
    secondary_succeeded_booking_status = serializers.SerializerMethodField()

    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False, write_only=True)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, write_only=True)

    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    class Meta:
        validators = [UniqueTogetherValidator(queryset=BookingStatusChain.objects.all().exclude(deleted=True),
                                              fields=('booking_status_id', 'primary_preceded_booking_status_id',
                                                      'primary_succeeded_booking_status_id')),
                      UniqueTogetherValidator(queryset=BookingStatusChain.objects.all().exclude(deleted=True),
                                              fields=('booking_status_id', 'secondary_preceded_booking_status_id',
                                                      'secondary_succeeded_booking_status_id'))]

    def create(self, validated_data):
        try:
            booking_status = BookingStatuses.objects.get(id=validated_data['booking_status_id'])
        except BookingStatuses.DoesNotExist:
            raise serializers.ValidationError("Booking Status Does Not Exist")
        try:
            primary_preceded_booking_status = BookingStatuses.objects.get(
                id=validated_data['primary_preceded_booking_status_id'])
        except BookingStatuses.DoesNotExist:
            raise serializers.ValidationError("Primary Preceded Booking Status Does Not Exist")
        try:
            primary_succeeded_booking_status = BookingStatuses.objects.get(
                id=validated_data['primary_succeeded_booking_status_id'])
        except BookingStatuses.DoesNotExist:
            raise serializers.ValidationError("Primary Succeeded Booking Status Does Not Exist")
        try:
            secondary_preceded_booking_status = BookingStatuses.objects.get(
                id=validated_data['secondary_preceded_booking_status_id'])
        except BookingStatuses.DoesNotExist:
            raise serializers.ValidationError("Secondary Preceded Booking Status Does Not Exist")
        try:
            secondary_succeeded_booking_status = BookingStatuses.objects.get(
                id=validated_data['secondary_succeeded_booking_status_id'])
        except BookingStatuses.DoesNotExist:
            raise serializers.ValidationError("Secondary Succeeded Booking Status Does Not Exist")

        booking_status_chain = BookingStatusChain.objects.create(booking_status=booking_status,
                                                                 level=validated_data['level'],
                                                                 primary_preceded_booking_status=primary_preceded_booking_status,
                                                                 primary_succeeded_booking_status=primary_succeeded_booking_status,
                                                                 secondary_preceded_booking_status=secondary_preceded_booking_status,
                                                                 secondary_succeeded_booking_status=secondary_succeeded_booking_status,
                                                                 created_by=validated_data['created_by'])
        return booking_status_chain

    def update(self, instance, validated_data):
        try:
            booking_status = BookingStatuses.objects.get(id=validated_data['booking_status_id'])
        except BookingStatuses.DoesNotExist:
            raise serializers.ValidationError("Booking Status Does Not Exist")
        try:
            primary_preceded_booking_status = BookingStatuses.objects.get(
                id=validated_data['primary_preceded_booking_status_id'])
        except BookingStatuses.DoesNotExist:
            raise serializers.ValidationError("Primary Preceded Booking Status Does Not Exist")
        try:
            primary_succeeded_booking_status = BookingStatuses.objects.get(
                id=validated_data['primary_succeeded_booking_status_id'])
        except BookingStatuses.DoesNotExist:
            raise serializers.ValidationError("Primary Succeeded Booking Status Does Not Exist")
        try:
            secondary_preceded_booking_status = BookingStatuses.objects.get(
                id=validated_data['secondary_preceded_booking_status_id'])
        except BookingStatuses.DoesNotExist:
            raise serializers.ValidationError("Secondary Preceded Booking Status Does Not Exist")
        try:
            secondary_succeeded_booking_status = BookingStatuses.objects.get(
                id=validated_data['secondary_succeeded_booking_status_id'])
        except BookingStatuses.DoesNotExist:
            raise serializers.ValidationError("Secondary Succeeded Booking Status Does Not Exist")

        instance.booking_status = booking_status
        instance.primary_preceded_booking_status = primary_preceded_booking_status
        instance.primary_succeeded_booking_status = primary_succeeded_booking_status
        instance.secondary_preceded_booking_status = secondary_preceded_booking_status
        instance.secondary_succeeded_booking_status = secondary_succeeded_booking_status
        instance.level = validated_data['level']
        instance.changed_by = validated_data['changed_by']
        instance.save()
        return instance

    def get_booking_status(self, obj):
        booking_status = get_or_none(BookingStatuses, id=int_or_none(obj.booking_status_id))
        if not booking_status:
            raise serializers.ValidationError("BookingStatuses Does Not Exist")
        return booking_status.get_status()

    def get_primary_preceded_booking_status(self, obj):
        booking_status = get_or_none(BookingStatuses, id=int_or_none(obj.primary_preceded_booking_status_id))
        if not booking_status:
            raise serializers.ValidationError("BookingStatuses Does Not Exist")
        return booking_status.get_status()

    def get_primary_succeeded_booking_status(self, obj):
        booking_status = get_or_none(BookingStatuses, id=int_or_none(obj.primary_succeeded_booking_status_id))
        if not booking_status:
            raise serializers.ValidationError("BookingStatuses Does Not Exist")
        return booking_status.get_status()

    def get_secondary_preceded_booking_status(self, obj):
        booking_status = get_or_none(BookingStatuses, id=int_or_none(obj.secondary_preceded_booking_status_id))
        if not booking_status:
            raise serializers.ValidationError("BookingStatuses Does Not Exist")
        return booking_status.get_status()

    def get_secondary_succeeded_booking_status(self, obj):
        booking_status = get_or_none(BookingStatuses, id=int_or_none(obj.secondary_succeeded_booking_status_id))
        if not booking_status:
            raise serializers.ValidationError("BookingStatuses Does Not Exist")
        return booking_status.get_status()


class EmployeeRolesBookingStatusMappingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    booking_status_chain_id = serializers.IntegerField(required=True)
    booking_status_chain = serializers.SerializerMethodField()
    employee_roles_mapping_id = serializers.IntegerField(required=True)
    employee_roles_mapping = serializers.SerializerMethodField()
    assignment_status = serializers.ChoiceField(allow_null=True, choices=EMP_STATUS, required=True)
    action = serializers.ChoiceField(allow_null=True, choices=EMP_BOOKING_STATUS_ACTION, required=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False, write_only=True)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, write_only=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    class Meta:
        validators = [
            UniqueTogetherValidator(queryset=EmployeeRolesBookingStatusMapping.objects.all().exclude(deleted=True),
                                    fields=('booking_status_chain_id', 'employee_roles_mapping_id'))]

    def create(self, validated_data):
        try:
            booking_status_chain = BookingStatusChain.objects.get(id=validated_data['booking_status_chain_id'])
        except BookingStatusChain.DoesNotExist:
            raise serializers.ValidationError("Booking Status Chain Does Not Exist")
        try:
            employee_roles_mapping = EmployeeRolesMapping.objects.get(id=validated_data['employee_roles_mapping_id'])
        except EmployeeRolesMapping.DoesNotExist:
            raise serializers.ValidationError("Employee Roles Mapping Does Not Exist")

        employee_roles_booking_status_mapping = EmployeeRolesBookingStatusMapping.objects.create(
            employee_roles_mapping=employee_roles_mapping,
            booking_status_chain=booking_status_chain,
            assignment_status=validated_data['assignment_status'],
            action=validated_data['action'],
            created_by=validated_data['created_by'])
        return employee_roles_booking_status_mapping

    def update(self, instance, validated_data):
        try:
            booking_status_chain = BookingStatusChain.objects.get(id=validated_data['booking_status_chain_id'])
        except BookingStatusChain.DoesNotExist:
            raise serializers.ValidationError("Booking Status Chain Does Not Exist")
        try:
            employee_roles_mapping = EmployeeRolesMapping.objects.get(id=validated_data['employee_roles_mapping_id'])
        except EmployeeRolesMapping.DoesNotExist:
            raise serializers.ValidationError("Employee Roles Mapping Does Not Exist")

        instance.employee_roles_mapping = employee_roles_mapping
        instance.booking_status_chain = booking_status_chain
        instance.assignment_status = validated_data['assignment_status']
        instance.action = validated_data['action']
        instance.changed_by = validated_data['changed_by']
        instance.save()
        return instance

    def get_booking_status_chain(self, obj):
        booking_status_chain = get_or_none(BookingStatusChain, id=int_or_none(obj.booking_status_chain_id))
        if not booking_status_chain:
            raise serializers.ValidationError("BookingStatusChain Does Not Exist")
        return booking_status_chain.get_booking_status()

    def get_employee_roles_mapping(self, obj):
        employee_roles_mapping = get_or_none(EmployeeRolesMapping, id=int_or_none(obj.employee_roles_mapping_id))
        if not employee_roles_mapping:
            raise serializers.ValidationError("EmployeeRolesMapping Does Not Exist")
        return employee_roles_mapping.get_employee_role_username()


class BookingStatusesMappingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    booking_status_chain_id = serializers.IntegerField(required=True)
    booking_status_chain = serializers.SerializerMethodField()
    manual_booking_id = serializers.IntegerField(required=True)
    manual_booking = serializers.SerializerMethodField()
    booking_stage = serializers.ChoiceField(allow_null=True, choices=BOOKING_STATUS_STAGE, required=True)
    due_date = serializers.DateTimeField(allow_null=True, required=False)
    due_date_m = serializers.SerializerMethodField()
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False, write_only=True)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, write_only=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    # class Meta:
    #     validators = [UniqueTogetherValidator(queryset=BookingStatusesMapping.objects.all().exclude(deleted=True),
    #                                           fields=('booking_status_chain_id', 'manual_booking_id'))]

    def create(self, validated_data):
        try:
            booking_status_chain = BookingStatusChain.objects.get(id=validated_data['booking_status_chain_id'])
        except BookingStatusChain.DoesNotExist:
            raise serializers.ValidationError("Booking Status Chain Does Not Exist")
        try:
            manual_booking = ManualBooking.objects.get(id=validated_data['manual_booking_id'])
        except ManualBooking.DoesNotExist:
            raise serializers.ValidationError("Manual Booking Does Not Exist")
        booking_statuses_mapping = BookingStatusesMapping.objects.filter(booking_status_chain=booking_status_chain,
                                                                         manual_booking=manual_booking)
        due_date = (timezone.now() + timedelta(minutes=booking_status_chain.booking_status.time_limit))
        if not booking_statuses_mapping:
            booking_statuses_mapping = BookingStatusesMapping.objects.create(booking_status_chain=booking_status_chain,
                                                                             manual_booking=manual_booking,
                                                                             booking_stage=validated_data['booking_stage'],
                                                                             created_by=validated_data['created_by'],
                                                                             due_date=due_date)
        else:
            booking_statuses_mapping = booking_statuses_mapping.order_by('id').last()
            BookingStatusesMapping.objects.filter(id=booking_statuses_mapping.id).update(
                booking_status_chain=booking_status_chain,
                manual_booking=manual_booking,
                booking_stage=validated_data['booking_stage'],
                changed_by=validated_data['created_by'],
                due_date=due_date)
        return booking_statuses_mapping

    def update(self, instance, validated_data):
        try:
            booking_status_chain = BookingStatusChain.objects.get(id=validated_data['booking_status_chain_id'])
        except BookingStatusChain.DoesNotExist:
            raise serializers.ValidationError("Booking Status Chain Does Not Exist")
        try:
            manual_booking = ManualBooking.objects.get(id=validated_data['manual_booking_id'])
        except ManualBooking.DoesNotExist:
            raise serializers.ValidationError("Manual Booking Does Not Exist")

        instance.booking_status_chain = booking_status_chain
        instance.manual_booking = manual_booking
        instance.booking_stage = validated_data['booking_stage']
        instance.changed_by = validated_data['changed_by']
        instance.due_date = validated_data['due_date'] if 'due_date' in validated_data else instance.due_date
        instance.save()
        return instance

    def get_booking_status_chain(self, obj):
        booking_status_chain = get_or_none(BookingStatusChain, id=int_or_none(obj.booking_status_chain_id))
        if not booking_status_chain:
            raise serializers.ValidationError("BookingStatusChain Does Not Exist")
        return booking_status_chain.get_booking_status()

    def get_manual_booking(self, obj):
        manual_booking = get_or_none(ManualBooking, id=int_or_none(obj.manual_booking_id))
        if not manual_booking:
            raise serializers.ValidationError("ManualBooking Does Not Exist")
        return manual_booking.booking_id

    def get_due_date_m(self, obj):
        return obj.due_date if obj.due_date else None


class TaskDashboardFunctionalitiesSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    functionality = serializers.ChoiceField(allow_null=True, choices=TD_FUNCTIONS, required=True,
                                            validators=[UniqueValidator(
                                                queryset=TaskDashboardFunctionalities.objects.all().exclude(
                                                    deleted=True))])
    consumer = serializers.ChoiceField(allow_null=True, choices=CONSUMER_PLATFORMS, required=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False, write_only=True)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, write_only=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    def create(self, validated_data):
        td_func = TaskDashboardFunctionalities.objects.create(functionality=validated_data['functionality'],
                                                              created_by=validated_data['created_by'])
        return td_func

    def update(self, instance, validated_data):
        instance.functionality = validated_data['functionality']
        instance.changed_by = validated_data['changed_by']
        instance.save()
        return instance


class EmployeeRolesFunctionalityMappingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    td_functionality_id = serializers.IntegerField(required=True)
    td_functionality = serializers.SerializerMethodField()
    employee_role_id = serializers.IntegerField(required=True)
    employee_role = serializers.SerializerMethodField()
    caption = serializers.CharField(max_length=35, trim_whitespace=True)
    current_functionality_count = serializers.SerializerMethodField()
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False, write_only=True)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, write_only=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    class Meta:
        validators = [
            UniqueTogetherValidator(queryset=EmployeeRolesFunctionalityMapping.objects.all().exclude(deleted=True),
                                    fields=('td_functionality_id', 'employee_role_id'))]

    def create(self, validated_data):
        try:
            td_functionality = TaskDashboardFunctionalities.objects.get(id=validated_data['td_functionality_id'])
        except TaskDashboardFunctionalities.DoesNotExist:
            raise serializers.ValidationError("Task Dashbaord Functionalities Does Not Exist")
        try:
            employee_role = EmployeeRoles.objects.get(id=validated_data['employee_role_id'])
        except EmployeeRoles.DoesNotExist:
            raise serializers.ValidationError("Employee Role Does Not Exist")
        employee_role_funationality_mapping = EmployeeRolesFunctionalityMapping.objects.create(
            td_functionality=td_functionality,
            employee_role=employee_role,
            caption=validated_data['caption'],
            created_by=validated_data['created_by'])
        return employee_role_funationality_mapping

    def update(self, instance, validated_data):
        try:
            td_functionality = TaskDashboardFunctionalities.objects.get(id=validated_data['td_functionality_id'])
        except TaskDashboardFunctionalities.DoesNotExist:
            raise serializers.ValidationError("Task Dashbaord Functionalities Does Not Exist")
        try:
            employee_role = EmployeeRoles.objects.get(id=validated_data['employee_role_id'])
        except EmployeeRoles.DoesNotExist:
            raise serializers.ValidationError("Employee Role Does Not Exist")
        instance.td_functionality = td_functionality
        instance.employee_role = employee_role
        instance.caption = validated_data['caption']
        instance.changed_by = validated_data['changed_by']
        instance.save()
        return instance

    def get_td_functionality(self, obj):
        td_func = get_or_none(TaskDashboardFunctionalities, id=int_or_none(obj.td_functionality_id))
        if not td_func:
            raise serializers.ValidationError("TaskDashboardFunctionalities Does Not Exist")
        return td_func.get_functionality()

    def get_employee_role(self, obj):
        emp_role = get_or_none(EmployeeRoles, id=int_or_none(obj.employee_role_id))
        if not emp_role:
            raise serializers.ValidationError("EmployeeRoles Does Not Exist")
        return emp_role.get_role()

    def get_current_functionality_count(self, obj):
        key = self.get_td_functionality(obj)['functionality'] + '_count'
        functionality_count_method = getattr(self, key, None)
        if callable(functionality_count_method):
            return functionality_count_method(obj)
        else:
            raise serializers.ValidationError(key + " is not method in EmployeeRolesFunctionalityMappingSerializer")

    def open_inquiries_count(self, obj):
        req_list_view = requirements.RequirementListView()
        setattr(req_list_view, 'request', self.context['request'])
        user = self.context['request'].user
        employee = Employee.objects.get(username=user)
        if not employee:
            raise serializers.ValidationError("Employee Does Not Exist")
        if self.get_employee_role(obj)['role'] == 'Technology' or self.get_employee_role(obj)['role'] == 'Management':
            aaho_office_id = None
        else:
            aaho_office_id = employee.office.id
        reqs = req_list_view.get_filtered_requirements(req_list_view.queryset, aaho_office_id, 'open')
        if reqs['status'] == 'success':
            return reqs['queryset'].count()
        else:
            return 0

    def delivered_count(self, obj):
        booking_dst_ids = manual_booking_id_dest_aaho_list(user=self.context['request'].user)
        try:
            employee = Employee.objects.get(username=self.context['request'].user)
        except Employee.DoesNotExist:
            employee = None
        try:
            if EmployeeRolesMapping.objects.filter(employee=employee).count() == 1:
                emp_role_mapping = EmployeeRolesMapping.objects.get(employee=employee, employee_role__role='sales')
            else:
                emp_role_mapping = None
        except EmployeeRolesMapping.DoesNotExist:
            emp_role_mapping = None
        if emp_role_mapping:
            pod_uploaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=[
                    'unloaded'], booking_stage='escalated').exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pod_verified_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=[
                    'pod_uploaded','pod_verified','inward_followup_completed', 'complete'], booking_stage='escalated').exclude(
                deleted=True). \
                values_list('manual_booking_id', flat=True)
            unloaded_bookings = [x for x in pod_uploaded_bookings if x not in pod_verified_bookings]
        else:
            pod_uploaded_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=[
                    'unloaded'], booking_stage__in=['in_progress', 'done']).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            pod_verified_bookings = BookingStatusesMapping.objects.filter(
                booking_status_chain__booking_status__status__in=[
                    'pod_uploaded', 'pod_verified', 'inward_followup_completed', 'complete']).exclude(deleted=True). \
                values_list('manual_booking_id', flat=True)
            unloaded_bookings = [x for x in pod_uploaded_bookings if x not in pod_verified_bookings]
        mbs = ManualBooking.objects.filter(id__in=booking_dst_ids).filter(id__in=unloaded_bookings).filter(
            Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=615)).date()) & (Q(
                booking_id__startswith='AH')) | Q(booking_id__startswith='AAHO')).exclude(
            Q(booking_status='cancelled') | Q(deleted=True) | Q(pod_status='not_required')).distinct()
        return mbs.count()

    def new_inquiry_count(self, obj):
        return 0

    def customer_inquiries_count(self, obj):
        req_list_view = requirements.RequirementListView()
        setattr(req_list_view, 'request', self.context['request'])
        user = self.context['request'].user
        employee = Employee.objects.get(username=user)
        if not employee:
            raise serializers.ValidationError("Employee Does Not Exist")
        if self.get_employee_role(obj)['role'] == 'Technology' or self.get_employee_role(obj)['role'] == 'Management':
            aaho_office_id = None
        else:
            aaho_office_id = employee.office.id
        reqs = req_list_view.get_filtered_requirements(req_list_view.queryset, aaho_office_id, 'unverified')
        if reqs['status'] == 'success':
            return reqs['queryset'].count()
        else:
            return 0

    def my_inquiries_count(self, obj):
        req_list_view = requirements.RequirementListView()
        setattr(req_list_view, 'request', self.context['request'])
        user = self.context['request'].user
        employee = Employee.objects.get(username=user)
        if not employee:
            raise serializers.ValidationError("Employee Does Not Exist")
        if self.get_employee_role(obj)['role'] == 'Technology' or self.get_employee_role(obj)['role'] == 'Management':
            return req_list_view.queryset.count()
        elif self.get_employee_role(obj)['role'] == 'City Head':
            reqs = req_list_view.get_filtered_requirements(req_list_view.queryset, employee.office.id, None)
        else:
            reqs = req_list_view.get_user_filtered_requirements()
        if reqs['status'] == 'success':
            return reqs['queryset'].count()
        else:
            return 0

    def pending_payments_count(self, obj):
        employee = get_or_none(Employee, username=self.context['request'].user)
        invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__in=['invoice_raised', 'party_invoice_sent',
                                                              'invoice_confirmed']).exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        complete_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='inward_followup_completed').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        pending_payments_bookings = [x for x in invoice_confirmed_bookings if x not in complete_bookings]
        emp_roles_response = get_employee_roles(self.context['request'].user)

        if emp_roles_response['status'] == 'success' and ('management' in emp_roles_response['roles']
                                                          or 'tech' in emp_roles_response['roles']):
            smes = Sme.objects.order_by('-id').exclude(deleted=True).exclude(name__profile=None)
        elif emp_roles_response['status'] == 'success' and ('city_head' in emp_roles_response['roles']):
            smes = Sme.objects.filter(aaho_office_id__in=employee.office_multiple.values_list('id')).exclude(
                deleted=True).exclude(name__profile=None).order_by('-id')
        else:
            smes = Sme.objects.filter(aaho_poc__username=self.context['request'].user).order_by('-id').exclude(
                deleted=True).exclude(name__profile=None)

        sme_ids = list(ManualBooking.objects.filter(id__in=pending_payments_bookings,
                                                    customer_to_be_billed_to__in=smes,
                                                    inward_payment_status__in=['no_payment','partial_received'],
                                                    invoice_status__in=['invoice_raised', 'invoice_sent',
                                                                        'invoice_confirmed']).
                       values_list('customer_to_be_billed_to_id',flat=True))
        return len(set(sme_ids))
        # invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
        #     booking_status_chain__booking_status__status__iexact='invoice_confirmed').exclude(deleted=True). \
        #     values_list('manual_booking_id', flat=True)
        # complete_bookings = BookingStatusesMapping.objects.filter(
        #     booking_status_chain__booking_status__status__iexact='inward_followup_completed').exclude(deleted=True). \
        #     values_list('manual_booking_id', flat=True)
        # pending_payments_bookings = [x for x in invoice_confirmed_bookings if x not in complete_bookings]
        #
        # ccp_about_to_over_bookings = []
        # for icb in pending_payments_bookings:
        #     try:
        #         ccp = int(ManualBooking.objects.get(id=icb).customer_to_be_billed_to.credit_period)
        #     except:
        #         ccp = 0
        #     try:
        #         ccp_about_to_over_objects = BookingStatusesMapping.objects.get(manual_booking_id=icb,
        #                                                                        booking_status_chain__booking_status__status__iexact='invoice_raised',
        #                                                                        created_on__lte=(
        #                                                                                datetime.now() - timedelta(
        #                                                                            days=ccp - 2)).date())
        #         ccp_about_to_over_bookings.append(ccp_about_to_over_objects.manual_booking.id)
        #     except BookingStatusesMapping.DoesNotExist:
        #         ccp_about_to_over_objects = None
        #
        # emp_roles_response = get_employee_roles(self.context['request'].user)
        # if emp_roles_response['status'] == 'success' and ('city_head' in emp_roles_response['roles']
        #                                                   or 'management' in emp_roles_response['roles']
        #                                                   or 'tech' in emp_roles_response['roles']):
        #     bookings = ManualBooking.objects.filter(id__in=ccp_about_to_over_bookings,
        #                                             invoice_status='invoice_confirmed').exclude(
        #         Q(booking_status='cancelled') | Q(deleted=True)).distinct()
        #
        # else:
        #     bookings = ManualBooking.objects.filter(id__in=ccp_about_to_over_bookings,
        #                                             invoice_status='invoice_confirmed',
        #                                             customer_to_be_billed_to__aaho_poc__username=self.context[
        #                                                 'request'].user).exclude(
        #         Q(booking_status='cancelled') | Q(deleted=True)).distinct()
        # inv = Invoice.objects.filter(bookings__in=bookings, payment_received=False,
        #                              date__gte=datetime.now().date() - timedelta(days=365))
        # return inv.count()

    def pending_lr_count(self, obj):
        booking_ids = manual_booking_id_list(user=self.context['request'].user)
        mbs = ManualBooking.objects.filter(id__in=booking_ids).filter(
            Q(lr_numbers=None) & Q(shipment_date__gte=(datetime.now() - timedelta(days=10)).date()) & Q(
                booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True))
        return mbs.count()

    def in_transit_count(self, obj):
        booking_ids = manual_booking_id_dest_aaho_list(user=self.context['request'].user)
        lr_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='lr_generated').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        unloaded_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__in=['unloaded', 'pod_uploaded'],
            booking_stage__in=['in_progress', 'done']).exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        in_transit_bookings = [x for x in lr_bookings if x not in unloaded_bookings]
        mbs = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=in_transit_bookings).filter(
            Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=115)).date()) & Q(
                booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True)).distinct()
        return mbs.count()

    def invoice_confirmation_count(self, obj):
        booking_ids = manual_booking_id_list(user=self.context['request'].user)
        invoice_sent_bookings = BookingStatusesMapping.objects. \
            filter(booking_status_chain__booking_status__status__iexact='party_invoice_sent'). \
            filter(booking_stage='escalated').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        emp_roles_response = get_employee_roles(self.context['request'].user)
        if emp_roles_response['status'] == 'success' and ('city_head' in emp_roles_response['roles']
                                                          or 'management' in emp_roles_response['roles']
                                                          or 'tech' in emp_roles_response['roles']):
            mbs = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_sent_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH') & Q(invoice_status='invoice_sent')).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
        else:
            mbs = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_sent_bookings).filter(
                Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
                Q(booking_id__startswith='AH') & Q(invoice_status='invoice_sent') &
                Q(customer_to_be_billed_to__aaho_poc__username=self.context['request'].user)).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).distinct()
        return mbs.count()

    def confirm_booking_count(self, obj):
        booking_ids = manual_booking_id_list(user=self.context['request'].user)
        party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='party_invoice_sent').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='invoice_confirmed').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        invoice_not_confirmed_bookings = [x for x in party_invoice_sent_bookings if x not in invoice_confirmed_bookings]
        bookings = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_not_confirmed_bookings). \
            filter(invoice_status='invoice_raised').exclude(billing_type='contract')
        return Invoice.objects.filter(bookings__in=bookings,
                                      date__gte=datetime.now().date() - timedelta(days=365)).distinct().count()

    def lr_generation_count(self, obj):
        booking_ids = manual_booking_id_list(user=self.context['request'].user)
        loaded_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='loaded'
        ).values_list('manual_booking_id', flat=True)
        mbs = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=loaded_bookings).filter(
            Q(lr_numbers=None) & Q(shipment_date__gte=(datetime.now() - timedelta(days=115)).date()) & Q(
                booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True))
        return mbs.count()

    def pay_advance_count(self, obj):
        booking_ids = manual_booking_id_list(user=self.context['request'].user)
        lr_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='lr_generated').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        advance_paid_delivered_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__in=['advance_paid', 'unloaded']).exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        advance_not_paid_bookings = [x for x in lr_bookings if x not in advance_paid_delivered_bookings]
        mbs = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=advance_not_paid_bookings).filter(
            Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=115)).date()) & Q(
                booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True)).distinct()
        return mbs.count()

    def pay_balance_count(self, obj):
        booking_ids = manual_booking_id_list(user=self.context['request'].user)
        pod_verified_bookings = BookingStatusesMapping.objects.filter(
            Q(booking_status_chain__booking_status__status__iexact='pod_verified') |
            (Q(manual_booking__pod_status='not_required') & Q(booking_status_chain__booking_status__status__iexact='unloaded'))).\
            exclude(deleted=True).values_list('manual_booking_id', flat=True)
        balance_paid_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__in=['balance_paid']).exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        balance_not_paid_bookings = [x for x in pod_verified_bookings if x not in balance_paid_bookings]
        return ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=balance_not_paid_bookings).filter(
            Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=115)).date()) & Q(
                booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True)).distinct().count()

    def send_invoice_count(self, obj):
        booking_ids = manual_booking_id_list(user=self.context['request'].user)
        invoice_raised_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='invoice_raised').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='party_invoice_sent').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        invoice_not_sent_bookings = [x for x in invoice_raised_bookings if x not in party_invoice_sent_bookings]
        bookings = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_not_sent_bookings). \
            filter(invoice_status='invoice_raised').exclude(billing_type='contract')
        return Invoice.objects.filter(bookings__in=bookings,
                                      date__gte=datetime.now().date() - timedelta(days=365)).distinct().count()

    def verify_pod_count(self, obj):
        return verify_pod_data_count()

    def raise_invoice_count(self, obj):
        try:
            bs = BookingStatuses.objects.get(status='pod_verified')
            tl = bs.time_limit
        except BookingStatuses.DoesNotExist:
            tl = 0
        booking_ids = manual_booking_id_list(user=self.context['request'].user)
        pod_verified_bookings = BookingStatusesMapping.objects.filter(
            Q(booking_status_chain__booking_status__status__iexact='pod_verified') |
            (Q(manual_booking__pod_status='not_required') & Q(booking_status_chain__booking_status__status__iexact='unloaded'))).\
            exclude(deleted=True).values_list('manual_booking_id', flat=True)
        invoice_raised_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='invoice_raised').exclude(Q(deleted=True)|Q(booking_stage='reverted')). \
            values_list('manual_booking_id', flat=True)
        invoice_not_raised_bookings = [x for x in pod_verified_bookings if x not in invoice_raised_bookings]
        b_ids = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_not_raised_bookings).filter(
            Q(lr_numbers__isnull=False) & Q(shipment_date__gte=(datetime.now() - timedelta(days=365)).date()) &
            Q(booking_id__startswith='AH')).exclude(Q(booking_status='cancelled') | Q(deleted=True)).distinct().\
            values_list('id', flat=True)
        return BookingStatusesMapping.objects.filter(manual_booking__id__in=b_ids,
                                                     booking_status_chain__booking_status__status__iexact='pod_verified',
                                                     created_on__lte=(datetime.now() - timedelta(minutes=tl)).date()).distinct().count()

    def confirm_invoice_count(self, obj):
        booking_ids = manual_booking_id_list(user=self.context['request'].user)
        party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='party_invoice_sent').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
            booking_status_chain__booking_status__status__iexact='invoice_confirmed').exclude(deleted=True). \
            values_list('manual_booking_id', flat=True)
        invoice_not_confirmed_bookings = [x for x in party_invoice_sent_bookings if x not in invoice_confirmed_bookings]
        bookings = ManualBooking.objects.filter(id__in=booking_ids).filter(id__in=invoice_not_confirmed_bookings). \
            filter(invoice_status='invoice_sent').exclude(billing_type='contract')
        return Invoice.objects.filter(bookings__in=bookings,
                                      date__gte=datetime.now().date() - timedelta(days=365)).distinct().count()

    def inward_entry_count(self, obj):
        return PendingInwardPaymentEntry.objects.filter(adjusted_flag=False).count()

    def process_payments_count(self, obj):
        op = OutWardPayment.objects.exclude(bank_account=None).exclude(
            Q(status__in=['paid', 'reconciled']) | Q(deleted=True))
        return op.count()

    def reconcile_count(self, obj):
        op = OutWardPayment.objects.filter(
            payment_date__gte='2018-10-29', status='paid',
            payment_mode__in=['neft', 'imps', 'hdfc_internal_account', 'cheque']).exclude(bank_account=None)
        return op.count()


class BookingStatusesMappingCommentsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    booking_status_mapping_id = serializers.IntegerField(required=True)
    booking_status_mapping = serializers.SerializerMethodField()
    comment = serializers.CharField(max_length=50, trim_whitespace=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False, write_only=True)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, write_only=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    def create(self, validated_data):
        try:
            booking_status_mapp = BookingStatusesMapping.objects.get(id=validated_data['booking_status_mapping_id'])
        except BookingStatusesMapping.DoesNotExist:
            raise serializers.ValidationError("BookingStatusesMapping Does Not Exist")

        booking_status_mapping_comment = BookingStatusesMappingComments.objects.create(
            booking_status_mapping=booking_status_mapp,
            comment=validated_data['comment'],
            created_by=validated_data['created_by'])
        return booking_status_mapping_comment

    def update(self, instance, validated_data):
        try:
            booking_status_mapping = BookingStatusesMapping.objects.get(id=validated_data['booking_status_mapping_id'])
        except BookingStatusesMapping.DoesNotExist:
            raise serializers.ValidationError("BookingStatusesMapping Does Not Exist")
        instance.booking_status_mapping = booking_status_mapping
        instance.comment = validated_data['comment']
        instance.changed_by = validated_data['changed_by']
        instance.save()
        return instance

    def get_booking_status_mapping(self, obj):
        booking_status_mapping = get_or_none(BookingStatusesMapping, id=int_or_none(obj.booking_status_mapping_id))
        if not booking_status_mapping:
            raise serializers.ValidationError("BookingStatusesMapping Does Not Exist")
        return booking_status_mapping.get_booking_status_mapping()


class BookingStatusesMappingLocationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    booking_status_mapping_id = serializers.IntegerField(required=True)
    booking_status_mapping = serializers.SerializerMethodField()
    latitude = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    longitude = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    city = serializers.CharField(max_length=100, trim_whitespace=False)
    district = serializers.CharField(max_length=100, trim_whitespace=False)
    state = serializers.CharField(max_length=100, trim_whitespace=False)
    country = serializers.CharField(max_length=50, trim_whitespace=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False, write_only=True)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, write_only=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    def create(self, validated_data):
        try:
            booking_status_mapp = BookingStatusesMapping.objects.get(id=validated_data['booking_status_mapping_id'])
        except BookingStatusesMapping.DoesNotExist:
            raise serializers.ValidationError("BookingStatusesMapping Does Not Exist")
        validated_data['booking_status_mapping'] = booking_status_mapp
        instance = BookingStatusesMappingLocation.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        try:
            booking_status_mapping = BookingStatusesMapping.objects.get(id=validated_data['booking_status_mapping_id'])
        except BookingStatusesMapping.DoesNotExist:
            raise serializers.ValidationError("BookingStatusesMapping Does Not Exist")
        validated_data.pop('booking_status_mapping_id')
        validated_data['booking_status_mapping'] = booking_status_mapping
        BookingStatusesMappingLocation.objects.filter(id=instance.id).update(**validated_data)
        return BookingStatusesMappingLocation.objects.get(id=instance.id)

    def get_booking_status_mapping(self, obj):
        booking_status_mapping = get_or_none(BookingStatusesMapping, id=int_or_none(obj.booking_status_mapping_id))
        if not booking_status_mapping:
            raise serializers.ValidationError("BookingStatusesMapping Does Not Exist")
        return booking_status_mapping.get_booking_status_mapping()


class SmePendingPaymentsCommentsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    sme_id = serializers.IntegerField(required=True)
    sme = serializers.SerializerMethodField()
    comment = serializers.CharField(max_length=150, trim_whitespace=False)
    due_date = serializers.DateField(allow_null=True, required=False)
    # due_date = serializers.SerializerMethodField()
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(required=False, write_only=True)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False, write_only=True)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), required=False, slug_field="username")

    def create(self, validated_data):
        try:
            sme = Sme.objects.get(id=validated_data['sme_id'])
        except Sme.DoesNotExist:
            raise serializers.ValidationError("Sme Does Not Exist")
        validated_data['sme'] = sme
        if 'due_date' not in validated_data:
            # latest_sme_comment = SmePaymentFollowupComments.objects.filter(sme=sme, due_date__isnull=False).exclude(deleted=True).last()
            # if latest_sme_comment:
            #     validated_data['due_date'] = latest_sme_comment.due_date
            # else:
            #     validated_data['due_date'] = None
            validated_data['due_date'] = None
        else:
            validated_data['due_date'] = datetime.strptime(str(validated_data['due_date']), '%Y-%m-%d').date()
        instance = SmePaymentFollowupComments.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        try:
            sme = Sme.objects.get(id=validated_data['sme_id'])
        except Sme.DoesNotExist:
            raise serializers.ValidationError("Sme Does Not Exist")
        validated_data.pop('sme_id')
        validated_data['sme'] = sme

        SmePaymentFollowupComments.objects.filter(id=instance.id).update(**validated_data)
        return SmePaymentFollowupComments.objects.get(id=instance.id)

    def get_sme(self, obj):
        sme = get_or_none(Sme, id=int_or_none(obj.sme_id))
        if not sme:
            raise serializers.ValidationError("Sme Does Not Exist")
        return sme.get_name()

    # def get_due_date(self, obj):
    #     return obj.due_date.date()
