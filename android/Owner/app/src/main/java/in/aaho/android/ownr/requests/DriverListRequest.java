package in.aaho.android.ownr.requests;

import android.text.TextUtils;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class DriverListRequest extends ApiGetRequest {

    public DriverListRequest(String url,ApiResponseListener listener) {
        super(generateUrl(url), ApiGetRequest.NO_HEADER, listener);
    }

    private static String generateUrl(String url) {
        if(TextUtils.isEmpty(url)) {
            return Api.DRIVER_LIST_URL;
        } else {
            return url;
        }
    }
}
