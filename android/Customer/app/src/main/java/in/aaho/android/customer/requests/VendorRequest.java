package in.aaho.android.customer.requests;

import org.json.JSONObject;

import in.aaho.android.customer.common.ApiPostRequest;
import in.aaho.android.customer.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class VendorRequest extends ApiPostRequest {

    public VendorRequest(JSONObject jsonRequest, ApiResponseListener listener) {
        super(Api.VENDOR_REQUEST_URL, jsonRequest, listener);
    }
}
