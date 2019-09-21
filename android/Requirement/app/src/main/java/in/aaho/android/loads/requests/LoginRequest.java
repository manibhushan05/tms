package in.aaho.android.loads.requests;

import org.json.JSONException;
import org.json.JSONObject;
import in.aaho.android.loads.common.ApiPostRequest;
import in.aaho.android.loads.common.ApiResponseListener;

/**
 * Created by aaho on 18/04/18.
 */

public class LoginRequest extends ApiPostRequest {

    private static final String USERNAME_KEY = "username";
    private static final String PASSWORD_KEY = "password";

    public LoginRequest(String username, String password, ApiResponseListener listener) {
        super(Api.LOGIN_URL, data(username, password), listener);
    }

    private static JSONObject data(String username, String password) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(USERNAME_KEY, username);
            jsonObject.put(PASSWORD_KEY, password);
        } catch (JSONException e) {
        }
        return jsonObject;
    }
}
