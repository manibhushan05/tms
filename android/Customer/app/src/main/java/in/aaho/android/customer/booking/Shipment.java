package in.aaho.android.customer.booking;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * Created by shobhit on 6/8/16.
 */
public class Shipment {

    private long id;
    private String truck;
    private int count = 0;

    public static final String ID_KEY = "id";
    public static final String TRUCK_KEY = "name";
    public static final String COUNT_KEY = "count";

    public Shipment(long id, String truck) {
        this.id = id;
        this.truck = truck;
    }

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public String getTruck() {
        return truck;
    }

    public void setTruck(String truck) {
        this.truck = truck;
    }

    public int getCount() {
        return count;
    }

    public void setCount(int count) {
        this.count = count;
    }

    public JSONObject toJson() {
        JSONObject ret = new JSONObject();
        try {
            ret.put(ID_KEY, id);
            ret.put(TRUCK_KEY, truck == null ? JSONObject.NULL : truck);
            ret.put(COUNT_KEY, count);
        } catch (JSONException e) {
        }
        return ret;
    }
}
