package in.aaho.android.customer.common;

import com.google.gson.Gson;

import java.net.CookieManager;
import java.net.CookieStore;
import java.net.HttpCookie;
import java.net.URI;
import java.util.List;


public class PersistentCookieStore implements CookieStore {

    private final static String PREF_DEFAULT_STRING = "";

    private final static String PREFS_NAME = PersistentCookieStore.class.getName();

    private final static String PREF_SESSION_COOKIE = "session_cookie";

    private final static String KEY_SESSION_COOKIE = "sessionid";

    private CookieStore mStore;

    private static PersistentCookieStore instance = null;

    public static PersistentCookieStore getInstance() {
        if (instance == null) {
            instance = new PersistentCookieStore();
        }
        return instance;
    }

    private PersistentCookieStore() {
        // get the default in memory store and if there is a cookie stored in shared preferences,
        // we added it to the cookie store
        mStore = new CookieManager().getCookieStore();

        String jsonSessionCookie = getJsonCookieString(PREF_SESSION_COOKIE);
        if (!jsonSessionCookie.equals(PREF_DEFAULT_STRING)) {
            Gson gson = new Gson();
            HttpCookie cookie = gson.fromJson(jsonSessionCookie, HttpCookie.class);
            mStore.add(URI.create(cookie.getDomain()), cookie);
        }
    }

    @Override
    public void add(URI uri, HttpCookie cookie) {
        if (cookie.getName().equals(KEY_SESSION_COOKIE)) {
            // if the cookie that the cookie store attempt to add is a session cookie,
            // we remove the older cookie and save the new one in shared preferences
            remove(URI.create(cookie.getDomain()), cookie);
            saveCookie(PREF_SESSION_COOKIE, cookie);

        }

        mStore.add(URI.create(cookie.getDomain()), cookie);
    }

    @Override
    public List<HttpCookie> get(URI uri) {
        return mStore.get(uri);
    }

    @Override
    public List<HttpCookie> getCookies() {
        return mStore.getCookies();
    }

    @Override
    public List<URI> getURIs() {
        return mStore.getURIs();
    }

    @Override
    public boolean remove(URI uri, HttpCookie cookie) {
        return mStore.remove(uri, cookie);
    }

    @Override
    public boolean removeAll() {
        return mStore.removeAll();
    }

    private String getJsonCookieString(String prefKey) {
        return Prefs.get(prefKey, PREF_DEFAULT_STRING);
    }

    private void saveCookie(String prefKey, HttpCookie cookie) {
        Gson gson = new Gson();
        String jsonCookieString = gson.toJson(cookie);
        Prefs.set(prefKey, jsonCookieString);
    }

}