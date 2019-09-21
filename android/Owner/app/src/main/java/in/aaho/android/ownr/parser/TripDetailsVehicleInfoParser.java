package in.aaho.android.ownr.parser;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.ownr.data.AllocatedVehicleData;

/**
 * Created by mani on 19/8/16.
 */
public class TripDetailsVehicleInfoParser {
    private JSONArray jsonArray;
    private ArrayList<AllocatedVehicleData> allocatedVehicleDataArrayList;

    public TripDetailsVehicleInfoParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }

    public ArrayList<AllocatedVehicleData> getAllocatedVehicleDataArrayList() {
        allocatedVehicleDataArrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                AllocatedVehicleData allocatedVehicleData = new AllocatedVehicleData();
                allocatedVehicleData.setTypeOfVehicle(jsonObject.getString("amount"));
                allocatedVehicleData.setVehicleNumber(jsonObject.getString("paid_to"));
                allocatedVehicleData.setDriverContactNumber(jsonObject.getString("paid_to"));
                allocatedVehicleData.setDriverLicenceNumber(jsonObject.getString("paid_to"));
                allocatedVehicleData.setDriverLicenceValidity(jsonObject.getString("paid_to"));
                allocatedVehicleData.setDriverName(jsonObject.getString("paid_to"));
                allocatedVehicleDataArrayList.add(allocatedVehicleData);

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return allocatedVehicleDataArrayList;
    }

    public void setAllocatedVehicleDataArrayList(ArrayList<AllocatedVehicleData> allocatedVehicleDataArrayList) {
        this.allocatedVehicleDataArrayList = allocatedVehicleDataArrayList;
    }
}
