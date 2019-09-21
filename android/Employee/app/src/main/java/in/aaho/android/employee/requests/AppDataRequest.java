package in.aaho.android.employee.requests;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by aaho on 18/04/18.
 */

public class AppDataRequest extends ApiGetRequest {

    public AppDataRequest(ApiResponseListener listener) {
        super(Api.APP_DATA_URL, ApiGetRequest.NO_HEADER, listener);
    }
}

