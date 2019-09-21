from django.contrib import admin
from django.utils.timezone import localtime
from simple_history.admin import SimpleHistoryAdmin

from driver.models import GPSLogNew, Driver, DriverAppUser, GPSDeviceLog, GPSDevice, TracknovateGPSDevice, \
    TracknovateGPSDeviceLog, WaytrackerGPSDevice, WaytrackerGPSDeviceLog, TempoGoGPSDevice, TempoGoGPSDeviceLog, \
    SecuGPSDevice, SecuGPSDeviceLog, MahindraGPSDevice, MahindraGPSDeviceLog, GPSDeviceProvider, BharatGPSTrackerLog
from owner.vehicle_util import display_format


class AccurateTimeAdmin(admin.ModelAdmin):
    def time_accurate(self, obj):
        return (obj.datetime).strftime("%H:%M:%S %d/%m/%Y")

    time_accurate.short_description = 'Log time'


class GPSLogNewAdmin(AccurateTimeAdmin):
    class Media:
        css = {
            'all': ('custom_admin/css/new_gps_log_admin.css',)
        }

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.opts.local_fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def free_memory_str(self, obj):
        return obj.free_memory()

    free_memory_str.short_description = 'Free Memory'

    def phone_model_str(self, obj):
        return obj.phone_model()

    phone_model_str.short_description = 'Phone Model'

    def location(self, obj):
        return '{:.7f},{:.7f}'.format(obj.latitude, obj.longitude)

    location.short_description = 'Location'

    def sdk(self, obj):
        return obj.android_release

    sdk.short_description = 'SDK'

    def app(self, obj):
        return obj.version_name

    app.short_description = 'App'

    def driver_name_str(self, obj):
        return obj.driver_name or obj.driver_number or '-'

    driver_name_str.short_description = 'Driver'

    def accuracy_round(self, obj):
        return None if obj.accuracy is None else round(obj.accuracy, 1)

    accuracy_round.short_description = 'Accuracy'

    list_display = (
        'device_id', 'time_accurate', 'location', 'provider', 'accuracy_round', 'battery', 'free_memory_str',
        'phone_model_str', 'sdk', 'app', 'driver_name_str')
    list_filter = ('device_id',)
    actions = None


class DriverAppUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'device_id', 'created_on', 'driver_name',
                    'vehicle_number', 'vehicle_type')
    readonly_fields = (
        'id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by', 'inactive_sms_sent_at')


class GPSDeviceLogAdmin(AccurateTimeAdmin):
    class Media:
        css = {
            'all': ('custom_admin/css/new_gps_log_admin.css',)
        }

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.opts.local_fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def location(self, obj):
        return '{:.7f},{:.7f}'.format(obj.latitude, obj.longitude)

    location.short_description = 'Location'

    def driver_name_str(self, obj):
        return obj.driver_name or obj.driver_number or '-'

    driver_name_str.short_description = 'Driver'

    def accuracy_round(self, obj):
        return None if obj.accuracy is None else round(obj.accuracy, 1)

    accuracy_round.short_description = 'Accuracy'

    list_display = ('device_id', 'time_accurate', 'location', 'accuracy_round', 'vehicle_number')
    list_filter = ('device_id',)
    actions = None


class GPSDeviceAdmin(SimpleHistoryAdmin):
    list_display = (
        'id', 'vehicle_id', 'vehicle_type', 'driver_name', 'driver_number', 'latitude', 'longitude', 'location_time',
        'device_provider', 'is_active', 'address')
    search_fields = ['id', 'vehicle__vehicle_number']
    readonly_fields = ('id', 'created_by', 'changed_by', 'created_on', 'updated_on', 'deleted', 'deleted_on')
    autocomplete_fields = ('vehicle', 'driver')
    list_filter = ('location_time', 'device_provider')
    history_list_display = ["status"]
    actions = ['delete_selected']

    def vehicle_id(self, instance):
        if instance.vehicle:
            return instance.vehicle.number()
        return '-'


class TempoGoGPSDeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'veh_num', 'driver_name', 'driver_number', 'latitude', 'longitude', 'location_time']
    readonly_fields = ('id', 'created_on', 'deleted', 'deleted_on', 'created_by', 'changed_by', 'inactive_sms_sent_at')
    search_fields = ('id', 'vehicle_number')
    actions = ['delete_selected']
    list_filter = ('imei',)

    def veh_num(self, obj):
        return display_format(obj.vehicle_number)


