package in.aaho.android.driver.tracking;


import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.IntentSender;
import android.content.pm.PackageManager;
import android.location.Location;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.ActivityCompat;
import android.util.Log;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.common.api.PendingResult;
import com.google.android.gms.common.api.ResultCallback;
import com.google.android.gms.common.api.Status;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.location.LocationSettingsRequest;
import com.google.android.gms.location.LocationSettingsResult;
import com.google.android.gms.location.LocationSettingsStates;
import com.google.android.gms.location.LocationSettingsStatusCodes;

import java.lang.ref.WeakReference;

import in.aaho.android.driver.DriverActivity;
import in.aaho.android.driver.Intervals;
import in.aaho.android.driver.R;


public class FusedPositionProvider extends BasePositionProvider implements GoogleApiClient.ConnectionCallbacks,
        GoogleApiClient.OnConnectionFailedListener, LocationListener {

    private static final String TAG = FusedPositionProvider.class.getSimpleName();

    private static int DISPLACEMENT = 0; // 0 meters so we get updates even when stationary

    private GoogleApiClient googleApiClient = null;
    private LocationRequest locationRequest = null;

    private long lastUpdateTime;

    private MixedPositionProvider backupProvider;

    private static WeakReference<FusedPositionProvider> instanceRef;

    public enum State {
        DISCONNECTED,
        SUSPENDED,
        CONNECTED
    }

    private State state = State.DISCONNECTED;

    public FusedPositionProvider(Context context, PositionListener listener) {
        super(context, listener);

        lastUpdateTime = System.currentTimeMillis();
        locationRequest = newLocationRequest();
        googleApiClient = newGoogleApiClient();

        backupProvider = new MixedPositionProvider(context, new BackupPositionListener());
        instanceRef = new WeakReference<>(this);
        resolveLocationSetting();
    }

    public State getState() {
        return state;
    }

    public static FusedPositionProvider getInstance() {
        return instanceRef == null ? null : instanceRef.get();
    }

    public void resolveLocationSetting() {
        DriverActivity driverActivity = DriverActivity.getInstance();
        if (driverActivity != null && driverActivity.isTaskRoot()) {
            LocationSettingsRequest.Builder builder = new LocationSettingsRequest.Builder()
                    .addLocationRequest(locationRequest);
            builder.setAlwaysShow(true); //this is the key ingredient

            PendingResult<LocationSettingsResult> result =
                    LocationServices.SettingsApi.checkLocationSettings(googleApiClient, builder.build());
            result.setResultCallback(new LocationSettingCallback(driverActivity));
        } else {
            DriverActivity.resolvingLocationSetting = false;
        }
    }

    private class BackupPositionListener implements PositionListener {

        @Override
        public void onPositionUpdate(Position position) {
            getListener().onPositionUpdate(position);
            startUpdates();
        }
    }

    @Override
    public void startUpdates() {

        if (System.currentTimeMillis() - lastUpdateTime >= Intervals.MAX_UPDATE_DELAY) {
            googleApiClient.disconnect(); // disconnect and connect again
            googleApiClient.connect();
            return;
        }

        if (googleApiClient.isConnected()) {
            Log.e(TAG, "startUpdates(): googleApiClient.isConnected() = true, requesting location updates");
            requestFusedUpdates();
        } else {
            Log.e(TAG, "startUpdates(): googleApiClient.isConnected() = false, calling connect");
            googleApiClient.connect();
        }

    }

    private void requestFusedUpdates() {
        if (ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
            ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            StatusDialog.addMessage("Permissions not available");
            return;
        }
        LocationServices.FusedLocationApi.requestLocationUpdates(googleApiClient, locationRequest, this);
    }

    private GoogleApiClient newGoogleApiClient() {
        GoogleApiClient mGoogleApiClient = new GoogleApiClient.Builder(context)
                .addConnectionCallbacks(this)
                .addOnConnectionFailedListener(this)
                .addApi(LocationServices.API)
                .setAccountName(String.valueOf(R.string.google_maps_key)).build();
        if (mGoogleApiClient == null) {
            Log.e(TAG, "newGoogleApiClient(): ERROR! could not create new api client");
        }
        return mGoogleApiClient;
    }

    private LocationRequest newLocationRequest() {
        LocationRequest locRequest = new LocationRequest();
        locRequest.setInterval(Intervals.UPDATE_INTERVAL);
        locRequest.setFastestInterval(Intervals.FASTEST_INTERVAL);
        locRequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);
        locRequest.setSmallestDisplacement(DISPLACEMENT);
        return locRequest;
    }

    @Override
    public void stopUpdates() {
        Log.e(TAG, "stopUpdates()");
        if (googleApiClient != null && googleApiClient.isConnected()) {
            Log.e(TAG, "stopUpdates(): removeLocationUpdates called");
            LocationServices.FusedLocationApi.removeLocationUpdates(googleApiClient, this);
            googleApiClient.disconnect();
        }
        backupProvider.stopUpdates();
    }


    @Override
    public void onConnected(@Nullable Bundle bundle) {
        Log.e(TAG, "onConnected()");
        state = State.CONNECTED;
        backupProvider.stopUpdates();
        requestFusedUpdates();
    }

    @Override
    public void onConnectionSuspended(int i) {
        Log.e(TAG, "onConnectionSuspended()");
        state = State.SUSPENDED;
        backupProvider.startUpdates();
    }

    @Override
    public void onConnectionFailed(@NonNull ConnectionResult connectionResult) {
        Log.e(TAG, "onConnectionFailed(): errorCode = " + connectionResult.getErrorCode());
        state = State.DISCONNECTED;
        backupProvider.startUpdates();
    }

    @Override
    public void onLocationChanged(Location location) {
        Log.i(TAG, "onLocationChanged(): provider location");
        lastUpdateTime = System.currentTimeMillis();
        backupProvider.stopUpdates();
        updateLocation(location);
    }

    private static class LocationSettingCallback implements ResultCallback<LocationSettingsResult> {

        private Activity activity;

        public LocationSettingCallback(Activity activity) {
            this.activity = activity;
        }

        @Override
        public void onResult(LocationSettingsResult result) {
            final Status status = result.getStatus();
            final LocationSettingsStates state = result.getLocationSettingsStates();
            switch (status.getStatusCode()) {
                case LocationSettingsStatusCodes.SUCCESS:
                    // All location settings are satisfied. The client can initialize location requests here.
                    DriverActivity.resolvingLocationSetting = false;
                    break;
                case LocationSettingsStatusCodes.RESOLUTION_REQUIRED:
                    // Location settings are not satisfied. But could be fixed by showing the user a dialog.
                    try {
                        // Show the dialog by calling startResolutionForResult() and check the result in onActivityResult().
                        status.startResolutionForResult(activity, DriverActivity.GPS_SETTINGS_REQUEST);
                    } catch (IntentSender.SendIntentException e) {
                        // Ignore the error.
                        DriverActivity.resolvingLocationSetting = false;
                    }
                    break;
                case LocationSettingsStatusCodes.SETTINGS_CHANGE_UNAVAILABLE:
                    // Location settings are not satisfied. However, we have no way to fix the settings so we won't show the dialog.
                    DriverActivity.resolvingLocationSetting = false;
                    break;
                default:
                    DriverActivity.resolvingLocationSetting = false;
                    break;
            }
        }
    }
}
