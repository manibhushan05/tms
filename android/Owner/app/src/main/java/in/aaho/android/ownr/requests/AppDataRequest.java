package in.aaho.android.ownr.requests;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class AppDataRequest extends ApiGetRequest {

    public AppDataRequest(ApiResponseListener listener) {
        super(Api.APP_DATA_URL, ApiGetRequest.NO_HEADER, listener);
    }
}
