package in.aaho.android.driver.requests;

import org.json.JSONObject;

import in.aaho.android.driver.common.ApiGetRequest;
import in.aaho.android.driver.common.ApiPostRequest;
import in.aaho.android.driver.common.ApiResponseListener;

/**
 * Created by mani on 17/5/16.
 */

public class VehiclePodDetailsRequest extends ApiGetRequest {

    public VehiclePodDetailsRequest(ApiResponseListener listener) {
        super(Api.VEHICLE_POD_DETAILS_URL, listener);
    }
}