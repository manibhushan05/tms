package in.aaho.android.ownr.map;

import com.google.android.gms.maps.model.LatLng;

import org.json.JSONException;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Date;

import in.aaho.android.ownr.common.Utils;

/**
 * Created by mani on 30/11/16.
 */

public class TimeLocation {
    public static final SimpleDateFormat DISPLAY_FORMAT = new SimpleDateFormat("d MMM, h:mm aaa");

    public final double latitude, longitude;
    public final Date time;
    public final String name;
    private final LatLng latLng;
    private final String district;
    private final String state;
    private final String country;

    private TimeLocation(double latitude, double longitude, Date time, String name, String district,
                         String state, String country) {
        this.latitude = latitude;
        this.longitude = longitude;
        this.time = time;
        this.name = name;
        this.district = district;
        this.state = state;
        this.country = country;
        this.latLng = new LatLng(latitude, longitude);
    }

    public static TimeLocation fromJson(JSONObject object) throws JSONException {
        if (object == null) {
            return null;
        }
        return new TimeLocation(
                object.getDouble("latitude"),
                object.getDouble("longitude"),
                Utils.jsonParseDate(object.getString("time")),
                object.getString("name"),
                object.getString("district"),
                object.getString("state"),
                object.getString("country")
        );
    }

    public String text() {
        return name + " at " + formatDate(time);
    }

    private String formatDate(Date date) {
        if (date == null) {
            return "";
        } else {
            return DISPLAY_FORMAT.format(date);
        }
    }

    public LatLng latlng() {
        return latLng;
    }

}
