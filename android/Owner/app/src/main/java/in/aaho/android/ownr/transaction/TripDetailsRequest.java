package in.aaho.android.ownr.transaction;

import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.requests.Api;

/**
 * Created by mani on 18/09/17.
 */

public class TripDetailsRequest extends ApiPostRequest {
    public TripDetailsRequest(JSONObject jsonObject, ApiResponseListener listener) {
        super(Api.TEAM_TRIP_DETAILS, jsonObject, listener);
    }
}
