from __future__ import unicode_literals

from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from numpy import random

EXPIRY_TIME = timedelta(minutes=15)

OTP_CHARS = '0123456789'


def new_otp(num_digits):
    max_index = len(OTP_CHARS) - 1
    return ''.join(OTP_CHARS[random.randint(0, max_index)] for _ in range(num_digits))


class PhoneOTP(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    expires_at = models.DateTimeField()
    otp = models.CharField(max_length=8)

    @staticmethod
    def verify(phone, otp):
        try:
            otp_instance = PhoneOTP.objects.get(phone=phone.strip())
            if otp_instance.expires_at < timezone.now():
                return False
            if otp_instance.otp != otp:
                return False
            return True
        except (PhoneOTP.DoesNotExist, PhoneOTP.MultipleObjectsReturned) as e:
            return False

    @staticmethod
    def generate(phone):
        phone = phone.strip()
        try:
            otp_instance = PhoneOTP.objects.get(phone=phone)
            if otp_instance.expires_at < timezone.now():
                otp_instance.otp = new_otp(6)
        except PhoneOTP.DoesNotExist:
            otp_instance = PhoneOTP(phone=phone)
            otp_instance.otp = new_otp(6)

        otp_instance.expires_at = (timezone.now() + EXPIRY_TIME)
        otp_instance.save()
        return otp_instance.otp


class EmailOTP(models.Model):
    email = models.EmailField(max_length=50, unique=True)
    expires_at = models.DateTimeField()
    otp = models.CharField(max_length=8)

    @staticmethod
    def verify(email, otp):
        try:
            otp_instance = EmailOTP.objects.get(email=email.strip())
            if otp_instance.expires_at < timezone.now():
                return False
            if otp_instance.otp != otp:
                return False
            return True
        except (EmailOTP.DoesNotExist, EmailOTP.MultipleObjectsReturned) as e:
            return False

    @staticmethod
    def generate(email):
        email = email.strip()
        try:
            otp_instance = EmailOTP.objects.get(email=email)
            if otp_instance.expires_at < timezone.now():
                otp_instance.otp = new_otp(6)
        except EmailOTP.DoesNotExist:
            otp_instance = EmailOTP(email=email)
            otp_instance.otp = new_otp(6)
        otp_instance.expires_at = (timezone.now() + EXPIRY_TIME)
        otp_instance.save()
        return otp_instance.otp


class Route(models.Model):
    source = models.CharField(max_length=70, blank=True, null=True)
    destination = models.CharField(max_length=70, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('source', 'destination')

    def save(self, *args, **kwargs):
        self.source = self.source.upper()
        self.destination = self.destination.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s - %s' % (self.source, self.destination)


class SubRoute(models.Model):
    route = models.ForeignKey(Route, null=True, related_name='index_route_rate', on_delete=models.CASCADE)
    loading_point = models.CharField(max_length=70, blank=True, null=True)
    unloading_point = models.CharField(max_length=70, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('loading_point', 'unloading_point')

    def save(self, *args, **kwargs):
        self.loading_point = self.loading_point.upper()
        self.unloading_point = self.unloading_point.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s - %s' % (self.loading_point, self.unloading_point)


class RouteFreight(models.Model):
    route = models.ForeignKey(SubRoute, null=True, related_name='index_sub_route_rate', on_delete=models.CASCADE)
    freight = models.CharField(max_length=100,null=True, blank=True, help_text='Frieght Per Ton')
    material = models.CharField(max_length=300, blank=True, null=True)
    truck_type = models.CharField(max_length=100, blank=True, null=True)
    datetime = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=300, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, related_name='index_route_freight', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.material = self.material.upper()
        super().save(*args, **kwargs)
