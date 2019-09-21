from datetime import datetime, timedelta

from django.core.exceptions import FieldError
#
# def is_key_exist(dict, key):
#     if key in dict.keys():
#         return True
#     else:
#         return False
#
#
# def check_if_key_is_positive(dict, key):
#     if "id" in dict.keys():
#
#         try:
#             if int(dict["id"]) >= 0:
#                 return [True]
#             else:
#                 return [False, "{} must be a positive Integer ".format(key)]
#         except ValueError:
#             return [False, "{} must be a positive Integer ".format(key)]
#
#     else:
#         return [False, "{} must be provided ".format(key)]
#
#
# def is_positive_number(data, key):
#     if type(data) is not dict:
#         for d in data:
#             if type(d) is not dict:
#                 return [False, "Data is not in correct format "]
#             result = check_if_key_is_positive(d, key)
#             if not result[0]:
#                 return result
#         return [True]
#     else:
#         return check_if_key_is_positive(data, key)
#
#
# def check_if_instances_of_given_model_exist(model, instance_list):
#     for obj in instance_list:
#         if not model.objects.filter(id=obj["id"]):
#             return [False, obj["id"]]
#     return [True]
#
from googletrans import Translator

from api.models import S3Upload


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs, deleted=False)
    except (model.DoesNotExist, ValueError) as err:
        return None
    except model.MultipleObjectsReturned:
        return model.objects.filter(**kwargs).last()
    except TypeError:
        return None
    except FieldError:
        try:
            return model.objects.get(**kwargs)
        except (model.DoesNotExist, ValueError) as err:
            return None
        except model.MultipleObjectsReturned:
            return model.objects.filter(**kwargs).last()
        except TypeError:
            return None


class AahoTranslator(object):
    def __init__(self):
        self.translator = Translator()
        self.translated_text = None
        self.translated_object = None
        self.translated_response = None

    def translate(self, text, dest='en', src='auto'):
        try:
            if src == 'auto':
                self.translated_object = self.translator.translate(text, dest=dest)
            else:
                self.translated_object = self.translator.translate(text, src=src, dest=dest)
        except:
            self.translated_text = text
            self.translated_response = {'status': 'failure', 'text': self.translated_text}
        if self.translated_object and not self.translated_text:
            self.translated_text = self.translated_object.text
            self.translated_response = {'status': 'success', 'text': self.translated_text}
        return self.translated_response


def manual_booking_zip_files():
    from team.models import ManualBooking
    for booking in ManualBooking.objects.exclude(lr_numbers=None):
        zip_file = []
        for lr in booking.lr_numbers.all():
            s3_file = S3Upload.objects.filter(folder='lr').filter(filename__icontains=lr.lr_number,
                                                                  filename__endswith='.zip')
            if s3_file and s3_file.count() == 1:
                zip_file.append(zip_file)

        if len(zip_file) == 0:
            pass


def to_float(value):
    try:
        return 0 if not value else float(value)
    except ValueError:
        return 0


def is_blank(string):
    return not (string and string.strip())


def django_date_format(date):
    if is_blank(date):
        return None
    elif date == 'None':
        return "Invalid Format"
    else:
        try:
            return datetime.strptime(date, '%d-%b-%Y')
        except ValueError:
            return "Invalid Format"


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


def calculate_sundays_between_dates(start_date, end_date):
    sundays_count = 0
    delta = end_date - start_date
    for i in range(delta.days):
        if (start_date + timedelta(days=i)).weekday() == 6:
            sundays_count += 1
    return sundays_count
