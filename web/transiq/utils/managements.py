from time import sleep

import pandas as pd
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.utils import json

from owner.models import Vehicle as o_Vehicle
from supplier.models import Vehicle as s_Vehicle
from utils.models import Bank, BankName, City, State, District, SubDistrict, PinCode, Locality, VehicleCategory, \
    CityLocal
from team.models import OutWardPayment, ManualBooking
from django.utils.text import capfirst
from django.utils.encoding import force_text
from googletrans import Translator

def manual_booking_source_dest():
    for booking in ManualBooking.objects.all():
        if SubDistrict.objects.filter(name__icontains=booking.to_city).exists():
            print(SubDistrict.objects.filter(name__icontains=booking.to_city))


def bank_account_user():
    data = []
    for bank in Bank.objects.all():
        try:
            data.append([
                bank.account_number,
                bank.account_holder_name,
                bank.beneficiary_code,
                bank.user.username if bank.user else '',
                bank.user.profile.name if bank.user else '',
                '\n'.join(bank.outwardpayment_set.values_list('paid_to', flat=True)),
                '\n'.join(
                    ['\n'.join(payment.booking_id.values_list('truck_broker_owner_name', flat=True)) for payment in
                     bank.outwardpayment_set.all()]),
                '\n'.join(
                    ['\n'.join(payment.booking_id.values_list('truck_broker_owner_phone', flat=True)) for payment in
                     bank.outwardpayment_set.all()]),
                '\n'.join(['\n'.join(payment.booking_id.values_list('truck_owner_name', flat=True)) for payment in
                           bank.outwardpayment_set.all()]),
                '\n'.join(['\n'.join(payment.booking_id.values_list('truck_owner_phone', flat=True)) for payment in
                           bank.outwardpayment_set.all()])
            ])
        except TypeError:
            data.append([
                bank.account_number,
                bank.account_holder_name,
                bank.beneficiary_code,
                bank.user.username if bank.user else '',
                bank.user.profile.name if bank.user else '',
                '\n'.join(bank.outwardpayment_set.values_list('paid_to', flat=True)),
                '',
                '',
                '',
                ''
            ])

    df = pd.DataFrame(data=data,
                      columns=['Account Number', 'Account Holder Name', 'Beneficiary Code', 'Username', 'Name',
                               'Paid To', 'Supplier Name', 'Supplier Phone', 'Owner Name', 'Owner Phone'])
    df.to_excel('bank_account_users.xlsx', index=False)


def user_details():
    df = pd.DataFrame(data=list(User.objects.values('id', 'username', 'profile__name', 'profile__phone')),
                      columns=['ID', 'Username', 'Name'])
    print (df)


def get_deleted_objects(objs):
    collector = NestedObjects(using='default')
    collector.collect([objs])

    def format_callback(obj):
        opts = obj._meta
        no_edit_link = '%s: %s' % (capfirst(opts.verbose_name),
                                   force_text(obj))
        return no_edit_link

    # to_delete = collector.nested(format_callback)
    to_delete = collector.nested()
    protected = [format_callback(obj) for obj in collector.protected]
    model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}
    return to_delete, model_count, protected


def update_cities_code():
    df = pd.read_excel('../../data/cities v1.0.xlsx')
    print(df.columns)
    for i, row in df.iterrows():
        city = City.objects.get(id=int(row['ID']))
        city.code = row['Code']
        city.save()


def to_str_ignore(str):
    return unicode(str, errors='ignore')


def create_pin_area_directory():
    df = pd.read_csv('../../data/Locality_village_pincode_final_mar-2017.csv')
    user = User.objects.get(username='mani@aaho.in')
    for i, row in df.iterrows():
        try:
            state = State.objects.get(name__iexact=row['StateName'])
            try:
                district = District.objects.get(Q(name__iexact=row['Districtname']) & Q(state=state))
            except District.DoesNotExist:
                district = District.objects.create(name=row['Districtname'], state=state, created_by=user)
            try:
                sub_district = SubDistrict.objects.get(name__iexact=row['Sub-distname'], district=district)
            except SubDistrict.DoesNotExist:
                sub_district = SubDistrict.objects.create(name=row['Sub-distname'], district=district, created_by=user)
            try:
                pin_code = PinCode.objects.get(pin_code=row['Pincode'])
            except PinCode.DoesNotExist:
                pin_code = PinCode.objects.create(pin_code=row['Pincode'], sub_district=sub_district, created_by=user)
            try:
                try:
                    Locality.objects.get(name=to_str_ignore(row['Village/Locality name']),
                                         post_office=to_str_ignore(row['Officename ( BO/SO/HO)']),
                                         pin_code=pin_code)
                except Locality.DoesNotExist:
                    Locality.objects.create(name=to_str_ignore(row['Village/Locality name']),
                                            post_office=to_str_ignore(row['Officename ( BO/SO/HO)']),
                                            pin_code=pin_code, created_by=user)
            except:
                print(row)
        except State.DoesNotExist:
            print(row['StateName'])


def update_vehicle_category():
    o_Vehicle.objects.filter(vehicle_type=VehicleCategory.objects.get(id=85)).update(
        vehicle_type=VehicleCategory.objects.get(id=2))
    # s_Vehicle.objects.filter(vehicle_type=VehicleCategory.objects.get(id=85)).update(
    #     vehicle_type=VehicleCategory.objects.get(id=2))
    ManualBooking.objects.filter(vehicle_category=VehicleCategory.objects.get(id=85)).update(
        vehicle_category=VehicleCategory.objects.get(id=2))


def update_city_local_name1():
    translator = Translator()
    all_cities = City.objects.filter(id__lt=300)
    for city in all_cities:
        if city and len(city.name) > 0 and city.name is not None:
            city_msg_trans = translator.translate(city.name.strip().lstrip().rstrip(), dest='hi')
            CityLocal.objects.create(city=city, hindi_name=city_msg_trans.text)


def update_city_local_name2():
    translator = Translator()
    all_cities = City.objects.filter(id__range=(300, 600))
    for city in all_cities:
        if city and len(city.name) > 0 and city.name is not None:
            city_msg_trans = translator.translate(city.name.strip().lstrip().rstrip(), dest='hi')
            CityLocal.objects.create(city=city, hindi_name=city_msg_trans.text)


def update_city_local_name3():
    translator = Translator()
    all_cities = City.objects.filter(id__range=(601, 900))
    for city in all_cities:
        if city and len(city.name) > 0 and city.name is not None:
            city_msg_trans = translator.translate(city.name.strip().lstrip().rstrip(), dest='hi')
            CityLocal.objects.create(city=city, hindi_name=city_msg_trans.text)


def update_city_local_name4():
    translator = Translator()
    all_cities = City.objects.filter(id__gt=900)
    for city in all_cities:
        if city and len(city.name) > 0 and city.name is not None:
            city_msg_trans = translator.translate(city.name.strip().lstrip().rstrip(), dest='hi')
            CityLocal.objects.create(city=city, hindi_name=city_msg_trans.text)