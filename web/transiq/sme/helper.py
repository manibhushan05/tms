DISPLAY_DATE_FORMAT = '%d-%b-%Y'


def display_date_format(date_obj):
    if date_obj:
        return date_obj.strftime(DISPLAY_DATE_FORMAT)
    else:
        return ''

