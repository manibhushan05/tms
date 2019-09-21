from django.db import models
from django.contrib.auth.models import User
from utils.models import City, Bank, TaxationID, Address


class MyBrok(models.Model):
    name = models.OneToOneField(User, blank=True, null=True)
    address = models.OneToOneField(Address, blank=True, null=True)
    route = models.CharField(max_length=400, null=True)
    city = models.ForeignKey(City, related_name='broker_city', null=True)
    pan = models.CharField(max_length=15, blank=True, null=True)
    id_proof = models.CharField(max_length=70, blank=True)
    account_details = models.OneToOneField(Bank, blank=True, null=True)
    taxation_details = models.OneToOneField(TaxationID, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = "Broker Basic Info"

    def __str__(self):
        return str(self.name)

    def to_json(self):
        data = {}
        if self.name:
            data['name'] = self.name.profile.name
            data['phone'] = self.name.profile.phone
        return data
