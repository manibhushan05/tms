import sys
import requests

from .defaults import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ENV = 'stage'

ALLOWED_HOSTS = ['www.stage.aaho.in', 'stage.aaho.in', '127.0.0.1', 'StageELB2-1730746449.ap-south-1.elb.amazonaws.com']

ADMINS = (
    ('Mani Bhushan Kumar', 'mani@aaho.in'),
    ('Ravindra Kulkarni', 'ravindra@aaho.in')
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'aahodb',
        'USER': 'aaho',
        'PASSWORD': 'whvc.1900',
        'HOST': 'aahodbstage.cow111xuzv8n.ap-south-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}

# use celery for async tasks
IS_TEST = 'test' in sys.argv
ENABLE_CELERY = True
CELERY_SEND_TASK_ERROR_EMAILS = True

# send mail
ENABLE_MAIL = False

# send sms
ENABLE_SMS = False

# send notification
ENABLE_NOTIFICATION = False

# secure proxy SSL header and secure cookies
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_API_TEST_CLIENT = True
# session expire at browser close
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_VERBOSE = 2
TEST_OUTPUT_DESCRIPTIONS = True
TEST_OUTPUT_DIR = 'xml-test-output'

S3_REPORTS_BUCKET = 'aahodocumentstest'

EC2_PRIVATE_IP = None
try:
    EC2_PRIVATE_IP = requests.get(
        'http://169.254.169.254/latest/meta-data/local-ipv4',
        timeout=0.01).text
except requests.exceptions.RequestException:
    pass

if EC2_PRIVATE_IP:
    ALLOWED_HOSTS.append(EC2_PRIVATE_IP)

CELERY_BEAT_SCHEDULE = {
    'tempogo-update-vehicles': {
        'task': 'team.tasks.update_tempogo_devices',
        'schedule': crontab(minute=0, hour='*/3'),
    },
    'tempogo-update-vehicles-locations': {
        'task': 'team.tasks.update_tempogo_devices_locations',
        'schedule': crontab(minute='*/15'),
    },
    'booking-status-exprired-check': {
        'task': 'restapi.tasks.send_booking_status_expired_notifications',
        'schedule': crontab(minute=0, hour=0),
    },
    'bharat-gps-update-vehicles-locations': {
        'task': 'team.tasks.update_bharat_gps_tracker_locations',
        'schedule': crontab(minute='*/30'),
    },
}
