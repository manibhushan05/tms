package in.aaho.android.ownr.requests;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class VendorDeleteRequest extends ApiPostRequest {

    private static final String ID_KEY = "id";

    public VendorDeleteRequest(long id, ApiResponseListener listener) {
        super(Api.DELETE_VENDOR_URL, data(id), listener);
    }

    private static JSONObject data(long id) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(ID_KEY, id);
        } catch (JSONException e) {
        }
        return jsonObject;
    }
}
