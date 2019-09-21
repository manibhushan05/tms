package in.aaho.android.employee.requests;

import java.util.Map;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

public class UserDataRequest extends ApiGetRequest {
    public UserDataRequest(Map<String, String> params, ApiResponseListener listener) {
        super(Api.USER_DATA_URL, params, listener);
    }
}
