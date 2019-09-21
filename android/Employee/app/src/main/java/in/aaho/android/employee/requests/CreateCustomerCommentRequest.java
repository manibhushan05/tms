package in.aaho.android.employee.requests;

import com.android.volley.AuthFailureError;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.employee.Aaho;
import in.aaho.android.employee.common.ApiPostRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by aaho on 28/02/19.
 */

public class CreateCustomerCommentRequest extends ApiPostRequest {

    public static final String KEY_SME_ID = "sme_id";
    public static final String KEY_COMMENT = "comment";

    public CreateCustomerCommentRequest(Integer id, String comment, ApiResponseListener listener) {
        super(Api.CREATE_PENDING_PAYMENT_COMMENT_URL, data(id, comment), listener);
    }

    private static JSONObject data(Integer id, String comment) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(KEY_SME_ID, id);
            jsonObject.put(KEY_COMMENT, comment);
        } catch (JSONException e) {
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