package in.aaho.android.aahocustomers.requests;

import in.aaho.android.aahocustomers.common.ApiGetRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class VehicleDetailsRequest extends ApiGetRequest {

    public VehicleDetailsRequest(long vehicleId, ApiResponseListener listener) {
        super(Api.VEHICLE_DETAILS_URL, vehicleId, listener);
    }

}
