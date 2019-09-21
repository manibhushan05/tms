package in.aaho.android.ownr.booking;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by mani on 13/9/16.
 */
public class UserAddress {
    private boolean synced = true;

    private Long id = null;
    private String line1 = "";
    private String line2 = "";
    private String line3 = "";
    private String landmark = "";
    private String pin = "";
    private City city = null;


    public void updateAddress(JSONObject jsonObject) {
        updateFromJson(jsonObject);
        synced = true;
    }

    public String getAddress() {
        List<String> toJoin = new ArrayList<>();
        if (line1 != null && !line1.trim().isEmpty()) {
            toJoin.add(line1.trim());
        }
        if (line2 != null && !line2.trim().isEmpty()) {
            toJoin.add(line2.trim());
        }
        if (line3 != null && !line3.trim().isEmpty()) {
            toJoin.add(line1.trim());
        }
        if (city != null) {
            toJoin.add(city.getFullName());
        }
        if (pin != null && !pin.trim().isEmpty()) {
            toJoin.add(pin.trim());
        }
        String addrStr = "";
        for (String part : toJoin) {
            addrStr = addrStr + (addrStr.isEmpty() ? "" : ", ") + part;
        }
        return addrStr;
    }

    private void update(Long id, String line1, String line2, String line3, String landmark, String pin, Long cityId) {
        this.id = id;
        this.line1 = App.nullToBlank(line1);
        this.line2 = App.nullToBlank(line2);
        this.line3 = App.nullToBlank(line3);
        this.landmark = App.nullToBlank(landmark);
        this.pin = App.nullToBlank(pin);
        this.city = (cityId == null ? null : City.get(cityId));
    }

    private void updateFromJson(JSONObject addr) {
        if (addr == null || addr.length() == 0) {
            return;
        }
        Long cityId;
        try {
            cityId = addr.getJSONObject("city").getLong("id");
        } catch (JSONException e) {
            cityId = null;
        }
        update(
                getOrNull(addr, "id"),
                getOrBlank(addr, "line1"),
                getOrBlank(addr, "line1"),
                getOrBlank(addr, "line1"),
                getOrBlank(addr, "landmark"),
                getOrBlank(addr, "pin"),
                cityId
        );
    }

    private static Long getOrNull(JSONObject jsonObject, String key) {
        try {
            return jsonObject.getLong(key);
        } catch (JSONException e) {
            return null;
        }
    }

    private static String getOrBlank(JSONObject jsonObject, String key) {
        try {
            return jsonObject.getString(key);
        } catch (JSONException e) {
            return "";
        }
    }

    public JSONObject toJson() {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("id", id == null ? JSONObject.NULL : id);
            jsonObject.put("line1", line1 == null ? JSONObject.NULL : line1);
            jsonObject.put("line2", line2 == null ? JSONObject.NULL : line2);
            jsonObject.put("line3", line3 == null ? JSONObject.NULL : line3);
            jsonObject.put("landmark", landmark == null ? JSONObject.NULL : landmark);
            jsonObject.put("pin", pin == null ? JSONObject.NULL : pin);
            jsonObject.put("city", city == null ? JSONObject.NULL : city.toJson());
        } catch (JSONException e) {
        }
        return jsonObject;
    }

    public Long getId() {
        return id;
    }

    public String getLine1() {
        return line1;
    }

    public void setLine1(String line1) {
        if (!App.equal(this.line1, line1)) {
            this.synced = false;
        }
        this.line1 = line1;
    }

    public String getLine2() {
        return line2;
    }

    public void setLine2(String line2) {
        if (!App.equal(this.line2, line2)) {
            this.synced = false;
        }
        this.line2 = line2;
    }

    public String getLine3() {
        return line3;
    }

    public void setLine3(String line3) {
        if (!App.equal(this.line3, line3)) {
            this.synced = false;
        }
        this.line3 = line3;
    }

    public String getLandmark() {
        return landmark;
    }

    public void setLandmark(String landmark) {
        if (!App.equal(this.landmark, landmark)) {
            this.synced = false;
        }
        this.landmark = landmark;
    }

    public String getPin() {
        return pin;
    }

    public void setPin(String pin) {
        if (!App.equal(this.pin, pin)) {
            this.synced = false;
        }
        this.pin = pin;
    }

    public City getCity() {
        return city;
    }

    public void setCity(City city) {
        if (!City.equal(this.city, city)) {
            this.synced = false;
        }
        this.city = city;
    }

    public boolean isSynced() {
        return synced;
    }

    public void clear() {
        update(null, "", "", "", "", "", null);
        synced = true;
    }
}
