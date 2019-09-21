package in.aaho.android.ownr.requests;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by Suraj M
 */
public class ForgotPasswordRequest extends ApiPostRequest {
    public static final String USERNAME_KEY = "username";

    public ForgotPasswordRequest(String username, ApiResponseListener listener) {
        super(Api.FORGOT_PASSWORD_URL, data(username), listener);
    }

    private static JSONObject data(String username) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(USERNAME_KEY, username);
        } catch (JSONException e) {
        }
        return jsonObject;
    }

}
