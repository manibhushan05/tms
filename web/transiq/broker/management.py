import random

import pandas as pd
from collections import Counter

from django.contrib.auth.models import User, Group
from django.db.models import Q
from psycopg2._psycopg import IntegrityError

from api.sms import send_sms
from broker.models import Broker, BrokerVehicle
from owner.models import Vehicle
from restapi.helper_api import generate_random_string
from team.models import ManualBookingSummary, ManualBooking
from utils.models import AahoOffice, State


def mumbai_directory():
    df = pd.read_excel('../../data/Mumbai Transport Directory.xlsx')
    df = df.fillna('')
    print(df.columns)
    for i, row in df.iterrows():
        print(row['name'])


def broker_aaho_office():
    data = []
    for broker in Broker.objects.all():
        bookings = broker.team_booking_broker.all()
        if bookings.count() > 0:
            aaho_source_offices = list(bookings.values_list('source_office__branch__name', flat=True))
            aaho_destination_offices = list(bookings.values_list('destination_office__branch__name', flat=True))
            print(['{}: {}'.format(office, aaho_source_offices.count(office)) for office in set(aaho_source_offices)])
            data.append([
                broker.id,
                broker.get_name(),
                broker.get_phone(),
                bookings.order_by('shipment_date').first().shipment_date,
                bookings.order_by('shipment_date').last().shipment_date,
                '\n'.join(['{}: {}'.format(office, aaho_source_offices.count(office)) for office in
                           set(aaho_source_offices)]),
                '\n'.join(['{}: {}'.format(office, aaho_destination_offices.count(office)) for office in
                           set(aaho_destination_offices)])
            ])
    df = pd.DataFrame(data=data, columns=['ID', 'Name', 'Phone', 'First Booking Date', 'Last Booking Date',
                                          'Source Booking Offices', 'Dest Booking Office'])
    df.to_excel('Aaho office wise Brokers.xlsx', index=False)


def update_broker_aaho_office():
    for broker in Broker.objects.all():
        bookings = broker.team_booking_broker.all()
        if bookings.count() > 0:
            aaho_source_offices = list(bookings.values_list('source_office__id', flat=True))
            data = {}
            for office in set(aaho_source_offices):
                data[office] = aaho_source_offices.count(office)
            office_id = max(data.iterkeys(), key=lambda k: data[k])
            aaho_office = AahoOffice.objects.get(id=office_id)
            broker.aaho_office = aaho_office
            broker.save()
            # print([{'{}: {}'.format(office, aaho_source_offices.count(office))} for office in set(aaho_source_offices)])


def broker_aaho_office_data():
    for broker in Broker.objects.all():
        print(broker.aaho_office.to_json() if broker.aaho_office else {})


def broker_vehicle():
    vehicle = Vehicle.objects.get(id=3834)

    broker = Broker.objects.get(id=616)
    BrokerVehicle.objects.create(broker=broker, vehicle=vehicle)


def broker_data():
    data = []
    for broker in Broker.objects.all().order_by('-id'):
        print(broker)
        data.append([
            broker.id,
            broker.get_name(),
            broker.get_phone(),
            broker.city.name if broker.city else '',
            broker.aaho_office.branch_name if broker.aaho_office else ''
        ])
    df = pd.DataFrame(data=data, columns=['ID', 'Name', 'Phone', 'City', 'Aaho Office'])
    df.to_excel('Brokers.xlsx', index=False)
    broker = Broker.objects.get(id=616)
    # BrokerVehicle.objects.create(broker=broker, vehicle=vehicle)


def update_state_name():
    df = pd.read_excel('/Users/mani/Downloads/Supplier Destination States.xlsx', sheet_name='New')
    df = df.fillna('')
    for i, row in df.iterrows():
        if row['Destination States']:
            broker = Broker.objects.get(id=row['ID'])
            states = row['Destination States'].split(',')
            for state in states:
                try:
                    st = State.objects.get(code=state)
                    broker.destination_state.add(st)
                except State.DoesNotExist:
                    if state == 'All':
                        broker.destination_state.add(*State.objects.all())


