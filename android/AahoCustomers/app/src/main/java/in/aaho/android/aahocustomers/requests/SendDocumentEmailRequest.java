package in.aaho.android.aahocustomers.requests;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.List;

import in.aaho.android.aahocustomers.common.ApiPostRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

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
}
