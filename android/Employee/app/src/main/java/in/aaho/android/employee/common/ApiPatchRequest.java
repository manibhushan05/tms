package in.aaho.android.employee.common;

import org.json.JSONObject;

/**
 * Created by mani on 3/7/16.
 */
public class ApiPatchRequest extends ApiRequest {

    public ApiPatchRequest(String url, JSONObject jsonRequest, ApiResponseListener listener) {
        super(Method.PATCH, url, jsonRequest, listener);
    }

    @Override
    public String getBodyContentType() {
        return "application/json";
    }

}

