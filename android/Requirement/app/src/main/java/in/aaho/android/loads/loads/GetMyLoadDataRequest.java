package in.aaho.android.loads.loads;

import in.aaho.android.loads.common.ApiGetRequest;
import in.aaho.android.loads.common.ApiResponseListener;
import in.aaho.android.loads.requests.Api;

/**
 * Created by aaho on 20/05/18.
 */

public class GetMyLoadDataRequest extends ApiGetRequest {

    public GetMyLoadDataRequest(String url, ApiResponseListener listener) {
        super(url, ApiGetRequest.NO_HEADER, listener);
    }

    /** Make the url for GET request with officeId and status
     * @return complete url with officeId and status
     */
    public static String makeUrl() {
        String url = Api.GET_MY_LOADS;

        return url;
    }
}
