import json
from datetime import datetime, date

from django.db.models import Q

from api.utils import financial_year_yy, to_int, int_or_none

from owner.vehicle_util import compare_format, display_format
from restapi.serializers.sme import ConsignorConsigneeSerializer
from restapi.serializers.supplier import SupplierVehicleSerializer, VehicleSerializer, DriverVehicleSerializer
from restapi.utils import get_or_none, to_float, is_blank, django_date_format
from sme.models import Sme, ContractRoute, ConsignorConsignee
# from team.helper.helper import is_blank, to_float, django_date_format
from supplier.models import Supplier, SupplierVehicle, Driver, DriverPhone, DriverVehicle, Vehicle
from team.models import LrNumber, ManualBooking, DebitNoteSupplier
from utils.models import AahoOffice, VehicleCategory, City, Bank

AAHO_OFFICE_MUMBAI = 1
AAHO_OFFICE_AHMEDABAD = 1
AAHO_OFFICE_VIZAG = 1
AAHO_OFFICE_RAIPUR = 1
AAHO_OFFICE_HALDIA = 1


def supplier_deductions(gst_liability, supplier, source_office, destination_office, supplier_charged_weight,
                        supplier_rate, company):
    freight_to_owner = to_int(to_float(supplier_charged_weight) * to_float(supplier_rate))
    sme = get_or_none(Sme, id=company)
    company_code = sme.company_code if isinstance(sme, Sme) else None
    source_office_id = to_int(source_office)
    destination_office_id = to_int(destination_office)
    destination_office = get_or_none(AahoOffice, id=destination_office_id)
    if source_office_id == 2 and destination_office_id == 3:
        if gst_liability != 'exempted':
            try:
                booking = ManualBooking.objects.filter(
                    source_office_id=2, destination_office_id=3, supplier=supplier).exclude(
                    gst_liability='exempted').latest('created_on')
            except ManualBooking.DoesNotExist:
                booking = None

            data = {
                'commission': {
                    'amount': booking.commission if booking else 0,
                    'editable': True if booking else True
                },
                'lr_cost': {
                    'amount': 200,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 200,
                    'editable': True
                },
            }
        elif company_code in ['JSM', 'CNS']:
            try:
                booking = ManualBooking.objects.filter(
                    source_office_id=2, destination_office_id=3, supplier=supplier, company_code=company_code,
                    gst_liability='exempted').latest('created_on')
            except ManualBooking.DoesNotExist:
                booking = None

            data = {
                'commission': {
                    'amount': booking.commission if booking else 0,
                    'editable': True if booking else True
                },
                'lr_cost': {
                    'amount': 200,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 0,
                    'editable': True
                },
            }
        else:
            try:
                booking = ManualBooking.objects.filter(
                    source_office_id=2, destination_office_id=3, supplier=supplier, gst_liability='exempted').latest(
                    'created_on')

            except ManualBooking.DoesNotExist:
                booking = None

            data = {
                'commission': {
                    'amount': booking.commission if booking else 0,
                    'editable': True if booking else True
                },
                'lr_cost': {
                    'amount': 200,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 350,
                    'editable': True
                },
            }
    elif source_office_id == 2 and destination_office_id == 1:
        data = {
            'commission': {
                'amount': 1000,
                'editable': True
            },
            'lr_cost': {
                'amount': 200,
                'editable': True
            },
            'deduction_for_advance': {
                'amount': 0,
                'editable': True
            },
            'deduction_for_balance': {
                'amount': 0,
                'editable': True
            },
        }
    elif source_office_id == 2:
        try:
            booking = ManualBooking.objects.filter(
                source_office_id=2,
                destination_office_id=destination_office.id if isinstance(destination_office, AahoOffice) else 1,
                supplier=supplier
            ).exclude(destination_office_id__in=[1, 3]).latest('created_on')
        except ManualBooking.DoesNotExist:
            booking = None
        data = {
            'commission': {
                'amount': booking.commission if booking else 0,
                'editable': True if booking else True
            },
            'lr_cost': {
                'amount': 200,
                'editable': True
            },
            'deduction_for_advance': {
                'amount': 0,
                'editable': True
            },
            'deduction_for_balance': {
                'amount': 0,
                'editable': True
            },
        }
    elif source_office_id == 3:
        data = {
            'commission': {
                'amount': 0,
                'editable': True
            },
            'lr_cost': {
                'amount': 200,
                'editable': True
            },
            'deduction_for_advance': {
                'amount': 0,
                'editable': True
            },
            'deduction_for_balance': {
                'amount': 200,
                'editable': True
            },
        }
    elif source_office_id == 1:
        if freight_to_owner < 10000:
            data = {
                'commission': {
                    'amount': 0,
                    'editable': True
                },
                'lr_cost': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 100,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 0,
                    'editable': True
                },
            }
        elif 10000 <= freight_to_owner < 30000:
            data = {
                'commission': {
                    'amount': 0,
                    'editable': True
                },
                'lr_cost': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 200,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 0,
                    'editable': True
                },
            }
        elif 30000 <= freight_to_owner < 70000:
            data = {
                'commission': {
                    'amount': 0,
                    'editable': True
                },
                'lr_cost': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 300,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 0,
                    'editable': True
                },
            }
        else:
            data = {
                'commission': {
                    'amount': 0,
                    'editable': True
                },
                'lr_cost': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 400,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 0,
                    'editable': True
                }
            }
    else:
        data = {
            'commission': {
                'amount': 0,
                'editable': True
            },
            'lr_cost': {
                'amount': 0,
                'editable': True
            },
            'deduction_for_advance': {
                'amount': 0,
                'editable': True
            },
            'deduction_for_balance': {
                'amount': 0,
                'editable': True
            }
        }
    return data


