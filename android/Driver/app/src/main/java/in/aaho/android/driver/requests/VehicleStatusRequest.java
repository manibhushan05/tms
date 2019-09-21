package in.aaho.android.driver.requests;

import org.json.JSONObject;

import in.aaho.android.driver.common.ApiPostRequest;
import in.aaho.android.driver.common.ApiResponseListener;

/**
 * Created by mani on 17/5/16.
 */

public class VehicleStatusRequest extends ApiPostRequest {

    public VehicleStatusRequest(JSONObject jsonRequest, ApiResponseListener listener) {
        super(Api.VEHICLE_STATUS_URL, jsonRequest, listener);
    }
}