# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords

from fms.models import ANDROID_APPS


class MobileDevice(models.Model):
    user = models.ForeignKey(User, related_name='notification_devices', on_delete=models.CASCADE)
    app = models.CharField(max_length=2, choices=ANDROID_APPS, default='AC')
    token = models.CharField(max_length=500, unique=True)
    device_id = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, related_name="mobile_device_changed_by", null=True, blank=True,
                                   limit_choices_to={'is_staff': True},
                                   on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, related_name="mobile_device_created_by",
                                   limit_choices_to={'is_staff': True},
                                   on_delete=models.CASCADE)

    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.deleted_on = datetime.now()
        super().save()

    def __str__(self):
        return self.device_id
