package in.aaho.android.ownr.requests;

import com.android.volley.AuthFailureError;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.ownr.Aaho;
import in.aaho.android.ownr.common.ApiPatchRequest;
import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiPutRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class PasswordEditRequest extends ApiPutRequest {

    private static final String CUR_PASSWORD_KEY = "old_password";
    private static final String NEW_PASSWORD_KEY = "new_password";

    public PasswordEditRequest(String currPass, String newPass, ApiResponseListener listener) {
        super(Api.EDIT_PASSWORD_URL, data(currPass, newPass), listener);
    }

    private static JSONObject data(String currPassword, String newPassword) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(CUR_PASSWORD_KEY, currPassword);
            jsonObject.put(NEW_PASSWORD_KEY, newPassword);
        } catch (JSONException e) {
        }
        return jsonObject;
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String>  params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());
        params.put("Accept", "application/json");

        return params;
    }

    @Override
    public String getBodyContentType() {
        return "application/json";
    }

}
