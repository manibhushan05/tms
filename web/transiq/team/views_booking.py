from __future__ import absolute_import

import json
from datetime import datetime, date

from django.conf import settings
from django.contrib import messages
from django.db.models import Q, F
from django.http import HttpResponseRedirect
from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from django.utils.html import format_html

from api.helper import json_success_response, EMP_GROUP3, EMP_GROUP2
from api.models import S3Upload
from api.utils import get_or_none, int_or_none, financial_year_yy, to_str
from broker.models import Broker, BrokerVehicle
from driver.models import Driver, DriverAppUser, TracknovateGPSDevice, \
    WaytrackerGPSDevice, TempoGoGPSDevice
from owner.models import Vehicle, FuelCard, Owner
from owner.vehicle_util import compare_format, display_format
from report.lr_html import generate_lorry_receipt
from sme.models import Sme, ContractRoute
from team import tasks
from team.decorators import authenticated_user
from team.helper.helper import manual_booking_id_list, django_date_format, to_float, is_blank, to_int
from team.models import InWardPayment, OutWardPayment, LrNumber, Invoice, DebitNoteSupplier
from team.models import ManualBooking
from team.services import booking_edit_data, booking_helper
from utils.models import City, AahoOffice, VehicleCategory, Bank


@authenticated_user
def fetch_full_booking_data_page(request):
    aaho_office = AahoOffice.objects.all()
    context_data = {
        'aaho_office': aaho_office,
    }

    return render(request=request, template_name='team/booking/fetch_full_booking_data_page.html', context=context_data)


@authenticated_user
def full_booking_page(request):
    source_office = get_or_none(AahoOffice, id=int_or_none(request.GET.get('source_office')))
    destination_office = get_or_none(AahoOffice, id=int_or_none(request.GET.get('destination_office')))
    customer = get_or_none(Sme, id=int_or_none(request.GET.get('customer_placed_order')))
    if not (isinstance(customer, Sme) or isinstance(source_office, AahoOffice) or isinstance(
            destination_office, AahoOffice)):
        return HttpResponseRedirect('/team/fetch-full-booking-data-page/')
    customer_to_be_billed = get_or_none(Sme, id=int_or_none(request.GET.get('customer_to_be_billed')))
    truck_driver = get_or_none(Driver, id=int_or_none(request.GET.get('truck_driver_id')))
    supplier = get_or_none(Broker, id=int_or_none(request.GET.get('supplier_id')))
    owner = get_or_none(Owner, id=int_or_none(request.GET.get('truck_owner_id')))
    vehicle_category = get_or_none(VehicleCategory, id=int_or_none(request.GET.get('vehicle_category_id')))
    gst_liability = request.GET.get('gst_liability')

    if customer_to_be_billed and isinstance(customer_to_be_billed, Sme):
        if (
                customer_to_be_billed.is_gst_applicable == 'yes' and not customer_to_be_billed.gstin) or customer_to_be_billed.is_gst_applicable == 'unknown' and gst_liability != 'exempted':
            messages.info(request=request,
                          message="GST details not updated. Please update before creating booking for {}".format(
                              customer_to_be_billed.get_name()))
            return HttpResponseRedirect('/team/fetch-full-booking-data-page/')

    consignor = customer.consignorconsignee_set.filter(type='consignor').last()
    consignee = customer.consignorconsignee_set.filter(type='consignee').last()
    shipment_datetime = request.GET.get('shipment_datetime')
    number_of_lr = request.GET.get('number_of_lr')
    vehicle = get_or_none(Vehicle, vehicle_number=compare_format(request.GET.get('vehicle_number')))

    if isinstance(vehicle, Vehicle):
        vehicle_number = display_format(vehicle.vehicle_number)
    else:
        vehicle_number = display_format(request.GET.get('vehicle_number'))

    from_city = get_or_none(City, id=request.GET.get('from_city'))
    if isinstance(from_city, City):
        from_city = {'id': from_city.id, 'name': from_city.name,
                     'state': from_city.state.name if from_city.state else ''}
    else:
        from_city = None
    to_city = get_or_none(City, id=request.GET.get('to_city'))
    if isinstance(to_city, City):
        to_city = {'id': to_city.id, 'name': to_city.name, 'state': to_city.state.name if to_city.state else ''}
    else:
        to_city = None

    context_data = {
        'source_office': source_office,
        'destination_office': destination_office,
        'customer': customer,
        'shipment_datetime': shipment_datetime,
        'vehicle_number': vehicle_number,
        'number_of_lr': number_of_lr,
        'truck_owner_id': owner.id if isinstance(owner, Owner) else '',
        'truck_driver': truck_driver,
        'supplier': supplier,
        'consignor': consignor,
        'consignee': consignee,
        'vehicle_category_id': vehicle_category.id if isinstance(vehicle_category, VehicleCategory) else '',
        'billing_type': request.GET.get('billing_type'),
        'gst_liability': gst_liability,
        'customer_to_be_billed': customer_to_be_billed,
        'from_city': from_city,
        'to_city': to_city,
        'refund_amount': request.GET.get('refundable_amount'),
        'supplier_weight': request.GET.get('supplier_charged_weight'),
        'supplier_rate': request.GET.get('supplier_rate'),
        'party_weight': request.GET.get('charged_weight'),
        'party_rate': request.GET.get('party_rate'),
        'loaded_weight': request.GET.get('loaded_weight'),
        'generate-booking-and-finish': request.GET.get('generate-booking-and-finish'),
        'is_print_payment_mode_instruction': request.GET.get('is_print_payment_mode_instruction'),
        'supplier_deductions': booking_helper.supplier_deductions(
            source_office=source_office if isinstance(source_office, AahoOffice) else None,
            destination_office=destination_office if isinstance(destination_office, AahoOffice) else None,
            freight_to_owner=to_int(
                to_float(request.GET.get('supplier_charged_weight')) * to_float(request.GET.get('supplier_rate'))
            ),
            company_code=customer.company_code if isinstance(customer, Sme) else None,
            gst_liability=gst_liability,
            supplier=supplier if isinstance(supplier, Broker) else None,
        )
    }
    return render(request=request, template_name='team/booking/full-booking.html', context=context_data)


def check_gps_device_attach(vehicle_number):
    vehicle_number = compare_format(vehicle_number)
    if TracknovateGPSDevice.objects.filter(vehicle_number__iexact=vehicle_number).exists():
        return True
    elif WaytrackerGPSDevice.objects.filter(vehicle_number__iexact=vehicle_number).exists():
        return True
    elif TempoGoGPSDevice.objects.filter(vehicle_number__iexact=vehicle_number).exists():
        return True
    else:
        return False


