package in.aaho.android.ownr.requests;

import com.android.volley.AuthFailureError;

import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.ownr.Aaho;
import in.aaho.android.ownr.common.ApiPatchRequest;
import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class ProfileEditRequest extends ApiPatchRequest {

    public ProfileEditRequest(JSONObject jsonRequest, ApiResponseListener listener) {
        super(Api.EDIT_PROFILE_URL, jsonRequest, listener);
    }

}
