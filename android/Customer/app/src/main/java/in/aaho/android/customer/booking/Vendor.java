package in.aaho.android.customer.booking;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import in.aaho.android.customer.common.Prefs;

/**
 * Created by shobhit on 6/8/16.
 */
public class Vendor {
    private static Map<Long, Vendor> vendorMap = new HashMap<>();
    private static List<Vendor> vendors = new ArrayList<>();

    public long id;
    public String name;
    public String phone;
    private boolean selected = false;

    public static final String ID_KEY = "id";
    public static final String NAME_KEY = "name";
    public static final String PHONE_KEY = "phone";
    public static final String SELECTED_KEY = "selected";

    public Vendor(long id, String name, String phone) {
        this.id = id;
        this.name = name;
        this.phone = phone;
        vendorMap.put(this.id, this);
        vendors.add(this);
    }

    public static void clear() {
        vendorMap.clear();
        vendors.clear();
    }

    public long getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public static List<Vendor> getAll() {
        return vendors;
    }

    public static boolean isEmpty() {
        return vendors.isEmpty();
    }

    public static void createFromJson(JSONArray jsonArray) throws JSONException {
        clear();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject cityObj = jsonArray.getJSONObject(i);
            new Vendor(cityObj.getLong("id"), cityObj.getString("name"), cityObj.getString("phone"));
        }
        Prefs.set("vendor_data", jsonArray.toString());
    }

    @Override
    public String toString() {
        return name;
    }

    public JSONObject toJson() {
        JSONObject ret = new JSONObject();
        try {
            ret.put(ID_KEY, id);
            ret.put(NAME_KEY, name == null ? JSONObject.NULL : name);
            ret.put(PHONE_KEY, phone == null ? JSONObject.NULL : phone);
            ret.put(SELECTED_KEY, selected);
        } catch (JSONException e) {
        }
        return ret;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public boolean isSelected() {
        return selected;
    }

    public void setSelected(boolean selected) {
        this.selected = selected;
    }
}
