package in.aaho.android.aahocustomers;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.Serializable;
import java.util.ArrayList;

/**
 * Created by mani on 28/3/18.
 */

public class VehicleGpsData implements Serializable {

    private String latitude = "";
    private String longitude = "";
    private String timestamp = "";

    public String getLatitude() {
        return latitude;
    }

    public void setLatitude(String latitude) {
        this.latitude = latitude;
    }

    public String getLongitude() {
        return longitude;
    }

    public void setLongitude(String longitude) {
        this.longitude = longitude;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    public static ArrayList<VehicleGpsData> getListFromJsonArray(JSONArray jsonArray) {
        ArrayList<VehicleGpsData> vehicleGpsDataArrayList = new ArrayList<>();
        if(jsonArray !=null && jsonArray.length() != 0) {
            JSONObject jsonObject;
            VehicleGpsData vehicleGpsData;
            for (int i = 0; i < jsonArray.length(); i++) {
                try {
                    jsonObject = (JSONObject) jsonArray.get(i);
                    if(jsonObject != null) {
                        vehicleGpsData = new VehicleGpsData();
                        vehicleGpsData.setLatitude(jsonObject.getString("latitude"));
                        vehicleGpsData.setLongitude(jsonObject.getString("longitude"));
                        vehicleGpsData.setTimestamp(jsonObject.getString("timestamp"));
                        vehicleGpsDataArrayList.add(vehicleGpsData);
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        }
        return vehicleGpsDataArrayList;
    }
}
