package in.aaho.android.driver.requests;

import org.json.JSONObject;

import in.aaho.android.driver.common.ApiPostRequest;
import in.aaho.android.driver.common.ApiResponseListener;

/**
 * Created by mani on 31/5/16.
 */
public class EditDriverDetailsRequest extends ApiPostRequest {

    public EditDriverDetailsRequest(JSONObject jsonRequest, ApiResponseListener listener) {
        super(Api.DRIVER_DETAIL_EDIT_URL, jsonRequest, listener);
    }
}
