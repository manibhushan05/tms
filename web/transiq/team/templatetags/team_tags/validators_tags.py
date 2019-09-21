from __future__ import unicode_literals
from api import validators
from django import template

register = template.Library()


@register.simple_tag
def regex_vehicle_number():
    return validators.VEHICLE_NUMBER


@register.simple_tag
def regex_gstin():
    return validators.GSTIN


@register.simple_tag
def regex_phone():
    return validators.PHONE


@register.simple_tag
def regex_pin():
    return validators.PIN


@register.simple_tag
def regex_pan():
    return validators.PAN


@register.simple_tag
def regex_ifsc():
    return validators.IFSC
