
package in.aaho.android.driver.tracking;

import android.app.Application;

public class MainApplication extends Application {

    @Override
    public void onCreate() {
        super.onCreate();
        System.setProperty("http.keepAliveDuration", String.valueOf(30 * 60 * 1000));
    }

}
