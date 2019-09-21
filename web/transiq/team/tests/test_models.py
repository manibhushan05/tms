from django.test import TestCase
from model_mommy import mommy

from team.models import ManualBooking, OutWardPayment, InWardPayment, InvoiceSummary, BookingStatusColor, LrNumber, \
    ManualBookingS3Upload, LrS3Upload, RejectedPOD


class ManualBookingTestModel(TestCase):
    def setUp(self):
        self.booking = mommy.make(ManualBooking, make_m2m=True)
        self.bookings = mommy.make(ManualBooking, make_m2m=True, _quantity=10)

    def test_manual_booking_create(self):
        self.assertTrue(isinstance(self.booking, ManualBooking))
        self.assertEqual(ManualBooking.objects.filter(id=self.booking.id).count(), 1)
        self.assertEqual(ManualBooking.objects.count(), 11)


class OutWardPaymentTestModel(TestCase):
    def setUp(self):
        self.payment = mommy.make(OutWardPayment, make_m2m=True)

    def test_outward_payment_create(self):
        self.assertTrue(isinstance(self.payment, OutWardPayment))


class InWardPaymentTestModel(TestCase):
    def setUp(self):
        self.payment = mommy.make(InWardPayment, make_m2m=True)

    def test_inward_payment_create(self):
        self.assertTrue(isinstance(self.payment, InWardPayment))


class InvoiceSummaryTestModel(TestCase):
    def setUp(self):
        self.invoice_summary = mommy.make(InvoiceSummary)

    def test_invoice_summary_create(self):
        self.assertTrue(isinstance(self.invoice_summary, InvoiceSummary))


class BookingStatusColorModel(TestCase):
    def setUp(self):
        self.booking_status_color = mommy.make(BookingStatusColor)

    def test_booking_status_color_create(self):
        self.assertTrue(isinstance(self.booking_status_color, BookingStatusColor))


class LrNumberTestModel(TestCase):
    def setUp(self):
        self.lr_number = mommy.make(LrNumber)

    def test_lr_number_create(self):
        self.assertTrue(isinstance(self.lr_number, LrNumber))


class ManualBookingS3UploadTestModel(TestCase):
    def setUp(self):
        self.manual_booking_s3_upload = mommy.make(ManualBookingS3Upload)

    def test_manual_booking_s3_upload_create(self):
        self.assertTrue(isinstance(self.manual_booking_s3_upload, ManualBookingS3Upload))


class LrS3UploadTestModel(TestCase):
    def setUp(self):
        self.lr_s3_object = mommy.make(LrS3Upload)

    def test_lr_s3_object_create(self):
        self.assertTrue(isinstance(self.lr_s3_object, LrS3Upload))


class RejectedPODTestModel(TestCase):
    def setUp(self):
        self.instance = mommy.make(RejectedPOD)

    def test_reject_pod_create(self):
        self.assertTrue(isinstance(self.instance, RejectedPOD))