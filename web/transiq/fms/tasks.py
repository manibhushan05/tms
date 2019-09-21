import datetime
from django.conf import settings

from transiq.celery import app
from api.sms import send_sms
from fcm_django.models import FCMDevice
from django.db.models import Q
from time import sleep


@app.task
def send_sms_to_suppliers(mobiles, template):
    if settings.ENABLE_SMS:
        send_sms(mobiles, template)
    else:
        msg = "SMS sent to: {} Body: {}".format(mobiles, template)
        print(msg)


@app.task(ignore_result=True)
def send_app_notification(all_devices, title, body, data=None):
    return
    from notification.models import MobileDevice
    all_devices = MobileDevice.objects.filter(id__in=all_devices)
    if not all_devices:
        print('No Devices found for notification')
        return
    if settings.ENABLE_NOTIFICATION:
        device = FCMDevice()
        for each_user in all_devices:
            # print(each_user.device_id)
            # print(each_user.token)
            device.device_id = each_user.device_id
            device.registration_id = each_user.token
            device.save()
            device.send_message(data=data)
    else:
        print('Notification sent to Users:')
        for each_user in all_devices:
            msg = "Device Id: {} Token: {} Title: {} Body: {} ".format(each_user.device_id, each_user.token, title,
                                                                       body)
            print(msg)


@app.task(ignore_result=True)
def check_lapsed_load_status():
    from fms.models import Requirement
    print('task initiated')
    q_objects = Q()
    present = datetime.datetime.now()
    q_objects |= Q(**{'req_status': 'open'})
    q_objects |= Q(**{'req_status': 'unverified'})
    loads = Requirement.objects.filter(q_objects).exclude(deleted=True)
    loads_with_todate = loads.filter(to_shipment_date__isnull=False, to_shipment_date__lt=present.date())
    loads_without_todate = loads.filter(to_shipment_date__isnull=True, from_shipment_date__lt=present.date())
    loads = loads_with_todate.union(loads_without_todate)
    for each_load in loads:
        print('load lapsed')
        each_load.req_status = 'lapsed'
        each_load.updated_on = present
        each_load.save(update_fields=['req_status', 'updated_on'])
