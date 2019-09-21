package in.aaho.android.aahocustomers.requests;

import in.aaho.android.aahocustomers.common.ApiGetRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by aaho on 18/04/18.
 */


public class LoginStatusRequest extends ApiGetRequest {

    public LoginStatusRequest(ApiResponseListener listener) {
        super(Api.LOGIN_STATUS_URL, ApiGetRequest.NO_HEADER, listener);
    }
}
