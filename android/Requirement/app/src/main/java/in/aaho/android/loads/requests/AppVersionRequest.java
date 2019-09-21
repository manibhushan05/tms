package in.aaho.android.loads.requests;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.loads.common.ApiPostRequest;
import in.aaho.android.loads.common.ApiResponseListener;

/**
 * Created by aaho on 22/05/18.
 */


public class AppVersionRequest extends ApiPostRequest {

    private static final String APP_PLATFORM_KEY = "app_platform";
    private static final String APP_NAME_KEY = "app_name";
    private static final String APP_VERSION_KEY = "app_version";

    public AppVersionRequest(String app_platform, String app_name, String app_version, ApiResponseListener listener) {
        super(Api.APP_VERSION_URL, data(app_platform, app_name, app_version), listener);
    }

    private static JSONObject data(String app_platform, String app_name, String app_version) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(APP_PLATFORM_KEY, app_platform);
            jsonObject.put(APP_NAME_KEY, app_name);
            jsonObject.put(APP_VERSION_KEY, app_version);
        } catch (JSONException e) {
        }
        return jsonObject;
    }
}
