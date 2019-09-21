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
 * Created by aaho on 27/02/19.
 */

public class PendingPaymentUpdateDueDateRequest extends ApiPostRequest{

    public static final String KEY_DUE_DATE = "due_date";

    public PendingPaymentUpdateDueDateRequest(Integer id, String date, ApiResponseListener listener) {
        super(Api.PENDING_PAYMENT_UPDATE_DUE_DATE_URL+id+"/", data(date), listener);
    }

    private static JSONObject data(String date) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(KEY_DUE_DATE, date);
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
