package in.aaho.android.ownr.booking;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.requests.Api;

/**
 * Created by mani on 19/9/17.
 */

class BookingArchiveRequest extends ApiGetRequest {
    BookingArchiveRequest(ApiResponseListener apiResponseListener) {
        super(Api.BOOKING_ARCHIVE_URL, apiResponseListener);
    }
}
