from broker.helper import django_date_format
from broker.models import Booking, Customer
from owner.models import Vehicle


def get_booking_id(booking_id):
    return '10000'





def get_customer_obj(cutomer_id):
    if cutomer_id:
        try:
            return Customer.objects.get(id=cutomer_id)
        except (Customer.DoesNotExist, Customer.MultipleObjectsReturned) as e:
            return None
    else:
        return None

def get_vehicle_obj(vehicle_id):
    if vehicle_id:
        try:
            return Vehicle.objects.get(id=vehicle_id)
        except (Customer.DoesNotExist, Customer.MultipleObjectsReturned) as e:
            return None
    else:
        return None


def place_order(booking_id, broker, customer, shipment_datetime, vehicle, driver, owner, source, destination,
                loading_locations, unloading_locations, quantity, material, vendor_weight, vendor_rate,
                vendor_detention_charge, vendor_labor_charge, vendor_other_charge, vendor_commission,
                vendor_other_deduction, total_amount_vendor, vendor_rate_remarks, customer_weight,
                customer_rate, customer_detention_charge, customer_labor_charge, customer_other_charge,
                total_amount_cutomer, customer_rate_remarks):
    booking = Booking()
    booking.booking_id = get_booking_id(booking_id=booking_id)
    # booking.supplier = get_broker_obj(broker_id=supplier)
    booking.customer = get_customer_obj(cutomer_id=customer)
    booking.shipment_datetime = django_date_format(shipment_datetime)
    booking.vehicle = ''
    booking.driver = ''
    booking.owner = ''
    booking.source = ''
    booking.destination = ''
    booking.loading_locations = ''
    booking.unloading_locations = ''
    booking.quantity = ''
    booking.material = ''
    # for vendor
    booking.vendor_weight = ''
    booking.vendor_rate = ''
    booking.vendor_detention_charge = ''
    booking.vendor_labor_charge = ''
    booking.vendor_other_charge = ''
    booking.vendor_commission = ''
    booking.vendor_other_deduction = ''
    booking.total_amount_vendor = ''
    booking.vendor_rate_remarks = ''
    # for customer
    booking.customer_weight = ''
    booking.customer_rate = ''
    booking.customer_detention_charge = ''
    booking.customer_labor_charge = ''
    booking.customer_other_charge = ''
    booking.total_amount_cutomer = ''
    booking.customer_rate_remarks = ''
    booking.remarks = ''
    booking.save()
