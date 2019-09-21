import re

PAN = r'(?i)^[a-z]{3}[abcfghljpte][a-z]\d{4}[a-z]$'
MOBILE_NUMBER_REGEX = r'^[1-9][0-9]{9}$'
IFSC_REGEX = r'(?i)^[A-Z]{4}0[A-Z0-9]{6}$'
GSTIN_REGEX = r'(?i)^\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}$'
NAME_REGEX = r'(?i)^[a-z\s]{1,}[\.]{0,1}[a-z0-9\.\s]{0,}$'
PIN_REGEX = r'^[1-9]{1}[0-9]{5}$'
USERNAME_REGEX = r'^[\w.@+-]+$'
VEHICLE_NUMBER_REGEX = r'(?i)^[A-Z]{2}[ -.]*\d{1,2}[ -.]*[A-Z]{0,3}[ -.]*\d{4}$'
COMPANY_CODE_REGEX = r'(?i)^[a-z]{3}$'
SUPPLIER_CODE_REGEX = r'(?i)^[a-z]{3}$'
BENEFICIARY_CODE_REGEX = r'^[A-Z0-9]{3,14}$'
ALPHANUMERIC_WITH_SPACE=r'(?i)^[a-z\d\s]+$'


def validate_pan(value):
    if not value:
        return False
    return True if re.match(pattern=PAN, string=value) else False


def validate_mobile_number(value):
    if not value:
        return False
    return True if re.match(pattern=MOBILE_NUMBER_REGEX, string=value) else False


def validate_ifsc(value):
    if not value:
        return False
    return True if re.match(pattern=IFSC_REGEX, string=value) else False


def validate_gstin(value):
    if not value:
        return False
    return True if re.match(pattern=GSTIN_REGEX, string=value) else False


def validate_name(value):
    if not value:
        return False
    return True if re.match(pattern=NAME_REGEX, string=value) else False


def validate_pin(value):
    if not value:
        return False
    return True if re.match(pattern=PIN_REGEX, string=str(value)) else False


def validate_username(value):
    if not value:
        return False
    return True if re.match(pattern=USERNAME_REGEX, string=str(value)) else False


def validate_vehicle_number(value):
    if not value:
        return False
    return True if re.match(pattern=VEHICLE_NUMBER_REGEX, string=str(value)) else False


def validate_company_code(value):
    if not value:
        return False
    return True if re.match(pattern=COMPANY_CODE_REGEX, string=str(value)) else False


def validate_beneficiary_code(value):
    if not value:
        return False
    return True if re.match(pattern=BENEFICIARY_CODE_REGEX, string=str(value)) else False

def validate_alphanumeric_with_space(value):
    if not value:
        return False
    return True if re.match(pattern=ALPHANUMERIC_WITH_SPACE, string=str(value)) else False

