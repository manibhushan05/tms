package in.aaho.android.loads.requests;

import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.loads.common.ApiPostRequest;
import in.aaho.android.loads.common.ApiResponseListener;

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
            jsonObject.put(APP_KEY, "AS");
        } catch (JSONException e) {
            Log.e("PostFcmTokenRequest","Error while making json object!");
        }

        return jsonObject;
    }
}
