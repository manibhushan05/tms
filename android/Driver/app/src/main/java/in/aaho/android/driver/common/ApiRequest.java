package in.aaho.android.driver.common;

import com.android.volley.AuthFailureError;
import com.android.volley.DefaultRetryPolicy;
import com.android.volley.toolbox.JsonObjectRequest;

import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.driver.Aaho;

/**
 * Created by shobhit on 3/7/16.
 */
public class ApiRequest extends JsonObjectRequest {

    // attempt 1: socket_timeout = timeout + timeout * backoff = 4 + 4 * 2 = 12s, timeout = socket_timeout
    // attempt 2: socket_timeout = timeout + timeout * backoff = 12 + 12 * 2 = 36s, and so on

    public ApiRequest(int method, String url, JSONObject jsonRequest, ApiResponseListener listener) {
        super(method, url, jsonRequest, listener, listener);
        this.setRetryPolicy(new DefaultRetryPolicy(this.getTimeout(), this.getRetries(), this.getBackoff()));
    }

    protected int getTimeout() {
        return 4 * 1000;  // 4 seconds
    }

    protected int getRetries() {
        return 1;  // retry once
    }

    protected float getBackoff() {
        return 2.0f;
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String> headers = new HashMap<>(super.getHeaders());
        String authToken = Aaho.getAuthToken();
        if (authToken == null) {
            return headers;
        }
        headers.put("Authorization", "Token " + authToken);
        return headers;
    }
}

