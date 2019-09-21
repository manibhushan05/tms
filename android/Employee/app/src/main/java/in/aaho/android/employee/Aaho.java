package in.aaho.android.employee;

import in.aaho.android.employee.common.Prefs;

/**
 * Created by aaho on 18/04/18.
 */


public class Aaho {

    // keys for shared preferences
    public static final String USERNAME_KEY = "username";
    public static final String PASSWORD_KEY = "password";
    public static final String FULLNAME_KEY = "full_name";
    public static final String LOGIN_STATUS_KEY = "login_status";

    public static final String FCM_TOKEN_KEY = "fcm_token";
    public static final String DEVICE_ID_KEY = "device_id";

    /** Token for app login and api access */
    public static final String TOKEN_KEY = "token_key";


    /** Employee id*/
    public static final String EMPLOYEE_ID_KEY = "emp_id";

    // App constants
    public static final String APP_SUPPORT_NUMBER = "+919969607841";

    public static final String ROLES_KEY = "roles";
    public static final String MY_NOTIFICATION_JSON_KEY = "my_notification_json";


    public static String getUsername() {
        return Prefs.get(USERNAME_KEY);
    }

    public static void setUsername(String uname) {
        Prefs.set(USERNAME_KEY,uname);
    }

    public static String getPassword() {
        return Prefs.get(PASSWORD_KEY);
    }

    public static boolean getLoginStatus() {
        return Prefs.get(LOGIN_STATUS_KEY, false);
    }

    public static String getFcmToken() {
        return Prefs.get(FCM_TOKEN_KEY);
    }

    public static void setFcmToken(String fcmToken) {
        Prefs.set(FCM_TOKEN_KEY,fcmToken);
    }


    public static String getDeviceId() {
        return Prefs.get(DEVICE_ID_KEY);
    }

    public static void setDeviceId(String deviceId) {
        Prefs.set(DEVICE_ID_KEY,deviceId);
    }

    public static String getToken() {
        return Prefs.get(TOKEN_KEY);
    }

    public static void setToken(String token) {
        Prefs.set(TOKEN_KEY,token);
    }

    public static String getEmployeeId() {
        return Prefs.get(EMPLOYEE_ID_KEY);
    }

    public static void setEmployeeId(String id) {
        Prefs.set(EMPLOYEE_ID_KEY,id);
    }

    public static String getUserFullname() {
        return Prefs.get(FULLNAME_KEY);
    }

    public static void setUserFullname(String userFullname) {
        Prefs.set(FULLNAME_KEY,userFullname);
    }

    public static String getRoles() {
        return Prefs.get(ROLES_KEY);
    }

    public static void setRoles(String roles) {
        Prefs.set(ROLES_KEY,roles);
    }

    public static String getMyNotificationJson() {
        return Prefs.get(MY_NOTIFICATION_JSON_KEY);
    }

    public static void setMyNotification(String notificationJson) {
        Prefs.set(MY_NOTIFICATION_JSON_KEY,notificationJson);
    }
}
