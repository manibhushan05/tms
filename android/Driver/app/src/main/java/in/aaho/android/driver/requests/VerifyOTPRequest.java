package in.aaho.android.driver.requests;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.driver.common.ApiPostRequest;
import in.aaho.android.driver.common.ApiResponseListener;

/**
 * Created by mani on 31/5/16.
 */
public class VerifyOTPRequest extends ApiPostRequest {

    public VerifyOTPRequest(String otp, ApiResponseListener listener) {
        super(Api.VERIFY_OTP_URL, getData(otp), listener);
    }

    private static JSONObject getData(String otp) {
        JSONObject object = new JSONObject();
        try {
            object.put("otp", otp);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return object;
    }
}
