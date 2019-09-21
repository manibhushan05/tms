package in.aaho.android.driver.requests;

import org.json.JSONObject;

import in.aaho.android.driver.common.ApiPostRequest;
import in.aaho.android.driver.common.ApiResponseListener;

/**
 * Created by mani on 31/5/16.
 */
public class RegisterVehicleRequest extends ApiPostRequest {

    public RegisterVehicleRequest(JSONObject jsonRequest, ApiResponseListener listener) {
        super(Api.DRIVER_REGISTER_URL, jsonRequest, listener);
    }
}
