package in.aaho.android.ownr.requests;


import android.text.TextUtils;

import java.util.Map;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by Suraj M
 */
public class GetPODDeliveredDataRequests extends ApiGetRequest {


    public GetPODDeliveredDataRequests(String url, Map<String, String> params, ApiResponseListener listener) {
        super(generateUrl(url), params, listener);
    }

    private static String generateUrl(String url) {
        if(TextUtils.isEmpty(url)) {
            return Api.GET_POD_DELIVERED_DATA;
        } else {
            return url;
        }
    }

}
