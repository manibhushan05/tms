package in.aaho.android.aahocustomers.requests;

/**
 * Created by aaho on 18/04/18.
 */

public class Api {
    public static final String SERVER_URL = "https://aaho.in";
//    public static final String SERVER_URL = "https://dev.aaho.in/";
//    public static final String SERVER_URL = "http://stage.aaho.in/";
//    public static final String SERVER_URL = "http://10.0.2.2:8000";
//    public static final String SERVER_URL = "http://192.168.1.4:8080";

    // Api urls
    static final String LOGIN_URL = url("/api/customer/login/");
    static final String LOGIN_STATUS_URL = url("/api/customer/login-status/");
    static final String AWS_CRED_URL = url("/api/retrieve-aws-credentials/");
    static final String LOGOUT_URL = url("/api/customer/logout/");
    static final String APP_DATA_URL = url("/api/customer/app-data/");

    public static final String TEAM_TRIP_DETAILS = url("/api/fms/customer-trip-data/");
    static final String VEHICLE_DETAILS_URL = url("/api/fms/vehicle/");
    static final String VEHICLE_EDIT_URL = url("/api/fms/edit-vehicle/");

    static final String REQUIREMENT_SUBMIT_URL = url("/api/fms/new-requirement/");

    static final String EDIT_PASSWORD_URL = url("/api/customer/change-password/");
    static final String ACCOUNT_EDIT_URL = url("/api/fms/edit-account/");

    /** To get the mobile number from username/phone-number */
    public static final String FORGOT_PASSWORD_URL = url("/api/fms/get-phone-number/");
    public static final String RESET_PASSWORD_URL = url("/api/fms/forgot-password-reset/");

    public static final String CITY_DATA_URL = url("/utils/cities-data/");
    public static final String VEHICLE_TYPE_DATA_URL = url("/utils/vehicle-categories-data/");
    public static final String CUSTOMER_DATA_URL = url("/utils/customers-data/");
    public static final String AAHO_OFFICE_DATA_URL = url("/utils/aaho-office-data/");
    public static final String BOOKING_ARCHIVE_URL = url("/api/customer/customer-bookings-data/");
    public static final String UPLOAD_POD_URL = url("/api/fms/upload-pod/");
    static final String VEHICLE_LIST_URL = url("/api/fms/list-vehicles/");
    static final String DRIVER_LIST_URL = url("/api/fms/list-drivers/");
    //update-requirement
    static final String UPDATE_REQUIREMENT_URL = url("/api/fms/update-requirement/");

    public static final String GET_MY_LOADS = url("/api/fms/get-my-requirements/");

    static final String APP_VERSION_URL = url("/api/fms/app-version-check/");
    // Status strings
    public static final String STATUS_SUCCESS = "success";
    public static final String STATUS_ERROR = "error";

    public static final String TAG = "AAHO";

    private static String url(String path) {
        return SERVER_URL + path;
    }

    public static final String POST_FCM_TOKEN_URL = url("/notification/create-notification-device/");

    static final String DRIVER_EDIT_URL = url("/api/fms/edit-driver/");
    public static final String GET_AVL_LOADS = url("/api/fms/get-filtered-requirements/");
    static final String SEND_QUOTE_URL = url("/api/fms/send-quote/");
    static final String OWNER_EDIT_URL = url("/api/fms/edit-owner/");
    static final String SEND_DOCUMENT_EMAIL_URL = url("/api/fms/vehicle/send-document-email/");
    static final String DRIVER_DETAILS_URL = url("/api/fms/driver/");
    public static final String VEHICLE_GPS_DATA_URL = url("/api/fms/vehicle-gps-data/");
    static final String VEHICLE_TRACK_URL = url("/api/fms/track-vehicles/");
}
