package in.aaho.android.aahocustomers.booking;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import in.aaho.android.aahocustomers.common.Prefs;

/**
 * Created by mani on 9/8/16.
 */
public class VehicleCategory {
    public static final VehicleCategory EMPTY_VEHICLE_SPINNER = new VehicleCategory("Select Vehicle Type");
    private static Map<Long, VehicleCategory> vehicleMap = new HashMap<>();
    private static List<VehicleCategory> vehicleCategories = new ArrayList<>();

    public static final String ID_KEY = "id";
    public static final String TYPE_KEY = "type";
    public static final String CAPACITY_KEY = "capacity";

    public long id;
    public String name;
    public String capacity;

    private VehicleCategory(String name) {
        this.id = -1;
        this.name = name;
        this.capacity = null;
    }

    private VehicleCategory(long id, String name, String capacity) {
        this.id = id;
        this.name = name;
        this.capacity = capacity;
        vehicleMap.put(this.id, this);
        vehicleCategories.add(this);
    }

    public static void clear() {
        vehicleMap.clear();
        vehicleCategories.clear();
    }

    public static VehicleCategory get(long id) {
        return vehicleMap.get(id);
    }

    public static boolean has(long id) {
        return vehicleMap.containsKey(id);
    }

    public static List<VehicleCategory> getAll() {
        return vehicleCategories;
    }

    public static boolean isEmpty() {
        return vehicleCategories.isEmpty();
    }

    public static void createFromJson(JSONArray jsonArray) throws JSONException {
        clear();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            new VehicleCategory(obj.getLong("id"), obj.getString("vehicle_type"), obj.getString("capacity"));
        }
        Prefs.set("vehicle_data", jsonArray.toString());
    }

    public static void add(JSONObject obj) {
        if (obj == null) {
            return;
        }
        try {
            new VehicleCategory(obj.getLong("id"), obj.getString("vehicle_type"), obj.getString("capacity"));
        } catch (JSONException e) {
            return;
        }
    }

    public String getFullName() {
        if (name == null && capacity == null) {
            return "";
        } else if (name != null && capacity != null) {
            return name + ", " + capacity;
        } else if (capacity == null) {
            return name;
        } else {
            return capacity;
        }

    }

    @Override
    public String toString() {
        return getFullName();
    }

    public JSONObject toJson() {
        JSONObject ret = new JSONObject();
        try {
            ret.put(ID_KEY, id);
            ret.put(TYPE_KEY, name);
            ret.put(CAPACITY_KEY, capacity);
        } catch (JSONException e) {
        }
        return ret;
    }
}
