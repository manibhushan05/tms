package in.aaho.android.loads.common;

import java.net.CookieHandler;
import java.net.CookieManager;
import java.net.CookiePolicy;

/**
 * Created by aaho on 18/04/18.
 */

public class Auth {

    private static CookieManager cookieManager = null;

    public static void setPersistentCookieStore() {
        if (cookieManager == null) {
            cookieManager = new CookieManager(PersistentCookieStore.getInstance(), CookiePolicy.ACCEPT_ORIGINAL_SERVER);
        }
        CookieHandler.setDefault(cookieManager);
    }
}