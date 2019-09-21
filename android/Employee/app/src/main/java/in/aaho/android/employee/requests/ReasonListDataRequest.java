package in.aaho.android.employee.requests;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by Suraj M on 18/04/18.
 */

public class ReasonListDataRequest extends ApiGetRequest {

    public ReasonListDataRequest(ApiResponseListener listener) {
        super(Api.REASON_LIST_DATA_URL, ApiGetRequest.NO_HEADER, listener);
    }
}

