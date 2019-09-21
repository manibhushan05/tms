package in.aaho.android.aahocustomers.requests;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.aahocustomers.common.ApiPostRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by aaho on 18/04/18.
 */

public class PasswordEditRequest extends ApiPostRequest {

    private static final String CUR_PASSWORD_KEY = "current_password";
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
}

