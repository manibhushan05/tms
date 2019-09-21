import json

import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import VehicleTempData, OthersTempData


@csrf_exempt
def vehicle_temp_data(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))
        VehicleTempData.objects.create(
            username=data['username'],
            driver_name=data['driverName'],
            owner_name=data['ownerName'],
            vehicle_type=data['vehicleType'],
            route=data['route'],
            owner_num_truck=data['numOfTruck'],
            frequency=data['frequency'],
            trip_duration=data['tripDuration'],
            owner_mobile_number=data['ownerMobile'],
            rate=data['rate'],
            vehicle_number=data['vehicleNumber'],
            load_provider=data['loadProvider'],
            driver_mobile=data['driverContact'],
            driver_nature=data['driverNature'],
            data_provider=data['ownerDriver'],
            datetime=data['date'],
        )
    return HttpResponse("success")


@csrf_exempt
def others_temp_data(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))
        OthersTempData.objects.create(
            datetime=str(data['date']) + ' ' + str(data['time']),
            company_name=data['company_name'],
            contact_person_name=data['person_name'],
            contact_person_phone=data['phone'],
            contact_person_email=data['email'],
            designation=data['designation'],
            route=data['route'],
            number_of_truck=data['number_of_truck'],
            other_point_to_be_noted=data['other_point'],
        )
    return HttpResponse('success')


def jeevansaathi():
    session = requests.Session()
    data = {
        'email': 'maniaug05@gmail.com',
        'password': 'whvc.1900',
        'remember': '1'
    }
    login=session.post(
        url='https://www.jeevansathi.com/api/v1/api/login?&captcha=0&fromPc=1&rememberme=1&g_recaptcha_response=undefined&secureSite=1',
        data=data)
    print (login.status_code)
