import json

from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from sme.models import Sme, SmeEnquiry, ContactDetails, Location, ConsignorConsignee, PreferredVehicle, SmeTaskEmail, \
    CustomerContract, ContractRoute, RateType, SmeSummary


class SmeAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'company_code', 'customer_address', 'city', 'pin', 'gstin']
    search_fields = ['id', 'name__profile__name', 'company_code', 'gstin']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    @staticmethod
    def customer_name(obj):
        return obj.get_name()


class ConsignorConsigneeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'address', 'city', 'pin']
    search_fields = ['name', 'type', 'address', 'city__name', 'pin']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')


class CustomerContractAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'start_date', 'end_date', 'billing_frequency', 'changed_by']
    search_fields = ['id', 'customer__name__profile__name', 'customer__company_code', 'billing_frequency',
                     'changed_by__profile__name']
    list_filter = ['billing_frequency', ('start_date', DateFieldListFilter), ('end_date', DateFieldListFilter),
                   'customer']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')
    autocomplete_fields = ('customer',)

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super().save_model(request, obj, form, change)


class ContractRouteAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'source', 'destination', 'rate_type', 'rate', 'changed_by']
    search_fields = ['id', 'contract__customer__company_code', 'contract__customer__name__profile__name',
                     'source__name', 'changed_by__profile__name',
                     'destination__name', 'rate_type__name', 'rate']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')
    autocomplete_fields = ('contract','source', 'destination',)

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super().save_model(request, obj, form, change)

    @staticmethod
    def customer(obj):
        try:
            return obj.contract.customer.get_name()
        except CustomerContract.DoesNotExist:
            return ''


class RateTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'changed_by']
    search_fields = ['id', 'name', 'changed_by__profile__name']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by')

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super().save_model(request, obj, form, change)


class SmeSummaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'sme', 'placed_order_accounting_summary_json', 'billed_accounting_summary_json']
    readonly_fields = ('id', 'deleted_on', 'deleted', 'created_on', 'updated_on')
    search_fields = ('id', 'sme__name__profile__name','sme__company_code')

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

    accounting_summary_json.short_description = 'Accounting Summary'

    def placed_order_accounting_summary_json(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.placed_order_accounting_summary, sort_keys=True, indent=2)

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

    accounting_summary_json.short_description = 'Placed Order Summary'

    def billed_accounting_summary_json(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.billed_accounting_summary, sort_keys=True, indent=2)

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

    accounting_summary_json.short_description = 'Billed Summary'


admin.site.register(Sme, SmeAdmin)
admin.site.register(SmeEnquiry)
admin.site.register(ContactDetails)
admin.site.register(Location)
admin.site.register(ConsignorConsignee, ConsignorConsigneeAdmin)
admin.site.register(PreferredVehicle)
admin.site.register(CustomerContract, CustomerContractAdmin)
admin.site.register(ContractRoute, ContractRouteAdmin)
admin.site.register(RateType, RateTypeAdmin)
admin.site.register(SmeTaskEmail)
admin.site.register(SmeSummary, SmeSummaryAdmin)
