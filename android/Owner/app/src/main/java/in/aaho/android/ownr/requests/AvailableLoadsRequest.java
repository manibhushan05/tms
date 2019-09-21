package in.aaho.android.ownr.requests;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by mani on 1/8/16.
 */
public class AvailableLoadsRequest extends ApiGetRequest {

    public AvailableLoadsRequest(ApiResponseListener listener) {
        super(Api.AVAILABLE_LOADS_URL, ApiGetRequest.NO_HEADER, listener);
    }
}
