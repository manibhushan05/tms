package in.aaho.android.ownr.requests;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class VehicleStatusEditRequest extends ApiPostRequest {

    public VehicleStatusEditRequest(long id, String status, ApiResponseListener listener) {
        super(Api.VEHICLE_STATUS_EDIT_URL, data(id, status), listener);
    }

    private static JSONObject data(long id, String status) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("id", id);
            jsonObject.put("vehicle_status", status);
        } catch (JSONException e) {
        }
        return jsonObject;
    }
}
