import re

NUMBER_PATTERN = re.compile(r'([A-Za-z]{2})[ \-,.]*([0-9]{1,2})[ \-,.]*([A-Za-z]{0,3})[ \-,.]*([0-9]{1,4})')


def display_format(num):
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


def compare_format(num):
    if not num:
        return num
    num = num.strip()
    match = NUMBER_PATTERN.match(num)
    if match:
        groups = match.groups()
        num = groups[0] + groups[1] + groups[2] + groups[3]
    else:
        num = num.replace('-', '').replace(',', '').replace('.', '').replace(' ', '')
    return num.lower()


def num_equal(str1, str2):
    str1 = compare_format(str1)
    str2 = compare_format(str2)
    return str1 == str2