class TempoGoGPSDeviceLogAdmin(admin.ModelAdmin):
    list_display = [
        'veh_num', 'driver_name', 'driver_number', 'latitude', 'longitude', 'datetime', 'gps_log_id', 'updated_on']
    search_fields = ['vehicle_number', 'driver_name', 'driver_number', 'vehicle_id']
    list_filter = ['device']

    ordering = ['-datetime']

    def veh_num(self, obj):
        return display_format(obj.vehicle_number)


class TracknovateGPSDeviceAdmin(admin.ModelAdmin):
    list_display = ['veh_num', 'driver_name', 'driver_number', 'latitude', 'longitude', 'location_time']

    def veh_num(self, obj):
        return display_format(obj.vehicle_number)


class DriverAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'driving_licence_number', 'driving_licence_validity','account_details']
    search_fields = ['id', 'name', 'phone', 'alt_phone', 'alt_phone2', 'driving_licence_number',
                     'driving_licence_validity']
    readonly_fields = (
        'id', 'deleted_on', 'deleted', 'created_by', 'created_on', 'updated_on', 'changed_by', 'address', 'taxation_id',
        'account_details', 'driving_licence')


class WaytrackerGPSDeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'veh_num', 'driver_name', 'driver_number', 'latitude', 'longitude', 'location_time']
    readonly_fields = ('id', 'created_on', 'deleted', 'deleted_on', 'created_by', 'changed_by', 'inactive_sms_sent_at')
    search_fields = ('id', 'vehicle_number')

    def veh_num(self, obj):
        return display_format(obj.vehicle_number)


class SecuGPSDeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'veh_num', 'driver_name', 'driver_number', 'latitude', 'longitude', 'location_time']
    readonly_fields = ('id', 'created_on', 'deleted', 'deleted_on', 'created_by', 'changed_by', 'inactive_sms_sent_at')
    search_fields = ('id', 'vehicle_number')

    def veh_num(self, obj):
        return display_format(obj.vehicle_number)


class MahindraGPSDeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'veh_num', 'driver_name', 'driver_number', 'latitude', 'longitude', 'location_time']
    readonly_fields = ('id', 'created_on', 'deleted', 'deleted_on', 'created_by', 'changed_by', 'inactive_sms_sent_at')
    search_fields = ('id', 'vehicle_number')

    def veh_num(self, obj):
        return display_format(obj.vehicle_number)


class MahindraGPSDeviceLogAdmin(admin.ModelAdmin):
    list_display = ['veh_num', 'driver_name', 'driver_number', 'latitude', 'longitude', 'datetime',
                    'updated_on']
    search_fields = ['vehicle_number', 'driver_name', 'driver_number', 'vehicle_id']
    ordering = ['-datetime']

    def veh_num(self, obj):
        return display_format(obj.vehicle_number)


class GPSDeviceProviderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

    # def get_readonly_fields(self, request, obj=None):
    #     return [field.name for field in self.opts.local_fields]
    #
    # def has_add_permission(self, request):
    #     return True

    def has_delete_permission(self, request, obj=None):
        return False


class BharatGPSTrackerLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'device', 'latitude', 'longitude', 'datetime']
    list_filter = ('datetime', 'vehicle_number')
    search_fields = ('id', 'vehicle_number')


admin.site.register(Driver, DriverAdmin)
admin.site.register(DriverAppUser, DriverAppUserAdmin)
admin.site.register(GPSLogNew, GPSLogNewAdmin)
admin.site.register(GPSDeviceLog, GPSDeviceLogAdmin)
admin.site.register(GPSDevice, GPSDeviceAdmin)
admin.site.register(GPSDeviceProvider, GPSDeviceProviderAdmin)
admin.site.register(TracknovateGPSDevice, TracknovateGPSDeviceAdmin)
admin.site.register(TracknovateGPSDeviceLog)
admin.site.register(WaytrackerGPSDevice, WaytrackerGPSDeviceAdmin)
admin.site.register(WaytrackerGPSDeviceLog)
admin.site.register(TempoGoGPSDevice, TempoGoGPSDeviceAdmin)
admin.site.register(TempoGoGPSDeviceLog, TempoGoGPSDeviceLogAdmin)
admin.site.register(SecuGPSDevice, SecuGPSDeviceAdmin)
admin.site.register(SecuGPSDeviceLog)
admin.site.register(MahindraGPSDevice, MahindraGPSDeviceAdmin)
admin.site.register(MahindraGPSDeviceLog, MahindraGPSDeviceLogAdmin)
admin.site.register(BharatGPSTrackerLog, BharatGPSTrackerLogAdmin)
