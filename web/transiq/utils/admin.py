from __future__ import absolute_import
from django.contrib import admin
from django.utils.html import format_html

from . import models


class BankAdmin(admin.ModelAdmin):
    list_display = ['id', 'account_holder_name', 'beneficiary_code', 'bank', 'transaction_type', 'account_number',
                    'ifsc',
                    'account_type', 'created_on']
    search_fields = ['id', 'account_holder_name', 'beneficiary_code', 'bank', 'account_number', 'transaction_type',
                     'ifsc', 'account_type']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')
    autocomplete_fields = ['user']

class AddressAdmin(admin.ModelAdmin):
    list_display = ['line1', 'line2', 'line3', 'landmark', 'city']
    search_fields = ['line1', 'line2', 'line3', 'landmark', 'city__name']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')


class IfscDetailAdmin(admin.ModelAdmin):
    list_display = ['bank', 'ifsc_code', 'micr_code', 'branch_name', 'address', 'centre', 'district', 'state']
    search_fields = ['bank__name', 'ifsc_code', 'micr_code', 'branch_name', 'address', 'centre', 'district', 'state']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')


class BankHolidaysAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'holidays_in_states', 'remarks']
    search_fields = ['name', 'date', 'remarks']

    @staticmethod
    def holidays_in_states(obj):
        return format_html('<br>'.join([state.name for state in obj.states.all()]))


class AahoOfficeAdmin(admin.ModelAdmin):
    list_display = ['id', 'branch_name', 'branch_head', 'address', 'pin', 'email', 'phone']
    search_fields = ['id', 'branch_name', 'branch_head']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def has_delete_permission(self, request, obj=None):
        return False


class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','code', 'created_on')
    search_fields = ('id', 'name')
    list_filter = ('created_on',)
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')


class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'state', 'latitude', 'longitude', 'created_on']
    search_fields = ['id', 'name', 'code', 'state__name']
    list_filter = ('created_on',)
    actions = ['delete_selected']


class DistrictAdmin(admin.ModelAdmin):
    list_filter = ['created_by']
    list_display = ('id', 'name', 'get_state')
    actions = ['delete_selected']
    search_fields = ('id', 'name', 'latitude', 'longitude', 'state__name')
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def get_state(self, instance):
        if isinstance(instance.state, models.State):
            return instance.state.name
        else:
            return '-'

    get_state.short_description = 'State'


class SubDistrictAdmin(admin.ModelAdmin):
    list_filter = ['created_by', 'created_on', 'updated_on']
    list_display = ['id', 'name', 'district', 'latitude', 'longitude', 'created_by', 'created_on']
    search_fields = ('id', 'name', 'district__name', 'district__state__name', 'latitude', 'longitude',)
    actions = ['delete_selected']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


class PinCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'pin_code', 'get_sub_district', 'get_district', 'get_state', 'latitude', 'longitude']
    search_fields = ['id', 'pin_code', 'sub_district__name', 'sub_district__district__name',
                     'sub_district__district__state__name']
    actions = ['delete_selected']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def get_sub_district(self, instance):
        if isinstance(instance.sub_district, models.SubDistrict):
            return instance.sub_district.name
        return '-'

    get_sub_district.short_description = 'Sub District'

    def get_district(self, instance):
        if isinstance(instance.sub_district, models.SubDistrict) and isinstance(instance.sub_district.district,
                                                                                models.District):
            return instance.sub_district.district.name
        return '-'

    get_district.short_description = 'District'

    def get_state(self, instance):
        if isinstance(
                instance.sub_district, models.SubDistrict) and isinstance(
            instance.sub_district.district, models.District
        ) and isinstance(instance.sub_district.district.state, models.State):
            return instance.sub_district.district.state.name
        return '-'

    get_state.short_description = 'State'


class LocalityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'post_office', 'get_pin_code', 'get_sub_district', 'get_district', 'get_state',
                    'latitude', 'longitude']
    search_fields = ('id', 'name', 'post_office', 'pin_code__pin_code', 'pin_code__sub_district__name',
                     'pin_code__sub_district__district__name',
                     'pin_code__sub_district__district__state__name')
    actions = ['delete_selected']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def get_pin_code(self, instance):
        if isinstance(instance.pin_code, models.PinCode):
            return instance.pin_code.pin_code
        return '-'

    get_pin_code.short_description = 'PIN Code'

    def get_sub_district(self, instance):
        if isinstance(instance.pin_code, models.PinCode) and isinstance(instance.pin_code.sub_district,
                                                                        models.SubDistrict):
            return instance.pin_code.sub_district.name
        return '-'

    get_sub_district.short_description = 'Sub District'

    def get_district(self, instance):
        if isinstance(instance.pin_code, models.PinCode) and isinstance(
                instance.pin_code.sub_district, models.SubDistrict
        ) and isinstance(instance.pin_code.sub_district.district, models.District):
            return instance.pin_code.sub_district.district.name
        return '-'

    get_district.short_description = 'District'

    def get_state(self, instance):
        if isinstance(instance.pin_code, models.PinCode) and isinstance(
                instance.pin_code.sub_district, models.SubDistrict) and isinstance(
            instance.pin_code.sub_district.district, models.District
        ) and isinstance(instance.pin_code.sub_district.district.state, models.State):
            return instance.pin_code.sub_district.district.state.name
        return '-'

    get_state.short_description = 'State'


class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle_type', 'capacity', 'truck_body', 'truck_body_type']
    search_fields = ['id', 'vehicle_type', 'capacity', 'truck_body__name']
    list_filter = ['truck_body', 'capacity']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')


class VehicleBodyCategoryAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'created_on']
    search_fields = ('name',)
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')


class CityLocalAdmin(admin.ModelAdmin):
    list_display = ['id','city', 'hindi_name']
    search_fields = ('city__name','hindi_name')
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')


class AahoHolidaysAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'holidays_in_offices', 'status']
    search_fields = ['name', 'date', 'status']

    @staticmethod
    def holidays_in_offices(obj):
        return format_html('<br>'.join([office.branch_name for office in obj.offices.all()]))


admin.site.register(models.State, StateAdmin)
admin.site.register(models.City, CityAdmin)
admin.site.register(models.District, DistrictAdmin)
admin.site.register(models.SubDistrict, SubDistrictAdmin)
admin.site.register(models.PinCode, PinCodeAdmin)
admin.site.register(models.Locality, LocalityAdmin)
admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.IDDetails)
admin.site.register(models.Bank, BankAdmin)
admin.site.register(models.TaxationID)
admin.site.register(models.VehicleCategory, VehicleCategoryAdmin)
admin.site.register(models.VehicleBodyCategory, VehicleBodyCategoryAdmin)
admin.site.register(models.AahoOffice, AahoOfficeAdmin)
admin.site.register(models.IfscDetail, IfscDetailAdmin)
admin.site.register(models.BankName)
admin.site.register(models.DatabaseUpdateLog)
admin.site.register(models.FieldChangeLog)
admin.site.register(models.BankHolidays, BankHolidaysAdmin)
admin.site.register(models.CityLocal, CityLocalAdmin)
admin.site.register(models.AahoHolidays, AahoHolidaysAdmin)