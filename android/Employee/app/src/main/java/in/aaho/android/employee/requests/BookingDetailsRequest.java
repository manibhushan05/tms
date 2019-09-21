package in.aaho.android.employee.requests;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by mani on 10/12/16.
 */

public class BookingDetailsRequest extends ApiGetRequest {

    public BookingDetailsRequest(long bookingId, ApiResponseListener listener) {
        super(Api.TEAM_TRIP_DETAILS+bookingId+"/", ApiGetRequest.NO_HEADER, listener);
    }
}
