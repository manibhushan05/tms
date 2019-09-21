import sys

from .defaults import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#DEBUG = False

ENV = 'local'
ALLOWED_HOSTS = ['*']

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
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
# use celery for async tasks

# IS_TEST = 'test' in sys.argv
ENABLE_CELERY = False
CELERY_SEND_TASK_ERROR_EMAILS = True

# send mail

ENABLE_MAIL = False

# send sms
ENABLE_SMS = False

# send notification
ENABLE_NOTIFICATION = False

WSGI_APPLICATION = 'transiq.wsgi.application'

TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_VERBOSE = 2
TEST_OUTPUT_DESCRIPTIONS = False
TEST_OUTPUT_DIR = 'xml-test-output'

S3_REPORTS_BUCKET = 'aahodocumentstest'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/aaho.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django_request.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['default'],
        'level': 'DEBUG'
    },
    'loggers': {
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

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
