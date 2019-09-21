from datetime import datetime

from django.db import IntegrityError
from django.db.models import Q

from django.contrib.auth.models import User

from api.helper import EMP_GROUP3, EMP_GROUP2, EMP_GROUP1
from api.utils import get_or_none
from broker.models import BrokerVehicle, Broker, BrokerDriver
from driver.models import Driver
from owner.models import Vehicle, Owner
from owner.vehicle_util import compare_format
from sme.models import Sme
from team.models import ManualBooking
from team.helper.helper import is_blank, django_date_format, to_float, to_int, update_outward_payments, \
    update_inward_payments, update_invoice_status
from utils.models import AahoOffice, VehicleCategory


def update_vehicle_details(vehicle, supplier, owner, driver, vehicle_category=None):
    vehicle.owner = None if not owner else get_or_none(Owner, id=owner)
    vehicle.vehicle_type = vehicle_category
    driver = None if not driver else get_or_none(Driver, id=driver)
    if Vehicle.objects.filter(driver=driver).exists():
        Vehicle.objects.filter(driver=driver).update(driver=None)
        vehicle.driver = driver
    else:
        vehicle.driver = driver
    broker = get_or_none(Broker, id=supplier)
    if not BrokerVehicle.objects.filter(vehicle=vehicle, broker=broker).exists():
        BrokerVehicle.objects.create(broker=broker, vehicle=vehicle)
    return vehicle


def create_broker_driver(supplier, driver):
    try:
        BrokerDriver.objects.create(
            broker=get_or_none(Broker, id=supplier),
            driver=get_or_none(Driver, id=driver)
        )
    except IntegrityError:
        pass


def save_vehicle_details(vehicle_number, vehicle_category_id, supplier, owner, driver):
    vehicle_category = get_or_none(VehicleCategory, id=vehicle_category_id)
    try:
        vehicle = Vehicle.objects.get(vehicle_number=compare_format(vehicle_number))
    except Vehicle.DoesNotExist:
        vehicle = Vehicle.objects.create(
            vehicle_number=compare_format(vehicle_number),
            vehicle_type=vehicle_category,
        )

    update_vehicle_details(vehicle=vehicle, supplier=supplier, owner=owner, driver=driver,
                           vehicle_category=vehicle_category)
    create_broker_driver(supplier=supplier, driver=driver)
    vehicle.save()


def save_invoice_details(request, booking):
    booking.party_invoice_number = request.POST.get('party_invoice_number')
    booking.party_invoice_date = django_date_format(request.POST.get('party_invoice_date'))
    booking.party_invoice_amount = to_float(request.POST.get('party_invoice_amount'))
    booking.road_permit_number = request.POST.get('road_permit_number')
    booking.save()


def save_vendor_details(booking):
    try:
        vehicle = Vehicle.objects.get(vehicle_number=compare_format(booking.lorry_number))
        booking.truck_owner_name = None if not vehicle.owner else vehicle.owner.name.profile.name
        booking.truck_owner_phone = None if not vehicle.owner else vehicle.owner.name.profile.phone
        broker_vehicle = BrokerVehicle.objects.filter(vehicle=vehicle).last()
        if broker_vehicle:
            booking.truck_broker_owner_name = broker_vehicle.broker.name.profile.name
            booking.truck_broker_owner_phone = broker_vehicle.broker.name.profile.phone
        booking.driver_name = None if not vehicle.driver else vehicle.driver.name
        booking.driver_phone = None if not vehicle.driver else vehicle.driver.phone
        booking.driver_dl_number = None if not vehicle.driver else vehicle.driver.driving_licence_number
        booking.driver_dl_validity = None if not vehicle.driver else vehicle.driver.driving_licence_validity
    except Vehicle.DoesNotExist:
        pass
    booking.save()


def save_consignment_details(request, booking):
    shipment_date = request.POST.get('shipment_date')
    booking.shipment_date = None if is_blank(shipment_date) else datetime.strptime(shipment_date, '%d-%b-%Y %I:%M %p')
    booking.billing_type = request.POST.get('billing_type')
    booking.number_of_package = request.POST.get('number_of_package')
    booking.material = request.POST.get('material')
    booking.from_city = request.POST.get('from')
    booking.to_city = request.POST.get('to')
    booking.loading_points = request.POST.get('loading_points')
    booking.unloading_points = request.POST.get('unloading_points')
    booking.lorry_number = request.POST.get('lorry_number')
    vehicle_category = get_or_none(VehicleCategory, id=request.POST.get('vehicle_category_id'))
    booking.type_of_vehicle = None if not vehicle_category else vehicle_category.name()
    booking.comments = request.POST.get('comments')
    booking.save()


