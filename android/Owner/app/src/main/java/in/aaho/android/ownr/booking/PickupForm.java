package in.aaho.android.ownr.booking;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Date;

/**
 * Created by mani on 6/8/16.
 */
public class PickupForm implements CityFieldForm {
    private City city;
    private String address;
    private Date datetime;

    public static final String CITY_KEY = "city";
    public static final String ADDRESS_KEY = "address";
    // public static final String DATETIME_KEY = "datetime";

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

    public Date getDatetime() {
        return datetime;
    }

    public void setDatetime(Date datetime) {
        this.datetime = datetime;
    }

    public String toString() {
        return "PickupForm[city='" + String.valueOf(city) + "', address='" + String.valueOf(address) + "']";
    }


    public JSONObject toJson() {
        JSONObject ret = new JSONObject();
        try {
            ret.put(CITY_KEY, city.toJson());
            ret.put(ADDRESS_KEY, address == null ? JSONObject.NULL : address);
            // ret.put(DATETIME_KEY, datetime == null ? JSONObject.NULL : datetime);
        } catch (JSONException e) {
        }
        return ret;
    }

    public boolean isComplete() {
        return city != null && address != null && address.trim().length() != 0;
    }

    public boolean isAllBlank() {
        return datetime == null && city == null && (address == null || address.trim().length() == 0);
    }
}
