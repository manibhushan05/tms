package in.aaho.android.aahocustomers.loads;

import in.aaho.android.aahocustomers.common.ApiGetRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.requests.Api;

/**
 * Created by Suraj
 */
public class GetAvlLoadDataRequest extends ApiGetRequest {

    public GetAvlLoadDataRequest(String url, ApiResponseListener listener) {
        super(url, ApiGetRequest.NO_HEADER, listener);
    }

    /** Make the url for GET request with officeId and status
     * @return complete url with officeId and status
     */
    public static String makeUrl(String officeId, String status) {
        String url = Api.GET_AVL_LOADS + "?aaho_office_id="+officeId +
                "&requirement_status="+status;

        return url;
    }
}