def save_additional_charges(request, booking):
    booking.loading_charge = to_int(request.POST.get('loading_charge'))
    booking.unloading_charge = to_int(request.POST.get('unloading_charge'))
    booking.detention_charge = to_int(request.POST.get('detention_charge'))
    booking.additional_charges_for_owner = to_int(request.POST.get('additional_charges_for_owner'))
    booking.note_for_additional_owner_charges = request.POST.get('note_for_additional_owner_charges')
    booking.save()


def save_vendor_deduction(request, booking):
    booking.commission = to_int(request.POST.get('commission'))
    booking.lr_cost = to_int(request.POST.get('lr_cost'))
    booking.deduction_for_advance = to_int(request.POST.get('deduction_for_advance'))
    booking.deduction_for_balance = to_int(request.POST.get('deduction_for_balance'))
    booking.other_deduction = to_int(request.POST.get('other_deduction'))
    booking.remarks_about_deduction = request.POST.get('remarks_about_deduction')
    booking.save()


def save_rate_details(request, booking):
    booking.loaded_weight = to_float(request.POST.get('loaded_weight'))
    booking.supplier_charged_weight = to_float(request.POST.get('supplier_charged_weight'))
    if EMP_GROUP1 in request.user.groups.values_list('name',
                                                     flat=True) or EMP_GROUP2 in request.user.groups.values_list('name',
                                                                                                                 flat=True):
        booking.party_rate = to_int(request.POST.get('party_rate'))
        booking.total_amount_to_company = to_int(request.POST.get('total_amount_to_party'))
        booking.charged_weight = to_float(request.POST.get('charged_weight'))
    booking.supplier_rate = to_int(request.POST.get('supplier_rate'))
    booking.total_amount_to_owner = to_int(request.POST.get('total_amount_to_owner'))
    booking.save()


def save_insurance_details(request, booking):
    booking.insurance_provider = request.POST.get('insurance_provider')
    booking.insurance_policy_number = request.POST.get('insurance_policy_number')
    booking.insured_amount = to_float(request.POST.get('insurance_amount'))
    booking.insurance_date = django_date_format(request.POST.get('insurance_date'))
    is_insured = request.POST.get('insured')
    if is_insured == 'insured':
        booking.is_insured = True
    else:
        booking.is_insured = False
    booking.save()





def get_commission_only_booking_id():
    try:
        booking = ManualBooking.objects.filter(Q(booking_id__istartswith='AB') | Q(
            booking_id__istartswith='BROKER')).latest('created_on')
        ids = str(booking.booking_id)
        temp = int(ids[6:]) + 1
        booking_id = ids[0:6] + '{0:05d}'.format(temp)
    except ManualBooking.DoesNotExist:
        booking_id = 'BROKER00001'
    return booking_id


def save_commission_only(request):
    booking = ManualBooking()
    booking.booking_id = get_commission_only_booking_id()
    try:
        sme = Sme.objects.get(id=request.POST.get('customer'))
        booking.company = sme
        booking.company_code = sme.company_code
    except Sme.DoesNotExist:
        sme = None
    company_code = request.POST.get('company_code')
    if not is_blank(company_code):
        booking.company_code = company_code
    booking.source_office = AahoOffice.objects.get(id=request.POST.get('source_office'))
    booking.destination_office = AahoOffice.objects.get(id=request.POST.get('destination_office'))
    booking.supplier = get_or_none(Broker, id=request.POST.get('supplier_id'))
    booking.owner = get_or_none(Owner, id=request.POST.get('truck_owner_id'))
    booking.driver = get_or_none(Driver, id=request.POST.get('truck_driver_id'))
    save_consignment_details(request, booking)
    save_rate_details(request, booking)
    save_vendor_deduction(request, booking)
    save_additional_charges(request, booking)
    save_status_details(request, booking)
    booking.created_by = User.objects.get(username=request.user.username)
    booking.save()
    save_vehicle_details(vehicle_number=request.POST.get('lorry_number'),
                         vehicle_category_id=request.POST.get('vehicle_category_id'),
                         supplier=request.POST.get('supplier_id'),
                         owner=request.POST.get('truck_owner_id'),
                         driver=request.POST.get('truck_driver_id'))
    save_vendor_details(booking)
    return booking


