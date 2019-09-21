from __future__ import absolute_import, print_function

from django.forms import ModelForm

from utils.models import VehicleBodyCategory, VehicleCategory, City


class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ['name', 'code', 'pin']
