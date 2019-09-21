package in.aaho.android.ownr.requests;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by Suraj
 */
public class GetNotificationDataRequest extends ApiGetRequest {

    public GetNotificationDataRequest(ApiResponseListener listener) {
        super(Api.NOTIFICATION_LIST_URL, ApiGetRequest.NO_HEADER, listener);
    }

}
