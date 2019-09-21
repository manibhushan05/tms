package in.aaho.android.ownr.requests;

import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class OwnerAddEditRequest extends ApiPostRequest {

    public OwnerAddEditRequest(JSONObject jsonObject, ApiResponseListener listener) {
        super(Api.OWNER_EDIT_URL, jsonObject, listener);
    }
}
