# from datetime import timedelta, datetime
# from django.contrib.auth.models import User
# from django.utils import timezone
#
# from api.abstract import GetCustomerAuthApiTestCase, GetApiTestCase, UnAbstractAuth, UnAbstract, PostApiTestCase, \
#     PASSWORD, PostCustomerAuthApiTestCase, UnAbstractAuth400
# from api.utils import format_iso
# from customer.test_helper import setup_for_vendor_request, get_vendor_request_data, \
#     confirm_vendor_request_result, setup_for_new_booking, get_cached_booking_request_data, confirm_new_booking_result, \
#     get_add_vendor_data, confirm_add_vendor_result, setup_for_delete_vendor, get_delete_vendor_data, \
#     confirm_delete_vendor_result, check_403_on_delete_vendor
#
# from customer.schema import customer_app_data_schema, customer_login_status_schema, customer_delete_vendor_schema, \
#     customer_add_vendor_schema, customer_edit_profile_schema, customer_new_booking_schema
# from fms.test_helper import add_app_data, add_vehicle_categories
# from sme.models import ContactDetails
# from transaction.models import UserVendor, Transaction, TransactionVendorRequest
# from utils.models import City
#
#
# # GETs
#
#
# class TestCustomerAppDataApi(GetCustomerAuthApiTestCase, UnAbstractAuth):
#
#     def url(self):
#         return '/api/customer/app-data/'
#
#     def schema(self):
#         return customer_app_data_schema()
#
#
# class TestCustomerLoginStatusApi(GetApiTestCase, UnAbstract):
#
#     def url(self):
#         return '/api/customer/login-status/'
#
#     def schema(self):
#         return customer_login_status_schema()
#
#
# # POSTs
#
# class TestChangePasswordApi(PostCustomerAuthApiTestCase, UnAbstractAuth400):
#
#     def url(self):
#         return '/api/customer/change-password/'
#
#     def data(self):
#         self.new_pass = 'OK1lets2do3this!'
#         return self.get_data(self.new_pass)
#
#     def invalid_data(self):
#         return self.get_data('2.tiny')
#
#     def get_data(self, new_pass, curr_pass=PASSWORD):
#         return {'current_password': curr_pass, 'new_password': new_pass}
#
#     def error_400_msg(self):
#         return 'Should give 400 response on invalid new password e.g. if the password is too small or something'
#
#     def confirm_result(self):
#         user = User.objects.get(id=self.user.id)
#         self.assertTrue(user.check_password(self.new_pass), 'Password does not match')
#
#     def test_wrong_password(self):
#         self.login()
#         response = self.get_response(data=self.get_data('valid new password', curr_pass='incorrect password'))
#         self.assert_response_code(self.url(), response, 403, 'Should give 403 response on incorrect password')
#
#
# class TestEditProfileApi(PostCustomerAuthApiTestCase, UnAbstractAuth400):
#
#     def url(self):
#         return '/api/customer/edit-profile/'
#
#     def data(self):
#         return {
#             'full_name': 'Notamade Upname', 'contact_name': 'Mitch McLovin', 'phone': '9143143143',
#             'email': 'info+66@aaho.in', 'designation': 'Tester'
#         }
#
#     def schema(self):
#         return customer_edit_profile_schema()
#
#     def confirm_result(self):
#         new_vals = self.data()
#         user = User.objects.get(id=self.user.id)
#         self.assertEqual(user.first_name, new_vals['full_name'], 'Full name not updated')
#         contact_updated = ContactDetails.objects.filter(
#             sme=self.sme, name=new_vals['contact_name'], phone=new_vals['phone'],
#             email=new_vals['email'], designation=new_vals['designation']
#         ).exists()
#         self.assertTrue(contact_updated, 'Contact details not created or updated')
#
#
# class TestVendorRequestApi(PostCustomerAuthApiTestCase, UnAbstractAuth400):
#
#     def setUp(self):
#         super(TestVendorRequestApi, self).setUp()
#         setup_for_vendor_request(self)
#
#     def url(self):
#         return '/api/customer/vendor-request/'
#
#     def data(self):
#         return get_vendor_request_data(self)
#
#     def confirm_result(self):
#         confirm_vendor_request_result(self)
#
# #
# # class TestNewBookingApi(PostCustomerAuthApiTestCase, UnAbstractAuth400):
# #
# #     def setUp(self):
# #         super(TestNewBookingApi, self).setUp()
# #         setup_for_new_booking(self)
# #
# #     def url(self):
# #         return '/api/customer/new-booking/'
# #
# #     def data(self):
# #         return get_cached_booking_request_data(self)
# #
# #     def schema(self):
# #         return customer_new_booking_schema()
# #
# #     def confirm_result(self):
# #         confirm_new_booking_result(self)
#
#
# class TestAddVendorApi(PostCustomerAuthApiTestCase, UnAbstractAuth400):
#
#     def url(self):
#         return '/api/customer/add-vendor/'
#
#     def schema(self):
#         return customer_add_vendor_schema()
#
#     def data(self):
#         return get_add_vendor_data()
#
#     def confirm_result(self):
#         confirm_add_vendor_result(self)
#
#
# class TestDeleteVendorApi(PostCustomerAuthApiTestCase, UnAbstractAuth400):
#
#     def setUp(self):
#         super(TestDeleteVendorApi, self).setUp()
#         setup_for_delete_vendor(self)
#
#     def url(self):
#         return '/api/customer/delete-vendor/'
#
#     def schema(self):
#         return customer_delete_vendor_schema()
#
#     def data(self):
#         return get_delete_vendor_data(self)
#
#     def confirm_result(self):
#         confirm_delete_vendor_result(self)
#
#     def test_403_response(self):
#         check_403_on_delete_vendor(self)
