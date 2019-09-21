package in.aaho.android.loads.requests;

/**
 * Created by aaho on 18/04/18.
 */

public class Api {
//    public static final String SERVER_URL = "https://aaho.in";
<<<<<<< Updated upstream
//    public static final String SERVER_URL = "https://dev.aaho.in/";
    public static final String SERVER_URL = "http://stage.aaho.in/";
=======
    public static final String SERVER_URL = "https://dev.aaho.in/";
//    public static final String SERVER_URL = "http://stage.aaho.in/";
>>>>>>> Stashed changes
//    public static final String SERVER_URL = "http://10.0.2.2:8000";
//    public static final String SERVER_URL = "http://192.168.1.10:8080";

    // Api urls
    static final String LOGIN_URL = url("/api/fms/login_employees/");
    static final String LOGIN_STATUS_URL = url("/api/fms/login-status/");
    static final String LOGOUT_URL = url("/api/fms/logout/");
    static final String APP_DATA_URL = url("/api/fms/app-data/");

    static final String REQUIREMENT_SUBMIT_URL = url("/api/fms/new-requirement/");

    static final String EDIT_PASSWORD_URL = url("/api/fms/change-password/");

    /** To get the mobile number from username/phone-number */
    public static final String FORGOT_PASSWORD_URL = url("/api/fms/get-phone-number/");
    public static final String RESET_PASSWORD_URL = url("/api/fms/forgot-password-reset/");

    public static final String CITY_DATA_URL = url("/utils/cities-data/");
    public static final String VEHICLE_TYPE_DATA_URL = url("/utils/vehicle-categories-data/");
    public static final String CUSTOMER_DATA_URL = url("/utils/customers-data/");
    public static final String AAHO_OFFICE_DATA_URL = url("/utils/aaho-office-data/");

    //update-requirement
    static final String UPDATE_REQUIREMENT_URL = url("/api/fms/update-requirement/");

    // Status strings
    public static final String STATUS_SUCCESS = "success";
    public static final String STATUS_ERROR = "error";

    public static final String TAG = "AAHO";

    private static String url(String path) {
        return SERVER_URL + path;
    }


    // Added by Suraj
    /** To get the available loads from server */
    public static final String GET_AVL_LOADS = url("/api/fms/get-filtered-requirements/");
    public static final String GET_MY_LOADS = url("/api/fms/get-my-requirements/");

    static final String APP_VERSION_URL = url("/api/fms/app-version-check/");
    public static final String POST_FCM_TOKEN_URL = url("/notification/create-notification-device/");

}
