from __future__ import absolute_import, print_function, division

import unittest
from datetime import date, datetime

from django.conf import settings
from django.urls import get_resolver, reverse, resolve
from django.test import TestCase
from django.test.utils import get_runner
from django.urls.exceptions import NoReverseMatch

from api.abstract import ApiTestCase, AuthApiTestCase
from api.tasks import run_async
from api.utils import financial_year_yy, to_int, to_round, float_or_none, int_or_none, to_str, similar_str, \
    clean_string, clean_int, clean_float, random_letters, random_digits, format_date, web_date_format, \
    display_date_format, display_datetime_format


def get_view_info(view):
    if not callable(view):
        try:
            url = reverse(view)
        except NoReverseMatch:
            return ('', '', ''), True
        resolver_match = resolve(url)
        view = resolver_match.func
    try:
        app, filename = view.__module__.split('.')
        return (app, filename, view.__name__), getattr(view, 'do_not_test', False)
    except ValueError:
        return 'django', ''


def get_url_data():
    data = get_resolver(None).reverse_dict
    url_data = []
    for v in data.keys():
        view_name, do_not_test = get_view_info(v)
        if do_not_test:
            continue
        urls = data.getlist(v)
        for url in urls:
            url_data.append((view_name, url[1]))
    return url_data


def count_test_cases(suite):
    normal_test_cases = 0
    api_test_cases = 0
    uniq_urls = set()
    for test in suite:
        if isinstance(test, ApiTestCase):
            api_test_cases += test.countTestCases()
            uniq_urls.add(test.url())
            if isinstance(test, AuthApiTestCase):
                [uniq_urls.add(u) for u in (test.login_url(), test.logout_url()) if u]
        else:
            normal_test_cases += test.countTestCases()
    return normal_test_cases + api_test_cases, normal_test_cases, api_test_cases, len(uniq_urls)

class TestRandomLetters(unittest.TestCase):
    def test_random_letters_success(self):
        self.assertEqual(len(random_letters(10)), 10)
        self.assertEqual(type(random_letters(10)), str)
        self.assertEqual(random_letters(0), '')

    def test_random_letters_failure(self):
        self.assertNotEqual(len(random_letters(10)), 11)
        self.assertNotEqual(type(random_letters(10)), int)

class TestRandomDigits(unittest.TestCase):
    def test_random_digits_success(self):
        self.assertEqual(len(random_digits(10)), 10)
        self.assertEqual(random_digits(0), '')

    def test_random_digits_failure(self):
        self.assertNotEqual(len(random_digits(10)), 11)
        self.assertNotEqual(type(random_digits(10)), float)

class TestFormatDate(unittest.TestCase):
    def test_format_date_success(self):
        self.assertEqual(format_date(date.today()), date.today().strftime('%Y/%m/%d %H:%M:%S'))
        self.assertEqual(format_date(date(2019,1,3)), '2019/01/03 00:00:00')

    def test_format_date_failure(self):
        self.assertNotEqual(format_date(date.today()), str(datetime.now()))

class TestWebFormatDate(unittest.TestCase):
    def test_web_format_date_success(self):
        self.assertEqual(web_date_format(date.today()), date.today().strftime('%m/%d/%Y'))
        self.assertEqual(web_date_format(date(2019,1,3)), '01/03/2019')
        self.assertEqual(web_date_format(date(2018, 12, 31)), '12/31/2018')

    def test_web_format_date_failure(self):
        self.assertNotEqual(web_date_format(date.today()), str(datetime.now()))
        self.assertNotEqual(web_date_format(date.today()), str(date.today()))

class TestDisplayDateFormat(unittest.TestCase):
    def test_display_date_format_success(self):
        self.assertEqual(display_date_format(date.today()), date.today().strftime('%d-%b-%Y'))
        self.assertEqual(display_date_format(date(2019,1,3)), '03-Jan-2019')
        self.assertEqual(display_date_format(date(2018,12,31)), '31-Dec-2018')

    def test_display_date_format_failure(self):
        self.assertNotEqual(display_date_format(date.today()), str(date.today()))
        self.assertNotEqual(display_date_format(date.today()), str(datetime.now()))

