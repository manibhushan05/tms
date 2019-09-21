package in.aaho.android.loads.requests;

import in.aaho.android.loads.common.ApiGetRequest;
import in.aaho.android.loads.common.ApiResponseListener;

/**
 * Created by aaho on 18/04/18.
 */


public class LoginStatusRequest extends ApiGetRequest {

    public LoginStatusRequest(ApiResponseListener listener) {
        super(Api.LOGIN_STATUS_URL, ApiGetRequest.NO_HEADER, listener);
    }
}