def office_code(office):
    if isinstance(office, AahoOffice) and office.id == 1:
        lr_code = '0'
    elif isinstance(office, AahoOffice) and office.id == 2:
        lr_code = '1'
    elif isinstance(office, AahoOffice) and office.id == 3:
        lr_code = '2'
    elif isinstance(office, AahoOffice) and office.id == 4:
        lr_code = '3'
    elif isinstance(office, AahoOffice) and office.id == 5:
        lr_code = '4'
    elif isinstance(office, AahoOffice) and office.id == 6:
        lr_code = '5'
    elif isinstance(office, AahoOffice) and office.id == 8:
        lr_code = '6'
    elif isinstance(office, AahoOffice) and office.id == 9:
        lr_code = '7'
    else:
        lr_code = '9'
    return lr_code


def get_lr_numbers(booking, source_office, destination_office, shipment_datetime, company_code, number_of_lr,
                   created_by):
    if company_code in ['IDK', 'IDR', 'IDS', 'IDL', 'IDH']:
        company_code = 'IDL'
    lr_numbers = []
    date_str = shipment_datetime.strftime("%y%m%d") if isinstance(shipment_datetime, date) else '000000'
    for value in range(number_of_lr):
        if Sme.objects.filter(company_code__iexact=company_code, lr_format_type='S').exists():
            lr = LrNumber.objects.filter(lr_number__istartswith=company_code).latest('id')
            lr_number = '{}{}{}'.format(
                company_code.upper(),
                office_code(source_office),
                '{0:04d}'.format(
                    to_int(lr.lr_number[4:]) + 1 if isinstance(lr, LrNumber) and len(lr.lr_number) == 8 else 1)
            )
            for i in range(2, 9999999):
                if LrNumber.objects.filter(lr_number__iexact=lr_number).exists():
                    lr_number = '{}{}{}'.format(
                        company_code.upper(),
                        office_code(source_office),
                        '{0:04d}'.format(
                            to_int(lr.lr_number[4:]) + i if isinstance(lr, LrNumber) and len(lr.lr_number) == 8 else 1)
                    )
                    continue
                break
        else:
            try:
                lr = LrNumber.objects.filter(
                    datetime__date=shipment_datetime,
                    source_office=source_office
                ).latest('id')
                lr_number = '{}{}{}{}'.format(
                    company_code.upper(),
                    date_str,
                    office_code(source_office),
                    '{0:02d}'.format(to_int(lr.lr_number[10:]) + 1)
                )
                for i in range(2, 9999999):
                    if LrNumber.objects.filter(lr_number__iexact=lr_number).exists():
                        lr_number = '{}{}{}{}'.format(
                            company_code.upper(),
                            date_str,
                            office_code(source_office),
                            '{0:02d}'.format(to_int(lr.lr_number[10:]) + i)
                        )
                        continue
                    break
            except LrNumber.DoesNotExist:
                lr_number = '{}{}{}{}'.format(
                    company_code.upper(),
                    date_str,
                    office_code(source_office),
                    '01'
                )
        lr_numbers.append(lr_number)
        LrNumber.objects.create(
            booking=booking,
            lr_number=lr_number,
            datetime=shipment_datetime,
            destination_office=destination_office,
            source_office=source_office,
            created_by=created_by,
            changed_by=created_by
        )
    return lr_numbers


