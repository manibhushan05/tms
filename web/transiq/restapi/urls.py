from django.urls import re_path
from rest_framework.authtoken import views as rest_framework_views

from restapi.dynamo.views import DynamoGPSDeviceListView, DynamoGPSDeviceViewSet
from restapi.views import authentication, users, app_version, driver, task_dashboard
from restapi.views import booking
from restapi.views import requirements
from restapi.views.authentication import ProfileViewSet, AWSCredentials
from restapi.views.broker import BrokerVehicleViewSet, BrokerViewSet, BrokerOwnerViewSet, BrokerDriverViewSet, \
    BrokerAccountViewSet, BrokerVehicleListView, BrokerOwnerListView, BrokerDriverListView, \
    BrokerAccountListView, BrokerListView, BrokerSummaryListView
from restapi.views.driver import DriverAppUserViewSet, GPSLogNewViewSet, OTPViewSet, GPSDeviceViewSet, \
    GPSDeviceLogViewSet, TracknovateGPSDeviceViewSet, TracknovateGPSDeviceLogViewSet, WaytrackerGPSDeviceViewSet, \
    WaytrackerGPSDeviceLogViewSet, TempoGoGPSDeviceViewSet, TempoGoGPSDeviceLogViewSet, SecuGPSDeviceViewSet, \
    SecuGPSDeviceLogViewSet, MahindraGPSDeviceViewSet, MahindraGPSDeviceLogViewSet, DriverViewSet, DriverPageView, \
    DriverListView, GPSDeviceListView, GPSDeviceProviderListView
from restapi.views.employee import EmployeeViewSet, DesignationViewSet, DepartmentViewSet, FitnessViewSet, \
    PastEmploymentViewSet, PermanentAddressViewSet, ReferralViewSet, EmploymentAgencyViewSet, \
    CurrentEmploymentDetailsViewSet, EducationalDegreeViewSet, CertificationCourseViewSet, SkillSetViewSet, \
    NomineeViewSet, LeaveRecordViewSet, SalaryViewSet, TaskViewSet, TaskEmailViewSet, EmployeeListView
from restapi.views.file_upload import PODFileViewSet, VehicleFileViewSet, OwnerFileViewSet, DriverFileViewSet, \
    ChequeFileViewSet, InvoiceReceiptFileViewSet, PODFileListView, VehicleFileListView, DriverFileListView, \
    OwnerFileListView, ChequeFileListView, InvoiceReceiptFileListView, PODFileCreatePageView
from restapi.views.notifications import MobileDeviceViewSet, MobileDeviceListView
from restapi.views.owner import OwnerViewSet, OwnerVehicleViewSet, RouteViewSet, FuelCardViewSet, \
    FuelCardTransactionViewSet, OwnerListView, OwnerVehicleListView, FuelCardListView, OwnerVehicleSummaryListView
from restapi.views.sme import SmeViewSet, CustomerContractViewSet, SmeTaskEmailViewSet, RateTypeViewSet, \
    ContractRouteViewSet, ContactDetailsViewSet, LocationViewSet, ConsignorConsigneeViewSet, PreferredVehicleViewSet, \
    SmeEnquiryViewSet, SmeListView, SmeTaskEmailListView, RateTypeListView, CustomerContractListView, \
    ContractRouteListView, ContactDetailsListView, LocationListView, ConsignorConsigneeListView, \
    PreferredVehicleListView, SmeCreatePageView, SmeSummaryListView
from restapi.views.supplier import VehicleBodyCategoryViewSet, VehicleCategoryViewSet, VehicleViewSet, \
    ServiceViewSet, SupplierViewSet, ContactPersonViewSet, SupplierDriverViewSet, SupplierDriverPhoneViewSet, \
    DriverVehicleViewSet, VehicleStatusViewSet, VehicleInsurerViewSet, VehicleInsuranceViewSet, VehiclePUCViewSet, \
    VehicleFitnessViewSet, VehiclePermitViewSet, SupplierVehicleViewSet, SupplierVehicleListView, \
    VehicleCategoryListView, ServiceListView, SupplierListView, ContactPersonListView, SupplierDriverListView, \
    SupplierDriverPhoneListView, VehicleBodyCategoryListView, DriverVehicleListView, VehicleStatusListView, \
    VehicleInsurerListView, VehicleInsuranceListView, VehiclePUCListView, VehicleFitnessListView, VehiclePermitListView, \
    VehicleListView, VehicleAccountingSummaryListView, SupplierAccountingSummaryListView
from restapi.views.team import InvoiceSummaryViewSet, ManualBookingViewSet, LrNumberViewSet, RejectedPODViewSet, \
    BookingConsignorConsigneeViewSet, InWardPaymentViewSet, OutWardPaymentViewSet, OutWardPaymentBillViewSet, \
    InvoiceViewSet, ToPayInvoiceViewSet, PendingInwardPaymentEntryViewSet, BookingInsuranceViewSet, \
    CreditDebitNoteReasonViewSet, CreditNoteCustomerViewSet, DebitNoteCustomerViewSet, CreditNoteSupplierViewSet, \
    DebitNoteSupplierViewSet, CreditNoteCustomerDirectAdvanceViewSet, DebitNoteSupplierDirectAdvanceViewSet, \
    ManualBookingListView, InwardPaymentListView, OutwardPaymentListView, OutwardPaymentBillListView, InvoiceListView, \
    CreditDebitNoteReasonListView, CreditNoteCustomerListView, DebitNoteCustomerListView, CreditNoteSupplierListView, \
    DebitNoteSupplierListView, CreditNoteCustomerDirectAdvanceListView, DebitNoteSupplierDirectAdvanceListView, \
    DashboardPageView, InvoiceSummaryListView, LrNumberListView, ManualBookingMISListView, TinyManualBookingListView, \
    DownloadPaymentFiles, DataTablesFilterViewSet, MobileDashboardPageView
from restapi.views.utils import StateViewSet, CityViewSet, AddressViewSet, IDDetailsViewSet, BankNameViewSet, \
    IfscDetailViewSet, BankViewSet, AahoOfficeViewSet, TaxationIDViewSet, BankListView, CityListView, \
    AahoOfficeListView, StateListView, BankNameListView, MultipleChoicesFilterListView
from restapi.views.views_page import OwnerListPageView, OwnerVehicleListPageView, SmeListPageView, SupplierListPageView, \
    DriverListPageView, VehicleRegisterPageView, OwnerRegisterPageView, SmeRegisterPageView, SupplierRegisterPageView, \
 \
    DriverRegisterPageView, IssueCreditDebitNotePageView, \
    ApproveCreditDebitNotePageView, IssueCreditNoteCustomerPageView, IssueCreditNoteSupplierPageView, \
    IssueDebitNoteCustomerPageView, IssueCreditNoteCustomerDirectAdvancePageView, IssueDebitNoteSupplierPageView, \
    ApproveCreditNoteCustomerPageView, ApproveCreditNoteSupplierPageView, ApproveDebitNoteCustomerPageView, \
    ApproveDebitNoteSupplierPageView, ApproveCreditNoteCustomerDirectAdvancePageView, ChequeFilePageView, \
    ManualBookingListPage, OutwardPaymentPageView, ManualBookingCreatePageView, UpdateContractBookingPage, \
    BookingMISPage, InwardPaymentListPageView, OutwardPaymentListPageView, PendingInwardPageView, ChequePageView, \
    InvoicePageView, PODPageView, AccountingSummaryPageView, BankAccountPageView, TrackVehiclePageView, \
    LrNumberPageView, EmployeeProfilePageView, MobilePageView, DocumentUploadPageView, PODUploadPageView, \
    ChangePasswordPageView, DownloadPaymentFilePage, PayBalanceBookingHistoryPage, RaiseInvoiceBookingHistoryPage, \
    ReconcilePaymentPage, ProcessPaymentEnetPage, UploadInvoiceSentReceiptPage, ConfirmInvoiceSentPage, \
    BookingStatusesMonitoringPageView, TaskStatusesMonitoringPageView

user_create = authentication.UserViewSet.as_view({'post': 'create'})
user_detail = authentication.UserViewSet.as_view({'get': 'retrieve'})
user_update = authentication.UserViewSet.as_view({'put': 'update'})
user_partial_update = authentication.UserViewSet.as_view({'patch': 'partial_update'})
user_soft_destroy = authentication.UserViewSet.as_view({'patch': 'soft_destroy'})
user_destroy = authentication.UserViewSet.as_view({'delete': 'destroy'})
retrieve_token_auth_user = authentication.UserTokenLogin.as_view()

vehicle_body_category_create = VehicleBodyCategoryViewSet.as_view({"post": "create"})
vehicle_body_category_update = VehicleBodyCategoryViewSet.as_view({"put": "update"})
vehicle_body_category_partial_update = VehicleBodyCategoryViewSet.as_view({"patch": "partial_update"})
vehicle_body_category_retrieve = VehicleBodyCategoryViewSet.as_view({"get": "retrieve"})

vehicle_category_create = VehicleCategoryViewSet.as_view({"post": "create"})
vehicle_category_update = VehicleCategoryViewSet.as_view({"put": "update"})
vehicle_category_partial_update = VehicleCategoryViewSet.as_view({"patch": "partial_update"})
vehicle_category_retrieve = VehicleCategoryViewSet.as_view({"get": "retrieve"})

vehicle_create = VehicleViewSet.as_view({"post": "create"})
vehicle_update = VehicleViewSet.as_view({"put": "update"})
vehicle_partial_update = VehicleViewSet.as_view({"patch": "partial_update"})
vehicle_retrieve = VehicleViewSet.as_view({"get": "retrieve"})
#

mobile_view_url_pattern = [
    re_path(r'^dashboard/$', MobilePageView.as_view({'post': 'dashboard'}),
            name="mobile_view_dashboard")]
page_url_patterns = [
    # Owner

    re_path(r'^download-payment-file/$', DownloadPaymentFilePage.as_view({'get': 'get'}),
            name="download_payment_page"),
    re_path(r'^pay-balance-booking-history/$', PayBalanceBookingHistoryPage.as_view({'get': 'get'}),
            name="pay_balance_booking_history_page"),
    re_path(r'^raise-invoice-booking-history/$', RaiseInvoiceBookingHistoryPage.as_view({'get': 'get'}),
            name="raise_invoice_booking_history_page"),
    re_path(r'^upload-invoice-send-receipt/$', UploadInvoiceSentReceiptPage.as_view({'get': 'get'}),
            name="upload_invoice_sent_receipt_page"),
    re_path(r'^confirm-invoice-sent-receipt/$', ConfirmInvoiceSentPage.as_view({'get': 'get'}),
            name="confirm_invoice_sent_receipt"),
    re_path(r'^process-payment-enet/$', ProcessPaymentEnetPage.as_view({'get': 'get'}),
            name="process_payment"),
    re_path(r'^reconcile-payment/$', ReconcilePaymentPage.as_view({'get': 'get'}),
            name="raise_invoice_booking_history_page"),
    re_path(r'^basic-full-booking/$', ManualBookingCreatePageView.as_view({'get': 'get_basic_full_booking'}),
            name="basic_full_booking_page"),
    re_path(r'^confirm-new-booking/$', ManualBookingCreatePageView.as_view({'get': 'get_confirm_booking'}),
            name="confirm_new_booking"),
    re_path(r'^detailed-full-booking/$', ManualBookingCreatePageView.as_view({'get': 'get_detailed_full_booking'}),
            name="detailed_full_booking_page"),
    re_path(r'^team-manual-booking-detailed-lr/(?P<pk>[0-9]+)/$',
            ManualBookingCreatePageView.as_view({'get': 'get_detailed_full_booking_mb_id_based'}),
            name="detailed_full_booking_page_mb_id_based"),
    re_path(r'^basic-commission-booking/$',
            ManualBookingCreatePageView.as_view({'get': 'get_basic_commission_booking'}),
            name="basic_commission_booking_page"),
    re_path(r'^detailed-commission-booking/$',
            ManualBookingCreatePageView.as_view({'get': 'get_detailed_commission_booking'}),
            name="basic_commission_booking_page"),
    re_path(r'^update-contract-booking/$', UpdateContractBookingPage.as_view({'get': 'get'}),
            name="update_contract_booking_page"),
    re_path(r'^booking-mis/$', BookingMISPage.as_view({'get': 'get'}), name="booking_mis_page"),
    re_path(r'^outward-payment-list/$', OutwardPaymentListPageView.as_view({'get': 'get'}),
            name="outward_payment_list"),
    re_path(r'^outward-payment-receipt-list/$', OutwardPaymentListPageView.as_view({'get': 'get_payment_receipt'}),
            name="get_payment_receipt_page"),

    re_path(r'^add-recieved-payment/$', PendingInwardPageView.as_view({'get': 'get'}),
            name="add_received_inward_payment"),
    re_path(r'^pending-inward-list/$', PendingInwardPageView.as_view({'get': 'unadjusted_list'}),
            name="pending_inward_list"),
    re_path(r'^pending-inward-adjustment/$', PendingInwardPageView.as_view({'get': 'payment_adjustment'}),
            name="pending_inward_payment_adjustment"),
    re_path(r'^upload-cheque/$', ChequePageView.as_view({'get': 'create'}), name="create_cheque_page"),
    re_path(r'^uncredited-cheques/$', ChequePageView.as_view({'get': 'uncredited_cheque_list'}),
            name="uncredited_cheque_page"),
    re_path(r'^invoices/$', InvoicePageView.as_view({'get': 'list'}), name="invoice_list_page"),
    re_path(r'^invoices-summary/$', InvoicePageView.as_view({'get': 'summary'}), name="invoice_summary_list_page"),
    re_path(r'^fetch-full-booking-invoie/$', InvoicePageView.as_view({'get': 'fetch_full_booking_invoice'}),
            name="fetch_full_booking_invoice_page"),
    re_path(r'^full-booking-invoie/$', InvoicePageView.as_view({'get': 'full_booking_invoice'}),
            name="full_booking_invoice_page"),
    re_path(r'^commission-booking-invoie/$', InvoicePageView.as_view({'get': 'commission_booking_invoice'}),
            name="commission_booking_invoice_page"),
    re_path(r'^fetch-commission-booking-invoie/$', InvoicePageView.as_view({'get': 'fetch_commission_booking_invoice'}),
            name="fetch_commission_booking_invoice_page"),
    re_path(r'^inward-payment-list/$', InwardPaymentListPageView.as_view({'get': 'get'}),
            name="inward_payment_list_page"),
    re_path(r'^pod-list/$', PODPageView.as_view({'get': 'list'}), name="pod_list_page"),
    re_path(r'^unverified-pod-list/$', PODPageView.as_view({'get': 'unverified_pod'}), name="unverified_pod_list_page"),
    re_path(r'^bookings-verify-pod-page/$', PODPageView.as_view({'get': 'td_unverified_pod'}),
            name="td_unverified_pod_list_page"),
    re_path(r'^my-uploaded-pod-list/$', PODPageView.as_view({'get': 'my_uploaded_pod'}),
            name="my_uploaded_pod_list_page"),
    re_path(r'^pod-upload/$', PODPageView.as_view({'get': 'upload'}), name="pod_upload_page"),
    re_path(r'^placed-order-customer-accounting-summary-page/$',
            AccountingSummaryPageView.as_view({'get': 'get_placed_order_customer_summary'}),
            name="get_placed_order_customer_summary_page"),
    re_path(r'^billed-customer-accounting-summary-page/$',
            AccountingSummaryPageView.as_view({'get': 'get_billed_customer_summary'}),
            name="get_billed_customer_summary_page"),
    re_path(r'^vehicle-accounting-summary-page/$', AccountingSummaryPageView.as_view({'get': 'get_vehicle_summary'}),
            name="get_vehicle_summary_page"),
    re_path(r'^supplier-accounting-summary-page/$', AccountingSummaryPageView.as_view({'get': 'get_supplier_summary'}),
            name="get_supplier_summary_page"),
    re_path(r'^fetch-ifsc/$', BankAccountPageView.as_view({'get': 'fetch_ifsc'}), name="fetch_ifsc_page"),
    re_path(r'^create-bank-account/$', BankAccountPageView.as_view({'get': 'create'}), name="create_bank_account_page"),
    re_path(r'^bank-account-list/$', BankAccountPageView.as_view({'get': 'list'}), name="bank_account_list_page"),
    re_path(r'^track-vehicles-dashboard/$', TrackVehiclePageView.as_view({'get': 'track_vehicles'}),
            name="track_dashboard_page"),
    re_path(r'^track-vehicle-dashboard/$', TrackVehiclePageView.as_view({'get': 'track_vehicle'}),
            name="track_dashboard_page"),
    re_path(r'^download-lr/$', LrNumberPageView.as_view({'get': 'list'}), name="download_lr_page"),
    re_path(r'^employee-profile/$', EmployeeProfilePageView.as_view({'get': 'get'}), name="employee_profile_page"),
    re_path(r'^change-password/$', ChangePasswordPageView.as_view({'get': 'get'}), name="change_password_page"),
    re_path(r'^owner-list-page/$', OwnerListPageView.as_view(), name="owner_list_page"),
    re_path(r'^owner-vehicle-list-page/$', OwnerVehicleListPageView.as_view(),
            name="team_owner_vehicle_list_page"),
    re_path(r'^sme-list-page/$', SmeListPageView.as_view(), name="sme_list_page"),
    re_path(r'^supplier-list-page/$', SupplierListPageView.as_view(), name="supplier_list_page"),
    re_path(r'^driver-list-page/$', DriverListPageView.as_view(), name="driver_list_page"),

    # Registrations

    re_path(r'^register-vehicle-page/$', VehicleRegisterPageView.as_view(), name="vehicle_register_page"),
    re_path(r'^register-owner-page/$', OwnerRegisterPageView.as_view(), name="owner_register_page"),
    re_path(r'^register-sme-page/$', SmeRegisterPageView.as_view(), name="sme_register_page"),
    re_path(r'^register-supplier-page/$', SupplierRegisterPageView.as_view(), name="supplier_register_page"),
    re_path(r'^register-driver-page/$', DriverRegisterPageView.as_view(), name="driver_register_page"),
    # booking
    re_path(r'^partial-booking-list-page/$', ManualBookingListPage.as_view({'get': 'get_partial_booking'}),
            name="partial_booking_list_page"),
    re_path(r'^full-booking-list-page/$', ManualBookingListPage.as_view({'get': 'get_full_booking'}),
            name="full_booking_list_page"),
    re_path(r'^generate-lr-page/$', ManualBookingListPage.as_view({'get': 'get_generate_lr'}),
            name="generate_lr_page"),
    re_path(r'^bookings-pay-advance-page/$', ManualBookingListPage.as_view({'get': 'get_bookings_pay_advance'}),
            name="bookings_pay_advance_page"),

    # File Upload
    re_path(r'^pod-upload-page/$', PODUploadPageView.as_view(), name="pod_upload_page"),
    re_path(r'^supplier-upload/$', DocumentUploadPageView.as_view({'get': 'supplier'}), name="owner_upload_page"),
    re_path(r'^driver-upload/$', DocumentUploadPageView.as_view({'get': 'driver'}), name="driver_upload_page"),
    re_path(r'^vehicle-upload/$', DocumentUploadPageView.as_view({'get': 'vehicle'}), name="vehicle_upload_page"),
    re_path(r'^weighing-slip-upload/$', DocumentUploadPageView.as_view({'get': 'weighing_slip'}), name="weighing_slip_upload_page"),
    re_path(r'^cheque-upload/$', DocumentUploadPageView.as_view({'get': 'cheque'}), name="cheque_upload_page"),
    re_path(r'^invoice-receipt-upload/$', DocumentUploadPageView.as_view({'get': 'invoice_receipt'}),
            name="invoice_receipt_upload_page"),

    # ISSUE CREDIT DEBIT NOTE
    re_path(r'^issue-credit-debit-note-page/$', IssueCreditDebitNotePageView.as_view(),
            name="issue_credit_debit_note_page"),
    re_path(r'^issue-credit-note-customer-page/$', IssueCreditNoteCustomerPageView.as_view(),
            name="issue_credit_note_customer_page"),
    re_path(r'^issue-credit-note-supplier-page/$', IssueCreditNoteSupplierPageView.as_view(),
            name="issue_credit_note_supplier_page"),
    re_path(r'^issue-debit-note-customer-page/$', IssueDebitNoteCustomerPageView.as_view(),
            name="issue_debit_note_customer_page"),
    re_path(r'^issue-debit-note-supplier-page/$', IssueDebitNoteSupplierPageView.as_view(),
            name="issue_debit_note_supplier_page"),
    re_path(r'^issue-credit-note-customer-direct-advance-page/$',
            IssueCreditNoteCustomerDirectAdvancePageView.as_view(),
            name="issue_credit_note_customer_direct_advance_page"),

    # Approve CREDIT DEBIT NOTE

    re_path(r'^approve-credit-debit-note-page/$', ApproveCreditDebitNotePageView.as_view(),
            name="approve_credit_debit_note_page"),

    re_path(r'^approve-credit-note-customer-page/$', ApproveCreditNoteCustomerPageView.as_view(),
            name="approve_credit_note_customer_page"),
    re_path(r'^approve-credit-note-supplier-page/$', ApproveCreditNoteSupplierPageView.as_view(),
            name="approve_credit_note_supplier_page"),
    re_path(r'^approve-debit-note-customer-page/$', ApproveDebitNoteCustomerPageView.as_view(),
            name="approve_debit_note_customer_page"),
    re_path(r'^approve-debit-note-supplier-page/$', ApproveDebitNoteSupplierPageView.as_view(),
            name="approve_debit_note_supplier_page"),
    re_path(r'^approve-credit-note-customer-direct-advance-page/$',
            ApproveCreditNoteCustomerDirectAdvancePageView.as_view(),
            name="approve_credit_note_customer_direct_advance_page"),

    re_path(r'^approve-credit-debit-note-page/$', ApproveCreditDebitNotePageView.as_view(),
            name="approve_credit_debit_note_page"),

    re_path(r'^uncredited-cheques/$', ChequeFilePageView.as_view(), name="uncredited_cheques"),

    # Outward Payment Page
    re_path(r'^outward-payment-page/$', OutwardPaymentPageView.as_view(), name="outward_payment_page"),

    re_path(r'^monitoring-web-senior-mgmt-booking-status-page/$', BookingStatusesMonitoringPageView.as_view(),
            name="monitoring_web_senior_mgmt_status_page"),

    re_path(r'^monitoring-web-senior-mgmt-task-status-page/$', TaskStatusesMonitoringPageView.as_view(),
            name="monitoring_web_senior_mgmt_task_status_page")
]

