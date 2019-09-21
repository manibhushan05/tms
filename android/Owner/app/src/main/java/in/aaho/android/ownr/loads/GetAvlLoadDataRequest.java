package in.aaho.android.ownr.loads;

import java.util.Map;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.requests.Api;

/**
 * Created by Suraj
 */
public class GetAvlLoadDataRequest extends ApiGetRequest {

    public GetAvlLoadDataRequest(Map<String, String> params, ApiResponseListener listener) {
        super(Api.GET_AVL_LOADS, params, listener);
    }

//    * Make the url for GET request with officeId and status
//     * @return complete url with officeId and status
//    public static String makeUrl(String officeId,String status) {
//        String url = Api.GET_AVL_LOADS + "?aaho_office_id="+officeId +
//                "&requirement_status="+status;
//
//        return url;
//    }
}
