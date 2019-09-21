import binascii
import os
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from numpy import random
from simple_history.models import HistoricalRecords

from api.utils import format_date
from fms.models import Document
from owner.vehicle_util import display_format, compare_format
from utils.models import Address, IDDetails, TaxationID, Bank


class Driver(models.Model):
    name = models.CharField(max_length=35, blank=True, null=True)
    address = models.OneToOneField(Address, blank=True, null=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=35, unique=True)
    alt_phone = models.CharField(max_length=35, blank=True, null=True, db_index=True)
    alt_phone2 = models.CharField(max_length=35, blank=True, null=True)
    driving_licence_number = models.CharField(max_length=50, null=True, blank=True)
    driving_licence_location = models.CharField(max_length=50, null=True, blank=True)
    driving_licence_validity = models.DateField(null=True, blank=True)
    id_proof = models.OneToOneField(IDDetails, blank=True, null=True, on_delete=models.CASCADE)
    account_details = models.OneToOneField(Bank, blank=True, null=True, on_delete=models.CASCADE)
    pan = models.CharField(max_length=11, null=True, blank=True)
    taxation_id = models.OneToOneField(TaxationID, blank=True, null=True, on_delete=models.CASCADE)
    smartphone_available = models.BooleanField(default=False)
    route = models.CharField(max_length=255, blank=True, null=True)
    priority_level = models.CharField(max_length=255, blank=True, null=True)

    driving_licence = models.ForeignKey(Document, blank=True, null=True, on_delete=models.CASCADE)

    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="driver_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="driver_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Driver Basic Info"
        ordering = ('-id',)

    def __str__(self):
        return '{}, {}'.format(self.name, self.phone)

    def to_json(self):
        data = {
            'id': self.id,
            'name': self.name,
            'address': None if not self.address else self.address.to_json(),
            'phone': self.phone,
            'driving_licence_number': self.driving_licence_number,
            'driving_licence_validity': format_date(self.driving_licence_validity),
            'driving_licence_location': self.driving_licence_location,
            'smartphone_available': self.smartphone_available,
            'route': self.route,
            'priority_level': self.priority_level,
            'id_proof': None if not self.id_proof else self.id_proof.to_json(),
            'account_details': None if not self.account_details else self.account_details.to_json(),
            'taxation_details': None if not self.taxation_id else self.taxation_id.to_json(),
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }
        tax = self.taxation_id
        if tax:
            data['pan_doc'] = {
                'url': None if not tax.pan_doc else tax.pan_doc.document,
                'thumb_url': None if not tax.pan_doc else tax.pan_doc.document_thumb,
                'doc_id': tax.pan,
                'validity': None
            }

        data['dl_doc'] = {
            'url': None if not self.driving_licence else self.driving_licence.document,
            'thumb_url': None if not self.driving_licence else self.driving_licence.document_thumb,
            'doc_id': self.driving_licence_number,
            'validity': format_date(self.driving_licence_validity),
            'issue_location': self.driving_licence_location
        }
        data['account'] = data.get('account_details', None)

        return data


VEHICLE_STATUS_CHOICES = (
    ('unloaded', 'unloaded'),
    ('loading', 'loading'),
    ('loaded', 'loaded'),
    ('unloading', 'unloading')
)


class DriverAppUser(models.Model):
    device_id = models.CharField(max_length=50, unique=True)
    auth_token = models.CharField(max_length=40, unique=True)
    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    number_verified = models.BooleanField(default=False)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE)

    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default='unloaded')

    location_time = models.DateTimeField(null=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    inactive_sms_sent_at = models.DateTimeField(null=True)

    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="driver_app_user_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="driver_app_user_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'driverapp_user'

    def save(self, *args, **kwargs):
        if not self.auth_token:
            self.auth_token = self.generate_token()
        if self.vehicle_number:
            self.vehicle_number = compare_format(self.vehicle_number)
        return super().save(*args, **kwargs)

    def number(self):
        return display_format(self.vehicle_number)

    @staticmethod
    def generate_token():
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.driver_name or str(self.id)

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.location_time or timezone.now())
        }
        return data

    def to_json(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'driver_name': self.driver_name,
            'driver_number': self.driver_number,
            'driving_licence_number': self.driving_licence_number,
            'vehicle_number': self.vehicle_number,
            'vehicle_type': self.vehicle_type,
            'vehicle_status': self.vehicle_status,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }


class GPSLogNew(models.Model):
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="gps_log_new_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="gps_log_new_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    # position
    datetime = models.DateTimeField(help_text='log time')
    device_id = models.CharField(max_length=50, help_text='imei or uuid generated on phone')
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    altitude = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    course = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    provider = models.CharField(max_length=20, null=True, blank=True)

    # phone state info
    battery = models.FloatField(null=True, blank=True)
    total_memory = models.FloatField(null=True, blank=True)
    available_memory = models.FloatField(null=True, blank=True)
    threshold = models.FloatField(null=True, blank=True)
    low_memory = models.BooleanField(default=False)

    # app and android sdk version info
    android_release = models.CharField(max_length=20, null=True, blank=True)
    android_sdk_int = models.IntegerField(null=True, blank=True)
    version_name = models.CharField(max_length=20, null=True, blank=True)
    version_code = models.IntegerField(null=True, blank=True)

    # phone model info
    brand = models.CharField(max_length=30, null=True, blank=True)
    manufacturer = models.CharField(max_length=30, null=True, blank=True)
    product = models.CharField(max_length=30, null=True, blank=True)
    device = models.CharField(max_length=30, null=True, blank=True)
    model = models.CharField(max_length=30, null=True, blank=True)

    # driver and vehicle info
    driver = models.ForeignKey(DriverAppUser, null=True, blank=True, related_name='new_gps_logs',
                               on_delete=models.CASCADE)
    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, null=True, blank=True)

    def free_memory(self):
        return '{:.1f}M {:.1f}%{}'.format(self.available_memory, self.percent_free(), self.low_memory_str())

    def percent_free(self):
        return (self.available_memory / self.total_memory) * 100.0

    def low_memory_str(self):
        return ' *' if self.low_memory else ''

    def phone_model(self):
        return ' '.join([self.manufacturer, self.model])

    def number(self):
        return display_format(self.vehicle_number)

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.datetime or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data

    class Meta:
        db_table = 'driverapp_gpslog_new'
        unique_together = ('device_id', 'datetime')
        verbose_name = 'New GPS Log'
        verbose_name_plural = 'New GPS Logs'

    def __str__(self):
        return '%s @ %s : [%s, %s]' % (self.device_id, self.datetime.isoformat(), self.latitude, self.longitude)


EXPIRY_TIME = timedelta(minutes=10)


