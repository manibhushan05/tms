import json
import zlib

from api.abstract import PostApiTestCase, PostDriverAuthApiTestCase, driver_details, UnAbstract, UnAbstractAuth, \
    GetDriverAuthApiTestCase, get_driver_details, UnAbstractAuth400, UnAbstract400
from api.utils import now_timestamp, from_timestamp, get_or_none
from driver.models import DriverAppUser, OTP, GPSLogNew
from driver.schema import update_pod_schema, driver_register_schema, pod_details_schema
from owner.models import Vehicle
from transaction.models import Transaction, VehicleAllocated


def get_driver(device_id):
    return get_or_none(DriverAppUser, device_id=device_id)


def gps_log_data(device_id, ts):
    return [
        device_id, ts, 'fused', 28.215999603271484, 19.1112867, 72.8979114, 0, 0, 0, 9, 3887656960,
        1131442176, 226492416, 0, 'OnePlus', 'OnePlus', 'OnePlus2', 'OnePlus2', 'ONE A2003', '0.1.1', 30, '6.0.1', 23
    ]


# GETs

class TestDriverPodDetailsApi(GetDriverAuthApiTestCase, UnAbstractAuth):

    def url(self):
        return '/api/driver/pod-details/'

    def schema(self):
        return pod_details_schema()


# POSTs

class TestDriverRegisterApi(PostApiTestCase, UnAbstract400):

    def url(self):
        return '/api/driver/register/'

    def data(self):
        self.device_id, driver_data = driver_details()
        return driver_data

    def schema(self):
        return driver_register_schema()

    def confirm_result(self):
        # check if the driver object was created
        driver = get_driver(self.device_id)
        self.assertIsNotNone(driver, 'Driver with device id %s does not exist in the database' % self.device_id)

'''

class TestDriverGpsLogApi(PostApiTestCase, UnAbstract):

    def setUp(self):
        super().setUp()
        self.device_id = 'MY1AMAZING2PHONE'
        self.log_timestamp = now_timestamp()
        self.log_time = from_timestamp(self.log_timestamp)
        self.log_data = gps_log_data(self.device_id, self.log_timestamp)

    def is_json(self):
        return False

    def url(self):
        return '/api/driver/location-update-new/'

    def data(self):
        return zlib.compress(json.dumps(bytes(self.log_data)))

    def confirm_result(self):
        # check if gps log was created
        self.gps_log = get_or_none(GPSLogNew, device_id=self.device_id, datetime=self.log_time)
        self.assertIsNotNone(self.gps_log, 'GPS Log not created')
        self.assertEqual(float(self.gps_log.latitude), self.log_data[4], 'latitude does not match')
        self.assertEqual(float(self.gps_log.longitude), self.log_data[5], 'longitude does not match')


class TestDriverGpsLogApiLatestLocationUpdate(TestDriverGpsLogApi):

    def setUp(self):
        super().setUp()
        self.driver = DriverAppUser.objects.create(**get_driver_details(self.device_id))
        self.vehicle = Vehicle.objects.create(driver_app_user=self.driver, vehicle_number=self.driver.vehicle_number)

    def confirm_result(self):
        super().confirm_result()
        dr = DriverAppUser.objects.get(id=self.gps_log.driver.id)
        self.assertEqual(dr.location_time, self.gps_log.datetime, 'location time not updated in driver app user table')
        self.assertEqual(dr.latitude, self.gps_log.latitude, 'latest latitude not updated in driver app user table')
        self.assertEqual(dr.longitude, self.gps_log.longitude, 'latest longitude not updated in driver app user table')


class TestDriverUpdatePodApi(PostDriverAuthApiTestCase, UnAbstractAuth400):

    def setUp(self):
        super().setUp()
        self.driver.number_verified = True
        self.driver.save()
        self.vehicle = Vehicle.objects.create(driver_app_user=self.driver, vehicle_number=self.driver.vehicle_number)
        self.transaction = Transaction.objects.create(transaction_id='TEST666', total_vehicle_requested=1)
        self.vehicle_allocated = VehicleAllocated.objects.create(
            transaction=self.transaction, vehicle_number=self.vehicle, driver_name=self.driver.driver_name,
            driver_phone=self.driver.driver_number
        )

    def url(self):
        return '/api/driver/update-pod/'

    def schema(self):
        return update_pod_schema()

    def data(self):
        return {'pod': 'pod_file_s3_key', 'pod_thumb': 'pod_thumb_file_s3_key'}

    def confirm_result(self):
        # check if the driver pod was updated
        driver = get_driver(self.device_id)
        self.assertIsNotNone(driver, 'Driver with device id %s does not exist in the database' % self.device_id)
        vehicle_allocated = get_or_none(VehicleAllocated, id=self.vehicle_allocated.id)
        self.assertEqual(vehicle_allocated.pod, self.data()['pod'], 'pod not updated')
        self.assertEqual(vehicle_allocated.pod_thumb, self.data()['pod_thumb'], 'pod_thumb not updated')


class TestDriverVerifyOtpApi(PostDriverAuthApiTestCase, UnAbstractAuth400):

    def setUp(self):
        super().setUp()
        self.driver.number_verified = False
        self.driver.save()
        self.otp = OTP.generate(self.driver.driver_number)

    def url(self):
        return '/api/driver/verify-otp/'

    def data(self):
        return {'otp': self.otp}

    def confirm_result(self):
        # check if the driver number_verified was changed
        driver = get_driver(self.device_id)
        self.assertIsNotNone(driver, 'Driver with device id %s does not exist in the database' % self.device_id)
        self.assertTrue(driver.number_verified, 'Driver number still not marked verified')

'''
# class TestDriverSendOtpApi(PostDriverAuthApiTestCase, UnAbstractAuth):
#
#     def setUp(self):
#         super(TestDriverSendOtpApi, self).setUp()
#         self.original_sms_setting = settings.ENABLE_SMS
#         settings.ENABLE_SMS = False
#
#     def url(self):
#         return '/api/driver/send-otp/'
#
#     def confirm_result(self):
#         # check if the otp was created
#         driver = get_driver(self.device_id)
#         self.assertIsNotNone(driver, 'Driver with device id %s does not exist in the database' % self.device_id)
#         otp_instance = get_or_none(OTP, phone=driver.driver_number)
#         self.assertIsNotNone(otp_instance, 'Entry missing in OTP table for number %s' % self.driver.driver_number)
#         self.assertGreater(otp_instance.expires_at, timezone.now(), 'OTP already expired')
#
#     def tearDown(self):
#         super(TestDriverSendOtpApi, self).tearDown()
#         settings.ENABLE_SMS = self.original_sms_setting


