package in.aaho.android.ownr.requests;

import com.android.volley.AuthFailureError;

import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.ownr.Aaho;
import in.aaho.android.ownr.common.ApiPatchRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class VehicleAddEditRequest extends ApiPatchRequest {

    public VehicleAddEditRequest(long driverId, JSONObject jsonObject, ApiResponseListener listener) {
        super(Api.VEHICLE_EDIT_URL+driverId+"/", jsonObject, listener);
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String>  params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());

        return params;
    }
}
