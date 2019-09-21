from rest_framework import serializers
from restapi.dynamo.config import DynamoTablesEnvConfiguration
from restapi.dynamo.utils import DynamoTable
from restapi.helper_api import DATETIME_FORMAT
from datetime import datetime
from restapi.service.validators import MOBILE_NUMBER_REGEX,VEHICLE_NUMBER_REGEX, validate_vehicle_number

class GPSDeviceSerializers(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    created_on = serializers.DateTimeField(allow_null=True, required=False, format=DATETIME_FORMAT)
    updated_on = serializers.DateTimeField(allow_null=True, required=False, format=DATETIME_FORMAT)
    deleted = serializers.BooleanField(required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    device_id = serializers.CharField(allow_blank=True, allow_null=True, max_length=50, required=False)
    imei = serializers.CharField(allow_blank=True, allow_null=True, max_length=40, required=False)
    address = serializers.CharField(allow_blank=True, allow_null=True, max_length=500, required=False)
    driver_name = serializers.CharField(allow_blank=True, allow_null=True, max_length=50, required=False)
    #driver_number = serializers.CharField(allow_blank=True, allow_null=True, max_length=20, required=False)
    driver_number = serializers.RegexField(regex=MOBILE_NUMBER_REGEX, allow_null=True, allow_blank=True, min_length=10, max_length=10, required=False)

    driving_licence_number = serializers.CharField(allow_blank=True, allow_null=True, max_length=20, required=False)
    #vehicle_number = serializers.CharField(allow_blank=True, allow_null=True, max_length=40, required=False)
    vehicle_number = serializers.RegexField(regex=VEHICLE_NUMBER_REGEX,allow_null=True,allow_blank=True,required=False)

    vehicle_type = serializers.CharField(allow_blank=True, allow_null=True, max_length=40, required=False)
    vehicle_status = serializers.ChoiceField(
        choices=(('unloaded', 'unloaded'), ('loading', 'loading'), ('loaded', 'loaded'), ('unloading', 'unloading')),
        required=False)
    location_time = serializers.DateTimeField(allow_null=True, required=False, format=DATETIME_FORMAT)
    latitude = serializers.DecimalField(decimal_places=10, max_digits=12, required=False)
    longitude = serializers.DecimalField(decimal_places=10, max_digits=12, required=False)
    is_active = serializers.BooleanField(required=False)
    created_by = serializers.CharField(allow_null=True, required=False)
    changed_by = serializers.CharField(allow_null=True, required=False)
    #gps_device_provider = serializers.CharField(allow_null=True, required=False)
    gps_device_provider = serializers.CharField(allow_null=True, max_length=25, required=False)

    def create(self, validated_data):
        dtc = DynamoTablesEnvConfiguration()
        gps_dt = DynamoTable(dtc.GPS_LOCATION)
        gps_dt.create()
        attributes = {
            'created_by': validated_data['created_by'] if 'created_by' in validated_data else None,
            'gps_device_provider': validated_data['gps_device_provider'] if 'gps_device_provider' in validated_data else None,
            'created_on': datetime.now(),
            'imei': validated_data['imei'] if 'imei' in validated_data else None,
            'driver_name': validated_data['driver_name'] if 'driver_name' in validated_data else None,
            'driver_number': validated_data['driver_number'] if 'driver_number' in validated_data else None,
            'driving_licence_number': validated_data['driving_licence_number'] if validated_data['driving_licence_number'] else None,
            'vehicle_number': validated_data['vehicle_number'] if 'vehicle_number' in validated_data else None,
            'vehicle_type': validated_data['vehicle_type'] if 'vehicle_type' in validated_data else None,
            'vehicle_status': validated_data['vehicle_status'] if 'vehicle_status' in validated_data else None,
            'location_time': validated_data['location_time'] if 'location_time' in validated_data else None,
            'address': validated_data['address'] if 'address' in validated_data else None,
            'is_active': validated_data['is_active'] if 'is_active' in validated_data else None,
            'latitude': float(validated_data['latitude']) if 'latitude' in validated_data else None,
            'longitude': float(validated_data['longitude']) if 'longitude' in validated_data else None
        }
        instance = gps_dt.put_item(validated_data['device_id'], attributes)
        return instance

    def update(self, instance, validated_data):
        dtc = DynamoTablesEnvConfiguration()
        gps_dt = DynamoTable(dtc.GPS_LOCATION)
        gps_dt.create()
        attributes = {
            'changed_by': validated_data['changed_by'] if 'changed_by' in validated_data else None,
            'updated_on': datetime.now(),
            'address': validated_data['address'] if 'address' in validated_data else None,
            'imei': validated_data['imei'] if 'imei' in validated_data else None

        }

        if 'changed_by' in validated_data:
            validated_data.pop('changed_by')
        if 'changed_on' in validated_data:
            validated_data.pop('changed_on')
        for key in validated_data.keys():
            if key == 'latitude' or key == 'longitude':
                attributes.update({key: float(validated_data[key])})
            else:
                attributes.update({key:validated_data[key]})

        instance = gps_dt.update_item(instance.device_id, attributes)
        return instance

    def validate_vehicle_number(self, value):
        if not validate_vehicle_number(value) and value:
            raise serializers.ValidationError("Not a valid vehicle number")
        return value