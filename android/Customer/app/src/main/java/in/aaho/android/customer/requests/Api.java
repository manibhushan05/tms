package in.aaho.android.customer.requests;

import java.net.CookieManager;

/**
 * Created by shobhit on 2/7/16.
 * <p/>
 * Api Helper
 */
public class Api {
//    public static final String SERVER_URL = "https://aaho.in";
    public static final String SERVER_URL = "https://dev.aaho.in/";
//    public static final String SERVER_URL = "http://54.169.122.109:8000";
//    public static final String SERVER_URL = "http://192.168.1.4:8080";
//    public static final String SERVER_URL = "http://192.168.0.8:8080";
    // public static final String SERVER_URL = "http://192.168.43.5:8080";

    // Api urls
    public static final String LOGIN_URL = url("/api/customer/login/");
    public static final String LOGIN_STATUS_URL = url("/api/customer/login-status/");
    public static final String LOGOUT_URL = url("/api/customer/logout/");
    public static final String APP_DATA_URL = url("/api/customer/app-data/");
    public static final String NEW_BOOKING_URL = url("/api/customer/new-booking/");
    public static final String VENDOR_REQUEST_URL = url("/api/customer/vendor-request/");
    public static final String EDIT_PROFILE_URL = url("/api/customer/edit-profile/");
    public static final String EDIT_PASSWORD_URL = url("/api/customer/change-password/");
    public static final String ADD_VENDOR_URL = url("/api/customer/add-vendor/");
    public static final String DELETE_VENDOR_URL = url("/api/customer/delete-vendor/");
    public static final String APP_LOGS_URL = url("/api/customer/store-app-logs/");

    // Api urls
    public static final String TRANSACTION_DATA_URL = url("/customer-app/transactions");
    public static final String CANCEL_TRANSACTION_REQUEST = url("/customer-app/cancel-transaction-request");
    public static final String TRACKING_DATA_URL = url("/customer-app/");
    public static final String COMPLETE_TRIP_DETAILS = url("/customer-app/complete-trip-details");
    public static final String QUOTATIONS = url("/customer-app/quotations");
    public static final String VENDOR_RESPONSE = url("/customer-app/vendor-response");
    public static final String CHANGE_VENDOR_RESPONSE_STATUS = url("/customer-app/change-response-status");


    // Status strings
    public static final String STATUS_SUCCESS = "success";
    public static final String STATUS_ERROR = "error";

    public static final String TAG = "AAHO";

    public static String url(String path) {
        return SERVER_URL + path;
    }

    private static CookieManager cookieManager = null;

}