restapi_urlpatterns = [

    # Authentication TC Plan: Done
    re_path(r'^get-auth-token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    re_path(r'^login/$', authentication.UserLogin.as_view(), name='login'),
    re_path(r'^logout/$', authentication.UserLogout.as_view(), name='logout'),
    re_path(r'^groups-list/$', authentication.GroupViewSet.as_view({'get': 'list'}), name='groups_list'),
    # re_path(r'^signup/$', authentication.UserRegister.as_view({'post': 'create_user'}), name='signup'),
    re_path(r'^change-password/$', authentication.UserUpdatePassword.as_view(), name='change_password'),
    re_path(r'^forgot-password/$', authentication.UserForgotPassword.as_view({'post': 'send_otp'}), name='forgot_pwd'),
    re_path(r'^verify-otp/$', authentication.UserForgotPassword.as_view({'post': 'verify_otp'}), name='verify_otp'),
    re_path(r'^reset-password/$', authentication.UserResetPassword.as_view(), name='reset_password'),
    re_path(r'^get-phone-username/$', authentication.UserForgotPassword.as_view({'get': 'get_phone_username'}),
            name='get_phone_username'),

    # User Category TC Plan: Done
    re_path(r'^usercategory-list/$', users.UserCategoryListView.as_view(), name='usercategory_list'),
    re_path(r'^multichoice-filter-list/$', MultipleChoicesFilterListView.as_view({'get': 'list'}),
            name='multiple_choices_list'),
    re_path(r'^usercategory-create/$', users.UserCategoryViewSet.as_view({'post': 'create'}),
            name='usercategory_create'),
    re_path(r'^usercategory-detail/(?P<pk>[0-9]+)/$', users.UserCategoryViewSet.as_view({'get': 'retrieve'}),
            name='usercategory_detail'),
    re_path(r'^usercategory-update/(?P<pk>[0-9]+)/$', users.UserCategoryViewSet.as_view({'put': 'update'}),
            name='usercategory_update'),
    re_path(r'^usercategory-destroy/(?P<pk>[0-9]+)/$', users.UserCategoryViewSet.as_view({'delete': 'destroy'}),
            name='usercategory_destroy'),

    # User Initial Data TC Plan: Done
    re_path(r'^get-user-initial-data/$', users.UserInitialData.as_view(), name='get_user_initial_data'),
    re_path(r'^get-user-initial-td-functionalities-data/$', users.UserInitialTDFunctionalitiesData.as_view(
        {'get': 'retrieve_td_func_data'}), name='get_user_initial_td_functionalities_data'),

    # Requirement Quotes TC Plan: Done
    re_path(r'^req-quotes-list/$', requirements.RequirementQuotesListView.as_view(), name='req_quotes_list'),
    re_path(r'^req-quotes-create/$', requirements.RequirementQuotesViewSet.as_view({'post': 'create'}),
            name='req_quotes_create'),
    re_path(r'^req-quotes-detail/(?P<pk>[0-9]+)/$', requirements.RequirementQuotesViewSet.as_view({'get': 'retrieve'}),
            name='req_quotes_detail'),
    re_path(r'^req-quotes-update/(?P<pk>[0-9]+)/$', requirements.RequirementQuotesViewSet.as_view({'post': 'update'}),
            name='req_quotes_update'),
    re_path(r'^req-quotes-destroy/(?P<pk>[0-9]+)/$', requirements.RequirementQuotesViewSet.as_view({'post': 'destroy'}),
            name='req_quotes_destroy'),

    # Requirement Apis TC Plan: Done
    re_path(r'^requirement-create/$', requirements.RequirementViewSet.as_view({'post': 'create'}),
            name='requirement_create'),
    re_path(r'^requirement-update/(?P<pk>[0-9]+)/$', requirements.RequirementViewSet.as_view({'post': 'update'}),
            name='requirement_update'),
    re_path(r'^requirement-destroy/(?P<pk>[0-9]+)/$', requirements.RequirementViewSet.as_view({'post': 'destroy'}),
            name='requirement_destroy'),
    re_path(r'^requirement-detail/(?P<pk>[0-9]+)/$', requirements.RequirementViewSet.as_view({'get': 'retrieve'}),
            name='requirement_detail'),
    re_path(r'^requirement-list-all/$', requirements.RequirementListView.as_view(),
            name='requirements_list'),
    re_path(r'^requirement-list-filter/$', requirements.RequirementListView.as_view(), name='requirement_list_filter'),
    re_path(r'^requirement-list-user/$', requirements.RequirementUserListView.as_view(), name='requirement_list_user'),
    re_path(r'^user-list/$', users.UserListView.as_view(), name='user_list'),
    re_path(r'^get-requirement-cancel-reasons/$', requirements.RequirementViewSet.as_view(
        {'get': 'retrieve_cancel_reasons'}), name='get_requirement_cancel_reasons'),

    # Mobile App Version Apis TC Plan: Done
    re_path(r'^mobile-app-version-list/$', app_version.MobileAppVersionListView.as_view(),
            name='mobile_app_version_list'),
    re_path(r'^mobile-app-version-create/$', app_version.MobileAppVersionViewSet.as_view({'post': 'create'}),
            name='mobile_app_version_create'),
    re_path(r'^mobile-app-version-detail/(?P<pk>[0-9]+)/$', app_version.MobileAppVersionViewSet.as_view(
        {'get': 'retrieve'}), name='mobile_app_version_retrieve'),
    re_path(r'^mobile-app-version-update/(?P<pk>[0-9]+)/$', app_version.MobileAppVersionViewSet.as_view(
        {'post': 'update'}), name='mobile_app_version_update'),
    re_path(r'^mobile-app-version-destroy/(?P<pk>[0-9]+)/$', app_version.MobileAppVersionViewSet.as_view(
        {'post': 'destroy'}), name='mobile_app_version_destroy'),
    re_path(r'^mobile-app-version-check/$', app_version.MobileAppVersionViewSet.as_view(
        {'post': 'check'}), name='mobile_app_version_check'),

    # Notification Apis TC Plan: Done
    re_path(r'^notification-mobile-devices-list/$', MobileDeviceListView.as_view(),
            name="notification_mobile_devices_list"),
    re_path(r'^notification-mobile-device-create-update/$', MobileDeviceViewSet.as_view({"post": "create"}),
            name="notification_mobile_device_create_update"),
    # re_path(r'^notification-mobile-device-update/(?P<pk>[0-9]+)/$',
    #         MobileDeviceViewSet.as_view({"put": "update"}), name="notification_mobile_device_update"),
    # re_path(r'^notification-mobile-device-partial-update/(?P<pk>[0-9]+)/$',
    #         MobileDeviceViewSet.as_view({"patch": "partial_update"}),
    #         name="notification_mobile_device_partial_update"),
    # re_path(r'^notification-mobile-device-retrieve/(?P<pk>[0-9]+)/$',
    #         MobileDeviceViewSet.as_view({"get": "retrieve"}), name="notification_mobile_device_retrieve"),

    # Task Dashboard
    # Employee Roles TC Plan: Done
    re_path(r'^employee-roles-list/$', task_dashboard.EmployeeRolesListView.as_view(), name='employee_roles_list/'),
    re_path(r'^employee-roles-create/$', task_dashboard.EmployeeRolesViewSet.as_view({'post': 'create'}),
            name='employee_roles_create/'),
    re_path(r'^employee-roles-retrieve/(?P<pk>[0-9]+)/$', task_dashboard.EmployeeRolesViewSet.as_view(
        {'get': 'retrieve'}), name='employee_roles_retrieve/'),
    re_path(r'^employee-roles-update/(?P<pk>[0-9]+)/$', task_dashboard.EmployeeRolesViewSet.as_view(
        {'post': 'update'}), name='employee_roles_update/'),
    re_path(r'^employee-roles-destroy/(?P<pk>[0-9]+)/$', task_dashboard.EmployeeRolesViewSet.as_view(
        {'post': 'destroy'}), name='employee_roles_destroy/'),

    # Employee Roles Mapping TC Plan: Done
    re_path(r'^employee-roles-mapping-list/$', task_dashboard.EmployeeRolesMappingListView.as_view(),
            name='employee_roles_mapping_list/'),
    re_path(r'^employee-roles-mapping-data/$', task_dashboard.EmployeeRolesMappingViewSet.as_view({'get': 'employee_role_list'}),
            name='employee_role_list_data/'),
    re_path(r'^employee-roles-mapping-create/$', task_dashboard.EmployeeRolesMappingViewSet.as_view({'post': 'create'}),
            name='employee_roles_mapping_create/'),
    re_path(r'^employee-roles-mapping-retrieve/(?P<pk>[0-9]+)/$', task_dashboard.EmployeeRolesMappingViewSet.as_view(
        {'get': 'retrieve'}), name='employee_roles_mapping_retrieve/'),
    re_path(r'^employee-roles-mapping-update/(?P<pk>[0-9]+)/$', task_dashboard.EmployeeRolesMappingViewSet.as_view(
        {'post': 'update'}), name='employee_roles_mapping_update/'),
    re_path(r'^employee-roles-mapping-destroy/(?P<pk>[0-9]+)/$', task_dashboard.EmployeeRolesMappingViewSet.as_view(
        {'post': 'destroy'}), name='employee_roles_mapping_destroy/'),

    # Booking Statuses TC Plan: Done
    re_path(r'^booking-statuses-list/$', task_dashboard.BookingStatusesListView.as_view(),
            name='booking_statuses_list/'),
    re_path(r'^booking-statuses-create/$', task_dashboard.BookingStatusesViewSet.as_view({'post': 'create'}),
            name='booking_statuses_create/'),
    re_path(r'^booking-statuses-retrieve/(?P<pk>[0-9]+)/$', task_dashboard.BookingStatusesViewSet.as_view(
        {'get': 'retrieve'}), name='booking_statuses_retrieve/'),
    re_path(r'^booking-statuses-update/(?P<pk>[0-9]+)/$', task_dashboard.BookingStatusesViewSet.as_view(
        {'post': 'update'}), name='booking_statuses_update/'),
    re_path(r'^booking-statuses-destroy/(?P<pk>[0-9]+)/$', task_dashboard.BookingStatusesViewSet.as_view(
        {'post': 'destroy'}), name='booking_statuses_destroy/'),

    # Booking Statuses TC Plan: Done
    re_path(r'^booking-status-chain-list/$', task_dashboard.BookingStatusChainListView.as_view(),
            name='booking_status_chain_list/'),
    re_path(r'^booking-status-chain-create/$', task_dashboard.BookingStatusChainViewSet.as_view({'post': 'create'}),
            name='booking_status_chain_create/'),
    re_path(r'^booking-status-chain-retrieve/(?P<pk>[0-9]+)/$', task_dashboard.BookingStatusChainViewSet.as_view(
        {'get': 'retrieve'}), name='booking_status_chain_retrieve/'),
    re_path(r'^booking-status-chain-update/(?P<pk>[0-9]+)/$', task_dashboard.BookingStatusChainViewSet.as_view(
        {'post': 'update'}), name='booking_status_chain_update/'),
    re_path(r'^booking-status-chain-destroy/(?P<pk>[0-9]+)/$', task_dashboard.BookingStatusChainViewSet.as_view(
        {'post': 'destroy'}), name='booking_status_chain_destroy/'),

    # Employee Roles Booking Statuses TC Plan: Done
    re_path(r'^employee-roles-booking-status-mapping-list/$', task_dashboard.EmployeeRolesBookingStatusMappingListView
            .as_view(), name='employee_roles_booking_status_mapping_list/'),
    re_path(r'^employee-roles-booking-status-mapping-create/$', task_dashboard.EmployeeRolesBookingStatusMappingViewSet.
            as_view({'post': 'create'}), name='employee_roles_booking_status_mapping_create/'),
    re_path(r'^employee-roles-booking-status-mapping-retrieve/(?P<pk>[0-9]+)/$',
            task_dashboard.EmployeeRolesBookingStatusMappingViewSet.as_view({'get': 'retrieve'}),
            name='employee_roles_booking_status_mapping_retrieve/'),
    re_path(r'^employee-roles-booking-status-mapping-update/(?P<pk>[0-9]+)/$',
            task_dashboard.EmployeeRolesBookingStatusMappingViewSet.as_view({'post': 'update'}),
            name='employee_roles_booking_status_mapping_update/'),
    re_path(r'^employee-roles-booking-status-mapping-destroy/(?P<pk>[0-9]+)/$',
            task_dashboard.EmployeeRolesBookingStatusMappingViewSet.as_view({'post': 'destroy'}),
            name='employee_roles_booking_status_mapping_destroy/'),

    # Booking Status Mapping TC Plan: Done
    re_path(r'^booking-statuses-mapping-list/$', task_dashboard.BookingStatusesMappingListView.as_view(),
            name='booking_statuses_mapping_list/'),
    re_path(r'^booking-statuses-mapping-create/$',
            task_dashboard.BookingStatusesMappingViewSet.as_view({'post': 'create'}),
            name='booking_statuses_mapping_create/'),
    re_path(r'^booking-statuses-mapping-create-key-based/$',
            task_dashboard.BookingStatusesMappingViewSet.as_view({'post': 'create_key_based'}),
            name='booking_statuses_mapping_create_key_based/'),
    re_path(r'^booking-statuses-mapping-create-key-based-bulk/$',
            task_dashboard.BookingStatusesMappingViewSet.as_view({'post': 'create_key_based_bulk'}),
            name='booking_statuses_mapping_create_key_based_bulk/'),
    re_path(r'^booking-statuses-mapping-retrieve/(?P<pk>[0-9]+)/$',
            task_dashboard.BookingStatusesMappingViewSet.as_view(
                {'get': 'retrieve'}), name='booking_statuses_mapping_retrieve/'),
    re_path(r'^booking-statuses-mapping-update/(?P<pk>[0-9]+)/$', task_dashboard.BookingStatusesMappingViewSet.as_view(
        {'post': 'update'}), name='booking_statuses_mapping_update/'),
    re_path(r'^booking-statuses-mapping-update-key-based-bulk/$',
            task_dashboard.BookingStatusesMappingViewSet.as_view({'post': 'update_key_based_bulk'}),
            name='booking_statuses_mapping_update_key_based_bulk/'),
    re_path(r'^booking-statuses-mapping-update-invoice-based/$',
            task_dashboard.BookingStatusesMappingViewSet.as_view({'post': 'update_invoice_based'}),
            name='booking_statuses_mapping_update_invoice_based/'),
    re_path(r'^booking-statuses-mapping-destroy/(?P<pk>[0-9]+)/$', task_dashboard.BookingStatusesMappingViewSet.as_view(
        {'post': 'destroy'}), name='booking_statuses_mapping_destroy/'),

    # Task Dashboard Functionalities TC Plan: Done
    re_path(r'^task-dashboard-functionalities-list/$', task_dashboard.TaskDashboardFunctionalitiesListView.as_view(),
            name='task_dashboard_functionalities_list/'),
    re_path(r'^task-dashboard-functionalities-create/$',
            task_dashboard.TaskDashboardFunctionalitiesViewSet.as_view({'post': 'create'}),
            name='task_dashboard_functionalities_create/'),
    re_path(r'^task-dashboard-functionalities-retrieve/(?P<pk>[0-9]+)/$',
            task_dashboard.TaskDashboardFunctionalitiesViewSet.as_view(
                {'get': 'retrieve'}), name='task_dashboard_functionalities_retrieve/'),
    re_path(r'^task-dashboard-functionalities-update/(?P<pk>[0-9]+)/$',
            task_dashboard.TaskDashboardFunctionalitiesViewSet.as_view(
                {'post': 'update'}), name='task_dashboard_functionalities_update/'),
    re_path(r'^task-dashboard-functionalities-destroy/(?P<pk>[0-9]+)/$',
            task_dashboard.TaskDashboardFunctionalitiesViewSet.as_view(
                {'post': 'destroy'}), name='task_dashboard_functionalities_destroy/'),

    # Employee Roles Functionalities Mapping TC Plan: Done
    re_path(r'^employee-roles-functionalities-mapping-list/$',
            task_dashboard.EmployeeRolesFunctionalityMappingListView.as_view(),
            name='employee_roles_functionalities_mapping_list/'),
    re_path(r'^employee-roles-functionalities-mapping-create/$',
            task_dashboard.EmployeeRolesFunctionalityMappingViewSet.as_view({'post': 'create'}),
            name='employee_roles_functionalities_mapping_create/'),
    re_path(r'^employee-roles-functionalities-mapping-retrieve/(?P<pk>[0-9]+)/$',
            task_dashboard.EmployeeRolesFunctionalityMappingViewSet.as_view(
                {'get': 'retrieve'}), name='employee_roles_functionalities_mapping_retrieve/'),
    re_path(r'^employee-roles-functionalities-mapping-update/(?P<pk>[0-9]+)/$',
            task_dashboard.EmployeeRolesFunctionalityMappingViewSet.as_view(
                {'post': 'update'}), name='employee_roles_functionalities_mapping_update/'),
    re_path(r'^employee-roles-functionalities-mapping-destroy/(?P<pk>[0-9]+)/$',
            task_dashboard.EmployeeRolesFunctionalityMappingViewSet.as_view(
                {'post': 'destroy'}), name='employee_roles_functionalities_mapping_destroy/'),

    # Booking Status Mapping Comments TC Plan: Done
    re_path(r'^booking-statuses-mapping-comments-list/$',
            task_dashboard.BookingStatusesMappingCommentsListView.as_view(),
            name='booking_statuses_mapping_comments_list/'),
    re_path(r'^booking-statuses-mapping-comments-create/$',
            task_dashboard.BookingStatusesMappingCommentsViewSet.as_view({'post': 'create'}),
            name='booking_statuses_mapping_comments_create/'),
    re_path(r'^booking-statuses-mapping-comments-create-bulk/$',
            task_dashboard.BookingStatusesMappingCommentsViewSet.as_view({'post': 'create_bulk'}),
            name='booking_statuses_mapping_comments_create_bulk/'),
    re_path(r'^booking-statuses-mapping-comments-retrieve/(?P<pk>[0-9]+)/$',
            task_dashboard.BookingStatusesMappingCommentsViewSet.as_view({'get': 'retrieve'}),
            name='booking_statuses_mapping_comments_retrieve/'),
    re_path(r'^booking-statuses-mapping-comments-update/(?P<pk>[0-9]+)/$',
            task_dashboard.BookingStatusesMappingCommentsViewSet.as_view({'post': 'update'}),
            name='booking_statuses_mapping_comments_update/'),
    re_path(r'^booking-statuses-mapping-comments-destroy/(?P<pk>[0-9]+)/$',
            task_dashboard.BookingStatusesMappingCommentsViewSet.as_view({'post': 'destroy'}),
            name='booking_statuses_mapping_comments_destroy/'),

    # Booking Status Mapping Location TC Plan: Done
    re_path(r'^booking-statuses-mapping-location-list/$',
            task_dashboard.BookingStatusesMappingLocationListView.as_view(),
            name='booking_statuses_mapping_location_list/'),
    re_path(r'^booking-statuses-mapping-location-create/$',
            task_dashboard.BookingStatusesMappingLocationViewSet.as_view({'post': 'create'}),
            name='booking_statuses_mapping_location_create/'),
    re_path(r'^booking-statuses-mapping-location-save/$',
            task_dashboard.BookingStatusesMappingLocationViewSet.as_view({'post': 'save_location'}),
            name='booking_statuses_mapping_location_create/'),
    re_path(r'^booking-statuses-mapping-location-retrieve/(?P<pk>[0-9]+)/$',
            task_dashboard.BookingStatusesMappingLocationViewSet.as_view({'get': 'retrieve'}),
            name='booking_statuses_mapping_location_retrieve/'),
    re_path(r'^booking-statuses-mapping-location-update/(?P<pk>[0-9]+)/$',
            task_dashboard.BookingStatusesMappingLocationViewSet.as_view({'post': 'update'}),
            name='booking_statuses_mapping_location_update/'),
    re_path(r'^booking-statuses-mapping-location-destroy/(?P<pk>[0-9]+)/$',
            task_dashboard.BookingStatusesMappingLocationViewSet.as_view({'post': 'destroy'}),
            name='booking_statuses_mapping_location_destroy/'),

    # Monitoring TC Plan: Done
    re_path(r'^monitoring-web-senior-mgmt-booking-status/$',
            task_dashboard.BookingStatusesMonitoringViewSet.as_view({'get': 'retrieve_booking_status'}),
            name='monitoring_web_senior_mgmt_booking_status/'),
    re_path(r'^monitoring-web-senior-mgmt-task-status/$',
            task_dashboard.BookingStatusesMonitoringViewSet.as_view({'get': 'retrieve_task_status'}),
            name='monitoring_web_senior_mgmt_task_status/'),
    re_path(r'^monitoring-web-city-head-booking-status/$',
            task_dashboard.BookingStatusesMonitoringViewSet.as_view({'get': 'retrieve_ch_booking_status'}),
            name='monitoring_web_city_head_booking_status/'),
    # re_path(r'^monitoring-web-city-head-task-status/$',
    #        task_dashboard.BookingStatusesMonitoringViewSet.as_view({'get': 'retrieve_ch_task_status'}),
    #        name='monitoring_web_city_head_task_status/'),
    re_path(r'^retrieve-aws-credentials/$',
            AWSCredentials.as_view({'get': 'get_aws_credentials'}), name='retrieve_aws_credentials'),


    re_path(r'^sme-pending-payments-comments-list/$', task_dashboard.SmePendingPaymentsCommentsListView.as_view(),
            name='sme_pending_payments_comments_list/'),
    re_path(r'^sme-pending-payments-comments-create/$', task_dashboard.SmePendingPaymentsCommentsViewSet.as_view({'post': 'create'}),
            name='sme_pending_payments_comments_create/'),
    re_path(r'^sme-pending-payments-comments-retrieve/(?P<pk>[0-9]+)/$', task_dashboard.SmePendingPaymentsCommentsViewSet.as_view(
        {'get': 'retrieve'}), name='sme_pending_payments_comments_retrieve/'),
    re_path(r'^sme-pending-payments-comments-retrieve-sme/(?P<sme_id>[0-9]+)/$', task_dashboard.SmePendingPaymentsCommentsViewSet.as_view(
        {'get': 'retrieve_sme'}), name='sme_pending_payments_comments_retrieve_sme/'),
    re_path(r'^sme-pending-payments-comments-update/(?P<pk>[0-9]+)/$', task_dashboard.SmePendingPaymentsCommentsViewSet.as_view(
        {'post': 'update'}), name='sme_pending_payments_comments_update/'),
    re_path(r'^sme-pending-payments-comments-update-sme/(?P<sme_id>[0-9]+)/$', task_dashboard.SmePendingPaymentsCommentsViewSet.as_view(
        {'post': 'update_sme'}), name='sme_pending_payments_comments_update_sme/'),
    re_path(r'^sme-pending-payments-comments-destroy/(?P<pk>[0-9]+)/$', task_dashboard.SmePendingPaymentsCommentsViewSet.as_view(
        {'post': 'destroy'}), name='sme_pending_payments_comments_destroy/'),


    # re_path(r'^dynamo-gps-device-location-list/$', DynamoGPSDeviceListView.as_view(), name="dynamo_gps_device_list"),
    re_path(r'^dynamo-gps-device-location-create-table/$', DynamoGPSDeviceViewSet.as_view({"post": "create_table"}), name="dynamo_gps_device_create_table"),
    re_path(r'^dynamo-gps-device-location-create-item/$', DynamoGPSDeviceViewSet.as_view({"post": "create_item"}), name="dynamo_gps_device_create_item"),
    re_path(r'^dynamo-gps-device-location-get-item/(?P<pk>[-a-zA-Z0-9]+)/$', DynamoGPSDeviceViewSet.as_view({"get": "retrieve"}), name="dynamo_gps_device_get_item"),
    re_path(r'^dynamo-gps-device-location-delete-item/(?P<pk>[a-zA-Z0-9]+)/$', DynamoGPSDeviceViewSet.as_view({"post": "destroy"}), name="dynamo_gps_device_delete_item"),
    re_path(r'^dynamo-gps-device-location-update-item/(?P<pk>[a-zA-Z0-9]+)/$', DynamoGPSDeviceViewSet.as_view({"post": "update"}), name="dynamo_gps_device_update_item"),


    # User
    re_path(r'^authentication-user-create/$', user_create, name="authentication_user_create"),
    re_path(r'^authentication-user-retrieve/(?P<pk>[0-9]+)/$', user_detail, name="authentication_user_retrieve"),
    re_path(r'^authentication-user-partial-update/(?P<pk>[0-9]+)/$', user_partial_update,
            name="authentication_user_partial_update"),
    re_path(r'^authentication-user-update/(?P<pk>[0-9]+)/$', user_update, name="authentication_user_update"),

    re_path(r'^authentication-user-soft-destroy/(?P<pk>[0-9]+)/$', user_soft_destroy,
            name="authentication_user_soft_destroy"),
    re_path(r'^authentication-user-destroy/(?P<pk>[0-9]+)/$', user_destroy, name="authentication_user_destroy"),
    re_path(r'^retrieve-token-auth-user/$', retrieve_token_auth_user, name="retrieve_token_auth_user"),

    # Profile

    re_path(r'^authentication-user-profile-create/$', ProfileViewSet.as_view({"post": "create"}),
            name="authentication_user_profile_create"),
    re_path(r'^authentication-user-profile-update/(?P<pk>[0-9]+)/$', ProfileViewSet.as_view({"put": "update"})),
    re_path(r'^authentication-user-profile-partial-update/(?P<pk>[0-9]+)/$',
            ProfileViewSet.as_view({"patch": "partial_update"})),
    re_path(r'^fms-user-profile-partial-update/$',
            ProfileViewSet.as_view({"patch": "fms_partial_update"})),
    re_path(r'^authentication-user-profile-retrieve/(?P<pk>[0-9]+)/$', ProfileViewSet.as_view({"get": "retrieve"})),


    # DownloadPaymentFiles
    re_path(r'^download-today-payment-file/$', DownloadPaymentFiles.as_view({'get': 'download_today_payment_file'}),
            name='download_today_payment_file'),
    re_path(r'^send-today-payment-file/$', DownloadPaymentFiles.as_view({'get': 'send_today_payment_file'}),
            name='send_today_payment_file'),
    re_path(r'^send-previous-day-sales-report/$',
            DownloadPaymentFiles.as_view({'get': 'send_previous_day_sales_report'}),
            name='send_previous_day_sales_report'),

    # BROKER FILE START

    # Broker

    re_path(r'^broker-broker-list/$', BrokerListView.as_view(), name="broker_broker_list"),
    re_path(r'^broker-summary-list/$', BrokerSummaryListView.as_view(), name="broker_summary_list"),
    re_path(r'^supplier-accounting-summary-list/$', SupplierAccountingSummaryListView.as_view(), name="supplier_accounting_summary_list"),
    re_path(r'^vehicle-accounting-summary-list/$', VehicleAccountingSummaryListView.as_view(), name="vehicle_accounting_summary_list"),
    re_path(r'^broker-broker-create/$', BrokerViewSet.as_view({"post": "create"}), name="broker_broker_create"),
    re_path(r'^broker-broker-update/(?P<pk>[0-9]+)/$', BrokerViewSet.as_view({"put": "update"}),
            name="broker_broker_update"),
    re_path(r'^broker-broker-partial-update/(?P<pk>[0-9]+)/$', BrokerViewSet.as_view({"patch": "partial_update"}),
            name="broker_broker_partial_update"),
    re_path(r'^broker-broker-retrieve/(?P<pk>[0-9]+)/$', BrokerViewSet.as_view({"get": "retrieve"}),
            name="broker_broker_retrieve"),

    # Broker Vehicle
    re_path(r'^broker-broker-vehicle-list/$', BrokerVehicleListView.as_view(), name="broker_broker_vehicle_list"),
    re_path(r'^broker-broker-vehicle-create/$', BrokerVehicleViewSet.as_view({"post": "create"}),
            name="broker_broker_vehicle_create"),
    re_path(r'^broker-broker-vehicle-update/(?P<pk>[0-9]+)/$', BrokerVehicleViewSet.as_view({"put": "update"}),
            name="broker_broker_vehicle_update"),
    re_path(r'^broker-broker-vehicle-partial-update/(?P<pk>[0-9]+)/$',
            BrokerVehicleViewSet.as_view({"patch": "partial_update"}), name="broker_broker_vehicle_partial_update"),
    re_path(r'^broker-broker-vehicle-retrieve/(?P<pk>[0-9]+)/$', BrokerVehicleViewSet.as_view({"get": "retrieve"}),
            name="broker_broker_vehicle_retrieve"),

    # Broker Owner
    re_path(r'^broker-broker-owner-list/$', BrokerOwnerListView.as_view(), name="broker_broker_owner_list"),
    re_path(r'^broker-broker-owner-create/$', BrokerOwnerViewSet.as_view({"post": "create"}),
            name="broker_broker_owner_create"),
    re_path(r'^broker-broker-owner-update/(?P<pk>[0-9]+)/$', BrokerOwnerViewSet.as_view({"put": "update"}),
            name="broker_broker_owner_update"),
    re_path(r'^broker-broker-owner-partial-update/(?P<pk>[0-9]+)/$',
            BrokerOwnerViewSet.as_view({"patch": "partial_update"}), name="broker_broker_owner_partial_update"),
    re_path(r'^broker-broker-owner-retrieve/(?P<pk>[0-9]+)/$', BrokerOwnerViewSet.as_view({"get": "retrieve"}),
            name="broker_broker_owner_retrieve"),

    # Broker Driver
    re_path(r'^broker-broker-driver-list/$', BrokerDriverListView.as_view(), name="broker_broker_driver_list"),
    re_path(r'^broker-broker-driver-create/$', BrokerDriverViewSet.as_view({"post": "create"}),
            name="broker_broker_driver_create"),
    re_path(r'^broker-broker-driver-update/(?P<pk>[0-9]+)/$', BrokerDriverViewSet.as_view({"put": "update"}),
            name="broker_broker_driver_update"),
    re_path(r'^broker-broker-driver-partial-update/(?P<pk>[0-9]+)/$',
            BrokerDriverViewSet.as_view({"patch": "partial_update"}), name="broker_broker_driver_partial_update"),
    re_path(r'^broker-broker-driver-retrieve/(?P<pk>[0-9]+)/$', BrokerDriverViewSet.as_view({"get": "retrieve"}),
            name="broker_broker_driver_retrieve"),

    # Broker Account
    re_path(r'^broker-broker-account-list/$', BrokerAccountListView.as_view(), name="broker_broker_account_list"),
    re_path(r'^broker-broker-account-create/$', BrokerAccountViewSet.as_view({"post": "create"}),
            name="broker_broker_account_create"),
    re_path(r'^broker-broker-account-update/(?P<pk>[0-9]+)/$', BrokerAccountViewSet.as_view({"put": "update"}),
            name="broker_broker_account_update"),
    re_path(r'^broker-broker-account-partial-update/(?P<pk>[0-9]+)/$',
            BrokerAccountViewSet.as_view({"patch": "partial_update"}), name="broker_broker_account_partial_update"),
    re_path(r'^broker-broker-account-retrieve/(?P<pk>[0-9]+)/$', BrokerAccountViewSet.as_view({"get": "retrieve"}),
            name="broker_broker_account_retrieve"),

    # Document

    # re_path(r'^broker-document-create/$', DocumentViewSet.as_view({"post": "create"})),
    # re_path(r'^broker-document-update/(?P<pk>[0-9]+)/$', DocumentViewSet.as_view({"put": "update"})),
    # re_path(r'^broker-document-partial-update/(?P<pk>[0-9]+)/$',
    #         DocumentViewSet.as_view({"patch": "partial_update"})),
    # re_path(r'^broker-document-retrieve/(?P<pk>[0-9]+)/$', DocumentViewSet.as_view({"get": "retrieve"})),

    # BROKER FILE END

    # DRIVER FILE START

    # re_path(r'^driver-track-vehicles-list/$', TrackVehiclesListView.as_view(), name="driver_track_vehicle_list"),

    # Driver
    re_path(r'^driver-driver-list/$', DriverListView.as_view(), name="driver_driver_list"),
    re_path(r'^driver-driver-create/$', DriverViewSet.as_view({"post": "create"}), name="driver_driver_create"),
    re_path(r'^driver-driver-update/(?P<pk>[0-9]+)/$', DriverViewSet.as_view({"put": "update"}),
            name="driver_driver_update"),
    re_path(r'^driver-driver-partial-update/(?P<pk>[0-9]+)/$', DriverViewSet.as_view({"patch": "partial_update"}),
            name="driver_driver_partial_update"),
    re_path(r'^driver-fms-partial-update/(?P<pk>[0-9]+)/$', DriverViewSet.as_view({"patch": "fms_partial_update"}),
            name="driver_driver_fms_partial_update"),
    re_path(r'^driver-driver-retrieve/(?P<pk>[0-9]+)/$', DriverViewSet.as_view({"get": "retrieve"}),
            name="driver_driver_retrieve"),
    re_path(r'^driver-driver-soft-destroy/(?P<pk>[0-9]+)/$', DriverViewSet.as_view({"patch": "soft_destroy"}),
            name="driver_driver_soft_destroy"),

    # Driver App User

    re_path(r'^driver-driver-app-user-create/$', DriverAppUserViewSet.as_view({"post": "create"}),
            name="driver_driver_app_user_create"),
    re_path(r'^driver-driver-app-user-update/(?P<pk>[0-9]+)/$', DriverAppUserViewSet.as_view({"put": "update"}),
            name="driver_driver_app_user_update"),
    re_path(r'^driver-driver-app-user-partial-update/(?P<pk>[0-9]+)/$',
            DriverAppUserViewSet.as_view({"patch": "partial_update"}), name="driver_driver_app_user_partial_update"),
    re_path(r'^driver-driver-app-user-retrieve/(?P<pk>[0-9]+)/$', DriverAppUserViewSet.as_view({"get": "retrieve"}),
            name="driver_driver_app_user_retrieve"),

    # GPS Log New

    re_path(r'^driver-gps-log-new-create/$', GPSLogNewViewSet.as_view({"post": "create"}),
            name="driver_gps_log_new_create"),
    re_path(r'^driver-gps-log-new-update/(?P<pk>[0-9]+)/$', GPSLogNewViewSet.as_view({"put": "update"}),
            name="driver_gps_log_new_update"),
    re_path(r'^driver-gps-log-new-partial-update/(?P<pk>[0-9]+)/$',
            GPSLogNewViewSet.as_view({"patch": "partial_update"}), name="driver_gps_log_new_partial_update"),
    re_path(r'^driver-gps-log-new-retrieve/(?P<pk>[0-9]+)/$', GPSLogNewViewSet.as_view({"get": "retrieve"}),
            name="driver_gps_log_new_retrieve"),

    # OTP

    re_path(r'^driver-otp-create/$', OTPViewSet.as_view({"post": "create"}), name="driver_otp_create"),
    re_path(r'^driver-otp-update/(?P<pk>[0-9]+)/$', OTPViewSet.as_view({"put": "update"}), name="driver_otp_update"),
    re_path(r'^driver-otp-partial-update/(?P<pk>[0-9]+)/$', OTPViewSet.as_view({"patch": "partial_update"}),
            name="driver_otp_partial_update"),
    re_path(r'^driver-otp-retrieve/(?P<pk>[0-9]+)/$', OTPViewSet.as_view({"get": "retrieve"}),
            name="driver_otp_retrieve"),

    # GPS Device
    re_path(r'^driver-gps-device-list/$', GPSDeviceListView.as_view(), name="driver_gps_device_list"),
    re_path(r'^driver-gps-device-provider-list/$', GPSDeviceProviderListView.as_view(),
            name="driver_gps_device_provider_list"),
    re_path(r'^driver-gps-device-create/$', GPSDeviceViewSet.as_view({"post": "create"}),
            name="driver_gps_device_create"),
    re_path(r'^driver-gps-device-update/(?P<pk>[0-9]+)/$', GPSDeviceViewSet.as_view({"put": "update"}),
            name="driver_gps_device_update"),
    re_path(r'^driver-gps-device-partial-update/(?P<pk>[0-9]+)/$',
            GPSDeviceViewSet.as_view({"patch": "partial_update"}), name="driver_gps_device_partial_update"),
    re_path(r'^driver-gps-device-retrieve/(?P<pk>[0-9]+)/$', GPSDeviceViewSet.as_view({"get": "retrieve"}),
            name="driver_gps_device_retrieve"),

    # GPS Device Log

    re_path(r'^driver-gps-device-log-create/$', GPSDeviceLogViewSet.as_view({"post": "create"}),
            name="driver_gps_device_log_create"),
    re_path(r'^driver-gps-device-log-update/(?P<pk>[0-9]+)/$', GPSDeviceLogViewSet.as_view({"put": "update"}),
            name="driver_gps_device_log_update"),
    re_path(r'^driver-gps-device-log-partial-update/(?P<pk>[0-9]+)/$',
            GPSDeviceLogViewSet.as_view({"patch": "partial_update"}), name="driver_gps_device_log_partial_update"),
    re_path(r'^driver-gps-device-log-retrieve/(?P<pk>[0-9]+)/$', GPSDeviceLogViewSet.as_view({"get": "retrieve"}),
            name="driver_gps_device_log_retrieve"),

    # Tracknovate GPS Device

    re_path(r'^driver-tracknovate-gps-device-create/$', TracknovateGPSDeviceViewSet.as_view({"post": "create"}),
            name="driver_tracknovate_gps_device_create"),
    re_path(r'^driver-tracknovate-gps-device-update/(?P<pk>[0-9]+)/$',
            TracknovateGPSDeviceViewSet.as_view({"put": "update"}), name="driver_tracknovate_gps_device_update"),
    re_path(r'^driver-tracknovate-gps-device-partial-update/(?P<pk>[0-9]+)/$',
            TracknovateGPSDeviceViewSet.as_view({"patch": "partial_update"}),
            name="driver_tracknovate_gps_device_partial_update"),
    re_path(r'^driver-tracknovate-gps-device-retrieve/(?P<pk>[0-9]+)/$',
            TracknovateGPSDeviceViewSet.as_view({"get": "retrieve"}), name="driver_tracknovate_gps_device_retrieve"),

    # Tracknovate GPS Device Log

    re_path(r'^driver-tracknovate-gps-device-log-create/$', TracknovateGPSDeviceLogViewSet.as_view({"post": "create"}),
            name="driver_tracknovate_gps_device_log_create"),
    re_path(r'^driver-tracknovate-gps-device-log-update/(?P<pk>[0-9]+)/$',
            TracknovateGPSDeviceLogViewSet.as_view({"put": "update"}), name="driver_tracknovate_gps_device_log_update"),
    re_path(r'^driver-tracknovate-gps-device-log-partial-update/(?P<pk>[0-9]+)/$',
            TracknovateGPSDeviceLogViewSet.as_view({"patch": "partial_update"}),
            name="driver_tracknovate_gps_device_log_partial_update"),
    re_path(r'^driver-tracknovate-gps-device-log-retrieve/(?P<pk>[0-9]+)/$',
            TracknovateGPSDeviceLogViewSet.as_view({"get": "retrieve"}),
            name="driver_tracknovate_gps_device_log_retrieve"),

    # Waytracker GPS Device

    re_path(r'^driver-waytracker-gps-device-create/$', WaytrackerGPSDeviceViewSet.as_view({"post": "create"}),
            name="driver_waytracker_gps_device_create"),
    re_path(r'^driver-waytracker-gps-device-update/(?P<pk>[0-9]+)/$',
            WaytrackerGPSDeviceViewSet.as_view({"put": "update"}), name="driver_waytracker_gps_device_update"),
    re_path(r'^driver-waytracker-gps-device-partial-update/(?P<pk>[0-9]+)/$',
            WaytrackerGPSDeviceViewSet.as_view({"patch": "partial_update"}),
            name="driver_waytracker_gps_device_partial_update"),
    re_path(r'^driver-waytracker-gps-device-retrieve/(?P<pk>[0-9]+)/$',
            WaytrackerGPSDeviceViewSet.as_view({"get": "retrieve"}), name="driver_waytracker_gps_device_retrieve"),

    # Waytracker GPS Device Log

    re_path(r'^driver-waytracker-gps-device-log-create/$', WaytrackerGPSDeviceLogViewSet.as_view({"post": "create"}),
            name="driver_waytracker_gps_device_log_create"),
    re_path(r'^driver-waytracker-gps-device-log-update/(?P<pk>[0-9]+)/$',
            WaytrackerGPSDeviceLogViewSet.as_view({"put": "update"}), name="driver_waytracker_gps_device_log_update"),
    re_path(r'^driver-waytracker-gps-device-log-partial-update/(?P<pk>[0-9]+)/$',
            WaytrackerGPSDeviceLogViewSet.as_view({"patch": "partial_update"}),
            name="driver_waytracker_gps_device_log_partial_update"),
    re_path(r'^driver-waytracker-gps-device-log-retrieve/(?P<pk>[0-9]+)/$',
            WaytrackerGPSDeviceLogViewSet.as_view({"get": "retrieve"}),
            name="driver_waytracker_gps_device_log_retrieve"),

    # Tempo Go GPS Device

    re_path(r'^driver-tempo-go-gps-device-create/$', TempoGoGPSDeviceViewSet.as_view({"post": "create"}),
            name="driver_tempo_go_gps_device_create"),
    re_path(r'^driver-tempo-go-gps-device-update/(?P<pk>[0-9]+)/$', TempoGoGPSDeviceViewSet.as_view({"put": "update"}),
            name="driver_tempo_go_gps_device_update"),
    re_path(r'^driver-tempo-go-gps-device-partial-update/(?P<pk>[0-9]+)/$',
            TempoGoGPSDeviceViewSet.as_view({"patch": "partial_update"}),
            name="driver_tempo_go_gps_device_partial_update"),
    re_path(r'^driver-tempo-go-gps-device-retrieve/(?P<pk>[0-9]+)/$',
            TempoGoGPSDeviceViewSet.as_view({"get": "retrieve"}), name="driver_tempo_go_gps_device_retrieve"),

    # Tempo Go GPS Device Log

    re_path(r'^driver-tempo-go-gps-device-log-create/$', TempoGoGPSDeviceLogViewSet.as_view({"post": "create"}),
            name="driver_tempo_go_gps_device_log_create"),
    re_path(r'^driver-tempo-go-gps-device-log-update/(?P<pk>[0-9]+)/$',
            TempoGoGPSDeviceLogViewSet.as_view({"put": "update"}), name="driver_tempo_go_gps_device_log_update"),
    re_path(r'^driver-tempo-go-gps-device-log-partial-update/(?P<pk>[0-9]+)/$',
            TempoGoGPSDeviceLogViewSet.as_view({"patch": "partial_update"}),
            name="driver_tempo_go_gps_device_log_partial_update"),
    re_path(r'^driver-tempo-go-gps-device-log-retrieve/(?P<pk>[0-9]+)/$',
            TempoGoGPSDeviceLogViewSet.as_view({"get": "retrieve"}), name="driver_tempo_go_gps_device_log_retrieve"),

    # Secu GPS Device

    re_path(r'^driver-secu-gps-device-create/$', SecuGPSDeviceViewSet.as_view({"post": "create"}),
            name="driver_secu_gps_device_create"),
    re_path(r'^driver-secu-gps-device-update/(?P<pk>[0-9]+)/$', SecuGPSDeviceViewSet.as_view({"put": "update"}),
            name="driver_secu_gps_device_update"),
    re_path(r'^driver-secu-gps-device-partial-update/(?P<pk>[0-9]+)/$',
            SecuGPSDeviceViewSet.as_view({"patch": "partial_update"}), name="driver_secu_gps_device_partial_update"),
    re_path(r'^driver-secu-gps-device-retrieve/(?P<pk>[0-9]+)/$', SecuGPSDeviceViewSet.as_view({"get": "retrieve"}),
            name="driver_secu_gps_device_retrieve"),

    # Secu GPS Device Log

    re_path(r'^driver-secu-gps-device-log-create/$', SecuGPSDeviceLogViewSet.as_view({"post": "create"}),
            name="driver_secu_gps_device_log_create"),
    re_path(r'^driver-secu-gps-device-log-update/(?P<pk>[0-9]+)/$', SecuGPSDeviceLogViewSet.as_view({"put": "update"}),
            name="driver_secu_gps_device_log_update"),
    re_path(r'^driver-secu-gps-device-log-partial-update/(?P<pk>[0-9]+)/$',
            SecuGPSDeviceLogViewSet.as_view({"patch": "partial_update"}),
            name="driver_secu_gps_device_log_partial_update"),
    re_path(r'^driver-secu-gps-device-log-retrieve/(?P<pk>[0-9]+)/$',
            SecuGPSDeviceLogViewSet.as_view({"get": "retrieve"}), name="driver_secu_gps_device_log_retrieve"),

    # Mahindra GPS Device

    re_path(r'^driver-mahindra-gps-device-create/$', MahindraGPSDeviceViewSet.as_view({"post": "create"}),
            name="driver_mahindra_gps_device_create"),
    re_path(r'^driver-mahindra-gps-device-update/(?P<pk>[0-9]+)/$',
            MahindraGPSDeviceViewSet.as_view({"put": "update"}), name="driver_mahindra_gps_device_update"),
    re_path(r'^driver-mahindra-gps-device-partial-update/(?P<pk>[0-9]+)/$',
            MahindraGPSDeviceViewSet.as_view({"patch": "partial_update"}),
            name="driver_mahindra_gps_device_partial_update"),
    re_path(r'^driver-mahindra-gps-device-retrieve/(?P<pk>[0-9]+)/$',
            MahindraGPSDeviceViewSet.as_view({"get": "retrieve"}), name="driver_mahindra_gps_device_retrieve"),

    # Mahindra GPS Device Log

    re_path(r'^driver-mahindra-gps-device-log-create/$', MahindraGPSDeviceLogViewSet.as_view({"post": "create"}),
            name="driver_mahindra_gps_device_log_create"),
    re_path(r'^driver-mahindra-gps-device-log-update/(?P<pk>[0-9]+)/$',
            MahindraGPSDeviceLogViewSet.as_view({"put": "update"}), name="driver_mahindra_gps_device_log_update"),
    re_path(r'^driver-mahindra-gps-device-log-partial-update/(?P<pk>[0-9]+)/$',
            MahindraGPSDeviceLogViewSet.as_view({"patch": "partial_update"}),
            name="driver_mahindra_gps_device_log_partial_update"),
    re_path(r'^driver-mahindra-gps-device-log-retrieve/(?P<pk>[0-9]+)/$',
            MahindraGPSDeviceLogViewSet.as_view({"get": "retrieve"}), name="driver_mahindra_gps_device_log_retrieve"),

    # DRIVER FILE END

    # EMPLOYEE FILE START

    # Designation

    re_path(r'^employee-designation-create/$', DesignationViewSet.as_view({"post": "create"}),
            name="employee_designation_create"),
    re_path(r'^employee-designation-update/(?P<pk>[0-9]+)/$', DesignationViewSet.as_view({"put": "update"}),
            name="employee_designation_update"),
    re_path(r'^employee-designation-partial-update/(?P<pk>[0-9]+)/$',
            DesignationViewSet.as_view({"patch": "partial_update"}), name="employee_designation_partial_update"),
    re_path(r'^employee-designation-retrieve/(?P<pk>[0-9]+)/$', DesignationViewSet.as_view({"get": "retrieve"}),
            name="employee_designation_retrieve"),

    # Department

    re_path(r'^employee-department-create/$', DepartmentViewSet.as_view({"post": "create"}),
            name="employee_department_create"),
    re_path(r'^employee-department-update/(?P<pk>[0-9]+)/$', DepartmentViewSet.as_view({"put": "update"}),
            name="employee_department_update"),
    re_path(r'^employee-department-partial-update/(?P<pk>[0-9]+)/$',
            DepartmentViewSet.as_view({"patch": "partial_update"}), name="employee_department_partial_update"),
    re_path(r'^employee-department-retrieve/(?P<pk>[0-9]+)/$', DepartmentViewSet.as_view({"get": "retrieve"}),
            name="employee_department_retrieve"),

    # Fitness

    re_path(r'^employee-fitness-detail-create/$', FitnessViewSet.as_view({"post": "create"}),
            name="employee_fitness_detail_create"),
    re_path(r'^employee-fitness-detail-update/(?P<pk>[0-9]+)/$', FitnessViewSet.as_view({"put": "update"}),
            name="employee_fitness_detail_update"),
    re_path(r'^employee-fitness-detail-partial-update/(?P<pk>[0-9]+)/$',
            FitnessViewSet.as_view({"patch": "partial_update"}), name="employee_fitness_detail_partial_update"),
    re_path(r'^employee-fitness-detail-retrieve/(?P<pk>[0-9]+)/$', FitnessViewSet.as_view({"get": "retrieve"}),
            name="employee_fitness_detail_retrieve"),

    # Past Employment

    re_path(r'^employee-past-employment-create/$', PastEmploymentViewSet.as_view({"post": "create"}),
            name="employee_past_employment_create"),
    re_path(r'^employee-past-employment-update/(?P<pk>[0-9]+)/$', PastEmploymentViewSet.as_view({"put": "update"}),
            name="employee_past_employment_update"),
    re_path(r'^employee-past-employment-partial-update/(?P<pk>[0-9]+)/$',
            PastEmploymentViewSet.as_view({"patch": "partial_update"}), name="employee_past_employment_partial_update"),
    re_path(r'^employee-past-employment-retrieve/(?P<pk>[0-9]+)/$',
            PastEmploymentViewSet.as_view({"get": "retrieve"}), name="employee_past_employment_retrieve"),

    # Permanent Address

    re_path(r'^employee-permanent-address-create/$', PermanentAddressViewSet.as_view({"post": "create"}),
            name="employee_permanent_address_create"),
    re_path(r'^employee-permanent-address-update/(?P<pk>[0-9]+)/$', PermanentAddressViewSet.as_view({"put": "update"}),
            name="employee_permanent_address_update"),
    re_path(r'^employee-permanent-address-partial-update/(?P<pk>[0-9]+)/$',
            PermanentAddressViewSet.as_view({"patch": "partial_update"}),
            name="employee_permanent_address_partial_update"),
    re_path(r'^employee-permanent-address-retrieve/(?P<pk>[0-9]+)/$',
            PermanentAddressViewSet.as_view({"get": "retrieve"}), name="employee_permanent_address_retrieve"),

    # Referral

    re_path(r'^employee-referral-create/$', ReferralViewSet.as_view({"post": "create"}),
            name="employee_referral_create"),
    re_path(r'^employee-referral-update/(?P<pk>[0-9]+)/$', ReferralViewSet.as_view({"put": "update"}),
            name="employee_referral_update"),
    re_path(r'^employee-referral-partial-update/(?P<pk>[0-9]+)/$',
            ReferralViewSet.as_view({"patch": "partial_update"}), name="employee_referral_partial_update"),
    re_path(r'^employee-referral-retrieve/(?P<pk>[0-9]+)/$', ReferralViewSet.as_view({"get": "retrieve"}),
            name="employee_referral_retrieve"),

    # Employment Agency

    re_path(r'^employee-employment-agency-create/$', EmploymentAgencyViewSet.as_view({"post": "create"}),
            name="employee_employment_agency_create"),
    re_path(r'^employee-employment-agency-update/(?P<pk>[0-9]+)/$', EmploymentAgencyViewSet.as_view({"put": "update"}),
            name="employee_employment_agency_update"),
    re_path(r'^employee-employment-agency-partial-update/(?P<pk>[0-9]+)/$',
            EmploymentAgencyViewSet.as_view({"patch": "partial_update"}),
            name="employee_employment_agency_partial_update"),
    re_path(r'^employee-employment-agency-retrieve/(?P<pk>[0-9]+)/$',
            EmploymentAgencyViewSet.as_view({"get": "retrieve"}), name="employee_employment_agency_retrieve"),

    # Employee
    re_path(r'^employee-list/$', EmployeeListView.as_view(), name="employee_employee_list"),
    re_path(r'^employee-employee-create/$', EmployeeViewSet.as_view({"post": "create"}),
            name="employee_employee_create"),
    re_path(r'^employee-employee-update/(?P<pk>[0-9]+)/$', EmployeeViewSet.as_view({"put": "update"}),
            name="employee_employee_update"),
    re_path(r'^employee-employee-partial-update/(?P<pk>[0-9]+)/$',
            EmployeeViewSet.as_view({"patch": "partial_update"}), name="employee_employee_partial_update"),
    re_path(r'^employee-employee-retrieve/(?P<pk>[0-9]+)/$', EmployeeViewSet.as_view({"get": "retrieve"}),
            name="employee_employee_retrieve"),

    # Current Employee Details

    re_path(r'^employee-current-employment-details-create/$',
            CurrentEmploymentDetailsViewSet.as_view({"post": "create"}),
            name="employee_current_employment_details_create"),
    re_path(r'^employee-current-employment-details-update/(?P<pk>[0-9]+)/$',
            CurrentEmploymentDetailsViewSet.as_view({"put": "update"}),
            name="employee_current_employment_details_update"),
    re_path(r'^employee-current-employment-details-partial-update/(?P<pk>[0-9]+)/$',
            CurrentEmploymentDetailsViewSet.as_view({"patch": "partial_update"}),
            name="employee_current_employment_details_partial_update"),
    re_path(r'^employee-current-employment-details-retrieve/(?P<pk>[0-9]+)/$',
            CurrentEmploymentDetailsViewSet.as_view({"get": "retrieve"}),
            name="employee_current_employment_details_retrieve"),

    # Education Degree

    re_path(r'^employee-education-degree-create/$', EducationalDegreeViewSet.as_view({"post": "create"}),
            name="employee_education_degree_create"),
    re_path(r'^employee-education-degree-update/(?P<pk>[0-9]+)/$', EducationalDegreeViewSet.as_view({"put": "update"}),
            name="employee_education_degree_update"),
    re_path(r'^employee-education-degree-partial-update/(?P<pk>[0-9]+)/$',
            EducationalDegreeViewSet.as_view({"patch": "partial_update"}),
            name="employee_education_degree_partial_update"),
    re_path(r'^employee-education-degree-retrieve/(?P<pk>[0-9]+)/$',
            EducationalDegreeViewSet.as_view({"get": "retrieve"}), name="employee_education_degree_retrieve"),

    # Certification Course

    re_path(r'^employee-certification-course-create/$', CertificationCourseViewSet.as_view({"post": "create"}),
            name="employee_certification_course_create"),
    re_path(r'^employee-certification-course-update/(?P<pk>[0-9]+)/$',
            CertificationCourseViewSet.as_view({"put": "update"}), name="employee_certification_course_update"),
    re_path(r'^employee-certification-course-partial-update/(?P<pk>[0-9]+)/$',
            CertificationCourseViewSet.as_view({"patch": "partial_update"}),
            name="employee_certification_course_partial_update"),
    re_path(r'^employee-certification-course-retrieve/(?P<pk>[0-9]+)/$',
            CertificationCourseViewSet.as_view({"get": "retrieve"}), name="employee_certification_course_retrieve"),

    # Skill set

    re_path(r'^employee-skill-set-create/$', SkillSetViewSet.as_view({"post": "create"}),
            name="employee_skill_set_create"),
    re_path(r'^employee-skill-set-update/(?P<pk>[0-9]+)/$', SkillSetViewSet.as_view({"put": "update"}),
            name="employee_skill_set_update"),
    re_path(r'^employee-skill-set-partial-update/(?P<pk>[0-9]+)/$',
            SkillSetViewSet.as_view({"patch": "partial_update"}), name="employee_skill_set_partial_update"),
    re_path(r'^employee-skill-set-retrieve/(?P<pk>[0-9]+)/$', SkillSetViewSet.as_view({"get": "retrieve"}),
            name="employee_skill_set_retrieve"),

    # Nominee

    re_path(r'^employee-nominee-create/$', NomineeViewSet.as_view({"post": "create"}), name="employee_nominee_create"),
    re_path(r'^employee-nominee-update/(?P<pk>[0-9]+)/$', NomineeViewSet.as_view({"put": "update"}),
            name="employee_nominee_update"),
    re_path(r'^employee-nominee-partial-update/(?P<pk>[0-9]+)/$',
            NomineeViewSet.as_view({"patch": "partial_update"}), name="employee_nominee_partial_update"),
    re_path(r'^employee-nominee-retrieve/(?P<pk>[0-9]+)/$', NomineeViewSet.as_view({"get": "retrieve"}),
            name="employee_nominee_retrieve"),

    # Leave Record

    re_path(r'^employee-leave-record-create/$', LeaveRecordViewSet.as_view({"post": "create"}),
            name="employee_leave_record_create"),
    re_path(r'^employee-leave-record-update/(?P<pk>[0-9]+)/$', LeaveRecordViewSet.as_view({"put": "update"}),
            name="employee_leave_record_update"),
    re_path(r'^employee-leave-record-partial-update/(?P<pk>[0-9]+)/$',
            LeaveRecordViewSet.as_view({"patch": "partial_update"}), name="employee_leave_record_partial_update"),
    re_path(r'^employee-leave-record-retrieve/(?P<pk>[0-9]+)/$', LeaveRecordViewSet.as_view({"get": "retrieve"}),
            name="employee_leave_record_retrieve"),

    # Salary

    re_path(r'^employee-salary-create/$', SalaryViewSet.as_view({"post": "create"}), name="employee_salary_create"),
    re_path(r'^employee-salary-update/(?P<pk>[0-9]+)/$', SalaryViewSet.as_view({"put": "update"}),
            name="employee_salary_update"),
    re_path(r'^employee-salary-partial-update/(?P<pk>[0-9]+)/$',
            SalaryViewSet.as_view({"patch": "partial_update"}), name="employee_salary_partial_update"),
    re_path(r'^employee-salary-retrieve/(?P<pk>[0-9]+)/$', SalaryViewSet.as_view({"get": "retrieve"}),
            name="employee_salary_retrieve"),

    # Task

    re_path(r'^employee-task-create/$', TaskViewSet.as_view({"post": "create"}), name="employee_task_create"),
    re_path(r'^employee-task-update/(?P<pk>[0-9]+)/$', TaskViewSet.as_view({"put": "update"}),
            name="employee_task_update"),
    re_path(r'^employee-task-partial-update/(?P<pk>[0-9]+)/$',
            TaskViewSet.as_view({"patch": "partial_update"}), name="employee_task_partial_update"),
    re_path(r'^employee-task-retrieve/(?P<pk>[0-9]+)/$', TaskViewSet.as_view({"get": "retrieve"}),
            name="employee_task_retrieve"),

    # Task Email

    re_path(r'^employee-task-email-create/$', TaskEmailViewSet.as_view({"post": "create"}),
            name="employee_task_email_create"),
    re_path(r'^employee-task-email-update/(?P<pk>[0-9]+)/$', TaskEmailViewSet.as_view({"put": "update"}),
            name="employee_task_email_update"),
    re_path(r'^employee-task-email-partial-update/(?P<pk>[0-9]+)/$',
            TaskEmailViewSet.as_view({"patch": "partial_update"}), name="employee_task_email_partial_update"),
    re_path(r'^employee-task-email-retrieve/(?P<pk>[0-9]+)/$', TaskEmailViewSet.as_view({"get": "retrieve"}),
            name="employee_task_email_retrieve"),

    # EMPLOYESS FILE END

    # File UPLOAD File Starts

    # PODFile
    re_path(r'^file-upload-pod-history/$', PODFileCreatePageView.as_view(), name='file_upload_pod_file_create'),
    re_path(r'^file-upload-pod-file-list/$', PODFileListView.as_view(), name='file_upload_pod_file_list'),
    re_path(r'^file-upload-pod-file-create/$', PODFileViewSet.as_view({"post": "create"}),
            name="file_upload_pod_file_create"),
    re_path(r'^file-upload-pod-file-web-upload/$', PODFileViewSet.as_view({"post": "web_upload"}),
            name="file_upload_pod_file_web_upload"),
    re_path(r'^file-upload-pod-file-update/(?P<pk>[0-9]+)/$', PODFileViewSet.as_view({"put": "update"}),
            name="file_upload_pod_file_update"),
    re_path(r'^file-upload-pod-file-partial-update/(?P<pk>[0-9]+)/$',
            PODFileViewSet.as_view({"patch": "partial_update"}), name="file_upload_pod_file_partial_update"),
    re_path(r'^fileupload-pod-approve/$',
            PODFileViewSet.as_view({"patch": "approve"}), name="fileupload_pod_accept"),
    re_path(r'^fileupload-pod-reject/$',
            PODFileViewSet.as_view({"patch": "reject"}), name="fileupload_pod_reject"),
    re_path(r'^fileupload-pod-resubmit/$',
            PODFileViewSet.as_view({"patch": "resubmit"}), name="fileupload_pod_resubmit"),
    re_path(r'^file-upload-pod-file-retrieve/(?P<pk>[0-9]+)/$', PODFileViewSet.as_view({"get": "retrieve"}),
            name="file_upload_pod_file_retrieve"),

    # Vehicle File
    re_path(r'^file-upload-vehicle-file-list/$', VehicleFileListView.as_view(), name='file_upload_vehicle_file_list'),
    re_path(r'^file-upload-vehicle-file-create/$', VehicleFileViewSet.as_view({"post": "create"}),
            name="file_upload_vehicle_file_create"),
    re_path(r'^file-upload-vehicle-file-update/(?P<pk>[0-9]+)/$', VehicleFileViewSet.as_view({"put": "update"}),
            name="file_upload_vehicle_file_update"),
    re_path(r'^file-upload-vehicle-file-partial-update/(?P<pk>[0-9]+)/$',
            VehicleFileViewSet.as_view({"patch": "partial_update"}), name="file_upload_vehicle_file_partial_update"),
    re_path(r'^file-upload-vehicle-file-retrieve/(?P<pk>[0-9]+)/$', VehicleFileViewSet.as_view({"get": "retrieve"}),
            name="file_upload_vehicle_file_retrieve"),

    # Owner File
    re_path(r'^file-upload-owner-file-list/$', OwnerFileListView.as_view(), name='file_upload_owner_file_list'),
    re_path(r'^file-upload-owner-file-create/$', OwnerFileViewSet.as_view({"post": "create"}),
            name="file_upload_owner_file_create"),
    re_path(r'^file-upload-owner-file-update/(?P<pk>[0-9]+)/$', OwnerFileViewSet.as_view({"put": "update"}),
            name="file_upload_owner_file_update"),
    re_path(r'^file-upload-owner-file-partial-update/(?P<pk>[0-9]+)/$',
            OwnerFileViewSet.as_view({"patch": "partial_update"}), name="file_upload_owner_file_partial_update"),
    re_path(r'^file-upload-owner-file-retrieve/(?P<pk>[0-9]+)/$', OwnerFileViewSet.as_view({"get": "retrieve"}),
            name="file_upload_owner_file_retrieve"),

    # Driver File
    re_path(r'^file-upload-driver-file-list/$', DriverFileListView.as_view(), name='file_upload_driver_file_list'),
    re_path(r'^file-upload-driver-file-create/$', DriverFileViewSet.as_view({"post": "create"}),
            name="file_upload_driver_file_create"),
    re_path(r'^file-upload-driver-file-update/(?P<pk>[0-9]+)/$', DriverFileViewSet.as_view({"put": "update"}),
            name="file_upload_driver_file_update"),
    re_path(r'^file-upload-driver-file-partial-update/(?P<pk>[0-9]+)/$',
            DriverFileViewSet.as_view({"patch": "partial_update"}), name="file_upload_driver_file_partial_update"),
    re_path(r'^file-upload-driver-file-retrieve/(?P<pk>[0-9]+)/$', DriverFileViewSet.as_view({"get": "retrieve"}),
            name="file_upload_driver_file_retrieve"),

    # Cheque File
    re_path(r'^file-upload-cheque-file-list/$', ChequeFileListView.as_view(), name='file_upload_cheque_file_list'),
    re_path(r'^file-upload-cheque-file-create/$', ChequeFileViewSet.as_view({"post": "create"}),
            name="file_upload_cheque_file_create"),
    re_path(r'^file-upload-cheque-file-update/(?P<pk>[0-9]+)/$', ChequeFileViewSet.as_view({"put": "update"}),
            name="file_upload_cheque_file_update"),
    re_path(r'^file-upload-cheque-file-partial-update/(?P<pk>[0-9]+)/$',
            ChequeFileViewSet.as_view({"patch": "partial_update"}), name="file_upload_cheque_file_partial_update"),
    re_path(r'^file-upload-cheque-file-retrieve/(?P<pk>[0-9]+)/$', ChequeFileViewSet.as_view({"get": "retrieve"}),
            name="file_upload_cheque_file_retrieve"),

    # Invoice Receipt File
    re_path(r'^file-upload-invoice-receipt-file-list/$', InvoiceReceiptFileListView.as_view(),
            name='file_upload_invoice_receipt_file_list'),
    re_path(r'^file-upload-invoice-receipt-file-create/$', InvoiceReceiptFileViewSet.as_view({"post": "create"}),
            name="file_upload_invoice_receipt_file_create"),
    re_path(r'^file-upload-invoice-receipt-file-update/(?P<pk>[0-9]+)/$',
            InvoiceReceiptFileViewSet.as_view({"put": "update"}), name="file_upload_invoice_receipt_file_update"),
    re_path(r'^file-upload-invoice-receipt-file-partial-update/(?P<pk>[0-9]+)/$',
            InvoiceReceiptFileViewSet.as_view({"patch": "partial_update"}),
            name="file_upload_invoice_receipt_file_partial_update"),
    re_path(r'^file-upload-invoice-receipt-file-retrieve/(?P<pk>[0-9]+)/$',
            InvoiceReceiptFileViewSet.as_view({"get": "retrieve"}), name="file_upload_invoice_receipt_file_retrieve"),

    # FILE UPLOAD END

    # SUPPLIER FILE

    # Service
    re_path(r'^supplier-service-list/$', ServiceListView.as_view(),
            name='supplier_service_list'),
    re_path(r'^supplier-service-create/$', ServiceViewSet.as_view({"post": "create"}), name='supplier_service_create'),
    re_path(r'^supplier-service-update/(?P<pk>[0-9]+)/$', ServiceViewSet.as_view({"put": "update"}),
            name='supplier_service_update'),
    re_path(r'^supplier-service-partial-update/(?P<pk>[0-9]+)/$', ServiceViewSet.as_view({"patch": "partial_update"}),
            name='supplier_service_partial_update'),
    re_path(r'^supplier-service-retrieve/(?P<pk>[0-9]+)/$', ServiceViewSet.as_view({"get": "retrieve"}),
            name='supplier_service_retrieve'),

    # Supplier
    re_path(r'^supplier-supplier-list/$', SupplierListView.as_view(),
            name='supplier_supplier_list'),
    re_path(r'^supplier-data-validation/$', SupplierViewSet.as_view({"post": "supplier_data_validation"}),
            name='supplier_data_validation'),
    re_path(r'^supplier-supplier-create/$', SupplierViewSet.as_view({"post": "create"}),
            name='supplier_supplier_create'),
    re_path(r'^supplier-supplier-update/(?P<pk>[0-9]+)/$', SupplierViewSet.as_view({"put": "update"}),
            name='supplier_supplier_update'),
    re_path(r'^supplier-supplier-partial-update/(?P<pk>[0-9]+)/$',
            SupplierViewSet.as_view({"patch": "partial_update"}), name='supplier_supplier_partial_update'),
    re_path(r'^supplier-supplier-retrieve/(?P<pk>[0-9]+)/$', SupplierViewSet.as_view({"get": "retrieve"}),
            name='supplier_supplier_retrieve'),

    # Contact Person

    re_path(r'^supplier-contact-person-list/$', ContactPersonListView.as_view(),
            name='supplier_contact_person_list'),
    re_path(r'^supplier-contact-person-create/$', ContactPersonViewSet.as_view({"post": "create"}),
            name='supplier_contact_person_create'),
    re_path(r'^supplier-contact-person-update/(?P<pk>[0-9]+)/$', ContactPersonViewSet.as_view({"put": "update"}),
            name='supplier_contact_person_update'),
    re_path(r'^supplier-contact-person-partial-update/(?P<pk>[0-9]+)/$',
            ContactPersonViewSet.as_view({"patch": "partial_update"}),
            name='supplier_contact_person_partial_update'),
    re_path(r'^supplier-contact-person-retrieve/(?P<pk>[0-9]+)/$', ContactPersonViewSet.as_view({"get": "retrieve"}),
            name='supplier_contact_person_retrieve'),

    # Supplier Driver
    re_path(r'^supplier-supplier-driver-list/$', SupplierDriverListView.as_view(),
            name='supplier_supplier_driver_list'),
    re_path(r'^supplier-supplier-driver-create/$', SupplierDriverViewSet.as_view({"post": "create"}),
            name='supplier_supplier_driver_create'),
    re_path(r'^supplier-driver-data-validation/$', SupplierDriverViewSet.as_view({"post": "driver_data_validation"}),
            name='supplier_driver_data_validation'),
    re_path(r'^supplier-supplier-driver-update/(?P<pk>[0-9]+)/$', SupplierDriverViewSet.as_view({"put": "update"}),
            name='supplier_supplier_driver_update'),
    re_path(r'^supplier-driver-fms-partial-update/(?P<pk>[0-9]+)/$', SupplierDriverViewSet.as_view({"patch": "fms_partial_update"}),
            name="supplier_driver_fms_partial_update"),
    re_path(r'^supplier-supplier-driver-partial-update/(?P<pk>[0-9]+)/$',
            SupplierDriverViewSet.as_view({"patch": "partial_update"}), name='supplier_supplier_driver_partial_update'),
    re_path(r'^supplier-supplier-driver-retrieve/(?P<pk>[0-9]+)/$', SupplierDriverViewSet.as_view({"get": "retrieve"}),
            name='supplier_supplier_driver_retrieve'),

    # Supplier Driver Phone
    re_path(r'^supplier-supplier-driver-phone-list/$', SupplierDriverPhoneListView.as_view(),
            name='supplier_supplier_driver_phone_list'),
    re_path(r'^supplier-supplier-driver-phone-create/$', SupplierDriverPhoneViewSet.as_view({"post": "create"}),
            name='supplier_supplier_driver_phone_create'),
    re_path(r'^supplier-supplier-driver-phone-update/(?P<pk>[0-9]+)/$',
            SupplierDriverPhoneViewSet.as_view({"put": "update"}), name='supplier_supplier_driver_phone_update'),
    re_path(r'^supplier-supplier-driver-phone-partial-update/(?P<pk>[0-9]+)/$',
            SupplierDriverPhoneViewSet.as_view({"patch": "partial_update"}),
            name='supplier_supplier_driver_phone_partial_update'),
    re_path(r'^supplier-supplier-driver-phone-retrieve/(?P<pk>[0-9]+)/$',
            SupplierDriverPhoneViewSet.as_view({"get": "retrieve"}), name='supplier_supplier_driver_phone_retrieve'),

    # Vehicle body category
    re_path(r'^supplier-vehicle-body-category-list/$', VehicleBodyCategoryListView.as_view(),
            name='supplier_vehicle_body_category_list'),
    re_path(r'^supplier-vehicle-body-category-create/$', vehicle_body_category_create,
            name='supplier_vehicle_body_category_create'),
    re_path(r'^supplier-vehicle-body-category-update/(?P<pk>[0-9]+)/$', vehicle_body_category_update,
            name='supplier_vehicle_body_category_update'),
    re_path(r'^supplier-vehicle-body-category-partial-update/(?P<pk>[0-9]+)/$', vehicle_body_category_partial_update,
            name='supplier_vehicle_body_category_partial_update'),
    re_path(r'^supplier-vehicle-body-category-retrieve/(?P<pk>[0-9]+)/$', vehicle_body_category_retrieve,
            name='supplier_vehicle_body_category_retrieve'),

    # Vehicle category
    re_path(r'^supplier-vehicle-category-list/$', VehicleCategoryListView.as_view(),
            name='supplier_vehicle_category_list'),
    re_path(r'^supplier-vehicle-category-create/$', vehicle_category_create, name='supplier_vehicle_category_create'),
    re_path(r'^supplier-vehicle-category-update/(?P<pk>[0-9]+)/$', vehicle_category_update,
            name='supplier_vehicle_category_update'),
    re_path(r'^supplier-vehicle-category-partial-update/(?P<pk>[0-9]+)/$', vehicle_category_partial_update,
            name='supplier_vehicle_category_partial_update'),
    re_path(r'^supplier-vehicle-category-retrieve/(?P<pk>[0-9]+)/$', vehicle_category_retrieve,
            name='supplier_vehicle_category_retrieve'),

    # Vehicle
    re_path(r'^supplier-vehicle-list/$', VehicleListView.as_view(),
            name='supplier_vehicle_list'),
    re_path(r'^supplier-vehicle-create/$', vehicle_create, name='supplier_vehicle_create'),
    re_path(r'^supplier-vehicle-update/(?P<pk>[0-9]+)/$', vehicle_update, name='supplier_vehicle_update'),
    re_path(r'^supplier-fms-vehicle-partial-update/(?P<pk>[0-9]+)/$', VehicleViewSet.as_view({'patch':'fms_update'}), name='supplier_fms_vehicle_update'),
    re_path(r'^supplier-vehicle-partial-update/(?P<pk>[0-9]+)/$', vehicle_partial_update,
            name='supplier_vehicle_partial_update'),
    re_path(r'^supplier-vehicle-retrieve/(?P<pk>[0-9]+)/$', vehicle_retrieve, name='supplier_vehicle_retrieve'),

    # Driver Vehicle
    re_path(r'^supplier-driver-vehicle-list/$', DriverVehicleListView.as_view(),
            name='supplier_driver_vehicle_list'),
    re_path(r'^supplier-driver-vehicle-create/$', DriverVehicleViewSet.as_view({"post": "create"}),
            name='supplier_driver_vehicle_create'),
    re_path(r'^supplier-driver-vehicle-update/(?P<pk>[0-9]+)/$', DriverVehicleViewSet.as_view({"put": "update"}),
            name='supplier_driver_vehicle_update'),
    re_path(r'^supplier-driver-vehicle-partial-update/(?P<pk>[0-9]+)/$',
            DriverVehicleViewSet.as_view({"patch": "partial_update"}), name='supplier_driver_vehicle_partial_update'),
    re_path(r'^supplier-driver-vehicle-retrieve/(?P<pk>[0-9]+)/$', DriverVehicleViewSet.as_view({"get": "retrieve"}),
            name='supplier_driver_vehicle_retrieve'),

    # Vehicle Status
    re_path(r'^supplier-vehicle-status-list/$', VehicleStatusListView.as_view(),
            name='supplier_vehicle_status_list'),
    re_path(r'^supplier-vehicle-status-create/$', VehicleStatusViewSet.as_view({"post": "create"}),
            name='supplier_vehicle_status_create'),
    re_path(r'^supplier-vehicle-status-update/(?P<pk>[0-9]+)/$', VehicleStatusViewSet.as_view({"put": "update"}),
            name='supplier_vehicle_status_update'),
    re_path(r'^supplier-vehicle-status-partial-update/(?P<pk>[0-9]+)/$',
            VehicleStatusViewSet.as_view({"patch": "partial_update"}), name='supplier_vehicle_status_partial_update'),
    re_path(r'^supplier-vehicle-status-retrieve/(?P<pk>[0-9]+)/$', VehicleStatusViewSet.as_view({"get": "retrieve"}),
            name='supplier_vehicle_status_retrieve'),

    # Vehicle Insurer
    re_path(r'^supplier-vehicle-insurer-list/$', VehicleInsurerListView.as_view(),
            name='supplier_vehicle_insurer_list'),
    re_path(r'^supplier-vehicle-insurer-create/$', VehicleInsurerViewSet.as_view({"post": "create"}),
            name='supplier_vehicle_insurer_create'),
    re_path(r'^supplier-vehicle-insurer-update/(?P<pk>[0-9]+)/$', VehicleInsurerViewSet.as_view({"put": "update"}),
            name='supplier_vehicle_insurer_update'),
    re_path(r'^supplier-vehicle-insurer-partial-update/(?P<pk>[0-9]+)/$',
            VehicleInsurerViewSet.as_view({"patch": "partial_update"}), name='supplier_vehicle_insurer_partial_update'),
    re_path(r'^supplier-vehicle-insurer-retrieve/(?P<pk>[0-9]+)/$', VehicleInsurerViewSet.as_view({"get": "retrieve"}),
            name='supplier_vehicle_insurer_retrieve'),

    # Vehicle Insurance
    re_path(r'^supplier-vehicle-insurance-list/$', VehicleInsuranceListView.as_view(),
            name='supplier_vehicle_insurance_list'),
    re_path(r'^supplier-vehicle-insurance-create/$', VehicleInsuranceViewSet.as_view({"post": "create"}),
            name='supplier_vehicle_insurance_create'),
    re_path(r'^supplier-vehicle-insurance-update/(?P<pk>[0-9]+)/$', VehicleInsuranceViewSet.as_view({"put": "update"}),
            name='supplier_vehicle_insurance_update'),
    re_path(r'^supplier-vehicle-insurance-partial-update/(?P<pk>[0-9]+)/$',
            VehicleInsuranceViewSet.as_view({"patch": "partial_update"}),
            name='supplier_vehicle_insurance_partial_update'),
    re_path(r'^supplier-vehicle-insurance-retrieve/(?P<pk>[0-9]+)/$',
            VehicleInsuranceViewSet.as_view({"get": "retrieve"}), name="supplier_vehicle_insurance_retrieve"),

    # Vehicle PUC
    re_path(r'^supplier-vehicle-puc-list/$', VehiclePUCListView.as_view(),
            name='supplier_vehicle_puc_list'),
    re_path(r'^supplier-vehicle-puc-create/$', VehiclePUCViewSet.as_view({"post": "create"}),
            name='supplier_vehicle_puc_create'),
    re_path(r'^supplier-vehicle-puc-update/(?P<pk>[0-9]+)/$', VehiclePUCViewSet.as_view({"put": "update"}),
            name='supplier_vehicle_puc_update'),
    re_path(r'^supplier-vehicle-puc-partial-update/(?P<pk>[0-9]+)/$',
            VehiclePUCViewSet.as_view({"patch": "partial_update"}), name='supplier_vehicle_puc_partial_update'),
    re_path(r'^supplier-vehicle-puc-retrieve/(?P<pk>[0-9]+)/$', VehiclePUCViewSet.as_view({"get": "retrieve"}),
            name='supplier_vehicle_puc_retrieve'),

    # Vehicle Fitness
    re_path(r'^supplier-vehicle-fitness-list/$', VehicleFitnessListView.as_view(),
            name='supplier_vehicle_fitness_list'),
    re_path(r'^supplier-vehicle-fitness-create/$', VehicleFitnessViewSet.as_view({"post": "create"}),
            name='supplier_vehicle_fitness_create'),
    re_path(r'^supplier-vehicle-fitness-update/(?P<pk>[0-9]+)/$', VehicleFitnessViewSet.as_view({"put": "update"}),
            name='supplier_vehicle_fitness_update'),
    re_path(r'^supplier-vehicle-fitness-partial-update/(?P<pk>[0-9]+)/$',
            VehicleFitnessViewSet.as_view({"patch": "partial_update"}), name='supplier_vehicle_fitness_partial_update'),
    re_path(r'^supplier-vehicle-fitness-retrieve/(?P<pk>[0-9]+)/$', VehicleFitnessViewSet.as_view({"get": "retrieve"}),
            name='supplier_vehicle_fitness_retrieve'),

    # Vehicle Permit
    re_path(r'^supplier-vehicle-permit-list/$', VehiclePermitListView.as_view(),
            name='supplier_vehicle_permit_list'),
    re_path(r'^supplier-vehicle-permit-create/$', VehiclePermitViewSet.as_view({"post": "create"}),
            name='supplier_vehicle_permit_create'),
    re_path(r'^supplier-vehicle-permit-update/(?P<pk>[0-9]+)/$', VehiclePermitViewSet.as_view({"put": "update"}),
            name='supplier_vehicle_permit_update'),
    re_path(r'^supplier-vehicle-permit-partial-update/(?P<pk>[0-9]+)/$',
            VehiclePermitViewSet.as_view({"patch": "partial_update"}), name='supplier_vehicle_permit_partial_update'),
    re_path(r'^supplier-vehicle-permit-retrieve/(?P<pk>[0-9]+)/$', VehiclePermitViewSet.as_view({"get": "retrieve"}),
            name='supplier_vehicle_permit_retrieve'),

    # Supplier Vehicle
    re_path(r'^supplier_supplier-vehicle-list/$', SupplierVehicleListView.as_view(),
            name='supplier_supplier_vehicle_list'),
    re_path(r'^supplier-supplier-vehicle-create/$', SupplierVehicleViewSet.as_view({"post": "create"}),
            name='supplier_supplier_vehicle_create'),
    re_path(r'^supplier-supplier-vehicle-update/(?P<pk>[0-9]+)/$', SupplierVehicleViewSet.as_view({"put": "update"}),
            name='supplier_supplier_vehicle_update'),
    re_path(r'^supplier-supplier-vehicle-partial-update/(?P<pk>[0-9]+)/$',
            SupplierVehicleViewSet.as_view({"patch": "partial_update"}),
            name='supplier_supplier_vehicle_partial_update'),
    re_path(r'^supplier-supplier-vehicle-retrieve/(?P<pk>[0-9]+)/$',
            SupplierVehicleViewSet.as_view({"get": "retrieve"}), name='supplier_supplier_vehicle_retrieve'),

    # SUPPLIER FILE END

    # TEAM FILE START

    # Invoice Summary

    re_path(r'^team-invoice-summary-create/$', InvoiceSummaryViewSet.as_view({"post": "create"}),
            name="team_invoice_summary_create"),
    re_path(r'^team-invoice-summary-update/(?P<pk>[0-9]+)/$', InvoiceSummaryViewSet.as_view({"put": "update"}),
            name="team_invoice_summary_update"),
    re_path(r'^team-invoice-summary-partial-update/(?P<pk>[0-9]+)/$',
            InvoiceSummaryViewSet.as_view({"patch": "partial_update"}), name="team_invoice_summary_partial_update"),
    re_path(r'^team-invoice-summary-retrieve/(?P<pk>[0-9]+)/$', InvoiceSummaryViewSet.as_view({"get": "retrieve"}),
            name="team_invoice_summary_retrieve"),

    re_path(r'^team-manual-booking-list/$', ManualBookingListView.as_view(), name="team_manual_booking_list"),
    re_path(r'^tiny-manual-booking-list/$', TinyManualBookingListView.as_view(), name="tiny_manual_booking_list"),
    re_path(r'^team-lr-number-list/$', LrNumberListView.as_view(), name="team_lr_number_list"),
    re_path(r'^team-outward-payment-list/$', OutwardPaymentListView.as_view(), name="team_outward_payment_list"),
    re_path(r'^team-inward-payment-list/$', InwardPaymentListView.as_view(), name="team_inward_payment_list"),
    re_path(r'^team-invoice-list/$', InvoiceListView.as_view(), name="team_invoice_list"),
    re_path(r'^team-invoice-summary-list/$', InvoiceSummaryListView.as_view(), name="team_invoice_summary_list"),

    re_path(r'^team-outward-payment-bill-list/$', OutwardPaymentBillListView.as_view(),
            name="team_outward_payment_bill_list"),
    re_path(r'^team-credit-debit-note-reason-list/$', CreditDebitNoteReasonListView.as_view(),
            name="team_credit_debit_note_reason_list"),
    re_path(r'^team-credit-note-customer-list/$', CreditNoteCustomerListView.as_view(),
            name="team_credit_note_customer_list"),
    re_path(r'^team-debit-note-customer-list/$', DebitNoteCustomerListView.as_view(),
            name="team_debit_note_customer_list"),
    re_path(r'^team-credit-note-supplier-list/$', CreditNoteSupplierListView.as_view(),
            name="team_credit_note_supplier_list"),
    re_path(r'^team-debit-note-supplier-list/$', DebitNoteSupplierListView.as_view(),
            name="team_debit_note_supplier_list"),
    re_path(r'^team-credit-note-customer-direct-advance-list/$', CreditNoteCustomerDirectAdvanceListView.as_view(),
            name="team_credit_note_customer_direct_advance_list"),
    re_path(r'^team-debit-note-supplier-direct-advance-list/$', DebitNoteSupplierDirectAdvanceListView.as_view(),
            name="team_debit_note_supplier_direct_advance_list"),

    # TEAM TEMPLATE
    re_path(r'^team-dashboard/$', DashboardPageView.as_view(), name="team_dashboad"),
    re_path(r'^mobile-dashboard/$', MobileDashboardPageView.as_view(), name="mobile_dashboad"),
    re_path(r'^team-driver-create-page/$', DriverPageView.as_view(), name="team_driver_create_page"),

    # Manual Booking
    re_path(r'^manual-booking-mis-list/$', ManualBookingMISListView.as_view(),
            name="team_manual_booking_mis_list"),
    re_path(r'^full-manual-booking-create/$', ManualBookingViewSet.as_view({"post": "create_full_booking"}),
            name="full_manual_booking_create"),
    re_path(r'^manual-booking-reprint-lr/(?P<pk>[0-9]+)/$', ManualBookingViewSet.as_view({"get": "reprint_lr"}),
            name="reprint_lr"),
    re_path(r'^commission-manual-booking-create/$', ManualBookingViewSet.as_view({"post": "create_commission_booking"}),
            name="commission_manual_booking_create"),
    re_path(r'^team-manual-booking-create/$', ManualBookingViewSet.as_view({"post": "create_mb"}),
            name="team_manual_booking_create"),
    re_path(r'^manual-booking-update/(?P<pk>[0-9]+)/$', ManualBookingViewSet.as_view({"put": "update"}),
            name="team_manual_booking_update"),
    re_path(r'^manual-booking-partial-update/(?P<pk>[0-9]+)/$',
            ManualBookingViewSet.as_view({"patch": "partial_update"}), name="team_manual_booking_partial_update"),
    re_path(r'^contract-booking-partial-update/$',
            ManualBookingViewSet.as_view({"patch": "update_contract_booking"}), name="contract_booking_partial_update"),
    re_path(r'^manual-booking-retrieve/(?P<pk>[0-9]+)/$', ManualBookingViewSet.as_view({"get": "retrieve"}),
            name="team_manual_booking_retrieve"),

    # LrNumber

    re_path(r'^team-lr-number-create/$', LrNumberViewSet.as_view({"post": "create"}), name="team_lr_number_create"),
    re_path(r'^create-confirmed-booking-lr/$', LrNumberViewSet.as_view({"post": "create_confirmed_booking_lr"}),
            name="create_confirmed_booking_lr"),
    re_path(r'^team-lr-number-update/(?P<pk>[0-9]+)/$', LrNumberViewSet.as_view({"put": "update"}),
            name="team_lr_number_update"),
    re_path(r'^team-lr-number-partial-update/(?P<pk>[0-9]+)/$', LrNumberViewSet.as_view({"patch": "partial_update"}),
            name="team_lr_number_partial_update"),
    re_path(r'^team-lr-number-retrieve/(?P<pk>[0-9]+)/$', LrNumberViewSet.as_view({"get": "retrieve"}),
            name="team_lr_number_retrieve"),

    # Rejected POD

    re_path(r'^team-rejected-pod-create/$', RejectedPODViewSet.as_view({"post": "create"}),
            name="team_rejected_pod_create"),
    # re_path(r'^team-rejected-pod-update/(?P<pk>[0-9]+)/$', RejectedPODViewSet.as_view({"put": "update"}),
    #         name="team_rejected_pod_update"),
    # re_path(r'^team-rejected-pod-partial-update/(?P<pk>[0-9]+)/$',
    #         RejectedPODViewSet.as_view({"patch": "partial_update"}), name="team_rejected_pod_partial_update"),
    re_path(r'^team-rejected-pod-retrieve/(?P<pk>[0-9]+)/$', RejectedPODViewSet.as_view({"get": "retrieve"}),
            name="team_rejected_pod_retrieve"),

    # Booking consigner consignee

    re_path(r'^team-booking-consignor-consignee-create/$',
            BookingConsignorConsigneeViewSet.as_view({"post": "create"}),
            name="team_booking_consignor_consignee_create"),
    re_path(r'^team-booking-consignor-consignee-update/(?P<pk>[0-9]+)/$',
            BookingConsignorConsigneeViewSet.as_view({"put": "update"}),
            name="team_booking_consignor_consignee_update"),
    re_path(r'^team-booking-consignor-consignee-partial-update/(?P<pk>[0-9]+)/$',
            BookingConsignorConsigneeViewSet.as_view({"patch": "partial_update"}),
            name="team_booking_consignor_consignee_partial_update"),
    re_path(r'^team-booking-consignor-consignee-retrieve/(?P<pk>[0-9]+)/$',
            BookingConsignorConsigneeViewSet.as_view({"get": "retrieve"}),
            name="team_booking_consignor_consignee_retrieve"),

    # Booking Insurance

    re_path(r'^team-booking-insurance-create/$', BookingInsuranceViewSet.as_view({"post": "create"}),
            name="team_booking_insurance_create"),
    re_path(r'^team-booking-insurance-update/(?P<pk>[0-9]+)/$', BookingInsuranceViewSet.as_view({"put": "update"}),
            name="team_booking_insurance_update"),
    re_path(r'^team-booking-insurance-partial-update/(?P<pk>[0-9]+)/$',
            BookingInsuranceViewSet.as_view({"patch": "partial_update"}), name="team_booking_insurance_partial_update"),
    re_path(r'^team-booking-insurance-retrieve/(?P<pk>[0-9]+)/$', BookingInsuranceViewSet.as_view({"get": "retrieve"}),
            name="team_booking_insurance_retrieve"),

    # InWard Payment
    re_path(r'^team-inward-payment-create/$', InWardPaymentViewSet.as_view({"post": "create"}),
            name="team_inward_payment_create"),
    re_path(r'^team-inward-payment-update/(?P<pk>[0-9]+)/$', InWardPaymentViewSet.as_view({"put": "update"}),
            name="team_inward_payment_update"),
    re_path(r'^team-inward-payment-partial-update/(?P<pk>[0-9]+)/$',
            InWardPaymentViewSet.as_view({"patch": "partial_update"}), name="team_inward_payment_partial_update"),
    re_path(r'^team-inward-payment-retrieve/(?P<pk>[0-9]+)/$', InWardPaymentViewSet.as_view({"get": "retrieve"}),
            name="team_inward_payment_retrieve"),

    # OutWard Payment

    re_path(r'^team-outward-payment-create/$', OutWardPaymentViewSet.as_view({"post": "create"}),
            name="team_outward_payment_create"),
    re_path(r'^team-outward-payment-update/(?P<pk>[0-9]+)/$', OutWardPaymentViewSet.as_view({"put": "update"}),
            name="team_outward_payment_update"),
    re_path(r'^team-outward-payment-partial-update/(?P<pk>[0-9]+)/$',
            OutWardPaymentViewSet.as_view({"patch": "partial_update"}), name="team_outward_payment_partial_update"),
    re_path(r'^team-reconcile-outward-payments/$',
            OutWardPaymentViewSet.as_view({"patch": "reconcile_payments"}), name="team_reconcile_outward_payments"),
    re_path(r'^team-reconcile-bulk-outward-payments/$',
            OutWardPaymentViewSet.as_view({"post": "reconcile_bulk_payments"}),
            name="team_pending_inward_payment_entry_bulk_create"),
    re_path(r'^team-outward-payment-retrieve/(?P<pk>[0-9]+)/$', OutWardPaymentViewSet.as_view({"get": "retrieve"}),
            name="team_outward_payment_retrieve"),
    re_path(r'^payment-mode-date-message/$', OutWardPaymentViewSet.as_view({"get": "payment_mode_date_message"}),
            name="payment_mode_date_message"),

    # OutWard Payment Bill

    re_path(r'^team-outward-payment-bill-create/$', OutWardPaymentBillViewSet.as_view({"post": "create"}),
            name="team_outward_payment_bill_create"),
    re_path(r'^team-outward-payment-bill-doc/$', OutWardPaymentBillViewSet.as_view({"post": "create_bill_doc"}),
            name="team_outward_payment_bill_doc"),
    re_path(r'^team-outward-payment-bill-update/(?P<pk>[0-9]+)/$',
            OutWardPaymentBillViewSet.as_view({"put": "update"}), name="team_outward_payment_bill_update"),
    re_path(r'^team-outward-payment-bill-partial-update/(?P<pk>[0-9]+)/$',
            OutWardPaymentBillViewSet.as_view({"patch": "partial_update"}),
            name="team_outward_payment_bill_partial_update"),
    re_path(r'^team-outward-payment-bill-retrieve/(?P<pk>[0-9]+)/$',
            OutWardPaymentBillViewSet.as_view({"get": "retrieve"}), name="team_outward_payment_bill_retrieve"),

    # Invoice

    re_path(r'^team-invoice-create/$', InvoiceViewSet.as_view({"post": "create"}), name="team_invoice_create"),
    re_path(r'^invoice-multiple-full-booking/$', InvoiceViewSet.as_view({"post": "invoice_multiple_full_booking"}),
            name="invoice_multiple_full_booking"),
    re_path(r'^invoice-multiple-commission-booking/$',
            InvoiceViewSet.as_view({"post": "invoice_multiple_commission_booking"}),
            name="invoice_multiple_commission_booking"),
    re_path(r'^create-single-booking-invoice/$', InvoiceViewSet.as_view({"post": "create_single_booking_invoice"}),
            name="create_single_booking_invoice"),
    re_path(r'^team-invoice-update/(?P<pk>[0-9]+)/$', InvoiceViewSet.as_view({"put": "update"}),
            name="team_invoice_update"),
    re_path(r'^team-invoice-partial-update/(?P<pk>[0-9]+)/$', InvoiceViewSet.as_view({"patch": "partial_update"}),
            name="team_invoice_partial_update"),
    re_path(r'^team-invoice-retrieve/(?P<pk>[0-9]+)/$', InvoiceViewSet.as_view({"get": "retrieve"}),
            name="team_invoice_retrieve"),
    re_path(r'^team-invoice-pod-files/(?P<pk>[0-9]+)/$', InvoiceViewSet.as_view({"get": "pod_files"}),
            name="team_invoice_pod_files"),

    # To Pay Invoice

    re_path(r'^team-to-pay-invoice-create/$', ToPayInvoiceViewSet.as_view({"post": "create"}),
            name="team_to_pay_invoice_create"),
    re_path(r'^team-to-pay-invoice-update/(?P<pk>[0-9]+)/$', ToPayInvoiceViewSet.as_view({"put": "update"}),
            name="team_to_pay_invoice_update"),
    re_path(r'^team-to-pay-invoice-partial-update/(?P<pk>[0-9]+)/$',
            ToPayInvoiceViewSet.as_view({"patch": "partial_update"}), name="team_to_pay_invoice_partial_update"),
    re_path(r'^team-to-pay-invoice-retrieve/(?P<pk>[0-9]+)/$', ToPayInvoiceViewSet.as_view({"get": "retrieve"}),
            name="team_to_pay_invoice_retrieve"),

    # Pending Inward payment entry

    re_path(r'^team-pending-inward-payment-entry-create/$',
            PendingInwardPaymentEntryViewSet.as_view({"post": "create"}),
            name="team_pending_inward_payment_entry_create"),
    re_path(r'^team-pending-inward-payment-entry-bulk-create/$',
            PendingInwardPaymentEntryViewSet.as_view({"post": "bulk_create"}),
            name="team_pending_inward_payment_entry_bulk_create"),
    re_path(r'^team-pending-inward-payment-bulk-adjust/$',
            PendingInwardPaymentEntryViewSet.as_view({"post": "bulk_adjust"}),
            name="team_pending_inward_payment_bulk_adjust"),
    re_path(r'^team-pending-inward-payment-entry-update/(?P<pk>[0-9]+)/$',
            PendingInwardPaymentEntryViewSet.as_view({"put": "update"}),
            name="team_pending_inward_payment_entry_update"),
    re_path(r'^team-pending-inward-payment-entry-partial-update/(?P<pk>[0-9]+)/$',
            PendingInwardPaymentEntryViewSet.as_view({"patch": "partial_update"}),
            name="team_pending_inward_payment_entry_partial_update"),
    re_path(r'^team-pending-inward-payment-entry-retrieve/(?P<pk>[0-9]+)/$',
            PendingInwardPaymentEntryViewSet.as_view({"get": "retrieve"}),
            name="team_pending_inward_payment_entry_retrieve"),

    # Credit Debit Note Reason

    re_path(r'^credit-debit-note-reason-list/$', CreditDebitNoteReasonListView.as_view(),
            name="team_credit_debit_note_reason_list"),
    re_path(r'^team-credit-debit-note-reason-create/$', CreditDebitNoteReasonViewSet.as_view({"post": "create"}),
            name="team_credit_debit_note_reason_create"),
    re_path(r'^team-credit-debit-note-reason-update/(?P<pk>[0-9]+)/$',
            CreditDebitNoteReasonViewSet.as_view({"put": "update"}), name="team_credit_debit_note_reason_update"),
    re_path(r'^team-credit-debit-note-reason-partial-update/(?P<pk>[0-9]+)/$',
            CreditDebitNoteReasonViewSet.as_view({"patch": "partial_update"}),
            name="team_credit_debit_note_reason_partial_update"),
    re_path(r'^team-credit-debit-note-reason-retrieve/(?P<pk>[0-9]+)/$',
            CreditDebitNoteReasonViewSet.as_view({"get": "retrieve"}), name="team_credit_debit_note_reason_retrieve"),

    # Credit Note Customer

    re_path(r'^team-credit-note-customer-create/$', CreditNoteCustomerViewSet.as_view({"post": "create"}),
            name="team_credit_note_customer_create"),
    re_path(r'^team-credit-note-customer-update/(?P<pk>[0-9]+)/$',
            CreditNoteCustomerViewSet.as_view({"put": "update"}), name="team_credit_note_customer_update"),
    re_path(r'^team-credit-note-customer-partial-update/(?P<pk>[0-9]+)/$',
            CreditNoteCustomerViewSet.as_view({"patch": "partial_update"}),
            name="team_credit_note_customer_partial_update"),
    re_path(r'^team-credit-note-customer-retrieve/(?P<pk>[0-9]+)/$',
            CreditNoteCustomerViewSet.as_view({"get": "retrieve"}), name="team_credit_note_customer_retrieve"),

    # Debit Note Customer

    re_path(r'^team-debit-note-customer-create/$', DebitNoteCustomerViewSet.as_view({"post": "create"}),
            name="team_debit_note_customer_create"),
    re_path(r'^team-debit-note-customer-update/(?P<pk>[0-9]+)/$', DebitNoteCustomerViewSet.as_view({"put": "update"}),
            name="team_debit_note_customer_update"),
    re_path(r'^team-debit-note-customer-partial-update/(?P<pk>[0-9]+)/$',
            DebitNoteCustomerViewSet.as_view({"patch": "partial_update"}),
            name="team_debit_note_customer_partial_update"),
    re_path(r'^team-debit-note-customer-retrieve/(?P<pk>[0-9]+)/$',
            DebitNoteCustomerViewSet.as_view({"get": "retrieve"}), name="team_debit_note_customer_retrieve"),

    # Credit Note Supplier

    re_path(r'^team-credit-note-supplier-create/$', CreditNoteSupplierViewSet.as_view({"post": "create"}),
            name="team_credit_note_supplier_create"),
    re_path(r'^team-credit-note-supplier-update/(?P<pk>[0-9]+)/$',
            CreditNoteSupplierViewSet.as_view({"put": "update"}), name="team_credit_note_supplier_update"),
    re_path(r'^team-credit-note-supplier-partial-update/(?P<pk>[0-9]+)/$',
            CreditNoteSupplierViewSet.as_view({"patch": "partial_update"}),
            name="team_credit_note_supplier_partial_update"),
    re_path(r'^team-credit-note-supplier-retrieve/(?P<pk>[0-9]+)/$',
            CreditNoteSupplierViewSet.as_view({"get": "retrieve"}), name="team_credit_note_supplier_retrieve"),

    # Debit Note Supplier

    re_path(r'^team-debit-note-supplier-create/$', DebitNoteSupplierViewSet.as_view({"post": "create"}),
            name="team_debit_note_supplier_create"),
    re_path(r'^team-debit-note-supplier-update/(?P<pk>[0-9]+)/$', DebitNoteSupplierViewSet.as_view({"put": "update"}),
            name="team_debit_note_supplier_update"),
    re_path(r'^team-debit-note-supplier-partial-update/(?P<pk>[0-9]+)/$',
            DebitNoteSupplierViewSet.as_view({"patch": "partial_update"}),
            name="team_debit_note_supplier_partial_update"),
    re_path(r'^team-debit-note-supplier-retrieve/(?P<pk>[0-9]+)/$',
            DebitNoteSupplierViewSet.as_view({"get": "retrieve"}), name="team_debit_note_supplier_retrieve"),

    # Credit Note Customer Direct Advance

    re_path(r'^team-credit-note-customer-direct-advance-create/$',
            CreditNoteCustomerDirectAdvanceViewSet.as_view({"post": "create"}),
            name="team_credit_note_customer_direct_advance_create"),
    re_path(r'^team-credit-note-customer-direct-advance-update/(?P<pk>[0-9]+)/$',
            CreditNoteCustomerDirectAdvanceViewSet.as_view({"put": "update"}),
            name="team_credit_note_customer_direct_advance_update"),
    re_path(r'^team-credit-note-customer-direct-advance-partial-update/(?P<pk>[0-9]+)/$',
            CreditNoteCustomerDirectAdvanceViewSet.as_view({"patch": "partial_update"}),
            name="team_credit_note_customer_direct_advance_partial_update"),
    re_path(r'^team-credit-note-customer-direct-advance-retrieve/(?P<pk>[0-9]+)/$',
            CreditNoteCustomerDirectAdvanceViewSet.as_view({"get": "retrieve"}),
            name="team_credit_note_customer_direct_advance_retrieve"),

    # Debit Note Supplier Direct Advance

    re_path(r'^team-debit-note-supplier-direct-advance-create/$',
            DebitNoteSupplierDirectAdvanceViewSet.as_view({"post": "create"}),
            name="team_debit_note_supplier_direct_advance_create"),
    re_path(r'^team-debit-note-supplier-direct-advance-update/(?P<pk>[0-9]+)/$',
            DebitNoteSupplierDirectAdvanceViewSet.as_view({"put": "update"}),
            name="team_debit_note_supplier_direct_advance_update"),
    re_path(r'^team-debit-note-supplier-direct-advance-partial-update/(?P<pk>[0-9]+)/$',
            DebitNoteSupplierDirectAdvanceViewSet.as_view({"patch": "partial_update"}),
            name="team_debit_note_supplier_direct_advance_partial_update"),
    re_path(r'^team-debit-note-supplier-direct-advance-retrieve/(?P<pk>[0-9]+)/$',
            DebitNoteSupplierDirectAdvanceViewSet.as_view({"get": "retrieve"}),
            name="team_debit_note_supplier_direct_advance_retrieve"),

    # TEAM FILE END

    # UTILS FILE START

    # State

    re_path(r'^state-list/$', StateListView.as_view(), name="utils_state_list"),
    re_path(r'^utils-state-create/$', StateViewSet.as_view({"post": "create"}), name="utils_state_create"),
    re_path(r'^utils-state-update/(?P<pk>[0-9]+)/$', StateViewSet.as_view({"put": "update"}),
            name="utils_state_update"),
    re_path(r'^utils-state-partial-update/(?P<pk>[0-9]+)/$', StateViewSet.as_view({"patch": "partial_update"}),
            name="utils_state_partial_update"),
    re_path(r'^utils-state-retrieve/(?P<pk>[0-9]+)/$', StateViewSet.as_view({"get": "retrieve"}),
            name="utils_state_retrieve"),

    # City
    re_path(r'^state-list/$', StateListView.as_view(), name="utils_state_list"),
    re_path(r'^utils-city-list/$', CityListView.as_view(), name="utils_city_list"),
    re_path(r'^utils-city-create/$', CityViewSet.as_view({"post": "create"}), name="utils_city_create"),
    re_path(r'^utils-city-update/(?P<pk>[0-9]+)/$', CityViewSet.as_view({"put": "update"}), name="utils_city_update"),
    re_path(r'^utils-city-partial-update/(?P<pk>[0-9]+)/$', CityViewSet.as_view({"patch": "partial_update"}),
            name="utils_city_partial_update"),
    re_path(r'^utils-city-retrieve/(?P<pk>[0-9]+)/$', CityViewSet.as_view({"get": "retrieve"}),
            name="utils_city_retrieve"),
    re_path(r'^utils-city-soft-destroy/(?P<pk>[0-9]+)/$', CityViewSet.as_view({"patch": "soft_destroy"}),
            name="utils_city_soft_destroy"),

    # Address
    re_path(r'^utils-address-create/$', AddressViewSet.as_view({"post": "create"}), name="utils_address_create"),
    re_path(r'^utils-address-update/(?P<pk>[0-9]+)/$', AddressViewSet.as_view({"put": "update"}),
            name="utils_address_update"),
    re_path(r'^utils-address-partial-update/(?P<pk>[0-9]+)/$', AddressViewSet.as_view({"patch": "partial_update"}),
            name="utils_address_partial_update"),
    re_path(r'^utils-address-retrieve/(?P<pk>[0-9]+)/$', AddressViewSet.as_view({"get": "retrieve"}),
            name="utils_address_retrieve"),

    # IDD Details

    re_path(r'^utils-id-details-create/$', IDDetailsViewSet.as_view({"post": "create"}),
            name="utils_id_details_create"),

    re_path(r'^utils-id-details-update/(?P<pk>[0-9]+)/$', IDDetailsViewSet.as_view({"put": "update"}),
            name="utils_id_details_update"),
    re_path(r'^utils-id-details-partial-update/(?P<pk>[0-9]+)/$',
            IDDetailsViewSet.as_view({"patch": "partial_update"}), name="utils_id_details_partial_update"),
    re_path(r'^utils-id-details-retrieve/(?P<pk>[0-9]+)/$', IDDetailsViewSet.as_view({"get": "retrieve"}),
            name="utils_id_details_retrieve"),

    # Bank Name

    re_path(r'^utils-bank-name-create/$', BankNameViewSet.as_view({"post": "create"}), name="utils_bank_name_create"),
    re_path(r'^utils-bank-name-update/(?P<pk>[0-9]+)/$', BankNameViewSet.as_view({"put": "update"}),
            name="utils_bank_name_update"),
    re_path(r'^utils-bank-name-partial-update/(?P<pk>[0-9]+)/$', BankNameViewSet.as_view({"patch": "partial_update"}),
            name="utils_bank_name_partial_update"),
    re_path(r'^utils-bank-name-retrieve/(?P<pk>[0-9]+)/$', BankNameViewSet.as_view({"get": "retrieve"}),
            name="utils_bank_name_retrieve"),

    # Ifsc Details

    re_path(r'^utils-ifsc-detail-create/$', IfscDetailViewSet.as_view({"post": "create"}),
            name="utils_ifsc_detail_create"),
    re_path(r'^utils-ifsc-detail-update/(?P<pk>[0-9]+)/$', IfscDetailViewSet.as_view({"put": "update"}),
            name="utils_ifsc_detail_update"),
    re_path(r'^utils-ifsc-detail-partial-update/(?P<pk>[0-9]+)/$',
            IfscDetailViewSet.as_view({"patch": "partial_update"}), name="utils_ifsc_detail_partial_update"),
    re_path(r'^utils-ifsc-detail-retrieve/(?P<pk>[0-9]+)/$', IfscDetailViewSet.as_view({"get": "retrieve"}),
            name="utils_ifsc_detail_retrieve"),

    # Bank
    re_path(r'^utils-bank-name-list/$', BankNameListView.as_view(), name="utils_bank_name_list"),
    re_path(r'^utils-bank-list/$', BankListView.as_view(), name="utils_bank_list"),
    re_path(r'^utils-bank-create/$', BankViewSet.as_view({"post": "create"}), name="utils_bank_create"),
    re_path(r'^utils-bank-update/(?P<pk>[0-9]+)/$', BankViewSet.as_view({"put": "update"}), name="utils_bank_update"),
    re_path(r'^utils-bank-partial-update/(?P<pk>[0-9]+)/$', BankViewSet.as_view({"patch": "partial_update"}),
            name="utils_bank_partial_update"),
    re_path(r'^utils-bank-retrieve/(?P<pk>[0-9]+)/$', BankViewSet.as_view({"get": "retrieve"}),
            name="utils_bank_retrieve"),

    # Taxation ID

    re_path(r'^utils-taxation-id-create/$', TaxationIDViewSet.as_view({"post": "create"}),
            name="utils_taxation_id_create"),
    re_path(r'^utils-taxation-id-update/(?P<pk>[0-9]+)/$', TaxationIDViewSet.as_view({"put": "update"}),
            name="utils_taxation_id_update"),
    re_path(r'^utils-taxation-id-partial-update/(?P<pk>[0-9]+)/$',
            TaxationIDViewSet.as_view({"patch": "partial_update"}), name="utils_taxation_id_partial_update"),
    re_path(r'^utils-taxation-id-retrieve/(?P<pk>[0-9]+)/$', TaxationIDViewSet.as_view({"get": "retrieve"}),
            name="utils_taxation_id_retrieve"),

    # Aaho Office
    re_path(r'^utils-aaho-office-list/$', AahoOfficeListView.as_view(), name="utils_aaho_office_list"),
    re_path(r'^utils-aaho-office-create/$', AahoOfficeViewSet.as_view({"post": "create"}),
            name="utils_aaho_office_create"),
    re_path(r'^utils-aaho-office-update/(?P<pk>[0-9]+)/$', AahoOfficeViewSet.as_view({"put": "update"}),
            name="utils_aaho_office_update"),
    re_path(r'^utils-aaho-office-partial-update/(?P<pk>[0-9]+)/$',
            AahoOfficeViewSet.as_view({"patch": "partial_update"}), name="utils_aaho_office_partial_update"),
    re_path(r'^utils-aaho-office-retrieve/(?P<pk>[0-9]+)/$', AahoOfficeViewSet.as_view({"get": "retrieve"}),
            name="utils_aaho_office_retrieve"),

    # UTILS FILE END

    # SME FILE START

    # Sme task email
    re_path(r'^sme-sme-task-email-list/$', SmeTaskEmailListView.as_view(), name="sme_sme_task_email_list"),
    re_path(r'^sme-sme-task-email-create/$', SmeTaskEmailViewSet.as_view({"post": "create"}),
            name="sme_sme_task_email_create"),
    re_path(r'^sme-sme-task-email-update/(?P<pk>[0-9]+)/$', SmeTaskEmailViewSet.as_view({"put": "update"}),
            name="sme_sme_task_email_update"),
    re_path(r'^sme-sme-task-email-partial-update/(?P<pk>[0-9]+)/$',
            SmeTaskEmailViewSet.as_view({"patch": "partial_update"}), name="sme_sme_task_email_partial_update"),
    re_path(r'^sme-sme-task-email-retrieve/(?P<pk>[0-9]+)/$', SmeTaskEmailViewSet.as_view({"get": "retrieve"}),
            name="sme_sme_task_email_retrieve"),

    # Sme

    re_path(r'^sme-sme-list/$', SmeListView.as_view(), name="sme_sme_list"),
    re_path(r'^sme-summary-list/$', SmeSummaryListView.as_view(), name="sme_summary_sme_list"),
    re_path(r'^sme-sme-create/$', SmeViewSet.as_view({"post": "create"}), name="sme_sme_create"),
    re_path(r'^sme-create-page/$', SmeCreatePageView.as_view(), name="sme_create_page"),
    re_path(r'^sme-sme-update/(?P<pk>[0-9]+)/$', SmeViewSet.as_view({"put": "update"}), name="sme_sme_update"),
    re_path(r'^sme-sme-partial-update/(?P<pk>[0-9]+)/$', SmeViewSet.as_view({"patch": "partial_update"}),
            name="sme_sme_partial_update"),
    re_path(r'^sme-sme-retrieve/(?P<pk>[0-9]+)/$', SmeViewSet.as_view({"get": "retrieve"}), name="sme_sme_retrieve"),
    re_path(r'^sme-sme-retrieve-app/(?P<pk>[0-9]+)/$', SmeViewSet.as_view({"get": "retrieve_app"}),
            name="sme_sme_retrieve_app"),

    # Rate Type
    re_path(r'^sme-rate-type-list/$', RateTypeListView.as_view(), name="sme_rate_type_list"),
    re_path(r'^sme-rate-type-create/$', RateTypeViewSet.as_view({"post": "create"}), name="sme_rate_type_create"),
    re_path(r'^sme-rate-type-update/(?P<pk>[0-9]+)/$', RateTypeViewSet.as_view({"put": "update"}),
            name="sme_rate_type_update"),
    re_path(r'^sme-rate-type-partial-update/(?P<pk>[0-9]+)/$', RateTypeViewSet.as_view({"patch": "partial_update"}),
            name="sme_rate_type_partial_update"),
    re_path(r'^sme-rate-type-retrieve/(?P<pk>[0-9]+)/$', RateTypeViewSet.as_view({"get": "retrieve"}),
            name="sme_rate_type_retrieve"),

    # Customer contract
    re_path(r'^sme-customer-contract-list/$', CustomerContractListView.as_view(), name="sme_customer_contract_list"),
    re_path(r'^sme-customer-contract-create/$', CustomerContractViewSet.as_view({"post": "create"}),
            name="sme_customer_contract_create"),
    re_path(r'^sme-customer-contract-update/(?P<pk>[0-9]+)/$', CustomerContractViewSet.as_view({"put": "update"}),
            name="sme_customer_contract_update"),
    re_path(r'^sme-customer-contract-partial-update/(?P<pk>[0-9]+)/$',
            CustomerContractViewSet.as_view({"patch": "partial_update"}), name="sme_customer_contract_partial_update"),
    re_path(r'^sme-customer-contract-retrieve/(?P<pk>[0-9]+)/$', CustomerContractViewSet.as_view({"get": "retrieve"}),
            name="sme_customer_contract_retrieve"),
    re_path(r'^customer-contract-data/$', CustomerContractViewSet.as_view({"get": "contract_customer_data"}),
            name="customer_contract_data"),

    # Contract Route
    re_path(r'^sme-contract-route-list/$', ContractRouteListView.as_view(), name="sme_contract_route_list"),
    re_path(r'^sme-contract-route-create/$', ContractRouteViewSet.as_view({"post": "create"}),
            name="sme_contract_route_create"),
    re_path(r'^sme-contract-route-update/(?P<pk>[0-9]+)/$', ContractRouteViewSet.as_view({"put": "update"}),
            name="sme_contract_route_update"),
    re_path(r'^sme-contract-route-partial-update/(?P<pk>[0-9]+)/$',
            ContractRouteViewSet.as_view({"patch": "partial_update"}), name="sme_contract_route_partial_update"),
    re_path(r'^sme-contract-route-retrieve/(?P<pk>[0-9]+)/$', ContractRouteViewSet.as_view({"get": "retrieve"}),
            name="sme_contract_route_retrieve"),

    # Contact Details
    re_path(r'^sme-contact-details-list/$', ContactDetailsListView.as_view(), name="sme_contact_details_list"),
    re_path(r'^sme-contact-details-create/$', ContactDetailsViewSet.as_view({"post": "create"}),
            name="sme_contact_details_create"),
    re_path(r'^sme-contact-details-update/(?P<pk>[0-9]+)/$', ContactDetailsViewSet.as_view({"put": "update"}),
            name="sme_contact_details_update"),
    re_path(r'^sme-contact-details-partial-update/(?P<pk>[0-9]+)/$',
            ContactDetailsViewSet.as_view({"patch": "partial_update"}), name="sme_contact_details_partial_update"),
    re_path(r'^sme-contact-details-retrieve/(?P<pk>[0-9]+)/$', ContactDetailsViewSet.as_view({"get": "retrieve"}),
            name="sme_contact_details_retrieve"),

    # Location
    re_path(r'^sme-location-list/$', LocationListView.as_view(), name="sme_location_list"),
    re_path(r'^sme-location-create/$', LocationViewSet.as_view({"post": "create"}), name="sme_location_create"),
    re_path(r'^sme-location-update/(?P<pk>[0-9]+)/$', LocationViewSet.as_view({"put": "update"}),
            name="sme_location_update"),
    re_path(r'^sme-location-partial-update/(?P<pk>[0-9]+)/$', LocationViewSet.as_view({"patch": "partial_update"}),
            name="sme_location_partial_update"),
    re_path(r'^sme-location-retrieve/(?P<pk>[0-9]+)/$', LocationViewSet.as_view({"get": "retrieve"}),
            name="sme_location_retrieve"),

    # Consignor Consignee
    re_path(r'^sme-consignor-consignee-list/$', ConsignorConsigneeListView.as_view(),
            name="sme_consignor_consignee_list"),
    re_path(r'^sme-consignor-consignee-create/$', ConsignorConsigneeViewSet.as_view({"post": "create"}),
            name="sme_consignor_consignee_create"),
    re_path(r'^sme-consignor-consignee-update/(?P<pk>[0-9]+)/$', ConsignorConsigneeViewSet.as_view({"put": "update"}),
            name="sme_consignor_consignee_update"),
    re_path(r'^sme-consignor-consignee-partial-update/(?P<pk>[0-9]+)/$',
            ConsignorConsigneeViewSet.as_view({"patch": "partial_update"}),
            name="sme_consignor_consignee_partial_update"),
    re_path(r'^sme-consignor-consignDriverViewSetee-retrieve/(?P<pk>[0-9]+)/$',
            ConsignorConsigneeViewSet.as_view({"get": "retrieve"}), name="sme_consignor_consignee_retrieve"),

    # Preferred Vehicle
    re_path(r'^sme-preferred-vehicle-list/$', PreferredVehicleListView.as_view(), name="sme_preferred_vehicle_list"),
    re_path(r'^sme-preferred-vehicle-create/$', PreferredVehicleViewSet.as_view({"post": "create"}),
            name="sme_preferred_vehicle_create"),
    re_path(r'^sme-preferred-vehicle-update/(?P<pk>[0-9]+)/$', PreferredVehicleViewSet.as_view({"put": "update"}),
            name="sme_preferred_vehicle_update"),
    re_path(r'^sme-preferred-vehicle-partial-update/(?P<pk>[0-9]+)/$',
            PreferredVehicleViewSet.as_view({"patch": "partial_update"}), name="sme_preferred_vehicle_partial_update"),
    re_path(r'^sme-preferred-vehicle-retrieve/(?P<pk>[0-9]+)/$', PreferredVehicleViewSet.as_view({"get": "retrieve"}),
            name="sme_preferred_vehicle_retrieve"),

    # Sme Enquiry

    re_path(r'^sme-sme-enquiry-create/$', SmeEnquiryViewSet.as_view({"post": "create"}), name="sme_sme_enquiry_create"),
    re_path(r'^sme-sme-enquiry-update/(?P<pk>[0-9]+)/$', SmeEnquiryViewSet.as_view({"put": "update"}),
            name="sme_sme_enquiry_update"),
    re_path(r'^sme-sme-enquiry-partial-update/(?P<pk>[0-9]+)/$',
            SmeEnquiryViewSet.as_view({"patch": "partial_update"}), name="sme_sme_enquiry_partial_update"),
    re_path(r'^sme-sme-enquiry-retrieve/(?P<pk>[0-9]+)/$', SmeEnquiryViewSet.as_view({"get": "retrieve"}),
            name="sme_sme_enquiry_retrieve"),

    # SME FILE END

    # OWNER FILE START

    # Route

    re_path(r'^owner-route-create/$', RouteViewSet.as_view({"post": "create"}), name="owner_route_create"),
    re_path(r'^owner-route-update/(?P<pk>[0-9]+)/$', RouteViewSet.as_view({"put": "update"}),
            name="owner_route_update"),
    re_path(r'^owner-route-partial-update/(?P<pk>[0-9]+)/$', RouteViewSet.as_view({"patch": "partial_update"}),
            name="owner_route_partial_update"),
    re_path(r'^owner-route-retrieve/(?P<pk>[0-9]+)/$', RouteViewSet.as_view({"get": "retrieve"}),
            name="owner_route_retrieve"),

    # Owner
    re_path(r'^owner-owner-list/$', OwnerListView.as_view(), name="owner_owner_list"),
    re_path(r'^owner-owner-create/$', OwnerViewSet.as_view({"post": "create"}), name="owner_owner_create"),
    re_path(r'^owner-owner-update/(?P<pk>[0-9]+)/$', OwnerViewSet.as_view({"put": "update"}),
            name="owner_owner_update"),
    re_path(r'^owner-owner-partial-update/(?P<pk>[0-9]+)/$', OwnerViewSet.as_view({"patch": "partial_update"}),
            name="owner_owner_partial_update"),
    re_path(r'^owner-owner-retrieve/(?P<pk>[0-9]+)/$', OwnerViewSet.as_view({"get": "retrieve"}),
            name="owner_owner_retrieve"),

    # Owner Vehicle
    re_path(r'^owner-owner-vehicle-list/$', OwnerVehicleListView.as_view(), name="owner_owner_vehicle_list"),
    re_path(r'^vehicle-summary-list/$', OwnerVehicleSummaryListView.as_view(), name="vehicle_summary_list"),
    re_path(r'^owner-owner-vehicle-create/$', OwnerVehicleViewSet.as_view({"post": "create"}),
            name="owner_owner_vehicle_create"),
    re_path(r'^owner-owner-vehicle-update/(?P<pk>[0-9]+)/$', OwnerVehicleViewSet.as_view({"put": "update"}),
            name="owner_owner_vehicle_update"),
    re_path(r'^owner-owner-vehicle-partial-update/(?P<pk>[0-9]+)/$',
            OwnerVehicleViewSet.as_view({"patch": "partial_update"}), name="owner_owner_vehicle_partial_update"),
    re_path(r'^owner-fms-vehicle-partial-update/(?P<pk>[0-9]+)/$',
            OwnerVehicleViewSet.as_view({"patch": "fms_update"}), name="owner_fms_vehicle_partial_update"),
    re_path(r'^owner-owner-vehicle-retrieve/(?P<pk>[0-9]+)/$', OwnerVehicleViewSet.as_view({"get": "retrieve"}),
            name="owner_owner_vehicle_retrieve"),

    # Fuel Card
    re_path(r'^owner-fuel-card-list/$', FuelCardListView.as_view(), name="owner_fuel_card_list"),
    re_path(r'^owner-fuel-card-create/$', FuelCardViewSet.as_view({"post": "create"}), name="owner_fuel_card_create"),
    re_path(r'^owner-fuel-card-update/(?P<pk>[0-9]+)/$', FuelCardViewSet.as_view({"put": "update"}),
            name="owner_fuel_card_update"),
    re_path(r'^owner-fuel-card-partial-update/(?P<pk>[0-9]+)/$', FuelCardViewSet.as_view({"patch": "partial_update"}),
            name="owner_fuel_card_partial_update"),
    re_path(r'^owner-fuel-card-retrieve/(?P<pk>[0-9]+)/$', FuelCardViewSet.as_view({"get": "retrieve"}),
            name="owner_fuel_card_retrieve"),

    # Owner

    re_path(r'^owner-fuel-card-transaction-create/$', FuelCardTransactionViewSet.as_view({"post": "create"}),
            name="owner_fuel_card_transaction_create"),
    re_path(r'^owner-fuel-card-transaction-update/(?P<pk>[0-9]+)/$',
            FuelCardTransactionViewSet.as_view({"put": "update"}), name="owner_fuel_card_transaction_update"),
    re_path(r'^owner-fuel-card-transaction-partial-update/(?P<pk>[0-9]+)/$',
            FuelCardTransactionViewSet.as_view({"patch": "partial_update"}),
            name="owner_fuel_card_transaction_partial_update"),
    re_path(r'^owner-fuel-card-transaction-retrieve/(?P<pk>[0-9]+)/$',
            FuelCardTransactionViewSet.as_view({"get": "retrieve"}), name="owner_fuel_card_transaction_retrieve"),


    # OWNER FILE END

    re_path(r'^send-document-email/$', app_version.SendEmailViewSet.as_view(
        {'post': 'vehicle_documents_email'}), name='send_document_email'),

    # Rest API for getting bookings data as per user category or vehicle ID
    re_path(r'^get-bookings-data/$', booking.BookingsDataListView.as_view(), name='get_bookings_data'),

    # Rest API for getting single vehicle gps data
    re_path(r'^get-vehicle-gps-data/$', driver.VehicleGPSDataListView.as_view(), name='get_vehicle_gps_data'),

    # Rest API for tracking all vehicles of a broker
    re_path(r'^get-supplier-vehicles-gps-data/$', driver.SupplierVehiclesGPSDataListView.as_view(),
            name='get_supplier_vehicles_gps_data'),


    re_path(r'^team-datatable-filter/(?P<pk>[0-9]+)/$',
            DataTablesFilterViewSet.as_view({'get': 'retrieve'}),
            name='team_datatable_filter'),

]
