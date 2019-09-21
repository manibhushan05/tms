from __future__ import absolute_import

import random
import string

import pandas as pd
from django.contrib.auth.models import User
from django.db import ProgrammingError

from authentication.models import Profile
from sme.models import Sme
from team.models import ManualBooking


def update_create_city():
    df = pd.read_excel('../../data/Customer Name Cleanup 11.04.18.xlsx')
    created_by = User.objects.get(username='mani@aaho.in')
    for i, row in df.iterrows():

        try:
            sme = Sme.objects.get(company_code__iexact=row['Customer Code'])
            Profile.objects.filter(user=sme.name).update(name=row['Final Name'])
        except Sme.DoesNotExist:
            try:
                user = User.objects.get(username__iexact=row['Customer Code'])
            except User.DoesNotExist:
                user = User.objects.create_user(username=row['Customer Code'].lower() + ''.join(
                    random.choice(string.ascii_lowercase + string.digits) for _ in range(10)), password='hj@yvjGH78')
                Profile.objects.create(user=user, name=row['Final Name'])
            sme = Sme.objects.create(
                name=user,
                company_code=row['Customer Code'],
                gstin=None,
                aaho_poc=None,
                credit_period=None,
                address=None,
                is_gst_applicable='unknown',
                customer_address=None,
                city=None,
                pin=None,
                created_by=created_by
            )
            print(sme)
        except ProgrammingError:
            print(row)


def booking_billed_customer():
    df = pd.read_excel('../../data/Booking Records Sat, Apr 14, 2018, 1244 PM.xlsx')
    for i, row in df.iterrows():
        try:
            booking = ManualBooking.objects.get(booking_id=row['Booking ID'])
            if not booking.customer_to_be_billed_to and row['Billed Cust Code']:
                try:
                    sme=Sme.objects.get(company_code__iexact=row['Billed Cust Code'])
                    booking.customer_to_be_billed_to=sme
                    booking.save()
                    print(booking)
                except (ProgrammingError,Sme.DoesNotExist) as e:
                    pass
        except ManualBooking.DoesNotExist:
            pass
