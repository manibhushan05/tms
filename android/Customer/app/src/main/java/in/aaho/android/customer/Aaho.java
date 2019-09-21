package in.aaho.android.customer;

import in.aaho.android.customer.common.Prefs;

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
}
