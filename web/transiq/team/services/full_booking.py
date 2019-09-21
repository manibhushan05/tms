from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Q
from django.db.utils import IntegrityError

from api.helper import EMP_GROUP3, EMP_GROUP2, EMP_GROUP1
from api.utils import get_or_none
from broker.models import BrokerVehicle, Broker, BrokerDriver
from driver.models import Driver
from team.helper.helper import django_date_format, is_blank, to_int, to_float, update_inward_payments, update_outward_payments, \
    update_invoice_status
from owner.models import Vehicle, Owner
from owner.vehicle_util import compare_format, display_format
from sme.models import Sme
from team.models import ManualBooking, OutWardPayment, InWardPayment
from utils.models import AahoOffice, VehicleCategory, City


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


def update_broker_vehicle(broker_vehicle_id, broker_id):
    bv = get_or_none(BrokerVehicle, id=broker_vehicle_id)
    if bv:
        bv.broker = get_or_none(Broker, id=broker_id)
        bv.save()


def save_consignor_details(request, booking):
    booking.consignor_name = request.POST.get('consignor_name')
    booking.consignor_address = request.POST.get('consignor_address')
    booking.consignor_city = request.POST.get('consignor_city')
    booking.consignor_pin = request.POST.get('consignor_pin')
    booking.consignor_phone = request.POST.get('consignor_phone')
    booking.consignor_gstin = request.POST.get('consignor_gstin')
    return booking


def save_consignee_details(request, booking):
    booking.consignee_name = request.POST.get('consignee_name')
    booking.consignee_address = request.POST.get('consignee_address')
    booking.consignee_city = request.POST.get('consignee_city')
    booking.consignee_pin = request.POST.get('consignee_pin')
    booking.consignee_phone = request.POST.get('consignee_phone')
    booking.consignee_gstin = request.POST.get('consignee_gstin')
    return booking


def save_invoice_details(request, booking):
    booking.party_invoice_number = request.POST.get('party_invoice_number')
    booking.party_invoice_date = django_date_format(request.POST.get('party_invoice_date'))
    booking.party_invoice_amount = to_float(request.POST.get('party_invoice_amount'))
    booking.road_permit_number = request.POST.get('road_permit_number')
    return booking


def save_vendor_details(booking):
    try:
        vehicle = Vehicle.objects.get(vehicle_number=compare_format(booking.lorry_number))
        booking.truck_owner_name = None if not vehicle.owner else vehicle.owner.name.profile.name
        booking.truck_owner_phone = None if not vehicle.owner else vehicle.owner.name.profile.phone
        broker_vehicle = BrokerVehicle.objects.filter(vehicle=vehicle).last()
        if broker_vehicle:
            booking.truck_broker_owner_name = broker_vehicle.broker.get_name()
            booking.truck_broker_owner_phone = broker_vehicle.broker.get_phone()
        booking.driver_name = None if not vehicle.driver else vehicle.driver.name
        booking.driver_phone = None if not vehicle.driver else vehicle.driver.phone
        booking.driver_dl_number = None if not vehicle.driver else vehicle.driver.driving_licence_number
        booking.driver_dl_validity = None if not vehicle.driver else vehicle.driver.driving_licence_validity
    except Vehicle.DoesNotExist:
        pass
    booking.save()


def save_consignment_details(request, booking):
    shipment_date = request.POST.get('shipment_datetime')
    booking.shipment_date = None if is_blank(shipment_date) else datetime.strptime(shipment_date, '%d-%b-%Y %I:%M %p')
    booking.billing_type = request.POST.get('billing_type')
    booking.number_of_package = request.POST.get('number_of_package')
    booking.material = request.POST.get('material')
    booking.from_city = request.POST.get('from')
    booking.to_city = request.POST.get('to')
    booking.lorry_number = request.POST.get('vehicle_number')
    vehicle_category = get_or_none(VehicleCategory, id=request.POST.get('vehicle_category_id'))
    booking.type_of_vehicle = None if not vehicle_category else vehicle_category.name()
    booking.gst_liability = request.POST.get('gst_liability')
    booking.comments = request.POST.get('comments')
    return booking


