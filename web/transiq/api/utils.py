import random
import re
import time
from datetime import datetime, date, timedelta
from difflib import SequenceMatcher

from babel.numbers import format_currency
from dateutil import parser
from django.contrib.admin.utils import NestedObjects
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.text import capfirst
from decimal import Decimal, ROUND_HALF_UP

JSON_DATE_FORMAT = '%Y/%m/%d %H:%M:%S'
WEB_DATE_FORMAT = '%m/%d/%Y'
DISPLAY_DATE_FORMAT = '%d-%b-%Y'
DISPLAY_DATETIME_FORMAT = '%d-%b-%Y %I:%M:%S %p'

EXT_REGEX = re.compile(r'^.*\.([A-Za-z0-9]{0,4})$')
EXT_DEFAULT = 'jpg'


def get_ext(filename, default=EXT_DEFAULT):
    filename = None if not filename else filename.strip()
    if not filename:
        return default

    match = EXT_REGEX.match(filename)
    if not match:
        return default

    try:
        ext = match.groups()[0]
        ext = None if not ext else ext.strip()
    except IndexError:
        ext = None

    return ext or default


def merge(dict1, dict2):
    dict3 = {}
    dict3.update(dict1)
    dict3.update(dict2)
    return dict3


def in_mb(memory_in_bytes):
    bytes_in_mb = 1024 * 1024
    return float(memory_in_bytes) / float(bytes_in_mb)


def random_ids(count, num_digits, chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    ids = set()
    while len(ids) < count:
        ids.add(random_id(num_digits, chars=chars))
    return list(ids)


def random_id(num_digits, chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    max_index = len(chars) - 1
    return ''.join(chars[random.randint(0, max_index)] for _ in range(num_digits))


def random_letters(num_digits):
    return random_id(num_digits, chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ')


def random_digits(num_digits):
    return random_id(num_digits, chars='0123456789')


def format_iso(dt):
    if not dt:
        return ''
    return dt.isoformat()


def parse_iso(dt):
    dt = None if not dt else dt.strip()
    return None if not dt else parser.parse(dt)


def from_timestamp(timestamp):
    log_time = None if not timestamp else make_aware(datetime.fromtimestamp(timestamp / 1e3))
    return log_time


def to_timestamp(dt):
    log_time = None if not dt else ((time.mktime(dt.timetuple()) + dt.microseconds / 1e6) * 1e3)
    return log_time


def now_timestamp():
    return time.time() * 1e3


def make_aware(dt):
    return timezone.make_aware(dt, timezone.get_current_timezone())


def parse_date(date_str):
    try:
        dt = datetime.strptime(date_str, JSON_DATE_FORMAT)
        return dt
    except ValueError:
        return None


def format_date(date_obj):
    if not date_obj:
        return ""
    return date_obj.strftime(JSON_DATE_FORMAT)


def web_date_format(date_obj):
    if not date_obj:
        return ""
    return date_obj.strftime(WEB_DATE_FORMAT)


def display_date_format(date):
    if not date:
        return ""
    return date.strftime(DISPLAY_DATE_FORMAT)


def display_datetime_format(date):
    if not date:
        return ""
    return date.strftime(DISPLAY_DATETIME_FORMAT)


def float_or_none(float_str):
    try:
        return float(float_str)
    except ValueError:
        return None


def to_int(value):
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return 0


def to_round(value):
    if not value:
        return 0
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def int_or_none(int_str):
    try:
        return int(int_str)
    except:
        return None


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except (model.DoesNotExist, ValueError) as err:
        return None
    except model.MultipleObjectsReturned:
        return model.objects.filter(**kwargs).last()
    except TypeError:
        return None


def is_unique_constraint_error(e):
    """
    @hack:
    IntegrityError duplicate key message looks like this (but this might change)
    'duplicate key value violates unique constraint "?"\nDETAIL:  Key (?)=(?) already exists.\n'
    """
    return e.message.startswith('duplicate key value violates unique constraint')


def to_str(val):
    if val:
        return str(val)
    else:
        return ''


def similar_str(a, b):
    return SequenceMatcher(None, a, b).ratio()


def similar_test():
    # a = 'P.O GHUTGORIA, P.S. BARJORA, Bankura, West Bengal 722167'
    #
    # b = '7123169'
    from sme.models import Sme

    for sme in Sme.objects.exclude(customer_address=None):
        try:
            a = sme.customer_address
            a = re.sub(' +', ' ', a.replace(',', ' ')).lower()
            b = sme.pin
            if any([similar_str(value, b.lower()) > 0.8 for value in a.split()]):
                pass
                # print(sme.get_name(), sme.customer_address, sme.city)
        except AttributeError:
            print(sme, sme.customer_address)


def clean_string(raw_str):
    if not raw_str:
        return ''
    raw_str = raw_str.strip()
    if not raw_str:
        return ''
    if raw_str == 'None':
        return ''
    return raw_str


def clean_int(num_str):
    if not num_str:
        return None
    num_str = num_str.strip()
    try:
        return int(num_str)
    except ValueError:
        return None


def clean_float(num_str):
    if not num_str:
        return None
    num_str = num_str.strip()
    try:
        return float(num_str)
    except ValueError:
        return None


def financial_year_yy(dt):
    if isinstance(dt, datetime):
        if dt > datetime(dt.year, 3, 31):
            return int(dt.strftime('%y')) + 1
        else:
            return int(dt.strftime('%y'))
    elif isinstance(dt, date):
        if dt > date(dt.year, 3, 31):
            return int(dt.strftime('%y')) + 1
        else:
            return int(dt.strftime('%y'))

    return ''


def format_inr(amount):
    try:
        return format_currency(float(amount), 'INR', locale='en_IN', currency_digits=True)[:-3]
    except (ValueError, TypeError) as e:
        return u'\u20b9\xa0.00'


def get_deleted_objects(objs):
    collector = NestedObjects(using='default')
    collector.collect(objs)

    def format_callback(obj):
        opts = obj._meta
        no_edit_link = '%s: %s' % (capfirst(opts.verbose_name),
                                   force_text(obj))
        return no_edit_link

    to_delete = collector.nested(format_callback)
    protected = [format_callback(obj) for obj in collector.protected]
    model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}
    #
    return to_delete, model_count, protected
