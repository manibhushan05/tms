from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models

from utils.models import City, VehicleCategory


class DailyRateEnquiry(models.Model):
    rate_update_source = (
        ('transporter', 'Transporter'),
        ('supplier', 'Broker'),
        ('traffic_person', 'Traffic Person'),
    )
    name = models.CharField(max_length=70, blank=True, null=True)
    phone = models.CharField(max_length=13, validators=[MinLengthValidator(10)], blank=True, null=True)
    source_of_information = models.CharField(max_length=35, choices=rate_update_source, blank=True, null=True)
    type_of_vehicle = models.ForeignKey(VehicleCategory, blank=True, null=True, on_delete=models.CASCADE)
    loading_point = models.CharField(max_length=200, blank=True, null=True)
    loading_city = models.ForeignKey(City, related_name='loading_city', on_delete=models.CASCADE)
    unloading_point = models.CharField(max_length=200, blank=True, null=True)
    unloading_city = models.ForeignKey(City, related_name='unloading_city', on_delete=models.CASCADE)
    material = models.CharField(max_length=150, blank=True, null=True)
    weight = models.CharField(max_length=35, blank=True, null=True)
    rate = models.CharField(max_length=10, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True, verbose_name="datetime")
    number_of_truck = models.CharField(max_length=5, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="daily_rate_enquiry_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="daily_rate_enquiry_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Daily Rate Enquiry Record"

    def __str__(self):
        return '%s , %s , %s' % (self.name, self.phone, self.created_on)


class EnquiryForm(models.Model):
    name = models.CharField(max_length=70)
    phone = models.CharField(max_length=17, validators=[MinLengthValidator(10)], blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    type_of_vehicle = models.ForeignKey(VehicleCategory, blank=True, null=True, on_delete=models.CASCADE)
    loading_point = models.CharField(max_length=200, blank=True, null=True)
    loading_city = models.ForeignKey(City, related_name='enquiry_loading_city', on_delete=models.CASCADE)
    unloading_point = models.CharField(max_length=200, blank=True, null=True)
    unloading_city = models.ForeignKey(City, related_name='enquiry_unloading_city', on_delete=models.CASCADE)
    material = models.CharField(max_length=200, blank=True, null=True)
    weight = models.CharField(max_length=35, blank=True, null=True)
    date = models.DateField()
    enquiry_date = models.DateField(auto_now_add=True, auto_now=False)
    comment = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="enquiry_form_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="enquiry_form_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "General Enquiry Record"

    def __str__(self):
        return '%s , %s , %s' % (self.name, self.phone, self.created_on)


class ContactUsLandingPage(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="contact_us_landing_page_created_by")
    changed_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="contact_us_landing_page_changed_by")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Contact Us Landing Page"

    def __str__(self):
        return "%s, %s, %s" % (self.name, self.phone, self.created_on)
