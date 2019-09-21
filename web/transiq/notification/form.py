
from django import forms

from notification.models import MobileDevice


class MobileDeviceForm(forms.ModelForm):
    token = forms.CharField(max_length=500)
    device_id = forms.CharField(max_length=100)
    app = forms.CharField(max_length=15)

    class Meta:
        model = MobileDevice
        fields = ['token', 'app', 'device_id']
