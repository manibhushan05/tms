package in.aaho.android.customer.parser;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.customer.data.AllocatedVehicleData;

/**
 * Created by mani on 19/8/16.
 */
public class AllocatedVehicleParser {
    private JSONArray jsonArray;
    private ArrayList<AllocatedVehicleData> allocatedVehicleDataArrayList;

    public AllocatedVehicleParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }

    public ArrayList<AllocatedVehicleData> getAllocatedVehicleDataArrayList() {
        allocatedVehicleDataArrayList = new ArrayList<>();
        for(int i = 0; i < jsonArray.length();i++){
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                AllocatedVehicleData allocatedVehicleData = new AllocatedVehicleData();
                allocatedVehicleData.setTypeOfVehicle(jsonObject.getString("vehicle_type"));
                allocatedVehicleData.setVehicleNumber(jsonObject.getString("vehicle_number"));
                allocatedVehicleData.setDriverContactNumber(jsonObject.getString("driver_phone"));
                allocatedVehicleData.setDriverLicenceNumber(jsonObject.getString("driving_licence"));
                allocatedVehicleData.setDriverName(jsonObject.getString("driver_name"));
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
