package in.aaho.android.customer.requests;

import in.aaho.android.customer.common.ApiGetRequest;
import in.aaho.android.customer.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class AppDataRequest extends ApiGetRequest {

    public AppDataRequest(ApiResponseListener listener) {
        super(Api.APP_DATA_URL, null, listener);
    }
}
