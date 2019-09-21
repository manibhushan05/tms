package in.aaho.android.employee.requests;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by aaho on 23/04/18.
 */

public class AahoOfficeDataRequest extends ApiGetRequest {

    public AahoOfficeDataRequest(String url, ApiResponseListener listener) {
        super(url, ApiGetRequest.NO_HEADER, listener);
    }

    /** Make the url for GET request with page and search value
     * @param page
     * @param search
     * @return complete url with page count and search keyword
     */
    public static String makeSearchUrl(String page,String search) {
        String url = Api.AAHO_OFFICE_DATA_URL + "?search="+search;
        /*String url = Api.AAHO_OFFICE_DATA_URL + "?page="+page + "&search="+search;*/
//        String url = Api.AAHO_OFFICE_DATA_URL;

        return url;
    }
}
