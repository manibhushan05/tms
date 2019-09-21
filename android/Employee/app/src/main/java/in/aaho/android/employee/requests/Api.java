package in.aaho.android.employee.requests;

/**
 * Created by Suraj M
 */

public class Api {
//    public static final String SERVER_URL = "https://aaho.in";


//    public static final String SERVER_URL = "https://dev.aaho.in";
//    public static final String SERVER_URL = "https://stage.aaho.in";
//    public static final String SERVER_URL = "http://10.0.2.2:8000";
    public static final String SERVER_URL = "http://192.168.1.9:8000";

    // Api urls
    static final String LOGIN_URL = url("/api/login/");
    /*static final String LOGIN_URL = url("/api/fms/login_employees/");*/

    static final String LOGIN_STATUS_URL = url("/api/fms/login-status/");
    static final String AWS_CRED_URL = url("/api/retrieve-aws-credentials/");

    static final String LOGOUT_URL = url("/api/logout/");
    /*static final String LOGOUT_URL = url("/api/fms/logout/");*/

    static final String APP_DATA_URL = url("/api/fms/app-data/");
    static final String USER_DATA_URL = url("/api/get-user-initial-data/");// new rest api

    static final String CATEGORY_DATA_URL = url("/api/usercategory-list/");// new rest api

    static final String REQUIREMENT_SUBMIT_URL = url("/api/requirement-create/");
    /*static final String REQUIREMENT_SUBMIT_URL = url("/api/fms/new-requirement/");*/

    static final String EDIT_PASSWORD_URL = url("/api/fms/change-password/");

    /** To get the mobile number from username/phone-number */
    public static final String FORGOT_PASSWORD_URL = url("/api/forgot-password/");
    /*public static final String FORGOT_PASSWORD_URL = url("/api/fms/get-phone-number/");*/

    public static final String VERIFY_OTP_URL = url("/api/verify-otp/"); // new Rest api

    public static final String RESET_PASSWORD_URL = url("/api/fms/forgot-password-reset/");

    public static final String CITY_DATA_URL = url("/api/utils-city-list/");
    /*public static final String CITY_DATA_URL = url("/utils/cities-data/");*/

    public static final String VEHICLE_TYPE_DATA_URL = url("/api/supplier-vehicle-category-list/");
    /*public static final String VEHICLE_TYPE_DATA_URL = url("/utils/vehicle-categories-data/");*/

    public static final String CUSTOMER_DATA_URL = url("/api/sme-sme-list/");
    /*public static final String CUSTOMER_DATA_URL = url("/utils/customers-data/");*/

    public static final String AAHO_OFFICE_DATA_URL = url("/api/utils-aaho-office-list/");
    /*public static final String AAHO_OFFICE_DATA_URL = url("/utils/aaho-office-data/");*/

    //update-requirement
    static final String UPDATE_REQUIREMENT_URL = url("/api/requirement-update/");
    /*static final String UPDATE_REQUIREMENT_URL = url("/api/fms/update-requirement/");*/

    // Status strings
    public static final String STATUS_SUCCESS = "success";
    public static final String STATUS_ERROR = "error";

    public static final String TAG = "AAHO";

    private static String url(String path) {
        return SERVER_URL + path;
    }


    // sales = unverified & traffic = open
    // Added by Suraj
    /** To get the available loads from server */
    public static final String GET_AVL_LOADS = url("/api/requirement-list-filter/");
    /*public static final String GET_AVL_LOADS = url("/api/fms/get-filtered-requirements/");*/

    public static final String GET_MY_LOADS = url("/api/requirement-list-user/");
    /*public static final String GET_MY_LOADS = url("/api/fms/get-my-requirements/");*/

    public static final String GET_AVL_REQ_QUOTE = url("/api/req-quotes-list/");

    public static final String APP_VERSION_URL = url("/api/mobile-app-version-check/");
    /*static final String APP_VERSION_URL = url("/api/fms/app-version-check/");*/

    /** To send the FCM token to server */
    public static final String POST_FCM_TOKEN_URL = url("/api/notification-mobile-device-create-update/");
    /*public static final String POST_FCM_TOKEN_URL = url("/notification/create-notification-device/");*/

    public static final String EMP_ROLE_FUNCTIONALITY_URL = url("/api/employee-roles-functionalities-mapping-list/");

    public static final String EMP_ROLE_MAPPING_LIST_URL = url("/api/employee-roles-mapping-list/");

    /** To get the SME data from server which is used to get aaho office data & material to
     *  Auto filled in requirement screen */
    static final String SME_DATA_URL = url("/api/sme-sme-retrieve-app/");
    /*static final String SME_DATA_URL = url("/api/sme-sme-retrieve/");*/

    static final String REASON_LIST_DATA_URL = url("/api/get-requirement-cancel-reasons/");

    /** To get list of Pending LR from server */
    public static final String GET_PENDING_LR_URL = url("/api/team-manual-booking-list/?booking_data_category=incomplete_lr");

    /** To update the Pending LR status */
    public static final String STATUS_UPDATE_URL = url("/api/booking-statuses-mapping-create-key-based/");

    /** To update the Pending LR status */
    public static final String BOOKING_MAPPING_STATUS_UPDATE_URL = url("/api/booking-statuses-mapping-update/");

    /** To update the Pending LR status */
    public static final String BULK_STATUS_UPDATE_URL = url("/api/booking-statuses-mapping-create-key-based-bulk/");

    /** To update the Pending LR comment */
    public static final String COMMENT_UPDATE_URL = url("/api/booking-statuses-mapping-comments-create/");

    /** To update the Bulk comment */
    public static final String BULK_COMMENT_UPDATE_URL = url("/api/booking-statuses-mapping-comments-create-bulk/");

    /** To get list of in transit from server */
    public static final String GET_IN_TRANSIT_URL = url("/api/team-manual-booking-list/?booking_data_category=in_transit");

    /** To update the In Transit Location */
    public static final String LOCATION_UPDATE_URL = url("/api/booking-statuses-mapping-location-save/");

    /** To get list of delivered from server */
    public static final String GET_DELIVRED_URL = url("/api/team-manual-booking-list/?booking_data_category=delivered");

    /** To get the booking details from server */
    public static final String TEAM_TRIP_DETAILS = url("/api/manual-booking-retrieve/");

    /** To upload the pod file entry to server */
    public static final String UPLOAD_POD_URL = url("/api/file-upload-pod-file-create/");

    /** To get list of invoice confirmation data from server */
    public static final String GET_INVOICE_CONFIRMATION_URL = url("/api/team-manual-booking-list/?booking_data_category=invoice_confirmation");

    /** To get list of customer pending payments data from server */
    public static final String GET_CUSTOMER_PENDING_PAYMENT_URL = url("/api/sme-sme-list/?sme_data_category=poc_invoices");

    /** To get list of pending payments data from server */
    public static final String GET_PENDING_PAYMENT_URL = url("/api/team-invoice-list/?invoice_data_category=pending_payments");

    /** To update Customer Pending Payment Due Date */
    public static final String PENDING_PAYMENT_UPDATE_DUE_DATE_URL = url("/api/sme-pending-payments-comments-update-sme/");

    /** To get Customer Pending Payment Comments */
    public static final String GET_PENDING_PAYMENT_COMMENTS_URL = url("/api/sme-pending-payments-comments-retrieve-sme/");

    /** To create Customer Pending Payment Comment */
    public static final String CREATE_PENDING_PAYMENT_COMMENT_URL = url("/api/sme-pending-payments-comments-create/");



}
