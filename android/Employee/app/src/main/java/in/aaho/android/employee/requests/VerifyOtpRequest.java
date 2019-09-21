package in.aaho.android.employee.requests;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.employee.common.ApiPostRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by Suraj M
 */
public class VerifyOtpRequest extends ApiPostRequest {
    public static final String USERNAME_KEY = "username";
    public static final String OTP_KEY = "otp";

    public VerifyOtpRequest(String username, String otp, ApiResponseListener listener) {
        super(Api.VERIFY_OTP_URL, data(username,otp), listener);
    }

    private static JSONObject data(String username, String otp) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(USERNAME_KEY, username);
            jsonObject.put(OTP_KEY, otp);
        } catch (JSONException e) {
        }
        return jsonObject;
    }

}