class OTP(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    expires_at = models.DateTimeField()
    otp = models.CharField(max_length=8)

    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="otp_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="otp_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def verify(phone, otp):
        try:
            otp_instance = OTP.objects.get(phone=phone.strip())
            if otp_instance.expires_at < timezone.now():
                return False, 'opt expired'
            if otp_instance.otp != otp:
                return False, 'otp not equal'
            return True, 'verified'
        except OTP.DoesNotExist:
            return False, 'otp does not exist'

    @staticmethod
    def generate(phone):
        phone = phone.strip()
        try:
            otp_instance = OTP.objects.get(phone=phone)
            if otp_instance.expires_at < timezone.now():
                otp_instance.otp = new_otp(6)
        except OTP.DoesNotExist:
            otp_instance = OTP(phone=phone)
            otp_instance.otp = new_otp(6)

        otp_instance.expires_at = (timezone.now() + EXPIRY_TIME)
        otp_instance.save()
        return otp_instance.otp


OTP_CHARS = '0123456789'


def new_otp(num_digits):
    max_index = len(OTP_CHARS) - 1
    return ''.join(OTP_CHARS[random.randint(0, max_index)] for _ in range(num_digits))


class GPSDeviceProvider(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class GPSDevice(models.Model):
    """
    load existing data
    create a periodic task to update gps logs
    show result in track vehicles page
    show in gps data page
    """
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="gps_device_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="gps_device_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    device_provider = models.ForeignKey(GPSDeviceProvider, null=True, on_delete=models.CASCADE)
    vehicle = models.ForeignKey('owner.Vehicle', on_delete=True, null=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    imei = models.CharField(max_length=40, null=True, blank=True)
    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE)
    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default='unloaded')

    location_time = models.DateTimeField(null=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    address = models.CharField(max_length=500, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-id']

    def number(self):
        return display_format(self.vehicle_number)

    def __str__(self):
        return str(self.vehicle_number)

    def to_json(self):
        return {
            'id': self.id,
            'vehicle_number': self.vehicle_number,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.location_time or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data


class GPSDeviceLog(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    # position
    location_id = models.CharField(max_length=40, unique=True)
    datetime = models.DateTimeField(help_text='log time')
    vehicle_id = models.CharField(max_length=50, help_text='imei or uuid generated on phone')
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    altitude = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    course = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    engine_on = models.BooleanField(default=False)

    device = models.ForeignKey(GPSDevice, null=True, blank=True, related_name='gps_device_logs',
                               on_delete=models.CASCADE)

    # driver and vehicle info
    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, null=True, blank=True)

    def number(self):
        return display_format(self.vehicle_number)

    class Meta:
        # unique_together = ('vehicle_id', 'datetime')
        verbose_name = 'GPS Device Log'
        verbose_name_plural = 'GPS Device Logs'

    def __str__(self):
        return '%s @ %s : [%s, %s]' % (self.device_id, self.datetime.isoformat(), self.latitude, self.longitude)

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.datetime or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data


class TracknovateGPSDevice(models.Model):
    """
    load existing data
    create a periodic task to update gps logs
    show result in track vehicles page
    show in gps data page
    """

    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="tracknovate_gps_device_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="tracknovate_gps_device_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    phone = models.CharField(max_length=20)
    sim_number = models.CharField(max_length=20)
    vehicle_id = models.CharField(max_length=40, unique=True)

    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    number_verified = models.BooleanField(default=False)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE)

    current_duration = models.TextField(null=True)
    current_vstatus = models.TextField(null=True)

    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default='unloaded')

    location_time = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)

    inactive_sms_sent_at = models.DateTimeField(null=True)

    def number(self):
        return display_format(self.vehicle_number)

    def __str__(self):
        return str(self.vehicle_id)

    def to_json(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'vehicle_number': self.vehicle_number,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.location_time or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data


class TracknovateGPSDeviceLog(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    # position
    datetime = models.DateTimeField(help_text='log time')
    vehicle_id = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    altitude = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    course = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    engine_on = models.BooleanField(default=False)

    device = models.ForeignKey(TracknovateGPSDevice, null=True, blank=True, related_name='device_logs',
                               on_delete=models.CASCADE)

    # driver and vehicle info
    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, null=True, blank=True)

    def number(self):
        return display_format(self.vehicle_number)

    class Meta:
        # unique_together = ('vehicle_id', 'datetime')
        verbose_name = 'Tracknovate GPS Device Log'
        verbose_name_plural = 'Tracknovate GPS Device Logs'

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.datetime or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data

    def __str__(self):
        return '%s @ %s : [%s, %s]' % (self.device_id, self.datetime.isoformat(), self.latitude, self.longitude)


class WaytrackerGPSDevice(models.Model):
    """
    load existing data
    create a periodic task to update gps logs
    show result in track vehicles page
    show in gps data page
    """
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="waytracker_gps_device_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="waytracker_gps_device_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    vehicle_id = models.CharField(max_length=40, unique=True)

    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    number_verified = models.BooleanField(default=False)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE)

    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default='unloaded')

    location_time = models.DateTimeField(null=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    inactive_sms_sent_at = models.DateTimeField(null=True)

    def number(self):
        return display_format(self.vehicle_number)

    def __str__(self):
        return str(self.vehicle_id)

    def to_json(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'vehicle_number': self.vehicle_number,
            'created_on': format_date(self.created_on),
            'updated_on': format_date(self.updated_on),
        }

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.location_time or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data


class WaytrackerGPSDeviceLog(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    # position
    datetime = models.DateTimeField(help_text='log time')
    vehicle_id = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    altitude = models.FloatField(null=True, blank=True)  # 0
    speed = models.FloatField(null=True, blank=True)
    course = models.FloatField(null=True, blank=True)  # 0
    accuracy = models.FloatField(null=True, blank=True)  # 0
    engine_on = models.BooleanField(default=False)

    fuel = models.CharField(max_length=10, null=True, blank=True)
    nearest_site = models.CharField(max_length=150, null=True, blank=True)
    nearest_location = models.CharField(max_length=150, null=True, blank=True)
    idle_time = models.CharField(max_length=20, null=True, blank=True)

    device = models.ForeignKey(WaytrackerGPSDevice, null=True, blank=True, related_name='device_logs',
                               on_delete=models.CASCADE)

    # driver and vehicle info
    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, null=True, blank=True)

    def number(self):
        return display_format(self.vehicle_number)

    class Meta:
        # unique_together = ('vehicle_id', 'datetime')
        verbose_name = 'Waytracker GPS Device Log'
        verbose_name_plural = 'Waytracker GPS Device Logs'

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.datetime or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data

    def __str__(self):
        return '%s @ %s : [%s, %s]' % (self.device_id, self.datetime.isoformat(), self.latitude, self.longitude)


class TempoGoGPSDevice(models.Model):
    """
       load existing data
       create a periodic task to update gps logs
       show result in track vehicles page
       show in gps data page
    """
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="tempo_go_gps_device_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="tempo_go_gps_device_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    device_id = models.CharField(max_length=50)
    imei = models.CharField(max_length=50)

    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    number_verified = models.BooleanField(default=False)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE)

    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default='unloaded')

    location_time = models.DateTimeField(null=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    inactive_sms_sent_at = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if self.vehicle_number:
            self.vehicle_number = compare_format(self.vehicle_number)
        return super().save(*args, **kwargs)

    def number(self):
        return display_format(self.vehicle_number)

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.location_time or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data


class TempoGoGPSDeviceLog(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    device = models.ForeignKey(TempoGoGPSDevice, null=True, blank=True, related_name='device_logs',
                               on_delete=models.CASCADE)
    gps_log_id = models.CharField(max_length=50)
    datetime = models.DateTimeField(help_text='log time')
    vehicle_id = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    speed = models.FloatField(null=True, blank=True)

    # driver and vehicle info
    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, null=True, blank=True)

    class Meta:
        unique_together = ('gps_log_id', 'datetime')
        verbose_name = 'TempoGO GPS Device Log'
        verbose_name_plural = 'TempoGO GPS Device Logs'

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.datetime or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data


class SecuGPSDevice(models.Model):
    """
       load existing data
       create a periodic task to update gps logs
       show result in track vehicles page
       show in gps data page
    """
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="secu_gps_device_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="secu_gps_device_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    device_id = models.CharField(max_length=50, unique=True)
    imei = models.CharField(max_length=50)

    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    number_verified = models.BooleanField(default=False)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE)

    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default='unloaded')

    location_time = models.DateTimeField(null=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    address = models.CharField(max_length=300, null=True)
    status = models.CharField(max_length=300, null=True)

    is_active = models.BooleanField(default=True)
    inactive_sms_sent_at = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if self.vehicle_number:
            self.vehicle_number = compare_format(self.vehicle_number)
        return super().save(*args, **kwargs)

    def number(self):
        return display_format(self.vehicle_number)

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.location_time or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data


class SecuGPSDeviceLog(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    device = models.ForeignKey(SecuGPSDevice, null=True, blank=True, related_name='device_logs',
                               on_delete=models.CASCADE)
    datetime = models.DateTimeField(help_text='log time')
    vehicle_id = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    speed = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=300, null=True)
    status = models.CharField(max_length=300, null=True)

    # driver and vehicle info
    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=40, null=True, blank=True)
    driving_licence_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = 'Secu GPS Device Log'
        verbose_name_plural = 'Secu GPS Device Logs'

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.datetime or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data


