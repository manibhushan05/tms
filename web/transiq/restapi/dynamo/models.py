from pynamodb.models import Model
from datetime import datetime
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, UTCDateTimeAttribute, MapAttribute, NumberAttribute


class DEV_User(Model):
    class Meta:
        aws_access_key_id = 'AKIAJXFC3JRVYNIHX2UA'
        aws_secret_access_key = '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'
        table_name = "DEV_User"
        region = 'ap-south-1'
        write_capacity_units = 10
        read_capacity_units = 10

    username = UnicodeAttribute(hash_key=True)
    password = UnicodeAttribute(null=False)
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    is_staff = BooleanAttribute(default=False)
    is_active = BooleanAttribute(default=True)
    date_joined = UTCDateTimeAttribute(default=datetime.now())


class STAGE_User(Model):
    class Meta:
        aws_access_key_id = 'AKIAJXFC3JRVYNIHX2UA'
        aws_secret_access_key = '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'
        table_name = "STAGE_User"
        region = 'ap-south-1'
        write_capacity_units = 10
        read_capacity_units = 10

    username = UnicodeAttribute(hash_key=True)
    password = UnicodeAttribute(null=False)
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    is_staff = BooleanAttribute(default=False)
    is_active = BooleanAttribute(default=True)
    date_joined = UTCDateTimeAttribute(default=datetime.now())


class PROD_User(Model):
    class Meta:
        aws_access_key_id = 'AKIAJXFC3JRVYNIHX2UA'
        aws_secret_access_key = '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'
        table_name = "PROD_User"
        region = 'ap-south-1'
        write_capacity_units = 10
        read_capacity_units = 10

    username = UnicodeAttribute(hash_key=True)
    password = UnicodeAttribute(null=False)
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    is_staff = BooleanAttribute(default=False)
    is_active = BooleanAttribute(default=True)
    date_joined = UTCDateTimeAttribute(default=datetime.now())


class LOCAL_User(Model):
    class Meta:
        aws_access_key_id = 'AKIAJXFC3JRVYNIHX2UA'
        aws_secret_access_key = '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'
        table_name = "LOCAL_User"
        region = 'ap-south-1'
        write_capacity_units = 10
        read_capacity_units = 10

    username = UnicodeAttribute(hash_key=True)
    password = UnicodeAttribute(null=False)
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    is_staff = BooleanAttribute(default=False)
    is_active = BooleanAttribute(default=True)
    date_joined = UTCDateTimeAttribute(default=datetime.now())


class DEV_GPS_LOCATION(Model):
    class Meta:
        aws_access_key_id = 'AKIAJXFC3JRVYNIHX2UA'
        aws_secret_access_key = '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'
        table_name = "DEV_GPS_LOCATION"
        region = 'ap-south-1'
        write_capacity_units = 2
        read_capacity_units = 2

    created_by = UnicodeAttribute(null=True)
    changed_by = UnicodeAttribute(null=True)
    gps_device_provider = UnicodeAttribute(null=True)
    created_on = UTCDateTimeAttribute(default=datetime.now())
    updated_on = UTCDateTimeAttribute(default=datetime.now())
    deleted = BooleanAttribute(default=False)
    deleted_on = UTCDateTimeAttribute(null=True)
    device_id = UnicodeAttribute(hash_key=True)
    imei = UnicodeAttribute(null=True)
    driver_name = UnicodeAttribute(null=True)
    driver_number = UnicodeAttribute(null=True)
    driving_licence_number = UnicodeAttribute(null=True)
    vehicle_number = UnicodeAttribute(null=True)
    vehicle_type = UnicodeAttribute(null=True)
    vehicle_status = UnicodeAttribute(null=True)
    location_time = UTCDateTimeAttribute(null=True)
    latitude = NumberAttribute(attr_name='latitude')
    longitude = NumberAttribute(attr_name='longitude')
    address = UnicodeAttribute(null=True)
    is_active = BooleanAttribute(default=True)


