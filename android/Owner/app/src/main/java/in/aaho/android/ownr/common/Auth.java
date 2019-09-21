package in.aaho.android.ownr.common;

import java.net.CookieHandler;
import java.net.CookieManager;
import java.net.CookiePolicy;

/**
 * Created by mani on 2/7/16.
 * <p/>
 * Auth Helper
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
