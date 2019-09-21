from __future__ import print_function, absolute_import, division

from django.contrib.auth.models import User
from django.test import TestCase, Client

from team.models import ManualBooking
from team.models import OutWardPayment

'''
class OutwardPaymentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='mani@aaho.in', password='whvc.1900')
        self.client = Client()
        self.client.login(username='mani@aaho.in', password='whvc.1900')
        self.booking = ManualBooking.objects.create(total_amount_to_owner=100000)

    def test_outward_payment_views(self):
        response = self.client.post(path='/team/outward-payments/', data={
            'booking_id[]': list(ManualBooking.objects.filter(id=self.booking.id).values_list('id', flat=True)),
            'paid_to': u'Mani Bhushan Kumar',
            'actual_amount': u'999',
            'outward_payment_mode': u'cash',
            'outward_payment_date': u'25-Aug-2018'
        })

        self.assertEqual(response.status_code, 200)

    def test_outward_payment_data(self):
        self.assertTrue(isinstance(self.booking, ManualBooking))
        self.assertTrue(isinstance(self.user, User))


class OutwardPaymentsEditBookingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ravindra@aaho.in', password='whvc.1900')
        self.client = Client()
        self.client.login(username='ravindra@aaho.in', password='whvc.1900')
        self.booking = ManualBooking.objects.create(total_amount_to_owner=100000)

    def test_outward_payments_edit_booking_views(self):
        response = self.client.post('/team/outward-payments-edit-booking/', {
            'booking_id': self.booking.id,
            'paid_to': u'Mani Bhushan Kumar',
            'actual_amount': u'1000',
            'outward_payment_mode': u'cash',
            'outward_payment_date': u'25-Aug-2018',
            'is_refund_amount': 'y',
        })
        # if dev.DEBUG or prod.DEBUG:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.booking.total_amount_to_owner, 100000)
        self.actual_amount = OutWardPayment .objects.filter(booking_id=self.booking.id).values_list('actual_amount',
                                                                                                   flat=True)
        self.paid_to = OutWardPayment.objects.filter(booking_id=self.booking.id).values_list('paid_to', flat=True)
        self.outward_payment_mode = OutWardPayment.objects.filter(booking_id=self.booking.id).values_list(
            'payment_mode', flat=True)
        self.assertIn(1000, self.actual_amount)
        self.assertIn('Mani Bhushan Kumar', self.paid_to)
        self.assertIn('cash', self.outward_payment_mode)
    # else:
    #     self.assertEqual(response.status_code, 301)


def test_outward_payment_data(self):
    self.assertTrue(isinstance(self.booking, ManualBooking))
    self.assertTrue(isinstance(self.user, User))

'''
