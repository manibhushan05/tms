"""
Django settings for transiq project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import os
import re

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import sys

from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7qvy%5z_-1ry_tl@pzx=)#+@r351w($b6bk4+wokqr^4bu!3)f'

ADMINS = (
    ('Mani Bhushan Kumar', 'mani@aaho.in'),
    ('Harsh Bhageria', 'harsh@aaho.in'),
    ('TPA', 'tp.ananth@aaho.in'),
    ('Ravindra Kulkarni', 'ravindra@aaho.in')
)

MANAGERS = (
    ('Ravindra Kulkarni', 'ravindra@aaho.in'),
    ('Mani Bhushan Kumar', 'mani@aaho.in'),
)
# Application definition

AAHO_APPS = [
    'broker',
    'datacollection',
    'enquiry',
    'index',
    'owner',
    'transporter',
    'driver',
    'customer',
    'fms',
    'ios',
    'api',
    'authentication',
    'sme',
    'team',
    'transaction',
    'utils',
    'employee',
    'report',
    'fileupload',
    'supplier',
    'mobile',
    'notification',
    'restapi'
]

INSTALLED_APPS = ['django.contrib.admin',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.messages',
                  'django.contrib.staticfiles',
                  'django.contrib.humanize',
                  'django.contrib.postgres',
                  'storages',
                  'rest_framework',
                  'django_filters',
                  'simple_history',
                  'fcm_django',
                  'rangefilter',
                  'rest_framework.authtoken',

                  ] + AAHO_APPS

GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}

FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": "AAAA0ogm9XI:APA91bG4rCmEYAUIgZ3LFm3TK0hZC6aRxANqQ7zl3t5EZ-OQsvn3vqx0dRBkutA-165MSyYi_CwF0Zwib2UoAXyqR0Eg8DjBH2_Lt6yxPT5nlSfpM6D2FZpPrHPXOzxP06W51_wpL8dZ"
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'transiq.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'transiq.wsgi.application'

STATICFILES_DIRS = (BASE_DIR + '/static/',)
# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8, }
     },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

# STATIC_URL = BASE_DIR+'/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATIC_URL = '/static/'

# AWS KEYS
AWS_ACCESS_KEY_ID = 'AKIAJCNWARSXHGOSFVFA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_SNS_REGION_NAME = 'ap-south-1'
ANDROID_PLATFORM_APPLICATION_ARN = 'arn:aws:sns:ap-south-1:911954495075:app/GCM/AahoSales'
IOS_PLATFORM_APPLICATION_ARN = ''

# AUTH_USER_MODEL = 'authentication.User'
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'info@aaho.in'
EMAIL_HOST_PASSWORD = 'aaho1234'
EMAIL_PORT = 587
ASANA_ACCESS_TOKEN = '0/646832b8e784f23faf9355008c42395e'

#  celery settings
BROKER_URL = [
    'amqp://aaho:aahoMQ1.12017@localhost:5672/aaho'
]

CELERY_BROKER_URL = BROKER_URL
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_RESULT_PERSISTENT = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_ENABLE_UTC = True


TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',

    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'restapi.pagination.CustomeDatatablesPaginator',
    'PAGE_SIZE': 25
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console'],
        },
    }
}

APPEND_SLASH = True

# Making cookie http only
# SESSION_COOKIE_PATH = '/;HttpOnly'
# CSRF_COOKIE_SECURE = True
