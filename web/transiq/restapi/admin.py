from django.contrib import admin
from fms.models import MobileAppVersions
from restapi.models import UserCategory, EmployeeRoles, EmployeeRolesMapping, TaskDashboardFunctionalities, \
    EmployeeRolesFunctionalityMapping, BookingStatuses, BookingStatusChain, BookingStatusesMapping, \
    BookingStatusesMappingComments, BookingStatusesMappingLocation


class MobileAppVersionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'app_platform', 'app_name', 'app_version', 'comment', 'upgrade_type']
    search_fields = ['id', 'app_platform', 'app_name', 'app_version', 'comment', 'upgrade_type']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def has_delete_permission(self, request, obj=None):
        return False


class UserCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category')
    search_fields = ('id','category')


class EmployeeRolesAdmin(admin.ModelAdmin):
    list_display = ['id', 'role']
    search_fields = ['id', 'role']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def has_delete_permission(self, request, obj=None):
        return False


class EmployeeRolesMappingAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'employee_role', 'employee_status']
    search_fields = ['id', 'employee__username__profile__name', 'employee_role__role', 'employee_status']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')
    list_filter = ('employee_status','employee_role')

    def has_delete_permission(self, request, obj=None):
        return False


class TaskDashboardFunctionalitiesAdmin(admin.ModelAdmin):
    list_display = ['id', 'functionality', 'consumer']
    search_fields = ['id', 'functionality', 'consumer']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def has_delete_permission(self, request, obj=None):
        return False


class EmployeeRolesFunctionalityMappingAdmin(admin.ModelAdmin):
    list_display = ['id', 'td_functionality', 'employee_role', 'caption', 'access']
    search_fields = ['id', 'td_functionality__functionality', 'employee_role__role', 'caption', 'access']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def has_delete_permission(self, request, obj=None):
        return False


class BookingStatusesAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'time_limit']
    search_fields = ['id', 'status', 'time_limit']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def has_delete_permission(self, request, obj=None):
        return False


class BookingStatusChainAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking_status', 'level', 'primary_preceded_booking_status',
                    'primary_succeeded_booking_status', 'secondary_preceded_booking_status',
                    'secondary_succeeded_booking_status']
    search_fields = ['id', 'booking_status', 'level', 'primary_preceded_booking_status',
                     'primary_succeeded_booking_status', 'secondary_preceded_booking_status',
                     'secondary_succeeded_booking_status']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def has_delete_permission(self, request, obj=None):
        return False


class BookingStatusesMappingAdmin(admin.ModelAdmin):
    list_display = ['id', 'manual_booking', 'booking_status_chain', 'booking_stage', 'due_date']
    search_fields = ['id', 'manual_booking__booking_id', 'manual_booking__id',
                     'booking_status_chain__booking_status__status', 'booking_stage', 'due_date']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')
    list_filter = ['booking_status_chain','booking_stage']
    autocomplete_fields = ['manual_booking']

    def has_delete_permission(self, request, obj=None):
        return False


class BookingStatusesMappingCommentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking_status_mapping', 'comment', 'created_on']
    search_fields = ['id', 'booking_status_mapping__id', 'booking_status_mapping__manual_booking__booking_id',
                     'booking_status_mapping__manual_booking__id','comment']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def has_delete_permission(self, request, obj=None):
        return False


class BookingStatusesMappingLocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking_status_mapping', 'city', 'district', 'state', 'latitude', 'longitude']
    search_fields = ['id', 'booking_status_mapping__id', 'booking_status_mapping__manual_booking__booking_id',
                     'booking_status_mapping__manual_booking__id',
                     'city', 'district', 'state', 'latitude', 'longitude']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(MobileAppVersions, MobileAppVersionsAdmin)
admin.site.register(UserCategory, UserCategoryAdmin)
admin.site.register(EmployeeRoles, EmployeeRolesAdmin)
admin.site.register(EmployeeRolesMapping, EmployeeRolesMappingAdmin)
admin.site.register(TaskDashboardFunctionalities, TaskDashboardFunctionalitiesAdmin)
admin.site.register(EmployeeRolesFunctionalityMapping, EmployeeRolesFunctionalityMappingAdmin)
admin.site.register(BookingStatuses, BookingStatusesAdmin)
admin.site.register(BookingStatusChain, BookingStatusChainAdmin)
admin.site.register(BookingStatusesMapping, BookingStatusesMappingAdmin)
admin.site.register(BookingStatusesMappingComments, BookingStatusesMappingCommentsAdmin)
admin.site.register(BookingStatusesMappingLocation, BookingStatusesMappingLocationAdmin)
