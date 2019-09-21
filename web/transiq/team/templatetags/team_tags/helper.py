from __future__ import absolute_import
from babel.numbers import format_currency
from django import template
from datetime import datetime, timedelta, date, time

from django.db.models import Q

from api.utils import get_or_none
from owner.vehicle_util import display_format
from sme.models import Sme
from team.helper.helper import is_neft_holiday

register = template.Library()


def to_int(value):
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        return int(float(value))


@register.filter
def inr_format(num):
    return format_currency(num, 'INR', locale='en_IN')


@register.simple_tag
def subtract_amount(num1, num2):
    return to_int(num1) - to_int(num2)


@register.simple_tag
def display_vehicle_number_format(vehicle_number):
    return display_format(vehicle_number)


@register.simple_tag
def contract_customer(id):
    customer = get_or_none(Sme, id=id)
    if isinstance(customer, Sme):
        today = datetime.now().date()
        if customer.customercontract_set.filter(Q(start_date__lte=today) & Q(end_date__gte=today)).exclude(
                deleted=True).exists():
            return {'id': customer.id, 'name': customer.get_name(), 'code': customer.company_code, 'is_contract': True}
        else:
            return {'id': customer.id, 'name': customer.get_name(), 'code': customer.company_code, 'is_contract': False}
    else:
        return {'id': -1, 'name': '', 'code': customer.company_code, 'is_contract': False}
