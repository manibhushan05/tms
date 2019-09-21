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

public class VehicleOwner {
    public static final List<VehicleOwner> ownerList = new ArrayList<>();

    public long id;
    public String name;
    public String phone;

    public VehicleOwner(long id, String name, String phone) {
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

    public static VehicleOwner fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }
        return new VehicleOwner(
                jsonObject.getLong("id"),
                Utils.get(jsonObject, "name"),
                Utils.get(jsonObject, "phone")
        );
    }

    public static void setData(JSONArray ownersData) throws JSONException {
        ownerList.clear();
        for (int i = 0; i < ownersData.length(); i++) {
            JSONObject obj = ownersData.getJSONObject(i);
            ownerList.add(fromJson(obj));
        }
    }

    public static VehicleOwner copy(VehicleOwner other) {
        if (other == null) {
            return null;
        }
        return new VehicleOwner(other.id, other.name, other.phone);
    }
}
