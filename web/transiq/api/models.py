import re
import time
from decimal import Decimal

import requests
from django.contrib.auth.models import User
from django.db import models
from django.db.models.aggregates import Max
from django.db.utils import IntegrityError
from django.utils import timezone

from api import s3
from api.utils import is_unique_constraint_error, get_or_none

MAPS_API_TEMPLATE = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&address_type=locality&key=%s'
MAPS_API_KEY = 'AIzaSyDxwSjMZTmk0gcLdNJnMKxZDxqfQTWhSCk'
MAPS_API_DAILY_LIMIT = 2500
MAPS_API_RATE_LIMIT = 50  # 50 api calls per second
MAPS_API_GAP = 1.0 / MAPS_API_RATE_LIMIT  # in seconds

FORMAT_DECIMAL = Decimal('1.00')


class S3Upload(models.Model):
    """
    the resource is uploaded to <bucket> with key <folder>/<uuid>/<filename>
    """
    bucket = models.CharField(max_length=63)
    folder = models.CharField(max_length=150)
    uuid = models.CharField(max_length=50, unique=True)
    filename = models.CharField(max_length=150)
    uploaded = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)

    uploaded_on = models.DateTimeField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)


    def __str__(self):
        return '{} {}'.format(self.uuid, self.filename)

    def key(self):
        path = [comp for comp in [self.folder, self.uuid, self.filename] if comp]
        return '/'.join(path).lower()

    def public_url(self):
        return 'https://{}.s3.amazonaws.com/{}'.format(self.bucket, self.key())

    def read(self):
        if not self.uploaded:
            return None
        key = self.key()
        return s3.download(self.bucket, key)

    def delete_from_s3(self):
        self.uploaded = False
        self.deleted = True
        self.deleted_on = timezone.now()
        self.save()
        s3.delete(self.bucket, self.key())


class PaymentFile(models.Model):
    upload = models.ForeignKey(S3Upload, on_delete=models.CASCADE)
    date = models.DateField()
    name = models.CharField(max_length=50, unique=True)
    summary = models.BooleanField(default=False)
    successful = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


    @staticmethod
    def get_latest(date):
        try:
            return PaymentFile.objects.filter(date=date).latest('updated_on')
        except PaymentFile.DoesNotExist:
            return None

    @staticmethod
    def get_file_name(date, number):
        return 'RIQ76RBI%s.%03d' % (date.strftime('%d%m'), number)

    @staticmethod
    def date_file_count(date):
        return PaymentFile.objects.filter(date=date, summary=False).count()

    @staticmethod
    def today_file_count():
        return PaymentFile.date_file_count(date=timezone.now().date())

    @staticmethod
    def get_next_file_name(date):
        return PaymentFile.get_file_name(date, PaymentFile.today_file_count() + 1)


class GeoLocatedData(models.Model):
    """
    1 degree of latitude ~ 111 Km
    0.01 degree ~ 1.11 Km
    All the locations are from India, and India does not even come close to the Meridian or the Equator.
    So it is safe for us to define vicinities in (lat +- delta, lon +- delta)
    India lies within a 40 deg x 40 deg area, so
    total_max_points = (40 * 100) * (40 * 100) = 16,000,000 ... manageable
    """
    latitude = models.DecimalField(max_digits=5, decimal_places=2)
    longitude = models.DecimalField(max_digits=5, decimal_places=2)

    district = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('latitude', 'longitude')

    def name(self):
        components = [self.district, self.state]
        components = [c.strip() for c in components if c and c.strip()]
        if self.country and self.country.strip():
            if self.country.strip().lower() != 'india' or not components:
                components.append(self.country.strip())

        return '' if not components else ', '.join(components)

    def to_json(self):
        return {
            'name': self.name(),
            'district': self.district,
            'state': self.state,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
        }


class MapsApiUsage(models.Model):
    day = models.DateField(unique=True)
    count = models.PositiveIntegerField(default=0)


class KeyValueStore(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)

    @staticmethod
    def get(key):
        instance = get_or_none(KeyValueStore, key=key)
        return None if not instance else instance.value

    @staticmethod
    def set(key, value):
        instance = get_or_none(KeyValueStore, key=key)
        if not instance:
            KeyValueStore.objects.create(key=key, value=value)
        else:
            KeyValueStore.objects.filter(key=key).update(value=value)


