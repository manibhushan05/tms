from django.contrib import admin
from django.utils.html import format_html

from api.models import S3Upload, FakeSms, GeoLocatedData


class S3UploadAdmin(admin.ModelAdmin):
    # class Media:
    #     css = {
    #         'all': ('custom_admin/css/new_gps_log_admin.css',)
    #     }

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.opts.local_fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def link(self, obj):
        return format_html('<a href="{}">download</a>'.format(obj.public_url()))

    link.short_description = 'Link'

    list_display = (
        'id', 'bucket', 'folder', 'uuid', 'filename', 'link', 'uploaded_on', 'verified', 'is_valid', 'deleted')
    search_fields = ('id', 'filename','uuid')
    list_filter = ('bucket', 'folder', 'uploaded_on')
    actions = None


class PaymentFileAdmin(admin.ModelAdmin):
    list_display = ('id')


admin.site.register(S3Upload, S3UploadAdmin)
admin.site.register(FakeSms)
admin.site.register(GeoLocatedData)
