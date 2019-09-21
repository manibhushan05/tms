package in.aaho.android.ownr.requests;

import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by mani on 10/12/16.
 */

public class CompleteTripDetailsRequest extends ApiGetRequest {
    /*public CompleteTripDetailsRequest(long bookingId, ApiResponseListener listener) {
        super(Api.TEAM_TRIP_DETAILS, bookingId, listener);
    }*/

    public CompleteTripDetailsRequest(long bookingId, ApiResponseListener listener) {
        super(Api.TEAM_TRIP_DETAILS+bookingId+"/", ApiGetRequest.NO_HEADER, listener);
    }
}
