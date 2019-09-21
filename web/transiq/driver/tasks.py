from datetime import timedelta

from django.conf import settings
from django.core.mail.message import EmailMessage
from django.template.base import Template
from django.template.context import Context
from django.utils import timezone

from api.sms import send_sms
from driver.helper import update_gps_devices
from driver.models import GPSLogNew, DriverAppUser
from owner.models import Vehicle
from transaction.models import VehicleAllocated
from transiq.celery import app


SMS_NOTIFY_TIME_GAP = 12  # hours
ADMIN_NOTIFY_TIME_GAP = 24  # hours


SMS_TEMPLATE = """
Hi {name}, Your device associated with vehicle {vehicle_number} has not been sending GPS data for last {last_update_gap} hrs.
Please make sure that GPS is running on the device.""".strip()


# run every hour
@app.task(ignore_result=True)
def notify_inactive_driver_apps():
    engaged_vehicle_ids = set(VehicleAllocated.objects.values_list('vehicle_number_id', flat=True))
    driver_ids = set(Vehicle.objects.filter(id__in=engaged_vehicle_ids, driver_app_user__isnull=False
                                      ).values_list('driver_app_user_id', flat=True))
    recent_gps_data = GPSLogNew.objects.filter(driver__in=driver_ids).latest('datetime')
    notify_time = timezone.now() - timedelta(hours=SMS_NOTIFY_TIME_GAP)
    inactive_drivers_data = dict([(g.driver_id, g.datetime) for g in recent_gps_data if g.datetime <= notify_time])

    vehicles = Vehicle.objects.filter(driver_id__in=inactive_drivers_data.keys()).select_related('driver_app_user')

    to_notify_vehicles = []
    notify_after = timezone.now() - timedelta(hours=SMS_NOTIFY_TIME_GAP)
    for v in vehicles:
        notif_time = v.driver_app_user.inactive_sms_sent_at
        if not notif_time:
            to_notify_vehicles.append(v)
        if notif_time < notify_after:
            to_notify_vehicles.append(v)

    if not to_notify_vehicles:
        return

    sms_data = [{
        'driver_id': v.driver_app_user_id,
        'phone': v.driver_app_user.driver_number,
        'name': v.driver_app_user.driver_name,
        'vehicle_number': v.vehicle_number,
        'last_update_gap': (timezone.now() - inactive_drivers_data[v.driver_app_user_id]).total_seconds() / 3600,
    } for v in to_notify_vehicles]

    sms_text = [(sms_data['driver_id'], sms_data['phone'], SMS_TEMPLATE.format(data)) for data in sms_data]
    for driver_id, phone, text in sms_text:
        send_sms(phone, text)
        DriverAppUser.objects.filter(driver_id=driver_id).update(inactive_sms_sent_at=timezone.now())
        print ('[notify_inactive_driver_apps] SMS sent to ' + phone + ': ' + sms_text)


MAIL_TEMPLATE = """

Following Driver App Users have been inactive for a while:

{% for d in inactive_drivers %}
- {{ d.name }} ({{ d.phone }}), last update {{ d.last_update_gap }} hours ago
{% endfor %}

""".strip()

NOTIFY_EMAILS = ['mani@aaho.in', 'shobhit.v87@gmail.com ', 'harsh@aaho.in']


# run daily
@app.task(ignore_result=True)
def notify_admins_about_inactive_driver_apps():
    recent_gps_data = GPSLogNew.objects.filter(driver__isnull=False, driver__number_verified=True).latest('datetime')
    notify_time = timezone.now() - timedelta(hours=ADMIN_NOTIFY_TIME_GAP)
    inactive_drivers_data = dict([(g.driver_id, g.datetime) for g in recent_gps_data if g.datetime <= notify_time])

    drivers = DriverAppUser.objects.filter(id__in=inactive_drivers_data.keys())

    inactive_data = [{
        'phone': d.driver_number,
        'name': d.driver_name,
        'last_update_gap': (timezone.now() - inactive_drivers_data[d.id]).total_seconds() / 3600,
    } for d in drivers]

    if not inactive_data:
        return

    subject = '[Aaho] Daily Inactive Driver App Update'
    body = Template(MAIL_TEMPLATE).render(Context({'inactive_drivers': inactive_data}))

    email = EmailMessage(subject, body, to=NOTIFY_EMAILS)
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()
    print ('[notify_admins_about_inactive_driver_apps] Mail sent:\n' + body)


@app.task(ignore_result=True)
def test_celery():
    print ('YEY!!!!')


@app.task(ignore_result=True)
def update_gps_data():
    update_gps_devices()





