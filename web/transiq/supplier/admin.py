import json

from datetime import datetime

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from owner.vehicle_util import display_format
from supplier.models import SupplierVehicle, Supplier, Vehicle, VehicleFitness, Driver, Service, DriverPhone, \
    DriverVehicle, VehicleStatus, VehicleInsurance, VehiclePUC, VehiclePermit, ContactPerson, VehicleInsurer, \
    SupplierAccountingSummary, VehicleAccountingSummary


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'deleted']
    search_fields = ['id', 'name']
    list_filter = ['deleted']
    empty_value_display = 'unknown'

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.deleted_on = datetime.now()
        obj.changed_by = request.user
        super().delete_model(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False
        return True


class SupplierAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'pan', 'code', 'vehicles', 'deleted']
    search_fields = ['id', 'user__profile__name', 'user__profile__phone', 'pan']
    list_filter = ['deleted', 'aaho_office']
    list_display_links = ('id', 'name')
    empty_value_display = 'unknown'
    autocomplete_fields = ('city', 'serving_states', 'aaho_poc', 'aaho_office')

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.deleted_on = datetime.now()
        obj.changed_by = request.user
        super(SupplierAdmin, self).delete_model(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False
        return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(SupplierAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['changed_by', 'created_by', 'created_on', 'updated_on']

    @staticmethod
    def vehicles(obj):
        return format_html('<br>'.join(
            ['{} ({})'.format(display_format(sv.vehicle.vehicle_number), sv.get_ownership_display()) for sv in
             obj.suppliervehicle_set.all()]))


class VehicleAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'vehicle_category', 'owner_name', 'owner_phone', 'driver_name', 'driver_phone',
                    'deleted']
    search_fields = ['id', 'vehicle_number', 'vehicle_type__vehicle_type']
    list_filter = ['deleted', 'vehicle_type']
    empty_value_display = 'unknown'

    # def delete_model(self, request, obj):
    #     obj.deleted = True
    #     obj.deleted_on = datetime.now()
    #     obj.changed_by = request.user
    #     super(VehicleAdmin, self).delete_model(request, obj)
    #
    # def has_delete_permission(self, request, obj=None):
    #     if obj and obj.deleted:
    #         return False
    #     return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(VehicleAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']

    def vehicle(self, obj):
        return obj.number()

    vehicle.short_description = 'Vehicle Number'

    def driver_phone(self, obj):
        return format_html('<br>'.join(obj.driver_phone.split('\n')))

    driver_phone.short_description = 'Driver Phone'


class DriverAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'driver_phone', 'dl_number', 'dl_validity', 'deleted']
    search_fields = ['id', 'user__profile__name', 'user__profile__phone']
    list_filter = ['deleted']
    empty_value_display = 'unknown'

    def driver_phone(self, obj):
        return format_html('<br>'.join(obj.phone.split('\n')))

    driver_phone.short_description = 'Driver Phone'

    def dl_number(self, obj):
        return obj.driving_licence_number

    dl_number.short_description = 'DL Number'

    def dl_validity(self, obj):
        return obj.driving_licence_validity

    dl_validity.short_description = 'DL Validity'

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(DriverAdmin, self).save_model(request, obj, form, change)

    # def delete_model(self, request, obj):
    #     obj.deleted = True
    #     obj.deleted_on = datetime.now()
    #     obj.changed_by = request.user
    #     obj.driverphone_set.update(deleted=True, deleted_on=datetime.now(), active=False)
    #     super(DriverAdmin, self).delete_model(request, obj)
    #
    # def has_delete_permission(self, request, obj=None):
    #     if obj and obj.deleted:
    #         return False
    #     return True

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']


class SupplierVehicleAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'supplier_name', 'supplier_phone', 'ownership', 'active', 'deleted']
    search_fields = ['id', 'vehicle__vehicle_number', 'supplier__user__profile__name', 'supplier__user__username',
                     'supplier__user__profile__phone']
    list_filter = ['deleted']
    autocomplete_fields = ('supplier', 'vehicle')

    @staticmethod
    def supplier_name(obj):
        return obj.supplier.name

    @staticmethod
    def supplier_phone(obj):
        return obj.supplier.phone

    # def delete_model(self, request, obj):
    #     obj.deleted = True
    #     obj.deleted_on = datetime.now()
    #     obj.changed_by = request.user
    #     super(SupplierVehicleAdmin, self).delete_model(request, obj)
    #
    # def has_delete_permission(self, request, obj=None):
    #     if obj and obj.deleted:
    #         return False
    #     return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(SupplierVehicleAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']


class DriverVehicleAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'driver_name', 'driver_phone', 'deleted']
    search_fields = ['id', 'vehicle__vehicle_number', 'driver__user__profile__name', 'driver__user__profile__phone']
    list_filter = ['deleted']
    autocomplete_fields = ('driver', 'vehicle')

    def driver_phone(self, obj):
        return format_html('<br>'.join(obj.driver.phone.split('\n')))

    driver_phone.short_description = 'Driver Phone'

    @staticmethod
    def driver_name(obj):
        return obj.driver.name

    # def delete_model(self, request, obj):
    #     obj.deleted = True
    #     obj.deleted_on = datetime.now()
    #     obj.changed_by = request.user
    #     super(DriverVehicleAdmin, self).delete_model(request, obj)
    #
    # def has_delete_permission(self, request, obj=None):
    #     if obj and obj.deleted:
    #         return False
    #     return True

    def has_add_permission(self, request):
        return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(DriverVehicleAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']


class DriverPhoneAdmin(admin.ModelAdmin):
    list_display = ['id', 'driver_name', 'phone', 'active', 'deleted']
    search_fields = ['id', 'driver__user__profile__name', 'driver__user__profile__phone', 'phone']
    list_filter = ['active', 'deleted']

    @staticmethod
    def driver_name(obj):
        if obj.driver:
            return obj.driver.name
        return '-'

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.deleted_on = datetime.now()
        obj.changed_by = request.user
        super(DriverPhoneAdmin, self).delete_model(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False
        return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(DriverPhoneAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']


class VehicleFitnessAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'serial_number', 'issued_date', 'expiry_date', 'deleted']
    search_fields = ['id', 'vehicle__vehicle_number', 'serial_number']
    list_filter = ['deleted']
    autocomplete_fields = ('vehicle',)

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.deleted_on = datetime.now()
        obj.changed_by = request.user
        super(VehicleFitnessAdmin, self).delete_model(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False
        return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(VehicleFitnessAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']


class VehicleStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'status', 'active', 'deleted']
    search_fields = ['id', 'vehicle__vehicle_number']
    list_filter = ['active', 'status', 'deleted']

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.deleted_on = datetime.now()
        obj.changed_by = request.user
        super(VehicleStatusAdmin, self).delete_model(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False
        return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(VehicleStatusAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']


class VehicleInsurerAdmin(admin.ModelAdmin):
    list_filter = ['name', 'deleted']
    list_display = ['id', 'name', 'deleted']
    search_fields = ['id', 'name']

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.deleted_on = datetime.now()
        obj.changed_by = request.user
        super(VehicleInsurerAdmin, self).delete_model(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False
        return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(VehicleInsurerAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']


class VehicleInsuranceAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'insurer', 'insurance_number', 'issued_on', 'expired_by', 'deleted']
    search_fields = ['id', 'vehicle__vehicle_number']
    list_filter = ['deleted']
    autocomplete_fields = ('vehicle', 'insurer')

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.deleted_on = datetime.now()
        obj.changed_by = request.user
        super(VehicleInsuranceAdmin, self).delete_model(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False
        return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(VehicleInsuranceAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']


class VehiclePUCAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'serial_number', 'issued_date', 'expiry_date', 'deleted']
    search_fields = ['id', 'vehicle__vehicle_number', 'serial_number']
    list_filter = ['deleted']
    autocomplete_fields = ('vehicle',)

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.deleted_on = datetime.now()
        obj.changed_by = request.user
        super(VehiclePUCAdmin, self).delete_model(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False
        return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(VehiclePUCAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']


class VehiclePermitAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'permit_number', 'issued_date', 'expiry_date', 'deleted']
    search_fields = ['id', 'vehicle__vehicle_number', 'permit_number']
    list_filter = ['deleted']
    autocomplete_fields = ('vehicle',)

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.deleted_on = datetime.now()
        obj.changed_by = request.user
        super(VehiclePermitAdmin, self).delete_model(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False
        return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(VehiclePermitAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']


class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'email', 'supplier_name', 'supplier_phone', 'deleted']
    search_fields = ['id', 'supplier__user__profile__name', 'supplier__user__profile__phone', 'user__profile__name',
                     'user__profile__phone']
    list_filter = ['deleted']
    autocomplete_fields = ('supplier',)

    @staticmethod
    def supplier_name(obj):
        return obj.supplier.name

    @staticmethod
    def supplier_phone(obj):
        return obj.supplier.phone

    # def delete_model(self, request, obj):
    #     obj.deleted = True
    #     obj.deleted_on = datetime.now()
    #     obj.changed_by = request.user
    #     super(ContactPersonAdmin, self).delete_model(request, obj)

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(ContactPersonAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_by', 'created_on', 'updated_on', 'deleted']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False
        return True


class SupplierAccountingSummaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'accounting_summary_json']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_on', 'updated_on')
    search_fields = ('id', 'supplier__user__profile__name')

    def accounting_summary_json(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.accounting_summary, sort_keys=True, indent=2)

        # Truncate the data. Alter as needed
        response = response

        # Get the Pygments formatter
        formatter = HtmlFormatter(style='colorful')

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    accounting_summary_json.short_description = 'data prettified'


class VehicleSummaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'accounting_summary_json']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_on', 'updated_on')
    search_fields = ('id', 'vehicle__vehicle_number')

    def accounting_summary_json(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.accounting_summary, sort_keys=True, indent=2)

        # Truncate the data. Alter as needed
        response = response

        # Get the Pygments formatter
        formatter = HtmlFormatter(style='colorful')

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    accounting_summary_json.short_description = 'data prettified'


admin.site.register(Service, ServiceAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(VehicleFitness, VehicleFitnessAdmin)
admin.site.register(VehicleStatus, VehicleStatusAdmin)
admin.site.register(VehicleInsurer, VehicleInsurerAdmin)
admin.site.register(VehicleInsurance, VehicleInsuranceAdmin)
admin.site.register(VehiclePUC, VehiclePUCAdmin)
admin.site.register(VehiclePermit, VehiclePermitAdmin)
admin.site.register(ContactPerson, ContactPersonAdmin)

admin.site.register(SupplierVehicle, SupplierVehicleAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(DriverPhone, DriverPhoneAdmin)
admin.site.register(DriverVehicle, DriverVehicleAdmin)
admin.site.register(SupplierAccountingSummary, SupplierAccountingSummaryAdmin)
admin.site.register(VehicleAccountingSummary, VehicleSummaryAdmin)
