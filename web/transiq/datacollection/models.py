from __future__ import unicode_literals

from django.db import models


class LoadingPoint(models.Model):
    loading_point = models.CharField(max_length=200, blank=True, null=True)
    material = models.CharField(max_length=200, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_on = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = "Loading point & Material details"

    def __str__(self):
        return "%s, %s" % (self.loading_point, self.material)


class VehicleTempData(models.Model):
    username = models.CharField(max_length=70, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    driver_name = models.CharField(max_length=35, blank=True, null=True, verbose_name='Driver Name')
    owner_name = models.CharField(max_length=35, blank=True, null=True, verbose_name='Owner Name')
    vehicle_type = models.CharField(max_length=70, blank=True, null=True, verbose_name='Type of Vehicle')
    route = models.CharField(max_length=70, blank=True, null=True)
    owner_num_truck = models.CharField(max_length=10, blank=True, null=True,
                                       verbose_name='How many trucks owner have ? ')
    loading_point = models.CharField(max_length=255, blank=True, null=True)
    frequency = models.CharField(max_length=10, blank=True, null=True,
                                 verbose_name='Frequency ( No. of Round trip per month)')
    trip_duration = models.CharField(max_length=10, blank=True, null=True,
                                     verbose_name='Time taken per trip (one side)')
    owner_mobile_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='Owner Mobile Number')
    rate = models.CharField(max_length=100, blank=True, null=True, verbose_name='Rate')
    vehicle_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Vehicle Number')
    load_provider = models.CharField(max_length=70, blank=True, null=True, verbose_name='')
    driver_mobile = models.CharField(max_length=15, blank=True, null=True,
                                     verbose_name=' Who provides load on each side?')
    driver_nature = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nature of driver")
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_on = models.DateTimeField(auto_now_add=False, auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)
    data_provider = models.CharField(max_length=70, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Vehicle Temp Data'

    def __str__(self):
        return self.username


class OthersTempData(models.Model):
    username = models.CharField(max_length=70, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    contact_person_name = models.CharField(max_length=70, blank=True, null=True)
    contact_person_phone = models.CharField(max_length=70, blank=True, null=True)
    contact_person_email = models.EmailField(max_length=70, blank=True, null=True)
    designation = models.CharField(max_length=70, blank=True, null=True)
    route = models.CharField(max_length=70, blank=True, null=True)
    number_of_truck = models.CharField(max_length=70, blank=True, null=True)
    other_point_to_be_noted = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_on = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = 'Others'

    def __str__(self):
        return '%s  %s' % (self.company_name, self.datetime)


class TransporterTempData(models.Model):
    username = models.CharField(max_length=70, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=35, blank=True, null=True)
    email = models.EmailField(max_length=70, blank=True, null=True)
    designation = models.CharField(max_length=70, blank=True, null=True)
    route = models.CharField(max_length=200, blank=True, null=True)
    number_of_truck_owned = models.CharField(max_length=35, blank=True, null=True)
    number_booking_done_daily = models.CharField(max_length=35, blank=True, null=True)
    number_of_truck_taken_from_market = models.CharField(max_length=35, blank=True, null=True)
    gps_fitted_vehicle = models.CharField(max_length=35, blank=True, null=True)
    contact_number_of_traffic_person = models.CharField(max_length=35, blank=True, null=True)
    any_reference = models.CharField(max_length=200, blank=True, null=True)
    other_point_to_noted = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_on = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = 'Transporter'

    def __str__(self):
        return '%s %s' % (self.company_name, self.datetime)


class BrokerTempData(models.Model):
    username = models.CharField(max_length=35, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=70, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    number_of_truck_booked_daily = models.CharField(max_length=35, blank=True, null=True)
    owner_base = models.CharField(max_length=35, blank=True, null=True)
    number_of_associated_transporter = models.CharField(max_length=35, blank=True, null=True)
    other_point_to_be_noted = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_on = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = 'Broker'

    def __str__(self):
        return '%s %s' % (self.name, self.datetime)


class OwnerTempData(models.Model):
    username = models.CharField(max_length=35, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    company_name = models.CharField(max_length=35, blank=True, null=True)
    owner_name = models.CharField(max_length=35, blank=True, null=True)
    contact_person_name = models.CharField(max_length=35, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=70, blank=True, null=True)
    designation = models.CharField(max_length=35, blank=True, null=True)
    route = models.CharField(max_length=70, blank=True, null=True)
    rate = models.CharField(max_length=70, blank=True, null=True)
    any_reference = models.CharField(max_length=70, blank=True, null=True)
    other_point_to_be_noted = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_on = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = 'Owner'

    def __str__(self):
        return '%s %s %s' % (self.company_name, self.owner_name, self.datetime)


class BookingAgent(models.Model):
    username = models.CharField(max_length=35, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=35, blank=True, null=True)
    phone = models.CharField(max_length=35, blank=True, null=True)
    number_of_truck = models.CharField(max_length=35, blank=True, null=True)
    route = models.CharField(max_length=35, blank=True, null=True)
    other_point_to_be_noted = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_on = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = 'Booking Agent'

    def __str__(self):
        return '%s %s' % (self.name, self.datetime)
