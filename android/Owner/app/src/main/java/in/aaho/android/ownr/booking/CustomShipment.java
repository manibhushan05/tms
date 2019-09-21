package in.aaho.android.ownr.booking;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * Created by mani on 6/8/16.
 */
public class CustomShipment {
    private String name;
    private String capacity;
    private int count = 0;

    public static final String NAME_KEY = "name";
    public static final String CAPACITY_KEY = "capacity";
    public static final String COUNT_KEY = "count";


    public int getCount() {
        return count;
    }

    public void setCount(int count) {
        this.count = count;
    }

    public JSONObject toJson() {
        JSONObject ret = new JSONObject();
        try {
            ret.put(NAME_KEY, name == null ? JSONObject.NULL : name);
            ret.put(CAPACITY_KEY, capacity == null ? JSONObject.NULL : capacity);
            ret.put(COUNT_KEY, count);
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

    public void setCapacity(String capacity) {
        this.capacity = capacity;
    }

    public String getCapacity() {
        return capacity;
    }

    public boolean isNotSet() {
        return hasNoName() || hasNoCapacity();
    }

    public boolean hasNoName() {
        return name == null || name.trim().length() == 0;
    }

    public boolean hasNoCapacity() {
        return capacity == null || capacity.trim().length() == 0;
    }

    public boolean isComplete() {
        return !isNotSet() && count > 0;
    }

    public String getTruck() {
        if (isNotSet()) {
            return "";
        } else {
            return name + ", " + capacity;
        }
    }
}
