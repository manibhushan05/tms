package in.aaho.android.ownr.vehicles;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.common.Utils;

/**
 * Created by shobhit on 14/10/16.
 */

public class VehicleDriver {
    public static final List<VehicleDriver> driverList = new ArrayList<>();

    public long id;
    public String name;
    public String phone;

    public VehicleDriver(long id, String name, String phone) {
        this.id = id;
        this.name = name;
        this.phone = phone;
    }

    public String title() {
        String t = "";
        if (name != null) {
            t = t + name.trim();
        }
        if (phone != null && !phone.trim().isEmpty()) {
            t = t + " (" + phone.trim() + ")";
        }
        return t.trim();
    }

    public JSONObject toJson() throws JSONException {
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("id", id);
        jsonObject.put("name", name);
        jsonObject.put("phone", phone);
        return jsonObject;
    }

    public static VehicleDriver fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }
        return new VehicleDriver(
                jsonObject.getLong("id"),
                Utils.get(jsonObject, "name"),
                Utils.get(jsonObject, "phone")
        );
    }

    public static void setData(JSONArray driversData) throws JSONException {
        driverList.clear();
        for (int i = 0; i < driversData.length(); i++) {
            JSONObject obj = driversData.getJSONObject(i);
            driverList.add(fromJson(obj));
        }
    }

    public static VehicleDriver copy(VehicleDriver other) {
        if (other == null) {
            return null;
        }
        return new VehicleDriver(other.id, other.name, other.phone);
    }
}
