from api.utils import to_int
from team import tasks
from team.models import ManualBooking, OutWardPayment
import pandas as pd
import requests

from utils.models import City


def booking_invoice():
    for booking in ManualBooking.objects.all():
        if booking.invoices.exists() and booking.invoices.count() >= 1:
            invoice = booking.invoices.last()
            booking.invoice_number = invoice.invoice_number
            booking.to_be_billed_to = invoice.company_name
            booking.billing_address = invoice.address
            booking.billing_invoice_date = invoice.date
            booking.save()

        elif booking.invoices.exists() and booking.invoices.count() == 0:
            if booking.invoice_status != 'no_invoice':
                pass


def send_booking_email():
    for booking in ManualBooking.objects.filter(id__gt=7051):
        tasks.email_lr(booking_id=booking.id)


def send_payment_email():
    for payment in OutWardPayment.objects.filter(id__gt=18961):
        tasks.email_outward_payment(payment_id=payment.id)


def inward_payment_status(booking):
    if isinstance(booking, ManualBooking):
        if to_int(booking.amount_received_from_customer) == 0:
            return 'no_payment'
        elif 0 < to_int(booking.amount_received_from_customer) < booking.customer_amount:
            return 'partial_received'
        elif to_int(booking.amount_received_from_customer) == to_int(booking.customer_amount):
            return 'full_received'
        elif to_int(booking.amount_received_from_customer) > to_int(booking.customer_amount):
            return 'excess'
        else:
            return None
    return None


def fix_inward_payment_status():
    data = []
    for booking in ManualBooking.objects.order_by('-id'):
        if booking.inward_payment_status != inward_payment_status(booking=booking) and booking.balance_for_customer > 2:
            data.append([booking.booking_id, booking.shipment_date,
                         inward_payment_status(booking=booking), booking.inward_payment_status, booking.customer_amount,
                         booking.total_in_ward_amount, booking.amount_received_from_customer])
    df = pd.DataFrame(data=data, columns=['Booking ID', 'Shipment Date', 'expected Status', 'Status', 'Customer Amount',
                                          'total_in_ward_amount', 'amount_received_from_customer'])
    df.to_excel('inward payment status.xlsx', index=False)


def update_latlng_cities():
    for city in City.objects.filter(updated_on__gt='2018-10-18')[:1]:
        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json',
                                params={'address': '{}, {}'.format(city.name, city.state_name),
                                        'key': 'AIzaSyA55P5d_nejkwua_AE8Xu2Wg8PaxjrswkI'})
        try:
            data = response.json()
            location = data['results'][0]['geometry']['location']
            print(location)
            city.latitude = location['lat']
            city.longitude = location['lng']
        except:
            print("FAiled",response.json())
