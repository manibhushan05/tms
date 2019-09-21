from django_filters import rest_framework as filters

from restapi.models import EmployeeRoles, EmployeeRolesMapping, BookingStatuses, BookingStatusChain, \
    EmployeeRolesBookingStatusMapping, BookingStatusesMapping, TaskDashboardFunctionalities, \
    EmployeeRolesFunctionalityMapping, BookingStatusesMappingComments, BookingStatusesMappingLocation, \
    SmePaymentFollowupComments


class EmployeeRolesFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    role = filters.CharFilter(name="role", label="Employee Role", lookup_expr='icontains')
    role_null = filters.BooleanFilter(name="role", label="Is Employee Role Null", lookup_expr="isnull")
    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = EmployeeRoles
        fields = []


class EmployeeRolesMappingFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    employee = filters.CharFilter(name="employee__username__username", label="Employee name", lookup_expr='icontains')
    employee_id = filters.CharFilter(name="employee__id", label="Employee Id", lookup_expr='exact')
    employee_null = filters.BooleanFilter(name="employee", label="Is Employee Null", lookup_expr="isnull")
    employee_role = filters.CharFilter(name="employee_role__role", label="Employee Role name", lookup_expr='icontains')
    employee_role_null = filters.BooleanFilter(name="employee_role", label="Is Employee Role Null", lookup_expr="isnull")
    employee_status = filters.CharFilter(name="employee_status", label="Employee Status", lookup_expr='icontains')
    employee_status_null = filters.BooleanFilter(name="employee_status", label="Is Employee Status Null", lookup_expr="isnull")
    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = EmployeeRolesMapping
        fields = []


class BookingStatusesFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    status = filters.CharFilter(name="status", label="Booking Status", lookup_expr='icontains')
    status_null = filters.BooleanFilter(name="status", label="Is Booking Status Null", lookup_expr="isnull")
    time_limit = filters.NumberFilter(name="time_limit", label="Time Limit", lookup_expr="exact")
    time_limit_range = filters.RangeFilter(name="time_limit", label="Time Limit Between")
    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = BookingStatuses
        fields = []


class BookingStatusChainFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    booking_status = filters.CharFilter(name="booking_status__status", label="Booking Status Name", lookup_expr='icontains')
    booking_status_null = filters.BooleanFilter(name="booking_status", label="Is Booking Status Null", lookup_expr="isnull")
    level = filters.CharFilter(name="level", label="Booking Status Chain Level", lookup_expr='icontains')
    level_null = filters.BooleanFilter(name="level", label="Is Booking Status Chain Level Null", lookup_expr="isnull")
    primary_preceded_booking_status = filters.CharFilter(name="primary_preceded_booking_status__status",
                                                         label="Booking Status Name", lookup_expr='icontains')
    primary_preceded_booking_status_null = filters.BooleanFilter(name="primary_preceded_booking_status",
                                                                 label="Is Booking Status Null", lookup_expr="isnull")
    primary_succeeded_booking_status = filters.CharFilter(name="primary_succeeded_booking_status__status",
                                                          label="Booking Status Name", lookup_expr='icontains')
    primary_succeeded_booking_status_null = filters.BooleanFilter(name="primary_succeeded_booking_status",
                                                                  label="Is Booking Status Null", lookup_expr="isnull")
    secondary_preceded_booking_status = filters.CharFilter(name="secondary_preceded_booking_status__status",
                                                           label="Booking Status Name", lookup_expr='icontains')
    secondary_preceded_booking_status_null = filters.BooleanFilter(name="secondary_preceded_booking_status",
                                                                   label="Is Booking Status Null", lookup_expr="isnull")
    secondary_succeeded_booking_status = filters.CharFilter(name="secondary_succeeded_booking_status__status",
                                                            label="Booking Status Name", lookup_expr='icontains')
    secondary_succeeded_booking_status_null = filters.BooleanFilter(name="secondary_succeeded_booking_status",
                                                                    label="Is Booking Status Null", lookup_expr="isnull")
    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = BookingStatusChain
        fields = []


class EmployeeRolesBookingStatusMappingFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    booking_status_chain = filters.CharFilter(name="booking_status_chain__booking_status__status",
                                              label="Booking Status Name", lookup_expr='icontains')
    booking_status_chain_null = filters.BooleanFilter(name="booking_status_chain", label="Is Booking Status Null",
                                                      lookup_expr="isnull")
    employee_name = filters.CharFilter(name="employee_roles_mapping__employee__username__username",
                                       label="Employee Name",lookup_expr='icontains')
    employee_name_null = filters.BooleanFilter(name="employee_roles_mapping", label="Is Employee Name Null",
                                               lookup_expr="isnull")
    employee_role = filters.CharFilter(name="employee_roles_mapping__employee_role__role",
                                       label="Employee Role",lookup_expr='icontains')
    employee_role_null = filters.BooleanFilter(name="employee_roles_mapping", label="Is Employee Name Null",
                                               lookup_expr="isnull")
    assignment_status = filters.CharFilter(name="assignment_status", label="Assignment Status Chain Level", lookup_expr='icontains')
    assignment_status_null = filters.BooleanFilter(name="assignment_status", label="Is Assignment Status Chain Level Null",
                                                   lookup_expr="isnull")
    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = EmployeeRolesBookingStatusMapping
        fields = []


class BookingStatusesMappingFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    booking_status_chain = filters.CharFilter(name="booking_status_chain__booking_status__status",
                                              label="Booking Status Name", lookup_expr='icontains')
    booking_status_chain_null = filters.BooleanFilter(name="booking_status_chain", label="Is Booking Status Null",
                                                      lookup_expr="isnull")
    manual_booking = filters.CharFilter(name="manual_booking__booking_id",label="Manual Booking ID", lookup_expr='icontains')
    manual_booking_null = filters.BooleanFilter(name="manual_booking", label="Is Manual Booking Null",lookup_expr="isnull")
    booking_stage = filters.CharFilter(name="booking_stage", label="Booking Stage",lookup_expr='icontains')
    booking_stage_null = filters.BooleanFilter(name="booking_stage",
                                               label="Is Booking Stage Null",
                                               lookup_expr="isnull")
    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = BookingStatusesMapping
        fields = []


class TaskDashboardFunctionalitiesFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    functionality = filters.CharFilter(name="functionality", label="Functionality",lookup_expr='icontains')
    functionality_null = filters.BooleanFilter(name="functionality",
                                               label="Is Functionality Null",
                                               lookup_expr="isnull")
    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = TaskDashboardFunctionalities
        fields = []


class EmployeeRolesFunctionalityMappingFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")
    td_functionality = filters.CharFilter(name="td_functionality__functionality",
                                              label="Task Dashboard Functionality", lookup_expr='icontains')
    td_functionality_null = filters.BooleanFilter(name="td_functionality", label="Is Task Dashboard Functionality Null",
                                                      lookup_expr="isnull")
    employee_role = filters.CharFilter(name="employee_role__role",
                                              label="Employee Role", lookup_expr='icontains')
    employee_role_id = filters.CharFilter(name="employee_role__id",
                                              label="Employee Role Id", lookup_expr='exact')
    employee_role_null = filters.BooleanFilter(name="employee_role", label="Is Employee Role Null",
                                                      lookup_expr="isnull")
    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = EmployeeRolesFunctionalityMapping
        fields = []


class BookingStatusesMappingCommentsFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    booking_status_mapping = filters.CharFilter(
        name="booking_status_mapping__booking_status_chain__booking_status__status",
        label="Booking Status Name", lookup_expr='icontains')
    booking_status_mapping_null = filters.BooleanFilter(name="booking_status_mapping",
                                                        label="Is Booking Status Mapping Null", lookup_expr="isnull")
    comment = filters.CharFilter(name="comment", label="Comment",lookup_expr='icontains')
    comment_null = filters.BooleanFilter(name="comment",
                                               label="Is Comment Null",
                                               lookup_expr="isnull")
    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = BookingStatusesMappingComments
        fields = []


class BookingStatusesMappingLocationFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    booking_status_mapping = filters.CharFilter(
        name="booking_status_mapping__booking_status_chain__booking_status__status",
        label="Booking Status Name", lookup_expr='icontains')
    booking_status_mapping_null = filters.BooleanFilter(name="booking_status_mapping",
                                                        label="Is Booking Status Mapping Null", lookup_expr="isnull")
    latitude = filters.NumberFilter(name="latitude", label="latitude",lookup_expr='icontains')
    longitude = filters.NumberFilter(name="longitude", label="longitude",lookup_expr='icontains')

    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = BookingStatusesMappingLocation
        fields = []


class SmePendingPaymentsCommentsFilter(filters.FilterSet):
    id = filters.NumberFilter(name="id", label="ID", lookup_expr="exact")
    id_range = filters.RangeFilter(name="id", label="ID Between")

    sme = filters.CharFilter(name="sme__name__profile__name", label="Sme Name", lookup_expr='icontains')
    sme_null = filters.BooleanFilter(name="sme", label="Is Sme Null", lookup_expr="isnull")

    comment = filters.CharFilter(name="comment", label="Comment", lookup_expr='icontains')
    comment_null = filters.BooleanFilter(name="comment",
                                         label="Is Comment Null",
                                         lookup_expr="isnull")

    due_date = filters.DateTimeFilter(name="due_date", label="Due Date", lookup_expr="date")
    due_date_between = filters.DateTimeFromToRangeFilter(name="due_date", label="Due Date Between")

    created_on = filters.DateTimeFilter(name="created_on", label="Created on", lookup_expr="date")
    created_between = filters.DateTimeFromToRangeFilter(name="created_on", label="Created Between")

    class Meta:
        model = SmePaymentFollowupComments
        fields = []