class STAGE_GPS_LOCATION(Model):
    class Meta:
        aws_access_key_id = 'AKIAJXFC3JRVYNIHX2UA'
        aws_secret_access_key = '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'
        table_name = "STAGE_GPS_LOCATION"
        region = 'ap-south-1'
        write_capacity_units = 2
        read_capacity_units = 2

    created_by = UnicodeAttribute(null=True)
    changed_by = UnicodeAttribute(null=True)
    gps_device_provider = UnicodeAttribute(null=True)
    created_on = UTCDateTimeAttribute(default=datetime.now())
    updated_on = UTCDateTimeAttribute(default=datetime.now())
    deleted = BooleanAttribute(default=False)
    deleted_on = UTCDateTimeAttribute(null=True)
    device_id = UnicodeAttribute(hash_key=True)
    imei = UnicodeAttribute(null=True)
    driver_name = UnicodeAttribute(null=True)
    driver_number = UnicodeAttribute(null=True)
    driving_licence_number = UnicodeAttribute(null=True)
    vehicle_number = UnicodeAttribute(null=True)
    vehicle_type = UnicodeAttribute(null=True)
    vehicle_status = UnicodeAttribute(null=True)
    location_time = UTCDateTimeAttribute(null=True)
    latitude = NumberAttribute(attr_name='latitude')
    longitude = NumberAttribute(attr_name='longitude')
    address = UnicodeAttribute(null=True)
    is_active = BooleanAttribute(default=True)


class PROD_GPS_LOCATION(Model):
    class Meta:
        aws_access_key_id = 'AKIAJXFC3JRVYNIHX2UA'
        aws_secret_access_key = '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'
        table_name = "PROD_GPS_LOCATION"
        region = 'ap-south-1'
        write_capacity_units = 2
        read_capacity_units = 2

    created_by = UnicodeAttribute(null=True)
    changed_by = UnicodeAttribute(null=True)
    gps_device_provider = UnicodeAttribute(null=True)
    created_on = UTCDateTimeAttribute(default=datetime.now())
    updated_on = UTCDateTimeAttribute(default=datetime.now())
    deleted = BooleanAttribute(default=False)
    deleted_on = UTCDateTimeAttribute(null=True)
    device_id = UnicodeAttribute(hash_key=True)
    imei = UnicodeAttribute(null=True)
    driver_name = UnicodeAttribute(null=True)
    driver_number = UnicodeAttribute(null=True)
    driving_licence_number = UnicodeAttribute(null=True)
    vehicle_number = UnicodeAttribute(null=True)
    vehicle_type = UnicodeAttribute(null=True)
    vehicle_status = UnicodeAttribute(null=True)
    location_time = UTCDateTimeAttribute(null=True)
    latitude = NumberAttribute(attr_name='latitude')
    longitude = NumberAttribute(attr_name='longitude')
    address = UnicodeAttribute(null=True)
    is_active = BooleanAttribute(default=True)


class LOCAL_GPS_LOCATION(Model):
    class Meta:
        aws_access_key_id = 'AKIAJXFC3JRVYNIHX2UA'
        aws_secret_access_key = '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'
        table_name = "LOCAL_GPS_LOCATION"
        region = 'ap-south-1'
        write_capacity_units = 2
        read_capacity_units = 2

    created_by = UnicodeAttribute(null=True)
    changed_by = UnicodeAttribute(null=True)
    gps_device_provider = UnicodeAttribute(null=True)
    created_on = UTCDateTimeAttribute(default=datetime.now())
    updated_on = UTCDateTimeAttribute(default=datetime.now())
    deleted = BooleanAttribute(default=False)
    deleted_on = UTCDateTimeAttribute(null=True)
    device_id = UnicodeAttribute(hash_key=True)
    imei = UnicodeAttribute(null=True)
    driver_name = UnicodeAttribute(null=True)
    driver_number = UnicodeAttribute(null=True)
    driving_licence_number = UnicodeAttribute(null=True)
    vehicle_number = UnicodeAttribute(null=True)
    vehicle_type = UnicodeAttribute(null=True)
    vehicle_status = UnicodeAttribute(null=True)
    location_time = UTCDateTimeAttribute(null=True)
    latitude = NumberAttribute(attr_name='latitude')
    longitude = NumberAttribute(attr_name='longitude')
    address = UnicodeAttribute(null=True)
    is_active = BooleanAttribute(default=True)

