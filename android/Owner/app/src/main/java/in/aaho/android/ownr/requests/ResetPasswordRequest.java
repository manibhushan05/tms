package in.aaho.android.ownr.requests;

import com.android.volley.AuthFailureError;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.ownr.Aaho;
import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by suraj
 */
public class ResetPasswordRequest extends ApiPostRequest {

    private static final String NEW_PASSWORD_KEY = "new_password";
    public static final String USERNAME_KEY = "username";

    public ResetPasswordRequest(String username,String newPass, ApiResponseListener listener) {
        super(Api.RESET_PASSWORD_URL, data(username,newPass), listener);
    }

    private static JSONObject data(String username,String newPassword) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(USERNAME_KEY, username);
            jsonObject.put(NEW_PASSWORD_KEY, newPassword);
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
