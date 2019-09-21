import requests
from bs4 import BeautifulSoup


def parse_bharat_gps_tracker():
    login_url = 'http://bharatgps.in/authentication/create'
    session = requests.session()
    login_page = session.get(login_url)
    login_data = {
        'email': 'rohit@aaho.in',
        'password': '123456',
    }
    login_response = session.post('http://bharatgps.in/authentication/store', data=login_data)
    location_data=session.get('http://bharatgps.in/history/positions?device_id=5359&from_date=2018-10-13&from_time=00%3A45&to_date=2018-10-13&to_time=23%3A45')
    html_data=location_data.content
    table = BeautifulSoup(html_data, 'lxml')
    table = table.tbody
    for tr in table.findAll("tr"):
        print(tr['data-lat'],tr['data-lng'],tr['data-position_id'],tr['data-speed'],tr['data-time'])
