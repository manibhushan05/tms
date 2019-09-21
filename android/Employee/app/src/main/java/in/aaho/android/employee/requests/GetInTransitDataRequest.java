package in.aaho.android.employee.requests;

import android.text.TextUtils;

import java.util.Map;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by Suraj M
 */
public class GetInTransitDataRequest extends ApiGetRequest {

    public GetInTransitDataRequest(String url, Map<String, String> params, ApiResponseListener listener) {
        super(generateUrl(url), params, listener);
    }

    private static String generateUrl(String url) {
        String newUrl = "";
        if(TextUtils.isEmpty(url)) {
            newUrl = Api.GET_IN_TRANSIT_URL;
        } else {
            newUrl = url;
        }

        return newUrl;
    }

}
