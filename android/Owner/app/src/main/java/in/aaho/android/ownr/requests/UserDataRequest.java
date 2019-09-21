package in.aaho.android.ownr.requests;

import java.util.Map;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

public class UserDataRequest extends ApiGetRequest {
    public UserDataRequest(Map<String, String> params,ApiResponseListener listener) {
        super(Api.USER_DATA_URL, params, listener);
    }
}
