package in.aaho.android.ownr.requests;

import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class SendQuoteRequest extends ApiPostRequest {

    public SendQuoteRequest(JSONObject jsonObject, ApiResponseListener listener) {
        super(Api.SEND_QUOTE_URL, jsonObject, listener);
    }
}