def save_additional_charges(request, booking):
    booking.loading_charge = to_int(request.POST.get('loading_charge'))
    booking.unloading_charge = to_int(request.POST.get('unloading_charge'))
    booking.detention_charge = to_int(request.POST.get('detention_charge'))
    booking.additional_charges_for_owner = to_int(request.POST.get('additional_charges_for_owner'))
    booking.note_for_additional_owner_charges = request.POST.get('note_for_additional_owner_charges')
    return booking


def save_vendor_deduction(request, booking):
    booking.commission = to_int(request.POST.get('commission'))
    booking.lr_cost = to_int(request.POST.get('lr_cost'))
    booking.deduction_for_advance = to_int(request.POST.get('deduction_for_advance'))
    booking.deduction_for_balance = to_int(request.POST.get('deduction_for_balance'))
    booking.other_deduction = to_int(request.POST.get('other_deduction'))
    booking.remarks_about_deduction = request.POST.get('remarks_about_deduction')
    return booking


def save_rate_details(request, booking):
    booking.loaded_weight = to_float(request.POST.get('loaded_weight'))
    booking.supplier_charged_weight = to_float(request.POST.get('supplier_charged_weight'))
    booking.supplier_rate = to_int(request.POST.get('supplier_rate'))
    booking.total_amount_to_owner = to_int(request.POST.get('total_amount_to_owner'))
    if EMP_GROUP1 in request.user.groups.values_list('name',
                                                     flat=True) or EMP_GROUP2 in request.user.groups.values_list('name',
                                                                                                                 flat=True):
        booking.charged_weight = to_float(request.POST.get('charged_weight'))
        booking.party_rate = to_int(request.POST.get('party_rate'))
        booking.total_amount_to_company = to_int(request.POST.get('total_amount_to_party'))
        booking.refund_amount = to_int(request.POST.get('refundable_amount'))
        booking.additional_charges_for_company = to_int(request.POST.get('additional_charges_for_company'))
        booking.deductions_for_company = to_int(request.POST.get('deductions_for_company'))
        booking.invoice_remarks_for_deduction_discount = request.POST.get('invoice_remarks_for_deduction_discount')
        booking.advance_amount_from_company = request.POST.get('advance_from_company')
        booking.invoice_remarks_for_additional_charges = request.POST.get('invoice_remarks_for_additional_charges')
        booking.tds_deducted_amount = to_int(request.POST.get('tds_deducted_amount'))
    return booking


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
        return booking


def update_mb_status(booking):
    booking.save()


def save_manual_booking_data(request, booking_id):
    booking = ManualBooking()
    booking.booking_id = booking_id
    try:
        sme = Sme.objects.get(id=request.POST.get('customer'))
        booking.company = sme
        booking.company_code = sme.company_code
    except Sme.DoesNotExist:
        booking.company = None
    booking.customer_to_be_billed_to = get_or_none(Sme, id=request.POST.get('customer_to_be_billed'))
    if not is_blank(request.POST.get('company_code')):
        booking.company_code = request.POST.get('company_code')
    source_office = request.POST.get('source_office')
    booking.source_office = AahoOffice.objects.get(id=source_office)
    destination_office = request.POST.get('destination_office')
    booking.supplier = get_or_none(Broker, id=request.POST.get('supplier_id'))
    booking.owner = get_or_none(Owner, id=request.POST.get('truck_owner_id'))
    booking.driver = get_or_none(Driver, id=request.POST.get('truck_driver_id'))
    booking.destination_office = AahoOffice.objects.get(id=destination_office)
    if source_office == '2' or source_office == '3' or destination_office == '2' or destination_office == '3':
        booking.is_advance = request.POST.get('is_print_payment_mode_instruction')
    save_consignor_details(request, booking)
    save_consignee_details(request, booking)
    save_consignment_details(request, booking)
    save_insurance_details(request, booking)
    save_invoice_details(request, booking)
    save_rate_details(request, booking)
    save_vendor_deduction(request, booking)
    save_additional_charges(request, booking)
    booking.created_by = User.objects.get(username=request.user.username)
    booking.save()
    # update_mb_status(booking)
    save_vehicle_details(vehicle_number=request.POST.get('vehicle_number'),
                         vehicle_category_id=request.POST.get('vehicle_category_id'),
                         supplier=request.POST.get('supplier_id'),
                         owner=request.POST.get('truck_owner_id'),
                         driver=request.POST.get('truck_driver_id'))
    save_vendor_details(booking)


