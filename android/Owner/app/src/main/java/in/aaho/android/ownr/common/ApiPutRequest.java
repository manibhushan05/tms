package in.aaho.android.ownr.common;

import com.android.volley.AuthFailureError;

import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.ownr.Aaho;

/**
 * Created by mani on 3/7/16.
 */
public class ApiPutRequest extends ApiRequest {

    public ApiPutRequest(String url, JSONObject jsonRequest, ApiResponseListener listener) {
        super(Method.PUT, url, jsonRequest, listener);
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String>  params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());
        params.put("app-category", "fms");

        return params;
    }

    @Override
    public String getBodyContentType() {
        return "application/json";
    }

}

