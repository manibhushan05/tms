from __future__ import unicode_literals
from django import template

register = template.Library()


@register.filter('has_group')
def has_group(user, group_name):
    groups = user.groups.all().values_list('name', flat=True)
    return True if group_name in groups else False


@register.simple_tag
def to_int(value):
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        return int(float(value))