def change_status_existing_booking(booking_id):
    try:
        booking = ManualBooking.objects.get(booking_id=booking_id)
    except ManualBooking.DoesNotExist:
        booking = ManualBooking.objects.get(id=booking_id)
    out_ward_payment = OutWardPayment.objects.filter(booking_id=booking)
    outward_amount = 0
    for value in out_ward_payment:
        outward_amount += value.actual_amount
    if outward_amount == 0:
        booking.outward_payment_status = 'no_payment_made'
    elif booking.total_amount_to_owner > outward_amount:
        booking.outward_payment_status = 'partial'
    elif booking.total_amount_to_owner == outward_amount:
        booking.outward_payment_status = 'complete'
    elif booking.total_amount_to_owner < outward_amount:
        booking.outward_payment_status = 'excess'
    in_ward_payment = InWardPayment.objects.filter(booking_id=booking)
    inward_amount = 0
    for value in in_ward_payment:
        inward_amount += value.actual_amount
    update_inward_payments(booking)


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
        # vehicle.vehicle_category = None if not vehicle_type else get_or_none(VehicleCategory, id=vehicle_type)
        vehicle.save()


def save_existing_manual_booking_data(request, booking_id):
    booking = ManualBooking.objects.get(id=booking_id)
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
    vehicle_category = get_or_none(VehicleCategory, id=request.POST.get('vehicle_category_id'))
    if isinstance(vehicle_category, VehicleCategory):
        type_of_vehicle = vehicle_category.vehicle_category
    else:
        type_of_vehicle = None
    vehicle = get_or_none(Vehicle, vehicle_number=compare_format(request.POST.get('vehicle_number')))
    if isinstance(vehicle, Vehicle):
        lorry_number = display_format(vehicle.vehicle_number)
    else:
        lorry_number = None
    if not EMP_GROUP3 in request.user.groups.values_list('name', flat=True):
        booking.party_rate = to_int(request.POST.get('party_rate'))
        booking.charged_weight = to_float(request.POST.get('charged_weight'))
        booking.additional_charges_for_company = to_int(request.POST.get('additional_charges_for_company'))
        booking.deductions_for_company = to_int(request.POST.get('deductions_for_company'))
        booking.total_amount_to_company = to_int(request.POST.get('total_amount_to_party'))
        booking.refund_amount = to_int(request.POST.get('refundable_amount'))
        booking.invoice_amount = to_int(request.POST.get('invoice_amount'))
        booking.invoice_remarks_for_deduction_discount = request.POST.get('invoice_remarks_for_deduction_discount')
        booking.advance_amount_from_company = request.POST.get('advance_from_company')
        booking.invoice_remarks_for_additional_charges = request.POST.get('invoice_remarks_for_additional_charges')

    booking.consignor_name = request.POST.get('consignor_name')
    booking.consignor_address = request.POST.get('consignor_address')
    booking.consignor_city = consignor_city
    booking.consignor_city_fk = consignor_city_fk
    booking.consignor_pin = request.POST.get('consignor_pin')
    booking.consignor_phone = request.POST.get('consignor_phone')
    booking.consignor_gstin = request.POST.get('consignor_gstin')

    booking.consignee_name = request.POST.get('consignee_name')
    booking.consignee_address = request.POST.get('consignee_address')
    booking.consignee_city = consignee_city
    booking.consignee_city_fk = consignee_city_fk
    booking.consignee_pin = request.POST.get('consignee_pin')
    booking.consignee_phone = request.POST.get('consignee_phone')
    booking.consignee_gstin = request.POST.get('consignee_gstin')

    booking.driver = get_or_none(Driver, id=request.POST.get('truck_driver_id'))
    shipment_date = request.POST.get('shipment_datetime')
    booking.shipment_date = None if is_blank(shipment_date) else datetime.strptime(shipment_date, '%Y-%m-%d')
    booking.billing_type = request.POST.get('billing_type')
    booking.number_of_package = request.POST.get('number_of_package')
    booking.material = request.POST.get('material')
    booking.from_city = from_city
    booking.from_city_fk = from_city_fk
    booking.to_city = to_city
    booking.to_city_fk = to_city_fk
    booking.lorry_number = lorry_number
    booking.vehicle = vehicle
    booking.party_invoice_number = request.POST.get('party_invoice_number')
    booking.party_invoice_date = django_date_format(request.POST.get('party_invoice_date'))
    booking.party_invoice_amount = to_float(request.POST.get('party_invoice_amount'))
    booking.road_permit_number = request.POST.get('road_permit_number')
    booking.vehicle_category = vehicle_category
    booking.type_of_vehicle = type_of_vehicle

    booking.liability_of_service_tax = request.POST.get('liability_of_service_tax')

    booking.loaded_weight = to_float(request.POST.get('loaded_weight'))

    booking.supplier_charged_weight = to_float(request.POST.get('supplier_charged_weight'))

    booking.supplier_rate = to_int(request.POST.get('supplier_rate'))

    save_insurance_details(request, booking)
    booking.comments = request.POST.get('comments')
    booking.billing_type = request.POST.get('billing_type')

    booking.loading_charge = to_int(request.POST.get('loading_charge'))
    booking.unloading_charge = to_int(request.POST.get('unloading_charge'))
    booking.detention_charge = to_int(request.POST.get('detention_charge'))
    booking.additional_charges_for_owner = to_int(request.POST.get('additional_charges_for_owner'))

    booking.commission = to_int(request.POST.get('commission'))
    booking.lr_cost = to_int(request.POST.get('lr_cost'))
    booking.deduction_for_advance = to_int(request.POST.get('deduction_for_advance'))
    booking.deduction_for_balance = to_int(request.POST.get('deduction_for_balance'))
    booking.other_deduction = to_int(request.POST.get('other_deduction'))

    booking.remarks_about_deduction = request.POST.get('remarks_about_deduction')

    booking.total_amount_to_owner = to_int(request.POST.get('total_amount_to_owner'))
    booking.tds_deducted_amount = to_int(request.POST.get('tds_deducted_amount'))
    booking.invoice_status = request.POST.get('invoice_status')
    booking.note_for_additional_owner_charges = request.POST.get('note_for_additional_owner_charges')
    booking.is_advance = request.POST.get('is_print_payment_mode_instruction')
    booking.changed_by = request.user
    booking.save()
    Vehicle.objects.filter(vehicle_number=compare_format(booking.lorry_number)).update(vehicle_type=vehicle_category)
    save_vendor_details(booking)
    update_inward_payments(booking)
    update_outward_payments(booking)
    update_invoice_status(booking)
    return booking


def get_booking_id():
    try:
        booking = ManualBooking.objects.filter(Q(booking_id__istartswith='AH') | Q(
            booking_id__istartswith='AAHO')).latest('created_on')
        id = str(booking.booking_id)
        temp = to_int(id[4:]) + 1
        booking_id = id[0:4] + '{0:05d}'.format(temp)
    except ManualBooking.DoesNotExist:
        booking_id = 'AAHO00001'
    return booking_id
