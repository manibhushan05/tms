package in.aaho.android.driver.tracking;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.BatteryManager;
import android.support.v4.app.ActivityCompat;
import android.util.Log;

import in.aaho.android.driver.Intervals;


public abstract class BasePositionProvider implements PositionProvider {

    protected static final String TAG = BasePositionProvider.class.getSimpleName();

    private final PositionListener listener;

    protected final Context context;
    protected final LocationManager locationManager;

    private long lastUpdateTime;

    protected int period = Intervals.UPDATE_INTERVAL;

    public BasePositionProvider(Context context, PositionListener listener) {
        this.context = context;
        this.listener = listener;

        locationManager = (LocationManager) context.getSystemService(Context.LOCATION_SERVICE);
    }

    protected void updateLocation(Location location) {
        if (location == null) {
            Log.e(TAG, "updateLocation(): location=null, return");
            return;
        }
        if (location.getTime() - lastUpdateTime <= 0) {
            Log.e(TAG, "updateLocation(): old location, return");
            return;
        }
        lastUpdateTime = location.getTime();
        listener.onPositionUpdate(new Position(location, getBatteryLevel(), MemInfo.get(context)));
    }

    private double getBatteryLevel() {
        Intent batteryIntent = context.registerReceiver(null, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
        if (batteryIntent == null) {
            return 0;
        }
        int level = batteryIntent.getIntExtra(BatteryManager.EXTRA_LEVEL, 0);
        int scale = batteryIntent.getIntExtra(BatteryManager.EXTRA_SCALE, 1);
        return (level * 100.0) / scale;
    }

    protected PositionListener getListener() {
        return listener;
    }


    protected void requestUpdates(String provider, LocationListener locationListener) {
        if (ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
            ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            StatusDialog.addMessage("Permissions not available");
            return;
        }
        locationManager.requestLocationUpdates(provider, period, 0, locationListener);
    }

    protected void removeUpdates(LocationListener locationListener) {
        if (ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
            ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            StatusDialog.addMessage("Permissions not available");
            return;
        }
        locationManager.removeUpdates(locationListener);
    }
}
