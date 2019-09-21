package in.aaho.android.ownr.requests;


import in.aaho.android.ownr.common.ApiDeleteRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by Suraj M
 */
public class LogoutRequest extends ApiDeleteRequest {

    public LogoutRequest(ApiResponseListener listener) {
        super(Api.LOGOUT_URL,null, listener);
    }

}
