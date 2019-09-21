package in.aaho.android.loads.requests;

import in.aaho.android.loads.common.ApiPostRequest;
import in.aaho.android.loads.common.ApiResponseListener;
/**
 * Created by aaho on 18/04/18.
 */

public class LogoutRequest extends ApiPostRequest {

    public LogoutRequest(ApiResponseListener listener) {
        super(Api.LOGOUT_URL, null, listener);
    }
}
