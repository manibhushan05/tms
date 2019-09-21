package in.aaho.android.ownr.requests;

/**
 * Created by mani on 2/7/16.
 * <p/>
 * Api Helper
 */
public class Api {
    public static final String SERVER_URL = "https://aaho.in";
//    public static final String SERVER_URL = "https://dev.aaho.in";
//    public static final String SERVER_URL = "https://stage.aaho.in";
//    public static final String SERVER_URL = "http://192.168.0.102:8000";

    // Status strings
    public static final String STATUS_SUCCESS = "success";
    public static final String STATUS_ERROR = "error";

    public static final String TAG = "AAHO";

    private static String url(String path) {
        return SERVER_URL + path;
    }

    // Api urls
    /*static final String LOGIN_URL = url("/api/fms/login/");*/
    static final String LOGIN_URL = url("/api/login/");

    static final String LOGIN_STATUS_URL = url("/api/fms/login-status/");
    static final String AWS_CRED_URL = url("/api/retrieve-aws-credentials/");

    static final String LOGOUT_URL = url("/api/logout/");
    /*static final String LOGOUT_URL = url("/api/fms/logout/");*/

    static final String APP_DATA_URL = url("/api/fms/app-data/");
    static final String USER_DATA_URL = url("/api/get-user-initial-data/");// new rest api

    static final String CATEGORY_DATA_URL = url("/api/usercategory-list/");// new rest api

    static final String VEHICLE_LIST_URL = url("/api/supplier-vehicle-list/");
//    static final String VEHICLE_LIST_URL = url("/api/owner-owner-vehicle-list/");
    /*static final String VEHICLE_LIST_URL = url("/api/fms/list-vehicles/");*/

    static final String AVAILABLE_LOADS_URL = url("/api/fms/available-loads/");
    static final String SEND_QUOTE_URL = url("/api/fms/send-quote/");

    static final String VEHICLE_TRACK_URL = url("/api/get-supplier-vehicles-gps-data/");
    /*static final String VEHICLE_TRACK_URL = url("/api/fms/track-vehicles/");*/

    static final String VEHICLE_DETAILS_URL = url("/api/supplier-vehicle-retrieve/");
//    static final String VEHICLE_DETAILS_URL = url("/api/owner-owner-vehicle-retrieve/");
    /*static final String VEHICLE_DETAILS_URL = url("/api/fms/vehicle/");*/

    static final String VEHICLE_EDIT_URL = url("/api/supplier-fms-vehicle-partial-update/");
//    static final String VEHICLE_EDIT_URL = url("/api/owner-fms-vehicle-partial-update/");
    /*static final String VEHICLE_EDIT_URL = url("/api/fms/edit-vehicle/");*/

    static final String VEHICLE_STATUS_EDIT_URL = url("/api/fms/edit-vehicle-status/");

    static final String DRIVER_LIST_URL = url("/api/supplier-supplier-driver-list/");
//    static final String DRIVER_LIST_URL = url("/api/driver-driver-list/");
    /*static final String DRIVER_LIST_URL = url("/api/fms/list-drivers/");*/

    static final String DRIVER_DETAILS_URL = url("/api/supplier-supplier-driver-retrieve/");
//    static final String DRIVER_DETAILS_URL = url("/api/driver-driver-retrieve/");
    /*static final String DRIVER_DETAILS_URL = url("/api/fms/driver/");*/

    static final String DRIVER_EDIT_URL = url("/api/supplier-driver-fms-partial-update/");
//    static final String DRIVER_EDIT_URL = url("/api/driver-fms-partial-update/");
    /*static final String DRIVER_EDIT_URL = url("/api/fms/edit-driver/");*/

    static final String OWNER_EDIT_URL = url("/api/fms/edit-owner/");

    static final String ACCOUNT_EDIT_URL = url("/api/utils-bank-create/");
    /*static final String ACCOUNT_EDIT_URL = url("/api/fms/edit-account/");*/

    static final String NEW_BOOKING_URL = url("/api/fms/new-booking/");
    static final String VENDOR_REQUEST_URL = url("/api/fms/vendor-request/");

    static final String EDIT_PROFILE_URL = url("/api/fms-user-profile-partial-update/");
    /*static final String EDIT_PROFILE_URL = url("/api/fms/edit-profile/");*/

    static final String EDIT_PASSWORD_URL = url("/api/change-password/");

    static final String ADD_VENDOR_URL = url("/api/fms/add-vendor/");
    static final String DELETE_VENDOR_URL = url("/api/fms/delete-vendor/");
    public static final String APP_LOGS_URL = url("/api/fms/store-app-logs/");

