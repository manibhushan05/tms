package in.aaho.android.driver.tracking;

import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;


public class SimplePositionProvider extends BasePositionProvider implements LocationListener {

    private String type;

    public SimplePositionProvider(Context context, PositionListener listener, String type) {
        super(context, listener);
        this.type = type;
        if (!this.type.equals(LocationManager.NETWORK_PROVIDER)) {
            this.type = LocationManager.GPS_PROVIDER;
        }
    }

    public void startUpdates() {
        try {
            requestUpdates(type, this);
        } catch (IllegalArgumentException e) {
            Log.w(TAG, e);
        }
    }

    public void stopUpdates() {
        removeUpdates(this);
    }

    @Override
    public void onLocationChanged(Location location) {
        updateLocation(location);
    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {
    }

    @Override
    public void onProviderEnabled(String provider) {
    }

    @Override
    public void onProviderDisabled(String provider) {
    }

}