class TestDriverEditDetailsApi(PostDriverAuthApiTestCase, UnAbstractAuth):

    def url(self):
        return '/api/driver/edit-details/'

    def data(self):
        self.new_name = 'Jason Bourne'
        return {'driver_name': self.new_name}

    def confirm_result(self):
        # check if the driver name was changed
        driver = get_driver(self.device_id)
        self.assertIsNotNone(driver, 'Driver with device id %s does not exist in the database' % self.device_id)
        self.assertEqual(driver.driver_name, self.new_name, 'Driver name not updated')


class TestDriverVehicleStatusApi(PostDriverAuthApiTestCase, UnAbstractAuth400):

    def setUp(self):
        super().setUp()
        self.old_status = 'unloading'
        self.new_status = 'loading'
        self.driver.vehicle_status = self.old_status
        self.driver.save()
        self.vehicle = Vehicle.objects.create(driver_app_user=self.driver, vehicle_number=self.driver.vehicle_number,
                                              status=self.old_status)

    def url(self):
        return '/api/driver/vehicle-status/'

    def data(self):
        return {'vehicle_status': self.new_status}

    def invalid_data(self):
        return {'vehicle_status': 'invalid_status'}

    def confirm_result(self):
        # check if the driver vehicle status was changed
        driver = get_driver(self.device_id)
        self.assertIsNotNone(driver, 'Driver with device id %s does not exist in the database' % self.device_id)
        self.check_vehicle_status(driver)

    def check_vehicle_status(self, driver):
        self.assertEqual(driver.vehicle_status, self.new_status, 'Status not updated')
        vehicle = get_or_none(Vehicle, driver_app_user=driver)
        new_vehicle_status = self.new_status if driver.number_verified else self.old_status
        unverified_err_msg = 'Status should not be updated if driver.number_verified = False'
        verified_err_msg = 'Status should be updated if driver.number_verified = True'
        err_msg = verified_err_msg if driver.number_verified else unverified_err_msg
        self.assertEqual(vehicle.status, new_vehicle_status, err_msg)


class TestDriverVehicleStatusApiVehicleStatus(TestDriverVehicleStatusApi):

    def setUp(self):
        super().setUp()
        self.driver.number_verified = True
        self.driver.save()
