package in.aaho.android.ownr;

import in.aaho.android.ownr.common.Prefs;

/**
 * Created by shobhit on 30/6/16.
 *
 * Project helper sort of thingy
 *
 */

public class Aaho {

    // keys for shared preferences
    public static final String USERNAME_KEY = "username";
    public static final String PASSWORD_KEY = "password";
    public static final String LOGIN_STATUS_KEY = "login_status";

    public static final String FCM_TOKEN_KEY = "fcm_token";
    public static final String DEVICE_ID_KEY = "device_id";

    /** Token for app login and api access */
    public static final String TOKEN_KEY = "token_key";

    // App constants
    public static final String APP_SUPPORT_NUMBER = "+919969607841";


    public static String getUsername() {
        return Prefs.get(USERNAME_KEY);
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
}
