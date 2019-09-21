package in.aaho.android.aahocustomers.requests;

import in.aaho.android.aahocustomers.common.ApiGetRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by aaho on 11/07/18.
 */

public class FinancialDataRequests extends ApiGetRequest {

    public FinancialDataRequests(ApiResponseListener listener) {
        //super(Api.BOOKING_ARCHIVE_URL, ApiGetRequest.NO_HEADER, listener);
        super(Api.BOOKING_ARCHIVE_URL, listener);
    }

}