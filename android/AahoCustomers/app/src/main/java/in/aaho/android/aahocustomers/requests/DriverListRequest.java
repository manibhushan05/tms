package in.aaho.android.aahocustomers.requests;

import in.aaho.android.aahocustomers.common.ApiGetRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class DriverListRequest extends ApiGetRequest {

    public DriverListRequest(ApiResponseListener listener) {
        super(Api.DRIVER_LIST_URL, ApiGetRequest.NO_HEADER, listener);
    }
}