def full_booking_id():
    if datetime.today().date() < date(2018, 3, 26):
        try:
            booking = ManualBooking.objects.filter(Q(booking_id__istartswith='AH') | Q(
                booking_id__istartswith='AAHO')).latest('created_on')
            id = str(booking.booking_id)
            temp = to_int(id[4:]) + 1
            booking_id = id[0:4] + '{0:05d}'.format(temp)
        except ManualBooking.DoesNotExist:
            booking_id = 'AAHO00001'
    else:
        try:
            booking = ManualBooking.objects.filter(
                Q(booking_id__istartswith='AH') | Q(booking_id__istartswith='AAHO')).latest('created_on')
            temp = to_int(booking.booking_id[4:]) + 1
            booking_id = 'AH' + str(financial_year_yy(datetime.today().date())) + '{0:05d}'.format(temp)
        except ManualBooking.DoesNotExist:
            booking_id = 'AH' + str(financial_year_yy(datetime.today().date())) + '00001'
    return booking_id


def commission_booking_id():
    if datetime.today().date() < date(2018, 3, 26):
        try:
            booking = ManualBooking.objects.filter(Q(booking_id__istartswith='AB') | Q(
                booking_id__istartswith='BROKER')).latest('created_on')
            ids = str(booking.booking_id)
            temp = int(ids[6:]) + 1
            booking_id = ids[0:6] + '{0:05d}'.format(temp)
        except ManualBooking.DoesNotExist:
            booking_id = 'BROKER00001'
    else:
        try:
            booking = ManualBooking.objects.filter(
                Q(booking_id__istartswith='BROKER') | Q(booking_id__istartswith='AB')).latest('created_on')
            id = str(booking.booking_id)
            temp = to_int(id[4:]) + 1 if booking.booking_id.startswith('AB') else int(booking.booking_id[6:]) + 1
            booking_id = 'AB' + str(financial_year_yy(datetime.today().date())) + '{0:05d}'.format(temp)
        except ManualBooking.DoesNotExist:
            booking_id = 'AB' + str(financial_year_yy(datetime.today().date())) + '00001'
    return booking_id


def get_contract_party_rate(from_city, to_city, customer):
    if not (isinstance(customer, Sme) and isinstance(to_city, City) and isinstance(from_city, City)):
        return None
    if ContractRoute.objects.filter(contract__customer__id=customer.id, source=from_city,
                                    destination=to_city).exists():
        active_contract = ContractRoute.objects.filter(contract__customer__id=customer.id, source=from_city,
                                                       destination=to_city).exclude(rate=None).last()
        party_rate = active_contract.rate
    else:
        party_rate = None
    return party_rate


def update_vehicle(vehicle_number, supplier_id, owner_id, driver_id, vehicle_category_id, user):
    vehicle = get_or_none(Vehicle, vehicle_number=compare_format(vehicle_number))
    supplier = get_or_none(Supplier, id=supplier_id)
    owner = get_or_none(Supplier, id=owner_id)
    driver = get_or_none(Driver, id=driver_id)
    vehicle_type = get_or_none(VehicleCategory, id=vehicle_category_id)
    if not isinstance(vehicle, Vehicle):
        vehicle_serializer = VehicleSerializer(
            data={'vehicle_number': compare_format(vehicle_number),
                  'vehicle_type': vehicle_type.id if isinstance(vehicle_type, VehicleCategory) else None,
                  'created_by': user,
                  'changed_by': user})
        if vehicle_serializer.is_valid():
            vehicle = vehicle_serializer.save()
        else:
            return False
    if isinstance(vehicle, Vehicle):
        if not isinstance(vehicle.vehicle_type, VehicleCategory) and isinstance(vehicle_type, VehicleCategory):
            vehicle_serializer = VehicleSerializer(instance=vehicle, partial=True,
                                                   data={'vehicle_type': vehicle_type.id})
            if vehicle_serializer.is_valid():
                vehicle_serializer.save()
            else:
                return False
        if isinstance(owner, Supplier) and not SupplierVehicle.objects.filter(
                vehicle=vehicle, ownership='O', active=True).exists():

            supplier_vehicle_serializer = SupplierVehicleSerializer(data={
                'ownership': 'O', 'supplier': owner_id, 'vehicle': vehicle.id, 'created_by': user,
                'changed_by': user})
            if supplier_vehicle_serializer.is_valid():
                supplier_vehicle_serializer.save()
            else:
                return False
        if supplier != owner and isinstance(supplier, Supplier) and not SupplierVehicle.objects.filter(
                vehicle=vehicle, supplier=supplier, ownership='B',
                active=True).exists() and not SupplierVehicle.objects.filter(
            vehicle=vehicle, supplier=supplier, ownership='O', active=True).exists():
            supplier_vehicle_serializer = SupplierVehicleSerializer(data={
                'ownership': 'B', 'supplier': supplier_id, 'vehicle': vehicle.id, 'created_by': user,
                'changed_by': user})
            if supplier_vehicle_serializer.is_valid():
                supplier_vehicle_serializer.save()
            else:
                return False
        if isinstance(driver, Driver) and not DriverVehicle.objects.filter(
                driver=driver, vehicle=vehicle, active=True).exists():
            driver_vehicle_serializer = DriverVehicleSerializer(
                data={'driver': driver.id, 'vehicle': vehicle.id, 'active': True, 'created_by': user,
                      'changed_by': user})
            if driver_vehicle_serializer.is_valid():
                driver_vehicle_serializer.save()
            else:
                return False
    else:
        return False
    return True