def update_state_code():
    data = [{'id': 1, 'name': 'Punjab', 'code': 'PB'}, {'id': 2, 'name': 'Maharashtra', 'code': 'MH'},
            {'id': 3, 'name': 'Andhra Pradesh', 'code': 'AP'}, {'id': 18, 'name': 'ODISHA', 'code': 'OD'},
            {'id': 36, 'name': 'TELANGANA', 'code': 'TS'}, {'id': 32, 'name': 'Goa', 'code': 'GA'},
            {'id': 5, 'name': 'Tripura', 'code': 'TR'}, {'id': 37, 'name': 'ARUNACHAL PRADESH', 'code': 'AR'},
            {'id': 23, 'name': 'Assam', 'code': 'AS'}, {'id': 15, 'name': 'Bihar', 'code': 'BR'},
            {'id': 13, 'name': 'Chhattisgarh', 'code': 'CG'}, {'id': 20, 'name': 'Delhi', 'code': 'DL'},
            {'id': 7, 'name': 'Gujarat', 'code': 'GJ'}, {'id': 12, 'name': 'Haryana', 'code': 'HR'},
            {'id': 30, 'name': 'Himachal Pradesh', 'code': 'HP'}, {'id': 14, 'name': 'Jammu and Kashmir', 'code': 'JK'},
            {'id': 4, 'name': 'Jharkhand', 'code': 'JH'}, {'id': 11, 'name': 'Kerala', 'code': 'KL'},
            {'id': 19, 'name': 'Madhya Pradesh', 'code': 'MP'}, {'id': 26, 'name': 'Manipur', 'code': 'MN'},
            {'id': 29, 'name': 'Meghalaya', 'code': 'ML'}, {'id': 8, 'name': 'Mizoram', 'code': 'MZ'},
            {'id': 24, 'name': 'Nagaland', 'code': 'NL'}, {'id': 16, 'name': 'West Bengal', 'code': 'WB'},
            {'id': 22, 'name': 'Uttarakhand', 'code': 'UK'}, {'id': 6, 'name': 'Uttar Pradesh', 'code': 'UP'},
            {'id': 10, 'name': 'Tamil Nadu', 'code': 'TN'}, {'id': 9, 'name': 'Rajasthan', 'code': 'RJ'},
            {'id': 21, 'name': 'Chandigarh', 'code': 'CH'}, {'id': 17, 'name': 'Karnataka', 'code': 'KA'},
            {'id': 35, 'name': 'PONDICHERRY', 'code': 'PY'}, {'id': 34, 'name': 'DAMAN and DIU', 'code': 'DD'},
            {'id': 25, 'name': 'Sikkim', 'code': 'SK'}, {'id': 31, 'name': 'Dadra and Nagar Haveli', 'code': 'DN'},
            {'id': 28, 'name': 'Andaman and Nicobar Islands', 'code': 'AN'},
            {'id': 27, 'name': 'Puducherry', 'code': 'PH'}]
    for d in data:
        state = State.objects.get(id=d['id'])
        state.code = d['code']
        state.save()


def update_booking_summary():
    data = {
        'pending_pod': {'number_of_booking': 1, 'amount_paid': 12, 'balance': 23, 'total_amount': 23},
        'delivered_pod': {'number_of_booking': 1, 'amount_paid': 12, 'balance': 23, 'total_amount': 23},
        'completed_booking': {'number_of_booking': 1, 'total_amount': 23},
    }
    ManualBookingSummary.objects.create(user=User.objects.get(username='roku'), summary=data)


def broker_booking_data():
    data = []
    for booking in ManualBooking.objects.filter(Q(source_office_id=4) | Q(destination_office_id=4)):
        if booking.supplier:
            data.append([
                booking.supplier.get_name(),
                booking.supplier.get_phone(),
                booking.from_city,
                booking.to_city,
                booking.lorry_number,
                booking.type_of_vehicle,
                booking.shipment_date
            ])
    df = pd.DataFrame(data=data,
                      columns=['Name', 'Phone', 'Source', 'Destination', 'Vehicle Number', 'Vehicle Category',
                               'Shipemnt Date'])
    df.to_excel('brokers.xlsx', index=False)


def create_username_broker():
    df = pd.read_excel('/Users/mani/Downloads/Brokers.xlsx')
    print(df.columns)
    df = df.fillna('')
    data = []
    for i, row in df.iterrows():
        try:
            temp = list(row)[1:5]
            broker = Broker.objects.get(id=row['ID'])
            user = User.objects.get(id=broker.name.id)
            print(user)
            temp.insert(0, broker.id)
            temp.insert(0, user.id)
            temp.append(user.username)
            if User.objects.filter(username=row['Phone']).exists() and user.username != row['Phone']:
                username = '{}{}'.format(row['Phone'], random.randint(10, 99))
            else:
                username = row['Phone']
            user.username = username
            password = 'aaho{0:04d}'.format(user.id)
            user.set_password(password)
            user.save()
            if not user.groups.exists():
                group = Group.objects.get(name='fms')
                user.groups.add(group)
            temp.append(username)
            temp.append(password)
            data.append(temp)
        except:
            print(row)
    df = pd.DataFrame(data=data,
                      columns=['User ID', 'Broker ID', 'Name', 'Phone', 'City', 'Aaho Office', 'Old Username',
                               'New Username',
                               'New Password'])
    df.to_excel('Brokers new username and password.xlsx', index=False)


def generate_broker_code():
    for broker in Broker.objects.filter(code=None):
        while True:
            code=generate_random_string(N=4)
            if Broker.objects.filter(code=code).exists():
                continue
            broker.code=code
            broker.save()
            break

def send_app_sms():
    df=pd.read_excel('/Users/mani/Downloads/fms_users.xlsx')
    for i,row in df.iterrows():
        sms_template=u"नववर्ष में Aaho FMS ऍप डाउनलोड करें - http://bit.ly/2zZuTwL \n इस ऍप में अपनी हर ट्रिप की एडवांस, बैलेन्स और अन्य सारी जानकारी देखें, अगले दिन की लोडिंग सुनिश्चित करें, और गाड़ियों की GPS ट्रैकिंग देखें। यह सुविधा Aaho के विशिष्ट साझीदारों के लिए बिल्कुल मुफ्त है. धन्यवाद.\n आपका Username: {}  और Password: {}  है.".format(row['username'],row['password'])
        print(sms_template,row['phone'])
        send_sms(message=sms_template,mobiles=row['phone'])