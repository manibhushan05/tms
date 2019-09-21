import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from owner.vehicle_util import display_format
from . import models


class BrokerAdmin(admin.ModelAdmin):
    list_display = ['id', 'broker_name', 'code', 'broker_phone', 'route', 'vehicles', 'created_on']
    search_fields = ['id', 'name__username', 'code', 'name__profile__name', 'name__profile__phone', 'route',
                     'broker_vehicle__vehicle__vehicle_number']
    actions = ['delete_selected']
    autocomplete_fields = ['aaho_office', 'city']
    readonly_fields = (
        'id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by', 'address',
        'account_details',
        'taxation_details')

    # list_filter = ['active']

    @staticmethod
    def broker_name(obj):
        return obj.name.profile.name if obj.name.profile else ''

    @staticmethod
    def broker_phone(obj):
        return obj.name.profile.phone if obj.name.profile else ''

    def vehicles(self, broker):
        return format_html(
            "<br>".join([display_format(bv.vehicle.vehicle_number) for bv in broker.broker_vehicle.all()]))


class BrokerDriverAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')
    list_display = ['id', 'broker', 'driver']
    search_fields = (
        'id', 'driver__name', 'driver__phone', 'broker__name__profile__name', 'broker__name__profile__phone')


class BrokerVehicleAdmin(admin.ModelAdmin):
    list_display = ['id', 'broker', 'vehicle', 'datetime']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    search_fields = ['id', 'broker__name__profile__name', 'vehicle__vehicle_number', 'broker__name__profile__phone']


class BrokerSummaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'broker', 'accounting_summary_json']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_on', 'updated_on')
    search_fields = ('id', 'broker__name__profile__name')

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


admin.site.register(models.Broker, BrokerAdmin)
admin.site.register(models.BrokerVehicle, BrokerVehicleAdmin)
admin.site.register(models.BrokerOwner)
admin.site.register(models.BrokerDriver, BrokerDriverAdmin)
admin.site.register(models.BrokerAccount)
admin.site.register(models.Document)
admin.site.register(models.BrokerSummary, BrokerSummaryAdmin)
