package in.aaho.android.loads.requests;

import in.aaho.android.loads.common.ApiGetRequest;
import in.aaho.android.loads.common.ApiResponseListener;

/**
 * Created by aaho on 18/04/18.
 */

public class ForgotPasswordRequest extends ApiGetRequest {

    public ForgotPasswordRequest(String username, ApiResponseListener listener) {
        super(Api.FORGOT_PASSWORD_URL, username, listener);
    }
}

