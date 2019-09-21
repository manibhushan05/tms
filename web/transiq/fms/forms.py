from django import forms

from sme.models import Sme
from .models import Requirement, MobileAppVersions


class RequirementForm(forms.ModelForm):
    tonnage = forms.IntegerField(max_value=99999, required=False)
    no_of_vehicles = forms.IntegerField(max_value=999, required=False)
    rate = forms.IntegerField(min_value=1, max_value=99999, required=False)
    client_id = forms.IntegerField()
    from_city_id = forms.IntegerField()
    to_city_id = forms.IntegerField()
    aaho_office_id = forms.IntegerField()
    vehicle_type_id = forms.IntegerField(required=False)
    material = forms.CharField(max_length=25)
    from_shipment_date = forms.CharField(max_length=25)

    class Meta:
        model = Requirement
        fields = ('tonnage', 'no_of_vehicles', 'rate', 'client_id', 'from_city_id',
                  'to_city_id', 'vehicle_type_id', 'material', 'from_shipment_date', 'aaho_office_id')


class RequirementGetForm(forms.ModelForm):
    requirement_id = forms.IntegerField()

    class Meta:
        model = Requirement
        fields = ('requirement_id',)


class MobileAppVersionsForm(forms.ModelForm):
    app_platform = forms.CharField(max_length=15)
    app_name = forms.CharField(max_length=15)
    app_version = forms.CharField(max_length=15)

    class Meta:
        model = MobileAppVersions
        fields = ('app_platform', 'app_name', 'app_version')
