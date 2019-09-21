# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import IntegrityError

from api.decorators import authenticated_user
from api.helper import json_response
from notification.form import MobileDeviceForm
from notification.models import MobileDevice
from api.decorators import api_post
import datetime


def get_all_mobile_devices(request):
    mobiledevices = MobileDevice.objects.all().exclude(deleted=True)
    if not mobiledevices:
        return json_response({'status': 'failure', 'msg': 'No devices found', 'data': {}})
    return json_response({'status': 'success', 'msg': 'mobile device data', 'data': get_mobiledevice_data(mobiledevices)})


def get_mobiledevice_data(mobiledevices):
    app_data = []
    for ver in mobiledevices:
        app_data.append({
            'id': ver.id,
            'username': ver.user.username,
            'active': ver.active,
            'token': ver.token,
            'device_id': ver.device_id,
            'created_on': str(ver.created_on),
            'updated_on': str(ver.updated_on)
        })
    data = {
        'mobile_devices': app_data
    }
    return data

@authenticated_user
@api_post
def create_notification_device(request):
    # data = json.loads(request.body)
    # token = data['token']
    # device_id = data['device_id']
    token = request.data.get('token')
    device_id = request.data.get('device_id')
    app = request.data.get('app')

    if not token:
        return json_response({'status': 'failure', 'msg': 'Pls enter all * fields'})
    if not device_id:
        return json_response({'status': 'failure', 'msg': 'Pls enter all * fields'})
    if not app:
        return json_response({'status': 'failure', 'msg': 'Pls enter all * fields'})
    # form = MobileDeviceForm(request.data)
    # if not form.is_valid():
    #     return json_response({'status': 'failure', 'msg': 'Pls enter all * fields'})
    try:
        if not MobileDevice.objects.filter(device_id=device_id, user=request.user).exists():
            print('creating mobile device entry')
            MobileDevice.objects.create(
                user=request.user,
                app=app,
                active=True,
                token=token,
                device_id=device_id,
                changed_by=request.user
            )
        else:
            print('updating mobile device entry')
            MobileDevice.objects.filter(device_id=device_id, user=request.user).update(
                # user=request.user,
                token=token,
                changed_by=request.user,
                updated_on=datetime.datetime.now()
            )
        return json_response({'status': 'success', 'msg': 'Token Successfully saved'})

    except IntegrityError:
        return json_response({'status': 'failure', 'msg': 'Token could not be saved'})