def booking_create_data(data):
    customer = get_or_none(Sme, id=data.get('customer_placed_order'))
    source_office = get_or_none(AahoOffice, id=data.get('source_office'))
    destination_office = get_or_none(AahoOffice, id=data.get('destination_office'))
    if (isinstance(source_office, AahoOffice) and isinstance(destination_office, AahoOffice)) and (
            source_office == '2' or source_office == '3' or destination_office == '2' or destination_office == '3'):
        is_advance = data.get('is_print_payment_mode_instruction')
    else:
        is_advance = None

    shipment_date = None if not data.get('shipment_datetime') or is_blank(
        data.get('shipment_datetime')) else datetime.strptime(
        data.get('shipment_datetime'), '%d-%b-%Y %I:%M %p')

    update_vehicles = update_vehicle(
        vehicle_number=data.get('vehicle_number', None),
        supplier_id=data.get('supplier_id', None),
        owner_id=data.get('truck_owner_id', None),
        driver_id=data.get('truck_driver_id', None),
        vehicle_category_id=data.get('vehicle_category_id', None),
        user=data.get('user', None)
    )
    supplier = get_or_none(Supplier, id=data.get('supplier_id', None))
    owner = get_or_none(Supplier, id=data.get('truck_owner_id', None))
    driver = get_or_none(Driver, id=data.get('truck_driver_id', None))
    vehicle = get_or_none(Vehicle, vehicle_number=compare_format(data.get('vehicle_number', None)))
    vehicle_type = get_or_none(VehicleCategory, id=data.get('vehicle_category_id', None))

    generate_booking_and_finish = data.get('generate-booking-and-finish')
    if generate_booking_and_finish == 'quick_full_booking':
        booking_id = full_booking_id()
        deductions = supplier_deductions(
            source_office=data.get('source_office', None),
            destination_office=data.get('destination_office', None),
            supplier_charged_weight=data.get('supplier_charged_weight', None),
            supplier_rate=data.get('supplier_rate', None),
            company=data.get('customer_placed_order', None),
            gst_liability=data.get('gst_liability', None),
            supplier=data.get('supplier_id', None),
        )
        commission = deductions['commission']['amount']
        lr_cost = deductions['lr_cost']['amount']
        deduction_for_advance = deductions['deduction_for_advance']['amount']
        deduction_for_balance = deductions['deduction_for_balance']['amount']
        amount_to_owner = to_int(data.get('total_amount_to_owner', 0)) - (
                commission + lr_cost + deduction_for_advance + deduction_for_balance)
    elif generate_booking_and_finish == 'quick_commission_booking':
        booking_id = commission_booking_id()
        commission = 0
        lr_cost = 0
        deduction_for_advance = 0
        deduction_for_balance = 0
        amount_to_owner = to_int(data.get('total_amount_to_owner', 0)) - (
                commission + lr_cost + deduction_for_advance + deduction_for_balance)

    elif generate_booking_and_finish == 'detailed_full_booking' or generate_booking_and_finish == 'detailed_commission_booking':
        if generate_booking_and_finish == 'detailed_commission_booking':
            booking_id = commission_booking_id()
        else:
            booking_id = full_booking_id()
        commission = data.get('commission')
        lr_cost = data.get('lr_cost')
        deduction_for_advance = data.get('deduction_for_advance')
        deduction_for_balance = data.get('deduction_for_balance')
        amount_to_owner = to_int(data.get('freight_owner', 0)) + (
                to_int(data.get('loading_charge', 0)) + to_int(data.get('unloading_charge', 0)) + to_int(
            data.get('detention_charge')) + to_int(
            data.get('additional_charges_for_owner', 0))) - (
                                  commission + lr_cost + deduction_for_advance + deduction_for_balance + to_int(
                              data.get('other_deduction', 0)))

    else:
        booking_id = full_booking_id()
        commission = data.get('commission', 0)
        lr_cost = data.get('lr_cost', 0)
        deduction_for_advance = data.get('deduction_for_advance', 0)
        deduction_for_balance = data.get('deduction_for_balance', 0)
        amount_to_owner = to_int(data.get('total_amount_to_owner', 0)) + (
                to_int(data.get('loading_charge')) + to_int(data.get('unloading_charge')) + to_int(
            data.get('detention_charge')) + to_int(data.get('additional_charges_for_owner'))) - (
                                  commission + lr_cost + deduction_for_advance + deduction_for_balance)

    from_city = get_or_none(City, id=data.get('from_city'))
    if isinstance(from_city, City):
        from_city_fk = from_city
        from_city = from_city.name

    else:
        from_city = None
        from_city_fk = None
    to_city = get_or_none(City, id=data.get('to_city'))
    if isinstance(to_city, City):
        to_city_fk = to_city
        to_city = to_city.name
    else:
        to_city = None
        to_city_fk = None
    consignor_city = get_or_none(City, id=data.get('consignor_city'))
    if isinstance(consignor_city, City):
        consignor_city_fk = consignor_city
        consignor_city = consignor_city.name
    else:
        consignor_city_fk = None
        consignor_city = None
    consignee_city = get_or_none(City, id=data.get('consignee_city'))
    if isinstance(consignee_city, City):
        consignee_city_fk = consignee_city
        consignee_city = consignee_city.name
    else:
        consignee_city_fk = None
        consignee_city = None

    if get_contract_party_rate(from_city=from_city_fk, to_city=to_city_fk,
                               customer=customer):
        party_rate = get_contract_party_rate(from_city=from_city_fk, to_city=to_city_fk, customer=customer)
        party_weight = to_float(data.get('charged_weight'))
        total_amount_to_party = party_rate * party_weight
    else:
        party_rate = data.get('party_rate')
        party_weight = to_float(data.get('charged_weight'))
        total_amount_to_party = data.get('total_amount_to_party', 0)
    data = {
        'booking_id': booking_id,
        'company': data.get('customer_placed_order', None),
        'company_code': customer.company_code if isinstance(customer, Sme) else None,
        'customer_to_be_billed_to': data.get('customer_to_be_billed', None),
        'to_be_billed_to': data.get('to_be_billed_to', None),
        'source_office': source_office.id if isinstance(source_office, AahoOffice) else None,
        'destination_office': destination_office.id if isinstance(destination_office, AahoOffice) else None,
        'supplier': data.get('supplier_id', None),
        'owner_supplier': data.get('truck_owner_id', None),
        'invoice_status': data.get('invoice_status', None),
        'truck_broker_owner_name': supplier.name if isinstance(supplier, Supplier) else None,
        'truck_broker_owner_phone': supplier.phone if isinstance(supplier, Supplier) else None,
        'truck_owner_name': owner.name if isinstance(owner, Supplier) else None,
        'truck_owner_phone': owner.phone if isinstance(owner, Supplier) else None,
        'driver_supplier': data.get('truck_driver_id', None),
        'driver_name': driver.name if isinstance(driver, Driver) else None,
        'driver_phone': driver.phone if isinstance(driver, Driver) else None,
        'driver_dl_number': driver.driving_licence_number if isinstance(driver,
                                                                        Driver) and driver.driving_licence_number else None,
        'driver_dl_validity': driver.driving_licence_validity if isinstance(driver, Driver) else None,
        'is_advance': data.get('is_print_payment_mode_instruction', None),
        'consignor_name': data.get('consignor_name', None),
        'consignor_address': data.get('consignor_address', None),
        'consignor_city': consignor_city,
        'consignor_city_fk': data.get('consignor_city', None),
        'consignor_pin': data.get('consignor_pin', None),
        'consignor_phone': data.get('consignor_phone', None),
        'consignor_gstin': data.get('consignor_gstin', None),
        'consignee_name': data.get('consignee_name', None),
        'consignee_address': data.get('consignee_address', None),
        'consignee_city': consignee_city,
        'consignee_city_fk': data.get('consignee_city', None),
        'consignee_pin': data.get('consignee_pin', None),
        'consignee_phone': data.get('consignee_phone', None),
        'consignee_gstin': data.get('consignee_gstin', None),
        'party_invoice_number': data.get('party_invoice_number', None),
        'party_invoice_date': data.get('party_invoice_date'),
        'party_invoice_amount': to_float(data.get('party_invoice_amount')),
        'road_permit_number': data.get('road_permit_number', None),
        'shipment_date': shipment_date.date() if isinstance(shipment_date, datetime) else None,
        'billing_type': data.get('billing_type', None),
        'number_of_package': data.get('number_of_package', None),
        'material': data.get('material', None),
        'from_city': from_city,
        'from_city_fk': data.get('from_city', None),
        'to_city': to_city,
        'to_city_fk': data.get('to_city', None),
        'liability_of_service_tax': data.get('liability_of_service_tax', None),
        'lorry_number': vehicle.vehicle_number if isinstance(vehicle, Vehicle) else None,
        'vehicle': vehicle.id if isinstance(vehicle, Vehicle) else None,
        'type_of_vehicle': vehicle_type.vehicle_category if vehicle_type else '',
        'vehicle_category': data.get('vehicle_category_id', None),
        'gst_liability': data.get('gst_liability', None),
        'comments': data.get('comments', None),
        'invoice_summary': data.get('invoice_summary', None),
        'loading_charge': data.get('loading_charge', 0),
        'unloading_charge': data.get('unloading_charge', 0),
        'detention_charge': data.get('detention_charge', 0),
        'additional_charges_for_owner': data.get('additional_charges_for_owner', 0),
        'note_for_additional_owner_charges': data.get('note_for_additional_owner_charges', None),
        'commission': commission,
        'lr_cost': lr_cost,
        'deduction_for_advance': deduction_for_advance,
        'deduction_for_balance': deduction_for_balance,
        'other_deduction': data.get('other_deduction', 0),
        'remarks_about_deduction': data.get('remarks_about_deduction'),
        'loaded_weight': to_float(data.get('loaded_weight')),
        'supplier_charged_weight': to_float(data.get('supplier_charged_weight')),
        'supplier_rate': data.get('supplier_rate'),
        'total_amount_to_owner': amount_to_owner,
        'charged_weight': to_float(data.get('charged_weight', 0)),
        'party_rate': party_rate,
        'total_amount_to_company': total_amount_to_party,
        'refund_amount': data.get('refundable_amount', 0),
        'additional_charges_for_company': data.get('additional_charges_for_company', 0),
        'deductions_for_company': data.get('deductions_for_company', 0),
        'invoice_remarks_for_deduction_discount': data.get('invoice_remarks_for_deduction_discount', None),
        'advance_amount_from_company': data.get('advance_from_company', 0),
        'invoice_remarks_for_additional_charges': data.get('invoice_remarks_for_additional_charges', None),
        'tds_deducted_amount': data.get('tds_deducted_amount', 0),
        'insurance_provider': data.get('insurance_provider', None),
        'insurance_policy_number': data.get('insurance_policy_number', None),
        'insured_amount': data.get('insurance_amount', 0),
        'insurance_date': data.get('insurance_date', None),
        'inward_payment_status': data.get('inward_payment_status', 'no_payment'),
        'pod_status': data.get('pod_status', 'pending'),
        'outward_payment_status': data.get('outward_payment_status', 'no_payment_made'),
        'pod_date': data.get('pod_date', None),
        'tds_certificate_status': data.get('tds_certificate_status', 'n'),
        'invoice_number': data.get('invoice_number', None),
        'insurance_risk': data.get('insurance_risk', None),
        'is_insured': data.get('insured', None) == 'insured',
        'consignee_cst_tin': data.get('consignee_cst_tin', None),
        'billing_invoice_date': data.get('billing_invoice_date', None),
        'created_by': data.get('user', None),
        'changed_by': data.get('user', None),
        'loading_points': data.get('loading_points', None),
        'unloading_points': data.get('unloading_points', None),
        'is_print_payment_mode_instruction': data.get('is_print_payment_mode_instruction', None) == 'yes'
    }
    return data


