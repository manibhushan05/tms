from django.conf.urls import url

from team import views_other, views_receipts, views_invoices, views_profile, views_users, views_booking, views_payment, \
    views_credit_debit_note, views_gps_tracking, views_documents, views_email_template

teamUrlPattern = [
    # views_receipts
    # url(r'^outward-payments-bills/$', views_receipts.outward_payments_bill),
    # url(r'^dashboard/$', views_other.dashboard),

    # # views_invoices
    # # FULL BOOKING
    # url(r'^fetch-full-booking-data-page/$', views_booking.fetch_full_booking_data_page),
    # url(r'^full-booking-page/$', views_booking.full_booking_page),
    # url(r'^place-full-booking/$', views_booking.place_full_booking),
    # url(r'^save-edited-booking-data/$', views_invoices.save_edited_booking_data),
    # url(r'^update-contract-booking-page/$', views_booking.update_contract_booking_rate_page),
    # url(r'^update-contract-booking/$', views_booking.update_contract_booking_rate),
    #
    # # COMMISSION BOOKING
    # url(r'^fetch-commission-booking-data-page/$', views_booking.fetch_commission_booking_data_page),
    # url(r'^commission-booking-page/$', views_booking.commission_booking_page),
    # url(r'^place-commission-booking/$', views_booking.place_commission_booking),
    # url(r'^save-edited-commission-booking-data/$',
    #     views_invoices.save_edited_commission_only_booking_data),
    #
    # # BOOKING ARCHIVE
    # url(r'^partial-booking-history/$', views_booking.partial_booking_history),
    # url(r'^partial-booking-data/$', views_booking.partial_booking_data),
    # url(r'^full-booking-history/$', views_booking.all_booking_history),
    # url(r'^booking-archive-data/$', views_booking.booking_archive_data),
    # url(r'^booking-edit/$', views_booking.booking_edit_save_reprint),
    # url(r'^mis-booking/$', views_booking.mis_booking_page),
    #
    # # PAYMENT
    # url(r'^inward-payments/$', views_payment.in_ward_payments),
    # url(r'^inward-payments-edit-booking/$', views_payment.inward_payments_edit_booking),
    # url(r'^inward-payments-commission-edit-booking/$',
    #     views_payment.inward_payments_commission_edit_booking),
    # url(r'^outward-payment-page/$', views_payment.outward_payment_page),
    # url(r'^outward-payments/$', views_payment.outward_payments),
    # url(r'^outward-payments-edit-booking/$', views_payment.outward_payments_edit_booking),
    # url(r'^outward-payments-commission-edit-booking/$',
    #     views_payment.outward_payments_commission_edit_booking),
    # url(r'^inward-payment-history/$', views_payment.inward_payment_history),
    # url(r'^outward-payment-history/$', views_payment.outward_payment_history),
    # url(r'^outward-payments-data/$', views_payment.outward_payments_data),
    # url(r'^inward-payments-data/$', views_payment.inward_payments_data),
    # url(r'^update-in-ward-payment/$', views_payment.update_in_ward_payment),
    # url(r'^save-updated-in-ward-payment/$', views_payment.save_updated_in_ward_payment),
    # url(r'^update-out-ward-payment/$', views_payment.update_out_ward_payment),
    # url(r'^save-updated-out-ward-payment/$', views_payment.save_updated_out_ward_payment),
    #
    # # Invoice
    # url(r'^fetch-full-booking-invoice-data-page/$',
    #     views_invoices.fetch_full_booking_invoice_data_page),
    # url(r'^commission-invoice-data-page/$', views_invoices.fetch_commission_invoice_data_page),
    # url(r'^commission-invoice-page/$', views_invoices.commission_invoice_page),
    # url(r'^full-booking-invoice-page/$', views_invoices.full_booking_invoice_page),
    # url(r'^full-booking-multi-invoice-booking_data/$',
    #     views_invoices.full_booking_multi_invoice_booking_data),
    # url(r'^invoice-multiple-commission-booking-page/$',
    #     views_invoices.invoice_multiple_commission_booking_page),
    # url(r'^invoice-multiple-full-booking/$', views_invoices.invoice_multiple_full_booking_post),
    # url(r'^invoice-multiple-commission-booking/$',
    #     views_invoices.invoice_multiple_commission_booking_post),
    #
    # # ravindra
    # url(r'^get_singlecustomer_bookingdata/$', views_invoices.get_singlecustomer_bookingdata),
    #
    # url(r'^get-lr-details/$', views_other.get_lr_details, name="get_lr_details"),
    # url(r'^track-vehicles/$', views_gps_tracking.track_vehicles, name="track_vehicle_team"),
    # url(r'^track-individual-vehicles/$', views_gps_tracking.track_individual_veh,
    #     name="track_indv_vehicle_team"),
    # url(r'^register-beneficiary-account/$', views_other.register_beneficiary_bank_account),
    # url(r'^fetch-bank-details-using-ifsc/$', views_other.fetch_bank_details_using_ifsc),
    # url(r'^create-beneficiary-account/$', views_other.create_beneficiary_account),
    # url(r'^update-beneficiary-account-page/$', views_other.update_bank_account_page),
    # url(r'^update-beneficiary-account/$', views_other.update_bank_account),
    # url(r'^beneficiary-list/$', views_other.beneficiary_list),
    # url(r'^invoice-summary-data/$', views_invoices.invoices_summary_data),
    # url(r'^invoice-summary-page/$', views_invoices.invoice_summary_list),
    #
    # url(r'^invoice-list/$', views_invoices.invoice_list),
    # url(r'^invoice-data/$', views_invoices.invoices_data),
    # url(r'^invoice-number-data/$', views_invoices.invoice_number_data),
    # url(r'^booking-id-data/$', views_booking.booking_id_data),
    # url(r'^lr-download/$', views_booking.lr_download),
    # url(r'^lr-download-data/$', views_booking.lr_download_data),
    # url(r'^downloads-bill-payments/$', views_other.supplier_payment_receipt_page),
    # url(r'^supplier-payment-receipt-data/$', views_other.supplier_payment_receipt_data),
    # url(r'^downloads-opb-edit-payments/$', views_other.downloads_opb_edit_payments),
    # url(r'^download-payment-file-post/$', views_other.download_payment_file_post),
    # url(r'^download-payment-file/$', views_other.download_payment_file_page),
    # url(r'^pod-history/$', views_other.pod_archive_page),
    # url(r'^pod-archive-data/$', views_other.pod_archive_data),
    # # payments
    # url(r'^pending-inward-payment-page/$', views_payment.pending_inward_payment_entry_template),
    # url(r'^pending-inward-payment/$', views_payment.pending_inward_payment),
    # url(r'^pending-inward-payment-list/$', views_payment.pending_payment_list),
    # url(r'^uncredited-cheques/$', views_payment.uncredited_cheques),
    # url(r'^resolve-cheque/$', views_payment.resolve_cheque),
    # url(r'^upload-inward-credited-payments/$', views_payment.upload_bulk_credited_payment),
    # url(r'^inward-payments-adjustment-page/$', views_payment.inward_payment_adjustment_page),
    # url(r'^inward-payments-adjustment-entry/$', views_payment.inward_payment_adjustments),
    # url(r'^payment-mode-date-message/$', views_payment.payment_mode_date_message),
    #
    # url(r'^register-sme-template/$', views_users.register_customer_template),
    # url(r'^register-vehicle-template/$', views_users.vehicle_registration_page),
    # url(r'^register-sme/$', views_users.register_customer),
    # url(r'^register-owner/$', views_users.register_owner),
    # url(r'^register-vehicle/$', views_users.register_vehicle),
    # url(r'^sme-list/$', views_users.sme_list),
    # url(r'^vehicle-list/$', views_users.vehicle_archive),
    # url(r'^owner-list/$', views_users.owner_list),
    # url(r'^update-customer-page/$', views_users.update_customer_page),
    # url(r'^update-vehicle-page/$', views_users.update_vehicle_page),
    # url(r'^update-owner-page/$', views_users.update_owner_page),
    # url(r'^update-customer-data/$', views_users.update_customer),
    # url(r'^update-vehicle-data/$', views_users.update_vehicle),
    # url(r'^update-owner-data/$', views_users.update_owner),
    # url(r'^register-supplier-template/$', views_users.register_supplier_template),
    # url(r'^register-supplier/$', views_users.register_supplier),
    # url(r'^supplier-list/$', views_users.supplier_list),
    # url(r'^register-driver/$', views_users.register_driver),
    # url(r'^register-owner-template/$', views_users.owner_registration_page),
    # # Employee
    # url(r'^employee-profile/$', views_profile.emp_profile),
    # url(r'^change-password-page/$', views_profile.change_password_page),
    # url(r'^change-password/$', views_profile.change_password),
    # url(r'^update-profile-page/$', views_profile.update_profile_page),
    # url(r'^update-profile/$', views_profile.update_profile),
    # url(r'^update-supplier-page/$', views_users.update_supplier_page),
    # url(r'^update-supplier/$', views_users.update_supplier),
    # # Driver
    # url(r'^register-driver-page/$', views_users.register_driver_page),
    # url(r'^driver-list/$', views_users.driver_list_page),
    # url(r'^update-driver-page/$', views_users.update_driver_page),
    # url(r'^update-driver/$', views_users.update_driver_details),
    #
    # # Documents
    # url(r'^unverified-documents/$', views_documents.unverified_documents),
    # url(r'^unverified-documents-data/$', views_documents.unverified_documents_data),
    # url(r'^verify-documents/$', views_documents.verify_documents),
    # # pod
    # url(r'^unverified-pod-page/$', views_documents.unverified_pod_page),
    # url(r'^my-pod-uploaded-page/$', views_documents.my_pod_uploaded_documents_page),
    # url(r'^verify-pod/$', views_documents.update_booking_pod_data),
    # url(r'^resubmit-rejected-pod/$', views_documents.resubmit_rejected_pod),
    # url(r'^pod-delivered-date-validation/$', views_documents.pod_delivered_date_validation),
    #
    # # accounting summary
    # url(r'^customer-accounting-summary/$', views_other.customer_accounting_summary),
    # url(r'^supplier-accounting-summary/$', views_other.supplier_accounting_summary),
    # url(r'^owner-accounting-summary/$', views_other.owner_accounting_summary),
    # url(r'^daily-freight-upload-page', views_other.daily_freight_upload_page),
    # url(r'^upload-daily-freight', views_other.upload_daily_freight),
    # url(r'^error-exceeding-amount', views_payment.error_exceeding_outward_amount),
    # # ajax call
    # url(r'^contract-customer-data/$', views_booking.contract_customer_data),
    #
    # # Credit Note Debit Note Page
    # url(r'^credit-debit-note-reason-data/$', views_credit_debit_note.credit_debit_note_reason_data),
    #
    # url(r'^issue-credit-note-customer-page/$', views_credit_debit_note.issue_credit_note_customer_page),
    # url(r'^issue-credit-note-customer-direct-advance-page/$',
    #     views_credit_debit_note.issue_credit_note_customer_direct_advance_page),
    # url(r'^issue-debit-note-customer-page/$', views_credit_debit_note.issue_debit_note_customer_page),
    # url(r'^issue-credit-note-supplier-page/$', views_credit_debit_note.issue_credit_note_supplier_page),
    # url(r'^issue-debit-note-supplier-page/$', views_credit_debit_note.issue_debit_note_supplier_page),
    # url(r'^issue-debit-note-supplier-direct-advance-page/$',
    #     views_credit_debit_note.issue_debit_note_supplier_direct_advance_page),
    #
    # # Issue Credit Debit  Note
    # url(r'^issue-credit-debit-note-page/$', views_credit_debit_note.issue_credit_debit_note_page),
    # url(r'^adjust-credit-debit-note-page/$', views_credit_debit_note.adjust_credit_debit_note_page),
    # url(r'^approve-credit-debit-note-page/$', views_credit_debit_note.approve_credit_debit_note_page),
    #
    # url(r'^create-credit-note-customer/$', views_credit_debit_note.create_issue_credit_note_customer),
    # url(r'^create-credit-note-supplier/$', views_credit_debit_note.create_issue_credit_note_supplier),
    # url(r'^create-debit-note-customer/$', views_credit_debit_note.create_issue_debit_note_customer),
    # url(r'^create-debit-note-supplier/$', views_credit_debit_note.create_issue_debit_note_supplier),
    # url(r'^create-credit-note-customer-direct-advance/$',
    #     views_credit_debit_note.create_issue_credit_note_customer_direct_advance),
    # url(r'^create-debit-note-supplier-direct-advance/$',
    #     views_credit_debit_note.create_issue_debit_note_supplier_direct_advance),
    #
    # # Issue Credit Debit  Note Approve Approve
    # url(r'^update-credit-note-customer/(?P<pk>[0-9]+)/$', views_credit_debit_note.update_credit_note_customer),
    # url(r'^update-credit-note-supplier/(?P<pk>[0-9]+)/$', views_credit_debit_note.update_issue_credit_note_supplier),
    # url(r'^update-debit-note-customer/(?P<pk>[0-9]+)/$', views_credit_debit_note.update_debit_note_customer),
    # url(r'^update-debit-note-supplier/(?P<pk>[0-9]+)/$', views_credit_debit_note.update_debit_note_supplier),
    # url(r'^update-credit-note-customer-direct-advance/(?P<pk>[0-9]+)/$',
    #     views_credit_debit_note.update_credit_note_customer_direct_advance),
    # url(r'^update-debit-note-supplier-direct-advance/(?P<pk>[0-9]+)/$',
    #     views_credit_debit_note.update_debit_note_supplier_direct_advance),
    #
    # # Issue Credit Debit  Note Approve Page
    # url(r'^approve-credit-note-customer-page/$', views_credit_debit_note.approve_credit_note_customer_page),
    # url(r'^approve-credit-note-supplier-page/$', views_credit_debit_note.approve_issue_credit_note_supplier_page),
    # url(r'^approve-debit-note-customer-page/$', views_credit_debit_note.approve_debit_note_customer_page),
    # url(r'^approve-debit-note-supplier-page/$', views_credit_debit_note.approve_debit_note_supplier_page),
    # url(r'^approve-credit-note-customer-direct-advance-page/$',
    #     views_credit_debit_note.approve_credit_note_customer_direct_advance_page),
    # url(r'^approve-debit-note-supplier-direct-advance-page/$',
    #     views_credit_debit_note.approve_debit_note_supplier_direct_advance_page),
    #
    # # Issue Credit Debit  Note Approve Data
    # url(r'^approve-credit-note-customer-data/$', views_credit_debit_note.approve_credit_note_customer_data),
    # url(r'^approve-credit-note-supplier-data/$', views_credit_debit_note.approve_credit_note_supplier_data),
    # url(r'^approve-debit-note-customer-data/$', views_credit_debit_note.approve_debit_note_customer_data),
    # url(r'^approve-debit-note-supplier-data/$', views_credit_debit_note.approve_debit_note_supplier_data),
    # url(r'^approve-credit-note-customer-direct-advance-data/$',
    #     views_credit_debit_note.approve_credit_note_customer_direct_advance_data),
    # url(r'^approve-debit-note-supplier-direct-advance-data/$',
    #     views_credit_debit_note.approve_debit_note_supplier_direct_advance_data),
    #
    # url(r'^adjust-credit-note-customer-page/$', views_credit_debit_note.adjust_credit_note_customer_page),
    # url(r'^adjust-credit-note-customer-direct-advance-page/$',
    #     views_credit_debit_note.adjust_credit_note_customer_direct_advance_page),
    # url(r'^adjust-debit-note-supplier-direct-advance-page/$',
    #     views_credit_debit_note.adjust_debit_note_supplier_direct_advance_page),
    # url(r'^adjust-credit-note-supplier-page/$', views_credit_debit_note.adjust_credit_note_supplier_page),
    # url(r'^adjust-debit-note-supplier-page/$', views_credit_debit_note.adjust_debit_note_supplier_page),
    # url(r'^adjust-debit-note-customer-page/$', views_credit_debit_note.adjust_debit_note_customer_page),
    #
    # MAIL TEMPLATE
    url(r'^daily_mail_pending_pod/$', views_email_template.daily_mail_pending_pod),
    url(r'^notify_admins_about_to_pay_booking/$', views_email_template.notify_admins_about_to_pay_booking),
    url(r'^notify_weekly_partial_tbb/$', views_email_template.notify_weekly_partial_tbb),
    url(r'^notify_pod_received_invoice_not_raised/$', views_email_template.notify_pod_received_invoice_not_raised),
    url(r'^notify_customer_dispatch_details/$', views_email_template.notify_customer_dispatch_details),
    url(r'^notify_invoice_customers_email_page/$', views_email_template.notify_invoice_customers_email_page),
    url(r'^notify_excess_outward_payment_email_page/$', views_email_template.notify_excess_outward_payment),
]