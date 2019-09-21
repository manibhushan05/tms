package in.aaho.android.customer.common;

import android.util.Log;

import org.json.JSONObject;

/**
 * Created by shobhit on 3/7/16.
 */
public class ApiPostRequest extends ApiRequest {

    public ApiPostRequest(String url, JSONObject jsonRequest, ApiResponseListener listener) {
        super(Method.POST, url, jsonRequest, listener);

        Log.e("[REQUEST]", "POST " + url + "\n\n" + (jsonRequest == null ? "<null>" : jsonRequest.toString()));
    }

}

