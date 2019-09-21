from rest_framework import status
from rest_framework.response import Response

from api.helper import json_success_response
from enquiry.serializers import ContactUsLandingPageSerializer
from .models import DailyRateEnquiry


def daily_rate_enquiry_form(request):
    if request.method == 'POST':
        form = DailyRateEnquiry(
            name=request.POST.get("")
        )
        form.save()


def contact_us_landing_page(request):
    data = {
        'name': request.POST.get('name'),
        'phone': request.POST.get('phone'),
        'email': request.POST.get('email'),
        'message': request.POST.get('message'),
    }
    serializer = ContactUsLandingPageSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return json_success_response(msg="Ok")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
