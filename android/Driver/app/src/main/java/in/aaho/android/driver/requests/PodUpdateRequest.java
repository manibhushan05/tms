package in.aaho.android.driver.requests;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.driver.common.ApiPostRequest;
import in.aaho.android.driver.common.ApiResponseListener;

/**
 * Created by mani on 31/5/16.
 */
public class PodUpdateRequest extends ApiPostRequest {

    public PodUpdateRequest(String pod, String podThumb, ApiResponseListener listener) {
        super(Api.POD_UPDATE_URL, getData(pod, podThumb), listener);
    }

    private static JSONObject getData(String pod, String podThumb) {
        JSONObject object = new JSONObject();
        try {
            object.put("pod", pod);
            object.put("pod_thumb", podThumb);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return object;
    }
}
