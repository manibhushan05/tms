from datetime import datetime

from django.core.exceptions import PermissionDenied

DISPLAY_DATE_FORMAT = '%d-%b-%Y'


def display_date_format(date_obj):
    if date_obj:
        return date_obj.strftime(DISPLAY_DATE_FORMAT)
    else:
        return ''


def is_blank(string):
    return not (string and string.strip())


def django_date_format(date):
    if is_blank(date):
        return None
    else:
        return datetime.strptime(date, '%m/%d/%Y')


def get_broker_obj(user):
    from broker.models import Broker
    if user.groups.filter(name='supplier').exists():
        if user.is_authenticated:
            try:
                return Broker.objects.get(name=user)
            except (Broker.DoesNotExist, Broker.MultipleObjectsReturned) as e:
                raise PermissionDenied
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied
