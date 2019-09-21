package in.aaho.android.customer.requests;

import org.json.JSONObject;

import in.aaho.android.customer.common.ApiPostRequest;
import in.aaho.android.customer.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class ProfileEditRequest extends ApiPostRequest {

    public ProfileEditRequest(JSONObject jsonRequest, ApiResponseListener listener) {
        super(Api.EDIT_PROFILE_URL, jsonRequest, listener);
    }
}
