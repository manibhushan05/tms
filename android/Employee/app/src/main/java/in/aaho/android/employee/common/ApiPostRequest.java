package in.aaho.android.employee.common;

import org.json.JSONObject;

/**
 * Created by mani on 3/7/16.
 */
public class ApiPostRequest extends ApiRequest {

    public ApiPostRequest(String url, JSONObject jsonRequest, ApiResponseListener listener) {
        super(Method.POST, url, jsonRequest, listener);
    }

    @Override
    public String getBodyContentType() {
        return "application/json";
    }

}

