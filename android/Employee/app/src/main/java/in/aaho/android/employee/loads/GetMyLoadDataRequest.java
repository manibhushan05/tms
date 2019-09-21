package in.aaho.android.employee.loads;

import android.text.TextUtils;

import java.util.Map;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.other.Role;
import in.aaho.android.employee.requests.Api;

/**
 * Created by aaho on 20/05/18.
 */

public class GetMyLoadDataRequest extends ApiGetRequest {

    public GetMyLoadDataRequest(String url, Map<String, String> params, int aahoOfficeId,  String roles,
                                ApiResponseListener listener) {
        super(generateUrl(url,aahoOfficeId,roles), params, listener);
    }

    private static String generateUrl(String url,int aahoOfficeId, String roles) {
        String newUrl = "";
        if(TextUtils.isEmpty(url)) {
            if(roles.contains(Role.TECHNOLOGY) || roles.contains(Role.MANAGEMENT)) {
                newUrl = Api.GET_AVL_LOADS;
            } else if(roles.contains(Role.CITY_HEAD)) {
                newUrl = Api.GET_AVL_LOADS + "?aaho_office_id=" + aahoOfficeId;
            } else {
                newUrl = Api.GET_MY_LOADS;
            }
        } else {
            return url;
        }

        return newUrl;
    }

}
