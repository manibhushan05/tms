package in.aaho.android.ownr.requests;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class DriverDetailsRequest extends ApiGetRequest {

    public DriverDetailsRequest(long driverId, ApiResponseListener listener) {
        super(Api.DRIVER_DETAILS_URL, driverId, listener);
    }

}
