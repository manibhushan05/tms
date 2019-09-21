package in.aaho.android.aahocustomers.map;

import android.util.Log;

import com.google.android.gms.maps.GoogleMap;

/**
 * Created by mani on 1/12/16.
 */

public class MapHelper {
    // map related can be accessed in parallel
    private GoogleMap googleMap = null;
    private Action pendingAction = null;

    private static final Object lock = new Object();

    public void perform(Action action) {
        if (action == null) {
            Log.e("MapHelper.perform", "action == null");
            return;
        }
        GoogleMap map;
        synchronized (lock) {
            if (googleMap == null) {
                Log.e("MapHelper.perform", "googleMap == null");
                pendingAction = action;
                return;
            } else {
                map = googleMap;
            }
        }
        action.onMapReady(map);
    }

    public void setGoogleMap(GoogleMap map) {
        Log.e("MapHelper.setGoogleMap", "called");
        Action action = null;
        synchronized (lock) {
            this.googleMap = map;
            if (pendingAction != null) {
                Log.e("MapHelper.setGoogleMap", "pendingAction != null");
                action = pendingAction;
                pendingAction = null;
            }
        }
        if (action != null) {
            Log.e("MapHelper.setGoogleMap", "action != null");
            action.onMapReady(map);
        }
    }

    interface Action {
        void onMapReady(GoogleMap map);
    }
}
