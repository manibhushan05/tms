package in.aaho.android.aahocustomers.requests;

import in.aaho.android.aahocustomers.common.ApiGetRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class VehicleListRequest extends ApiGetRequest {

    public VehicleListRequest(ApiResponseListener listener) {
        super(Api.VEHICLE_LIST_URL, ApiGetRequest.NO_HEADER, listener);
    }
}
