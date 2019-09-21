package in.aaho.android.employee.requests;

import android.util.Log;

import com.android.volley.AuthFailureError;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.employee.Aaho;
import in.aaho.android.employee.common.ApiPostRequest;
import in.aaho.android.employee.common.ApiResponseListener;

public class PostFcmTokenRequest extends ApiPostRequest {

    public static final String TOKEN_KEY = "token";
    private static final String DEVICE_ID_KEY = "device_id";
    private static final String APP_KEY = "app";

    public PostFcmTokenRequest(String token, String device_id, ApiResponseListener listener) {
        super(Api.POST_FCM_TOKEN_URL, data(token,device_id), listener);
    }

    private static JSONObject data(String token, String device_id) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(TOKEN_KEY, token);
            jsonObject.put(DEVICE_ID_KEY, device_id);
            jsonObject.put(APP_KEY, "AE");
        } catch (JSONException e) {
            Log.e("PostFcmTokenRequest","Error while making json object!");
        }

        return jsonObject;
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String>  params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());

        return params;
    }

    @Override
    public String getBodyContentType() {
        return "application/json";
    }
}
