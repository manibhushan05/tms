import sys
import requests

from .defaults import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ENV = 'prod'

ALLOWED_HOSTS = ['aaho.in', 'www.aaho.in', '127.0.0.1', 'ProdELB2-1257897086.ap-south-1.elb.amazonaws.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'aahodb',
        'USER': 'aaho',
        'PASSWORD': 'whvc.1900',
        'HOST': 'aahodbprod.cow111xuzv8n.ap-south-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}

# use celery for async tasks
IS_TEST = 'test' in sys.argv
ENABLE_CELERY = True
CELERY_SEND_TASK_ERROR_EMAILS = True

# send mail
ENABLE_MAIL = True

# send sms
ENABLE_SMS = True

# send notification
ENABLE_NOTIFICATION = True

# secure proxy SSL header and secure cookies
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_API_TEST_CLIENT = True
# session expire at browser close
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

S3_REPORTS_BUCKET = 'aahodocuments'

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
    'gps-device-update-tempgo': {
        'task': 'driver.tasks.update_gps_data',
        'schedule': crontab(minute='*/15'),
    },
    # 'mail-admins-about-pending-pod': {
    #     'task': 'team.tasks.notify_admins_about_pending_pod',
    #     'schedule': crontab(hour=2, minute=28, day_of_week='mon'),
    # },
    # 'mail-admins-about-partial-tbb': {
    #     'task': 'team.tasks.notify_weekly_partial_tbb',
    #     'schedule': crontab(hour=2, minute=24, day_of_week='mon'),
    # },
    'mail-notify-excess-outward-payment': {
        'task': 'team.tasks.notify_excess_outward_payment',
        'schedule': crontab(hour=2, minute=11, day_of_week='mon'),
    },
    # 'mail-admins-about-to-pay-payments': {
    #     'task': 'team.tasks.notify_admins_about_to_pay_booking',
    #     'schedule': crontab(hour=2, minute=28, day_of_week='mon'),
    # },
    'notify_invoice_customers_email': {
        'task': 'team.tasks.notify_invoice_customers_email',
        'schedule': crontab(hour=2, minute=28),
    },
    # 'mail-admins-about-outward-payments': {
    #     'task': 'team.tasks.notify_outward_payment_status',
    #     'schedule': crontab(hour=2, minute=28, day_of_week='mon'),
    # },
    'notify_customers_dispatched_shipment_email': {
        'task': 'team.tasks.notify_customers_dispatched_shipment_email',
        'schedule': crontab(hour=2, minute=28),
    },
    # 'mail-admins-pod-recieved-invoice-unraised': {
    #     'task': 'team.tasks.notify_pod_received_invoice_not_raised',
    #     'schedule': crontab(hour=2, minute=35, day_of_week='mon'),
    # },
    'tempogo-update-vehicles-locations': {
        'task': 'team.tasks.update_tempogo_gps_locations',
        'schedule': crontab(minute='*/15'),
    },
    # 'secugps-update-vehicles-locations': {
    #     'task': 'team.tasks.update_secugps_locations',
    #     'schedule': crontab(minute='*/15'),
    # },
    # 'bharat-gps-update-vehicles-locations': {
    #     'task': 'team.tasks.update_bharat_gps_tracker_locations',
    #     'schedule': crontab(minute='*/30'),
    # },
    # 'mahindra-digsense-update-vehicles-locations': {
    #     'task': 'team.tasks.update_mahindra_digisense_locations',
    #     'schedule': crontab(minute='*/15'),
    # },
    'daily-last-day-payments-account': {
        'task': 'team.tasks.email_accounts_last_day_payments',
        'schedule': crontab(hour=2, minute=30),
    },
    'daily-daily-sales-report': {
        'task': 'team.tasks.notify_daily_sales_report',
        'schedule': crontab(hour=2, minute=40),
    },
    'daily-delayed-pod-warning-sms-supplier': {
        'task': 'team.tasks.delayed_pod_warning_sms_supplier',
        'schedule': crontab(hour=10, minute=2),
    },
    'check-lapsed-load-status': {
        'task': 'fms.tasks.check_lapsed_load_status',
        'schedule': crontab(hour=0, minute=0),
    },
    'daily-rds-db-backup': {
        'task': 'team.tasks.daily_rds_backup',
        'schedule': crontab(hour=0, minute=30),
    },
    'booking-status-exprired-check': {
        'task': 'restapi.tasks.send_booking_status_expired_notifications',
        'schedule': crontab(hour=1, minute=0),
    },
    'daily-table-dump': {
        'task': 'team.tasks.daily_dump',
        'schedule': crontab(hour=1, minute=30),
    },
    'mail-notify-inquiry-status-report': {
        'task': 'restapi.tasks.notify_weekly_inquiry_report',
        'schedule': crontab(hour=3, minute=0, day_of_week='mon'),
    }
}
