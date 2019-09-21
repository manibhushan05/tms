package in.aaho.android.employee.common;

import com.android.volley.AuthFailureError;

import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.employee.Aaho;

/**
 * Created by Suraj M
 */
public class ApiDeleteRequest extends ApiRequest {

    public ApiDeleteRequest(String url, JSONObject jsonRequest, ApiResponseListener listener) {
        super(Method.DELETE, url, jsonRequest, listener);
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String> params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());

        return params;
    }

    @Override
    public String getBodyContentType() {
        return "application/json";
    }

}