class TestDisplayDateTimeFormat(unittest.TestCase):
    def test_display_date_time_format_success(self):
        self.assertEqual(display_datetime_format(date.today()), date.today().strftime('%d-%b-%Y %I:%M:%S %p'))
        self.assertEqual(display_datetime_format(date(2019,1,3)), '03-Jan-2019 12:00:00 AM')
        self.assertEqual(display_datetime_format(date(2018,12,31)), '31-Dec-2018 12:00:00 AM')

    def test_display_date_time_format_failure(self):
        self.assertNotEqual(display_datetime_format(date.today()), str(datetime.now()))
        self.assertNotEqual(display_datetime_format(date.today()), str(date.today()))

class TestFinancialYearYY(unittest.TestCase):
    def test_financial_year_yy_success(self):
        self.assertEqual(financial_year_yy(date(2018, 3, 20)), 18)
        self.assertEqual(financial_year_yy(date(2018, 3, 31)), 18)
        self.assertEqual(financial_year_yy(date(2018, 4, 1)), 19)
        self.assertEqual(financial_year_yy(date(2015, 4, 1)), 16)
        self.assertEqual(financial_year_yy(date(2018, 4, 1)), 19)
        self.assertEqual(financial_year_yy(date(2018, 4, 1)), 19)
        self.assertEqual(financial_year_yy(date(2018, 1, 1)), 18)
        self.assertEqual(financial_year_yy(datetime(2018, 1, 1)), 18)
        self.assertEqual(financial_year_yy('2017-04-01'), '')
        self.assertEqual(financial_year_yy(None), '')
        self.assertEqual(financial_year_yy('None'), '')

    def test_financial_year_yy_failure(self):
        self.assertNotEqual(financial_year_yy('2017-04-01'), 17)
        self.assertNotEqual(financial_year_yy(None), 18)
        self.assertNotEqual(financial_year_yy('None'), 18)

class TestFloatOrNone(unittest.TestCase):
    def test_float_or_none_success(self):
        self.assertEqual(float_or_none("3.234"), 3.234)
        self.assertEqual(float_or_none("301"), 301.0)
        self.assertEqual(float_or_none("0"), 0.0)

    def test_float_or_none_failure(self):
        self.assertFalse(float_or_none("3.ad1"))
        self.assertFalse(float_or_none("ab.cd"))
        self.assertFalse(float_or_none("1 + 2.4"))
        self.assertFalse(float_or_none(""))

class TestToInt(unittest.TestCase):
    def test_to_int_success(self):
        self.assertEqual(to_int(2), 2)
        self.assertEqual(to_int(3.9999), 3)
        self.assertEqual(to_int("21.11112"), 21)
        self.assertEqual(to_int(8.000001), 8)
        self.assertEqual(to_int("1.22313"), 1)
        self.assertEqual(to_int("19.00001"), 19)
        self.assertEqual(to_int("0.000"), 0)
        self.assertEqual(to_int(0.999), 0)
        self.assertEqual(to_int("999.9999"), 999)
        self.assertEqual(to_int(None), 0)
        self.assertEqual(to_int('None'), 0)

    def test_to_int_failure(self):
        self.assertNotEqual(to_int('1.99999'), 2)
        self.assertNotEqual(to_int(None), 1)
        self.assertNotEqual(to_int('None'), 1)

class TestToRound(unittest.TestCase):
    def test_to_round_success(self):
        self.assertEqual(to_round(2), 2)
        self.assertEqual(to_round(3.9999), 4)
        self.assertEqual(to_round("2.11112"), 2)
        self.assertEqual(to_round(8.000001), 8)
        self.assertEqual(to_round("1.4992313"), 1)
        self.assertEqual(to_round("19.00001"), 19)
        self.assertEqual(to_round("0.000"), 0)
        self.assertEqual(to_round(2.5), 3)
        self.assertEqual(to_round("999.9999"), 1000)
        self.assertEqual(to_round(None), 0)

    def test_to_round_failure(self):
        self.assertNotEqual(to_round('11.99999'), 11)
        self.assertNotEqual(to_round(None), 4)

class TestIntOrNone(unittest.TestCase):
    def test_int_or_none_success(self):
        self.assertEqual(int_or_none("000"), 0)
        self.assertEqual(int_or_none("21"), 21)

    def test_int_or_none_failure(self):
        self.assertFalse(int_or_none("0.00"))
        self.assertFalse(int_or_none(""))
        self.assertFalse(int_or_none("12.3a"))

