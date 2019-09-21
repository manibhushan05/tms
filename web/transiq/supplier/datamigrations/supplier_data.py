from django.db import IntegrityError
from django.db.models import Q, Count
import pandas as pd

from broker.models import Broker
from owner.models import Owner
from supplier.models import Supplier
from django.contrib.postgres.search import TrigramSimilarity


def add_owner_to_supplier():
    Owner.objects.filter(pan='').update(pan=None)
    for owner in Owner.objects.all():
        if owner.manualbooking_set.count() > 0:
            try:
                if not Supplier.objects.filter(
                        Q(user__profile__phone=owner.get_phone()) | Q(pan__iexact=owner.pan)).exists():
                    Supplier.objects.create(user=owner.name, address=owner.owner_address, pin=owner.pin, pan=owner.pan)
            except IntegrityError:
                print(owner.pan)


def add_broker_supplier():
    Owner.objects.filter(pan='').update(pan=None)
    Broker.objects.filter(pan='').update(pan=None)
    owners = Owner.objects.annotate(page_count=Count('manualbooking__id')).filter(page_count__gte=1).values_list(
        'name__username', flat=True)
    for broker in Broker.objects.exclude(name__username__in=owners).annotate(
            page_count=Count('team_booking_broker__id')).filter(page_count__gte=1):
        try:
            Supplier.objects.create(user=broker.name, address=broker.address.full_address() if broker.address else None,
                                    pan=broker.pan.upper() if broker.pan else None, aaho_poc=broker.aaho_poc,
                                    aaho_office=broker.aaho_office, code=broker.code)
        except:
            print(broker)


def owner_data():
    booking_owners = Owner.objects.annotate(page_count=Count('manualbooking__id')).filter(
        page_count__gte=1).values_list('id', flat=True)
    vehicle_owner = Owner.objects.annotate(page_count=Count('vehicle_owner__id')).filter(page_count__gte=1).values_list(
        'id', flat=True)
    # uploaded_docs_owner=Owner.objects.annotate(page_count=Count('owner_files__id')).filter(page_count__gte=1).values_list('id',flat=True)
    # unwanted_owner=Owner.objects.exclude(id__in=list(set(list(booking_owners)+list(vehicle_owner)+list(uploaded_docs_owner))))
    valid_owners = Owner.objects.filter(id__in=list(set(list(booking_owners) + list(vehicle_owner))))

    data = []
    for owner in valid_owners:
        print(owner)
        data.append([
            owner.id,
            owner.name.username,
            owner.get_name(),
            owner.get_phone(),
            owner.pan,
            '\n'.join([vehicle.vehicle_number for vehicle in owner.vehicle_owner.all()]),
            owner.manualbooking_set.latest(
                '-shipment_date').shipment_date if owner.manualbooking_set.count() > 0 else None,
            'Yes' if owner.owner_files.filter(document_category='DEC').exists else 'No',
            'Yes' if owner.owner_files.filter(document_category='PAN').exists else 'No',
            None
        ])
    df = pd.DataFrame(data=data,
                      columns=['id', 'username', 'name', 'phone', 'pan', 'vehicles', 'latest_shipment', 'Declaration',
                               'PAN', 'correct owner'])
    df.to_excel('owner data.xlsx', index=False)


def broker_data():
    booking_owners = Owner.objects.annotate(page_count=Count('manualbooking__id')).filter(
        page_count__gte=1).values_list('id', flat=True)
    vehicle_owner = Owner.objects.annotate(page_count=Count('vehicle_owner__id')).filter(page_count__gte=1).values_list(
        'id', flat=True)
    # uploaded_docs_owner=Owner.objects.annotate(page_count=Count('owner_files__id')).filter(page_count__gte=1).values_list('id',flat=True)
    # unwanted_owner=Owner.objects.exclude(id__in=list(set(list(booking_owners)+list(vehicle_owner)+list(uploaded_docs_owner))))
    valid_owners = Owner.objects.filter(id__in=list(set(list(booking_owners) + list(vehicle_owner)))).values_list('name__username')
    data = []
    for broker in Broker.objects.exclude(name__username__in=valid_owners).annotate(
            page_count=Count('team_booking_broker__id')).filter(page_count__gte=1).order_by('name__profile__name'):
        print(broker)
        data.append([
            broker.id,
            broker.name.username,
            broker.get_name(),
            broker.get_phone(),
            broker.pan,
            broker.vehicles,
            broker.team_booking_broker.latest('-shipment_date').shipment_date,
            broker.aaho_office.branch_name if broker.aaho_office else None,
            broker.aaho_poc_name,
            None
        ])
    df = pd.DataFrame(data=data,
                      columns=['id', 'username', 'name', 'phone', 'pan', 'vehicles', 'latest_shipment', 'Aaho Office',
                               'Aaho POC', 'correct broker'])
    df.to_excel('broker with bookings.xlsx', index=False)


def owner_booking_data():
    Owner.objects.filter(pan='').update(pan=None)
    data = []
    for owner in Owner.objects.all():
        if owner.manualbooking_set.count() > 0:
            data.append([
                owner.id,
                owner.name.username,
                owner.get_name(),
                owner.get_phone(),
                owner.pan,
                '\n'.join([vehicle.vehicle_number for vehicle in owner.vehicle_owner.all()]),
                owner.manualbooking_set.latest('-shipment_date').shipment_date,
                'Yes' if owner.owner_files.filter(document_category='DEC').exists else 'No',
                'Yes' if owner.owner_files.filter(document_category='PAN').exists else 'No'
            ])
    df = pd.DataFrame(data=data,
                      columns=['id', 'username', 'name', 'phone', 'pan', 'vehicles', 'latest_shipment', 'Declaration',
                               'PAN'])
    df.to_excel('owner with bookings.xlsx', index=False)
