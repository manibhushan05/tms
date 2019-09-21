package in.aaho.android.ownr.requests;


import android.text.TextUtils;

import java.util.Map;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by mani on 28/7/16.
 */
public class TransactionDataRequests extends ApiGetRequest {


    public TransactionDataRequests(String url,Map<String, String> params, ApiResponseListener listener) {
        super(generateUrl(url), params, listener);
    }

    private static String generateUrl(String url) {
        if(TextUtils.isEmpty(url)) {
            return Api.BOOKING_ARCHIVE_URL;
        } else {
            return url;
        }
    }


    /*public TransactionDataRequests(String vehicleId, ApiResponseListener listener) {
        //super(Api.BOOKING_ARCHIVE_URL, ApiGetRequest.NO_HEADER, listener);
        super(Api.BOOKING_ARCHIVE_URL, ApiGetRequest.NO_HEADER, listener);
    }*/

}
