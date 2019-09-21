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
public class StatusUpdateRequest extends ApiPostRequest {
    public static final String KEY_BOOKING_STATUS = "booking_status";
    public static final String KEY_MANUAL_BOOKING_ID = "manual_booking_id";
    public static final String KEY_BOOKING_STAGE = "booking_stage";

    public StatusUpdateRequest(Integer id, String bookingStatus, ApiResponseListener listener) {
        super(Api.STATUS_UPDATE_URL, data(bookingStatus,id), listener);
    }

    private static JSONObject data(String bookingStatus,Integer id) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(KEY_MANUAL_BOOKING_ID, String.valueOf(id));
            jsonObject.put(KEY_BOOKING_STATUS, bookingStatus);
            jsonObject.put(KEY_BOOKING_STAGE, "in_progress");
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

