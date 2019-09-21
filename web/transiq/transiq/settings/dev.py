import sys

from .defaults import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ENV = 'dev'

ALLOWED_HOSTS = ['www.dev.aaho.in', 'dev.aaho.in','127.0.0.1']

ADMINS = (
    ('Mani Bhushan Kumar', 'mani@aaho.in'),
    ('Ravindra Kulkarni','ravindra@aaho.in')
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': 'aahodb',
        'NAME': 'aahodbdev',
        # 'NAME': 'dev_aahodb',
        'USER': 'aaho',
        'PASSWORD': 'whvc.1900',
        # 'HOST': 'aahodbdev.cow111xuzv8n.ap-south-1.rds.amazonaws.com',
        'HOST': 'aahodbstage.cow111xuzv8n.ap-south-1.rds.amazonaws.com',
        # 'HOST': 'aaho.c7be1yonlwr1.ap-southeast-1.rds.amazonaws.com',
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

CELERY_BEAT_SCHEDULE = {
    'check-lapsed-load-status': {
        'task': 'fms.tasks.check_lapsed_load_status',
        'schedule': crontab(minute=0, hour=0),
    },
    'booking-status-exprired-check': {
        'task': 'restapi.tasks.send_booking_status_expired_notifications',
        'schedule': crontab(minute=0, hour=0),
    },
}

