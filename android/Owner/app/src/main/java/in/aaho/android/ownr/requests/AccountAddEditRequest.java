package in.aaho.android.ownr.requests;

import com.android.volley.AuthFailureError;

import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.ownr.Aaho;
import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class AccountAddEditRequest extends ApiPostRequest {

    public AccountAddEditRequest(JSONObject jsonObject, ApiResponseListener listener) {
        super(Api.ACCOUNT_EDIT_URL, jsonObject, listener);
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String>  params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());

        return params;
    }

    /*public AccountAddEditRequest(JSONObject jsonObject, ApiResponseListener listener) {
        super(Api.ACCOUNT_EDIT_URL, jsonObject, listener);
    }*/
}
