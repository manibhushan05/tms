from django.contrib import admin
from django.utils.html import format_html

from . import models


class DeleteNotAllowedTaskAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'emp_name', 'emp_phone', 'emp_alt_phone', 'office_name', 'status', 'created_on']
    search_fields = ['id', 'username__profile__name', 'username__profile__phone', 'username__profile__alternate_phone']
    list_filter = ['status', 'office_multiple']
    autocomplete_fields = ['created_by', 'office']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    @staticmethod
    def emp_name(obj):
        return obj.emp_name()

    @staticmethod
    def emp_phone(obj):
        return obj.emp_phone()

    @staticmethod
    def emp_alt_phone(obj):
        return obj.emp_alt_phone()

    @staticmethod
    def office_name(obj):
        return ', '.join(obj.office_multiple.values_list('branch__name', flat=True))

    def has_delete_permission(self, request, obj=None):
        return False


class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on']
    search_fields = ['id', 'name']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def has_delete_permission(self, request, obj=None):
        return False


class TaskEmailAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'office', 'employees']
    search_fields = ['id', 'task__name', 'employee__username__profile__name']
    autocomplete_fields = ['task', 'office']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def has_delete_permission(self, request, obj=None):
        return False

    @staticmethod
    def employees(obj):
        return format_html('<br>'.join([emp.emp_name() for emp in obj.employee.all()]))


admin.site.register(models.Employee, EmployeeAdmin)
admin.site.register(models.EducationalDegree)
admin.site.register(models.CertificationCourse)
admin.site.register(models.SkillSet)
admin.site.register(models.PastEmployment)
admin.site.register(models.CurrentEmploymentDetails)
admin.site.register(models.Referral)
admin.site.register(models.PermanentAddress)
admin.site.register(models.EmploymentAgency)
admin.site.register(models.Nominee)
admin.site.register(models.LeaveRecord)
admin.site.register(models.Salary)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.TaskEmail, TaskEmailAdmin)
admin.site.register(models.Department)
admin.site.register(models.Designation)
admin.site.register(models.FitnessDetail)
