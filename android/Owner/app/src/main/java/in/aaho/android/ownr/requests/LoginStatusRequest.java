package in.aaho.android.ownr.requests;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by mani on 1/8/16.
 */
public class LoginStatusRequest extends ApiGetRequest {

    public LoginStatusRequest(ApiResponseListener listener) {
        super(Api.LOGIN_STATUS_URL, ApiGetRequest.NO_HEADER, listener);
    }
}
