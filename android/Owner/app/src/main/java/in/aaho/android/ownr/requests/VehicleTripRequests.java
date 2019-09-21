package in.aaho.android.ownr.requests;

import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.ApiPostRequest;
/**
 * Created by mani on 9/12/16.
 */

public class VehicleTripRequests extends ApiPostRequest {

    public VehicleTripRequests(JSONObject jsonObject, ApiResponseListener listener) {
        super(Api.MB_VEHICLE_TRIP_DATA_URL, jsonObject, listener);
    }
}