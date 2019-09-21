package in.aaho.android.ownr.requests;

import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class VendorRequest extends ApiPostRequest {

    public VendorRequest(JSONObject jsonRequest, ApiResponseListener listener) {
        super(Api.VENDOR_REQUEST_URL, jsonRequest, listener);
    }
}
