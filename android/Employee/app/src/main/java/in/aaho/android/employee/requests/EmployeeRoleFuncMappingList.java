package in.aaho.android.employee.requests;

import com.android.volley.AuthFailureError;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.employee.Aaho;
import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiPostRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by aaho on 22/05/18.
 */


public class EmployeeRoleFuncMappingList extends ApiGetRequest {

    public EmployeeRoleFuncMappingList(Map<String, String> params, ApiResponseListener listener) {
        super(Api.EMP_ROLE_FUNCTIONALITY_URL, params, listener);
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
