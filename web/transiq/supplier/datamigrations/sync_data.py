import pandas as pd

from fileupload.models import DriverFile, OwnerFile, VehicleFile
from supplier.models import Supplier, Vehicle
from team.models import ManualBooking, DebitNoteSupplier, CreditNoteCustomerDirectAdvance, CreditNoteSupplier
from team.payments.accounting import supplier_accounting_summary, vehicle_accounting_summary


def sync_manual_booking_data():
    df = pd.read_excel('static/aaho/data/manual_booking_data.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        print(row['id'])
        ManualBooking.objects.filter(id=row['id']).update(
            booking_supplier_id=row['booking_supplier_id'] if row['booking_supplier_id'] else None,
            accounting_supplier_id=row['accounting_supplier_id'] if row['accounting_supplier_id'] else None,
            owner_supplier_id=row['owner_supplier_id'] if row['owner_supplier_id'] else None,
            driver_supplier_id=row['driver_supplier_id'] if row['driver_supplier_id'] else None,
            supplier_vehicle_id=row['supplier_vehicle_id'] if row['supplier_vehicle_id'] else None,
        )


def sync_dns_data():
    df = pd.read_excel('static/aaho/data/dns_data.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        print(row['id'])
        if Supplier.objects.filter(id=row['accounting_supplier']).exists():
            DebitNoteSupplier.objects.filter(id=row['id']).update(accounting_supplier_id=row['accounting_supplier'] if row['accounting_supplier'] else None)


def sync_cnca_data():
    df = pd.read_excel('static/aaho/data/cnca_data.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        print(row['id'])
        if Supplier.objects.filter(id=row['accounting_supplier']).exists():
            CreditNoteCustomerDirectAdvance.objects.filter(id=row['id']).update(accounting_supplier_id=row['accounting_supplier'] if row['accounting_supplier'] else None)



def sync_cns_data():
    df = pd.read_excel('static/aaho/data/cns_data.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        print(row['id'])
        if Supplier.objects.filter(id=row['accounting_supplier']).exists():
            CreditNoteSupplier.objects.filter(id=row['id']).update(accounting_supplier_id=row['accounting_supplier'] if row['accounting_supplier'] else None)



def sync_driver_file_data():
    df = pd.read_excel('static/aaho/data/driver_file.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        print(row['id'])
        DriverFile.objects.filter(id=row['id']).update(supplier_driver_id=row['s_driver_id'] if row['s_driver_id'] else None)



def sync_owner_file_data():
    df = pd.read_excel('static/aaho/data/owner_file.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        print(row['id'])
        OwnerFile.objects.filter(id=row['id']).update(supplier_id=row['supplier_id'] if row['supplier_id'] else None)



def sync_vehicle_data():
    df = pd.read_excel('static/aaho/data/vehicle_file.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        print(row['id'])
        VehicleFile.objects.filter(id=row['id']).update(supplier_vehicle_id=row['supplier_vehicle_id'] if row['supplier_vehicle_id'] else None)


def sync_supplier_accounnting_summary():
    for supplier in Supplier.objects.all():
        supplier_accounting_summary(supplier=supplier)
        print(supplier)

def sync_vehicle_accounting_summary():
    for vehicle in Vehicle.objects.all():
        print(vehicle)
        vehicle_accounting_summary(vehicle=vehicle)