class MahindraGPSDevice(models.Model):
    """
       load existing data
       create a periodic task to update gps logs
       show result in track vehicles page
       show in gps data page
    """
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="mahindra_gps_device_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                   related_name="mahindra_gps_device_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    device_id = models.CharField(max_length=50, unique=True)
    imei = models.CharField(max_length=50, null=True)

    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=20, null=True, blank=True)
    number_verified = models.BooleanField(default=False)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE)

    driving_licence_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default='unloaded')

    location_time = models.DateTimeField(null=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    address = models.CharField(max_length=300, null=True)
    status = models.CharField(max_length=300, null=True)

    is_active = models.BooleanField(default=True)
    inactive_sms_sent_at = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if self.vehicle_number:
            self.vehicle_number = compare_format(self.vehicle_number)
        return super().save(*args, **kwargs)

    def number(self):
        return display_format(self.vehicle_number)

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.location_time or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data


class MahindraGPSDeviceLog(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    device = models.ForeignKey(MahindraGPSDevice, null=True, blank=True, related_name='fjhfjhfgjh',
                               on_delete=models.CASCADE)
    datetime = models.DateTimeField(help_text='log time')
    vehicle_id = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    speed = models.FloatField(null=True, blank=True)
    fuel_efficiency = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=300, null=True)
    status = models.CharField(max_length=300, null=True)

    # driver and vehicle info
    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=40, null=True, blank=True)
    driving_licence_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = 'Mahindra Digisense GPS Device Log'
        verbose_name_plural = 'Mahindra Digisense Device Logs'

    def location(self):
        if self.longitude is None or self.latitude is None:
            return None
        from api.models import google_reverse_geocode
        geo_data = google_reverse_geocode(self.latitude, self.longitude)
        data = {
            'name': geo_data['name'],
            'district': geo_data['district'],
            'state': geo_data['state'],
            'country': geo_data['country'],
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'time': format_date(self.datetime or timezone.now())
        }
        return data

    def driver_json(self):
        data = {
            'id': self.id,
            'name': self.driver_name,
            'phone': self.driver_number,
            'dl_number': self.driving_licence_number
        }
        return data


class BharatGPSTrackerLog(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE)
    position_id = models.CharField(max_length=35, null=True, unique=True)
    datetime = models.DateTimeField(help_text='log time')
    latitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    speed = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=300, null=True)
    status = models.CharField(max_length=300, null=True)

    # driver and vehicle info
    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_number = models.CharField(max_length=40, null=True, blank=True)
    driving_licence_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_number = models.CharField(max_length=40, null=True, blank=True)
    vehicle_type = models.CharField(max_length=40, null=True, blank=True)
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = 'Bharat GPS Device Log'
        verbose_name_plural = 'Bharat Device Logs'
