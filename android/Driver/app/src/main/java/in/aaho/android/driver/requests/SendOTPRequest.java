package in.aaho.android.driver.requests;

import org.json.JSONObject;

import in.aaho.android.driver.common.ApiPostRequest;
import in.aaho.android.driver.common.ApiResponseListener;

/**
 * Created by mani on 31/5/16.
 */
public class SendOTPRequest extends ApiPostRequest {

    public SendOTPRequest(JSONObject jsonRequest, ApiResponseListener listener) {
        super(Api.SEND_OTP_URL, jsonRequest, listener);
    }
}
