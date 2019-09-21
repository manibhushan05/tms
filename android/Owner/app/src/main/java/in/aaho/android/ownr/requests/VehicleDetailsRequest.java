package in.aaho.android.ownr.requests;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class VehicleDetailsRequest extends ApiGetRequest {

    public VehicleDetailsRequest(long vehicleId, ApiResponseListener listener) {
        /*super(Api.VEHICLE_DETAILS_URL, vehicleId, listener);*/
        super(Api.VEHICLE_DETAILS_URL+vehicleId, ApiGetRequest.NO_HEADER, listener);
    }

}
