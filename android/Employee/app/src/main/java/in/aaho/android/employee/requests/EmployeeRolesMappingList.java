package in.aaho.android.employee.requests;

import com.android.volley.AuthFailureError;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.employee.Aaho;
import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by Suraj M on 22/05/18.
 */


public class EmployeeRolesMappingList extends ApiGetRequest {

    public EmployeeRolesMappingList(Map<String, String> params, ApiResponseListener listener) {
        super(Api.EMP_ROLE_MAPPING_LIST_URL, params, listener);
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String>  params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());

        return params;
    }
}
