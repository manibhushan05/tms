from django.contrib import admin

from fms.models import Document, Requirement


class RequirementAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'aaho_office', 'from_city', 'to_city', 'from_shipment_date', 'to_shipment_date',
                    'no_of_vehicles', 'rate', 'tonnage', 'material']
    search_fields = ['id', 'client__name__profile__name', 'from_city__name', 'from_city__state__name', 'to_city__name',
                     'to_city__state__name', 'no_of_vehicles', 'rate', 'tonnage', 'material',
                     'aaho_office__branch__name']

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.opts.local_fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(RequirementAdmin, self).changeform_view(request, object_id, extra_context=extra_context)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'document']
    search_fields = ['id', 'user__username']


admin.site.register(Document, DocumentAdmin)
admin.site.register(Requirement, RequirementAdmin)
