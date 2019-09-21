package in.aaho.android.ownr.common;

import android.text.TextUtils;
import android.util.Log;

import com.android.volley.AuthFailureError;

import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.ownr.Aaho;

/**
 * Created by mani on 3/7/16.
 */
public class ApiPostRequest extends ApiRequest {

    public ApiPostRequest(String url, JSONObject jsonRequest, ApiResponseListener listener) {
        super(Method.POST, url, jsonRequest, listener);
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String>  params = new HashMap<String, String>();
        params.put("app-category", "fms");

        return params;
    }

    @Override
    public String getBodyContentType() {
        return "application/json";
    }
}

