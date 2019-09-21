from __future__ import unicode_literals

import re

from django import template

register = template.Library()

NUMBER_PATTERN = re.compile(r'([A-Za-z]{2})[ \-,.]*([0-9]{1,2})[ \-,.]*([A-Za-z]{0,3})[ \-,.]*([0-9]{1,4})')


@register.simple_tag
def display_vehicle_number(num):
    if not num:
        return num
    num = num.strip()
    match = NUMBER_PATTERN.match(num)
    if match:
        groups = match.groups()
        if groups[2]:
            num = groups[0] + groups[1] + ' ' + groups[2] + ' ' + groups[3]
        else:
            num = groups[0] + groups[1] + ' ' + groups[3]
    return num.upper()


@register.simple_tag
def substract(num1, num2):
    return int(num1 - num2)


@register.simple_tag
def to_int(value):
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        return int(float(value))
