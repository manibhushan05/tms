package in.aaho.android.employee.requests;

import in.aaho.android.employee.common.ApiDeleteRequest;
import in.aaho.android.employee.common.ApiPostRequest;
import in.aaho.android.employee.common.ApiResponseListener;
/**
 * Created by aaho on 18/04/18.
 */

public class LogoutRequest extends ApiDeleteRequest {

    public LogoutRequest(ApiResponseListener listener) {
        super(Api.LOGOUT_URL, null, listener);
    }
}
