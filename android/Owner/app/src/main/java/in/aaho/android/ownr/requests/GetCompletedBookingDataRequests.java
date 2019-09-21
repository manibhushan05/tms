package in.aaho.android.ownr.requests;


import android.text.TextUtils;

import java.util.Map;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by Suraj M
 */
public class GetCompletedBookingDataRequests extends ApiGetRequest {


    public GetCompletedBookingDataRequests(String url, Map<String, String> params, ApiResponseListener listener) {
        super(generateUrl(url), params, listener);
    }

    private static String generateUrl(String url) {
        if(TextUtils.isEmpty(url)) {
            return Api.GET_BOOKING_COMPLETED_DATA;
        } else {
            return url;
        }
    }

}
