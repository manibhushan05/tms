package in.aaho.android.ownr.requests;

import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class NewBookingRequest extends ApiPostRequest {

    public NewBookingRequest(JSONObject jsonRequest, ApiResponseListener listener) {
        super(Api.NEW_BOOKING_URL, jsonRequest, listener);
    }
}
