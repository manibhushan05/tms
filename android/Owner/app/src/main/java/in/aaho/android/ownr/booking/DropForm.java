package in.aaho.android.ownr.booking;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * Created by mani on 6/8/16.
 */
public class DropForm implements CityFieldForm {
    private City city;
    private String address;

    public static final String CITY_KEY = "city";
    public static final String ADDRESS_KEY = "address";

    @Override
    public City getCity() {
        return city;
    }

    @Override
    public void setCity(City city) {
        this.city = city;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = (address == null ? null : address.trim());
    }

    public JSONObject toJson() {
        JSONObject ret = new JSONObject();
        try {
            ret.put(CITY_KEY, city.toJson());
            ret.put(ADDRESS_KEY, address == null ? JSONObject.NULL : address);
        } catch (JSONException e) {
        }
        return ret;
    }

    public boolean isComplete() {
        return city != null && address != null && address.trim().length() != 0;
    }

    public boolean isAllBlank() {
        return city == null && (address == null || address.trim().length() == 0);
    }
}