def detailed_full_booking_page_data(data):
    from_city = get_or_none(City, id=data.get('from_city', None))
    to_city = get_or_none(City, id=data.get('to_city', None))
    customer_placed_order = get_or_none(Sme, id=data.get('customer_placed_order', None))
    customer_billed = get_or_none(Sme, id=data.get('customer_to_be_billed', None))
    vehicle_category = get_or_none(VehicleCategory, id=data.get('vehicle_category_id', None))
    truck_driver = get_or_none(Driver, id=data.get('truck_driver_id', None))
    # broker = get_or_none(Broker, id=data.get('supplier_id', None))
    # owner = get_or_none(Owner, id=data.get('truck_owner_id', None))
    source_office_obj = get_or_none(AahoOffice, id=data.get('source_office', None))
    destination_office_obj = get_or_none(AahoOffice, id=data.get('destination_office', None))
    if isinstance(customer_placed_order, Sme):
        consignor = customer_placed_order.consignorconsignee_set.filter(type='consignor').last()
        consignee = customer_placed_order.consignorconsignee_set.filter(type='consignee').last()
        if isinstance(consignor, ConsignorConsignee):
            data['consignor'] = ConsignorConsigneeSerializer(consignor).data
        if isinstance(consignee, ConsignorConsignee):
            data['consignee'] = ConsignorConsigneeSerializer(consignee).data

    data['from_city'] = {'id': from_city.id, 'name': from_city.name, 'state': from_city.state} if isinstance(from_city,
                                                                                                             City) else {}
    data['to_city'] = {'id': to_city.id, 'name': to_city.name, 'state': to_city.state} if isinstance(to_city,
                                                                                                     City) else {}
    data['customer_placed_order'] = {'id': customer_placed_order.id,
                                     'name': customer_placed_order.get_name()} if isinstance(customer_placed_order,
                                                                                             Sme) else {}
    data['customer_billed'] = {'id': customer_billed.id,
                               'name': customer_billed.get_name()} if isinstance(customer_billed,
                                                                                 Sme) else {}
    data['vehicle_category'] = {'id': vehicle_category.id, 'type': vehicle_category.vehicle_type} \
        if isinstance(vehicle_category, VehicleCategory) else {}
    data['truck_driver'] = {'id': truck_driver.id, 'name': truck_driver.name} \
        if isinstance(truck_driver, Driver) else {}
    # data['supplier'] = {'id': broker.id, 'name': broker.get_name()} \
    #     if isinstance(broker, Broker) else {}
    # data['owner'] = {'id': owner.id, 'name': owner.get_name()} \
    #     if isinstance(owner, Owner) else {}
    data['source_office_obj'] = {'id': source_office_obj.id, 'name': source_office_obj.branch_name} \
        if isinstance(source_office_obj, AahoOffice) else {}
    data['destination_office_obj'] = {'id': destination_office_obj.id, 'name': destination_office_obj.branch_name} \
        if isinstance(destination_office_obj, AahoOffice) else {}

    data['supplier_deductions'] = supplier_deductions(
        source_office=data.get('source_office', None),
        destination_office=data.get('destination_office', None),
        supplier_charged_weight=data.get('supplier_charged_weight', None),
        supplier_rate=data.get('supplier_rate', None),
        company=data.get('customer_placed_order', None),
        gst_liability=data.get('gst_liability', None),
        supplier=data.get('supplier_id', None),
    )
    return data


