package in.aaho.android.aahocustomers.requests;

import org.json.JSONObject;

import in.aaho.android.aahocustomers.common.ApiPostRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class DriverAddEditRequest extends ApiPostRequest {

    public DriverAddEditRequest(JSONObject jsonObject, ApiResponseListener listener) {
        super(Api.DRIVER_EDIT_URL, jsonObject, listener);
    }
}
