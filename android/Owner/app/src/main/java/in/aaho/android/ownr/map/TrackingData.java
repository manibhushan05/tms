package in.aaho.android.ownr.map;

import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.maps.android.clustering.ClusterItem;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.drivers.BrokerDriver;
import in.aaho.android.ownr.vehicles.VehicleNumber;

/**
 * Created by mani on 30/11/16.
 */

public class TrackingData implements ClusterItem {

    private long vehicleId;
    private String vehicleNumber;
    private TimeLocation lastLocation;
    private BrokerDriver driver;
    private String status;
    private MarkerOptions marker;
    private double bearing;

    private TrackingData(long vehicleId, String vehicleNumber, String status, TimeLocation lastLocation, BrokerDriver driver, double bearing) {
        this.vehicleId = vehicleId;
        this.vehicleNumber = VehicleNumber.displayFormat(vehicleNumber);
        this.status = status;
        this.lastLocation = lastLocation;
        this.driver = driver;
        this.bearing = bearing;
    }


    private static TrackingData fromJson(JSONObject obj) throws JSONException {
        if (obj == null) {
            return null;
        }
        return new TrackingData(
                obj.getLong("vehicle_id"),
                obj.getString("vehicle_number"),
                obj.getString("vehicle_status"),
                TimeLocation.fromJson(obj.getJSONObject("location")),
                BrokerDriver.fromJson(obj.getJSONObject("driver")),
                obj.getDouble("bearing")
        );
    }

    public double getBearing() {
        return bearing;
    }

    public BrokerDriver getDriver() {
        return driver;
    }

    public TimeLocation getLastLocation() {
        return lastLocation;
    }

    public long getVehicleId() {
        return vehicleId;
    }

    public String getStatus() {
        return status;
    }

    public String getVehicleNumber() {
        return VehicleNumber.displayFormat(vehicleNumber);
    }

    public String getVehicleNumberSearchString() {
        return VehicleNumber.compareFormat(vehicleNumber);
    }

    public MarkerOptions getMarker() {
        if (marker == null) {
            marker = new MarkerOptions();
            marker.position(latlng());
            marker.title(getVehicleNumber());
            marker.snippet(status);
            marker.icon(MapMarkers.getSmallMarker());
            marker.anchor(0.5f, 0.5f);
            marker.rotation((float) bearing);
        }
        return marker;
    }

    public MarkerOptions getMarker(MarkerOptions marker) {
        if (marker == null) {
            marker = new MarkerOptions();
        }
        marker.position(latlng());
        marker.title(getVehicleNumber());
        marker.snippet(status);
        marker.icon(MapMarkers.getSmallMarker());
        marker.anchor(0.5f, 0.5f);
        marker.rotation((float) bearing);
        return marker;
    }

    public static List<TrackingData> fromJson(JSONArray jsonArray) throws JSONException {
        List<TrackingData> data = new ArrayList<>();
        if (Utils.not(jsonArray)) {
            return data;
        }
        for (int i = 0; i < jsonArray.length(); i++) {
            data.add(fromJson(jsonArray.getJSONObject(i)));
        }
        return data;
    }

    public String getAutocompleteText() {
        return getVehicleNumber() + " - " + status;
    }

    public LatLng latlng() {
        if (lastLocation == null) {
            return null;
        }
        return lastLocation.latlng();
    }

    @Override
    public LatLng getPosition() {
        return latlng();
    }
}
