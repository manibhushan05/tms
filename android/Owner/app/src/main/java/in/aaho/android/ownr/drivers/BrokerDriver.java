package in.aaho.android.ownr.drivers;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.common.Utils;

/**
 * Created by mani on 6/8/16.
 */
public class BrokerDriver {

    private long id;
    private String name;
    private String phone;

    public static final String ID_KEY = "id";
    public static final String NAME_KEY = "name";
    public static final String PHONE_KEY = "phone";


    public BrokerDriver(long id, String name, String phone) {
        this.id = id;
        this.name = name;
        this.phone = phone;
    }

    public long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getPhone() {
        return phone;
    }

    public void setId(long id) {
        this.id = id;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public static BrokerDriver fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }
        return new BrokerDriver(
                jsonObject.getLong(ID_KEY),
                Utils.get(jsonObject, NAME_KEY),
                Utils.get(jsonObject, PHONE_KEY)
        );
    }

    public static List<BrokerDriver> fromJson(JSONArray jsonArray) throws JSONException {
        List<BrokerDriver> drivers = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            BrokerDriver driver = fromJson(obj);
            drivers.add(driver);
        }
        return drivers;
    }
}
