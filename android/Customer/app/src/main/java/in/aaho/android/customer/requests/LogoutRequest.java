package in.aaho.android.customer.requests;

import in.aaho.android.customer.common.ApiPostRequest;
import in.aaho.android.customer.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class LogoutRequest extends ApiPostRequest {

    public LogoutRequest(ApiResponseListener listener) {
        super(Api.LOGOUT_URL, null, listener);
    }
}
