package in.aaho.android.loads.requests;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.loads.common.ApiPostRequest;
import in.aaho.android.loads.common.ApiResponseListener;

/**
 * Created by aaho on 18/04/18.
 */

public class ResetPasswordRequest extends ApiPostRequest {

    private static final String NEW_PASSWORD_KEY = "new_password";
    public static final String USERNAME_KEY = "username";

    public ResetPasswordRequest(String username,String newPass, ApiResponseListener listener) {
        super(Api.RESET_PASSWORD_URL, data(username,newPass), listener);
    }

    private static JSONObject data(String username, String newPassword) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(USERNAME_KEY, username);
            jsonObject.put(NEW_PASSWORD_KEY, newPassword);
        } catch (JSONException e) {
        }
        return jsonObject;
    }
}

