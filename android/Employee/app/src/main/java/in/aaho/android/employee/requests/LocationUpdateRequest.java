package in.aaho.android.employee.requests;

import com.android.volley.AuthFailureError;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.employee.Aaho;
import in.aaho.android.employee.common.ApiPostRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by Suraj M
 */
public class LocationUpdateRequest extends ApiPostRequest {
    public static final String KEY_BOOKING_STATUS_MAPPING_ID = "booking_status_mapping_id";
    public static final String KEY_GOOGLE_PLACES = "google_places";

    public LocationUpdateRequest(Integer id,String googlePlaces, ApiResponseListener listener) {
        super(Api.LOCATION_UPDATE_URL, data(id,googlePlaces), listener);
    }

    private static JSONObject data(Integer id, String googlePlaces) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(KEY_BOOKING_STATUS_MAPPING_ID, String.valueOf(id));
            jsonObject.put(KEY_GOOGLE_PLACES, new JSONObject(googlePlaces));
        } catch (JSONException e) {
        }
        return jsonObject;
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String>  params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());

        return params;
    }

}