def update_vehicle(vehicle, supplier, owner, driver, vehicle_category):
    if isinstance(vehicle, Vehicle):
        if isinstance(driver, Driver):
            Vehicle.objects.filter(driver=driver).update(driver=None)
            Vehicle.objects.filter(id=vehicle.id).update(
                driver=driver, owner=owner,
                vehicle_type=vehicle.vehicle_type if not isinstance(vehicle_category,
                                                                    VehicleCategory) else vehicle_category)
        if isinstance(supplier, Broker):
            if not BrokerVehicle.objects.filter(broker=supplier, vehicle=vehicle).exists():
                BrokerVehicle.objects.create(broker=supplier, vehicle=vehicle)


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
    date_str = shipment_datetime.strftime("%y%m%d") if isinstance(shipment_datetime, datetime) else '000000'
    for value in range(number_of_lr):
        if Sme.objects.filter(company_code__iexact=company_code, lr_format_type='S'):
            lr = LrNumber.objects.filter(lr_number__istartswith=company_code).latest('id')
            lr_number = '{}{}{}'.format(
                company_code.upper(),
                office_code(source_office),
                '{0:04d}'.format(to_int(lr.lr_number[4:]) + 1 if isinstance(lr, LrNumber) else 1)
            )
            for i in range(2, 9999999):
                if LrNumber.objects.filter(lr_number__iexact=lr_number).exists():
                    lr_number = '{}{}{}'.format(
                        company_code.upper(),
                        office_code(source_office),
                        '{0:04d}'.format(to_int(lr.lr_number[4:]) + i if isinstance(lr, LrNumber) else 1)
                    )
                    continue
                break
        else:
            try:
                lr = LrNumber.objects.filter(
                    datetime__date=shipment_datetime.date(),
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


def create_full_booking_data(request):
    customer = get_or_none(Sme, id=int_or_none(request.POST.get('customer_placed_order')))
    source_office = get_or_none(AahoOffice, id=int_or_none(request.POST.get('source_office')))
    destination_office = get_or_none(AahoOffice, id=int_or_none(request.POST.get('destination_office')))
    if (isinstance(source_office, AahoOffice) and isinstance(destination_office, AahoOffice)) and (
            source_office == '2' or source_office == '3' or destination_office == '2' or destination_office == '3'):
        is_advance = request.POST.get('is_print_payment_mode_instruction')
    else:
        is_advance = None
    shipment_date = None if is_blank(request.POST.get('shipment_datetime')) else datetime.strptime(
        request.POST.get('shipment_datetime'), '%d-%b-%Y %I:%M %p')
    vehicle = get_or_none(Vehicle, vehicle_number=compare_format(request.POST.get('vehicle_number')))
    vehicle_category = get_or_none(VehicleCategory, id=int_or_none(request.POST.get('vehicle_category_id')))
    supplier = get_or_none(Broker, id=int_or_none(request.POST.get('supplier_id')))
    owner = get_or_none(Owner, id=int_or_none(request.POST.get('truck_owner_id')))
    driver = get_or_none(Driver, id=int_or_none(request.POST.get('truck_driver_id')))
    if isinstance(vehicle, Vehicle):
        update_vehicle(vehicle=vehicle, supplier=supplier, driver=driver, vehicle_category=vehicle_category,
                       owner=owner)
    else:
        Vehicle.objects.filter(driver=driver).update(driver=None)
        vehicle = Vehicle.objects.create(vehicle_number=compare_format(request.POST.get('vehicle_number')),
                                         driver=driver, owner=owner, vehicle_type=vehicle_category)
        if not BrokerVehicle.objects.filter(broker=supplier, vehicle=vehicle).exists():
            BrokerVehicle.objects.create(broker=supplier, vehicle=vehicle)

    generate_booking_and_finish = request.POST.get('generate-booking-and-finish')
    if generate_booking_and_finish == 'quick_full_booking':
        booking_id = full_booking_id()
        deductions = booking_helper.supplier_deductions(
            source_office=source_office if isinstance(source_office, AahoOffice) else None,
            destination_office=destination_office if isinstance(destination_office, AahoOffice) else None,
            freight_to_owner=to_int(
                to_float(request.GET.get('supplier_charged_weight')) * to_float(request.GET.get('supplier_rate'))
            ),
            company_code=customer.company_code if isinstance(customer, Sme) else None,
            gst_liability=request.POST.get('gst_liability', None),
            supplier=supplier if isinstance(supplier, Broker) else None
        )
        commission = to_int(deductions['commission']['amount'])
        lr_cost = to_int(deductions['lr_cost']['amount'])
        deduction_for_advance = to_int(deductions['deduction_for_advance']['amount'])
        deduction_for_balance = to_int(deductions['deduction_for_balance']['amount'])
        amount_to_owner = to_int(request.POST.get('total_amount_to_owner')) - (
                commission + lr_cost + deduction_for_advance + deduction_for_balance)
    elif generate_booking_and_finish == 'quick_commission_booking':
        booking_id = commission_booking_id()
        commission = 0
        lr_cost = 0
        deduction_for_advance = 0
        deduction_for_balance = 0
        amount_to_owner = to_int(request.POST.get('total_amount_to_owner')) - (
                commission + lr_cost + deduction_for_advance + deduction_for_balance)
    elif generate_booking_and_finish == 'detailed_full_booking' or generate_booking_and_finish == 'detailed_commission_booking':
        if generate_booking_and_finish == 'detailed_commission_booking':
            booking_id = commission_booking_id()
        else:
            booking_id = full_booking_id()
        commission = to_int(request.POST.get('commission'))
        lr_cost = to_int(request.POST.get('lr_cost'))
        deduction_for_advance = to_int(request.POST.get('deduction_for_advance'))
        deduction_for_balance = to_int(request.POST.get('deduction_for_balance'))
        amount_to_owner = to_int(request.POST.get('freight_owner')) + (
                to_int(request.POST.get('loading_charge')) + to_int(request.POST.get('unloading_charge')) + to_int(
            request.POST.get('detention_charge')) + to_int(request.POST.get('additional_charges_for_owner'))) - (
                                  commission + lr_cost + deduction_for_advance + deduction_for_balance + to_int(
                              request.POST.get('other_deduction')))
    else:
        booking_id = full_booking_id()
        commission = to_int(request.POST.get('commission'))
        lr_cost = to_int(request.POST.get('lr_cost'))
        deduction_for_advance = to_int(request.POST.get('deduction_for_advance'))
        deduction_for_balance = to_int(request.POST.get('deduction_for_balance'))
        amount_to_owner = to_int(request.POST.get('total_amount_to_owner')) + (
                to_int(request.POST.get('loading_charge')) + to_int(request.POST.get('unloading_charge')) + to_int(
            request.POST.get('detention_charge')) + to_int(request.POST.get('additional_charges_for_owner'))) - (
                                  commission + lr_cost + deduction_for_advance + deduction_for_balance)
    from_city = get_or_none(City, id=request.POST.get('from_city'))
    if isinstance(from_city, City):
        from_city_fk = from_city
        from_city = from_city.name

    else:
        from_city = None
        from_city_fk = None
    to_city = get_or_none(City, id=request.POST.get('to_city'))
    if isinstance(to_city, City):
        to_city_fk = to_city
        to_city = to_city.name
    else:
        to_city = None
        to_city_fk = None
    consignor_city = get_or_none(City, id=request.POST.get('consignor_city'))
    if isinstance(consignor_city, City):
        consignor_city_fk = consignor_city
        consignor_city = consignor_city.name
    else:
        consignor_city_fk = None
        consignor_city = None
    consignee_city = get_or_none(City, id=request.POST.get('consignee_city'))
    if isinstance(consignee_city, City):
        consignee_city_fk = consignee_city
        consignee_city = consignee_city.name
    else:
        consignee_city_fk = None
        consignee_city = None

    if get_contract_party_rate(from_city=from_city_fk, to_city=to_city_fk,
                               customer=customer):
        party_rate = get_contract_party_rate(from_city=from_city_fk, to_city=to_city_fk, customer=customer)
        party_weight = to_float(request.POST.get('charged_weight'))
        total_amount_to_party = party_rate * party_weight
    else:
        party_rate = to_int(request.POST.get('party_rate'))
        party_weight = to_float(request.POST.get('charged_weight'))
        total_amount_to_party = request.POST.get('total_amount_to_party')
    type_of_vehicle = get_or_none(VehicleCategory, id=request.POST.get('vehicle_category_id'))
    if not isinstance(type_of_vehicle, VehicleCategory):
        type_of_vehicle = None
    data = {
        'booking_id': booking_id,
        'company': customer,
        'company_code': customer.company_code if isinstance(customer, Sme) else None,
        'customer_to_be_billed_to': get_or_none(Sme, id=int_or_none(request.POST.get('customer_to_be_billed'))),
        'source_office': source_office,
        'destination_office': destination_office,
        'supplier': supplier,
        'truck_broker_owner_name': supplier.get_name() if isinstance(supplier, Broker) else None,
        'truck_broker_owner_phone': supplier.get_phone() if isinstance(supplier, Broker) else None,
        'owner': owner,
        'truck_owner_name': owner.get_name() if isinstance(owner, Owner) else None,
        'truck_owner_phone': owner.get_phone() if isinstance(owner, Owner) else None,
        'driver': driver,
        'driver_name': driver.name if isinstance(driver, Driver) else None,
        'driver_phone': driver.phone if isinstance(driver, Driver) else None,
        'driver_dl_number': driver.driving_licence_number if isinstance(driver, Driver) else None,
        'driver_dl_validity': driver.driving_licence_validity if isinstance(driver, Driver) else None,
        'is_advance': is_advance,
        'consignor_name': request.POST.get('consignor_name', None),
        'consignor_address': request.POST.get('consignor_address', None),
        'consignor_city': consignor_city,
        'consignor_city_fk': consignor_city_fk,
        'consignor_pin': request.POST.get('consignor_pin', None),
        'consignor_phone': request.POST.get('consignor_phone', None),
        'consignor_gstin': request.POST.get('consignor_gstin', None),
        'consignee_name': request.POST.get('consignee_name', None),
        'consignee_address': request.POST.get('consignee_address', None),
        'consignee_city': consignee_city,
        'consignee_city_fk': consignee_city_fk,
        'consignee_pin': request.POST.get('consignee_pin', None),
        'consignee_phone': request.POST.get('consignee_phone', None),
        'consignee_gstin': request.POST.get('consignee_gstin', None),
        'party_invoice_number': request.POST.get('party_invoice_number', None),
        'party_invoice_date': django_date_format(request.POST.get('party_invoice_date')),
        'party_invoice_amount': to_float(request.POST.get('party_invoice_amount')),
        'road_permit_number': request.POST.get('road_permit_number', None),
        'shipment_date': shipment_date,
        'billing_type': request.POST.get('billing_type', None),
        'number_of_package': request.POST.get('number_of_package', None),
        'material': request.POST.get('material', None),
        'from_city': from_city,
        'from_city_fk': from_city_fk,
        'to_city': to_city,
        'to_city_fk': to_city_fk,
        'lorry_number': display_format(vehicle.vehicle_number),
        'vehicle': vehicle,
        'type_of_vehicle': type_of_vehicle.vehicle_category if type_of_vehicle else '',
        'vehicle_category': type_of_vehicle,
        'gst_liability': request.POST.get('gst_liability', None),
        'comments': request.POST.get('comments', None),
        'loading_charge': to_int(request.POST.get('loading_charge')),
        'unloading_charge': to_int(request.POST.get('unloading_charge')),
        'detention_charge': to_int(request.POST.get('detention_charge')),
        'additional_charges_for_owner': to_int(request.POST.get('additional_charges_for_owner')),
        'note_for_additional_owner_charges': request.POST.get('note_for_additional_owner_charges'),
        'commission': commission,
        'lr_cost': lr_cost,
        'deduction_for_advance': deduction_for_advance,
        'deduction_for_balance': deduction_for_balance,
        'other_deduction': to_int(request.POST.get('other_deduction')),
        'remarks_about_deduction': request.POST.get('remarks_about_deduction'),
        'loaded_weight': to_float(request.POST.get('loaded_weight')),
        'supplier_charged_weight': to_float(request.POST.get('supplier_charged_weight')),
        'supplier_rate': to_int(request.POST.get('supplier_rate')),
        'total_amount_to_owner': amount_to_owner,
        'charged_weight': to_float(request.POST.get('charged_weight')),
        'party_rate': party_rate,
        'total_amount_to_company': total_amount_to_party,
        'refund_amount': to_int(request.POST.get('refundable_amount')),
        'additional_charges_for_company': to_int(request.POST.get('additional_charges_for_company')),
        'deductions_for_company': to_int(request.POST.get('deductions_for_company')),
        'invoice_remarks_for_deduction_discount': request.POST.get('invoice_remarks_for_deduction_discount', None),
        'advance_amount_from_company': to_int(request.POST.get('advance_from_company', None)),
        'invoice_remarks_for_additional_charges': request.POST.get(''),
        'tds_deducted_amount': to_int(request.POST.get('tds_deducted_amount')),
        'insurance_provider': request.POST.get('insurance_provider', None),
        'insurance_policy_number': request.POST.get('insurance_policy_number', None),
        'insured_amount': to_float(request.POST.get('insurance_amount')),
        'insurance_date': django_date_format(request.POST.get('insurance_date')),
        'insurance_risk': None,
        'is_insured': request.POST.get('insured') == 'insured',
        'created_by': request.user,
        'loading_points': request.POST.get('loading_points', None),
        'unloading_points': request.POST.get('unloading_points', None),
        'is_print_payment_mode_instruction': True if request.POST.get('is_print_payment_mode_instruction',
                                                                      None) == 'yes' else False,
    }
    return data


def create_full_booking(data):
    booking = ManualBooking()
    booking.booking_id = data['booking_id']
    booking.source_office = data['source_office']
    booking.destination_office = data['destination_office']
    booking.company = data['company']
    booking.customer_to_be_billed_to = data['customer_to_be_billed_to']
    booking.company_code = data['company_code']
    booking.supplier = data['supplier']
    booking.owner = data['owner']
    booking.driver = data['driver']
    booking.consignor_name = data['consignor_name']
    booking.consignor_address = data['consignor_address']
    booking.consignor_city = data['consignor_city']
    booking.consignor_pin = data['consignor_pin']
    booking.consignor_phone = data['consignor_phone']
    booking.consignor_gstin = data['consignor_gstin']
    booking.consignee_name = data['consignee_name']
    booking.consignee_address = data['consignee_address']
    booking.consignee_city = data['consignee_city']
    booking.consignee_pin = data['consignee_pin']
    booking.consignee_phone = data['consignee_phone']
    booking.consignee_gstin = data['consignee_gstin']
    booking.billing_type = data['billing_type']
    booking.shipment_date = data['shipment_date']
    booking.from_city = data['from_city']
    booking.from_city_fk = data['from_city_fk']
    booking.to_city = data['to_city']
    booking.to_city_fk = data['to_city_fk']
    booking.lorry_number = data['lorry_number']
    booking.vehicle = data['vehicle']
    booking.road_permit_number = data['road_permit_number']
    booking.party_invoice_number = data['party_invoice_number']
    booking.party_invoice_date = data['party_invoice_date']
    booking.party_invoice_amount = data['party_invoice_amount']
    booking.number_of_package = data['number_of_package']
    booking.material = data['material']
    booking.loaded_weight = data['loaded_weight']
    booking.charged_weight = data['charged_weight']
    booking.supplier_charged_weight = data['supplier_charged_weight']
    booking.party_rate = data['party_rate']
    booking.supplier_rate = data['supplier_rate']
    booking.is_insured = data['is_insured']
    booking.insurance_provider = data['insurance_provider']
    booking.insurance_policy_number = data['insurance_policy_number']
    booking.insured_amount = data['insured_amount']
    booking.insurance_date = data['insurance_date']
    booking.insurance_risk = data['insurance_risk']
    booking.gst_liability = data['gst_liability']
    booking.driver_name = data['driver_name']
    booking.driver_phone = data['driver_phone']
    booking.driver_dl_number = data['driver_dl_number']
    booking.driver_dl_validity = data['driver_dl_validity']
    booking.type_of_vehicle = data['type_of_vehicle']
    booking.vehicle_category = data['vehicle_category']
    booking.truck_broker_owner_name = data['truck_broker_owner_name']
    booking.truck_broker_owner_phone = data['truck_broker_owner_phone']
    booking.truck_owner_name = data['truck_owner_name']
    booking.truck_owner_phone = data['truck_owner_phone']
    booking.loading_points = data['loading_points']
    booking.unloading_points = data['unloading_points']
    booking.total_amount_to_company = data['total_amount_to_company']
    booking.advance_amount_from_company = data['advance_amount_from_company']
    booking.refund_amount = data['refund_amount']
    booking.total_amount_to_owner = data['total_amount_to_owner']
    booking.loading_charge = data['loading_charge']
    booking.unloading_charge = data['unloading_charge']
    booking.detention_charge = data['detention_charge']
    booking.additional_charges_for_company = data['additional_charges_for_company']
    booking.additional_charges_for_owner = data['additional_charges_for_owner']
    booking.note_for_additional_owner_charges = data['note_for_additional_owner_charges']
    booking.commission = data['commission']
    booking.lr_cost = data['lr_cost']
    booking.deduction_for_advance = data['deduction_for_advance']
    booking.deduction_for_balance = data['deduction_for_balance']
    booking.other_deduction = data['other_deduction']
    booking.remarks_about_deduction = data['remarks_about_deduction']
    booking.deductions_for_company = data['deductions_for_company']
    booking.invoice_remarks_for_additional_charges = data['invoice_remarks_for_additional_charges']
    booking.invoice_remarks_for_deduction_discount = data['invoice_remarks_for_deduction_discount']
    booking.tds_deducted_amount = data['tds_deducted_amount']
    booking.comments = data['comments']
    booking.is_advance = data['is_advance']
    booking.created_by = data['created_by']
    booking.is_print_payment_mode_instruction = data['is_print_payment_mode_instruction']
    booking.save()
    return booking


def update_booking_field(data):
    booking = get_or_none(ManualBooking, id=data['booking_id'])
    booking.customer_to_be_billed_to = get_or_none(Sme, id=int_or_none(data['to_be_billed_to']))
    booking.save()


def update_full_booking(data):
    booking = get_or_none(ManualBooking, id=int_or_none(data['id']))
    booking.booking_id = data['booking_id']
    booking.source_office = data['source_office']
    booking.destination_office = data['destination_office']
    booking.company = data['company']
    booking.customer_to_be_billed_to = data['customer_to_be_billed_to']
    booking.company_code = data['company_code']
    booking.supplier = data['supplier']
    booking.owner = data['owner']
    booking.driver = data['driver']
    booking.consignor_name = data['consignor_name']
    booking.consignor_address = data['consignor_address']
    booking.consignor_city = data['consignor_city']
    booking.consignor_pin = data['consignor_pin']
    booking.consignor_phone = data['consignor_phone']
    booking.consignor_gstin = data['consignor_gstin']
    booking.consignee_name = data['consignee_name']
    booking.consignee_address = data['consignee_address']
    booking.consignee_city = data['consignee_city']
    booking.consignee_pin = data['consignee_pin']
    booking.consignee_phone = data['consignee_phone']
    booking.consignee_gstin = data['consignee_gstin']
    booking.billing_type = data['billing_type']
    booking.shipment_date = data['shipment_date']
    booking.from_city = data['from_city']
    booking.to_city = data['to_city']
    booking.lorry_number = data['lorry_number']
    booking.road_permit_number = data['road_permit_number']
    booking.party_invoice_number = data['party_invoice_number']
    booking.party_invoice_date = data['party_invoice_date']
    booking.party_invoice_amount = data['party_invoice_amount']
    booking.number_of_package = data['number_of_package']
    booking.material = data['material']
    booking.loaded_weight = data['loaded_weight']
    booking.charged_weight = data['charged_weight']
    booking.supplier_charged_weight = data['supplier_charged_weight']
    booking.party_rate = data['party_rate']
    booking.supplier_rate = data['supplier_rate']
    booking.is_insured = data['is_insured']
    booking.insurance_provider = data['insurance_provider']
    booking.insurance_policy_number = data['insurance_policy_number']
    booking.insured_amount = data['insured_amount']
    booking.insurance_date = data['insurance_date']
    booking.insurance_risk = data['insurance_risk']
    booking.liability_of_service_tax = data['liability_of_service_tax']
    booking.gst_liability = data['gst_liability']
    booking.driver_name = data['driver_name']
    booking.driver_phone = data['driver_phone']
    booking.driver_dl_number = data['driver_dl_number']
    booking.driver_dl_validity = data['driver_dl_validity']
    booking.type_of_vehicle = data['type_of_vehicle']
    booking.truck_broker_owner_name = data['truck_broker_owner_name']
    booking.truck_broker_owner_phone = data['truck_broker_owner_phone']
    booking.truck_owner_name = data['truck_owner_name']
    booking.truck_owner_phone = data['truck_owner_phone']
    booking.loading_points = data['loading_points']
    booking.unloading_points = data['unloading_points']
    booking.total_in_ward_amount = data['total_in_ward_amount']
    booking.total_out_ward_amount = data['total_out_ward_amount']
    booking.total_amount_to_company = data['total_amount_to_company']
    booking.advance_amount_from_company = data['advance_amount_from_company']
    booking.refund_amount = data['refund_amount']
    booking.total_amount_to_owner = data['total_amount_to_owner']
    booking.loading_charge = data['loading_charge']
    booking.unloading_charge = data['unloading_charge']
    booking.detention_charge = data['detention_charge']
    booking.additional_charges_for_company = data['additional_charges_for_company']
    booking.remarks_about_additional_charges = data['remarks_about_additional_charges']
    booking.additional_charges_for_owner = data['additional_charges_for_owner']
    booking.note_for_additional_owner_charges = data['note_for_additional_owner_charges']
    booking.commission = data['commission']
    booking.lr_cost = data['lr_cost']
    booking.deduction_for_advance = data['deduction_for_advance']
    booking.deduction_for_balance = data['deduction_for_balance']
    booking.other_deduction = data['other_deduction']
    booking.remarks_about_deduction = data['remarks_about_deduction']
    booking.deductions_for_company = data['deductions_for_company']
    booking.billing_address = data['billing_address']
    booking.billing_contact_number = data['billing_contact_number']
    booking.billing_invoice_date = data['billing_invoice_date']
    booking.invoice_remarks_for_additional_charges = data['invoice_remarks_for_additional_charges']
    booking.invoice_remarks_for_deduction_discount = data['invoice_remarks_for_deduction_discount']
    booking.tds_deducted_amount = data['tds_deducted_amount']
    booking.pod_status = data['pod_status']
    booking.outward_payment_status = data['outward_payment_status']
    booking.inward_payment_status = data['inward_payment_status']
    booking.invoice_status = data['invoice_status']
    booking.comments = data['comments']
    booking.remarks_advance_from_company = data['remarks_advance_from_company']
    booking.tds_certificate_status = data['tds_certificate_status']
    booking.is_advance = data['is_advance']
    booking.created_by = data['created_by']
    booking.save()


@authenticated_user
def place_full_booking(request):
    mb = create_full_booking(create_full_booking_data(request))
    customer = get_or_none(Sme, id=int_or_none(request.POST.get('customer_placed_order')))
    shipment_datetime = datetime.strptime(request.POST.get('shipment_datetime'), '%d-%b-%Y %I:%M %p')
    number_of_lr = to_int(request.POST.get("number_of_lr"))
    lr_numbers = get_lr_numbers(
        booking=mb,
        source_office=mb.source_office if isinstance(mb, ManualBooking) else None,
        destination_office=get_or_none(AahoOffice, id=int_or_none(request.POST.get('destination_office'))),
        shipment_datetime=shipment_datetime,
        company_code=customer.company_code if isinstance(customer, Sme) else '',
        number_of_lr=number_of_lr,
        created_by=request.user
    )
    generate_lorry_receipt(mb)
    if settings.ENABLE_SMS:
        tasks.full_booking_sms_customer.delay(booking_id=mb.id)
        tasks.full_booking_sms_employee.delay(booking_id=mb.id)
    if check_gps_device_attach(mb.lorry_number):
        if settings.ENABLE_SMS:
            tasks.tracking_sms_customer.delay(booking_id=mb.id)
    return json_success_response(msg='{} generated successfully'.format(', '.join(lr_numbers)))


@authenticated_user
def fetch_commission_booking_data_page(request):
    aaho_office = AahoOffice.objects.all()
    return render(request=request, template_name='team/booking/fetch-commission-booking-data.html',
                  context={'aaho_office': aaho_office})


@authenticated_user
def commission_booking_page(request):
    source_office = get_or_none(AahoOffice, id=int_or_none(request.GET.get('source_office')))
    destination_office = get_or_none(AahoOffice, id=int_or_none(request.GET.get('destination_office')))
    truck_owners = Owner.objects.all().values('id', 'name__profile__name', 'name__profile__phone')
    customer = get_or_none(Sme, id=int_or_none(request.GET.get('customer_placed_order')))
    if not (isinstance(customer, Sme) or isinstance(source_office, AahoOffice) or isinstance(destination_office,
                                                                                             AahoOffice)):
        return HttpResponseRedirect('/team/fetch-commission-booking-data-page/')
    shipment_datetime = request.GET.get('shipment_datetime')
    vehicle_category = get_or_none(VehicleCategory, id=int_or_none(request.GET.get('vehicle_category_id')))

    truck_driver = get_or_none(Driver, id=int_or_none(request.GET.get('truck_driver_id')))
    supplier = get_or_none(Broker, id=int_or_none(request.GET.get('supplier_id')))

    vehicle = get_or_none(Vehicle, vehicle_number=compare_format(request.GET.get('vehicle_number')))
    owner = get_or_none(Owner, id=int_or_none(request.GET.get('truck_owner_id')))

    if isinstance(vehicle, Vehicle):
        vehicle_number = display_format(vehicle.vehicle_number)
    else:
        vehicle_number = display_format(request.GET.get('vehicle_number'))

    from_city = get_or_none(City, id=request.GET.get('from_city'))
    if isinstance(from_city, City):
        from_city = {'id': from_city.id, 'name': from_city.name,
                     'state': from_city.state.name if from_city.state else ''}
    else:
        from_city = None
    to_city = get_or_none(City, id=request.GET.get('to_city'))
    if isinstance(to_city, City):
        to_city = {'id': to_city.id, 'name': to_city.name, 'state': to_city.state.name if to_city.state else ''}
    else:
        to_city = None

    context_data = {
        'source_office': source_office,
        'destination_office': destination_office,
        'customer': customer,
        'shipment_datetime': shipment_datetime,
        'vehicle_number': vehicle_number,
        'from_city': from_city,
        'truck_owner_id': owner.id if isinstance(owner, Owner) else '',
        'vehicle_category_id': vehicle_category.id if isinstance(vehicle_category, VehicleCategory) else '',
        'to_city': to_city,
        'vehicle': vehicle,
        'supplier': supplier,
        'truck_owners': truck_owners,
        'truck_driver': truck_driver,
        'billing_type': request.GET.get('billing_type'),
        'refund_amount': request.GET.get('refundable_amount'),
        'supplier_weight': request.GET.get('supplier_charged_weight'),
        'supplier_rate': request.GET.get('supplier_rate'),
        'party_weight': request.GET.get('charged_weight'),
        'party_rate': request.GET.get('party_rate'),
        'loaded_weight': request.GET.get('loaded_weight'),
    }
    return render(request=request, template_name='team/booking/commission-booking.html', context=context_data)


@authenticated_user
def place_commission_booking(request):
    booking = create_full_booking(create_full_booking_data(request))
    if settings.ENABLE_MAIL:
        tasks.email_commission_booking.delay(booking.id)
    if settings.ENABLE_SMS:
        tasks.commission_booking_sms_customer.delay(booking_id=booking.id)
        tasks.commission_booking_sms_employee.delay(booking_id=booking.id)
    if request.POST.get('generate-booking-and-finish') == 'quick_commission_booking':
        return json_success_response(msg='{} generated successfully'.format(booking.booking_id))
    else:
        return HttpResponseRedirect('/team/fetch-commission-booking-data-page/')


def booking_search_kwargs(exclude_kwargs, search_value, booking_ids):
    filter_kwargs = Q(id__in=booking_ids)
    if search_value == 'zblue':
        booking_ids = ManualBooking.objects.filter(
            Q(total_amount_to_company=0)).exclude(booking_status='cancelled').values_list('id', flat=True)
        return None, booking_ids

    if search_value == 'zgreen':
        booking_ids = ManualBooking.objects.filter(
            Q(total_amount_to_company__lte=F('total_in_ward_amount') + F('tds_deducted_amount')
              ) & Q(total_amount_to_company__gt=0)).exclude(booking_status='cancelled').values_list('id', flat=True)
        return None, booking_ids

    if search_value == 'zorange':
        booking_ids = ManualBooking.objects.filter(
            pod_status='completed', invoice_status='no_invoice').exclude(booking_status='cancelled').values_list('id',
                                                                                                                 flat=True)
        return None, booking_ids

    if search_value == 'zpurple':
        booking_ids = ManualBooking.objects.filter(
            pod_status='completed', invoice_status='invoice_raised').exclude(
            Q(total_amount_to_company__lte=F('total_in_ward_amount') + F('tds_deducted_amount')
              ) & Q(total_amount_to_company__gt=0)).exclude(booking_status='cancelled').exclude(
            Q(total_amount_to_company=0)).values_list('id', flat=True)
        return None, booking_ids
    if search_value == 'zpurple':
        booking_ids = ManualBooking.objects.filter(
            pod_status='completed', invoice_status='invoice_raised').exclude(
            Q(total_amount_to_company__lte=F('total_in_ward_amount') + F('tds_deducted_amount')
              ) & Q(total_amount_to_company__gt=0)).exclude(booking_status='cancelled').values_list('id', flat=True)
        return None, booking_ids
    if search_value == 'zred':
        booking_ids = ManualBooking.objects.filter(total_amount_to_company__gt=0).exclude(
            pod_status='completed').exclude(booking_status='cancelled').values_list('id', flat=True)
        return None, booking_ids

    try:
        search_kwargs = Q(booking_id__icontains=search_value) | Q(
            lorry_number__icontains=search_value) | Q(
            tds_deducted_amount=search_value) | Q(
            invoice_number__icontains=search_value)

        if LrNumber.objects.filter(lr_number__icontains=search_value).exists():
            booking_ids = LrNumber.objects.filter(lr_number__icontains=search_value).values_list('booking__id')
            search_kwargs = None
        elif ManualBooking.objects.filter(filter_kwargs).filter(search_kwargs).exclude(exclude_kwargs).exists():
            search_kwargs = Q(booking_id__icontains=search_value) | Q(lorry_number__icontains=search_value) | Q(
                invoice_number__icontains=search_value) | Q(truck_broker_owner_name__icontains=search_value)
        else:
            search_value = int(float(search_value))
            search_kwargs = Q(
                total_in_ward_amount=search_value) | Q(
                total_out_ward_amount=search_value) | Q(
                total_amount_to_company=search_value) | Q(
                total_amount_to_owner=search_value) | Q(
                refund_amount=search_value) | Q(
                party_rate=search_value) | Q(
                charged_weight=search_value) | Q(
                supplier_charged_weight=search_value) | Q(
                tds_deducted_amount=search_value) | Q(
                truck_broker_owner_name__icontains=search_value)
    except ValueError:
        search_kwargs = Q(from_city__icontains=search_value) | Q(
            to_city__icontains=search_value) | Q(
            lorry_number__icontains=search_value) | Q(
            vehicle__vehicle_number__icontains=search_value) | Q(
            vehicle__vehicle_type__vehicle_type__icontains=search_value) | Q(
            type_of_vehicle=search_value) | Q(
            truck_owner_name__icontains=search_value) | Q(
            booking_id__icontains=search_value) | Q(
            company__name__profile__name__icontains=search_value) | Q(
            supplier__name__profile__name__icontains=search_value) | Q(
            billing_type__icontains=search_value) | Q(
            pod_status__icontains=search_value) | Q(
            outward_payment_status__icontains=search_value) | Q(
            inward_payment_status__icontains=search_value) | Q(
            invoice_number__icontains=search_value) | Q(
            truck_broker_owner_name__icontains=search_value)
    return search_kwargs, booking_ids


def get_booking_invoice_number(booking):
    if Invoice.objects.filter(bookings=booking).exists():
        return '\n'.join(Invoice.objects.filter(bookings=booking).values_list('invoice_number', flat=True))
    else:
        return None


def get_booking_invoice_date(booking):
    if Invoice.objects.filter(bookings=booking).exists():
        return '\n'.join(invoice.date.strftime('%d-%b-%Y') if invoice.date else '' for invoice in
                         Invoice.objects.filter(bookings=booking))
    else:
        return None


def get_booking_invoice_customer(booking):
    if Invoice.objects.filter(bookings=booking).exists():
        return '\n'.join(invoice.company for invoice in
                         Invoice.objects.filter(bookings=booking))
    else:
        return None


@authenticated_user
def partial_booking_data(request):
    user_group = request.user.groups.values_list('name', flat=True)[0]
    booking_ids = manual_booking_id_list(username=request.user.username,
                                         user_group_list=request.user.groups.values_list('name', flat=True))
    start = to_int(request.GET.get('start'))
    end = start + to_int(request.GET.get('length'))

    exclude_kwargs = Q(total_in_ward_amount__gte=F('total_amount_to_company') - F('tds_deducted_amount')) & Q(
        total_out_ward_amount__exact=F('total_amount_to_owner')) | Q(booking_status='cancelled')
    if request.GET.get('search[value]'):
        search_value = request.GET.get('search[value]')
        # implement search on booking
        search_kwargs, booking_ids = booking_search_kwargs(
            exclude_kwargs=exclude_kwargs, search_value=search_value, booking_ids=booking_ids)
    else:
        search_kwargs = None

    if search_kwargs:
        bookings = ManualBooking.objects.filter(Q(id__in=booking_ids)).exclude(exclude_kwargs).filter(
            search_kwargs).order_by(
            '-shipment_date', '-booking_id')
    else:
        bookings = ManualBooking.objects.filter(Q(id__in=booking_ids)).exclude(exclude_kwargs).order_by(
            '-shipment_date', '-booking_id')
    data = []
    if EMP_GROUP3 is not user_group:
        for booking in bookings[start:end if end != -1 else bookings.count()]:
            data.append([
                booking.shipment_date.strftime('%d-%b-%Y') if booking.shipment_date else '',
                format_html(''' <form action="/team/booking-edit/" method="GET">                                            
                                                  <button class="transaction-button" style="background: {}; color:white"
                                                   name="booking_id" value="{}" type="submit">{}</button> </form>''',
                            booking_status_color(booking), booking.id, booking.booking_id),
                '<br>'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                booking.company.get_name() if booking.company else '',
                booking.company.company_code if booking.company else '',
                booking.supplier.get_name() if booking.supplier else to_str(booking.truck_broker_owner_name),
                booking.from_city,
                booking.to_city,
                '{}<br>{}'.format(booking.lorry_number, booking.type_of_vehicle),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else str(
                    to_int(booking.total_amount_to_company)),
                str(booking.charged_weight),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else str(
                    to_int(booking.party_rate)),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else str(
                    to_int(booking.balance_for_customer)),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else str(
                    to_int(booking.refund_amount)),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else str(
                    to_int(booking.tds_deducted_amount)),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else (
                    booking.customer_to_be_billed_to.get_name() if booking.customer_to_be_billed_to else str(
                        booking.to_be_billed_to if booking.to_be_billed_to else '')),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else (
                    booking.customer_to_be_billed_to.company_code if booking.customer_to_be_billed_to else ''),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else booking.invoice_number,
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else (
                    booking.billing_invoice_date.strftime('%d-%b-%Y') if booking.billing_invoice_date else ''),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else booking.to_be_billed_to,
                str(to_int(booking.total_amount_to_owner)),
                str(booking.supplier_charged_weight),
                str(to_int(booking.supplier_rate)),
                str(to_int(booking.balance_for_supplier)),
                booking.get_pod_status_display(),
                booking.get_invoice_status_display(),
                booking.get_inward_payment_status_display(),
                booking.get_outward_payment_status_display(),
                booking.source_office.branch_name if booking.source_office else '-',
                booking.destination_office.branch_name if booking.destination_office else '-',
                booking.delivery_datetime.strftime('%d-%b-%Y') if booking.delivery_datetime else '-'
            ])
    else:
        for booking in bookings[start:end if end != -1 else bookings.count()]:
            data.append([
                booking.shipment_date.strftime('%d-%b-%Y') if booking.shipment_date else '',
                format_html(''' <form action="/team/booking-edit/" method="GET">                                            
                                                              <button class="transaction-button" style="background: {}; color:white" name="booking_id" value="{}" type="submit">{}</button> </form>''',
                            booking_status_color(booking), booking.id, booking.booking_id),
                '<br>'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                booking.company.get_name() if booking.company else '-',
                booking.supplier.get_name() if booking.supplier else to_str(booking.truck_broker_owner_name),
                booking.from_city,
                booking.to_city,
                '{}<br>{}'.format(booking.lorry_number, booking.type_of_vehicle),
                str(to_int(booking.total_amount_to_owner)),
                str(to_float(booking.supplier_charged_weight)),
                str(to_int(booking.supplier_rate)),
                str(to_int(booking.balance_for_supplier)),
                booking.get_pod_status_display(),
                booking.get_invoice_status_display(),
                booking.get_inward_payment_status_display(),
                booking.get_outward_payment_status_display(),
                booking.source_office.branch_name if booking.source_office else '-',
                booking.destination_office.branch_name if booking.destination_office else '-',
                booking.delivery_datetime.strftime('%d-%b-%Y') if booking.delivery_datetime else '-'
            ])
    booking_data = {
        "draw": to_int(request.GET.get('draw')),
        "recordsTotal": bookings.count(),
        "recordsFiltered": bookings.count(),
        "data": data
    }
    return HttpResponse(json.dumps(booking_data), content_type='application/json')


@authenticated_user
def partial_booking_history(request):
    return render(request, 'team/booking/partial_booking.html')


def booking_status_color(booking):
    if booking.total_amount_to_company == 0:
        return 'cornflowerblue'
    elif booking.balance_for_customer <= 0:
        return 'darkseagreen'
    elif booking.pod_status == 'completed' and booking.invoice_status == 'no_invoice':
        return 'orange'
    elif booking.pod_status == 'completed' and booking.invoice_status == 'invoice_raised':
        return 'purple'
    elif booking.pod_status == 'completed' and booking.invoice_status == 'invoice_sent':
        return 'purple'
    elif booking.pod_status != 'completed':
        return 'indianred'
    else:
        return 'black'


@authenticated_user
def booking_archive_data(request):
    user_group = request.user.groups.values_list('name', flat=True)[0]
    booking_ids = manual_booking_id_list(username=request.user.username,
                                         user_group_list=request.user.groups.values_list('name', flat=True))
    start = to_int(request.GET.get('start'))
    end = start + to_int(request.GET.get('length'))
    exclude_kwargs = Q(booking_status='cancelled')
    if request.GET.get('search[value]'):
        search_value = request.GET.get('search[value]')
        # implement search on booking
        search_kwargs, booking_ids = booking_search_kwargs(
            exclude_kwargs=exclude_kwargs, search_value=search_value, booking_ids=booking_ids)
    else:
        search_kwargs = None

    if search_kwargs:
        bookings = ManualBooking.objects.filter(Q(id__in=booking_ids)).exclude(exclude_kwargs).filter(
            search_kwargs).order_by(
            '-shipment_date', '-booking_id')
    else:
        bookings = ManualBooking.objects.filter(Q(id__in=booking_ids)).exclude(exclude_kwargs).order_by(
            '-shipment_date', '-booking_id')

    data = []
    if EMP_GROUP3 not in request.user.groups.values_list('name', flat=True):
        for booking in bookings[start:end if end != -1 else bookings.count()]:
            data.append([
                booking.shipment_date.strftime('%d-%b-%Y') if booking.shipment_date else '',
                format_html(''' <form action="/team/booking-edit/" method="GET">                                            
                                                              <button class="transaction-button" style="background: {}; color:white" name="booking_id" value="{}" type="submit">{}</button> </form>''',
                            booking_status_color(booking), booking.id, booking.booking_id),
                '<br>'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                booking.company.get_name() if booking.company else '',
                booking.company.company_code if booking.company else '',
                booking.supplier.get_name() if booking.supplier else to_str(booking.truck_broker_owner_name),
                booking.from_city,
                booking.to_city,
                '{}<br>{}'.format(booking.lorry_number, booking.type_of_vehicle),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else str(
                    to_int(booking.total_amount_to_company)),
                str(booking.charged_weight),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else str(
                    to_int(booking.party_rate)),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else str(
                    to_int(booking.balance_for_customer)),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else str(
                    to_int(booking.refund_amount)),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else str(
                    to_int(booking.tds_deducted_amount)),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else (
                    booking.customer_to_be_billed_to.get_name() if booking.customer_to_be_billed_to else str(
                        booking.to_be_billed_to if booking.to_be_billed_to else '')),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else (
                    booking.customer_to_be_billed_to.company_code if booking.customer_to_be_billed_to else ''),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else booking.invoice_number,
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else (
                    booking.billing_invoice_date.strftime('%d-%b-%Y') if booking.billing_invoice_date else ''),
                '-' if user_group == EMP_GROUP2 and booking.billing_type == 'contract' else booking.to_be_billed_to,
                str(to_int(booking.total_amount_to_owner)),
                str(booking.supplier_charged_weight),
                str(to_int(booking.supplier_rate)),
                str(to_int(booking.balance_for_supplier)),
                booking.get_pod_status_display(),
                booking.get_invoice_status_display(),
                booking.get_inward_payment_status_display(),
                booking.get_outward_payment_status_display(),
                booking.source_office.branch_name if booking.source_office else '-',
                booking.destination_office.branch_name if booking.destination_office else '-',
                booking.delivery_datetime.strftime('%d-%b-%Y') if booking.delivery_datetime else '-'
            ])
    else:
        for booking in bookings[start:end if end != -1 else bookings.count()]:
            data.append([
                booking.shipment_date.strftime('%d-%b-%Y') if booking.shipment_date else '',
                format_html(''' <form action="/team/booking-edit/" method="GET">                                            
                                                              <button class="transaction-button" style="background: {}; color:white" name="booking_id" value="{}" type="submit">{}</button> </form>''',
                            booking_status_color(booking), booking.id, booking.booking_id),
                '<br>'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
                booking.company.get_name() if booking.company else '',
                booking.company.company_code if booking.company else '',
                booking.supplier.get_name() if booking.supplier else to_str(booking.truck_broker_owner_name),
                booking.from_city,
                booking.to_city,
                '{}<br>{}'.format(booking.lorry_number, booking.type_of_vehicle),
                str(to_int(booking.total_amount_to_owner)),
                str(to_int(booking.supplier_charged_weight)),
                str(to_int(booking.supplier_rate)),
                str(to_int(booking.balance_for_supplier)),
                booking.get_pod_status_display(),
                booking.get_invoice_status_display(),
                booking.get_inward_payment_status_display(),
                booking.get_outward_payment_status_display(),
                booking.source_office.branch_name if booking.source_office else '-',
                booking.destination_office.branch_name if booking.destination_office else '-',
                booking.delivery_datetime.strftime('%d-%b-%Y') if booking.delivery_datetime else '-'

            ])
    booking_data = {
        "draw": to_int(request.GET.get('draw')),
        "recordsTotal": bookings.count(),
        "recordsFiltered": bookings.count(),
        "data": data
    }
    return HttpResponse(json.dumps(booking_data), content_type='application/json')


@authenticated_user
def all_booking_history(request):
    return render(request, 'team/booking/booking-archive.html')


def mis_booking_page(request):
    return render(request, 'team/booking/mis-booking.html')


def get_booking_images(booking):
    data = []
    if isinstance(booking, ManualBooking):
        for doc in booking.podfile_set.filter(verified=True, is_valid=True):
            data.append(
                {'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder, 'url': doc.s3_upload.public_url()})

        vehicle = get_or_none(Vehicle, vehicle_number=compare_format(booking.lorry_number))
        if vehicle:
            for doc in vehicle.vehicle_files.all():
                data.append({'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                             'url': doc.s3_upload.public_url()})
            if vehicle.owner:
                for doc in vehicle.owner.owner_files.all():
                    data.append({'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                 'url': doc.s3_upload.public_url()})
            if vehicle.driver:
                for doc in vehicle.driver.driver_files.all():
                    data.append({'filename': doc.s3_upload.filename, 'folder': doc.s3_upload.folder,
                                 'url': doc.s3_upload.public_url()})
    return data


def booking_supplier(booking):
    try:
        supplier = Broker.objects.get(name__profile__phone=booking.truck_broker_owner_phone)
    except Broker.DoesNotExist:
        supplier = get_or_none(Broker, name__username='unknown_supplier')
    except Broker.MultipleObjectsReturned:
        supplier = Broker.objects.filter(name__profile__phone=booking.truck_broker_owner_phone).exclude(
            name__username__in=Owner.objects.filter(
                name__profile__phone=booking.truck_broker_owner_phone).values_list('name__username', flat=True)
        ).last()
    return supplier


def get_invoice_details(booking):
    if booking.invoices.all():
        return [
            {
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'customer': invoice.company_name,
                'address': invoice.address,
                'pin': invoice.pin if invoice.pin else '',
                'city': None if not invoice.city else invoice.city.to_json(),
                'date': invoice.date.strftime('%d-%b-%Y') if invoice.date else '',
            } for invoice in booking.invoices.all()
        ]
    elif booking.to_pay_invoices.all():
        return [
            {
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'customer': invoice.company_name,
                'address': invoice.company_address,
                'pin': invoice.pin if invoice.pin else '',
                'city': None if not invoice.city else invoice.city.to_json(),
                'date': invoice.date.strftime('%d-%b-%Y') if invoice.date else '',
            } for invoice in booking.to_pay_invoices.all()
        ]
    elif booking.customer_to_be_billed_to:
        return [
            {
                'id': None,
                'invoice_number': None,
                'customer': booking.customer_to_be_billed_to.get_name(),
                'address': booking.customer_to_be_billed_to.customer_address,
                'pin': booking.customer_to_be_billed_to.pin if booking.customer_to_be_billed_to.pin else '',
                'city': booking.customer_to_be_billed_to.city.to_json() if booking.customer_to_be_billed_to.city else None,
                'date': '',
            }
        ]
    else:
        return [{
            'id': '',
            'invoice_number': '',
            'customer': '',
            'address': '',
            'pin': '',
            'city': '',
            'date': ''
        }]


def update_booking_data(mb_id):
    try:
        try:
            booking = ManualBooking.objects.get(id=int(mb_id))
        except ValueError:
            status = 'error'
            error_message = 'Booking ID is not valid'

    except ManualBooking.DoesNotExist:
        status = 'error'
        error_message = '{} does not exist'.format(mb_id)


def access_payment_paid_to_supplier(supplier):
    amount = 0
    message_data = []
    for booking in ManualBooking.objects.filter(supplier=supplier, outward_payment_status='excess').exclude(
            booking_status='cancelled').exclude(supplier=None):
        amount += (-booking.balance_for_supplier)
        message_data.append('{} ({})'.format(booking.booking_id, booking.balance_for_supplier))
    return amount, 'Excess amount of {}  made in {}'.format(amount, ', '.join(message_data))


def debit_amount_to_be_adjusted(supplier):
    if not isinstance(supplier, Broker):
        return 0
    return sum([dn.amount_to_be_adjusted for dn in DebitNoteSupplier.objects.filter(broker=supplier).filter(
        status__in=['approved', 'partial', 'adjusted'])])


@authenticated_user
def booking_edit_save_reprint(request):
    try:
        booking = ManualBooking.objects.get(id=int_or_none(request.GET.get('booking_id')))
    except ManualBooking.DoesNotExist:
        raise Http404
    in_ward_payment = InWardPayment.objects.filter(booking_id=booking)
    out_ward_payment = OutWardPayment.objects.filter(booking_id=booking)
    fuel_card = FuelCard.objects.exclude(card_number=None)
    outward_balance = booking.total_amount_to_owner - booking.total_out_ward_amount
    inward_balance = booking.total_amount_to_company - booking.total_in_ward_amount
    inward_paid = booking.total_in_ward_amount + booking.tds_deducted_amount
    bank_account = Bank.objects.filter(status='active')
    suppliers = Broker.objects.all().values('id', 'name__profile__name', 'name__profile__phone')
    truck_owners = Owner.objects.all().values('id', 'name__profile__name', 'name__profile__phone')
    vehicle = get_or_none(Vehicle, vehicle_number=compare_format(booking.lorry_number))
    from_city = booking.from_city_fk
    to_city = booking.to_city_fk
    consignor_city_fk = booking.consignor_city_fk
    consignee_city_fk = booking.consignee_city_fk
    vehicle_category = booking.vehicle_category

    if vehicle:
        try:
            broker_vehicle = vehicle.brokervehicle_set.latest('updated_on')
        except BrokerVehicle.DoesNotExist:
            broker_vehicle = []
    else:
        broker_vehicle = None

    supplier_excess_amount, supplier_excess_amount_msg = access_payment_paid_to_supplier(supplier=booking.supplier)
    context = {
        'supplier_excess_amount': supplier_excess_amount,
        'debit_amount_to_be_adjusted': debit_amount_to_be_adjusted(supplier=booking.supplier),
        'supplier_excess_amount_msg': supplier_excess_amount_msg,
        'booking_data': booking_edit_data.get_full_booking_data(booking.id),
        'from_city': from_city,
        'to_city': to_city,
        'consignor_city_fk': consignor_city_fk,
        'consignee_city_fk': consignee_city_fk,
        'vehicle_category': vehicle_category,
        'booking_data_fetched': booking,
        'bank_account': bank_account,
        'outward_balance': outward_balance,
        'inward_balance': inward_balance,
        'in_ward_payment': in_ward_payment,
        'inward_paid': inward_paid,
        'out_ward_payment': out_ward_payment,
        'fuel_card': fuel_card,
        'suppliers': suppliers,
        'truck_owners': truck_owners,
        'vehicle': vehicle,
        'broker_vehicle': broker_vehicle,
        'customers': Sme.objects.all(),
        'invoices': get_invoice_details(booking=booking),
        'images_files': get_booking_images(booking=booking)
    }
    if booking.booking_id.startswith("AAHO") or booking.booking_id.startswith("AH"):
        return render(
            request=request,
            template_name='team/booking/update-full-booking.html',
            context=context
        )
    elif booking.booking_id.startswith("BROKER") or booking.booking_id.startswith("AB"):
        return render(
            request=request,
            template_name='team/booking/update-commission-booking.html',
            context=context
        )
    else:
        raise Http404


def lr_download_data(request):
    start = to_int(request.GET.get('start'))
    end = start + to_int(request.GET.get('length'))
    booking_ids = manual_booking_id_list(username=request.user.username,
                                         user_group_list=request.user.groups.values_list('name', flat=True))
    if request.GET.get('search[value]'):
        search_value = request.GET.get('search[value]')
        lr_numbers = LrNumber.objects.filter(
            Q(booking_id__in=booking_ids) and (
                    Q(lr_number__icontains=search_value) | Q(booking__booking_id__icontains=search_value))
        ).order_by('-datetime')
    else:
        lr_numbers = LrNumber.objects.filter(
            booking_id__in=manual_booking_id_list(
                username=request.user.username,
                user_group_list=request.user.groups.values_list('name', flat=True)
            )
        ).order_by('-datetime')
    data = []
    for lr in lr_numbers[start:end]:
        data.append([
            lr.datetime.strftime('%d-%b-%Y') if lr.datetime else '',
            lr.booking.booking_id if lr.booking else '',
            lr.lr_number,
            format_html('''<a href="{}" download><i class="fa fa-download" aria-hidden="true"></i></a>''',
                        S3Upload.objects.filter(filename__istartswith=lr.lr_number,
                                                filename__iendswith='.pdf').last().public_url()) if S3Upload.objects.filter(
                filename__istartswith=lr.lr_number, filename__iendswith='.pdf').exists() else ''
        ])
    data = {
        "draw": to_int(request.GET.get('draw')),
        "recordsTotal": lr_numbers.count(),
        "recordsFiltered": lr_numbers.count(),
        "data": data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


@authenticated_user
def lr_download(request):
    return render(request, 'team/booking/download-lr.html')


@authenticated_user
def update_contract_booking_rate_page(request):
    bookings = ManualBooking.objects.filter(Q(total_amount_to_company=0)).filter(billing_type='contract').exclude(
        Q(deleted=True) | Q(booking_status='cancelled'))
    data = []
    for booking in bookings:
        data.append({
            'id': booking.id,
            'booking_id': booking.booking_id,
            'shipment_date': booking.shipment_date.strftime('%d-%b-%Y') if booking.shipment_date else '',
            'lr_numbers': '\n'.join(booking.lr_numbers.values_list('lr_number', flat=True)),
            'customer_name': booking.company.get_name() if booking.company else '',
            'origin': booking.from_city,
            'destination': booking.to_city,
            'weight': booking.charged_weight,
            'rate_id': '{}_{}'.format('rate', booking.booking_id),
            'amount_id': '{}_{}'.format('amount', booking.booking_id)
        })
    return render(request=request, template_name='team/booking/update-contract-bookings-rate.html',
                  context={'bookings': data, 'id': ','.join(map(str, bookings.values_list('id', flat=True)))})


@authenticated_user
def update_contract_booking_rate(request):
    id = request.POST.get('id').split(',') if request.POST.get('id') else []
    for booking in ManualBooking.objects.filter(id__in=id):
        party_rate = to_int(request.POST.get('{}_{}'.format('rate', booking.booking_id)))
        booking.party_rate = party_rate
        booking.total_amount_to_company = party_rate * booking.charged_weight
        booking.save()
    return json_success_response('Rate is updated for booking_id(s) {}'.format(
        ', '.join(ManualBooking.objects.filter(id__in=id).values_list('booking_id', flat=True))))


def contract_customer_data(request):
    sme_id = request.GET.get('sme_id')
    customer = get_or_none(Sme, id=sme_id)
    if isinstance(customer, Sme):
        today = datetime.now().date()
        if customer.customercontract_set.filter(Q(start_date__lte=today) & Q(end_date__gte=today)).exclude(
                deleted=True).exists():
            data = {'id': customer.id, 'name': customer.get_name(), 'code': customer.company_code, 'is_contract': True}
        else:
            data = {'id': customer.id, 'name': customer.get_name(), 'code': customer.company_code, 'is_contract': False}
    else:
        data = {'id': -1, 'name': '', 'code': '', 'is_contract': False}
    return HttpResponse(json.dumps(data), content_type='application/json')


@authenticated_user
def booking_id_data(request):
    rows = to_int(request.GET.get('page'))
    bookings = ManualBooking.objects.exclude(Q(deleted=True) & Q(booking_status='cancelled'))

    search_value = request.GET.get('search')
    if search_value:
        bookings = ManualBooking.objects.filter(booking_id__icontains=search_value).exclude(
            Q(deleted=True) & Q(booking_status='cancelled'))
    data = []
    for booking in bookings[:rows]:
        data.append({
            'id': booking.id,
            'text': '{}'.format(booking.booking_id)
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
