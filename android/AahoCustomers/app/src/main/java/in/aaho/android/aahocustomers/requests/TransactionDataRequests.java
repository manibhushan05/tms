package in.aaho.android.aahocustomers.requests;


import in.aaho.android.aahocustomers.common.ApiGetRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by mani on 28/7/16.
 */
public class TransactionDataRequests extends ApiGetRequest {

    public TransactionDataRequests(ApiResponseListener listener) {
        //super(Api.BOOKING_ARCHIVE_URL, ApiGetRequest.NO_HEADER, listener);
        super(Api.BOOKING_ARCHIVE_URL, listener);
    }

}
