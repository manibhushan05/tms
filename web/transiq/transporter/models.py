from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from utils.models import Address, IDDetails, Bank, TaxationID


class Transporter(models.Model):
    name = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, blank=True, null=True, on_delete=models.CASCADE)
    # id_proof = models.ManyToManyField(IDDetails, blank=True)
    account_details = models.ForeignKey(Bank, blank=True, null=True, on_delete=models.CASCADE)
    taxation_details = models.ForeignKey(TaxationID, blank=True, null=True, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Transporter\'s Info"

    def __str__(self):
        return self.name
