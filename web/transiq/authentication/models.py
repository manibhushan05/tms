from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from utils.models import City


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    contact_person_name = models.CharField(max_length=70, blank=True, null=True)
    contact_person_phone = models.CharField(max_length=70, blank=True, null=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    alternate_phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    alternate_email = models.EmailField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    organization = models.CharField(max_length=100, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['user']
        verbose_name = 'user'
        verbose_name_plural = 'Profile'

    # def clean(self):
    #     if self.phone and Profile.objects.filter(Q(phone__icontains=self.phone)).exclude(user=self.user).exists():
    #         raise ValidationError('Phone already exist with {}'.format(', '.join(
    #             Profile.objects.filter(Q(phone__icontains=self.phone)).exclude(
    #                 user=self.user).values_list('name', flat=True))))

    def save(self, *args, **kwargs):
        if not self.user.sme_set.exists():
            self.name = None if not self.name else self.name.title()
        self.contact_person_name = None if not self.contact_person_name else self.contact_person_name.title()
        return super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return "user@%s, phone@%s" % (str(self.user), self.phone)


class ServerErrorMessage(models.Model):
    error_type = models.CharField(max_length=10, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=35, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_on = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "Error Type: %s, Message: %s" % (self.error_type, self.message)
