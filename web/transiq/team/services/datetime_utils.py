import calendar
import numpy as np
from datetime import datetime

from broker.helper import django_date_format

calendar.setfirstweekday(6)


def get_week_of_month(year, month, day):
    x = np.array(calendar.monthcalendar(year, month))
    week_of_month = np.where(x == day)[0][0] + 1
    return (week_of_month)


def next_week_day(date):
    try:
        date = datetime.strptime(date, 'YYYY-MM-dd')
    except ValueError:
        return "Only YYYY-MM-DD is Accepted"
    return date


def is_weekend_except_even_saturday(date):
    pass


def is_weekend(date):
    pass


get_week_of_month(2015, 9, 14)