def detailed_commission_booking_page_data(data):
    from_city = get_or_none(City, id=data.get('from_city', None))
    to_city = get_or_none(City, id=data.get('to_city', None))
    customer_placed_order = get_or_none(Sme, id=data.get('customer_placed_order', None))
    data['from_city'] = {
        'id': from_city.id, 'name': from_city.name, 'state': from_city.state} if isinstance(from_city, City) else {}
    data['to_city'] = {
        'id': to_city.id, 'name': to_city.name, 'state': to_city.state} if isinstance(to_city, City) else {}
    data['customer_placed_order'] = {
        'id': customer_placed_order.id, 'name': customer_placed_order.get_name()} if isinstance(customer_placed_order,
                                                                                                Sme) else {}
    data['supplier_deductions'] = supplier_deductions(
        source_office=data.get('source_office', None),
        destination_office=data.get('destination_office', None),
        supplier_charged_weight=data.get('supplier_charged_weight', None),
        supplier_rate=data.get('supplier_rate', None),
        company=data.get('customer_placed_order', None),
        gst_liability=data.get('gst_liability', None),
        supplier=data.get('supplier_id', None),
    )
    return data


def update_booking_field(data):
    booking = get_or_none(ManualBooking, id=data['booking_id'])
    booking.customer_to_be_billed_to = get_or_none(Sme, id=int_or_none(data['to_be_billed_to']))
    booking.save()


