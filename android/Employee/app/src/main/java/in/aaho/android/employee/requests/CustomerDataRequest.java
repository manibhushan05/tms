package in.aaho.android.employee.requests;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by aaho on 22/04/18.
 */

public class CustomerDataRequest extends ApiGetRequest {

    public CustomerDataRequest(String url, ApiResponseListener listener) {
        super(url, ApiGetRequest.NO_HEADER, listener);
    }

    /** Make the url for GET request with page and search value
     * @param page
     * @param search
     * @return complete url with page count and search keyword
     */
    public static String makeSearchUrl(String page,String search) {
        if(search.contains(" "))
            search = search.replace(" ","+");
        String url = Api.CUSTOMER_DATA_URL + "?search="+search;
        /*String url = Api.CUSTOMER_DATA_URL + "?page="+page + "&search="+search;*/

        return url;
    }
}

