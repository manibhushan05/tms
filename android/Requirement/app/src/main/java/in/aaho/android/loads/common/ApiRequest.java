package in.aaho.android.loads.common;

import com.android.volley.DefaultRetryPolicy;
import com.android.volley.toolbox.JsonObjectRequest;

import org.json.JSONObject;

/**
 * Created by aaho on 18/04/18.
 */

public class ApiRequest extends JsonObjectRequest {

    // attempt 1: socket_timeout = timeout + timeout * backoff = 4 + 4 * 2 = 12s, timeout = socket_timeout
    // attempt 2: socket_timeout = timeout + timeout * backoff = 12 + 12 * 2 = 36s, and so on

    public ApiRequest(int method, String url, JSONObject jsonRequest, ApiResponseListener listener) {
        super(method, url, jsonRequest, listener, listener);
        this.setRetryPolicy(new DefaultRetryPolicy(this.getTimeout(), this.getRetries(), this.getBackoff()));
    }

    protected int getTimeout() {
        return 60 * 1000;  // 60 seconds
    }

    protected int getRetries() {
        return 1;  // retry once
    }

    protected float getBackoff() {
        return 2.0f;
    }
}

