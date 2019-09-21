package in.aaho.android.employee.requests;

import android.text.TextUtils;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by Suraj M
 */

public class GetPendingLRDataRequest extends ApiGetRequest {

    public GetPendingLRDataRequest(String url,ApiResponseListener listener) {
        super(generateUrl(url), ApiGetRequest.NO_HEADER, listener);
    }

    private static String generateUrl(String url) {
        String newUrl = "";
        if(TextUtils.isEmpty(url)) {
            newUrl = Api.GET_PENDING_LR_URL;
        } else {
            newUrl = url;
        }

        return newUrl;
    }

}
