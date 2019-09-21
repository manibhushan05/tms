package in.aaho.android.ownr.requests;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class VendorAddRequest extends ApiPostRequest {

    private static final String NAME_KEY = "name";
    private static final String PHONE_KEY = "phone";

    public VendorAddRequest(String name, String phone, ApiResponseListener listener) {
        super(Api.ADD_VENDOR_URL, data(name, phone), listener);
    }

    private static JSONObject data(String name, String phone) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(NAME_KEY, name);
            jsonObject.put(PHONE_KEY, phone);
        } catch (JSONException e) {
        }
        return jsonObject;
    }
}
