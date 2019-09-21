package in.aaho.android.aahocustomers.common;

import android.util.Log;

import org.json.JSONObject;

/**
 * Created by aaho on 18/04/18.
 */
public class ApiPostRequest extends ApiRequest {

    public ApiPostRequest(String url, JSONObject jsonRequest, ApiResponseListener listener) {
        super(Method.POST, url, jsonRequest, listener);

        Log.e("[REQUEST]", "POST " + url + "\n\n" + (jsonRequest == null ? "<null>" : jsonRequest.toString()));
    }

}


