package in.aaho.android.customer.common;

import android.app.Application;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.Volley;

import org.acra.ACRA;
import org.acra.annotation.ReportsCrashes;
import org.acra.sender.HttpSender;

/**
 * Created by shobhit on 2/7/16.
 */

@ReportsCrashes(
        httpMethod = HttpSender.Method.PUT,
        reportType = HttpSender.Type.JSON,
        formUri = "http://aaho.in:5984/acra-aaho/_design/acra-storage/_update/report",
        formUriBasicAuthLogin = "shobhit",
        formUriBasicAuthPassword = "optimus"
)
public class MainApplication extends Application {

    private static MainApplication instance = null;
    private static SharedPreferences prefs = null;
    private static RequestQueue requestQueue = null;

    @Override
    public void onCreate() {
        super.onCreate();
        ACRA.init(this);
        instance = this;
        prefs = PreferenceManager.getDefaultSharedPreferences(this.getApplicationContext());
        Auth.setPersistentCookieStore();
        requestQueue = Volley.newRequestQueue(this.getApplicationContext());
    }

    public static SharedPreferences getPrefs() {
        return prefs;
    }

    public static MainApplication getInstance() {
        return instance;
    }

    public static void queueRequest(Request<?> request) {
        requestQueue.add(request);
    }
}