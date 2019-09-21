from django.core.validators import RegexValidator

VEHICLE_NUMBER = '/^[A-Z]{2}[ -.]*\d{1,2}[ -.]*[A-Z]{0,3}[ -.]*\d{4}$/i'
GSTIN = '^\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}$'
PHONE = '^(\+\d{1,3}[- ]?)?\d{10}$'
PIN = '^\d{6}$'
PAN = '/^[a-z]{3}[abcfghljptk][a-z]\d{4}[a-z]$/i'
IFSC = '/^[A-Z]{4}0[A-Z0-9]{6}$/i'
phone_regex = '^(\+\d{1,3}[- ]?)?\d{10}$'


def get_phone_regex():
    return RegexValidator(regex=r'((\+*)((0[ -]+)*|(91 )*)(\d{12}+|\d{10}+))|\d{5}([- ]*)\d{6}',
                          message="Phone number must be entered in the format: '9775876662, 0 9754845789, 0-9778545896, +91 9456211568, 91 9857842356 , 919578965389, 03595-259506, 03592 245902,03598245785'. Up to 15 digits allowed.")


def get_name_regex():
    return RegexValidator("^([a-zA-Z]{2,}\\s[a-zA-z]{1,}'?-?[a-zA-Z]{2,}\\s?([a-zA-Z]{1,})?)",
                          message='Enter Valid name')