    static final String SEND_DOCUMENT_EMAIL_URL = url("/api/send-document-email/");
    /*static final String SEND_DOCUMENT_EMAIL_URL = url("/api/fms/vehicle/send-document-email/");*/

    //public static final String TRANSACTION_DATA_URL = url("/api/fms/booking-history-data/");

    public static final String BOOKING_ARCHIVE_URL = url("/api/team-manual-booking-list/");
    /*public static final String BOOKING_ARCHIVE_URL = url("/api/fms/bookings-data/");*/

    public static final String TEAM_TRIP_DETAILS = url("/api/manual-booking-retrieve/");
    /*public static final String TEAM_TRIP_DETAILS = url("/api/fms/trip-data/");*/

    public static final String VEHICLE_TRIP_DATA_URL = url("/api/fms/vehicle-trip-data/");
    public static final String MB_VEHICLE_TRIP_DATA_URL = url("/api/fms/mb-vehicle-trip-data/");
    static final String CANCEL_TRANSACTION_REQUEST = url("/customer-app/cancel-transaction-request");
    public static final String TRACKING_DATA_URL = url("/customer-app/");
    public static final String COMPLETE_TRIP_DETAILS = url("/api/fms/complete-trip-details/");
    public static final String QUOTATIONS = url("/customer-app/quotations");
    static final String VENDOR_RESPONSE = url("/customer-app/vendor-response");
    public static final String CHANGE_VENDOR_RESPONSE_STATUS = url("/customer-app/change-response-status");

    /** To get the mobile number from username/phone-number */
    public static final String FORGOT_PASSWORD_URL = url("/api/forgot-password/");
    /*public static final String FORGOT_PASSWORD_URL = url("/api/fms/get-phone-number/");*/

    public static final String VERIFY_OTP_URL = url("/api/verify-otp/"); // new Rest api

    public static final String RESET_PASSWORD_URL = url("/api/fms/forgot-password-reset/");

    public static final String UPLOAD_POD_URL = url("/api/file-upload-pod-file-create/");
//    public static final String UPLOAD_POD_URL = url("/api/upload-pod/");

    public static final String VEHICLE_GPS_DATA_URL = url("/api/get-vehicle-gps-data/");
    /*public static final String VEHICLE_GPS_DATA_URL = url("/api/fms/vehicle-gps-data/");*/

    // To get the city from api with search param
    public static final String CITY_DATA_URL = url("/utils/cities-data/");
    /** Get the notification count */
    public static final String NOTIFICATION_COUNT_URL = url("/api/fms/notification-count/");
    /** Get the notification details */
    public static final String NOTIFICATION_LIST_URL = url("/api/fms/notification-list/");

    /** To send the FCM token to server */
    public static final String POST_FCM_TOKEN_URL = url("/api/notification-mobile-device-create-update/");
    /*public static final String POST_FCM_TOKEN_URL = url("/notification/create-notification-device/");*/

    /** To get the available loads from server */
    public static final String GET_AVL_LOADS = url("/api/requirement-list-filter/");
    /*public static final String GET_AVL_LOADS = url("/api/fms/get-filtered-requirements/");*/

    public static final String APP_VERSION_URL = url("/api/mobile-app-version-check/");
    /*public static final String APP_VERSION_URL = url("/api/fms/app-version-check/");*/

    /** To get the POD pending data from server */
    public static final String GET_POD_PENDING_DATA = url("/api/team-manual-booking-list/?booking_data_category=pending_pod_bookings");

    /** To get the POD completed data from server */
    public static final String GET_POD_DELIVERED_DATA = url("/api/team-manual-booking-list/?booking_data_category=pending_supplier_payment_bookings");

    /** To get the complete booking data from server */
    public static final String GET_BOOKING_COMPLETED_DATA = url("/api/team-manual-booking-list/?booking_data_category=completed_supplier_payment_bookings");


    /* http://127.0.0.1:8000/api/notification-mobile-devices-list/

    For profile update, send userId
    *  http://127.0.0.1:8000/api/authentication-user-profile-partial-update/775/*/


    /*
    http://127.0.0.1:8000/api/team-manual-booking-list/?booking_data_category=pending_pod_bookings&vehicle_id=2252

    http://127.0.0.1:8000/api/team-manual-booking-list/?booking_data_category=pending_supplier_payment_bookings&vehicle_id=2252

    http://127.0.0.1:8000/api/team-manual-booking-list/?booking_data_category=completed_supplier_payment_bookings&vehicle_id=2252
    */

}