def parse_create_confirmed_booking_lr_data(data, existing_booking=None):
    consignor_city = get_or_none(City, id=data.get('consignor_city', None))
    if isinstance(consignor_city, City):
        consignor_city_fk = consignor_city
        consignor_city = consignor_city.name
    else:
        consignor_city_fk = None
        consignor_city = None
    consignee_city = get_or_none(City, id=data.get('consignee_city', None))
    if isinstance(consignee_city, City):
        consignee_city_fk = consignee_city
        consignee_city = consignee_city.name
    else:
        consignee_city_fk = None
        consignee_city = None
    return_response = {
        'consignor_name': data.get('consignor_name', None),
        'consignor_address': data.get('consignor_address', None),
        'consignor_city': consignor_city,
        'consignor_city_fk': consignor_city_fk.id if isinstance(consignor_city_fk, City) else None,
        'consignor_pin': data.get('consignor_pin', None),
        'consignor_phone': data.get('consignor_phone', None),
        'consignor_gstin': data.get('consignor_gstin', None),
        'consignee_name': data.get('consignee_name', None),
        'consignee_address': data.get('consignee_address', None),
        'consignee_city': consignee_city,
        'consignee_city_fk': consignee_city_fk.id if isinstance(consignee_city_fk, City) else None,
        'consignee_pin': data.get('consignee_pin', None),
        'consignee_phone': data.get('consignee_phone', None),
        'consignee_gstin': data.get('consignee_gstin', None),
        'number_of_package': data.get('number_of_package', None),
        'material': data.get('material', None),
        'party_invoice_number': data.get('party_invoice_number', None),
        'party_invoice_date': django_date_format(data.get('party_invoice_date')).date() if data.get(
            'party_invoice_date', None) else None,
        'party_invoice_amount': data.get('party_invoice_amount', None),
        'road_permit_number': data.get('road_permit_number', None),
        'loading_charge': data.get('loading_charge', 0),
        'unloading_charge': data.get('unloading_charge', 0),
        'detention_charge': data.get('detention_charge', 0),
        'additional_charges_for_owner': data.get('additional_charges_for_owner', 0),
        'note_for_additional_owner_charges': data.get('note_for_additional_owner_charges', None),
        'commission': data.get('commission', 0),
        'lr_cost': data.get('lr_cost', 0),
        'deduction_for_advance': data.get('deduction_for_advance', 0),
        'deduction_for_balance': data.get('deduction_for_balance', 0),
        'other_deduction': data.get('other_deduction', 0),
        'remarks_about_deduction': data.get('remarks_about_deduction', None),
        'supplier_rate': data.get('supplier_rate', 0),
        'party_rate': data.get('party_rate', 0),
        'additional_charges_for_company': data.get('additional_charges_for_company', 0),
        'deductions_for_company': data.get('deductions_for_company', 0),
        'invoice_remarks_for_deduction_discount': data.get('invoice_remarks_for_deduction_discount', None),
        'advance_amount_from_company': data.get('advance_from_company', 0),
        'invoice_remarks_for_additional_charges': data.get('invoice_remarks_for_additional_charges', None),
        'tds_deducted_amount': data.get('tds_deducted_amount', 0),
        'insurance_provider': data.get('insurance_provider', None),
        'insurance_policy_number': data.get('insurance_policy_number', None),
        'insured_amount': to_float(data.get('insurance_amount', None)),
        'booking_status': data.get('booking_status', 'confirmed'),
        'insurance_date': django_date_format(data.get('insurance_date')).date() if data.get('insurance_date',
                                                                                            None) else None,
        'insurance_risk': None,
        'is_insured': data.get('insured', False),
        'supplier_charged_weight': data.get('supplier_charged_weight', 0),
        'loaded_weight': data.get('loaded_weight', 0),
        'charged_weight': data.get('charged_weight', 0),
        'refund_amount': data.get('refundable_amount', 0),
    }
    return_response = merge_existing_booking_data(return_response, existing_booking)
    return return_response


