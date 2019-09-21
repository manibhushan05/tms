package in.aaho.android.ownr.requests;

import com.android.volley.AuthFailureError;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import in.aaho.android.ownr.Aaho;
import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class SendDocumentEmailRequest extends ApiPostRequest {

    private static final String ID_KEY = "id";
    private static final String EMAILS_KEY = "emails";
    private static final String EXCLUDED_KEY = "excluded";

    public SendDocumentEmailRequest(long id, List<String> emails, List<String> excluded, ApiResponseListener listener) {
        super(Api.SEND_DOCUMENT_EMAIL_URL, data(id, emails, excluded), listener);
    }

    private static JSONObject data(long id, List<String> emails, List<String> excluded) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(ID_KEY, id);
            jsonObject.put(EMAILS_KEY, new JSONArray(emails));
            jsonObject.put(EXCLUDED_KEY, new JSONArray(excluded));
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jsonObject;
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String>  params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());

        return params;
    }
}
