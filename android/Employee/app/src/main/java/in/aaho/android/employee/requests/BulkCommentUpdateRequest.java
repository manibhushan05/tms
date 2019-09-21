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
public class BulkCommentUpdateRequest extends ApiPostRequest {
    public static final String KEY_BOOKING_STATUS_MAPPING_ID = "booking_status_mapping_id";
    public static final String KEY_COMMENT = "comment";

    public BulkCommentUpdateRequest(String id, String comment, ApiResponseListener listener) {
        super(Api.BULK_COMMENT_UPDATE_URL, data(id,comment), listener);
    }

    private static JSONObject data(String id, String comment) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(KEY_BOOKING_STATUS_MAPPING_ID, String.valueOf(id));
            jsonObject.put(KEY_COMMENT, comment);
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

