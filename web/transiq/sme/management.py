import pandas as pd

from authentication.models import Profile
from broker.models import Broker
from restapi.helper_api import get_broker_user_data
from employee.models import Employee
from sme.models import Sme, SmeTaskEmail
from utils.models import AahoOffice, Bank


def update_aaho_office():
    data = []
    for sme in Sme.objects.all():

        offices = sme.mb_bill_order_placed.all()
        if not offices.exists():
            offices = sme.mb_bill_paid_by.all()
        if offices.count() > 0:
            aaho_source_offices = list(offices.values_list('source_office__id', flat=True))
            data = {}
            for office in set(aaho_source_offices):
                data[office] = aaho_source_offices.count(office)
            office_id = max(data.keys(), key=lambda k: data[k])
            aaho_office = AahoOffice.objects.get(id=office_id)
            sme.aaho_office = aaho_office
            sme.save()


def retrieve_sme():
    data = []
    for sme in Sme.objects.all():
        print(sme)
        data.append([
            sme.id,
            sme.get_name(),
            sme.company_code,
            sme.name.profile.email,
            sme.aaho_office.branch_name if sme.aaho_office else '',
            sme.city.name if sme.city else '',
            sme.credit_period
        ])
    df = pd.DataFrame(data=data, columns=['ID', 'Name', 'Code', 'Email', 'Branch', 'City', 'Credit Period'])
    df.to_excel('customers.xlsx', index=False)


def check_wrong_customer():
    df = pd.read_excel('../../data/Customer Name Cleanup 11.04.18.xlsx')
    data = []
    for i, row in df.iterrows():
        try:
            sme = Sme.objects.get(company_code=row['Customer Code'])
            if row['Final Name'] != sme.get_name():
                profile = Profile.objects.get(user=sme.name)
                profile.name = row['Final Name']
                profile.save()
            data.append([
                row['Customer Code'],
            ])
        except Sme.DoesNotExist:
            print(row, i)


def update_sme_email():
    for sme in Sme.objects.exclude(company_code__in=['IDL', 'IDS', 'IDR', 'IDH', 'IDK']):
        for sme_task in SmeTaskEmail.objects.all():
            sme.email_tasks.add(sme_task)



def get_broker_data(user):
    try:
        broker = Broker.objects.get(name=user)
    except Broker.DoesNotExist:
        return {'status': 'failure', 'msg': 'User Broker does not exist', 'data': {}}
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user, name=user.first_name, email=user.email)
    accounts = Bank.objects.filter(user=user)
    accounts_data = []
    for ac in accounts:
        ac_data = ac.to_json()
        accounts_data.append(ac_data)
    data = {
        'user': get_broker_user_data(user, profile, broker=broker),
        'accounts_data': accounts_data,
        'aaho_office': broker.aaho_office.to_json() if broker.aaho_office else {},
    }
    return {'status': 'success', 'data': data}


def broker_intital_data_test():
    for broker in Broker.objects.all():
        print(get_broker_data(broker.name))


def update_sme_material():
    df = pd.read_excel('/Users/aaho/Downloads/Customer Thu, Sep 6, 2018, 216 PM.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        if row['Material']:
            try:
                sme = Sme.objects.get(company_code=row['Code'])
                material = row['Material']
                sme.material = material
                sme.save()
            except Sme.DoesNotExist:
                print(row, i)


def update_sme_aaho_office():
    df = pd.read_excel('/Users/aaho/Downloads/Customer POC and Office Update.xlsx', sheet_name='Office Update')
    df = df.fillna('')
    for i, row in df.iterrows():
        if row['Aaho Office']:
            try:
                sme = Sme.objects.get(company_code=row['Code'])
                aaho_office = AahoOffice.objects.get(branch_name=row['Aaho Office'])
                sme.aaho_office = aaho_office
                sme.save()
            except Sme.DoesNotExist:
                print(row, i)


def update_sme_poc():
    df = pd.read_excel('/Users/aaho/Downloads/Customer POC and Office Update.xlsx', sheet_name='POC Update')
    df = df.fillna('')
    for i, row in df.iterrows():
        if row['Aaho POC']:
            try:
                sme = Sme.objects.get(company_code=row['Code'])
                employee = Employee.objects.get(username__profile__name=row['Aaho POC'])
                # print(employee)
                sme.aaho_poc = employee
                sme.save()
            except Sme.DoesNotExist:
                print(row, i)

