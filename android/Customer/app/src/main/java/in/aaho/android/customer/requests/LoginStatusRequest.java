package in.aaho.android.customer.requests;

import in.aaho.android.customer.common.ApiGetRequest;
import in.aaho.android.customer.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class LoginStatusRequest extends ApiGetRequest {

    public LoginStatusRequest(ApiResponseListener listener) {
        super(Api.LOGIN_STATUS_URL, null, listener);
    }
}
