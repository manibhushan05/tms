package in.aaho.android.ownr.requests;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by Suraj
 */
public class GetNotificationCountRequest extends ApiGetRequest {

    public GetNotificationCountRequest(ApiResponseListener listener) {
        super(Api.NOTIFICATION_COUNT_URL, ApiGetRequest.NO_HEADER, listener);
    }

}
