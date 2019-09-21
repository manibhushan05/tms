package in.aaho.android.employee.requests;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by aaho on 18/04/18.
 */

public class SmeDataRequest extends ApiGetRequest {

    public SmeDataRequest(int clientId,ApiResponseListener listener) {
        super(Api.SME_DATA_URL + clientId +"/", ApiGetRequest.NO_HEADER, listener);
    }
}

