# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.contrib import admin

from notification.models import MobileDevice


class MobileDeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'app', 'token', 'device_id', 'active']
    list_filter = ['app', 'device_id', 'active']
    search_fields = ['user__profile__name', 'user__username', 'app', 'token', 'device_id']

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.deleted_on = datetime.now()
        obj.changed_by = request.user
        super(MobileDeviceAdmin, self).delete_model(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False
        return True

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(MobileDeviceAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['deleted_on', 'changed_by', 'created_on', 'updated_on', 'deleted']


admin.site.register(MobileDevice, MobileDeviceAdmin)
