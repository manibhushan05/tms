import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from owner.vehicle_util import display_format
from .models import Owner, Vehicle, Route, FuelCard, FuelCardTransaction, VehicleSummary


class FuelCardAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_id', 'card_number', 'issue_date', 'created_on']
    search_fields = ['id', 'customer_id', 'card_number']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')


class VehicleAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'owner', 'driver', 'vehicle_type']
    search_fields = ['vehicle_number', 'id', 'owner__name__profile__name', 'owner__name__profile__phone']

    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super().save_model(request, obj, form, change)


class OwnerAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner_name', 'owner_phone', 'pan', 'vehicles']
    search_fields = ['name__profile__name', 'name__profile__phone', 'name__profile__contact_person_name',
                     'name__profile__contact_person_phone', 'name__profile__alternate_phone','pan']
    readonly_fields = (
        'id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by', 'declaration_doc',
        'account_details', 'taxation_details', 'address')

    @staticmethod
    def owner_name(obj):
        return obj.get_name()

    @staticmethod
    def owner_phone(obj):
        return obj.get_phone()

    def vehicles(self, obj):
        return format_html(
            '<br>'.join([display_format(vehicle.vehicle_number) for vehicle in Vehicle.objects.filter(owner=obj)]))


class FuelCardTransactionAdmin(admin.ModelAdmin):
    list_display = ('id',)
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')


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


admin.site.register(Owner, OwnerAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Route)
admin.site.register(FuelCard, FuelCardAdmin)
admin.site.register(FuelCardTransaction, FuelCardTransactionAdmin)
admin.site.register(VehicleSummary, VehicleSummaryAdmin)
