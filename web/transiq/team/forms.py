from django import forms

from team.models import ManualBooking


class FullBookingPageForm(forms.ModelForm):
    source_office = forms.IntegerField()
    destination_office = forms.IntegerField()
    customer_placed_order = forms.IntegerField()
    customer_to_be_billed = forms.IntegerField(required=False)
    truck_owner_id = forms.IntegerField(required=False)
    supplier_id = forms.IntegerField()
    truck_driver_id = forms.IntegerField()
    vehicle_category_id = forms.IntegerField()
    gst_liability = forms.CharField()
    number_of_lr = forms.IntegerField()
    vehicle_number = forms.CharField()
    from_city = forms.IntegerField()
    to_city = forms.IntegerField()
    billing_type = forms.CharField()
    refund = forms.IntegerField()
    supplier_charged_weight = forms.IntegerField()
    supplier_rate = forms.IntegerField()
    charged_weight = forms.IntegerField()
    party_rate = forms.IntegerField()
    loaded_weight = forms.IntegerField()
    total_amount_to_party = forms.IntegerField(required=False)
    shipment_datetime = forms.CharField()


    class Meta:
        model = ManualBooking
        fields = ()
