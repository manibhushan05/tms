package in.aaho.android.employee.loads;

import android.text.TextUtils;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.other.Role;
import in.aaho.android.employee.requests.Api;

/**
 * Created by Suraj M
 */
public class GetAvlLoadDataRequest extends ApiGetRequest {

    public GetAvlLoadDataRequest(String url,int officeId, String status,
                                 String roles, ApiResponseListener listener) {
        super(makeUrl(url,officeId,status,roles), ApiGetRequest.NO_HEADER, listener);
    }

    /** Make the url for GET request with officeId and status
     * @return complete url with officeId and status
     */
    public static String makeUrl(String url,int officeId, String status,String roles) {
        String newUrl = "";
        if(TextUtils.isEmpty(url)) {
            if(roles.contains(Role.TECHNOLOGY) || roles.contains(Role.MANAGEMENT)) {
                newUrl = Api.GET_AVL_LOADS + "?requirement_status=" + status;
            } else {
                newUrl = Api.GET_AVL_LOADS + "?aaho_office_id=" + officeId +
                        "&requirement_status=" + status;
            }
        } else {
            newUrl = url;
        }

        return newUrl;
    }
}
