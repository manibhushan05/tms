import os
import random
import json
import shutil

import requests
import time
import csv

from datetime import datetime

from django.core.mail.message import EmailMessage

from django.conf import settings


BASE_DIR = settings.BASE_DIR

SESSION_KEY = 'sk2hmjbq2lb0f9c9puhgosub3gn0lhge'  # changes after expiry, will have to enter manually


TIME_GAP = 3.0
VARIATION = 1.0

MAX_ITERATIONS = 5

SERVER_URL = 'https://www.blackbuck.com/'
LOCATIONS_URL = SERVER_URL + 'api/availableOrdersLocations'
ORDERS_URL = SERVER_URL + 'api/availableOrders'

USER_AGENT = 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; ONE A2003 Build/MMB29M)'

CACHE_DIR = os.path.join(BASE_DIR, '.blackbuck_cache')
DATA_DIR = os.path.join(BASE_DIR, 'api', 'blackbuck')


FIELDNAMES = [
    'id', 'user_id', 'from_city', 'start_sublocation', 'to_city', 'end_sublocation', 'truck_type',
    'dynamic_price', 'order_value', 'loading_charges', 'unloading_charges', 'product', 'weight',
    'reporting_time'  # order important
] + [
    'start_location_id', 'start_loc_lat', 'start_loc_lng', 'from_city_id', 'from_state',
    'end_location_id', 'end_loc_lat', 'end_loc_lng', 'to_city_id', 'truck_type_id',
    'alarm_price', 'bonus_amount', 'loading_unloading_rate', 'matching_trucks', 'order_missed',
    'order_placed', 'price_alarm_reached', 'price_alarm_set', 'relevant_order', 'status',
    'is_watch', 'is_watchable', 'is_watched', 'watch_id'  # order irrelevant
]


def fetch_blackbuck_data(clean):
    data = BlackBuck(clean).fetch()
    data_filename = os.path.join(DATA_DIR, 'Blackbuck_orders_%s.csv' % datetime.now().strftime("%Y-%m-%d %H:%M"))

    flat_data = [row for rows in data.values() for row in rows]

    with open(data_filename, 'wb') as csvfile:
        ordered_fieldnames = [f for f in FIELDNAMES if f in flat_data[0]]
        remaining_fieldnames = [f for f in flat_data[0].keys() if f not in ordered_fieldnames]
        fieldnames = ordered_fieldnames + remaining_fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in flat_data:
            row['reporting_time'] = datetime.fromtimestamp(row['reporting_time'] / 1e3).strftime("%Y/%m/%d %H:%M")
            writer.writerow(row)

    return data


def send_expiry_msg():
    subject = 'Blackbuck session token expired'
    body = 'Session Token: %s is no longer valid' % SESSION_KEY
    email = EmailMessage(subject, body, to=['mani@aaho.in'])
    if settings.ENABLE_MAIL and not settings.TESTING:
        email.send()


class BlackBuck(object):

    def __init__(self, clean=None):
        self.last_request_time = None
        self.location_orders = {}
        self.cities = []
        self.url_cache = {}
        self.start_time = None
        self.iter_count = 0
        if clean and os.path.exists(CACHE_DIR):
            shutil.rmtree(CACHE_DIR)
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def fetch(self):
        print('\n\n')
        self.start_time = time.time()
        locations_response = self.locations_request()
        locations_response_result = None if not locations_response else locations_response.get('result', None)
        if not locations_response_result:
            send_expiry_msg()
            raise AssertionError('Location request unsuccessful')
        self.cities = [r['id'] for r in locations_response_result]

        while len(self.location_orders) < len(self.cities) and self.iter_count < MAX_ITERATIONS:
            self.iter_count += 1
            self.fetch_remaining_orders()

        return self.location_orders

    def fetch_remaining_orders(self):
        print('\n\n')
        remaining_cities = [c for c in self.cities if c not in self.location_orders]
        print('%s cities remaining' % len(remaining_cities))
        for city in remaining_cities:
            print('\n')
            orders_response = self.orders_request(city)
            orders_response_result = None if not orders_response else orders_response.get('result', None)
            if orders_response_result:
                self.location_orders[city] = orders_response_result
                self.write_to_db(city, orders_response_result)

    def write_to_db(self, city, orders_response_result):
        pass

    def locations_request(self):
        return self.post_request(LOCATIONS_URL, self.get_request_data())

    def orders_request(self, city_id):
        print('City=%s, starting orders request, ETA: %s ms' % (city_id, self.estimated_time() or 'n/a'))
        return self.post_request(ORDERS_URL, self.get_order_request_data(city_id))

    def estimated_time(self):
        time_lapsed = time.time() - self.start_time
        total_cities = len(self.cities)
        cities_fetched = len(self.location_orders)
        if cities_fetched == 0:
            return None
        time_per_city = time_lapsed / cities_fetched
        return (total_cities - cities_fetched) * time_per_city

    def post_request(self, url, data):
        response = self.get_from_cache(url, data)
        if response:
            print('Found in cache! url=%s' % url)
            return response

        json_data = json.dumps(data)

        self.wait_if_required()
        print('POST %s data=%s' % (url, json_data))
        req = requests.post(url, data=json_data, headers=self.headers())
        self.last_request_time = time.time()

        if req.status_code != 200:
            print('Error: status=%s, error=%s' % (req.status_code, req.text))
            return None

        response = req.json()
        if not response:
            print('Error: No Json received')
            return None

        print('SUCCESS response=%s...' % json.dumps(response)[:200])
        self.write_to_cache(url, data, response)
        return response

    def get_from_cache(self, url, data):
        key = self.cache_key(url, data)
        response = self.url_cache.get(key, None)
        if response:
            return response

        try:
            response_str = open(self.cache_file_path(url, data)).read()
            response = json.loads(response_str)
            self.url_cache[url] = response
        except (IOError, ValueError):
            response = None

        return response

    def write_to_cache(self, url, data, response):
        self.url_cache[url] = response
        try:
            open(self.cache_file_path(url, data), 'wb').write(json.dumps(response))
        except (IOError, ValueError):
            print('Error writing to cache url=%s, response=%s' % (url, response))

    def wait_if_required(self):
        if self.last_request_time is not None:
            wait_time = self.random_duration() - (time.time() - self.last_request_time)
            if wait_time > 0:
                print('Waiting %s seconds...' % wait_time)
                time.sleep(wait_time)

    @staticmethod
    def get_request_data():
        return {'session_key': SESSION_KEY}

    @staticmethod
    def get_order_request_data(city_id):
        return {'session_key': SESSION_KEY, 'from_city_id': city_id}

    @staticmethod
    def cache_file_path(url, data):
        filename = BlackBuck.cache_key(url, data)
        return os.path.join(CACHE_DIR, filename)

    @staticmethod
    def cache_key(url, data):
        city_id = data.get('from_city_id', None)
        if city_id:
            return str(hash((url, city_id)))
        else:
            return str(hash(url))

    @staticmethod
    def headers():
        return {
            'Content-type': 'application/json',
            'Accept': '*/*',
            'User-Agent': USER_AGENT
        }

    @staticmethod
    def random_duration():
        return TIME_GAP + (random.random() * 2.0 - 1.0) * VARIATION