def merge_existing_booking_data(response, booking):
    for k, v in response.items():
        if not v:
            response[k] = getattr(booking, k) if getattr(booking, k) else v
    return response


def get_booking_images(booking):
    data = []
    if isinstance(booking, ManualBooking):
        for doc in booking.podfile_set.filter(verified=True, is_valid=True):
            data.append(
                {'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder, 'url': doc.s3_upload.public_url()})
        for doc in booking.weighingslip_set.filter(verified=True, is_valid=True):
            data.append(
                {'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder, 'url': doc.s3_upload.public_url()})
        vehicle = booking.supplier_vehicle
        if isinstance(vehicle, Vehicle):
            for doc in vehicle.supplier_vehicle_files.all():
                data.append({'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                             'url': doc.s3_upload.public_url()})
        driver = booking.driver_supplier
        if isinstance(driver, Driver):
            for doc in driver.supplier_driver_files.all():
                data.append({'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                             'url': doc.s3_upload.public_url()})
        supplier = booking.accounting_supplier
        if isinstance(supplier, Supplier):
            for doc in supplier.supplier_files.all():
                data.append({'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                             'url': doc.s3_upload.public_url()})
    return data


def get_booking_bank_accounts(booking):
    users = []
    if booking.booking_supplier:
        users.append(booking.booking_supplier.user_id)
    if booking.accounting_supplier:
        users.append(booking.accounting_supplier.user_id)
    if booking.owner_supplier:
        users.append(booking.owner_supplier.user_id)
    if booking.driver_supplier:
        users.append(booking.driver_supplier.user_id)
    banks = []
    for bank in Bank.objects.filter(user_id__in=list(set(users))):
        banks.append({
            'id': bank.id,
            'name': bank.account_holder_name,
            'account_number': bank.account_number,
            'ifsc': bank.ifsc
        })
    return banks


def access_payment_paid_to_supplier(supplier):
    amount = 0
    message_data = []
    for booking in ManualBooking.objects.filter(accounting_supplier=supplier, outward_payment_status='excess').exclude(
            booking_status='cancelled').exclude(supplier=None):
        amount += (-booking.balance_for_supplier)
        message_data.append('{} ({})'.format(booking.booking_id, booking.balance_for_supplier))
    return amount, 'Excess amount of {}  made in {}'.format(amount, ', '.join(message_data))


def debit_amount_to_be_adjusted(supplier):
    if not isinstance(supplier, Supplier):
        return 0
    return sum(
        [dn.amount_to_be_adjusted for dn in DebitNoteSupplier.objects.filter(accounting_supplier=supplier).filter(
            status__in=['approved', 'partial', 'adjusted'])])
