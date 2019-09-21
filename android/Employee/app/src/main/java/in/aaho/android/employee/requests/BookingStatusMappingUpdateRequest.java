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
 * Created by aaho on 20/02/19.
 */

public class BookingStatusMappingUpdateRequest extends ApiPostRequest{
    public static final String KEY_BOOKING_STATUS_CHAIN_ID = "booking_status_chain_id";
    public static final String KEY_MANUAL_BOOKING_ID = "manual_booking_id";
    public static final String KEY_BOOKING_STAGE = "booking_stage";
    public static final String KEY_DUE_DATE = "due_date";

    public BookingStatusMappingUpdateRequest(Integer id, Integer chain_id, Integer manual_booking_id,
                                             String date, ApiResponseListener listener) {
        super(Api.BOOKING_MAPPING_STATUS_UPDATE_URL+id+"/", data(chain_id, manual_booking_id, date), listener);
    }

    private static JSONObject data(Integer chain_id, Integer manual_booking_id, String date) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(KEY_MANUAL_BOOKING_ID, String.valueOf(manual_booking_id));
            jsonObject.put(KEY_BOOKING_STATUS_CHAIN_ID, chain_id);
            jsonObject.put(KEY_BOOKING_STAGE, "in_progress");
            jsonObject.put(KEY_DUE_DATE, date);
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
