from django.contrib import admin
from . import models


class RouteAdmin(admin.ModelAdmin):
    list_display = ['source', 'destination', 'created_on']
    search_fields = ['source', 'destination']


class SubRouteAdmin(admin.ModelAdmin):
    list_display = ['id', 'loading_point', 'unloading_point']
    readonly_fields = ('id', 'created_on', 'updated_on')


class RouteFreightAdmin(admin.ModelAdmin):
    search_fields = ['route__loading_point', 'route__unloading_point', 'freight', 'material']
    list_display = ['id', 'freight', 'material', 'datetime']
    list_filter = ('datetime',)
    readonly_fields = ('id', 'created_by', 'created_on', 'updated_on')


admin.site.register(models.EmailOTP)
admin.site.register(models.PhoneOTP)
admin.site.register(models.Route, RouteAdmin)
admin.site.register(models.SubRoute, SubRouteAdmin)
admin.site.register(models.RouteFreight, RouteFreightAdmin)
