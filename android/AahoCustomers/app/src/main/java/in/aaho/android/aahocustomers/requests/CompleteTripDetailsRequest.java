package in.aaho.android.aahocustomers.requests;

import in.aaho.android.aahocustomers.common.ApiGetRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by mani on 10/12/16.
 */

public class CompleteTripDetailsRequest extends ApiGetRequest {
    public CompleteTripDetailsRequest(long bookingId, ApiResponseListener listener) {
        super(Api.TEAM_TRIP_DETAILS, bookingId, listener);
    }
}