def update_vehicle(broker_vehicle_id, vehicle_number, supplier, vehicle_owner, driver, vehicle_type):
    broker_vehicle = get_or_none(BrokerVehicle, id=broker_vehicle_id)
    if broker_vehicle:
        broker_vehicle.broker = get_or_none(Broker, id=supplier)
        broker_vehicle.save()
    vehicle = get_or_none(Vehicle, vehicle_number=compare_format(vehicle_number))
    if vehicle:
        driver = None if not driver else get_or_none(Driver, id=driver)
        Vehicle.objects.filter(driver=driver).update(driver=None)
        vehicle.driver = driver
        vehicle.owner = None if not vehicle_owner else get_or_none(Owner, id=vehicle_owner)
        vehicle.vehicle_category = None if not vehicle_type else get_or_none(VehicleCategory, id=vehicle_type)
        vehicle.save()


def update_commission_booking(request):
    try:
        booking = ManualBooking.objects.get(booking_id=request.POST.get('booking_id'))
    except ManualBooking.DoesNotExist:
        booking = ManualBooking.objects.get(id=request.POST.get('booking_id'))
    # Basic Details
    booking.billing_type = request.POST.get('billing_type')
    booking.number_of_package = request.POST.get('number_of_package')
    booking.material = request.POST.get('material')
    booking.from_city = request.POST.get('from_city')
    booking.to_city = request.POST.get('to_city')
    booking.lorry_number = request.POST.get('lorry_number')
    vehicle_category = get_or_none(VehicleCategory, id=request.POST.get('vehicle_category_id'))
    booking.type_of_vehicle = None if not vehicle_category else vehicle_category.name()
    booking.loading_points = request.POST.get('loading_points')
    booking.unloading_points = request.POST.get('unloading_points')
    # booking.supplier = get_or_none(Broker, id=request.POST.get('supplier_id'))
    # booking.owner = get_or_none(Owner, id=request.POST.get('truck_owner_id'))
    booking.driver = get_or_none(Driver, id=request.POST.get('truck_driver_id'))

    # rate details
    booking.loaded_weight = to_float(request.POST.get('loaded_weight'))
    booking.supplier_charged_weight = to_float(request.POST.get('supplier_charged_weight'))
    booking.supplier_rate = to_int(request.POST.get('supplier_rate'))

    # additional charges
    booking.loading_charge = to_int(request.POST.get('loading_charge'))
    booking.unloading_charge = to_int(request.POST.get('unloading_charge'))
    booking.detention_charge = to_int(request.POST.get('detention_charge'))
    booking.additional_charges_for_owner = to_int(request.POST.get('additional_charges_for_owner'))
    booking.note_for_additional_owner_charges = request.POST.get('note_for_additional_owner_charges')

    # deduction for vendor
    booking.commission = to_int(request.POST.get('commission'))
    booking.lr_cost = to_int(request.POST.get('lr_cost'))
    booking.deduction_for_advance = to_int(request.POST.get('deduction_for_advance'))
    booking.deduction_for_balance = to_int(request.POST.get('deduction_for_balance'))
    booking.other_deduction = to_int(request.POST.get('other_deduction'))
    booking.remarks_about_deduction = request.POST.get('remarks_about_deduction')

    # total amount
    booking.total_amount_to_owner = to_int(request.POST.get('total_amount_to_owner'))
    booking.total_amount_to_company = to_int(request.POST.get('total_amount_to_party'))

    if not EMP_GROUP3 in request.user.groups.values_list('name', flat=True):
        # invoice details
        booking.additional_charges_for_company = to_int(request.POST.get('additional_charges_for_company'))
        booking.invoice_remarks_for_additional_charges = request.POST.get('invoice_remarks_for_additional_charges')
        booking.deductions_for_company = to_int(request.POST.get('deductions_for_company'))
        booking.invoice_remarks_for_deduction_discount = request.POST.get('invoice_remarks_for_deduction_discount')
        booking.advance_amount_from_company = to_int(request.POST.get('advance_from_company'))
        booking.tds_deducted_amount = to_int(request.POST.get('tds_deducted_amount'))

        # Rate Details
        booking.charged_weight = to_float(request.POST.get('charged_weight'))
        booking.party_rate = to_int(request.POST.get('party_rate'))

    # status update
    booking.pod_status = request.POST.get('pod_status')
    booking.invoice_status = request.POST.get('invoice_status')
    booking.save()
    Vehicle.objects.filter(vehicle_number=compare_format(booking.lorry_number)).update(vehicle_type=vehicle_category)
    update_inward_payments(booking)
    update_outward_payments(booking)
    update_invoice_status(booking)
    return booking