class FakeSmsNumber(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    number = models.CharField(max_length=10, unique=True)


class FakeSms(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    text = models.TextField()
    receiver = models.ForeignKey(FakeSmsNumber, on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)

    @staticmethod
    def send(numbers, text):
        text = None if not text else text.strip()
        if not text:
            raise AssertionError('no text to send')
        clean_numbers = get_cleaned_numbers(numbers)
        fns = [FakeSmsNumber.objects.get_or_create(number=number)[0] for number in clean_numbers]
        FakeSms.objects.bulk_create([FakeSms(text=text, receiver=fn) for fn in fns])

    @staticmethod
    def inbox(number):
        number = get_cleaned_number(number)
        receiver = FakeSmsNumber.objects.get(number=number)
        return list(FakeSms.objects.filter(receiver=receiver).values('created_on', 'text'))


def get_cleaned_numbers(numbers):
    if isinstance(numbers, str):
        numbers = numbers.strip().split(',')

    if not hasattr(numbers, '__iter__'):
        raise AssertionError('invalid phone numbers : %s' % numbers)

    cleaned_numbers = set()
    for number in numbers:
        clean_number = get_cleaned_number(number)
        cleaned_numbers.add(clean_number)
    return cleaned_numbers


def get_cleaned_number(number):
    number = None if not number else number.strip()
    if not number:
        raise AssertionError('invalid number')

    digit_only_number = re.sub(r'[(+ )\-]+', '', number)
    has_only_digits = re.match(r'[0-9]+', digit_only_number)
    if not has_only_digits:
        raise AssertionError('invalid number : %s' % number)

    num_digits = len(digit_only_number)
    if num_digits == 10:
        clean_number = digit_only_number
    elif num_digits == 12 and digit_only_number.startswith('91'):
        clean_number = digit_only_number[2:]
    else:
        raise AssertionError('invalid number : %s' % number)
    return clean_number


def google_reverse_geocode(lat, lon):
    # return from cache if available
    lat = Decimal(lat).quantize(FORMAT_DECIMAL)
    lon = Decimal(lon).quantize(FORMAT_DECIMAL)
    try:
        loc_data = GeoLocatedData.objects.get(latitude=lat, longitude=lon)
        return loc_data.to_json()
    except GeoLocatedData.DoesNotExist:
        pass

    # reject if daily limit met
    api_usage, _ = MapsApiUsage.objects.get_or_create(day=timezone.now().date())
    if api_usage.count > MAPS_API_DAILY_LIMIT:
        raise AssertionError("Google Maps Api limit exceeded")

    # rate limit wait
    last_call_time = GeoLocatedData.objects.all().aggregate(last=Max('created_on')).get('last', None)
    delay = None if not last_call_time else (timezone.now() - last_call_time).total_seconds()
    wait_time = None if delay is None else (1.0 / MAPS_API_RATE_LIMIT - delay)

    if delay:
        pass
    if wait_time is not None and wait_time > 0:
        time.sleep(wait_time)

    # call maps api
    url = MAPS_API_TEMPLATE % (str(lat), str(lon), MAPS_API_KEY)

    data = requests.get(url).json()
    api_usage.count += 1
    api_usage.save()

    # extract state and district from response
    results = data.get('results', None) or []
    to_extract = ['administrative_area_level_2', 'administrative_area_level_1', 'country']
    info = {}
    for result in results:
        types = result.get('types', None) or []
        for key in to_extract:
            if key not in info and key in types:
                address_components = result.get('address_components', None) or []
                value = None
                for component in address_components:
                    comp_types = component.get('types', None) or []
                    if not value and key in comp_types:
                        value = component.get('long_name', None)
                if value:
                    info[key] = value

    district = info.get('administrative_area_level_2', None)
    state = info.get('administrative_area_level_1', None)
    country = info.get('country', None)

    # save the data to cache
    try:
        loc_data = GeoLocatedData.objects.create(latitude=lat, longitude=lon)
    except IntegrityError as e:
        # handle race condition, if somehow this was already created during this time
        if is_unique_constraint_error(e):
            return GeoLocatedData.objects.get(latitude=lat, longitude=lon).to_json()
        else:
            raise
    loc_data.district = district
    loc_data.state = state
    loc_data.country = country
    loc_data.save()
    return loc_data.to_json()