class TestToString(unittest.TestCase):
    def test_to_string_success(self):
        self.assertEqual(to_str(5), '5')
        self.assertEqual(to_str(5+6), '11')
        self.assertEqual(to_str(None), '')
        self.assertEqual(to_str('a12.3b'), 'a12.3b')

    def test_to_string_failure(self):
        self.assertFalse(to_str(None))
        self.assertNotEqual(to_str(5+6), '5+6')

class TestCleanString(unittest.TestCase):
    def test_clean_string_success(self):
        self.assertEqual(clean_string('  a.1#@   '), 'a.1#@')
        self.assertEqual(clean_string('  a b   '), 'a b')
        self.assertEqual(clean_string(None), '')

    def test_clean_string_failure(self):
        self.assertNotEqual(clean_string(' a b  '), 'ab')
        self.assertNotEqual(clean_string(' abc '), 'abc ')
        self.assertNotEqual(clean_string(' abc '), ' abc')

class TestCleanInt(unittest.TestCase):
    def test_clean_int_success(self):
        self.assertEqual(clean_int(' 123  '), 123)
        self.assertEqual(clean_int(' 12 34'), None)

    def test_clean_int_failure(self):
        self.assertNotEqual(clean_int('2+3'), 5)
        self.assertNotEqual(clean_int('a123'), 123)

class TestCleanFloat(unittest.TestCase):
    def test_clean_float_success(self):
        self.assertEqual(clean_float(' 123.45 '), 123.45)
        self.assertEqual(clean_float('12'), 12.0)
        self.assertEqual(clean_float(None), None)
        self.assertEqual(clean_float('12.3A'), None)

    def test_clean_float_failure(self):
        self.assertNotEqual(clean_float('12.3a'), 12.3)
        self.assertNotEqual(clean_float(' 1 + 2.3 '), 3.3)

class TestApiTestCoverage(TestCase):
    """
    The purpose of this test is to test our test coverage, its like a meta test.
    This test only fails if you have no urls to test, otherwise it just outputs the test coverage
    P.S. This is so hacky, I love it :)
    """

    def test_api_test_coverage(self):

        url_data = get_url_data()
        url_count = len(url_data)

        url_count_per_app = {}
        for view_full_name, url_pattern in url_data:
            app = view_full_name[0]
            if app in url_count_per_app:
                url_count_per_app[app] += 1
            else:
                url_count_per_app[app] = 1

        TestRunner = get_runner(settings)
        test_runner = TestRunner()

        total_api_tests = 0
        total_tests = 0
        total_urls_covered = 0
        data_per_app = {}
        for app in settings.AAHO_APPS:
            suite = test_runner.build_suite([app])
            total_count, normal_count, api_count, urls_covered = count_test_cases(suite)
            total_api_tests += api_count
            total_tests += total_count
            total_urls_covered += urls_covered
            data_per_app[app] = (url_count_per_app.get(app, 0), urls_covered, api_count, total_count)

        self.assertGreater(url_count, 0, 'No urls present')
        print('\n\nTEST COVERAGE REPORT:')
        print('______________________________________________________________')
        print(' App                 Tested URLs   Coverage   ApiTests  Total ')
        print('______________________________________________________________')
        for app, counts in data_per_app.items():
            print(' %s%s / %s%s%s%s ' % (
                app.ljust(16),
                str(counts[1]).rjust(7), str(counts[0]).ljust(3),
                ('' if counts[0] == 0 else ('%.1f%%' % (counts[1] * 100.0 / counts[0]))).rjust(12),
                str(counts[2]).rjust(9),
                str(counts[3]).rjust(9)
            ))
        print('______________________________________________________________')
        print(' %s%s / %s%s%s%s ' % (
            'TOTAL'.ljust(16),
            str(total_urls_covered).rjust(7), str(url_count).ljust(3),
            ('%.1f%%' % (total_urls_covered * 100.0 / url_count)).rjust(12),
            str(total_api_tests).rjust(10),
            str(total_tests).rjust(8)
        ))
        print('______________________________________________________________\n\n\n')
        self.assertGreater(url_count, 0, 'No urls present')


class TestAsyncFunctionApi(TestCase):

    def test_async(self):
        run_async('api.tests.async_test_func', args=['arg1', 'arg2'], kwargs=dict(a=1, b=True, c=dict(list=[1, 2])))


def async_test_func(*args, **kwargs):
    pass
